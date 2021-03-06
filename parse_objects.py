
from parse_results import ParseResultFootball,ParsingError
# from collections import deque
from functools import wraps
from meta_data import ISEMAIL_ALLOWED_GENERAL_ADDRESS_LITERAL_STANDARD_TAGS, ISEMAIL_DOMAIN_TYPE, ISEMAIL_DNS_LOOKUP_LEVELS, META_LOOKUP

def make_char_str(*chars_in):
    tmp_ret = []
    for char in chars_in:
        if isinstance(char, str):
            tmp_ret.append(char)
        elif isinstance(char, int):
            tmp_ret.append(chr(char))
        elif isinstance(char, tuple):
            for c in range(char[0], char[1]+1):
                tmp_ret.append(chr(c))
    return ''.join(tmp_ret)


def as_football(segment=True, comment=False, skip=False, diags=None):
    def football_decorator(func):
        @wraps(func)
        def func_wrapper(self, position, *args, non_segment=False, **kwargs):
            is_segment = segment and not non_segment
            raise_error = False
            error_raised = None
            tmp_near_at_flag = self.near_at_flag

            stage_name = kwargs.get('stage_name', func.__name__)        
            self.stage.append(stage_name)
    
            self.add_begin_trace(position)
    
            position = int(position)

            if not self.at_end(position):

                try:
                    # self.add_note_trace('** checking near_at_flag: %s' % self.near_at_flag)

                    tmp_ret = func(self, position, *args, **kwargs)
                    # self.add_note_trace('** checking at_in_cfws: %s' % self.at_in_cfws)

                except ParsingError as err:
                    self.near_at_flag = tmp_near_at_flag
                    raise_error = True
                    error_raised = err
                    tmp_ret = err.results

                if not isinstance(tmp_ret, ParseResultFootball):
                    raise AttributeError('invalid return object = %r' % tmp_ret)

            else:
                tmp_ret = self._empty

            tmp_ret.segment_name = stage_name

            if tmp_ret and is_segment and not tmp_ret.error:
                tmp_ret.add(position=position)
                tmp_ret._history.name = stage_name
                tmp_ret._history.begin = position
                tmp_ret._history.length = tmp_ret.l
            else:
                tmp_ret._history.clear()
                tmp_ret.segment_name = ''

            if tmp_ret and diags is not None:
                if isinstance(diags, (list, tuple)):
                    tmp_ret.add(*diags)
                else:
                    tmp_ret.add(diags)

            if not tmp_ret or tmp_ret.error:
                self.near_at_flag = tmp_near_at_flag

            self.add_end_trace(position, tmp_ret, raise_error=raise_error)
    
            self.stage.pop()
    
            if raise_error:
                raise error_raised

            if tmp_ret and not tmp_ret.error:
                if comment:
                    tmp_ret.add_comment(position, tmp_ret.length)
            return tmp_ret
    
        return func_wrapper
    return football_decorator

"""

def full_domain_segment():
    def football_decorator(func):
        @wraps(func)
        def func_wrapper(self, position, *args, **kwargs):
            tmp_char = self.this_char(position)
            if tmp_char == self.HYPHEN:
                tmp_ret = self._empty
                return tmp_ret('ERR_DOMAIN_HYPHEN_START')
            elif tmp_char == self.DOT:
                tmp_ret = self._empty
                return tmp_ret('ERR_DOT_START')

            tmp_ret = func(self, position, *args, **kwargs)

            tmp_ret_codes = []

            def check_pos(pos):
                tmp_sub_codes = []
                self.add_note_trace('Checking Char: %s' % self.this_char(pos))
                sub_ret = self.dot(pos, non_segment=True)
                if sub_ret:
                    tmp_sub_codes.append('ERR_DOT_END')
                else:
                    sub_ret = self.back_slash(pos, non_segment=True)
                    if sub_ret:
                        tmp_sub_codes.append('ERR_BACKSLASH_END')
                    elif is_domain:
                        sub_ret = self.hyphen(pos, non_segment=True)
                        if sub_ret:
                            tmp_sub_codes.append('ERR_DOMAIN_HYPHEN_END')
                if not sub_ret:
                    sub_ret = None
                return tmp_sub_codes, sub_ret

            tmp_ret = None
            plus_pos = None

            self.add_note_trace('Start End verification')
            self._set_trace(1)
            if is_domain:
                self.add_note_trace('In Domain')

                if football > 255:
                    tmp_ret_codes.append('RFC5322_DOMAIN_TOO_LONG')

                end_pos = self.email_len
                if not self.at_end(position + football):
                    self.add_note_trace('Not at end')
                    if not self.at_end(position + football + 1):
                        plus_pos = end_pos + 1
                        self.add_note_trace('Has One Extra Char')
                        tmp_ret_codes.append(err_expecting_code)
                        return tmp_ret_codes, None
            else:
                self.add_note_trace('In Local')

                end_pos = position + football
                if self.this_char(position + football) != self.AT:
                    self.add_note_trace('Not at end')
                    if self.this_char(position + football + 1) != self.AT:
                        plus_pos = end_pos + 1
                        self.add_note_trace('Has One Extra Char')
                        tmp_ret_codes.append(err_expecting_code)
                        return tmp_ret_codes, None

            if plus_pos is not None:
                codes, tmp_ret = check_pos(plus_pos)
                if codes:
                    tmp_ret_codes.extend(codes)
                else:
                    tmp_ret_codes.append(err_expecting_code)
            else:
                codes, junk = check_pos(end_pos)
                tmp_ret_codes.extend(codes)

            self._set_trace(-1)

            if tmp_ret:
                self.add_note_trace('Finish end verification: returning obj + %r' % tmp_ret_codes)
            else:
                self.add_note_trace('Finish end verification: returning %r' % tmp_ret_codes)

            return tmp_ret_codes, tmp_ret

            return tmp_ret

        return func_wrapper

    return football_decorator


def full_local_segment(post_text_error):
    def football_decorator(func):
        @wraps(func)
        def func_wrapper(self, position, *args, non_segment=False, **kwargs):
            return tmp_ret

        return func_wrapper

    return football_decorator



def wrapped_segment(pre_seg_char=None, post_segment_char=None):
    def football_decorator(func):
        @wraps(func)
        def func_wrapper(self, position, *args, non_segment=False, **kwargs):

            tmp_ret = self.empty

            tmp_ret = func(self, position, *args, **kwargs)



            is_segment = segment and not non_segment
            raise_error = False
            error_raised = None
            tmp_near_at_flag = self.near_at_flag

            stage_name = kwargs.get('stage_name', func.__name__)
            self.stage.append(stage_name)

            self.add_begin_trace(position)

            position = int(position)

            if not self.at_end(position):

                try:
                    # self.add_note_trace('** checking near_at_flag: %s' % self.near_at_flag)

                    tmp_ret = func(self, position, *args, **kwargs)
                    # self.add_note_trace('** checking at_in_cfws: %s' % self.at_in_cfws)

                except ParsingError as err:
                    self.near_at_flag = tmp_near_at_flag
                    raise_error = True
                    error_raised = err
                    tmp_ret = err.results

                if not isinstance(tmp_ret, (ParseResultFootball)):
                    raise AttributeError('invalid return object = %r' % tmp_ret)

            else:
                tmp_ret = self._empty

            tmp_ret.add(segment=stage_name)
            if tmp_ret and is_segment and not tmp_ret.error:
                tmp_ret.add(position=position)
                tmp_ret._history.name = stage_name
                tmp_ret._history.begin = position
                tmp_ret._history.length = tmp_ret.l
            else:
                tmp_ret._history.clear()
                tmp_ret.segment_name = ''

            if not tmp_ret or tmp_ret.error:
                self.near_at_flag = tmp_near_at_flag

            self.add_end_trace(position, tmp_ret, raise_error=raise_error)

            self.stage.pop()

            if raise_error:
                raise error_raised

            return tmp_ret

        return func_wrapper

    return football_decorator
"""

"""
def as_int(func):
   def func_wrapper(self, position):
        self.stage.append(func.__name__)
        position = self.pos(position)
        tmp_ret = func(self, position)
        self.stage.pop()
        if isinstance(tmp_ret, ParseResultFootball):
            tmp_ret = tmp_ret.l
        return tmp_ret
   return func_wrapper


class P4(object):
    min_count = 1
    max_count = 9999
    optional = False
    ordered = False
    include_str = True

    def __init__(self, parse_for, **kwargs):
        self.parse_for = parse_for
        for arg, value in kwargs.items():
            setattr(self, arg, value)

class P4Ord(P4):
    min_count = 1
    max_count = 1
    ordered = True

class P4Char(P4):
    min_count = 1
    max_count = 1
    ordered = False
"""


class TraceObj(object):
    def __init__(self, parser, stage, full_stage, position=0, begin=True, results=None,
                 trace_level=0, note=False, note_text=None, raise_error=False):
        self.parser = parser
        self.stage_name = stage
        self.full_stage_name = full_stage
        self.begin = begin
        self.results = results
        self.trace_level = trace_level
        self.position = position
        self.note = note
        self.note_text = note_text
        self.raise_error = raise_error

    def __str__(self):
        tmp_indent = ''.rjust(self.trace_level * 4)

        if self.begin:
            tmp_str = '%sbegin (%s): %s  scanning: ->%r<-' % (tmp_indent, self.position, self.stage_name, self.parser.mid(self.position))

        elif self.note:
            if self.position == 0:
                tmp_str = '%sNote : %s' % (tmp_indent, self.note_text)
            else:
                tmp_str = '%sNote (%s): %s' % (tmp_indent, self.position, self.note_text)

        else:
            if self.raise_error:
                tmp_raised = ' -RAISED - '
            else:
                tmp_raised = ''

            if self.results.l == 0 or self.results.error:
                tmp_str = '%send      %s : %s  -- %r ' % (tmp_indent, tmp_raised, self.stage_name, self.results)
            else:
                tmp_str = '%send       (%r) %s : %s  -- %r ' % (tmp_indent,
                                                                self.parser.mid(self.position, self.results.length),
                                                                tmp_raised,
                                                                self.stage_name,
                                                                self.results)

        return tmp_str


class EmailParser(object):
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

    # test_text = ''

    def __init__(self,
                 email_in=None,
                 verbose=0,
                 trace_filter=-1,
                 raise_on_error=False,
                 dns_lookup_level=None,
                 dns_servers=None,
                 dns_timeout=None,
                 tld_list=None):
        """
        :param email_in:  the email to parse
        :param verbose:
            * 0 = only return true/false
            * 1 = return t/f + cleaned email + major reason
            * 2 = return all

        :param error_on_warning:
        :param error_on_category:
        :param error_on_diag:
        """
        self._dns_lookup_level = dns_lookup_level or ISEMAIL_DNS_LOOKUP_LEVELS.NO_LOOKUP
        self._dns_servers = dns_servers
        self._dns_timeout = dns_timeout
        self._tld_list = tld_list
        self.email_in = ''
        self.result = None
        self.position = -1
        self.email_len = 0
        # self.parsed = []
        # self.remaining = deque()
        self.email_list = []
        self.cleaned = []
        self.verbose = verbose
        # self.error_on_warning = error_on_warning
        # self.error_on_category = error_on_category
        # self.error_on_diag = error_on_diag
        self._raise_on_error = raise_on_error

        if email_in is not None:
            self.setup(email_in)

        self.stage = []
        self.trace = []
        self.trace_level = 0
        self.trace_filter = trace_filter
        self.in_local_part = False
        self.in_domain_part = False
        self.in_crlf = False

        self.at_in_cfws = False
        self.near_at_flag = False

    def __repr__(self):
        return 'Parse: "%s", at stage %s' % (self.email_in, self.stage)

    @property
    def _empty(self):
        return ParseResultFootball(self)

    def mid(self, begin: int = 0, length: int = 0):
        if length > 0:
            tmp_end = min(begin + length, self.email_len)
        else:
            tmp_end = self.email_len
        tmp_str = ''.join(self.email_list[begin:tmp_end])
        return tmp_str

    def setup(self, email_in):
        # self.result = ParseEmailResult(email_in)
        self.result = None
        self.email_len = len(email_in)
        self.email_in = email_in
        self.position = 0
        self.email_list.clear()
        self.email_list.extend(email_in)

        # self.parsed = []
        # self.remaining = deque()
        self.cleaned = []

        self.stage = []
        self.trace = []
        self.trace_level = 0

        self.in_crlf = False

    """
    def set_response(self, response_code, position, length):
        response_dict = ISEMAIL_DIAG_RESPONSES()
    """
    """
    @property
    def _fb(self):
        return self._empty
    """
    def remaining(self, position, until=None):
        position = self.pos(position)
        until = until or self.email_len
        for i in range(position, until):
            yield self.email_list[i]

    """
    def next_char(self, from_pos=None):
        from_pos = self.pos(from_pos)
        return self.email_list[from_pos+1]


    def last_char(self, from_pos=None):
        from_pos = self.pos(from_pos)
        return self.email_list[from_pos-1]
    """

    @property
    def cur_stage(self):
        return self.stage[-1]

    @property
    def stage_str(self):
        return '.'.join(self.stage)

    @property
    def trace_str(self):
        tmp_list = []
        for t in self.trace:
            tmp_list.append(str(t))

        tmp_ret = '\nTRACE (%s records, string: %s): \n%s\n-----------------' % (len(self.trace), repr(self.email_in), '\n'.join(tmp_list))
        return tmp_ret

    def _set_trace(self, trace_level_change=0):
        if self.verbose == 2:
            self.trace_level += trace_level_change
            if self.trace_filter == -1 or self.trace_filter >= self.trace_level:
                return True
        return False

    def add_begin_trace(self, position):
        if self._set_trace(1):
            self._add_trace(position, is_begin=True)

    def add_end_trace(self, position, results, raise_error=False):
        if self._set_trace():
            self._add_trace(position, results=results, raise_error=raise_error)
        self._set_trace(-1)

    def add_note_trace(self, note, position=0):
        if self._set_trace(1):
            self._add_trace(position, is_note=True, note_str=note)
        self._set_trace(-1)

    def _add_trace(self, position, is_note=False, note_str=None, results=None, is_begin=False, raise_error=False):
        if results is not None:
            results = results.copy()
        self.trace.append(TraceObj(
            parser=self,
            stage=self.cur_stage,
            full_stage=self.stage_str,
            position=position,
            begin=is_begin,
            trace_level=self.trace_level,
            results=results,
            note=is_note,
            note_text=note_str,
            raise_error=raise_error))

    def parse(self,
              email_in=None,
              method=None,
              position=0,
              dns_lookup_level=None,
              raise_on_error=False,
              **kwargs):

        return_football = kwargs.pop('return_football', False)

        dns_lookup_level = dns_lookup_level or self._dns_lookup_level
        raise_on_error = raise_on_error or self._raise_on_error

        if email_in == '' or email_in is None:
            tmp_ret = self._empty
            tmp_ret('ERR_EMPTY_ADDRESS', raise_on_error=False)
            if return_football:
                if raise_on_error and tmp_ret.error:
                    raise ParsingError(tmp_ret)
                else:
                    return tmp_ret

            return tmp_ret.finish(dns_lookup_level=dns_lookup_level, raise_on_error=raise_on_error)

        if method is None:
            method = self.address_spec
        elif isinstance(method, str):
            method = getattr(self, method)

        if email_in is not None:
            self.setup(email_in=email_in)

        try:
            tmp_ret = method(position, **kwargs)
        except ParsingError as err:
            tmp_ret = err.results

        if return_football:
            if raise_on_error and tmp_ret.error:
                raise ParsingError(tmp_ret)
            else:
                return tmp_ret

        return tmp_ret.finish(dns_lookup_level=dns_lookup_level, raise_on_error=raise_on_error)
    __call__ = parse

    def this_char(self, position):
        position = self.pos(position)
        try:
            return self.email_list[position]
        except IndexError:
            return ''

    def pos(self, position=None):
        if isinstance(position, int):
            return position
        else:
            return position.length

    def at_end(self, position):
        position = self.pos(position)
        if position >= self.email_len:
            return True
        return False

    def find(self, position, search_for, stop_at='', skip_quoted_str=False, skip_chars=''):
        position = self.pos(position)
        tmp_ret = 0
        in_qs = False
        for c in self.remaining(position):
            tmp_ret += 1
            if skip_quoted_str and c == self.BACKSLASH and not in_qs:
                in_qs = True
            elif c not in skip_chars:
                if not in_qs:
                    if c in search_for:
                        return tmp_ret
                    if c in stop_at:
                        return -1
                else:
                    in_qs = False
        return -1

    def count(self, position, search_for, stop_for=None, length=None):
        tmp_ret = 0
        tmp_pos = position
        for c in self.remaining(position, length):
            tmp_pos += 1
            if c in search_for:
                tmp_ret += 1
            if stop_for is not None and c in stop_for:
                return tmp_ret
        return tmp_ret

    def simple_char(self,
                    position: int,
                    parse_for: str,
                    min_count: int = -1,
                    max_count: int = 99999,
                    parse_until: str = None) -> ParseResultFootball:
        
        tmp_ret = ParseResultFootball(self)
        for i in self.remaining(position):
            if parse_until is not None and i in parse_until:
                return tmp_ret
            if i in parse_for:
                tmp_ret += 1
                if tmp_ret == max_count:
                    break
            else:
                if tmp_ret >= min_count:
                    break
                else:
                    return self._empty

        if parse_until is not None:
            return self._empty

        if tmp_ret >= min_count:
            return tmp_ret
        return tmp_ret(set_length=0)

    def simple_str(self, position, parse_for, caps_sensitive=True):
        tmp_ret = ParseResultFootball(self)
        tmp_len = len(parse_for)

        tmp_check = self.mid(position, tmp_len)

        if not caps_sensitive:
            tmp_check = tmp_check.lower()
            parse_for = parse_for.lower()

        if tmp_check == parse_for:
            tmp_ret += tmp_len

        return tmp_ret

    def single_char(self, position, parse_for):
        return self.simple_char(position, parse_for=parse_for, min_count=1, max_count=1)

    def _try_action(self, position, action_dict):
        if isinstance(action_dict, dict):
            action_dict = action_dict.copy()
            if 'string_in' in action_dict:
                parse_for = action_dict.pop('string_in')
                return self.simple_char(position, parse_for=parse_for, **action_dict)

            elif 'function' in action_dict:
                tmp_func = action_dict.pop('function')
                return tmp_func(position, **action_dict)
            else:
                raise AttributeError('Invalid dictionary passed: %r' % action_dict)
        elif isinstance(action_dict, str):
            return self.simple_char(position, parse_for=action_dict)

        else:
            return action_dict(position)

    def try_or(self, position, *args):
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
        position = self.pos(position)
        for act in args:
            if isinstance(act, dict):
                tmp_name = act.pop('name')
            elif isinstance(act, str):
                tmp_name = act
            else:
                tmp_name = act.__name__

            tmp_ret = self._try_action(position, act)
            if tmp_ret or tmp_ret.error:
                return tmp_name, tmp_ret

        return '', ParseResultFootball(self)

    def try_counted_and(self, position, *args, min_loop=1, max_loop=1):

        final_loop_count = 0
        position = self.pos(position)
        tmp_ret = ParseResultFootball(self)
        exit_break = False
        empty_return = False

        # self.add_note_trace('looping begin outside AND at: ', position + tmp_ret.l)
        # self.trace_level += 1
        for loop_count in range(max_loop):
            tmp_loop_ret = ParseResultFootball(self)
            self.add_begin_trace(position + tmp_ret.l)
            # self.add_note_trace('looping begin inside  AND at: ', position + tmp_ret.l + tmp_loop_ret.l)
            # self.trace_level += 1
            for act in args:
                # if isinstance(act, dict):
                #     tmp_name = act.pop('name', '')
                # elif isinstance(act, str):
                #     tmp_name = act
                # else:
                #     tmp_name = act.__name__

                tmp_ret_1 = self._try_action(position + tmp_ret.l + tmp_loop_ret.l, act)

                if not tmp_ret_1:
                    exit_break = True
                    # self.add_note_trace('Breaking inside loop')
                    break

                tmp_loop_ret += tmp_ret_1

            # self.trace_level -= 1
            # self.add_note_trace('looping end inside  AND', position + tmp_ret.l + tmp_loop_ret.l)
            self.add_end_trace(position + tmp_ret.l, tmp_ret)
            if exit_break:
                if tmp_loop_ret:
                    # self.add_note_trace('Breaking outside loop - 1')
                    break
                else:
                    tmp_ret += tmp_loop_ret
                    # self.add_note_trace('Breaking outside loop - 2')
                    break

            else:
                if tmp_loop_ret:
                    tmp_ret += tmp_loop_ret
                else:
                    # self.add_note_trace('Breaking outside loop - 3')
                    break

            final_loop_count += 1

        # self.trace_level -= 1
        # self.add_note_trace('looping end of outside AND at: ', position + tmp_ret.l)

        if final_loop_count >= min_loop and not empty_return:
            return final_loop_count, tmp_ret
        else:
            return 0, ParseResultFootball(self)

    def try_and(self, position, *args, min_loop=1, max_loop=1):
        count, tmp_ret = self.try_counted_and(position, *args, min_loop=min_loop, max_loop=max_loop)
        return tmp_ret

    def ipv6_segment(self, position, min_count=1, max_count=7):
        tmp_ret = self._empty
        tmp_ret += self.ipv6_hex(position)

        if tmp_ret:
            if max_count == 1:
                return 1, tmp_ret

            if not self.at_end(position + tmp_ret.l + 1) and \
                    self.this_char(position + tmp_ret.l) == ':' and \
                    self.this_char(position + tmp_ret.l + 1) == ':' and \
                    min_count <= 1:
                self.add_note_trace('Double Colons found, exiting')
                return 1, tmp_ret

            tmp_colon_str = {'string_in': self.COLON, 'min_count': 1, 'max_count': 1}
            tmp_count, tmp_ret_2 = self.try_counted_and(position + tmp_ret.l,
                                                        self.colon,
                                                        self.ipv6_hex, min_loop=min_count-1, max_loop=max_count-1)
        else:
            return 0, ParseResultFootball(self)

        if tmp_ret_2:
            return tmp_count+1, tmp_ret(tmp_ret_2)
        else:
            return 0, ParseResultFootball(self)

    def football_max(self, *footballs, names=None):
        names = names or []

        self.add_note_trace('Comparing Footballs')
        if self._set_trace(1):
            for index, fb in enumerate(footballs):
                if len(names) < index+1:
                    if fb.segment_name == '':
                        names.append('#%s' % index)
                    else:
                        names.append(fb.segment_name)

                if fb.error:
                    self.add_note_trace('Comp %s [ERROR] (%s/%s)' % (names[index], int(fb), fb._max_length))
                else:
                    self.add_note_trace('Comp %s (%s/%s)' % (names[index], int(fb), fb._max_length))
                self.add_note_trace('        %r' % fb.diags())


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

            if self._set_trace():
                self.add_note_trace('Test #%s: %s > %s  %s' % (index, names[a_index], names[b_index], ab_note))

        if self._set_trace(-1):
            self.add_note_trace('Returning %s' % names[tmp_index])
        return tmp_ret

    def check_part_end(self, position, football, err_expecting_code, is_domain):
        tmp_ret_codes = []

        def check_pos(pos):
            tmp_sub_codes = []
            self.add_note_trace('Checking Char: %s' % self.this_char(pos))
            sub_ret = self.dot(pos, non_segment=True)
            if sub_ret:
                tmp_sub_codes.append('ERR_DOT_END')
            else:
                sub_ret = self.back_slash(pos, non_segment=True)
                if sub_ret:
                    tmp_sub_codes.append('ERR_BACKSLASH_END')
                elif is_domain:
                    sub_ret = self.hyphen(pos, non_segment=True)
                    if sub_ret:
                        tmp_sub_codes.append('ERR_DOMAIN_HYPHEN_END')
            if not sub_ret:
                sub_ret = None
            return tmp_sub_codes, sub_ret

        tmp_ret = None
        plus_pos = None

        self.add_note_trace('Start End verification')
        self._set_trace(1)
        if is_domain:
            self.add_note_trace('In Domain')

            if football > 255:
                tmp_ret_codes.append('RFC5322_DOMAIN_TOO_LONG')

            end_pos = self.email_len
            if not self.at_end(position + football):
                self.add_note_trace('Not at end')
                if not self.at_end(position + football + 1):
                    plus_pos = end_pos + 1
                    self.add_note_trace('Has One Extra Char')
                    tmp_ret_codes.append(err_expecting_code)
                    return tmp_ret_codes, None
        else:
            self.add_note_trace('In Local')

            end_pos = position + football
            if self.this_char(position + football) != self.AT:
                self.add_note_trace('Not at end')
                if self.this_char(position + football + 1) != self.AT:
                    plus_pos = end_pos + 1
                    self.add_note_trace('Has One Extra Char')
                    tmp_ret_codes.append(err_expecting_code)
                    return tmp_ret_codes, None

        if plus_pos is not None:
            codes, tmp_ret = check_pos(plus_pos)
            if codes:
                tmp_ret_codes.extend(codes)
            else:
                tmp_ret_codes.append(err_expecting_code)
        else:
            codes, junk = check_pos(end_pos)
            tmp_ret_codes.extend(codes)

        self._set_trace(-1)

        if tmp_ret:
            self.add_note_trace('Finish end verification: returning obj + %r' % tmp_ret_codes)
        else:
            self.add_note_trace('Finish end verification: returning %r' % tmp_ret_codes)

        return tmp_ret_codes, tmp_ret

    # def check_domain(self):
    #     """
    #     send back:
    #         DNSWARN_NO_MX_RECORD
    #         DNSWARN_NO_RECORD
    #
    #         DNSWARN_INVALID_TLD
    #
    #     :param domain:
    #     :return:
    #     """
    #     tmp_ret = []
    #     if self.lookup_domain:
    #         if self.tlds:
    #             # check tld v. tlss list
    #             pass
    #
    #         # check for MX record
    #         # check for any record
    #     return tmp_ret
    #
    # def at_end_of_domain(self, position, football):
    #     add_to = []
    #     self.add_note_trace('Domain Validation: Start')
    #
    #     if not football or football.error:
    #         self.add_note_trace('    Domain Validation: Error or not found')
    #         return False, []
    #
    #     added_char = 0
    #     if self.at_end(position + football - 1) or self.at_end(position + football):
    #         tmp_char = self.this_char(-1)
    #         self.add_note_trace('Final domain char = ' + tmp_char)
    #         if tmp_char == self.HYPHEN:
    #             added_char = 1
    #             add_to.append('ERR_DOMAIN_HYPHEN_END')
    #         elif tmp_char == self.DOT:
    #             added_char = 1
    #             add_to.append('ERR_DOT_END')
    #         elif tmp_char == self.BACKSLASH:
    #             added_char = 1
    #             add_to.append('ERR_BACKSLASH_END')
    #
    #         if not self.at_end(position + football + added_char):
    #             add_to.append('ERR_EXPECTING_ATEXT')
    #
    #         if football > 255:
    #             add_to.append('RFC5322_DOMAIN_TOO_LONG')
    #
    #         self.add_note_trace('    Domain Validation: At end, diags to add: %s' % add_to)
    #         return True, add_to
    #
    #     else:
    #
    #         self.add_note_trace('    Domain Validation: Not at end')
    #         return False, []
    #
    # def validate_domain(self, position, football):
    #     at_end, tmp_adds = self.at_end_of_domain(position, football)
    #
    #     if not self.at_end(position + football):
    #         tmp_adds.append('ERR_EXPECTING_ATEXT')
    #
    #     return football(*tmp_adds)


    """
    def validate_domain(self, position, football, update_fb=None):
        update_fb = update_fb or football
        add_to = []
        if football.error:
            return False
        added_char = 0
        if self.at_end(position + football - 1) or self.at_end(position + football):
            tmp_char = self.this_char(-1)
            self.add_note_trace('Final domain char = ' + tmp_char)
            if tmp_char == self.HYPHEN:
                added_char = 1
                add_to.append('ERR_DOMAIN_HYPHEN_END')
            elif tmp_char == self.DOT:
                added_char = 1
                add_to.append('ERR_DOT_END')
                update_fb('ERR_DOT_END', raise_on_error=False)
            elif tmp_char == self.BACKSLASH:
                added_char = 1
                add_to.append('ERR_BACKSLASH_END')
                update_fb('ERR_BACKSLASH_END', raise_on_error=False)
        else:
            return False

        if football > 255:
            add_to.append('RFC5322_DOMAIN_TOO_LONG')
            update_fb('RFC5322_DOMAIN_TOO_LONG', raise_on_error=False)

        if not self.at_end(position + football + added_char):
            add_to.append('ERR_EXPECTING_ATEXT')
            update_fb('ERR_EXPECTING_ATEXT', raise_on_error=False)
    """


    # **********************************************************************************
    # ******** START PARSERS
    #
    #    Everything under here should return a football
    # **********************************************************************************

    """
        [1000]                     VALID  Valid Email (ISEMAIL_VALID_CATEGORY)
        [1005]      DNSWARN_NO_MX_RECORD  Couldn't find an MX record for this domain but an A-record does exist (ISEMAIL_DNSWARN)
        [1006]         DNSWARN_NO_RECORD  Couldn't find an MX record or an A-record for this domain (ISEMAIL_DNSWARN)
        [1009]               RFC5321_TLD  Address is valid but at a Top Level Domain (ISEMAIL_RFC5321)
        [1010]       RFC5321_TLD_NUMERIC  Address is valid but the Top Level Domain begins with a number (ISEMAIL_RFC5321)
        [1011]     RFC5321_QUOTED_STRING  Address is valid but contains a quoted string (ISEMAIL_RFC5321)
        [1012]   RFC5321_ADDRESS_LITERAL  Address is valid but at a literal address not a domain (ISEMAIL_RFC5321)
        [1013]   RFC5321_IPV6_DEPRECATED  Address is valid but contains a :: that only elides one zero group. All implementations must accept and be able to handle any legitimate RFC 4291 format. (ISEMAIL_DEPREC)
        [1017]              CFWS_COMMENT  Address contains comments (ISEMAIL_CFWS)
        [1018]                  CFWS_FWS  Address contains FWS (ISEMAIL_CFWS)
        [1033]         DEPREC_LOCAL_PART  The local part is in a deprecated form (ISEMAIL_DEPREC)
        [1034]                DEPREC_FWS  Address contains an obsolete form of Folding White Space (ISEMAIL_DEPREC)
        [1035]              DEPREC_QTEXT  A quoted string contains a deprecated character (ISEMAIL_DEPREC)
        [1036]                 DEPREC_QP  A quoted pair contains a deprecated character (ISEMAIL_DEPREC)
        [1037]            DEPREC_COMMENT  Address contains a comment in a position that is deprecated (ISEMAIL_DEPREC)
        [1038]              DEPREC_CTEXT  A comment contains a deprecated character (ISEMAIL_DEPREC)
        [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign (ISEMAIL_DEPREC)
        [1065]            RFC5322_DOMAIN  Address is RFC 5322 compliant but contains domain characters that are not allowed by DNS (ISEMAIL_RFC5322)
        [1066]          RFC5322_TOO_LONG  Address is too long (ISEMAIL_RFC5322)
        [1067]    RFC5322_LOCAL_TOO_LONG  The local part of the address is too long (ISEMAIL_RFC5322)
        [1068]   RFC5322_DOMAIN_TOO_LONG  The domain part is too long (ISEMAIL_RFC5322)
        [1069]    RFC5322_LABEL_TOO_LONG  The domain part contains an element that is too long (ISEMAIL_RFC5322)
        [1070]    RFC5322_DOMAIN_LITERAL  The domain literal is not a valid RFC 5321 address literal (ISEMAIL_RFC5322)
        [1071] RFC5322_DOM_LIT_OBS_DTEXT  The domain literal is not a valid RFC 5321 address literal and it contains obsolete characters (ISEMAIL_RFC5322)
        [1072]    RFC5322_IPV6_GRP_COUNT  The IPv6 literal address contains the wrong number of groups (ISEMAIL_RFC5322)
        [1073]   RFC5322_IPV6_2X2X_COLON  The IPv6 literal address contains too many :: sequences (ISEMAIL_RFC5322)
        [1074]     RFC5322_IPV6_BAD_CHAR  The IPv6 address contains an illegal group of characters (ISEMAIL_RFC5322)
        [1075]     RFC5322_IPV6_MAX_GRPS  The IPv6 address has too many groups (ISEMAIL_RFC5322)
        [1076]   RFC5322_IPV6_COLON_STRT  IPv6 address starts with a single colon (ISEMAIL_RFC5322)
        [1077]    RFC5322_IPV6_COLON_END  IPv6 address ends with a single colon (ISEMAIL_RFC5322)
        [1129]       ERR_EXPECTING_DTEXT  A domain literal contains a character that is not allowed (ISEMAIL_ERR)
        [1130]         ERR_NO_LOCAL_PART  Address has no local part (ISEMAIL_ERR)
        [1131]        ERR_NO_DOMAIN_PART  Address has no domain part (ISEMAIL_ERR)
        [1132]      ERR_CONSECUTIVE_DOTS  The address may not contain consecutive dots (ISEMAIL_ERR)
        [1133]      ERR_ATEXT_AFTER_CFWS  Address contains text after a comment or Folding White Space (ISEMAIL_ERR)
        [1134]        ERR_ATEXT_AFTER_QS  Address contains text after a quoted string (ISEMAIL_ERR)
        [1135]    ERR_ATEXT_AFTER_DOMLIT  Extra characters were found after the end of the domain literal (ISEMAIL_ERR)
        [1136]       ERR_EXPECTING_QPAIR  The address contains a character that is not allowed in a quoted pair (ISEMAIL_ERR)
        [1137]       ERR_EXPECTING_ATEXT  Address contains a character that is not allowed (ISEMAIL_ERR)
        [1138]       ERR_EXPECTING_QTEXT  A quoted string contains a character that is not allowed (ISEMAIL_ERR)
        [1139]       ERR_EXPECTING_CTEXT  A comment contains a character that is not allowed (ISEMAIL_ERR)
        [1140]         ERR_BACKSLASH_END  The address can't end with a backslash (ISEMAIL_ERR)
        [1141]             ERR_DOT_START  Neither part of the address may begin with a dot (ISEMAIL_ERR)
        [1142]               ERR_DOT_END  Neither part of the address may end with a dot (ISEMAIL_ERR)
        [1143]   ERR_DOMAIN_HYPHEN_START  A domain or subdomain cannot begin with a hyphen (ISEMAIL_ERR)
        [1144]     ERR_DOMAIN_HYPHEN_END  A domain or subdomain cannot end with a hyphen (ISEMAIL_ERR)
        [1145]   ERR_UNCLOSED_QUOTED_STR  Unclosed quoted string (ISEMAIL_ERR)
        [1146]      ERR_UNCLOSED_COMMENT  Unclosed comment (ISEMAIL_ERR)
        [1147]      ERR_UNCLOSED_DOM_LIT  Domain literal is missing its closing bracket (ISEMAIL_ERR)
        [1148]           ERR_FWS_CRLF_X2  Folding White Space contains consecutive CRLF sequences (ISEMAIL_ERR)
        [1149]          ERR_FWS_CRLF_END  Folding White Space ends with a CRLF sequence (ISEMAIL_ERR)
        [1150]              ERR_CR_NO_LF  Address contains a carriage return that is not followed by a line feed (ISEMAIL_ERR)
        [1151]         ERR_NO_DOMAIN_SEP  Address does not contain a domain seperator (@ sign) (ISEMAIL_ERR)
        [1255]         ERR_EMPTY_ADDRESS  Empty Address Passed (ISEMAIL_ERR)


        ???
                    [1037]            DEPREC_COMMENT  Address contains a comment in a position that is deprecated (ISEMAIL_DEPREC)
        [1137]       ERR_EXPECTING_ATEXT  Address contains a character that is not allowed (ISEMAIL_ERR)

    Maximums:
        Username or local part = 64    RFC5322_LOCAL_TOO_LONG
        total address length = 254 RFC5322_TOO_LONG
        domain name = 255 RFC5322_DOMAIN_TOO_LONG
        domain name label = 63 : RFC5322_LABEL_TOO_LONG

    """

    @as_football(skip=True)
    def address_spec(self, position):

        """
        addr-spec       =   local-part "@" domain

        [1000]                     VALID  Valid Email (ISEMAIL_VALID_CATEGORY)
        [1066]          RFC5322_TOO_LONG  Address is too long (ISEMAIL_RFC5322)
        [1130]         ERR_NO_LOCAL_PART  Address has no local part (ISEMAIL_ERR)
        [1131]        ERR_NO_DOMAIN_PART  Address has no domain part (ISEMAIL_ERR)
        [1132]      ERR_CONSECUTIVE_DOTS  The address may not contain consecutive dots (ISEMAIL_ERR)
        [1140]         ERR_BACKSLASH_END  The address can't end with a backslash (ISEMAIL_ERR)
        [1141]             ERR_DOT_START  Neither part of the address may begin with a dot (ISEMAIL_ERR)
        [1142]               ERR_DOT_END  Neither part of the address may end with a dot (ISEMAIL_ERR)
        [1151]         ERR_NO_DOMAIN_SEP  Address does not contain a domain seperator (@ sign) (ISEMAIL_ERR)
        [1255]         ERR_EMPTY_ADDRESS  Empty Address Passed (ISEMAIL_ERR)

        [1133]      ERR_ATEXT_AFTER_CFWS  Address contains text after a comment or Folding White Space (ISEMAIL_ERR)
        [1134]        ERR_ATEXT_AFTER_QS  Address contains text after a quoted string (ISEMAIL_ERR)

        """
        self.in_local_part = True
        self.in_domain_part = False
        self.near_at_flag = False
        tmp_ret = self._empty
        self.add_note_trace('Address Length: ' + str(self.email_len))

        if self.email_len == 0:
            self.add_note_trace('Empty address')
            return tmp_ret('ERR_EMPTY_ADDRESS')

        tmp_ret += self.local_part(position)

        if not tmp_ret:
            tmp_ret += self.at(position)
            if tmp_ret:
                return tmp_ret('ERR_NO_LOCAL_PART')
            else:
                return tmp_ret('ERR_UNKNOWN')

        self.in_local_part = False

        tmp_ret_2 = self.at(position + tmp_ret)

        self.near_at_flag = True
        self.in_domain_part = True

        if tmp_ret_2:
            tmp_ret_2.at_loc = position + tmp_ret

            tmp_ret_3 = self.domain(position + tmp_ret + tmp_ret_2)

            if tmp_ret_3:
                tmp_ret += tmp_ret_2
                tmp_ret += tmp_ret_3
            else:
                return tmp_ret(tmp_ret_2, 'ERR_NO_DOMAIN_PART')

        elif not self.find(position + tmp_ret, self.AT, skip_quoted_str=True):
                tmp_ret('ERR_NO_DOMAIN_SEP')
        else:
            return tmp_ret

        if tmp_ret > 254:
            tmp_ret('RFC5322_TOO_LONG')

        if not tmp_ret.results:
            tmp_ret('VALID')

        return tmp_ret

    # def local_part_skip(self, position, football):
    #     skip_next = False
    #     if football and not football.error:
    #         if self.at_end(position + football) and not football.error:
    #             self.add_note_trace('Skipping due to at the end (and no error)')
    #             skip_next = True
    #         elif self.this_char(position + football) == self.AT and not football.error:
    #             self.add_note_trace('Skipping due to @ next (and no error)')
    #             skip_next = True
    #     return skip_next

    @as_football()
    def local_part(self, position):

        tmp_ret = self._empty

        if self.this_char(position) == self.DOT:
            return tmp_ret('ERR_DOT_START')

        tmp_ret += self._local_part(position)

        if 'RFC5321_QUOTED_STRING' in tmp_ret:
            extra_text_error = 'ERR_ATEXT_AFTER_QS'
        else:
            if 'CFWS_LAST' in tmp_ret.flags:
                extra_text_error = 'ERR_ATEXT_AFTER_CFWS'
            else:
                extra_text_error = 'ERR_EXPECTING_ATEXT'

        if self.at_in_cfws:
            tmp_ret('DEPREC_CFWS_NEAR_AT')

        if self.this_char(position + tmp_ret) != self.AT:
            tmp_ret(extra_text_error)

            if not self.find(position + tmp_ret, self.AT, skip_quoted_str=True):
                tmp_ret('ERR_NO_DOMAIN_SEP')

        else:
            if tmp_ret > 64:
                tmp_ret('RFC5322_LOCAL_TOO_LONG')

            last_char = self.this_char(-1)

            if last_char == self.BACKSLASH:
                tmp_ret('ERR_BACKSLASH_END')
            elif last_char == self.DOT:
                tmp_ret('ERR_DOT_END')

        if tmp_ret.error:
            raise ParsingError(tmp_ret)

        return tmp_ret

    def _local_part(self, position):
        """        
        local-part      =   dot-atom / quoted-string / obs-local-part
            // http://tools.ietf.org/html/rfc5321#section-4.5.3.1.1
            //   The maximum total length of a user name or other local-part is 64
            //   octets.


        [1033]         DEPREC_LOCAL_PART  The local part is in a deprecated form (ISEMAIL_DEPREC)
        [1067]    RFC5322_LOCAL_TOO_LONG  The local part of the address is too long (ISEMAIL_RFC5322)

        """

        tmp_dot_atom = self.dot_atom(position)
        if tmp_dot_atom:
            return tmp_dot_atom

        tmp_qstring = self.quoted_string(position)
        if tmp_qstring:
            return tmp_qstring

        tmp_obs_lpart = self.obs_local_part(position)
        if tmp_obs_lpart:
            return tmp_obs_lpart

        return self.football_max(tmp_dot_atom, tmp_qstring, tmp_obs_lpart,
                                 names=['dot-atom', 'quoted_string', 'obs_local_part'])

        # try:
        #     tmp_ret_2 = self.dot_atom(position)
        #
        # except ParsingError as err:
        #     tmp_ret_2 = err.results
        #
        # skip_next = self.local_part_skip(position, tmp_ret_2)
        #
        # if not skip_next:
        #     self.add_note_trace('Trying Quoted String')
        #     try:
        #         tmp_ret_3 = self.quoted_string(position)
        #
        #     except ParsingError as err:
        #         tmp_ret_3 = err.results
        #
        #     tmp_ch, tmp_ret_2 = self.football_max(tmp_ret_2, tmp_ret_3)
        #     if tmp_ch == 0:
        #         is_qs = True
        #
        #     skip_next = self.local_part_skip(position, tmp_ret_3)
        # else:
        #     self.add_note_trace('skipping Quoted String')
        #
        # if not skip_next:
        #     try:
        #         self.add_note_trace('trying obs-local-part')
        #         tmp_ret_3 = self.obs_local_part(position)
        #
        #     except ParsingError as err:
        #         tmp_ret_3 = err.results
        #
        #     tmp_ch, tmp_ret_2 = self.football_max(tmp_ret_2, tmp_ret_3)
        #     if tmp_ch == 0:
        #         is_qs = False
        # else:
        #     self.add_note_trace('skipping obs-local-part')
        #
        # tmp_ret(tmp_ret_2, raise_on_error=False)
        #
        # self.add_note_trace('Returning length: ' + str(tmp_ret.l))
        # if not self.at_end(position + tmp_ret):
        #     self.add_note_trace('not at the end, checking next char: ' + self.this_char(position + tmp_ret))
        #     if self.this_char(position + tmp_ret) == self.DOT:
        #         self.add_note_trace('adding a dot end warning')
        #         # errors_to_add.append('ERR_DOT_END')
        #         tmp_ret('ERR_DOT_END', raise_on_error=False)
        #
        # if tmp_ret:
        #     if not self.at_end(position + tmp_ret):
        #         if self.this_char(position + tmp_ret) != self.AT:
        #             if is_qs:
        #                 self.add_note_trace('adding ERR_ATEXT_AFTER_QS for QS')
        #                 tmp_ret('ERR_ATEXT_AFTER_QS', raise_on_error=False)
        #             else:
        #                 self.add_note_trace('adding ERR_EXPECTING_ATEXT')
        #                 tmp_ret('ERR_EXPECTING_ATEXT', raise_on_error=False)
        #
        # if 'DEPREC_LOCAL_PART' in tmp_ret and 'CFWS_COMMENT' in tmp_ret:
        #     tmp_ret('DEPREC_COMMENT')
        #
        # if tmp_ret.error:
        #     self.add_note_trace('Raising the error')
        #     raise ParsingError(results=tmp_ret)
        #
        # return tmp_ret

    def domain_dot_atom(self, *args, **kwargs):
        tmp_ret = self.dot_atom(*args, **kwargs)
        if tmp_ret:
            tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.DNS
            tmp_ret('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN')
        return tmp_ret

    @as_football()
    def dot_atom(self, position, init_cfws=None):
        """
        dot-atom        =   [CFWS] dot-atom-text [CFWS]
        """

        tmp_ret = self._empty
        self.near_at_flag = False
        self.at_in_cfws = False

        if init_cfws is None:
            tmp_ret_cfws = self.cfws(position)
        else:
            tmp_ret_cfws = init_cfws

        tmp_ret_cfws.flags -= 'CFWS_LAST'

        tmp_ret_2 = self.dot_atom_text(position + tmp_ret_cfws)

        if tmp_ret_2:
            tmp_ret += tmp_ret_cfws
            tmp_ret += tmp_ret_2

            tmp_ret_cfws = self.cfws(position + tmp_ret)

            tmp_ret += tmp_ret_cfws

        return tmp_ret

    @as_football()
    def dot_atom_text(self, position):
        """
            dot-atom-text   =   1*atext *("." 1*atext)
        """
        tmp_ret = self._empty
        tmp_ret += self.atext(position)
        # self.add_note_trace('1 tmp_ret.l = ' + str(tmp_ret.l ))
        if self.at_end(position + tmp_ret):
            return tmp_ret

        if tmp_ret:
            while True:
                tmp_ret_2 = self.single_dot(position + tmp_ret)
                if tmp_ret_2:
                    tmp_ret_3 = self.atext(position + tmp_ret + tmp_ret_2)
                    if tmp_ret_3:
                        tmp_ret += tmp_ret_2
                        tmp_ret += tmp_ret_3
                        continue
                break

        return tmp_ret

    @as_football(diags='DEPREC_LOCAL_PART')
    def obs_local_part(self, position):
        """
            obs-local-part = word *("." word)

        """
        tmp_word = self.word(position)
        tmp_ret = self._empty

        if not tmp_word:
            return tmp_ret

        tmp_ret += tmp_word

        tmp_ret += self.try_and(position + tmp_ret,
                                self.single_dot,
                                self.word,
                                min_loop=0, max_loop=256)

        if 'CFWS_COMMENT' in tmp_ret:
            tmp_ret('DEPREC_COMMENT')

        return tmp_ret

    @as_football()
    def word(self, position):
        """
            word = atom / quoted-string
        """
        self.at_in_cfws = False
        tmp_ret = self._empty
        # tmp_act, tmp_ret2 = self.try_or(position,
        #                       self.atom,
        #                       self.quoted_string)

        tmp_ret_2 = self.atom(position)
        if tmp_ret_2 and not tmp_ret_2.error:
            return tmp_ret(tmp_ret_2)

        tmp_ret_3 = self.quoted_string(position)
        if tmp_ret_3 and not tmp_ret_3.error:
            return tmp_ret(tmp_ret_3)

        return tmp_ret(self.football_max(tmp_ret_2, tmp_ret_3, names=['atom', 'quoted_string']))


    @as_football()
    def atom(self, position, init_cfws=None):
        """
                atom = [CFWS] 1*atext [CFWS]

                // The entire local-part can be a quoted string for RFC 5321
                // If it's just one atom that is quoted then it's an RFC 5322 obsolete form
        """

        tmp_ret = self._empty

        if init_cfws is None:
            tmp_ret += self.cfws(position)
        else:
            tmp_ret += init_cfws

        tmp_ret.flags -= 'CFWS_LAST'

        self.near_at_flag = False

        tmp_ret_2 = self.atext(position + tmp_ret)

        if not tmp_ret_2:
            return tmp_ret('ERR_EXPECTING_ATEXT')

        tmp_ret += tmp_ret_2
        tmp_ret_cfws = self.cfws(position + tmp_ret)

        tmp_ret += tmp_ret_cfws

        if tmp_ret and tmp_ret_cfws:
            self.add_note_trace('Found last CFWS')
            if not (self.at_end(position + tmp_ret + tmp_ret_cfws) or
                    self.this_char(position + tmp_ret + tmp_ret_cfws) == self.AT or
                    self.this_char(position + tmp_ret + tmp_ret_cfws) == self.DOT):
                tmp_ret('ERR_ATEXT_AFTER_CFWS', raise_on_error=False)

        # if not tmp_ret or tmp_ret.error:
        #     self.near_at_flag = tmp_near_at_flag

        return tmp_ret

    @as_football()
    def domain(self, position):

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
            //   of a top-level domain used by itself in an email address, a single
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
        tmp_ret = self._empty

        only_domain_lit = False
        is_literal = False
        # has_cfws = False

        lit_init = self._empty
        lit_sb = self.open_sq_bracket(position)

        if lit_sb:
            is_literal = True
            lit_init += lit_sb
            lit_cfws = self._empty
        else:
            lit_cfws = self.cfws(position)
            if lit_cfws:
                # has_cfws = True
                lit_init += lit_cfws
                lit_sb += self.open_sq_bracket(position + lit_cfws)
                if lit_sb:
                    is_literal = True
                    only_domain_lit = True
                    lit_init += lit_sb

        if is_literal:
            tmp_ret += self._domain_literals(position, lit_init, only_domain_lit)
        else:
            tmp_char = self.this_char(position)
            if tmp_char == self.HYPHEN:
                return tmp_ret('ERR_DOMAIN_HYPHEN_START')
            elif tmp_char == self.DOT:
                return tmp_ret('ERR_DOT_START')

            tmp_ret += self._domain_non_literals(position, lit_cfws)

        if is_literal:
            extra_text_error = 'ERR_ATEXT_AFTER_DOMLIT'
        elif 'RFC5322_LIMITED_DOMAIN' in tmp_ret:
            if 'CFWS_LAST' in tmp_ret.flags:
                extra_text_error = 'ERR_ATEXT_AFTER_CFWS'
            else:
                extra_text_error = 'ERR_EXPECTING_ATEXT'
        else:
            extra_text_error = 'ERR_EXPECTING_DTEXT'

        if not self.at_end(position + tmp_ret):
            tmp_ret(extra_text_error)
        else:
            if tmp_ret > 255:
                tmp_ret('RFC5322_DOMAIN_TOO_LONG')

            last_char = self.this_char(-1)

            if last_char == self.HYPHEN:
                tmp_ret('ERR_DOMAIN_HYPHEN_END')
            elif last_char == self.BACKSLASH:
                tmp_ret('ERR_BACKSLASH_END')
            elif last_char == self.DOT:
                tmp_ret('ERR_DOT_END')

        if tmp_ret.error:
            raise ParsingError(tmp_ret)

        return tmp_ret

    def _domain_non_literals(self, position, init_cfws=None):

        if not init_cfws:
            tmp_domain_addr = self.domain_addr(position)
            if tmp_domain_addr:
                return tmp_domain_addr
        else:
            tmp_domain_addr = self._empty

        tmp_dot_atom = self.domain_dot_atom(position, init_cfws=init_cfws)
        if tmp_dot_atom:
            return tmp_dot_atom

        tmp_obs_domain = self.obs_domain(position, init_cfws=init_cfws)
        if tmp_obs_domain:
            return tmp_obs_domain

        return self.football_max(tmp_domain_addr, tmp_dot_atom, tmp_obs_domain, names=['domain_addr', 'dot_atom', 'obs_domain'])

    def _domain_literals(self, position, init_lit, only_domain_lit):

        tmp_close_loc = self.find(position + init_lit, self.CLOSESQBRACKET)
        if tmp_close_loc == -1:
            tmp_ret = self._empty
            return tmp_ret('ERR_UNCLOSED_DOM_LIT')

        if not only_domain_lit:
            tmp_addr_lit = self.address_literal(position, init_lit)
            if tmp_addr_lit:
                return tmp_addr_lit
        else:
            tmp_addr_lit = self._empty

        tmp_dom_lit = self.domain_literal(position, init_lit)
        if tmp_dom_lit:
            return tmp_dom_lit

        return self.football_max(tmp_addr_lit, tmp_dom_lit, names=['addr_lit', 'domain_lit'])


    # @as_football(segment=False)
    # def literals(self, position):
    #     only_domain_lit = False
    #     tmp_ret = self._empty
    #     tmp_ret_2 = self.open_sq_bracket(position)
    #
    #     if not self.open_sq_bracket(position, non_segment=True):
    #         tmp_ret_2 += self.cfws(position, non_segment=True)
    #         if tmp_ret:
    #             tmp_ret_2 += self.open_sq_bracket(position + tmp_ret, non_segment=True)
    #             only_domain_lit = True
    #         else:
    #             return tmp_ret
    #
    #     tmp_close_loc = self.find(position + tmp_ret_2, self.CLOSESQBRACKET)
    #     if tmp_close_loc == -1:
    #         return tmp_ret('ERR_UNCLOSED_DOM_LIT')
    #
    #     tmp_ret_2 = self._empty
    #     if not only_domain_lit:
    #         try:
    #             tmp_ret_2 = self.address_literal(position)
    #         except ParsingError as err:
    #             tmp_ret_2 = err.results
    #
    #     if tmp_ret_2:
    #         if self.at_end(position + tmp_ret_2):
    #             return tmp_ret(tmp_ret_2)
    #         else:
    #             if not tmp_ret_2.error:
    #                 tmp_ret += tmp_ret_2
    #                 return tmp_ret('ERR_ATEXT_AFTER_DOMLIT')
    #
    #     self.add_note_trace('Should be non-ip-address domain literal')
    #     tmp_ret_3 = self.domain_literal(position)
    #     if tmp_ret_3:
    #         tmp_ret_3('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN')
    #         tmp_ret += tmp_ret_3
    #         if not self.at_end(position + tmp_ret_3):
    #             tmp_ret += tmp_ret_3
    #             return tmp_ret('ERR_ATEXT_AFTER_DOMLIT')
    #
    #     tmp_index, tmp_ret_4 = self.football_max(tmp_ret_2, tmp_ret_3)
    #     tmp_ret += tmp_ret_4
    #     if tmp_ret.error:
    #         raise ParsingError(tmp_ret_2)
    #
    #     if not self.at_end(position + tmp_ret):
    #         return tmp_ret('ERR_ATEXT_AFTER_DOMLIT')
    #
    #     add_to = []
    #
    #     if self.at_end(position + tmp_ret - 1) or self.at_end(position + tmp_ret):
    #         added_char = 0
    #         tmp_char = self.this_char(-1)
    #         self.add_note_trace('Final domain char = ' + tmp_char)
    #         if tmp_char == self.HYPHEN:
    #             added_char = 1
    #             add_to.append('ERR_DOMAIN_HYPHEN_END')
    #         elif tmp_char == self.DOT:
    #             added_char = 1
    #             add_to.append('ERR_DOT_END')
    #         elif tmp_char == self.BACKSLASH:
    #             added_char = 1
    #             add_to.append('ERR_BACKSLASH_END')
    #
    #         if not self.at_end(position + tmp_ret + added_char):
    #             add_to.append('ERR_EXPECTING_ATEXT')
    #
    #         if tmp_ret > 255:
    #             add_to.append('RFC5322_DOMAIN_TOO_LONG')
    #
    #         self.add_note_trace('    Domain Validation: At end, diags to add: %s' % add_to)
    #
    #         tmp_ret(*add_to, raise_on_error=False)
    #
    #     return tmp_ret('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN')
    #
    #     return tmp_ret


    @as_football()
    def domain_addr(self, position):
        """
        domain-addr = sub-domain *("." sub-domain)
        [1009]               RFC5321_TLD  Address is valid but at a Top Level Domain (ISEMAIL_RFC5321)
        [1010]       RFC5321_TLD_NUMERIC  Address is valid but the Top Level Domain begins with a number (ISEMAIL_RFC5321)

        """
        last_dom_pos = position
        is_tld = True
        tmp_ret = self._empty
        tmp_ret += self.sub_domain(position)
        # if not tmp_ret:
        #     tmp_ret = self.sub_domain(position)
        #     if tmp_ret:
        #         tmp_ret('RFC5321_TLD_NUMERIC')

        if not tmp_ret:
            return tmp_ret

        while True:
            tmp_ret_2 = self.single_dot(position + tmp_ret)
            if not tmp_ret_2:
                break
            tmp_ret_3 = self.sub_domain(position + tmp_ret + tmp_ret_2)
            if not tmp_ret_3:
                break
            last_dom_pos = position + tmp_ret + tmp_ret_2
            tmp_ret += tmp_ret_2
            tmp_ret += tmp_ret_3
            is_tld = False

        if is_tld:
            tmp_ret('RFC5321_TLD')

        if self.this_char(last_dom_pos) in self.DIGIT:
            tmp_ret('RFC5321_TLD_NUMERIC')
            tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.OTHER_NON_DNS
        else:
            tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.DNS

        return tmp_ret

        # add_to = []
        #
        # if self.at_end(position + tmp_ret + 1):
        #
        #     tmp_ret_2 = self.single_char(position + tmp_ret, self.HYPHEN)
        #     if tmp_ret_2:
        #         tmp_ret += tmp_ret_2
        #         tmp_ret('ERR_DOMAIN_HYPHEN_END', raise_on_error=False)
        #
        #     tmp_ret_2 = self.single_char(position + tmp_ret, self.DOT)
        #     if tmp_ret_2:
        #         tmp_ret += tmp_ret_2
        #         tmp_ret('ERR_DOT_END', raise_on_error=False)
        #
        #     tmp_ret_2 = self.single_char(position + tmp_ret, self.BACKSLASH)
        #     if tmp_ret_2:
        #         tmp_ret += tmp_ret_2
        #         tmp_ret('ERR_BACKSLASH_END', raise_on_error=False)
        #
        # elif not self.at_end(position + tmp_ret):
        #     add_to.append('ERR_EXPECTING_DTEXT')
        #
        # if tmp_ret > 255:
        #      add_to.append('RFC5322_DOMAIN_TOO_LONG')
        #
        # return tmp_ret(*add_to, raise_on_error=False)

    # @as_football()
    # def tld_domain(self, position):
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
    #     tmp_ret = self._empty
    #     tmp_ret += self.alpha(position)
    #     if tmp_ret:
    #         tmp_ret += self.ldh_str(position + tmp_ret)
    #         if tmp_ret.l > 63:
    #             tmp_ret('RFC5322_LABEL_TOO_LONG')
    #         return tmp_ret
    #     else:
    #         return self._empty

    @as_football()
    def sub_domain(self, position):
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
        tmp_ret = self._empty
        tmp_ret += self.let_dig(position)
        if tmp_ret:
            tmp_ret += self.ldh_str(position + tmp_ret)

            if tmp_ret.l > 63:
                tmp_ret('RFC5322_LABEL_TOO_LONG')

            return tmp_ret
        else:
            return self._empty

    # @as_football()
    # def let_str(self, position):
    #     """
    #             Ldh-str        = *( ALPHA / DIGIT / "-" ) Let-dig
    #     """
    #     tmp_ret = self._empty
    #     tmp_ret += self.ldh_str(position)
    #
    #     while tmp_ret and self.this_char(position + tmp_ret.l-1) not in self.LET_DIG:
    #         tmp_ret -= 1
    #
    #     if tmp_ret:
    #         return tmp_ret
    #
    #     return self._empty

    @as_football(diags=['RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_LIMITED_DOMAIN'])
    def domain_literal(self, position, lit_init=None):
        """
        domain-literal  =   [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
        // Domain literal must be the only component

        [1070]    RFC5322_DOMAIN_LITERAL  The domain literal is not a valid RFC 5321 address literal (ISEMAIL_RFC5322)
        [1129]       ERR_EXPECTING_DTEXT  A domain literal contains a character that is not allowed (ISEMAIL_ERR)
        [1135]    ERR_ATEXT_AFTER_DOMLIT  Extra characters were found after the end of the domain literal (ISEMAIL_ERR)
        [1147]      ERR_UNCLOSED_DOM_LIT  Domain literal is missing its closing bracket (ISEMAIL_ERR)
        """
        tmp_ret = self._empty
        if lit_init is None:
            lit_init = self._empty
            lit_init += self.cfws(position)
            lit_init_sb = self.open_sq_bracket(position + lit_init)
            if not lit_init_sb:
                return tmp_ret
            else:
                lit_init += lit_init_sb

        lit_init.flags -= 'CFWS_LAST'

        tmp_ret += lit_init

        # tmp_ret += self.cfws(position)
        # tmp_near_at_flag = self.near_at_flag
        self.near_at_flag = False
        # tmp_ret_2 = self.open_sq_bracket(position + tmp_ret.l)

        # if not tmp_ret_2:
            # self.near_at_flag = tmp_near_at_flag
        #     return self._empty

        # tmp_loc_close = self.find(position + tmp_ret, self.CLOSESQBRACKET)
        # if tmp_loc_close == -1:
        #     return tmp_ret('ERR_UNCLOSED_DOM_LIT')

        # tmp_ret += tmp_ret_2

        # tmp_ret_2 = self.domain_literal_sub(position + tmp_ret, non_segment=True)
        # ************************
        tmp_ret_2 = self._empty
        has_dtext = False
        while True:
            tmp_ret_fws = self.fws(position + tmp_ret + tmp_ret_2)

            tmp_ret_dtext = self.dtext(position + tmp_ret + tmp_ret_2 + tmp_ret_fws)

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
            tmp_ret_2 += self.fws(position + tmp_ret + tmp_ret_2)
        else:
            # self.near_at_flag = tmp_near_at_flag
            return tmp_ret('ERR_EXPECTING_DTEXT', raise_on_error=False)

        tmp_ret += tmp_ret_2

        tmp_ret_2 = self.close_sq_bracket(position + tmp_ret)

        if tmp_ret_2:
            tmp_ret += tmp_ret_2
            if tmp_ret == 2:
                return tmp_ret('ERR_EXPECTING_DTEXT', raise_on_error=False)

        else:
            if self.at_end(position + tmp_ret):
                return tmp_ret('ERR_UNCLOSED_DOM_LIT', raise_on_error=False)
            else:
                return tmp_ret('ERR_EXPECTING_DTEXT', raise_on_error=False)

        tmp_ret += self.cfws(position + tmp_ret)

        if tmp_ret and not self.at_end(position + tmp_ret + 1):
            tmp_ret('ERR_ATEXT_AFTER_DOMLIT', raise_on_error=False)

        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT

        if tmp_ret > 255:
            tmp_ret('RFC5322_DOMAIN_TOO_LONG', raise_on_error=False)

        return tmp_ret

    # @as_football()
    # def domain_literal_sub(self, position):
    #     """
    #     domain-literal-sub  =   *([FWS] dtext) [FWS]
    #     """
    #
    #     tmp_ret = ParseResultFootball(self)
    #     while True:
    #         tmp_ret_fws = self.fws(position + tmp_ret.l)
    #
    #         tmp_ret_dtext = self.dtext(position + tmp_ret.l + tmp_ret_fws.l)
    #
    #         if tmp_ret_dtext:
    #             tmp_ret += tmp_ret_fws
    #             tmp_ret += tmp_ret_dtext
    #         else:
    #             break
    #
    #     if tmp_ret:
    #         tmp_ret += self.fws(position + tmp_ret.l)
    #
    #     return tmp_ret

    @as_football()
    def dtext(self, position):

        """
            dtext           =   %d33-90 /          ; Printable US-ASCII
                               %d94-126 /         ;  characters not including
                               obs-dtext          ;  "[", "]", or "\"
        """
        tmp_ret = self._empty

        while True:
            tmp_ret_2 = self.simple_char(position + tmp_ret, self.DTEXT)
            tmp_ret_2 += self.obs_dtext(position + tmp_ret + tmp_ret_2)
            if tmp_ret_2:
                tmp_ret += tmp_ret_2
            else:
                break

        # tmp_act, tmp_ret_2 = self.try_or(position,
        #                                self.dtext_sub,
        #                               self.obs_dtext)

        return tmp_ret

    # @as_football(segment=False)
    # def dtext_sub(self, position):
    #
    #     """
    #         dtext           =   %d33-90 /          ; Printable US-ASCII
    #                            %d94-126 /         ;  characters not including
    #                            obs-dtext          ;  "[", "]", or "\"
    #     """
    #     return self.simple_char(position, self.DTEXT)

    @as_football(diags='RFC5322_DOM_LIT_OBS_DTEXT')
    def obs_dtext(self, position):

        """
                obs-dtext       =   obs-NO-WS-CTL / quoted-pair
        [1071] RFC5322_DOM_LIT_OBS_DTEXT  The domain literal is not a valid RFC 5321 address literal and it contains obsolete characters (ISEMAIL_RFC5322)

        """
        tmp_ret = self._empty

        while True:
            tmp_ret_2 = self.obs_dtext_sub(position + tmp_ret)

            tmp_ret_2 += self.quoted_pair(position + tmp_ret + tmp_ret_2)

            if tmp_ret_2:
                tmp_ret += tmp_ret_2
            else:
                break

        return tmp_ret

    @as_football(diags=['RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN'])
    def obs_domain(self, position, init_cfws=None):
        """
        obs-domain      =   atom *("." atom)
                [1037]            DEPREC_COMMENT  Address contains a comment in a position that is deprecated (ISEMAIL_DEPREC)
        """
        tmp_ret = self._empty
        tmp_ret += self.atom(position, init_cfws=init_cfws)

        if not tmp_ret:
            return tmp_ret('ERR_EXPECTING_ATEXT', raise_on_error=False)

        tmp_ret += self.try_and(position + tmp_ret.l,
                                self.single_dot,
                                self.atom,
                                min_loop=0, max_loop=256)

        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.OTHER_NON_DNS

        add_to = []

        if self.at_end(position + tmp_ret + 1):
            #added_char = 0
            #tmp_char = self.this_char(-1)
            #self.add_note_trace('Final domain char = ' + tmp_char)
            tmp_ret_2 = self.single_char(position + tmp_ret, self.HYPHEN)
            if tmp_ret_2:
                tmp_ret += tmp_ret_2
                tmp_ret('ERR_DOMAIN_HYPHEN_END', raise_on_error=False)

            tmp_ret_2 = self.single_char(position + tmp_ret, self.DOT)
            if tmp_ret_2:
                tmp_ret += tmp_ret_2
                tmp_ret('ERR_DOT_END', raise_on_error=False)

            tmp_ret_2 = self.single_char(position + tmp_ret, self.BACKSLASH)
            if tmp_ret_2:
                tmp_ret += tmp_ret_2
                tmp_ret('ERR_BACKSLASH_END', raise_on_error=False)

            if tmp_ret > 255:
                 add_to.append('RFC5322_DOMAIN_TOO_LONG')

        elif self.at_end(position + tmp_ret):
            add_to.append('ERR_EXPECTING_DTEXT')

        tmp_ret(*add_to, raise_on_error=False)

        return tmp_ret


    @as_football(diags='RFC5321_ADDRESS_LITERAL')
    def address_literal(self, position, lit_init=None):
        """
        address-literal  = "[" ( IPv4-address-literal /
                        IPv6-address-literal /
                        General-address-literal ) "]"

        [1012]   RFC5321_ADDRESS_LITERAL  Address is valid but at a literal address not a domain (ISEMAIL_RFC5321)
        ERR_UNCLOSED_DOM_LIT  Unclosed domain literal.

        ERR_INVALID_ADDR_LITERAL
        """

        tmp_ret = self._empty
        if lit_init is None:
            lit_init = self.open_sq_bracket(position)
            if not lit_init:
                return tmp_ret

        tmp_ipv4 = self.ipv4_address_literal(position + tmp_ret + lit_init)
        if tmp_ipv4:
            tmp_csb = self.close_sq_bracket(position + tmp_ret + lit_init + tmp_ipv4)
            if tmp_csb:
                return tmp_ret(lit_init, tmp_ipv4, tmp_csb)

        tmp_ipv6 = self.ipv6_address_literal(position + tmp_ret + lit_init)
        if tmp_ipv6:
            tmp_csb = self.close_sq_bracket(position + tmp_ret + lit_init + tmp_ipv6)
            if tmp_csb:
                return tmp_ret(lit_init, tmp_ipv6, tmp_csb)

        tmp_gen_lit = self.general_address_literal(position + tmp_ret + lit_init)
        if tmp_gen_lit:
            tmp_csb = self.close_sq_bracket(position + tmp_ret + lit_init + tmp_gen_lit)
            if tmp_csb:
                tmp_ret('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN')
                return tmp_ret(lit_init, tmp_gen_lit, tmp_csb)

        tmp_ret = self.football_max(tmp_ipv4, tmp_ipv6, tmp_gen_lit, names=['ipv4', 'ipv6', 'gen_lit'])

        if not tmp_ret:
            return tmp_ret

        tmp_ret_2 = self.close_sq_bracket(position + tmp_ret)

        if tmp_ret_2:
            return tmp_ret(tmp_ret_2)
        else:
            return tmp_ret('ERR_INVALID_ADDR_LITERAL', raise_on_error=False)


    @as_football(diags='RFC5322_GENERAL_LITERAL')
    def general_address_literal(self, position):
        """
        General-address-literal  = Standardized-tag ":" 1*dcontent

                RFC5322_GENERAL_LITERAL

        """
        tmp_ret = self._empty
        tmp_ret_2 = self.try_and(position,
                            self.standardized_tag,
                            self.colon,
                            self.dcontent)
        if tmp_ret_2:
            tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.GENERAL_LIT
            return tmp_ret(tmp_ret_2)
        else:
            return tmp_ret

    @as_football()
    def standardized_tag(self, position):
        """
            Standardized-tag  = Ldh-str
                             ; Standardized-tag MUST be specified in a
                             ; Standards-Track RFC and registered with IANA
        """
        if self.simple_str(position, 'IPv6:', False):
            return self._empty

        tmp_ret = self.ldh_str(position)
        tmp_str = self.mid(position, tmp_ret.l)

        if tmp_str in ISEMAIL_ALLOWED_GENERAL_ADDRESS_LITERAL_STANDARD_TAGS:
            return tmp_ret
        else:
            return self._empty

    @as_football()
    def ldh_str(self, position):
        """
            Ldh-str = *( ALPHA / DIGIT / "-" ) Let-dig
        """
        tmp_ret = self.sub_ldh_str(position)

        while self.this_char(position + tmp_ret - 1) == "-":
            tmp_ret -= 1
            if tmp_ret == 0:
                return tmp_ret
        return tmp_ret

    @as_football('RFC5322_IPV4_ADDR')
    def ipv4_address_literal(self, position):
        """
        IPv4-address-literal  = Snum 3("."  Snum)

        RFC5322_IPV4_ADDR

        """
        tmp_ret = self._empty
        tmp_ret += self.try_and(position,
                            self.snum,
                            self.single_dot, self.snum,
                            self.single_dot, self.snum,
                            self.single_dot, self.snum)

        if tmp_ret:
            tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.IPv4
        return tmp_ret

    @as_football()
    def snum(self, position):
        """
                Snum           = 1*3DIGIT
                              ; representing a decimal integer
                              ; value in the range 0 through 255
        """
        tmp_ret = self.three_digit(position)
        if tmp_ret:
            tmp_str = self.mid(position, tmp_ret.l)

            tmp_digit = int(tmp_str)
            if tmp_digit > 255:
                return self._empty

        return tmp_ret

    @as_football(diags='RFC5322_IPV6_ADDR')
    def ipv6_address_literal(self, position):
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
        tmp_ret = self._empty
        tmp_ret += self.ipv6(position)

        if tmp_ret:
            tmp_ret_2 = self.ipv6_addr(position + tmp_ret)

            if tmp_ret_2:
                tmp_ret += tmp_ret_2
                tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.IPv6
                return tmp_ret

        return self._empty

    @as_football()
    def ipv6_addr(self, position):
        """
                IPv6-addr      = IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp
        """
        tmp_ret = self._empty

        dot_count = self.count(position, self.DOT, stop_for=self.CLOSESQBRACKET)

        self.add_note_trace('Dot count = ' + str(dot_count))
        if dot_count:
            tmp_ret += self.ipv6v4_full(position) or self.ipv6v4_comp(position)
        else:
            tmp_ret += self.ipv6_full(position) or self.ipv6_comp(position)

        return tmp_ret

    @as_football()
    def ipv6_hex(self, position):
        """
        IPv6-hex       = 1*4HEXDIG
        """
        return self.hexdigit(position)

    @as_football(diags='RFC5322_IPV6_FULL_ADDR')
    def ipv6_full(self, position):
        """
                IPv6-full      = IPv6-hex 7(":" IPv6-hex)
                RFC5322_IPV6_FULL_ADDR

        """
        tmp_ret = self._empty
        tmp_count, tmp_ret_2 = self.ipv6_segment(position, max_count=8, min_count=8)
        if tmp_ret_2:
            return tmp_ret(tmp_ret_2)
        else:
            return self._empty

    @as_football(diags='RFC5322_IPV6_COMP_ADDR')
    def ipv6_comp(self, position):
        """
                IPv6-comp      = [IPv6-hex *5(":" IPv6-hex)] "::"
                              [IPv6-hex *5(":" IPv6-hex)]
                              ; The "::" represents at least 2 16-bit groups of
                              ; zeros.  No more than 6 groups in addition to the
                              ; "::" may be present.
              RFC5322_IPV6_COMP_ADDR

        """
        tmp_ret = self._empty
        tmp_pre_count, tmp_ret_2 = self.ipv6_segment(position, min_count=1, max_count=6)

        if not tmp_ret_2:
            return self._empty
        tmp_ret += tmp_ret_2

        tmp_ret_2 = self.double_colon(position + tmp_ret)

        if not tmp_ret_2:
            return self._empty

        tmp_ret += tmp_ret_2

        tmp_post_count, tmp_ret_2 = self.ipv6_segment(position + tmp_ret.l, min_count=1, max_count=6)

        if not tmp_ret_2:
            tmp_ret_2 = self.ipv6_hex(position + tmp_ret.l)
            if not tmp_ret_2:
                return self._empty
            tmp_post_count = 1

        tmp_ret += tmp_ret_2
        if (tmp_pre_count + tmp_post_count) > 6:
            self.add_note_trace('Segment count: %s + %s, exceeds 6, failing' % (tmp_pre_count, tmp_post_count) )
            return self._empty

        else:
            self.add_note_trace('Segment count: %s + %s, passing' % (tmp_pre_count, tmp_post_count) )
            return tmp_ret

    @as_football(diags='RFC5322_IPV6_IPV4_ADDR')
    def ipv6v4_full(self, position):
        """
                IPv6v4-full    = IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal

                        RFC5322_IPV6_IPV4_ADDR

        """
        tmp_ret = self._empty
        tmp_count, tmp_ret_2 = self.ipv6_segment(position, min_count=6, max_count=6)
        tmp_ret += tmp_ret_2

        if tmp_ret_2:
            tmp_ret_2 = self.colon(position + tmp_ret)
        else:
            return self._empty

        if tmp_ret_2:
            tmp_ret += tmp_ret_2
            tmp_ret_2 = self.ipv4_address_literal(position + tmp_ret.l)
        else:
            return self._empty

        if tmp_ret_2:
            tmp_ret += tmp_ret_2
        else:
            return self._empty

        tmp_ret.remove('RFC5322_IPV4_ADDR')
        return tmp_ret

    @as_football(diags='RFC5322_IPV6_IPV4_COMP_ADDR')
    def ipv6v4_comp(self, position):
        """
                IPv6v4-comp    = [IPv6-hex *3(":" IPv6-hex)] "::"
                              [IPv6-hex *3(":" IPv6-hex) ":"]
                              IPv4-address-literal
                              ; The "::" represents at least 2 16-bit groups of
                              ; zeros.  No more than 4 groups in addition to the
                              ; "::" and IPv4-address-literal may be present.
                RFC5322_IPV6_IPV4_COMP_ADDR


        """
        tmp_ret = self._empty
        tmp_pre_count, tmp_ret_2 = self.ipv6_segment(position, min_count=1, max_count=3)
        tmp_ret += tmp_ret_2

        if not tmp_ret:
            return self._empty

        tmp_ret_2 = self.double_colon(position + tmp_ret)

        if not tmp_ret_2:
            return self._empty

        tmp_ret += tmp_ret_2

        colon_count = self.count(position + tmp_ret, self.COLON, stop_for=self.CLOSESQBRACKET)
        if colon_count > 3:
            return self._empty

        tmp_post_count, tmp_ret_2 = self.ipv6_segment(position + tmp_ret.l, min_count=colon_count, max_count=colon_count)

        """
        if not tmp_ret_2 or tmp_post_count == 1:
            return self._empty

        self.add_note_trace('found end of ipv6 segments at segment: %s RESTARTING' % str(tmp_post_count))

        tmp_colon_count = self.count(position + tmp_ret.l + tmp_ret_2.l, search_for=':', length=10)
        self.add_note_trace('Checking for more colons, found %s more in %s' % (tmp_colon_count, self.mid(position + tmp_ret.l + tmp_ret_2.l, 10)))

        if tmp_colon_count == 1:
            tmp_post_count += 1

        tmp_post_count, tmp_ret_2 = self.ipv6_segment(position + tmp_ret.l, min_count=tmp_post_count-1, max_count=tmp_post_count-1)
        if not tmp_ret_2:
            return self._empty
        """
        self.add_note_trace('should be start of IPv4 segment')

        tmp_ret += tmp_ret_2
        tmp_ret_2 = self.colon(position + tmp_ret)

        if not tmp_ret_2:
            return self._empty

        tmp_ret += tmp_ret_2
        tmp_ret_2 = self.ipv4_address_literal(position + tmp_ret.l)

        if not tmp_ret_2:
            return self._empty

        tmp_ret += tmp_ret_2

        if tmp_pre_count + tmp_post_count > 4:
            self.add_note_trace('Segment count: %s + %s, exceeds 4, failing' % (tmp_pre_count, tmp_post_count))
            return self._empty

        else:
            self.add_note_trace('Segment count: %s + %s, passing' % (tmp_pre_count, tmp_post_count))
            tmp_ret.remove('RFC5322_IPV4_ADDR')
            return tmp_ret

    @as_football(skip=True)
    def cfws(self, position):
        """
        CFWS   =   (1*([FWS] comment) [FWS]) / FWS
            // http://tools.ietf.org/html/rfc5322#section-3.4.1
            //   Comments and folding white space
            //   SHOULD NOT be used around the "@" in the addr-spec.

        """

        tmp_ret = self._empty

        if not self.pre_cfws(position):
            return tmp_ret

        tmp_ret_fws = self.fws(position)
        tmp_ret_comment = self.comment(position + tmp_ret_fws)
        if tmp_ret_comment:
            tmp_ret += tmp_ret_fws
            tmp_ret += tmp_ret_comment
            tmp_ret += self.fws(position + tmp_ret)

            # tmp_find = self.count(position, self.AT, length=tmp_ret.l)
            # self.add_note_trace('pre (1) checking for AT count: %s in: %s' % (tmp_find, self.mid(position, tmp_ret.l)))

            # if tmp_ret:

                #self.at_in_cfws = self.AT in self.mid(position, tmp_ret.l)

                #if self.at_in_cfws and self.near_at_flag:
                #    tmp_ret('DEPREC_CFWS_NEAR_AT')

            # self.add_note_trace('post (1) checking at_in_cfws: %s' % self.at_in_cfws)

            # return tmp_ret

        # tmp_ret += self.fws(position)

        if 'CFWS_LAST' in tmp_ret.flags and self.AT in self.mid(position, tmp_ret.l):
            tmp_ret('DEPREC_CFWS_NEAR_AT')

        if tmp_ret:
            tmp_ret.flags += 'CFWS_LAST'

        # self.add_note_trace('post (2) checking at_in_cfws: %s' % self.at_in_cfws)

        return tmp_ret

    @as_football(segment=False)
    def sub_cfws(self, position):
        """
        sub_CFWS = (1*([FWS] comment) [FWS])
            // http://tools.ietf.org/html/rfc5322#section-3.4.1
            //   Comments and folding white space
            //   SHOULD NOT be used around the "@" in the addr-spec.

        """
        tmp_ret = self._empty
        tmp_ret += self.fws(position)
        tmp_ret += self.no_at(position + tmp_ret.l)
        tmp_ret += self.comment(position + tmp_ret.l)
        if tmp_ret:
            tmp_ret += self.no_at(position + tmp_ret.l)
            tmp_ret += self.fws(position + tmp_ret.l)
        return tmp_ret

    @as_football(comment=True, diags='CFWS_COMMENT')
    def comment(self, position):
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
        tmp_ret = self._empty
        tmp_ret += self.open_parenthesis(position)

        self.add_note_trace('Return from openparen = %s' % tmp_ret.l)

        if not tmp_ret:
            return self._empty

        last_was_fws = False
        has_close_quotes = False

        while True:
            action_name, tmp_loop_1 = self.try_or(position + tmp_ret.l,
                                                  self.ccontent,
                                                  self.fws,
                                                  self.close_parenthesis)

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
                if self.at_end(position + tmp_loop_1 + tmp_ret) or self.this_char(position + tmp_loop_1 + tmp_ret) == self.AT:
                    tmp_ret('ERR_UNCLOSED_COMMENT')
                tmp_ret('ERR_EXPECTING_CTEXT')
                break
            else:
                raise AttributeError('Invalid Action Name: %s' % action_name)

        if not has_close_quotes:
            return tmp_ret('ERR_UNCLOSED_COMMENT')

        return tmp_ret

    @as_football()
    def ccontent(self, position):
        """
        ccontent        =   ctext / quoted-pair / comment
    
        """
        tmp_ret = self._empty
        tmp_ret += self.ctext(position) or self.quoted_pair(position) or self.comment(position)
        return tmp_ret

    @as_football()
    def ctext(self, position):
        """
        ctext           =   %d33-39 /          ; Printable US-ASCII
                           %d42-91 /          ;  characters not including
                           %d93-126 /         ;  "(", ")", or "\"
                           obs-ctext
        [1139]       ERR_EXPECTING_CTEXT  A comment contains a character that is not allowed (ISEMAIL_ERR)

        """
        tmp_ret = self._empty
        return tmp_ret(self.sub_ctext(position) or self.obs_ctext(position))

    @as_football(diags='DEPREC_CTEXT')
    def obs_ctext(self, position):
        """
            obs-ctext       =   obs-NO-WS-CTL
        [1038]              DEPREC_CTEXT  A comment contains a deprecated character (ISEMAIL_DEPREC)
        """
        return self.simple_char(position, self.OBS_CTEXT)

    @as_football(diags='CFWS_FWS')
    def fws(self, position=None):
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

        tmp_ret = self.fws_sub(position)
        if not tmp_ret:
            tmp_ret = self.obs_fws(position)

        return tmp_ret

    @as_football()
    def fws_sub(self, position=None):
        """
        FWS             =   ([*WSP CRLF] 1*WSP)
        [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign (ISEMAIL_DEPREC)
        """
        tmp_ret = self._empty

        tmp_ret += self.wsp(position)

        if not tmp_ret:
            return self._empty

        else:
            tmp_ret_crlf = self.crlf(position + tmp_ret)

            if tmp_ret_crlf.error:
                return tmp_ret.add(tmp_ret_crlf).set(0)

            if not tmp_ret_crlf:
                return tmp_ret

            tmp_ret_2 = self.one_wsp(position + tmp_ret.l + tmp_ret_crlf.l)

            if tmp_ret_2:
                return tmp_ret(tmp_ret_crlf, tmp_ret_2)

            else:
                return self._empty

    @as_football(diags='DEPREC_FWS')
    def obs_fws(self, position):
        """
            obs-FWS         =   1*([CRLF] WSP)     ; As amended in erratum #1908

        [1034]                DEPREC_FWS  Address contains an obsolete form of Folding White Space (ISEMAIL_DEPREC)
        [1148]           ERR_FWS_CRLF_X2  Folding White Space contains consecutive CRLF sequences (ISEMAIL_ERR)
        [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign (ISEMAIL_DEPREC)

        """
        tmp_ret = self._empty
        tmp_ret += self.crlf(position)

        if tmp_ret.error:
            return tmp_ret

        if tmp_ret:
            if self.at_end(position + tmp_ret.l):
                return tmp_ret("ERR_FWS_CRLF_END")

        tmp_ret_2 = self.wsp(position + tmp_ret)
        if tmp_ret_2:

            # if not self.at_end(position + tmp_ret.l) and self.this_char(position + tmp_ret.l) in self.WSP:
            # tmp_ret += 1
            return tmp_ret(tmp_ret_2)
        else:

            return self._empty

    @as_football(diags='RFC5321_QUOTED_STRING')
    def quoted_string(self, position):
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
        tmp_ret = self._empty
        tmp_ret += self.cfws(position)
        self.near_at_flag = False

        tmp_ret.flags -= 'CFWS_LAST'

        tmp_init_dquote = self.double_quote(position + tmp_ret)

        if tmp_init_dquote:
            tmp_ret += tmp_init_dquote
        else:
            return self._empty

        tmp_closing_dquote = self.find(position + tmp_ret, self.DQUOTE, skip_quoted_str=True)
        if tmp_closing_dquote == -1:
            return tmp_ret('ERR_UNCLOSED_QUOTED_STR')

        last_was_fws = False
        has_qtext = False
        while True:

            tmp_loop_1 = self.fws(position + tmp_ret)

            if tmp_loop_1:
                tmp_loop_1.remove('CFWS_FWS')
                if last_was_fws:
                    tmp_ret += tmp_loop_1
                    return tmp_ret(("ERR_MULT_FWS_IN_QS", position + tmp_ret, tmp_ret))
                else:
                    last_was_fws = False

            tmp_loop_2 = self.qcontent(position + tmp_ret + tmp_loop_1)

            if tmp_loop_2:
                tmp_ret += tmp_loop_1
                tmp_ret += tmp_loop_2
                has_qtext = True
            else:
                break

        tmp_last_quote = self.double_quote(position + tmp_ret)

        if tmp_last_quote:
            tmp_ret += tmp_last_quote
            tmp_cfws = self.cfws(position + tmp_ret.l)
            tmp_ret += tmp_cfws
            return tmp_ret
        else:
            return tmp_ret('ERR_EXPECTING_QTEXT')

    @as_football()
    def qcontent(self, position):
        """
            qcontent  =   qtext / quoted-pair
        """
        tmp_ret = self._empty
        tmp_ret += self.qtext(position) or self.quoted_pair(position)
        return tmp_ret

    @as_football()
    def qtext(self, position):
        """
            qtext           =   %d33 /             ; Printable US-ASCII
                               %d35-91 /          ;  characters not including
                               %d93-126 /         ;  "\" or the quote character
                               obs-qtext
        """
        tmp_ret = self._empty
        tmp_ret += self.simple_char(position, self.QTEXT) or self.obs_qtext(position)
        return tmp_ret

    @as_football(diags='DEPREC_QTEXT')
    def obs_qtext(self, position):
        """
            obs-qtext       =   obs-NO-WS-CTL

        [1035]              DEPREC_QTEXT  A quoted string contains a deprecated character (ISEMAIL_DEPREC)

        """
        return self.simple_char(position, self.OBS_QTEXT)

    @as_football()
    def quoted_pair(self, position):
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

        tmp_ret = self._empty

        tmp_ret += self.back_slash(position)

        if tmp_ret and self.at_end(position+1):
            tmp_ret('ERR_EXPECTING_QPAIR')

        if tmp_ret:

            tmp_ret_1 = self.vchar_wsp(position + 1)

            if tmp_ret_1:
                return tmp_ret(tmp_ret_1)
            tmp_ret_1 = self.obs_qp(position + 1)

            if tmp_ret_1:
                return tmp_ret(tmp_ret_1)

            else:
                tmp_ret('ERR_EXPECTING_QPAIR')

        else:
            return self._empty

    @as_football()
    def vchar_wsp(self, position):
        '''
        quoted-pair_sub =  VCHAR / WSP

                    // At this point we know where this qpair occurred so
                    // we could check to see if the character actually
                    // needed to be quoted at all.
                    // http://tools.ietf.org/html/rfc5321#section-4.1.2
                    //   the sending system SHOULD transmit the
                    //   form that uses the minimum quoting possible.
                // To do: check whether the character needs to be quoted (escaped) in this context
                // The maximum sizes specified by RFC 5321 are octet counts, so we must include the backslash
        '''
        return self.simple_char(position, self.VCHAR_WSP, max_count=1)

    @as_football(diags='DEPREC_QP')
    def obs_qp(self, position):
        '''
            obs-qp = (%d0 / obs-NO-WS-CTL / LF / CR)

        [1036]                 DEPREC_QP  A quoted pair contains a deprecated character (ISEMAIL_DEPREC)

        '''
        return self.simple_char(position, self.OBS_QP, max_count=1)

    @as_football()
    def crlf(self, position, in_crlf=False):
        """
        [1150] ERR_CR_NO_LF  Address contains a carriage return that is not followed by a line feed (ISEMAIL_ERR)
        [1148] ERR_FWS_CRLF_X2  Folding White Space contains consecutive CRLF sequences (ISEMAIL_ERR)
        """
        tmp_ret = self._empty
        if self.at_end(position):
            return tmp_ret

        if self.this_char(position) == '\r':
            if not self.at_end(position+1) and self.this_char(position+1) == '\n':
                tmp_ret += 2

                if not in_crlf:
                    tmp_crlf_2 = self.crlf(position + tmp_ret.l, in_crlf=True)
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

    @as_football(segment=False, diags='DEPREC_CFWS_NEAR_AT')
    def no_at(self, position):
        return self.simple_char(position, self.AT, max_count=1)

    @as_football()
    def at(self, position):        
        return self.single_char(position, self.AT)

    @as_football()
    def atext(self, position):        
        return self.simple_char(position, self.ATEXT)

    @as_football()
    def single_dot(self, position):
        tmp_ret = self.single_char(position, self.DOT)
        if tmp_ret and not self.at_end(position+1) and self.this_char(position+1) == self.DOT:
            tmp_ret('ERR_CONSECUTIVE_DOTS')
        return tmp_ret

    @as_football()
    def alpha(self, position):        
        return self.simple_char(position, self.ALPHA)

    @as_football()
    def let_dig(self, position):
        return self.simple_char(position, self.LET_DIG)

    @as_football(segment=False)
    def sub_ldh_str(self, position):
        return self.simple_char(position, self.LDH_STR)

    @as_football()
    def open_sq_bracket(self, position):        
        return self.single_char(position, self.OPENSQBRACKET)

    @as_football()
    def close_sq_bracket(self, position):        
        return self.single_char(position, self.CLOSESQBRACKET)

    @as_football(segment=False)
    def obs_dtext_sub(self, position):
        return self.simple_char(position, self.OBS_DTEXT)

    @as_football()
    def colon(self, position):
        return self.single_char(position, self.COLON)

    @as_football()
    def double_colon(self, position):
        return self.simple_str(position, self.DOUBLECOLON)

    @as_football()
    def dcontent(self, position):
        return self.simple_char(position, self.DCONTENT)

    @as_football(segment=False)
    def pre_cfws(self, position):
        return self.simple_char(position, self.PRE_CFWS)

    @as_football()
    def ipv6(self, position):
        return self.simple_str(position, "IPv6:", caps_sensitive=False)

    @as_football()
    def three_digit(self, position):
        return self.simple_char(position, self.DIGIT, max_count=3)

    @as_football(segment=False)
    def hexdigit(self, position):
        return self.simple_char(position, self.HEXDIG, min_count=-1, max_count=4)

    @as_football()
    def open_parenthesis(self, position):
        return self.single_char(position, self.OPENPARENTHESIS)

    @as_football()
    def close_parenthesis(self, position):
        return self.single_char(position, self.CLOSEPARENTHESIS)

    @as_football(segment=False)
    def sub_ctext(self, position):
        return self.simple_char(position, self.CTEXT)

    @as_football()
    def wsp(self, position):
        return self.simple_char(position, self.WSP)

    @as_football()
    def one_wsp(self, position):
        return self.single_char(position, self.WSP)

    @as_football()
    def double_quote(self, position):
        return self.single_char(position, self.DQUOTE)

    @as_football()
    def back_slash(self, position):
        return self.single_char(position, self.BACKSLASH)

    @as_football()
    def hyphen(self, position):
        return self.single_char(position, self.HYPHEN)

    @as_football()
    def dot(self, position):
        return self.single_char(position, self.DOT)


    '''
    ---------------------------------------
    NOTES:
        $end_or_die	= false;			// CFWS can only appear at the end of the element

        local_part_open_parans
                        // Comments are OK at the beginning of an element
                        $end_or_die		= true;	// We can't start a comment in the middle of an element, so this better be the end

         local_part_string_quote
                        $end_or_die	= false;	// CFWS & quoted strings are OK again now we're at the beginning of an element (although they are obsolete forms)
        local_part FWS
                        $end_or_die = true;	// We can't start FWS in the middle of an element, so this better be the end

    '''
