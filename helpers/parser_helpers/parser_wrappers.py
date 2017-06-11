__all__ = ['pass_diags', 'fail_diags', 'email_parser', 'wrapped_parser']

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


def email_parser(is_history_item=True, name=None):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(email_info, position, *args, is_history_item=is_history_item, name=name, **kwargs):
            tmp_err = None
            position = int(position)
            name = name or func.__name__
            # stage_name = kwargs.get('name', name or func.__name__)
            # is_history_item = kwargs.get('is_history_item', is_history_item)

            email_info.begin_stage(name, position=position)

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

            if tmp_ret and is_history_item:
                tmp_ret.set_history(name)

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
        def func_wrapper(email_info, position, *args, end_wrapper=end_wrapper, **kwargs):

            if end_wrapper is None:
                end_wrapper = start_wrapper

            wrapped_stage_name = 'wrapping_in_%s%s' % (start_wrapper, end_wrapper)

            email_info.begin_stage(wrapped_stage_name, position)

            if end_wrapper is None:
                end_wrapper = start_wrapper

            tmp_ret = email_info.fb(position)

            if not email_info.at_end(position + tmp_ret) and email_info[position] == start_wrapper:
                tmp_ret += 1
            else:
                return tmp_ret

            tmp_ret += func(email_info, position + tmp_ret, *args, **kwargs)

            if not email_info.at_end(position + tmp_ret) and email_info[position + tmp_ret] == end_wrapper:
                tmp_ret += 1
                return tmp_ret
            else:
                if email_info.at_end(position + tmp_ret):
                    return tmp_ret(no_end_error)
                else:
                    return tmp_ret(bad_text_error)

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