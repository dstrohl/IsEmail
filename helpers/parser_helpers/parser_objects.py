__all__ = ['AT', 'BACKSLASH', 'CLOSESQBRACKET', 'CLOSEPARENTHESIS', 'COLON', 'COMMA', 'CR', 'CRLF', 'DIGIT', 'DOT',
           'DOUBLECOLON', 'DQUOTE', 'HEXDIG', 'HTAB', 'HYPHEN', 'ALPHA', 'LET_DIG', 'LF', 'OPENPARENTHESIS',
           'OPENSQBRACKET', 'SP', 'OPERATION', 'PHBase', 'PHEnclosed', 'PHMaxLen', 'PHMinLen', 'PHInvalidNext',
           'PHBaseSingleChar', 'PHBaseChar', 'PHBaseString', 'PHInvalidStartStop', 'make_char_str',
           'at', 'backslash', 'closesqbracket', 'closeparenthesis', 'colon', 'comma', 'cr', 'crlf', 'digit', 'dot',
           'double_colon', 'dquote', 'hexdig', 'htab', 'hyphen', 'alpha', 'let_dig', 'lf', 'openparenthesis',
           'opensqbracket', 'sp', 'ParsingObj'
           ]

# from functools import wraps
from helpers.exceptions import ParsingError
# from helpers.footballs import ParseResultFootball
from helpers.footballs import ParsingObj
from helpers .general.general import make_char_str
from enum import Enum

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


class OPERATION(Enum):
    SINGLE_CHAR = 'single_char'
    SINGLE_STRING = 'single_string'
    CHAR = 'char'


class PHBase(object):
    parser = True
    is_history_item = True
    is_segment_item = True

    name = None
    description = None
    references = None

    on_pass_msg = name, 'VALID'
    on_fail_msg = name, 'ERROR'

    parse_object = ParsingObj

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _parse(self, parse_obj, position, **kwargs):
        tmp_ret = parse_obj.fb(position)
        return tmp_ret

    def super_call(self, *args, **kwargs):
        try:
            tmp_ret = super().__call__(*args, **kwargs)
        except AttributeError:
            tmp_ret = self._parse(*args, **kwargs)
        return tmp_ret

    def __call__(self, parse_obj, position=0, **kwargs):
        """
        must call:
            self.super_call(parse_obj, position, **kwargs)

        """
        tmp_err = None
        position = int(position)
        name = self.name or self.__class__.__name__

        if self.is_segment_item:
            parse_obj.begin_stage(name, position=position)

        raise_error = False

        if not parse_obj.at_end(position):
            try:
                tmp_ret = self.super_call(parse_obj, position, **kwargs)
            except ParsingError as err:
                tmp_err = err
                raise_error = True
                tmp_ret = err.results
        else:
            tmp_ret = parse_obj.fb(position)

        if tmp_ret:
            if self.is_history_item:
                tmp_ret.set_history(name)
            if self.on_pass_msg:
                if isinstance(self.on_pass_msg, str):
                    pass_d = [self.on_pass_msg]
                else:
                    pass_d = self.on_pass_msg
                tmp_ret(*pass_d)

        elif self.on_fail_msg:
            if isinstance(self.on_fail_msg, str):
                fail_d = [self.on_fail_msg]
            else:
                fail_d = self.on_fail_msg
            tmp_ret(*fail_d)

        if self.is_segment_item:
            parse_obj.end_stage(tmp_ret, raise_error=raise_error)

        if raise_error:
            raise tmp_err


class PHBaseSingleChar(PHBase):
    look_for = None
    caps_sensitive = True

    def __init__(self, look_for=None, **kwargs):
        self.look_for = look_for
        super().__init__(**kwargs)

    def _parse(self, parse_obj, position, **kwargs):
        tmp_ret = parse_obj.fb(position)
        if self.look_for is None:
            return tmp_ret

        if self.caps_sensitive:
            tmp_check = parse_obj[position].lower()
            parse_for = self.look_for.lower()
            if tmp_check in parse_for:
                return tmp_ret(1)
        else:
            if parse_obj[position] == self.look_for:
                return tmp_ret(1)
        return tmp_ret


class PHBaseString(PHBase):
    look_for = None
    caps_sensitive = True

    def __init__(self, look_for=None, **kwargs):
        self.look_for = look_for
        super().__init__(**kwargs)

    def _parse(self, parse_obj, position, **kwargs):
        tmp_ret = parse_obj.fb(position)
        if self.look_for is None:
            return tmp_ret

        tmp_len = len(self.look_for)
        tmp_check = parse_obj.mid(position, tmp_len)

        if self.caps_sensitive:
            tmp_check = tmp_check.lower()
            parse_for = self.look_for.lower()
        else:
            parse_for = self.look_for

        if tmp_check == parse_for:
            tmp_ret += tmp_len

        return tmp_ret


class PHBaseChar(PHBase):
    look_for = None
    char_until_char = None
    min_char_count = -1
    max_char_count = 9999
    min_char_count_msg = 'SEGMENT_TOO_SHORT'
    caps_sensitive = True

    def __init__(self, look_for=None, **kwargs):
        self.look_for = look_for
        super().__init__(**kwargs)

    def _parse(self, parse_obj, position, **kwargs):
        tmp_ret = parse_obj.fb(position)
        tmp_count = 0
        if self.look_for is None:
            return tmp_ret

        if self.char_until_char is None:
            looper = parse_obj.remaining_complex(begin=position, count=self.max_char_count)
        else:
            looper = parse_obj.remaining_complex(begin=position, count=self.max_char_count,
                                                 until_char=self.char_until_char)

        if self.caps_sensitive:
            parse_for = self.look_for.lower()
            looper = looper.lower()

        else:
            parse_for = self.look_for

        for i in looper:
            if i in parse_for:
                tmp_count += 1
            else:
                if tmp_count >= self.min_char_count:
                    return tmp_ret(tmp_count)
                else:
                    return tmp_ret(self.min_char_count_msg)

        if tmp_count >= self.min_char_count:
            return tmp_ret(tmp_count)
        return tmp_ret


"""

class PHLoop(object):
    parser = True
    min_loop = -1
    min_loop_fail_msg = 'TOO_FEW_SEGMENTS'
    max_loop = -1
    max_loop_fail_msg = 'TOO_MANY_SEGMENTS'
"""

class PHInvalidNext(object):
    invalid_next_char = None
    invalid_next_char_msg = 'INVALID_NEXT_CHAR'

    def __call__(self, parse_obj, position, **kwargs):
        tmp_ret = self.super_call(parse_obj, position, **kwargs)
        if tmp_ret and not parse_obj.at_end(position + 1) and parse_obj[position + 1] in self.invalid_next_char:
            tmp_ret(self.invalid_next_char_msg)
        return tmp_ret


class PHEnclosed(object):
    parser = True
    enclosure_start = '"'
    enclosure_stop = '"'
    skip_quoted = True
    unclosed_msg = 'UNCLOSED_STRING'


class PHMinLen(object):
    parser = True
    min_length = None
    min_length_msg = 'SEGMENT_TOO_LONG'


class PHMaxLen(object):
    parser = True
    max_length = None
    max_length_msg = 'SEGMENT_TOO_SHORT'


class PHInvalidStartStop(object):
    invalid_start_chars = None
    invlaid_start_chars_msg = 'INVALID_START'
    invalid_end_chars = None
    invlaid_end_chars_msg = 'INVALID_END'

class SingleDot(PHBaseSingleChar, PHInvalidNext):
    look_for = DOT
    invalid_next_char = DOT
    invalid_next_char_msg = {'name': 'INVALID_NEXT_CHAR', 'description': ''}

single_dot = SingleDot()
alpha = PHBaseChar(ALPHA)
at = PHBaseSingleChar(AT)
backslash = PHBaseSingleChar(BACKSLASH)
closeparenthesis = PHBaseSingleChar(CLOSEPARENTHESIS)
closesqbracket = PHBaseSingleChar(CLOSESQBRACKET)
colon = PHBaseSingleChar(COLON)
comma = PHBaseSingleChar(COMMA)
cr = PHBaseSingleChar(CR)
crlf = PHBaseString(CRLF)
digit = PHBaseSingleChar(DIGIT)
dot = PHBaseSingleChar(DOT)
dquote = PHBaseSingleChar(DQUOTE)
hexdig = PHBaseSingleChar(HEXDIG)
htab = PHBaseSingleChar(HTAB)
hyphen = PHBaseSingleChar(HYPHEN)
lf = PHBaseSingleChar(LF)
openparenthesis = PHBaseSingleChar(OPENPARENTHESIS)
opensqbracket = PHBaseSingleChar(OPENSQBRACKET)
sp = PHBaseSingleChar(SP)
let_dig = PHBaseChar(LET_DIG)
double_colon = PHBaseString(DOUBLECOLON)


# **********************************************************************************
# <editor-fold desc="  WRAPPERS  ">
# **********************************************************************************
"""

def email_parser(is_history_item=True, name=None, pass_diags=None, fail_diags=None, is_comment=False,
                 extra_text_error=None, full_domain_part=False, full_local_part=False):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(email_info, position, *args, is_history=is_history_item, pass_d=pass_diags,
                         fail_d=fail_diags, is_comment_flag=is_comment, func_name=name, full_domain=full_domain_part,
                         full_local=full_local_part, extra_text_err=extra_text_error, **kwargs):
            tmp_err = None
            position = int(position)
            func_name = func_name or func.__name__
            # stage_name = kwargs.get('name', name or func.__name__)
            # is_history_item = kwargs.get('is_history_item', is_history_item)

            email_info.begin_stage(func_name, position=position)

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

            if tmp_ret:
                if is_history:
                    tmp_ret.set_history(func_name)
                if pass_d:
                    if isinstance(pass_d, str):
                        pass_d = [pass_d]
                    tmp_ret(*pass_d)
                if is_comment_flag:
                    email_info.add_comment(tmp_ret)

                if full_domain:

                    tmp_char = email_info[position]
                    if tmp_char == HYPHEN:
                        return tmp_ret('ERR_DOMAIN_HYPHEN_START')
                    elif tmp_char == DOT:
                        return tmp_ret('ERR_DOT_START')

                    if not email_info.at_end(position + tmp_ret):
                        tmp_ret(extra_text_err)
                    else:
                        if tmp_ret > 255:
                            tmp_ret('RFC5322_DOMAIN_TOO_LONG')

                        last_char = email_info[-1]

                        if last_char == HYPHEN:
                            tmp_ret('ERR_DOMAIN_HYPHEN_END')
                        elif last_char == BACKSLASH:
                            tmp_ret('ERR_BACKSLASH_END')
                        elif last_char == DOT:
                            tmp_ret('ERR_DOT_END')

                if full_local:

                    if email_info[position] == DOT:
                        return tmp_ret('ERR_DOT_START')

                    if email_info.flags.at_in_cfws:
                        tmp_ret('DEPREC_CFWS_NEAR_AT')

                    if email_info[position + tmp_ret] != AT:
                        tmp_ret(extra_text_err)

                        if not email_info.find(position + tmp_ret, AT, skip_quoted=True):
                            tmp_ret('ERR_NO_DOMAIN_SEP')

                    else:
                        if tmp_ret > 64:
                            tmp_ret('RFC5322_LOCAL_TOO_LONG')

                        last_char = email_info[-1]

                        if last_char == BACKSLASH:
                            tmp_ret('ERR_BACKSLASH_END')
                        elif last_char == DOT:
                            tmp_ret('ERR_DOT_END')

            elif fail_d:
                if isinstance(fail_d, str):
                    fail_d = [fail_d]
                tmp_ret(*fail_d)

            email_info.flags.near_at_flag = tmp_near_at_flag
            email_info.end_stage(tmp_ret, raise_error=raise_error)

            if raise_error:
                raise tmp_err

            return tmp_ret

        return func_wrapper

    return func_decorator


def wrapped_parser(str_wrapper=None, no_end_error=''):  # , bad_text_error=''):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(email_info, position, *args, stw=str_wrapper, init_start=None, **kwargs):

            wrapped_stage = []

            if stw is None:
                start_wrapper = None
                end_wrapper = None
            else:
                start_wrapper = stw[0]
                if len(stw) == 2:
                    end_wrapper = stw[1]
                else:
                    end_wrapper = start_wrapper

                wrapped_stage.append(stw)

            wrapped_stage_name = 'wrapping in >%s<' % '/'.join(wrapped_stage)
            email_info.begin_stage(wrapped_stage_name, position)

            tmp_ret = email_info.fb(position)

            if start_wrapper is not None:
                if init_start is None:
                    init_start = single_char(email_info, position + tmp_ret, start_wrapper)
                if init_start:
                    tmp_ret += init_start
                else:
                    return tmp_ret

            tmp_ret_2 = func(email_info, position + tmp_ret, *args, **kwargs)
            tmp_ret += tmp_ret_2

            if not tmp_ret_2:
                return tmp_ret(0)

            if end_wrapper is not None:
                tmp_ret_2 = single_char(email_info, position + tmp_ret, end_wrapper)
                if tmp_ret_2:
                    tmp_ret += tmp_ret_2
                else:
                    tmp_ret(no_end_error)

            return tmp_ret

        return func_wrapper

    return func_decorator


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  HELPERS  ">
# **********************************************************************************


def simple_char(email_info, position, parse_for, min_count=-1, max_count=99999, parse_until=None):
    tmp_ret = email_info.fb(position)
    tmp_count = 0

    if parse_until is None:
        looper = email_info.remaining_complex(begin=position, count=max_count)
    else:
        looper = email_info.remaining_complex(begin=position, count=max_count, until_char=parse_until)

    for i in looper:
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


def _make_ret(email_info, position, parser, *args, **kwargs):
    if isinstance(parser, ParseResultFootball):
        return parser
    elif isinstance(parser, str):
        if len(parser) > 1 and parser[0] == '"' and parser[-1] == '"':
            return simple_str(email_info, position, parser[1:-1])
        else:
            return simple_char(email_info, position, parser)
    else:
        return parser(email_info, position, *args, **kwargs)


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


def parse_best(email_info, position, *parsers, try_all=False):
    email_info.begin_stage('BEST', position)
    tmp_ret = email_info.fb(position)

    for p in parsers:
        if not try_all and p and email_info.at_end(position + p):
            tmp_ret = p
            break

        tmp_ret = tmp_ret.max(p)
    email_info.end_stage(results=tmp_ret)
    return tmp_ret
"""
# **********************************************************************************
# </editor-fold>
# **********************************************************************************

