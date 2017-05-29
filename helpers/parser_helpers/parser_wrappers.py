from functools import wraps
from helpers.exceptions import *


def is_comment(func):
    @wraps(func)
    def func_wrapper(email_info, position, *args, **kwargs):
        tmp_ret = func(email_info, position, *args, **kwargs)
        if tmp_ret and is_comment:
            email_info.add_comment(tmp_ret)
        return tmp_ret
    return func_wrapper


def pass_diags(*diags):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(email_info, position, *args, **kwargs):
            tmp_ret = func(email_info, position, *args, **kwargs)
            if tmp_ret and diags is not None:
                tmp_ret.add(*diags)
            return tmp_ret

        return func_wrapper

    return func_decorator


def fail_diags(*diags):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(email_info, position, *args, **kwargs):
            tmp_ret = func(email_info, position, *args, **kwargs)
            if not tmp_ret and diags is not None:
                tmp_ret.add(*diags)
            return tmp_ret
        return func_wrapper
    return func_decorator


def email_parser(history_segment=True, name=None):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(email_info, position, *args, **kwargs):
            tmp_err = None
            position = int(position)
            stage_name = kwargs.get('stage_name', name or func.__name__)

            email_info.begin_stage(stage_name, position=position)

            tmp_near_at_flag = email_info.flags('near_at')
            raise_error = False

            if not email_info.at_end(position):
                try:
                    tmp_ret = func(email_info, position, *args, **kwargs)
                except ParsingError as err:
                    tmp_err = err
                    raise_error = True
                    tmp_ret = err.results
            else:
                tmp_ret = email_info.fb(position)

            if tmp_ret and history_segment:
                tmp_ret.set_history()

            email_info.flags.near_at_flag = tmp_near_at_flag
            email_info.end_stage(tmp_ret, raise_error=raise_error)

            if raise_error:
                raise tmp_err

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

'''
def must_end_local_part(fail_msg=None):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(email_info, position, *args, **kwargs):
            tmp_ret = func(email_info, position, *args, **kwargs)
            if not tmp_ret and diags is not None:
                tmp_ret.add(*diags)
            return tmp_ret
        return func_wrapper
    return func_decorator

def must_end_domain_part(fail_msg=None):


def must_end_part(fail_msg=None):

'''