from functools import wraps
from helpers.exceptions import *


def email_parser(segment=True, is_comment=False, diags=None):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(email_info, position, *args, **kwargs):
            stage_name = kwargs.get('stage_name', func.__name__)
            email_info.stage(stage_name)
            email_info.trace.begin(position)
            tmp_near_at_flag = email_info.flags('near_at')
            position = int(position)
            raise_error = False

            if not email_info.at_end(position):

                try:
                    tmp_ret = func(email_info, position, *args, **kwargs)

                except ParsingError as err:
                    raise_error = True
                    tmp_ret = err.results

            else:
                tmp_ret = email_info.fb

            if tmp_ret and segment:
                tmp_ret.set_as_element()

            if tmp_ret and diags is not None:
                if isinstance(diags, (list, tuple)):
                    tmp_ret.add(*diags)
                else:
                    tmp_ret.add(diags)

            if tmp_near_at_flag:
                email_info.flags('near_at')

            email_info.end(position, tmp_ret)

            email_info.stage.pop()

            if raise_error:
                raise ParsingError(results=tmp_ret)

            if tmp_ret and is_comment:
                email_info.add_comment(position, tmp_ret.length)
            return tmp_ret

        return func_wrapper

    return func_decorator


def wrapped_parser(start_wrapper, end_wrapper=None, no_end_error='', bad_text_error=''):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(email_info, position, *args, **kwargs):
            if end_wrapper is None:
                end_wrapper = start_wrapper

            tmp_ret = email_info.fb(position)

            tmp_start = start_wrapper(email_info, position)

            if not tmp_start:
                return tmp_ret

            if not email_info.find(position + tmp_start, end_wrapper.char, skip_quoted=True):
                return tmp_ret(no_end_error)

            tmp_ret += tmp_start
            tmp_ret += func(email_info, position, *args, **kwargs)
            tmp_end = end_wrapper(email_info, position)

            if not tmp_end:
                return tmp_ret(bad_text_error)

            return tmp_ret(tmp_end)

        return func_wrapper

    return func_decorator
