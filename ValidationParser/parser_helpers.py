from functools import wraps
from helpers.exceptions import ParsingError
from helpers.footballs import ParseResultFootball


from helpers .general.general import make_char_str

AT = '@'
BACKSLASH = '\\'
CLOSEPARENTHESIS = ')'
CLOSESQBRACKET = ']'
COLON = ':'
COMMA = ','
CR = "\r"
DOT = '.'
DOUBLECOLON = '::'
DQUOTE = '"'
HTAB = "\t"
HYPHEN = '-'
LF = "\n"
OPENPARENTHESIS = '('
OPENSQBRACKET = '['
SP = ' '
CRLF = '\r\n'

DIGIT = '1234567890'
HEXDIG = '1234567890abcdefABCDEF'

ALPHA = make_char_str((65, 90), (97, 122))
LET_DIG = make_char_str(ALPHA, DIGIT)

# **********************************************************************************
# <editor-fold desc="  WRAPPERS  ">
# **********************************************************************************
#
#
# def email_parser(is_history_item=True, name=None, pass_diags=None, fail_diags=None, is_comment=False,
#                  extra_text_error=None, full_domain_part=False, full_local_part=False):
#     def func_decorator(func):
#         @wraps(func)
#         def func_wrapper(email_info, position, *args, is_history=is_history_item, pass_d=pass_diags,
#                          fail_d=fail_diags, is_comment_flag=is_comment, func_name=name, full_domain=full_domain_part,
#                          full_local=full_local_part, extra_text_err=extra_text_error, **kwargs):
#             tmp_err = None
#             position = int(position)
#             func_name = func_name or func.__name__
#             # stage_name = kwargs.get('name', name or func.__name__)
#             # is_history_item = kwargs.get('is_history_item', is_history_item)
#
#             email_info.begin_stage(func_name, position=position)
#
#             tmp_near_at_flag = email_info.flags('near_at')
#             raise_error = False
#
#             if not email_info.at_end(position):
#                 try:
#                     tmp_ret = func(email_info, position, *args, **kwargs)
#                 except ParsingError as err:
#                     tmp_err = err
#                     raise_error = True
#                     tmp_ret = err.results
#             else:
#                 tmp_ret = email_info.fb(position)
#
#             if tmp_ret:
#                 if is_history:
#                     tmp_ret.set_history(func_name)
#                 if pass_d:
#                     if isinstance(pass_d, str):
#                         pass_d = [pass_d]
#                     tmp_ret(*pass_d)
#                 if is_comment_flag:
#                     email_info.add_comment(tmp_ret)
#
#                 if full_domain:
#
#                     tmp_char = email_info[position]
#                     if tmp_char == HYPHEN:
#                         return tmp_ret('ERR_DOMAIN_HYPHEN_START')
#                     elif tmp_char == DOT:
#                         return tmp_ret('ERR_DOT_START')
#
#                     if not email_info.at_end(position + tmp_ret):
#                         tmp_ret(extra_text_err)
#                     else:
#                         if tmp_ret > 255:
#                             tmp_ret('RFC5322_DOMAIN_TOO_LONG')
#
#                         last_char = email_info[-1]
#
#                         if last_char == HYPHEN:
#                             tmp_ret('ERR_DOMAIN_HYPHEN_END')
#                         elif last_char == BACKSLASH:
#                             tmp_ret('ERR_BACKSLASH_END')
#                         elif last_char == DOT:
#                             tmp_ret('ERR_DOT_END')
#
#                 if full_local:
#
#                     if email_info[position] == DOT:
#                         return tmp_ret('ERR_DOT_START')
#
#                     if email_info.flags.at_in_cfws:
#                         tmp_ret('DEPREC_CFWS_NEAR_AT')
#
#                     if email_info[position + tmp_ret] != AT:
#                         tmp_ret(extra_text_err)
#
#                         if not email_info.find(position + tmp_ret, AT, skip_quoted=True):
#                             tmp_ret('ERR_NO_DOMAIN_SEP')
#
#                     else:
#                         if tmp_ret > 64:
#                             tmp_ret('RFC5322_LOCAL_TOO_LONG')
#
#                         last_char = email_info[-1]
#
#                         if last_char == BACKSLASH:
#                             tmp_ret('ERR_BACKSLASH_END')
#                         elif last_char == DOT:
#                             tmp_ret('ERR_DOT_END')
#
#             elif fail_d:
#                 if isinstance(fail_d, str):
#                     fail_d = [fail_d]
#                 tmp_ret(*fail_d)
#
#             email_info.flags.near_at_flag = tmp_near_at_flag
#             email_info.end_stage(tmp_ret, raise_error=raise_error)
#
#             if raise_error:
#                 raise tmp_err
#
#             return tmp_ret
#
#         return func_wrapper
#
#     return func_decorator
#
#
# def wrapped_parser(str_wrapper=None, no_end_error=''):  # , bad_text_error=''):
#     def func_decorator(func):
#         @wraps(func)
#         def func_wrapper(email_info, position, *args, stw=str_wrapper, init_start=None, **kwargs):
#
#             wrapped_stage = []
#
#             if stw is None:
#                 start_wrapper = None
#                 end_wrapper = None
#             else:
#                 start_wrapper = stw[0]
#                 if len(stw) == 2:
#                     end_wrapper = stw[1]
#                 else:
#                     end_wrapper = start_wrapper
#
#                 wrapped_stage.append(stw)
#
#             wrapped_stage_name = 'wrapping in >%s<' % '/'.join(wrapped_stage)
#             email_info.begin_stage(wrapped_stage_name, position)
#
#             tmp_ret = email_info.fb(position)
#
#             if start_wrapper is not None:
#                 if init_start is None:
#                     init_start = single_char(email_info, position + tmp_ret, start_wrapper)
#                 if init_start:
#                     tmp_ret += init_start
#                 else:
#                     return tmp_ret
#
#             tmp_ret_2 = func(email_info, position + tmp_ret, *args, **kwargs)
#             tmp_ret += tmp_ret_2
#
#             if not tmp_ret_2:
#                 return tmp_ret(0)
#
#             if end_wrapper is not None:
#                 tmp_ret_2 = single_char(email_info, position + tmp_ret, end_wrapper)
#                 if tmp_ret_2:
#                     tmp_ret += tmp_ret_2
#                 else:
#                     tmp_ret(no_end_error)
#
#             return tmp_ret
#
#         return func_wrapper
#
#     return func_decorator


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  HELPERS  ">
# **********************************************************************************

#
# def simple_char(email_info, position, parse_for, min_count=-1, max_count=99999, parse_until=None):
#     tmp_ret = email_info.fb(position)
#     tmp_count = 0
#
#     if parse_until is None:
#         looper = email_info.remaining_complex(begin=position, count=max_count)
#     else:
#         looper = email_info.remaining_complex(begin=position, count=max_count, until_char=parse_until)
#
#     for i in looper:
#         if i in parse_for:
#             tmp_count += 1
#         else:
#             if tmp_count >= min_count:
#                 return tmp_ret(tmp_count)
#             else:
#                 return tmp_ret
#
#     if tmp_count >= min_count:
#         return tmp_ret(tmp_count)
#     return tmp_ret
#
#
# def single_char(email_info, position, parse_for):
#     tmp_ret = email_info.fb(position)
#     if email_info[position] == parse_for:
#         return tmp_ret(1)
#     else:
#         return tmp_ret
#
#
# def simple_str(email_info, position, parse_for, caps_sensitive=True):
#     tmp_ret = email_info.fb(position)
#     tmp_len = len(parse_for)
#
#     tmp_check = email_info.mid(position, tmp_len)
#
#     if not caps_sensitive:
#         tmp_check = tmp_check.lower()
#         parse_for = parse_for.lower()
#
#     if tmp_check == parse_for:
#         tmp_ret += tmp_len
#
#     return tmp_ret
#
#
# def _make_ret(email_info, position, parser, *args, **kwargs):
#     if isinstance(parser, ParseResultFootball):
#         return parser
#     elif isinstance(parser, str):
#         if len(parser) > 1 and parser[0] == '"' and parser[-1] == '"':
#             return simple_str(email_info, position, parser[1:-1])
#         else:
#             return simple_char(email_info, position, parser)
#     else:
#         return parser(email_info, position, *args, **kwargs)


def parse_or(email_info, position, *parsers, **kwargs):
    email_info.begin_stage('OR', position)
    for p in parsers:
        tmp_ret = _make_ret(email_info, position, p, **kwargs)
        if tmp_ret:
            email_info.end_stage(results=tmp_ret)
            return tmp_ret
    email_info.end_stage(results=email_info.fb(position))
    return email_info.fb(position)


def parse_and(email_info, position, *parsers, **kwargs):
    email_info.begin_stage('OR', position)
    tmp_ret = email_info.fb(position)
    for p in parsers:
        tmp_ret_2 = _make_ret(email_info, position + tmp_ret, p, **kwargs)
        if not tmp_ret_2:
            email_info.end_stage(results=tmp_ret)
            return email_info.fb(position)
        tmp_ret += tmp_ret_2
    email_info.end_stage(results=tmp_ret)
    return tmp_ret


def parse_loop(email_info, position, parser, *args, min_loop=1, max_loop=256, ret_count=False, **kwargs):
    email_info.begin_stage('LOOP', position)
    tmp_ret = email_info.fb(position)
    loop_count = 0

    while loop_count in range(max_loop):
        email_info.begin_stage('Loop #%s, @ %s' % (loop_count, position + tmp_ret), position + tmp_ret)

        tmp_loop_ret = parser(email_info, position + tmp_ret, *args, **kwargs)
        email_info.end_stage(results=tmp_loop_ret)

        if tmp_loop_ret:
            tmp_ret += tmp_loop_ret
        else:
            break

        loop_count += 1

    email_info.end_stage(results=tmp_ret)

    if loop_count >= min_loop:
        if ret_count:
            return loop_count, tmp_ret
        else:
            return tmp_ret
    else:
        if ret_count:
            return 0, email_info.fb(position)
        else:
            return email_info.fb(position)

#
# def parse_best(email_info, position, *parsers, try_all=False):
#     email_info.begin_stage('BEST', position)
#     tmp_ret = email_info.fb(position)
#
#     for p in parsers:
#         if not try_all and p and email_info.at_end(position + p):
#             tmp_ret = p
#             break
#
#         tmp_ret = tmp_ret.max(p)
#     email_info.end_stage(results=tmp_ret)
#     return tmp_ret

# **********************************************************************************
# </editor-fold>
# **********************************************************************************

