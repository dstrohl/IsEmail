from parse_results import ParseResultFootball, ParsingError
# from collections import deque
from functools import wraps
from meta_data import ISEMAIL_ALLOWED_GENERAL_ADDRESS_LITERAL_STANDARD_TAGS, ISEMAIL_DOMAIN_TYPE

from parser_helpers import *

# **********************************************************************************
# <editor-fold desc="GLOBALS">
# **********************************************************************************


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
IPV6TAG = 'ipv6:'
LF = "\n"
OPENPARENTHESIS = '('
OPENSQBRACKET = '['
SP = ' '
CRLF = '\r\n'
DIGIT = '1234567890'
TWO_DIGIT = '12'
HEXDIG = '1234567890abcdefABCDEF'

ADDR_LIT_IPV4 = '0123456789.'
ADDR_LIT_IPV6 = make_char_str(HEXDIG, ADDR_LIT_IPV4, COLON)

ALPHA = make_char_str((65, 90), (97, 122))

LTR_STR = make_char_str((65, 90), (97, 122), (48, 57))
LET_DIG = make_char_str(ALPHA, DIGIT)
LDH_STR = make_char_str(LET_DIG, '-')
VCHAR = make_char_str((31, 126))
ATEXT = make_char_str(ALPHA, DIGIT, "!#$%&'+-/=?^_`{|}~*")
DCONTENT = make_char_str((33, 90), (94, 126))

OBS_NO_WS_CTL = make_char_str((1, 8), (11, 12), (14, 31), 127)

OBS_QP = make_char_str(0, OBS_NO_WS_CTL, LF, CR)

QTEXT = make_char_str(33, (35, 91), (93, 126))
OBS_QTEXT = make_char_str(OBS_NO_WS_CTL, QTEXT)

CTEXT = make_char_str((33, 39), (42, 91), (93, 126))
OBS_CTEXT = make_char_str(OBS_NO_WS_CTL, CTEXT)

DTEXT = DCONTENT
OBS_DTEXT = make_char_str(OBS_NO_WS_CTL, DTEXT)

WSP = make_char_str(SP, HTAB)

VCHAR_WSP = make_char_str(VCHAR, WSP)

PRE_CFWS = make_char_str(WSP, OPENPARENTHESIS, CR)

# **********************************************************************************
# </editor-fold desc="GLOBALS">
# **********************************************************************************

# **********************************************************************************
# <editor-fold desc="WRAPPERS">
# **********************************************************************************


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


# **********************************************************************************
# </editor-fold desc="WRAPPERS">
# **********************************************************************************

# **********************************************************************************
# <editor-fold desc="PARSER HELPERS">
# **********************************************************************************


def simple_char(email_info, position, parse_for, min_count=-1, max_count=99999, parse_until=None):
    tmp_ret = email_info.fb(position)
    tmp_count = 0
    for i in email_info.remaining_complex(begin=position, count=max_count, until_char=parse_until):
        if i in parse_for:
            tmp_count += 1
        else:
            if tmp_count >= min_count:
                return tmp_ret(tmp_count)
            else:
                return tmp_ret

    if tmp_count >= min_count:
        return tmp_ret(tmp_count)
    return tmp_ret


def single_char(email_info, position, parse_for):
    tmp_ret = email_info.fb(position)
    if email_info[position] == parse_for:
        return tmp_ret(1)
    else:
        return tmp_ret


def simple_str(email_info, position, parse_for, caps_sensitive=True):
    tmp_ret = email_info.fb(position)
    tmp_len = len(parse_for)

    tmp_check = email_info.mid(position, tmp_len)

    if not caps_sensitive:
        tmp_check = tmp_check.lower()
        parse_for = parse_for.lower()

    if tmp_check == parse_for:
        tmp_ret += tmp_len

    return tmp_ret


# **********************************************************************************
# </editor-fold desc="PARSER HELPERS">
# **********************************************************************************



# **********************************************************************************
# <editor-fold desc="PARSERS">
# **********************************************************************************


'''
def _try_action(email_info, position, action_dict):
    if isinstance(action_dict, dict):
        action_dict = action_dict.copy()
        if 'string_in' in action_dict:
            parse_for = action_dict.pop('string_in')
            return email_info.simple_char(position, parse_for=parse_for, **action_dict)

        elif 'function' in action_dict:
            tmp_func = action_dict.pop('function')
            return tmp_func(position, **action_dict)
        else:
            raise AttributeError('Invalid dictionary passed: %r' % action_dict)
    elif isinstance(action_dict, str):
        return email_info.simple_char(position, parse_for=action_dict)

    else:
        return action_dict(position)

def try_or(email_info, position, *args):
    """
    :param position:
    :param args:

     args =
        dict(
            name=<action_name>,
            string_in="parse_string",
            kwargs for simple_str),
        dict(
            name=<action_name>,
            function="function_name",
            kwargs fpr function)
    :return:  (<action_name>, football)
    """
    position = email_info.pos(position)
    for act in args:
        if isinstance(act, dict):
            tmp_name = act.pop('name')
        elif isinstance(act, str):
            tmp_name = act
        else:
            tmp_name = act.__name__

        tmp_ret = email_info._try_action(position, act)
        if tmp_ret or tmp_ret.error:
            return tmp_name, tmp_ret

    return '', ParseResultFootball(email_info)

def try_counted_and(email_info, position, *args, min_loop=1, max_loop=1):

    final_loop_count = 0
    position = email_info.pos(position)
    tmp_ret = ParseResultFootball(email_info)
    exit_break = False
    empty_return = False

    # email_info.add_note_trace('looping begin outside AND at: ', position + tmp_ret.l)
    # email_info.trace_level += 1
    for loop_count in range(max_loop):
        tmp_loop_ret = ParseResultFootball(email_info)
        email_info.add_begin_trace(position + tmp_ret.l)
        # email_info.add_note_trace('looping begin inside  AND at: ', position + tmp_ret.l + tmp_loop_ret.l)
        # email_info.trace_level += 1
        for act in args:
            # if isinstance(act, dict):
            #     tmp_name = act.pop('name', '')
            # elif isinstance(act, str):
            #     tmp_name = act
            # else:
            #     tmp_name = act.__name__

            tmp_ret_1 = email_info._try_action(position + tmp_ret.l + tmp_loop_ret.l, act)

            if not tmp_ret_1:
                exit_break = True
                # email_info.add_note_trace('Breaking inside loop')
                break

            tmp_loop_ret += tmp_ret_1

        # email_info.trace_level -= 1
        # email_info.add_note_trace('looping end inside  AND', position + tmp_ret.l + tmp_loop_ret.l)
        email_info.add_end_trace(position + tmp_ret.l, tmp_ret)
        if exit_break:
            if tmp_loop_ret:
                # email_info.add_note_trace('Breaking outside loop - 1')
                break
            else:
                tmp_ret += tmp_loop_ret
                # email_info.add_note_trace('Breaking outside loop - 2')
                break

        else:
            if tmp_loop_ret:
                tmp_ret += tmp_loop_ret
            else:
                # email_info.add_note_trace('Breaking outside loop - 3')
                break

        final_loop_count += 1

    # email_info.trace_level -= 1
    # email_info.add_note_trace('looping end of outside AND at: ', position + tmp_ret.l)

    if final_loop_count >= min_loop and not empty_return:
        return final_loop_count, tmp_ret
    else:
        return 0, ParseResultFootball(email_info)

def try_and(email_info, position, *args, min_loop=1, max_loop=1):
    count, tmp_ret = email_info.try_counted_and(position, *args, min_loop=min_loop, max_loop=max_loop)
    return tmp_ret

def ipv6_segment(email_info, position, min_count=1, max_count=7):
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.ipv6_hex(position)

    if tmp_ret:
        if max_count == 1:
            return 1, tmp_ret

        if not email_info.at_end(position + tmp_ret.l + 1) and \
                        email_info.this_char(position + tmp_ret.l) == ':' and \
                        email_info.this_char(position + tmp_ret.l + 1) == ':' and \
                        min_count <= 1:
            email_info.add_note_trace('Double Colons found, exiting')
            return 1, tmp_ret

        tmp_colon_str = {'string_in': email_info.COLON, 'min_count': 1, 'max_count': 1}
        tmp_count, tmp_ret_2 = email_info.try_counted_and(position + tmp_ret.l,
                                                    email_info.colon,
                                                    email_info.ipv6_hex, min_loop=min_count - 1, max_loop=max_count - 1)
    else:
        return 0, ParseResultFootball(email_info)

    if tmp_ret_2:
        return tmp_count + 1, tmp_ret(tmp_ret_2)
    else:
        return 0, ParseResultFootball(email_info)

def football_max(email_info, *footballs, names=None):
    names = names or []

    email_info.add_note_trace('Comparing Footballs')
    if email_info._set_trace(1):
        for index, fb in enumerate(footballs):
            if len(names) < index + 1:
                if fb.segment_name == '':
                    names.append('#%s' % index)
                else:
                    names.append(fb.segment_name)

            if fb.error:
                email_info.add_note_trace('Comp %s [ERROR] (%s/%s)' % (names[index], int(fb), fb._max_length))
            else:
                email_info.add_note_trace('Comp %s (%s/%s)' % (names[index], int(fb), fb._max_length))
            email_info.add_note_trace('        %r' % fb.diags())

    tmp_ret = None
    tmp_index = -1
    a_index = -1
    b_index = -1
    ab_note = ''

    for index, fb in enumerate(footballs):
        if tmp_ret is None:
            tmp_ret = fb
            tmp_index = index
            continue

        a_index = tmp_index
        b_index = index
        ab_note = ''
        update_ret = False

        if tmp_ret.error != fb.error:
            if tmp_ret.error:
                if fb:
                    update_ret = False
                    ab_note = '(B has error, A haa content)'
            elif fb.error:
                if not tmp_ret:
                    update_ret = False
                    ab_note = '(A has Error, B no content)'
        else:
            if fb > tmp_ret:
                update_ret = False
                ab_note = '(A is larger)'
            elif fb == tmp_ret:
                if fb._max_length > tmp_ret._max_length:
                    update_ret = False
                    ab_note = '(A max length longer)'

        if update_ret:
            tmp_ret = fb
            tmp_index = index
            a_index = index
            b_index = tmp_index

        if email_info._set_trace():
            email_info.add_note_trace('Test #%s: %s > %s  %s' % (index, names[a_index], names[b_index], ab_note))

    if email_info._set_trace(-1):
        email_info.add_note_trace('Returning %s' % names[tmp_index])
    return tmp_ret


@email_parser(skip=True)
def address_spec(email_info, parser, position):
    """
    addr-spec       =   local-part "@" domain
    """
    email_info.in_local_part = True
    email_info.in_domain_part = False
    email_info.near_at_flag = False
    tmp_ret = email_info.fb(position)
    email_info.add_note_trace('Address Length: ' + str(email_info.email_len))

    if email_info.email_len == 0:
        email_info.add_note_trace('Empty address')
        return tmp_ret('ERR_EMPTY_ADDRESS')

    tmp_ret += email_info.local_part(position)

    if not tmp_ret:
        tmp_ret += email_info.at(position)
        if tmp_ret:
            return tmp_ret('ERR_NO_LOCAL_PART')
        else:
            return tmp_ret('ERR_UNKNOWN')

    email_info.in_local_part = False

    tmp_ret_2 = email_info.at(position + tmp_ret)

    email_info.near_at_flag = True
    email_info.in_domain_part = True

    if tmp_ret_2:
        tmp_ret_2.at_loc = position + tmp_ret

        tmp_ret_3 = email_info.domain(position + tmp_ret + tmp_ret_2)

        if tmp_ret_3:
            tmp_ret += tmp_ret_2
            tmp_ret += tmp_ret_3
        else:
            return tmp_ret(tmp_ret_2, 'ERR_NO_DOMAIN_PART')

    elif not email_info.find(position + tmp_ret, email_info.AT, skip_quoted_str=True):
        tmp_ret('ERR_NO_DOMAIN_SEP')
    else:
        return tmp_ret

    if tmp_ret > 254:
        tmp_ret('RFC5322_TOO_LONG')

    if not tmp_ret.results:
        tmp_ret('VALID')

    return tmp_ret

# def local_part_skip(email_info, parser, position, football):
#     skip_next = False
#     if football and not football.error:
#         if email_info.at_end(position + football) and not football.error:
#             email_info.add_note_trace('Skipping due to at the end (and no error)')
#             skip_next = True
#         elif email_info.this_char(position + football) == email_info.AT and not football.error:
#             email_info.add_note_trace('Skipping due to @ next (and no error)')
#             skip_next = True
#     return skip_next

@email_parser()
def local_part(email_info, parser, position):

    tmp_ret = email_info.fb(position)

    if email_info.this_char(position) == email_info.DOT:
        return tmp_ret('ERR_DOT_START')

    tmp_ret += email_info._local_part(position)

    if 'RFC5321_QUOTED_STRING' in tmp_ret:
        extra_text_error = 'ERR_ATEXT_AFTER_QS'
    else:
        if 'CFWS_LAST' in tmp_ret.flags:
            extra_text_error = 'ERR_ATEXT_AFTER_CFWS'
        else:
            extra_text_error = 'ERR_EXPECTING_ATEXT'

    if email_info.at_in_cfws:
        tmp_ret('DEPREC_CFWS_NEAR_AT')

    if email_info.this_char(position + tmp_ret) != email_info.AT:
        tmp_ret(extra_text_error)

        if not email_info.find(position + tmp_ret, email_info.AT, skip_quoted_str=True):
            tmp_ret('ERR_NO_DOMAIN_SEP')

    else:
        if tmp_ret > 64:
            tmp_ret('RFC5322_LOCAL_TOO_LONG')

        last_char = email_info.this_char(-1)

        if last_char == email_info.BACKSLASH:
            tmp_ret('ERR_BACKSLASH_END')
        elif last_char == email_info.DOT:
            tmp_ret('ERR_DOT_END')

    if tmp_ret.error:
        raise ParsingError(tmp_ret)

    return tmp_ret

def _local_part(email_info, parser, position):
    """
    local-part      =   dot-atom / quoted-string / obs-local-part
        // http://tools.ietf.org/html/rfc5321#section-4.5.3.1.1
        //   The maximum total length of a user name or other local-part is 64
        //   octets.


    [1033]         DEPREC_LOCAL_PART  The local part is in a deprecated form (ISEMAIL_DEPREC)
    [1067]    RFC5322_LOCAL_TOO_LONG  The local part of the address is too long (ISEMAIL_RFC5322)

    """

    tmp_dot_atom = email_info.dot_atom(position)
    if tmp_dot_atom:
        return tmp_dot_atom

    tmp_qstring = email_info.quoted_string(position)
    if tmp_qstring:
        return tmp_qstring

    tmp_obs_lpart = email_info.obs_local_part(position)
    if tmp_obs_lpart:
        return tmp_obs_lpart

    return email_info.football_max(tmp_dot_atom, tmp_qstring, tmp_obs_lpart,
                             names=['dot-atom', 'quoted_string', 'obs_local_part'])

    # try:
    #     tmp_ret_2 = email_info.dot_atom(position)
    #
    # except ParsingError as err:
    #     tmp_ret_2 = err.results
    #
    # skip_next = email_info.local_part_skip(position, tmp_ret_2)
    #
    # if not skip_next:
    #     email_info.add_note_trace('Trying Quoted String')
    #     try:
    #         tmp_ret_3 = email_info.quoted_string(position)
    #
    #     except ParsingError as err:
    #         tmp_ret_3 = err.results
    #
    #     tmp_ch, tmp_ret_2 = email_info.football_max(tmp_ret_2, tmp_ret_3)
    #     if tmp_ch == 0:
    #         is_qs = True
    #
    #     skip_next = email_info.local_part_skip(position, tmp_ret_3)
    # else:
    #     email_info.add_note_trace('skipping Quoted String')
    #
    # if not skip_next:
    #     try:
    #         email_info.add_note_trace('trying obs-local-part')
    #         tmp_ret_3 = email_info.obs_local_part(position)
    #
    #     except ParsingError as err:
    #         tmp_ret_3 = err.results
    #
    #     tmp_ch, tmp_ret_2 = email_info.football_max(tmp_ret_2, tmp_ret_3)
    #     if tmp_ch == 0:
    #         is_qs = False
    # else:
    #     email_info.add_note_trace('skipping obs-local-part')
    #
    # tmp_ret(tmp_ret_2, raise_on_error=False)
    #
    # email_info.add_note_trace('Returning length: ' + str(tmp_ret.l))
    # if not email_info.at_end(position + tmp_ret):
    #     email_info.add_note_trace('not at the end, checking next char: ' + email_info.this_char(position + tmp_ret))
    #     if email_info.this_char(position + tmp_ret) == email_info.DOT:
    #         email_info.add_note_trace('adding a dot end warning')
    #         # errors_to_add.append('ERR_DOT_END')
    #         tmp_ret('ERR_DOT_END', raise_on_error=False)
    #
    # if tmp_ret:
    #     if not email_info.at_end(position + tmp_ret):
    #         if email_info.this_char(position + tmp_ret) != email_info.AT:
    #             if is_qs:
    #                 email_info.add_note_trace('adding ERR_ATEXT_AFTER_QS for QS')
    #                 tmp_ret('ERR_ATEXT_AFTER_QS', raise_on_error=False)
    #             else:
    #                 email_info.add_note_trace('adding ERR_EXPECTING_ATEXT')
    #                 tmp_ret('ERR_EXPECTING_ATEXT', raise_on_error=False)
    #
    # if 'DEPREC_LOCAL_PART' in tmp_ret and 'CFWS_COMMENT' in tmp_ret:
    #     tmp_ret('DEPREC_COMMENT')
    #
    # if tmp_ret.error:
    #     email_info.add_note_trace('Raising the error')
    #     raise ParsingError(results=tmp_ret)
    #
    # return tmp_ret

def domain_dot_atom(email_info, *args, **kwargs):
    tmp_ret = email_info.dot_atom(*args, **kwargs)
    if tmp_ret:
        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.DNS
        tmp_ret('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN')
    return tmp_ret

@email_parser()
def dot_atom(email_info, parser, position, init_cfws=None):
    """
    dot-atom        =   [CFWS] dot-atom-text [CFWS]
    """

    tmp_ret = email_info.fb(position)
    email_info.near_at_flag = False
    email_info.at_in_cfws = False

    if init_cfws is None:
        tmp_ret_cfws = email_info.cfws(position)
    else:
        tmp_ret_cfws = init_cfws

    tmp_ret_cfws.flags -= 'CFWS_LAST'

    tmp_ret_2 = email_info.dot_atom_text(position + tmp_ret_cfws)

    if tmp_ret_2:
        tmp_ret += tmp_ret_cfws
        tmp_ret += tmp_ret_2

        tmp_ret_cfws = email_info.cfws(position + tmp_ret)

        tmp_ret += tmp_ret_cfws

    return tmp_ret

@email_parser()
def dot_atom_text(email_info, parser, position):
    """
        dot-atom-text   =   1*atext *("." 1*atext)
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.atext(position)
    # email_info.add_note_trace('1 tmp_ret.l = ' + str(tmp_ret.l ))
    if email_info.at_end(position + tmp_ret):
        return tmp_ret

    if tmp_ret:
        while True:
            tmp_ret_2 = email_info.single_dot(position + tmp_ret)
            if tmp_ret_2:
                tmp_ret_3 = email_info.atext(position + tmp_ret + tmp_ret_2)
                if tmp_ret_3:
                    tmp_ret += tmp_ret_2
                    tmp_ret += tmp_ret_3
                    continue
            break

    return tmp_ret

@email_parser(diags='DEPREC_LOCAL_PART')
def obs_local_part(email_info, parser, position):
    """
        obs-local-part = word *("." word)

    """
    tmp_word = email_info.word(position)
    tmp_ret = email_info.fb(position)

    if not tmp_word:
        return tmp_ret

    tmp_ret += tmp_word

    tmp_ret += email_info.try_and(position + tmp_ret,
                            email_info.single_dot,
                            email_info.word,
                            min_loop=0, max_loop=256)

    if 'CFWS_COMMENT' in tmp_ret:
        tmp_ret('DEPREC_COMMENT')

    return tmp_ret

@email_parser()
def word(email_info, parser, position):
    """
        word = atom / quoted-string
    """
    email_info.at_in_cfws = False
    tmp_ret = email_info.fb(position)
    # tmp_act, tmp_ret2 = email_info.try_or(position,
    #                       email_info.atom,
    #                       email_info.quoted_string)

    tmp_ret_2 = email_info.atom(position)
    if tmp_ret_2 and not tmp_ret_2.error:
        return tmp_ret(tmp_ret_2)

    tmp_ret_3 = email_info.quoted_string(position)
    if tmp_ret_3 and not tmp_ret_3.error:
        return tmp_ret(tmp_ret_3)

    return tmp_ret(email_info.football_max(tmp_ret_2, tmp_ret_3, names=['atom', 'quoted_string']))

@email_parser()
def atom(email_info, parser, position, init_cfws=None):
    """
            atom = [CFWS] 1*atext [CFWS]

            // The entire local-part can be a quoted string for RFC 5321
            // If it's just one atom that is quoted then it's an RFC 5322 obsolete form
    """

    tmp_ret = email_info.fb(position)

    if init_cfws is None:
        tmp_ret += email_info.cfws(position)
    else:
        tmp_ret += init_cfws

    tmp_ret.flags -= 'CFWS_LAST'

    email_info.near_at_flag = False

    tmp_ret_2 = email_info.atext(position + tmp_ret)

    if not tmp_ret_2:
        return tmp_ret('ERR_EXPECTING_ATEXT')

    tmp_ret += tmp_ret_2
    tmp_ret_cfws = email_info.cfws(position + tmp_ret)

    tmp_ret += tmp_ret_cfws

    if tmp_ret and tmp_ret_cfws:
        email_info.add_note_trace('Found last CFWS')
        if not (email_info.at_end(position + tmp_ret + tmp_ret_cfws) or
                        email_info.this_char(position + tmp_ret + tmp_ret_cfws) == email_info.AT or
                        email_info.this_char(position + tmp_ret + tmp_ret_cfws) == email_info.DOT):
            tmp_ret('ERR_ATEXT_AFTER_CFWS', raise_on_error=False)

    # if not tmp_ret or tmp_ret.error:
    #     email_info.near_at_flag = tmp_near_at_flag

    return tmp_ret

@email_parser()
def domain(email_info, parser, position):

    """
    domain          =   dot-atom / domain-literal / address_literal /obs-domain
        ---------------------------------------------------------------------------------------------
        ; NB For SMTP mail, the domain-literal is restricted by RFC5321 as follows:
                Mailbox        = Local-part "@" ( domain-addr / address-literal )
        -----------------------------------------------------------------------------------------

        // http://tools.ietf.org/html/rfc5322#section-3.4.1
        //      Note: A liberal syntax for the domain portion of addr-spec is
        //      given here.  However, the domain portion contains addressing
        //      information specified by and used in other protocols (e.g.,
        //      [RFC1034], [RFC1035], [RFC1123], [RFC5321]).  It is therefore
        //      incumbent upon implementations to conform to the syntax of
        //      addresses for the context in which they are used.
        // is_email() author's note: it's not clear how to interpret this in
        // the context of a general email address validator. The conclusion I
        // have reached is this: "addressing information" must comply with
        // RFC 5321 (and in turn RFC 1035), anything that is "semantically
        // invisible" must comply only with RFC 5322.

        // http://tools.ietf.org/html/rfc5321#section-4.5.3.1.2
        //   The maximum total length of a domain name or number is 255 octets.

        // http://tools.ietf.org/html/rfc5321#section-4.1.2
        //   Forward-path   = Path
        //
        //   Path           = "<" [ A-d-l ":" ] Mailbox ">"
        //
        // http://tools.ietf.org/html/rfc5321#section-4.5.3.1.3
        //   The maximum total length of a reverse-path or forward-path is 256
        //   octets (including the punctuation and element separators).
        //
        // Thus, even without (obsolete) routing information, the Mailbox can
        // only be 254 characters long. This is confirmed by this verified
        // erratum to RFC 3696:
        //
        // http://www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690
        //   However, there is a restriction in RFC 2821 on the length of an
        //   address in MAIL and RCPT commands of 254 characters.  Since addresses
        //   that do not fit in those fields are not normally useful, the upper
        //   limit on address lengths should normally be considered to be 254.



        //  dns check
        // http://tools.ietf.org/html/rfc5321#section-2.3.5
        //   Names that can
        //   be resolved to MX RRs or address (i.e., A or AAAA) RRs (as discussed
        //   in Section 5) are permitted, as are CNAME RRs whose targets can be
        //   resolved, in turn, to MX or address RRs.
        //
        // http://tools.ietf.org/html/rfc5321#section-5.1
        //   The lookup first attempts to locate an MX record associated with the
        //   name.  If a CNAME record is found, the resulting name is processed as
        //   if it were the initial name. ... If an empty list of MXs is returned,
        //   the address is treated as if it was associated with an implicit MX
        //   RR, with a preference of 0, pointing to that host.
        //
        // is_email() author's note: We will regard the existence of a CNAME to be
        // sufficient evidence of the domain's existence. For performance reasons
        // we will not repeat the DNS lookup for the CNAME's target, but we will
        // raise a warning because we didn't immediately find an MX record.

        // dns tld
        // Check for TLD addresses
        // -----------------------
        // TLD addresses are specifically allowed in RFC 5321 but they are
        // unusual to say the least. We will allocate a separate
        // status to these addresses on the basis that they are more likely
        // to be typos than genuine addresses (unless we've already
        // established that the domain does have an MX record)
        //
        // http://tools.ietf.org/html/rfc5321#section-2.3.5
        //   In the case
        //   of a top-level domain used by itemail_info in an email address, a single
        //   string is used without any dots.  This makes the requirement,
        //   described in more detail below, that only fully-qualified domain
        //   names appear in SMTP transactions on the public Internet,
        //   particularly important where top-level domains are involved.
        //
        // TLD format
        // ----------
        // The format of TLDs has changed a number of times. The standards
        // used by IANA have been largely ignored by ICANN, leading to
        // confusion over the standards being followed. These are not defined
        // anywhere, except as a general component of a DNS host name (a label).
        // However, this could potentially lead to 123.123.123.123 being a
        // valid DNS name (rather than an IP address) and thereby creating
        // an ambiguity. The most authoritative statement on TLD formats that
        // the author can find is in a (rejected!) erratum to RFC 1123
        // submitted by John Klensin, the author of RFC 5321:
        //
        // http://www.rfc-editor.org/errata_search.php?rfc=1123&eid=1353
        //   However, a valid host name can never have the dotted-decimal
        //   form #.#.#.#, since this change does not permit the highest-level
        //   component label to start with a digit even if it is not all-numeric.

        domain          =   dot-atom / domain-literal / address_literal /obs-domain

     [1005]      DNSWARN_NO_MX_RECORD  Couldn't find an MX record for this domain but an A-record does exist (ISEMAIL_DNSWARN)
    [1006]         DNSWARN_NO_RECORD  Couldn't find an MX record or an A-record for this domain (ISEMAIL_DNSWARN)
    [1065]            RFC5322_DOMAIN  Address is RFC 5322 compliant but contains domain characters that are not allowed by DNS (ISEMAIL_RFC5322)
    [1068]   RFC5322_DOMAIN_TOO_LONG  The domain part is too long (ISEMAIL_RFC5322)
    [1069]    RFC5322_LABEL_TOO_LONG  The domain part contains an element that is too long (ISEMAIL_RFC5322)
    [1143]   ERR_DOMAIN_HYPHEN_START  A domain or subdomain cannot begin with a hyphen (ISEMAIL_ERR)
    [1144]     ERR_DOMAIN_HYPHEN_END  A domain or subdomain cannot end with a hyphen (ISEMAIL_ERR)
    """
    tmp_ret = email_info.fb(position)

    only_domain_lit = False
    is_literal = False
    # has_cfws = False

    lit_init = email_info.fb(position)
    lit_sb = email_info.open_sq_bracket(position)

    if lit_sb:
        is_literal = True
        lit_init += lit_sb
        lit_cfws = email_info.fb(position)
    else:
        lit_cfws = email_info.cfws(position)
        if lit_cfws:
            # has_cfws = True
            lit_init += lit_cfws
            lit_sb += email_info.open_sq_bracket(position + lit_cfws)
            if lit_sb:
                is_literal = True
                only_domain_lit = True
                lit_init += lit_sb

    if is_literal:
        tmp_ret += email_info._domain_literals(position, lit_init, only_domain_lit)
    else:
        tmp_char = email_info.this_char(position)
        if tmp_char == email_info.HYPHEN:
            return tmp_ret('ERR_DOMAIN_HYPHEN_START')
        elif tmp_char == email_info.DOT:
            return tmp_ret('ERR_DOT_START')

        tmp_ret += email_info._domain_non_literals(position, lit_cfws)

    if is_literal:
        extra_text_error = 'ERR_ATEXT_AFTER_DOMLIT'
    elif 'RFC5322_LIMITED_DOMAIN' in tmp_ret:
        if 'CFWS_LAST' in tmp_ret.flags:
            extra_text_error = 'ERR_ATEXT_AFTER_CFWS'
        else:
            extra_text_error = 'ERR_EXPECTING_ATEXT'
    else:
        extra_text_error = 'ERR_EXPECTING_DTEXT'

    if not email_info.at_end(position + tmp_ret):
        tmp_ret(extra_text_error)
    else:
        if tmp_ret > 255:
            tmp_ret('RFC5322_DOMAIN_TOO_LONG')

        last_char = email_info.this_char(-1)

        if last_char == email_info.HYPHEN:
            tmp_ret('ERR_DOMAIN_HYPHEN_END')
        elif last_char == email_info.BACKSLASH:
            tmp_ret('ERR_BACKSLASH_END')
        elif last_char == email_info.DOT:
            tmp_ret('ERR_DOT_END')

    if tmp_ret.error:
        raise ParsingError(tmp_ret)

    return tmp_ret

def _domain_non_literals(email_info, parser, position, init_cfws=None):

    if not init_cfws:
        tmp_domain_addr = email_info.domain_addr(position)
        if tmp_domain_addr:
            return tmp_domain_addr
    else:
        tmp_domain_addr = email_info.fb(position)

    tmp_dot_atom = email_info.domain_dot_atom(position, init_cfws=init_cfws)
    if tmp_dot_atom:
        return tmp_dot_atom

    tmp_obs_domain = email_info.obs_domain(position, init_cfws=init_cfws)
    if tmp_obs_domain:
        return tmp_obs_domain

    return email_info.football_max(tmp_domain_addr, tmp_dot_atom, tmp_obs_domain,
                             names=['domain_addr', 'dot_atom', 'obs_domain'])

def _domain_literals(email_info, parser, position, init_lit, only_domain_lit):

    tmp_close_loc = email_info.find(position + init_lit, email_info.CLOSESQBRACKET)
    if tmp_close_loc == -1:
        tmp_ret = email_info.fb(position)
        return tmp_ret('ERR_UNCLOSED_DOM_LIT')

    if not only_domain_lit:
        tmp_addr_lit = email_info.address_literal(position, init_lit)
        if tmp_addr_lit:
            return tmp_addr_lit
    else:
        tmp_addr_lit = email_info.fb(position)

    tmp_dom_lit = email_info.domain_literal(position, init_lit)
    if tmp_dom_lit:
        return tmp_dom_lit

    return email_info.football_max(tmp_addr_lit, tmp_dom_lit, names=['addr_lit', 'domain_lit'])

# @email_parser(segment=False)
# def literals(email_info, parser, position):
#     only_domain_lit = False
#     tmp_ret = email_info.fb(position)
#     tmp_ret_2 = email_info.open_sq_bracket(position)
#
#     if not email_info.open_sq_bracket(position, non_segment=True):
#         tmp_ret_2 += email_info.cfws(position, non_segment=True)
#         if tmp_ret:
#             tmp_ret_2 += email_info.open_sq_bracket(position + tmp_ret, non_segment=True)
#             only_domain_lit = True
#         else:
#             return tmp_ret
#
#     tmp_close_loc = email_info.find(position + tmp_ret_2, email_info.CLOSESQBRACKET)
#     if tmp_close_loc == -1:
#         return tmp_ret('ERR_UNCLOSED_DOM_LIT')
#
#     tmp_ret_2 = email_info.fb(position)
#     if not only_domain_lit:
#         try:
#             tmp_ret_2 = email_info.address_literal(position)
#         except ParsingError as err:
#             tmp_ret_2 = err.results
#
#     if tmp_ret_2:
#         if email_info.at_end(position + tmp_ret_2):
#             return tmp_ret(tmp_ret_2)
#         else:
#             if not tmp_ret_2.error:
#                 tmp_ret += tmp_ret_2
#                 return tmp_ret('ERR_ATEXT_AFTER_DOMLIT')
#
#     email_info.add_note_trace('Should be non-ip-address domain literal')
#     tmp_ret_3 = email_info.domain_literal(position)
#     if tmp_ret_3:
#         tmp_ret_3('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN')
#         tmp_ret += tmp_ret_3
#         if not email_info.at_end(position + tmp_ret_3):
#             tmp_ret += tmp_ret_3
#             return tmp_ret('ERR_ATEXT_AFTER_DOMLIT')
#
#     tmp_index, tmp_ret_4 = email_info.football_max(tmp_ret_2, tmp_ret_3)
#     tmp_ret += tmp_ret_4
#     if tmp_ret.error:
#         raise ParsingError(tmp_ret_2)
#
#     if not email_info.at_end(position + tmp_ret):
#         return tmp_ret('ERR_ATEXT_AFTER_DOMLIT')
#
#     add_to = []
#
#     if email_info.at_end(position + tmp_ret - 1) or email_info.at_end(position + tmp_ret):
#         added_char = 0
#         tmp_char = email_info.this_char(-1)
#         email_info.add_note_trace('Final domain char = ' + tmp_char)
#         if tmp_char == email_info.HYPHEN:
#             added_char = 1
#             add_to.append('ERR_DOMAIN_HYPHEN_END')
#         elif tmp_char == email_info.DOT:
#             added_char = 1
#             add_to.append('ERR_DOT_END')
#         elif tmp_char == email_info.BACKSLASH:
#             added_char = 1
#             add_to.append('ERR_BACKSLASH_END')
#
#         if not email_info.at_end(position + tmp_ret + added_char):
#             add_to.append('ERR_EXPECTING_ATEXT')
#
#         if tmp_ret > 255:
#             add_to.append('RFC5322_DOMAIN_TOO_LONG')
#
#         email_info.add_note_trace('    Domain Validation: At end, diags to add: %s' % add_to)
#
#         tmp_ret(*add_to, raise_on_error=False)
#
#     return tmp_ret('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN')
#
#     return tmp_ret


@email_parser()
def domain_addr(email_info, parser, position):
    """
    domain-addr = sub-domain *("." sub-domain)
    [1009]               RFC5321_TLD  Address is valid but at a Top Level Domain (ISEMAIL_RFC5321)
    [1010]       RFC5321_TLD_NUMERIC  Address is valid but the Top Level Domain begins with a number (ISEMAIL_RFC5321)

    """
    last_dom_pos = position
    is_tld = True
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.sub_domain(position)
    # if not tmp_ret:
    #     tmp_ret = email_info.sub_domain(position)
    #     if tmp_ret:
    #         tmp_ret('RFC5321_TLD_NUMERIC')

    if not tmp_ret:
        return tmp_ret

    while True:
        tmp_ret_2 = email_info.single_dot(position + tmp_ret)
        if not tmp_ret_2:
            break
        tmp_ret_3 = email_info.sub_domain(position + tmp_ret + tmp_ret_2)
        if not tmp_ret_3:
            break
        last_dom_pos = position + tmp_ret + tmp_ret_2
        tmp_ret += tmp_ret_2
        tmp_ret += tmp_ret_3
        is_tld = False

    if is_tld:
        tmp_ret('RFC5321_TLD')

    if email_info.this_char(last_dom_pos) in email_info.DIGIT:
        tmp_ret('RFC5321_TLD_NUMERIC')
        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.OTHER_NON_DNS
    else:
        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.DNS

    return tmp_ret

    # add_to = []
    #
    # if email_info.at_end(position + tmp_ret + 1):
    #
    #     tmp_ret_2 = email_info.single_char(position + tmp_ret, email_info.HYPHEN)
    #     if tmp_ret_2:
    #         tmp_ret += tmp_ret_2
    #         tmp_ret('ERR_DOMAIN_HYPHEN_END', raise_on_error=False)
    #
    #     tmp_ret_2 = email_info.single_char(position + tmp_ret, email_info.DOT)
    #     if tmp_ret_2:
    #         tmp_ret += tmp_ret_2
    #         tmp_ret('ERR_DOT_END', raise_on_error=False)
    #
    #     tmp_ret_2 = email_info.single_char(position + tmp_ret, email_info.BACKSLASH)
    #     if tmp_ret_2:
    #         tmp_ret += tmp_ret_2
    #         tmp_ret('ERR_BACKSLASH_END', raise_on_error=False)
    #
    # elif not email_info.at_end(position + tmp_ret):
    #     add_to.append('ERR_EXPECTING_DTEXT')
    #
    # if tmp_ret > 255:
    #      add_to.append('RFC5322_DOMAIN_TOO_LONG')
    #
    # return tmp_ret(*add_to, raise_on_error=False)

# @email_parser()
# def tld_domain(email_info, parser, position):
#     """"
#         sub-domain     = Let-dig [Ldh-str]
#
#         // Nowhere in RFC 5321 does it say explicitly that the
#         // domain part of a Mailbox must be a valid domain according
#         // to the DNS standards set out in RFC 1035, but this *is*
#         // implied in several places. For instance, wherever the idea
#         // of host routing is discussed the RFC says that the domain
#         // must be looked up in the DNS. This would be nonsense unless
#         // the domain was designed to be a valid DNS domain. Hence we
#         // must conclude that the RFC 1035 restriction on label length
#         // also applies to RFC 5321 domains.
#         //
#         // http://tools.ietf.org/html/rfc1035#section-2.3.4
#         // labels          63 octets or less
#
#     """
#     tmp_ret = email_info.fb(position)
#     tmp_ret += email_info.alpha(position)
#     if tmp_ret:
#         tmp_ret += email_info.ldh_str(position + tmp_ret)
#         if tmp_ret.l > 63:
#             tmp_ret('RFC5322_LABEL_TOO_LONG')
#         return tmp_ret
#     else:
#         return email_info.fb(position)

@email_parser()
def sub_domain(email_info, parser, position):
    """"
        sub-domain     = Let-dig [Ldh-str]

        // Nowhere in RFC 5321 does it say explicitly that the
        // domain part of a Mailbox must be a valid domain according
        // to the DNS standards set out in RFC 1035, but this *is*
        // implied in several places. For instance, wherever the idea
        // of host routing is discussed the RFC says that the domain
        // must be looked up in the DNS. This would be nonsense unless
        // the domain was designed to be a valid DNS domain. Hence we
        // must conclude that the RFC 1035 restriction on label length
        // also applies to RFC 5321 domains.
        //
        // http://tools.ietf.org/html/rfc1035#section-2.3.4
        // labels          63 octets or less

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.let_dig(position)
    if tmp_ret:
        tmp_ret += email_info.ldh_str(position + tmp_ret)

        if tmp_ret.l > 63:
            tmp_ret('RFC5322_LABEL_TOO_LONG')

        return tmp_ret
    else:
        return email_info.fb(position)

# @email_parser()
# def let_str(email_info, parser, position):
#     """
#             Ldh-str        = *( ALPHA / DIGIT / "-" ) Let-dig
#     """
#     tmp_ret = email_info.fb(position)
#     tmp_ret += email_info.ldh_str(position)
#
#     while tmp_ret and email_info.this_char(position + tmp_ret.l-1) not in email_info.LET_DIG:
#         tmp_ret -= 1
#
#     if tmp_ret:
#         return tmp_ret
#
#     return email_info.fb(position)

@email_parser(diags=['RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_LIMITED_DOMAIN'])
def domain_literal(email_info, parser, position, lit_init=None):
    """
    domain-literal  =   [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
    // Domain literal must be the only component

    [1070]    RFC5322_DOMAIN_LITERAL  The domain literal is not a valid RFC 5321 address literal (ISEMAIL_RFC5322)
    [1129]       ERR_EXPECTING_DTEXT  A domain literal contains a character that is not allowed (ISEMAIL_ERR)
    [1135]    ERR_ATEXT_AFTER_DOMLIT  Extra characters were found after the end of the domain literal (ISEMAIL_ERR)
    [1147]      ERR_UNCLOSED_DOM_LIT  Domain literal is missing its closing bracket (ISEMAIL_ERR)
    """
    tmp_ret = email_info.fb(position)
    if lit_init is None:
        lit_init = email_info.fb(position)
        lit_init += email_info.cfws(position)
        lit_init_sb = email_info.open_sq_bracket(position + lit_init)
        if not lit_init_sb:
            return tmp_ret
        else:
            lit_init += lit_init_sb

    lit_init.flags -= 'CFWS_LAST'

    tmp_ret += lit_init

    # tmp_ret += email_info.cfws(position)
    # tmp_near_at_flag = email_info.near_at_flag
    email_info.near_at_flag = False
    # tmp_ret_2 = email_info.open_sq_bracket(position + tmp_ret.l)

    # if not tmp_ret_2:
    # email_info.near_at_flag = tmp_near_at_flag
    #     return email_info.fb(position)

    # tmp_loc_close = email_info.find(position + tmp_ret, email_info.CLOSESQBRACKET)
    # if tmp_loc_close == -1:
    #     return tmp_ret('ERR_UNCLOSED_DOM_LIT')

    # tmp_ret += tmp_ret_2

    # tmp_ret_2 = email_info.domain_literal_sub(position + tmp_ret, non_segment=True)
    # ************************
    tmp_ret_2 = email_info.fb(position)
    has_dtext = False
    while True:
        tmp_ret_fws = email_info.fws(position + tmp_ret + tmp_ret_2)

        tmp_ret_dtext = email_info.dtext(position + tmp_ret + tmp_ret_2 + tmp_ret_fws)

        if tmp_ret_dtext:
            tmp_ret_2 += tmp_ret_fws
            tmp_ret_2 += tmp_ret_dtext
            has_dtext = True
        else:
            break

    if tmp_ret_2:
        if not has_dtext:
            tmp_ret += tmp_ret_2
            return tmp_ret('ERR_EXPECTING_DTEXT', raise_on_error=False)
        tmp_ret_2 += email_info.fws(position + tmp_ret + tmp_ret_2)
    else:
        # email_info.near_at_flag = tmp_near_at_flag
        return tmp_ret('ERR_EXPECTING_DTEXT', raise_on_error=False)

    tmp_ret += tmp_ret_2

    tmp_ret_2 = email_info.close_sq_bracket(position + tmp_ret)

    if tmp_ret_2:
        tmp_ret += tmp_ret_2
        if tmp_ret == 2:
            return tmp_ret('ERR_EXPECTING_DTEXT', raise_on_error=False)

    else:
        if email_info.at_end(position + tmp_ret):
            return tmp_ret('ERR_UNCLOSED_DOM_LIT', raise_on_error=False)
        else:
            return tmp_ret('ERR_EXPECTING_DTEXT', raise_on_error=False)

    tmp_ret += email_info.cfws(position + tmp_ret)

    if tmp_ret and not email_info.at_end(position + tmp_ret + 1):
        tmp_ret('ERR_ATEXT_AFTER_DOMLIT', raise_on_error=False)

    tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT

    if tmp_ret > 255:
        tmp_ret('RFC5322_DOMAIN_TOO_LONG', raise_on_error=False)

    return tmp_ret

# @email_parser()
# def domain_literal_sub(email_info, parser, position):
#     """
#     domain-literal-sub  =   *([FWS] dtext) [FWS]
#     """
#
#     tmp_ret = ParseResultFootball(email_info)
#     while True:
#         tmp_ret_fws = email_info.fws(position + tmp_ret.l)
#
#         tmp_ret_dtext = email_info.dtext(position + tmp_ret.l + tmp_ret_fws.l)
#
#         if tmp_ret_dtext:
#             tmp_ret += tmp_ret_fws
#             tmp_ret += tmp_ret_dtext
#         else:
#             break
#
#     if tmp_ret:
#         tmp_ret += email_info.fws(position + tmp_ret.l)
#
#     return tmp_ret

@email_parser()
def dtext(email_info, parser, position):

    """
        dtext           =   %d33-90 /          ; Printable US-ASCII
                           %d94-126 /         ;  characters not including
                           obs-dtext          ;  "[", "]", or "\"
    """
    tmp_ret = email_info.fb(position)

    while True:
        tmp_ret_2 = email_info.simple_char(position + tmp_ret, email_info.DTEXT)
        tmp_ret_2 += email_info.obs_dtext(position + tmp_ret + tmp_ret_2)
        if tmp_ret_2:
            tmp_ret += tmp_ret_2
        else:
            break

    # tmp_act, tmp_ret_2 = email_info.try_or(position,
    #                                email_info.dtext_sub,
    #                               email_info.obs_dtext)

    return tmp_ret

# @email_parser(segment=False)
# def dtext_sub(email_info, parser, position):
#
#     """
#         dtext           =   %d33-90 /          ; Printable US-ASCII
#                            %d94-126 /         ;  characters not including
#                            obs-dtext          ;  "[", "]", or "\"
#     """
#     return email_info.simple_char(position, email_info.DTEXT)

@email_parser(diags='RFC5322_DOM_LIT_OBS_DTEXT')
def obs_dtext(email_info, parser, position):

    """
            obs-dtext       =   obs-NO-WS-CTL / quoted-pair
    [1071] RFC5322_DOM_LIT_OBS_DTEXT  The domain literal is not a valid RFC 5321 address literal and it contains obsolete characters (ISEMAIL_RFC5322)

    """
    tmp_ret = email_info.fb(position)

    while True:
        tmp_ret_2 = email_info.obs_dtext_sub(position + tmp_ret)

        tmp_ret_2 += email_info.quoted_pair(position + tmp_ret + tmp_ret_2)

        if tmp_ret_2:
            tmp_ret += tmp_ret_2
        else:
            break

    return tmp_ret

@email_parser(diags=['RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN'])
def obs_domain(email_info, parser, position, init_cfws=None):
    """
    obs-domain      =   atom *("." atom)
            [1037]            DEPREC_COMMENT  Address contains a comment in a position that is deprecated (ISEMAIL_DEPREC)
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.atom(position, init_cfws=init_cfws)

    if not tmp_ret:
        return tmp_ret('ERR_EXPECTING_ATEXT', raise_on_error=False)

    tmp_ret += email_info.try_and(position + tmp_ret.l,
                            email_info.single_dot,
                            email_info.atom,
                            min_loop=0, max_loop=256)

    tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.OTHER_NON_DNS

    add_to = []

    if email_info.at_end(position + tmp_ret + 1):
        # added_char = 0
        # tmp_char = email_info.this_char(-1)
        # email_info.add_note_trace('Final domain char = ' + tmp_char)
        tmp_ret_2 = email_info.single_char(position + tmp_ret, email_info.HYPHEN)
        if tmp_ret_2:
            tmp_ret += tmp_ret_2
            tmp_ret('ERR_DOMAIN_HYPHEN_END', raise_on_error=False)

        tmp_ret_2 = email_info.single_char(position + tmp_ret, email_info.DOT)
        if tmp_ret_2:
            tmp_ret += tmp_ret_2
            tmp_ret('ERR_DOT_END', raise_on_error=False)

        tmp_ret_2 = email_info.single_char(position + tmp_ret, email_info.BACKSLASH)
        if tmp_ret_2:
            tmp_ret += tmp_ret_2
            tmp_ret('ERR_BACKSLASH_END', raise_on_error=False)

        if tmp_ret > 255:
            add_to.append('RFC5322_DOMAIN_TOO_LONG')

    elif email_info.at_end(position + tmp_ret):
        add_to.append('ERR_EXPECTING_DTEXT')

    tmp_ret(*add_to, raise_on_error=False)

    return tmp_ret

@email_parser(diags='RFC5321_ADDRESS_LITERAL')
def address_literal(email_info, parser, position, lit_init=None):
    """
    address-literal  = "[" ( IPv4-address-literal /
                    IPv6-address-literal /
                    General-address-literal ) "]"

    [1012]   RFC5321_ADDRESS_LITERAL  Address is valid but at a literal address not a domain (ISEMAIL_RFC5321)
    ERR_UNCLOSED_DOM_LIT  Unclosed domain literal.

    ERR_INVALID_ADDR_LITERAL
    """

    tmp_ret = email_info.fb(position)
    if lit_init is None:
        lit_init = email_info.open_sq_bracket(position)
        if not lit_init:
            return tmp_ret

    tmp_ipv4 = email_info.ipv4_address_literal(position + tmp_ret + lit_init)
    if tmp_ipv4:
        tmp_csb = email_info.close_sq_bracket(position + tmp_ret + lit_init + tmp_ipv4)
        if tmp_csb:
            return tmp_ret(lit_init, tmp_ipv4, tmp_csb)

    tmp_ipv6 = email_info.ipv6_address_literal(position + tmp_ret + lit_init)
    if tmp_ipv6:
        tmp_csb = email_info.close_sq_bracket(position + tmp_ret + lit_init + tmp_ipv6)
        if tmp_csb:
            return tmp_ret(lit_init, tmp_ipv6, tmp_csb)

    tmp_gen_lit = email_info.general_address_literal(position + tmp_ret + lit_init)
    if tmp_gen_lit:
        tmp_csb = email_info.close_sq_bracket(position + tmp_ret + lit_init + tmp_gen_lit)
        if tmp_csb:
            tmp_ret('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN')
            return tmp_ret(lit_init, tmp_gen_lit, tmp_csb)

    tmp_ret = email_info.football_max(tmp_ipv4, tmp_ipv6, tmp_gen_lit, names=['ipv4', 'ipv6', 'gen_lit'])

    if not tmp_ret:
        return tmp_ret

    tmp_ret_2 = email_info.close_sq_bracket(position + tmp_ret)

    if tmp_ret_2:
        return tmp_ret(tmp_ret_2)
    else:
        return tmp_ret('ERR_INVALID_ADDR_LITERAL', raise_on_error=False)

@email_parser(diags='RFC5322_GENERAL_LITERAL')
def general_address_literal(email_info, parser, position):
    """
    General-address-literal  = Standardized-tag ":" 1*dcontent

            RFC5322_GENERAL_LITERAL

    """
    tmp_ret = email_info.fb(position)
    tmp_ret_2 = email_info.try_and(position,
                             email_info.standardized_tag,
                             email_info.colon,
                             email_info.dcontent)
    if tmp_ret_2:
        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.GENERAL_LIT
        return tmp_ret(tmp_ret_2)
    else:
        return tmp_ret

@email_parser()
def standardized_tag(email_info, parser, position):
    """
        Standardized-tag  = Ldh-str
                         ; Standardized-tag MUST be specified in a
                         ; Standards-Track RFC and registered with IANA
    """
    if email_info.simple_str(position, 'IPv6:', False):
        return email_info.fb(position)

    tmp_ret = email_info.ldh_str(position)
    tmp_str = email_info.mid(position, tmp_ret.l)

    if tmp_str in ISEMAIL_ALLOWED_GENERAL_ADDRESS_LITERAL_STANDARD_TAGS:
        return tmp_ret
    else:
        return email_info.fb(position)

@email_parser()
def ldh_str(email_info, parser, position):
    """
        Ldh-str = *( ALPHA / DIGIT / "-" ) Let-dig
    """
    tmp_ret = email_info.sub_ldh_str(position)

    while email_info.this_char(position + tmp_ret - 1) == "-":
        tmp_ret -= 1
        if tmp_ret == 0:
            return tmp_ret
    return tmp_ret

@email_parser('RFC5322_IPV4_ADDR')
def ipv4_address_literal(email_info, parser, position):
    """
    IPv4-address-literal  = Snum 3("."  Snum)

    RFC5322_IPV4_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.try_and(position,
                            email_info.snum,
                            email_info.single_dot, email_info.snum,
                            email_info.single_dot, email_info.snum,
                            email_info.single_dot, email_info.snum)

    if tmp_ret:
        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.IPv4
    return tmp_ret

@email_parser()
def snum(email_info, parser, position):
    """
            Snum           = 1*3DIGIT
                          ; representing a decimal integer
                          ; value in the range 0 through 255
    """
    tmp_ret = email_info.three_digit(position)
    if tmp_ret:
        tmp_str = email_info.mid(position, tmp_ret.l)

        tmp_digit = int(tmp_str)
        if tmp_digit > 255:
            return email_info.fb(position)

    return tmp_ret

@email_parser(diags='RFC5322_IPV6_ADDR')
def ipv6_address_literal(email_info, parser, position):
    """
        IPv6-address-literal  = "IPv6:" IPv6-addr
    [1013]   RFC5321_IPV6_DEPRECATED  Address is valid but contains a :: that only elides one zero group. All implementations must accept and be able to handle any legitimate RFC 4291 format. (ISEMAIL_DEPREC)
    [1072]    RFC5322_IPV6_GRP_COUNT  The IPv6 literal address contains the wrong number of groups (ISEMAIL_RFC5322)
    [1073]   RFC5322_IPV6_2X2X_COLON  The IPv6 literal address contains too many :: sequences (ISEMAIL_RFC5322)
    [1074]     RFC5322_IPV6_BAD_CHAR  The IPv6 address contains an illegal group of characters (ISEMAIL_RFC5322)
    [1075]     RFC5322_IPV6_MAX_GRPS  The IPv6 address has too many groups (ISEMAIL_RFC5322)
    [1076]   RFC5322_IPV6_COLON_STRT  IPv6 address starts with a single colon (ISEMAIL_RFC5322)
    [1077]    RFC5322_IPV6_COLON_END  IPv6 address ends with a single colon (ISEMAIL_RFC5322)

    RFC5322_IPV6_ADDR
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.ipv6(position)

    if tmp_ret:
        tmp_ret_2 = email_info.ipv6_addr(position + tmp_ret)

        if tmp_ret_2:
            tmp_ret += tmp_ret_2
            tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.IPv6
            return tmp_ret

    return email_info.fb(position)

@email_parser()
def ipv6_addr(email_info, parser, position):
    """
            IPv6-addr      = IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp
    """
    tmp_ret = email_info.fb(position)

    dot_count = email_info.count(position, email_info.DOT, stop_for=email_info.CLOSESQBRACKET)

    email_info.add_note_trace('Dot count = ' + str(dot_count))
    if dot_count:
        tmp_ret += email_info.ipv6v4_full(position) or email_info.ipv6v4_comp(position)
    else:
        tmp_ret += email_info.ipv6_full(position) or email_info.ipv6_comp(position)

    return tmp_ret

@email_parser()
def ipv6_hex(email_info, parser, position):
    """
    IPv6-hex       = 1*4HEXDIG
    """
    return email_info.hexdigit(position)

@email_parser(diags='RFC5322_IPV6_FULL_ADDR')
def ipv6_full(email_info, parser, position):
    """
            IPv6-full      = IPv6-hex 7(":" IPv6-hex)
            RFC5322_IPV6_FULL_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_count, tmp_ret_2 = email_info.ipv6_segment(position, max_count=8, min_count=8)
    if tmp_ret_2:
        return tmp_ret(tmp_ret_2)
    else:
        return email_info.fb(position)

@email_parser(diags='RFC5322_IPV6_COMP_ADDR')
def ipv6_comp(email_info, parser, position):
    """
            IPv6-comp      = [IPv6-hex *5(":" IPv6-hex)] "::"
                          [IPv6-hex *5(":" IPv6-hex)]
                          ; The "::" represents at least 2 16-bit groups of
                          ; zeros.  No more than 6 groups in addition to the
                          ; "::" may be present.
          RFC5322_IPV6_COMP_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_pre_count, tmp_ret_2 = email_info.ipv6_segment(position, min_count=1, max_count=6)

    if not tmp_ret_2:
        return email_info.fb(position)
    tmp_ret += tmp_ret_2

    tmp_ret_2 = email_info.double_colon(position + tmp_ret)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2

    tmp_post_count, tmp_ret_2 = email_info.ipv6_segment(position + tmp_ret.l, min_count=1, max_count=6)

    if not tmp_ret_2:
        tmp_ret_2 = email_info.ipv6_hex(position + tmp_ret.l)
        if not tmp_ret_2:
            return email_info.fb(position)
        tmp_post_count = 1

    tmp_ret += tmp_ret_2
    if (tmp_pre_count + tmp_post_count) > 6:
        email_info.add_note_trace('Segment count: %s + %s, exceeds 6, failing' % (tmp_pre_count, tmp_post_count))
        return email_info.fb(position)

    else:
        email_info.add_note_trace('Segment count: %s + %s, passing' % (tmp_pre_count, tmp_post_count))
        return tmp_ret

@email_parser(diags='RFC5322_IPV6_IPV4_ADDR')
def ipv6v4_full(email_info, parser, position):
    """
            IPv6v4-full    = IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal

                    RFC5322_IPV6_IPV4_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_count, tmp_ret_2 = email_info.ipv6_segment(position, min_count=6, max_count=6)
    tmp_ret += tmp_ret_2

    if tmp_ret_2:
        tmp_ret_2 = email_info.colon(position + tmp_ret)
    else:
        return email_info.fb(position)

    if tmp_ret_2:
        tmp_ret += tmp_ret_2
        tmp_ret_2 = email_info.ipv4_address_literal(position + tmp_ret.l)
    else:
        return email_info.fb(position)

    if tmp_ret_2:
        tmp_ret += tmp_ret_2
    else:
        return email_info.fb(position)

    tmp_ret.remove('RFC5322_IPV4_ADDR')
    return tmp_ret

@email_parser(diags='RFC5322_IPV6_IPV4_COMP_ADDR')
def ipv6v4_comp(email_info, parser, position):
    """
            IPv6v4-comp    = [IPv6-hex *3(":" IPv6-hex)] "::"
                          [IPv6-hex *3(":" IPv6-hex) ":"]
                          IPv4-address-literal
                          ; The "::" represents at least 2 16-bit groups of
                          ; zeros.  No more than 4 groups in addition to the
                          ; "::" and IPv4-address-literal may be present.
            RFC5322_IPV6_IPV4_COMP_ADDR


    """
    tmp_ret = email_info.fb(position)
    tmp_pre_count, tmp_ret_2 = email_info.ipv6_segment(position, min_count=1, max_count=3)
    tmp_ret += tmp_ret_2

    if not tmp_ret:
        return email_info.fb(position)

    tmp_ret_2 = email_info.double_colon(position + tmp_ret)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2

    colon_count = email_info.count(position + tmp_ret, email_info.COLON, stop_for=email_info.CLOSESQBRACKET)
    if colon_count > 3:
        return email_info.fb(position)

    tmp_post_count, tmp_ret_2 = email_info.ipv6_segment(position + tmp_ret.l, min_count=colon_count,
                                                  max_count=colon_count)

    """
    if not tmp_ret_2 or tmp_post_count == 1:
        return email_info.fb(position)

    email_info.add_note_trace('found end of ipv6 segments at segment: %s RESTARTING' % str(tmp_post_count))

    tmp_colon_count = email_info.count(position + tmp_ret.l + tmp_ret_2.l, search_for=':', length=10)
    email_info.add_note_trace('Checking for more colons, found %s more in %s' % (tmp_colon_count, email_info.mid(position + tmp_ret.l + tmp_ret_2.l, 10)))

    if tmp_colon_count == 1:
        tmp_post_count += 1

    tmp_post_count, tmp_ret_2 = email_info.ipv6_segment(position + tmp_ret.l, min_count=tmp_post_count-1, max_count=tmp_post_count-1)
    if not tmp_ret_2:
        return email_info.fb(position)
    """
    email_info.add_note_trace('should be start of IPv4 segment')

    tmp_ret += tmp_ret_2
    tmp_ret_2 = email_info.colon(position + tmp_ret)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2
    tmp_ret_2 = email_info.ipv4_address_literal(position + tmp_ret.l)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2

    if tmp_pre_count + tmp_post_count > 4:
        email_info.add_note_trace('Segment count: %s + %s, exceeds 4, failing' % (tmp_pre_count, tmp_post_count))
        return email_info.fb(position)

    else:
        email_info.add_note_trace('Segment count: %s + %s, passing' % (tmp_pre_count, tmp_post_count))
        tmp_ret.remove('RFC5322_IPV4_ADDR')
        return tmp_ret

@email_parser(skip=True)
def cfws(email_info, parser, position):
    """
    CFWS   =   (1*([FWS] comment) [FWS]) / FWS
        // http://tools.ietf.org/html/rfc5322#section-3.4.1
        //   Comments and folding white space
        //   SHOULD NOT be used around the "@" in the addr-spec.

    """

    tmp_ret = email_info.fb(position)

    if not email_info.pre_cfws(position):
        return tmp_ret

    tmp_ret_fws = email_info.fws(position)
    tmp_ret_comment = email_info.comment(position + tmp_ret_fws)
    if tmp_ret_comment:
        tmp_ret += tmp_ret_fws
        tmp_ret += tmp_ret_comment
        tmp_ret += email_info.fws(position + tmp_ret)

        # tmp_find = email_info.count(position, email_info.AT, length=tmp_ret.l)
        # email_info.add_note_trace('pre (1) checking for AT count: %s in: %s' % (tmp_find, email_info.mid(position, tmp_ret.l)))

        # if tmp_ret:

        # email_info.at_in_cfws = email_info.AT in email_info.mid(position, tmp_ret.l)

        # if email_info.at_in_cfws and email_info.near_at_flag:
        #    tmp_ret('DEPREC_CFWS_NEAR_AT')

        # email_info.add_note_trace('post (1) checking at_in_cfws: %s' % email_info.at_in_cfws)

        # return tmp_ret

    # tmp_ret += email_info.fws(position)

    if 'CFWS_LAST' in tmp_ret.flags and email_info.AT in email_info.mid(position, tmp_ret.l):
        tmp_ret('DEPREC_CFWS_NEAR_AT')

    if tmp_ret:
        tmp_ret.flags += 'CFWS_LAST'

    # email_info.add_note_trace('post (2) checking at_in_cfws: %s' % email_info.at_in_cfws)

    return tmp_ret

@email_parser(segment=False)
def sub_cfws(email_info, parser, position):
    """
    sub_CFWS = (1*([FWS] comment) [FWS])
        // http://tools.ietf.org/html/rfc5322#section-3.4.1
        //   Comments and folding white space
        //   SHOULD NOT be used around the "@" in the addr-spec.

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.fws(position)
    tmp_ret += email_info.no_at(position + tmp_ret.l)
    tmp_ret += email_info.comment(position + tmp_ret.l)
    if tmp_ret:
        tmp_ret += email_info.no_at(position + tmp_ret.l)
        tmp_ret += email_info.fws(position + tmp_ret.l)
    return tmp_ret

@email_parser(comment=True, diags='CFWS_COMMENT')
def comment(email_info, parser, position):
    """
        comment         =   "(" *([FWS] ccontent) [FWS] ")"
            // http://tools.ietf.org/html/rfc5322#section-3.2.2
            //   Runs of FWS, comment, or CFWS that occur between lexical tokens in a
            //   structured header field are semantically interpreted as a single
            //   space character.
            //
            // is_email() author's note: This *cannot* mean that we must add a
            // space to the address wherever CFWS appears. This would result in
            // any addr-spec that had CFWS outside a quoted string being invalid
                    // for RFC 5321.

    [1017]              CFWS_COMMENT  Address contains comments (ISEMAIL_CFWS)
    [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign (ISEMAIL_DEPREC)
    [1146]      ERR_UNCLOSED_COMMENT  Unclosed comment (ISEMAIL_ERR)
    [1152]     ERR_MULT_FWS_IN_COMMENT Address contains multiple FWS in a comment (ISEMAIL_ERR)

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.open_parenthesis(position)

    email_info.add_note_trace('Return from openparen = %s' % tmp_ret.l)

    if not tmp_ret:
        return email_info.fb(position)

    last_was_fws = False
    has_close_quotes = False

    while True:
        action_name, tmp_loop_1 = email_info.try_or(position + tmp_ret.l,
                                              email_info.ccontent,
                                              email_info.fws,
                                              email_info.close_parenthesis)

        if action_name == 'close_parenthesis':
            tmp_ret += tmp_loop_1
            has_close_quotes = True
            break

        elif action_name == 'no_at':
            tmp_ret += tmp_loop_1
            last_was_fws = False

        elif action_name == 'fws':
            tmp_loop_1.remove('CFWS_FWS')
            if last_was_fws:
                tmp_ret += tmp_loop_1
                return tmp_ret("ERR_MULT_FWS_IN_COMMENT")
            else:
                last_was_fws = True
                tmp_ret += tmp_loop_1

        elif action_name == 'ccontent':
            last_was_fws = False
            tmp_ret += tmp_loop_1

        elif action_name == '':
            if email_info.at_end(position + tmp_loop_1 + tmp_ret) or email_info.this_char(
                                    position + tmp_loop_1 + tmp_ret) == email_info.AT:
                tmp_ret('ERR_UNCLOSED_COMMENT')
            tmp_ret('ERR_EXPECTING_CTEXT')
            break
        else:
            raise AttributeError('Invalid Action Name: %s' % action_name)

    if not has_close_quotes:
        return tmp_ret('ERR_UNCLOSED_COMMENT')

    return tmp_ret

@email_parser()
def ccontent(email_info, parser, position):
    """
    ccontent        =   ctext / quoted-pair / comment

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.ctext(position) or email_info.quoted_pair(position) or email_info.comment(position)
    return tmp_ret

@email_parser()
def ctext(email_info, parser, position):
    """
    ctext           =   %d33-39 /          ; Printable US-ASCII
                       %d42-91 /          ;  characters not including
                       %d93-126 /         ;  "(", ")", or "\"
                       obs-ctext
    [1139]       ERR_EXPECTING_CTEXT  A comment contains a character that is not allowed (ISEMAIL_ERR)

    """
    tmp_ret = email_info.fb(position)
    return tmp_ret(email_info.sub_ctext(position) or email_info.obs_ctext(position))

@email_parser(diags='DEPREC_CTEXT')
def obs_ctext(email_info, parser, position):
    """
        obs-ctext       =   obs-NO-WS-CTL
    [1038]              DEPREC_CTEXT  A comment contains a deprecated character (ISEMAIL_DEPREC)
    """
    return email_info.simple_char(position, email_info.OBS_CTEXT)

@email_parser(diags='CFWS_FWS')
def fws(email_info, parser, position=None):
    """
    FWS             =   <fws_sub> /  obs-FWS
                                          ; Folding white space
        // Folding White Space
        // Inside a quoted string, spaces are allowed as regular characters.
        // It's only FWS if we include HTAB or CRLF


        // http://tools.ietf.org/html/rfc5322#section-3.2.2
        //   Runs of FWS, comment, or CFWS that occur between lexical tokens in a
        //   structured header field are semantically interpreted as a single
        //   space character.

        // http://tools.ietf.org/html/rfc5322#section-3.2.4
        //   the CRLF in any FWS/CFWS that appears within the quoted-string [is]
        //   semantically "invisible" and therefore not part of the quoted-string

            // http://tools.ietf.org/html/rfc5322#section-3.2.2
            //   FWS             =   ([*WSP CRLF] 1*WSP) /  obs-FWS
            //                                          ; Folding white space

            // But note the erratum:
            // http://www.rfc-editor.org/errata_search.php?rfc=5322&eid=1908:
            //   In the obsolete syntax, any amount of folding white space MAY be
            //   inserted where the obs-FWS rule is allowed.  This creates the
            //   possibility of having two consecutive "folds" in a line, and
            //   therefore the possibility that a line which makes up a folded header
            //   field could be composed entirely of white space.
            //
            //   obs-FWS         =   1*([CRLF] WSP)


                // http://tools.ietf.org/html/rfc5322#section-3.2.2
                //   Runs of FWS, comment, or CFWS that occur between lexical tokens in a
                //   structured header field are semantically interpreted as a single
                //   space character.
                //
                // is_email() author's note: This *cannot* mean that we must add a
                // space to the address wherever CFWS appears. This would result in
                // any addr-spec that had CFWS outside a quoted string being invalid
                // for RFC 5321.

    FWS             =   ([*WSP CRLF] 1*WSP) /  obs-FWS

    [1018]                  CFWS_FWS  Address contains FWS (ISEMAIL_CFWS)
    [1149]          ERR_FWS_CRLF_END  Folding White Space ends with a CRLF sequence (ISEMAIL_ERR)

    """

    tmp_ret = email_info.fws_sub(position)
    if not tmp_ret:
        tmp_ret = email_info.obs_fws(position)

    return tmp_ret

@email_parser()
def fws_sub(email_info, parser, position=None):
    """
    FWS             =   ([*WSP CRLF] 1*WSP)
    [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign (ISEMAIL_DEPREC)
    """
    tmp_ret = email_info.fb(position)

    tmp_ret += email_info.wsp(position)

    if not tmp_ret:
        return email_info.fb(position)

    else:
        tmp_ret_crlf = email_info.crlf(position + tmp_ret)

        if tmp_ret_crlf.error:
            return tmp_ret.add(tmp_ret_crlf).set(0)

        if not tmp_ret_crlf:
            return tmp_ret

        tmp_ret_2 = email_info.one_wsp(position + tmp_ret.l + tmp_ret_crlf.l)

        if tmp_ret_2:
            return tmp_ret(tmp_ret_crlf, tmp_ret_2)

        else:
            return email_info.fb(position)

@email_parser(diags='DEPREC_FWS')
def obs_fws(email_info, parser, position):
    """
        obs-FWS         =   1*([CRLF] WSP)     ; As amended in erratum #1908

    [1034]                DEPREC_FWS  Address contains an obsolete form of Folding White Space (ISEMAIL_DEPREC)
    [1148]           ERR_FWS_CRLF_X2  Folding White Space contains consecutive CRLF sequences (ISEMAIL_ERR)
    [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign (ISEMAIL_DEPREC)

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.crlf(position)

    if tmp_ret.error:
        return tmp_ret

    if tmp_ret:
        if email_info.at_end(position + tmp_ret.l):
            return tmp_ret("ERR_FWS_CRLF_END")

    tmp_ret_2 = email_info.wsp(position + tmp_ret)
    if tmp_ret_2:

        # if not email_info.at_end(position + tmp_ret.l) and email_info.this_char(position + tmp_ret.l) in email_info.WSP:
        # tmp_ret += 1
        return tmp_ret(tmp_ret_2)
    else:

        return email_info.fb(position)

@email_parser(diags='RFC5321_QUOTED_STRING')
def quoted_string(email_info, parser, position):
    """
            quoted-string   =   [CFWS]
                       DQUOTE *([FWS] qcontent) [FWS] DQUOTE
                       [CFWS]

        // for Domain Names
        // http://tools.ietf.org/html/rfc5322#section-3.4.1
        //   If the
        //   string can be represented as a dot-atom (that is, it contains no
        //   characters other than atext characters or "." surrounded by atext
        //   characters), then the dot-atom form SHOULD be used and the quoted-
        //   string form SHOULD NOT be used.

        [1011]     RFC5321_QUOTED_STRING  Address is valid but contains a quoted string (ISEMAIL_RFC5321)

    [1138]       ERR_EXPECTING_QTEXT  A quoted string contains a character that is not allowed (ISEMAIL_ERR)
    [1145]   ERR_UNCLOSED_QUOTED_STR  Unclosed quoted string (ISEMAIL_ERR)

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.cfws(position)
    email_info.near_at_flag = False

    tmp_ret.flags -= 'CFWS_LAST'

    tmp_init_dquote = email_info.double_quote(position + tmp_ret)

    if tmp_init_dquote:
        tmp_ret += tmp_init_dquote
    else:
        return email_info.fb(position)

    tmp_closing_dquote = email_info.find(position + tmp_ret, email_info.DQUOTE, skip_quoted_str=True)
    if tmp_closing_dquote == -1:
        return tmp_ret('ERR_UNCLOSED_QUOTED_STR')

    last_was_fws = False
    has_qtext = False
    while True:

        tmp_loop_1 = email_info.fws(position + tmp_ret)

        if tmp_loop_1:
            tmp_loop_1.remove('CFWS_FWS')
            if last_was_fws:
                tmp_ret += tmp_loop_1
                return tmp_ret(("ERR_MULT_FWS_IN_QS", position + tmp_ret, tmp_ret))
            else:
                last_was_fws = False

        tmp_loop_2 = email_info.qcontent(position + tmp_ret + tmp_loop_1)

        if tmp_loop_2:
            tmp_ret += tmp_loop_1
            tmp_ret += tmp_loop_2
            has_qtext = True
        else:
            break

    tmp_last_quote = email_info.double_quote(position + tmp_ret)

    if tmp_last_quote:
        tmp_ret += tmp_last_quote
        tmp_cfws = email_info.cfws(position + tmp_ret.l)
        tmp_ret += tmp_cfws
        return tmp_ret
    else:
        return tmp_ret('ERR_EXPECTING_QTEXT')

@email_parser()
def qcontent(email_info, parser, position):
    """
        qcontent  =   qtext / quoted-pair
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.qtext(position) or email_info.quoted_pair(position)
    return tmp_ret

@email_parser()
def qtext(email_info, parser, position):
    """
        qtext           =   %d33 /             ; Printable US-ASCII
                           %d35-91 /          ;  characters not including
                           %d93-126 /         ;  "\" or the quote character
                           obs-qtext
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.simple_char(position, email_info.QTEXT) or email_info.obs_qtext(position)
    return tmp_ret

@email_parser(diags='DEPREC_QTEXT')
def obs_qtext(email_info, parser, position):
    """
        obs-qtext       =   obs-NO-WS-CTL

    [1035]              DEPREC_QTEXT  A quoted string contains a deprecated character (ISEMAIL_DEPREC)

    """
    return email_info.simple_char(position, email_info.OBS_QTEXT)

@email_parser()
def quoted_pair(email_info, parser, position):
    """
    quoted-pair     =   ("\" <quoted-pair-sub> / obs-qp

                // At this point we know where this qpair occurred so
                // we could check to see if the character actually
                // needed to be quoted at all.
                // http://tools.ietf.org/html/rfc5321#section-4.1.2
                //   the sending system SHOULD transmit the
                //   form that uses the minimum quoting possible.
            // To do: check whether the character needs to be quoted (escaped) in this context
            // The maximum sizes specified by RFC 5321 are octet counts, so we must include the backslash

    [1136]       ERR_EXPECTING_QPAIR  The address contains a character that is not allowed in a quoted pair (ISEMAIL_ERR)

    """

    tmp_ret = email_info.fb(position)

    tmp_ret += email_info.back_slash(position)

    if tmp_ret and email_info.at_end(position + 1):
        tmp_ret('ERR_EXPECTING_QPAIR')

    if tmp_ret:

        tmp_ret_1 = email_info.vchar_wsp(position + 1)

        if tmp_ret_1:
            return tmp_ret(tmp_ret_1)
        tmp_ret_1 = email_info.obs_qp(position + 1)

        if tmp_ret_1:
            return tmp_ret(tmp_ret_1)

        else:
            tmp_ret('ERR_EXPECTING_QPAIR')

    else:
        return email_info.fb(position)

@email_parser()
def vchar_wsp(email_info, parser, position):
    """
    quoted-pair_sub =  VCHAR / WSP

                // At this point we know where this qpair occurred so
                // we could check to see if the character actually
                // needed to be quoted at all.
                // http://tools.ietf.org/html/rfc5321#section-4.1.2
                //   the sending system SHOULD transmit the
                //   form that uses the minimum quoting possible.
            // To do: check whether the character needs to be quoted (escaped) in this context
            // The maximum sizes specified by RFC 5321 are octet counts, so we must include the backslash
    """
    return email_info.simple_char(position, email_info.VCHAR_WSP, max_count=1)

@email_parser(diags='DEPREC_QP')
def obs_qp(email_info, parser, position):
    """
        obs-qp = (%d0 / obs-NO-WS-CTL / LF / CR)

    [1036]                 DEPREC_QP  A quoted pair contains a deprecated character (ISEMAIL_DEPREC)

    """
    return email_info.simple_char(position, email_info.OBS_QP, max_count=1)

@email_parser()
def crlf(email_info, parser, position, in_crlf=False):
    """
    [1150] ERR_CR_NO_LF  Address contains a carriage return that is not followed by a line feed (ISEMAIL_ERR)
    [1148] ERR_FWS_CRLF_X2  Folding White Space contains consecutive CRLF sequences (ISEMAIL_ERR)
    """
    tmp_ret = email_info.fb(position)
    if email_info.at_end(position):
        return tmp_ret

    if email_info.this_char(position) == '\r':
        if not email_info.at_end(position + 1) and email_info.this_char(position + 1) == '\n':
            tmp_ret += 2

            if not in_crlf:
                tmp_crlf_2 = email_info.crlf(position + tmp_ret.l, in_crlf=True)
                if tmp_crlf_2.error:
                    tmp_ret += tmp_crlf_2
                    tmp_ret('ERR_FWS_CRLF_X2', set_length=4)
                    return tmp_ret
                elif tmp_crlf_2:
                    tmp_ret += 2
                    tmp_ret('ERR_FWS_CRLF_X2', set_length=4)
                    return tmp_ret
        else:
            return tmp_ret('ERR_CR_NO_LF', set_length=2)
    return tmp_ret

@email_parser(segment=False, diags='DEPREC_CFWS_NEAR_AT')
def no_at(email_info, parser, position):
    return email_info.simple_char(position, email_info.AT, max_count=1)

'''


@email_parser()
def at(email_info, position):
    return single_char(email_info, position, AT)


@email_parser()
def atext(email_info, position):
    return simple_char(email_info, position, ATEXT)


@email_parser()
def single_dot(email_info, position):
    tmp_ret = single_char(email_info, position, DOT)
    if tmp_ret and not email_info.at_end(position + 1) and email_info[position + 1] == DOT:
        tmp_ret('ERR_CONSECUTIVE_DOTS')
    return tmp_ret


@email_parser()
def alpha(email_info, position):
    return simple_char(email_info, position, ALPHA)


@email_parser()
def let_dig(email_info, position):
    return simple_char(email_info, position, LET_DIG)


@email_parser(segment=False)
def sub_ldh_str(email_info, position):
    return simple_char(email_info, position, LDH_STR)


@email_parser()
def open_sq_bracket(email_info, position):
    return single_char(email_info, position, OPENSQBRACKET)


@email_parser()
def close_sq_bracket(email_info, position):
    return single_char(email_info, position, CLOSESQBRACKET)


@email_parser(segment=False)
def obs_dtext_sub(email_info, position):
    return simple_char(email_info, position, OBS_DTEXT)


@email_parser()
def colon(email_info, position):
    return single_char(email_info, position, COLON)


@email_parser()
def double_colon(email_info, position):
    return simple_str(email_info, position, DOUBLECOLON)


@email_parser()
def dcontent(email_info, position):
    return simple_char(email_info, position, DCONTENT)


@email_parser(segment=False)
def pre_cfws(email_info, position):
    return simple_char(email_info, position, PRE_CFWS)


@email_parser()
def ipv6(email_info, position):
    return simple_str(email_info, position, "IPv6:", caps_sensitive=False)


@email_parser()
def three_digit(email_info, position):
    return simple_char(email_info, position, DIGIT, max_count=3)


@email_parser(segment=False)
def hexdigit(email_info, position):
    return simple_char(email_info, position, HEXDIG, min_count=-1, max_count=4)


@email_parser()
def open_parenthesis(email_info, position):
    return single_char(email_info, position, OPENPARENTHESIS)


@email_parser()
def close_parenthesis(email_info, position):
    return single_char(email_info, position, CLOSEPARENTHESIS)


@email_parser(segment=False)
def sub_ctext(email_info, position):
    return simple_char(email_info, position, CTEXT)


@email_parser()
def wsp(email_info, position):
    return simple_char(email_info, position, WSP)


@email_parser()
def one_wsp(email_info, position):
    return single_char(email_info, position, WSP)


@email_parser()
def double_quote(email_info, position):
    return single_char(email_info, position, DQUOTE)


@email_parser()
def back_slash(email_info, position):
    return single_char(email_info, position, BACKSLASH)


@email_parser()
def hyphen(email_info, position):
    return single_char(email_info, position, HYPHEN)


@email_parser()
def dot(email_info, position):
    return single_char(email_info, position, DOT)


# </editor-fold>
# **********************************************************************************

