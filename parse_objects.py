
from parse_results import ParseResultFootball,ParsingError
# from collections import deque
from functools import wraps

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




def as_football(func):
    @wraps(func)
    def func_wrapper(self, position, *args, **kwargs):
        raise_error = False
        error_raised = None
        if 'stage_name' in kwargs:
            self.stage.append(kwargs['stage_name'])
        else:
            self.stage.append(func.__name__)

        # position = self.pos(position)

        """
        if self.verbose == 3:
            self.trace_level += 1
            if self.trace_filter == -1 or self.trace_filter >= self.trace_level:
                self.trace.append(TraceObj(self, self.cur_stage, self.stage_str, position, True, trace_level=self.trace_level))
        """
        self.add_begin_trace(position)

        try:
            tmp_ret = func(self, position, *args, **kwargs)
        except ParsingError as err:
            raise_error = True
            error_raised = err
            tmp_ret = err.results

        # if isinstance(tmp_ret, int):
        #      tmp_ret = ParseResultFootball(tmp_ret, stage=self.stage_str)

        tmp_ret.stage = self.stage_str

        self.add_end_trace(position, tmp_ret, raise_error=raise_error)
        """
        if self.verbose == 3:
            if self.trace_filter == -1 or self.trace_filter >= self.trace_level:
                self.trace.append(TraceObj(self, self.cur_stage, self.stage_str, position, False, results=tmp_ret, trace_level=self.trace_level))
            self.trace_level -= 1
        """
        self.stage.pop()

        if raise_error:
            raise error_raised

        return tmp_ret

    return func_wrapper

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
                tmp_str = '%send      %s : %s  -- %s ' % (tmp_indent, tmp_raised, self.stage_name, self.results)
            else:
                tmp_str = '%send       (%r) %s : %s  -- %s ' % (tmp_indent,
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
    ALPHA = make_char_str((65, 90), (97, 122))

    LTR_STR = make_char_str((65, 90), (97, 122), (48, 57))
    LET_DIG = make_char_str(ALPHA, DIGIT)
    LDH_STR = make_char_str(LET_DIG, '-')
    VCHAR = make_char_str((31, 126))
    ATEXT = make_char_str(ALPHA, DIGIT, "!#$%&'+-/=?^_`{|}~")
    DCONTENT = make_char_str((33, 90), (94, 126))


    OBS_NO_WS_CTL = make_char_str((1, 8), (11, 12), (14, 31), 127)

    OBS_QP = make_char_str(0, OBS_NO_WS_CTL, LF, CR)

    QTEXT = make_char_str(33, (35, 91), (93, 126))
    OBS_QTEXT = make_char_str(OBS_NO_WS_CTL, QTEXT)

    CTEXT = make_char_str((33, 39), (42, 91), (93, 126))
    OBS_CTEXT = make_char_str(OBS_NO_WS_CTL, CTEXT)


    WSP = make_char_str(SP, HTAB)

    VCHAR_WSP = make_char_str(VCHAR, WSP)

    # test_text = ''

    def __init__(self, email_in=None, verbose=0, error_on_warning=False,
                 error_on_category=None, error_on_diag=None, trace_filter=-1):
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

        self.email_in = ''
        self.result = None
        self.position = -1
        self.email_len = 0
        # self.parsed = []
        # self.remaining = deque()
        self.email_list = []
        self.cleaned = []
        self.verbose = verbose
        self.error_on_warning = error_on_warning
        self.error_on_category = error_on_category
        self.error_on_diag = error_on_diag
        if email_in is not None:
            self.setup(email_in)

        self.stage = []
        self.trace = []
        self.trace_level = 0
        self.trace_filter = trace_filter

        self.in_crlf = False

    def __repr__(self):
        return 'Parse: "%s", at stage %s' % (self.email_in, self.stage)

    def mid(self, begin: int = 0, length: int = 0):
        if length > 0:
            tmp_end = min(begin + length, self.email_len)
        else:
            tmp_end = self.email_len
        tmp_str = ''.join(self.email_list[begin:tmp_end])
        return tmp_str

    def setup(self, email_in):
        # self.result = ParseEmailResult(email_in)
        self.email_len = len(email_in)
        self.email_in = email_in
        self.position = 0
        self.email_list.clear()
        self.email_list.extend(email_in)

    """
    def set_response(self, response_code, position, length):
        response_dict = ISEMAIL_DIAG_RESPONSES()
    """

    def remaining(self, position):
        position = self.pos(position)
        for i in range(position, self.email_len):
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

    def add_begin_trace(self, position):
        self.trace_level += 1
        self._add_trace(position, is_begin=True)

    def add_end_trace(self, position, results, raise_error=False):
        self._add_trace(position, results=results, raise_error=raise_error)
        self.trace_level -= 1

    def add_note_trace(self, note, position=0):
        self.trace_level += 1
        self._add_trace(position, is_note=True, note_str=note)
        self.trace_level -= 1

    def _add_trace(self, position, is_note=False, note_str=None, results=None, is_begin=False, raise_error=False):
        if results is not None:
            results = results.copy()
        if self.verbose == 3:
            if self.trace_filter == -1 or self.trace_filter >= self.trace_level:
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

    def run_method_test(self, method, *args, **kwargs):
        try:
            tmp_ret = method(*args, **kwargs)
            tmp_ret.finish()
            return tmp_ret
        except ParsingError as err:
            tmp_ret = err.results
            tmp_ret.finish()
            return tmp_ret

    def this_char(self, position):
        position = self.pos(position)
        return self.email_list[position]

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

    def find(self, position, search_for, stop_at=None):
        position = self.pos(position)
        tmp_ret = 0
        for c in self.remaining(position):
            tmp_ret += 1
            if c in search_for:
                return tmp_ret
            if c in stop_at:
                return -1
        return -1

    """
    def parse(self, parse_for, position=None, prefix=None, postfix=None, add=0, **kwargs):
        tmp_pre = 0
        tmp_base = 0
        tmp_post = 0
        tmp_ret = 0
        position = self.pos(position)

        if prefix is not None:
            if not issubclass(prefix.__class__, P4):
                prefix = P4Char(prefix, **kwargs)
                prefix.optional = False

            tmp_pre = self._parse_str(prefix, position)
            if not prefix.optional and tmp_pre == 0:
                return 0

            if prefix.include_str:
                tmp_ret += tmp_pre

        if not issubclass(parse_for.__class__, P4):
            parse_for = P4(parse_for, **kwargs)

        tmp_base = self._parse_str(parse_for, position+tmp_pre)
        if not parse_for.optional and tmp_base == 0:
            return 0

        if parse_for.include_str:
            tmp_ret += tmp_base

        if postfix is not None:
            if not issubclass(postfix.__class__, P4):
                postfix = P4Char(postfix, **kwargs)
                postfix.optional = False

            tmp_post = self._parse_str(postfix, position+tmp_pre+tmp_base)
            if not postfix.optional and tmp_post == 0:
                return 0

            if postfix.include_str:
                tmp_ret += tmp_post

        return tmp_ret + add

    def _parse_str(self, p4, position):
        if p4.ordered:
            return self.ordered_str(p4.parse_for, position, p4.min_count, p4.max_count)
        else:
            return self.simple_str(p4.parse_for, position, p4.min_count, p4.max_count)
    """
    @as_football
    def simple_str(self,
                   position: int,
                   parse_for: str,
                   min_count: int = -1,
                   max_count: int = 99999,
                   stage_name: str = None) -> ParseResultFootball:
        tmp_ret = ParseResultFootball(self)
        for i in self.remaining(position):
            if i in parse_for:
                tmp_ret += 1
                if tmp_ret == max_count:
                    return tmp_ret
            else:
                if tmp_ret >= min_count:
                    return tmp_ret
                else:
                    return tmp_ret(set=0)
        if tmp_ret >= min_count:
            return tmp_ret
        return tmp_ret(set=0)

    def _try_action(self, position, action_dict):
        if isinstance(action_dict, dict):
            if 'string_in' in action_dict:
                parse_for = action_dict.pop('string_in')
                return self.simple_str(position, parse_for=parse_for, **action_dict)

            else:
                tmp_func = action_dict.pop('function')
                return tmp_func(position, **action_dict)
        elif isinstance(action_dict, str):
            return self.simple_str(position, parse_for=action_dict, stage_name=repr(action_dict))

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

    def try_and(self, position, *args):
        """

        """
        position = self.pos(position)
        tmp_ret = ParseResultFootball(self)
        for act in args:
            if isinstance(act, dict):
                tmp_name = act.pop('name', '')
            elif isinstance(act, str):
                tmp_name = act
            else:
                tmp_name = act.__name__

            tmp_ret_1 = self._try_action(position, act)
            if tmp_ret.error:
                return tmp_ret.add(tmp_ret_1)
            elif not tmp_ret:
                return ParseResultFootball(self)
            tmp_ret += tmp_ret_1

        return tmp_ret


    """
    def ordered_str(self, parse_for, position=None, min_count=1, max_count=1):
        if min_count > max_count:
            raise AttributeError('Min (%s) cannot be larger than max (%s) !' % (min_count, max_count))
        position = self.pos(position)
        tmp_ret = 0
        tmp_ret_char = 0
        tmp_ret_count = 0
        check_len = len(parse_for)

        for c in self.remaining(position):
            if tmp_ret_count == max_count:
                return tmp_ret
            if c != parse_for[tmp_ret_char]:
                if tmp_ret_count < min_count:
                    return 0
                else:
                    return tmp_ret
            tmp_ret_char += 1
            if tmp_ret_char > (check_len - 1):
                tmp_ret_char = 0
                tmp_ret_count += 1
                tmp_ret += check_len

        if tmp_ret_count < min_count:
            return 0
        else:
            return tmp_ret
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
    """

    # TODO: THIS
    @as_football
    def address_spec(self):

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

    # TODO: THIS
    @as_football
    def local_part(self):
        """        
        local-part      =   dot-atom / quoted-string / obs-local-part
            // http://tools.ietf.org/html/rfc5321#section-4.5.3.1.1
            //   The maximum total length of a user name or other local-part is 64
            //   octets.


        [1033]         DEPREC_LOCAL_PART  The local part is in a deprecated form (ISEMAIL_DEPREC)
        [1067]    RFC5322_LOCAL_TOO_LONG  The local part of the address is too long (ISEMAIL_RFC5322)

        """


    # TODO: THIS
    @as_football
    def dot_atom(self):
        """
        dot-atom        =   [CFWS] dot-atom-text [CFWS]
        [1137]       ERR_EXPECTING_ATEXT  Address contains a character that is not allowed (ISEMAIL_ERR)
        """

    @as_football
    def dot_atom_text(self, position):
        """
            dot-atom-text   =   1*atext *("." 1*atext)
        """
        """
        # position = self.pos(position)
        tmp_ret = ParseResultFootball(self)
        tmp_ret += self.simple_str(self.ATEXT, position)

        if self.at_end(position + tmp_ret):
            return tmp_ret

        if tmp_ret:
            while True:
                tmp_sub = ParseResultFootball(self)
                if self.this_char(position + tmp_ret) == ".":
                    tmp_sub += 1
                    tmp_sub += self.simple_str(self.ATEXT, position + tmp_ret.l + 1)
                    if tmp_sub > 1:
                        tmp_ret += tmp_sub
                    else:
                        return tmp_ret
                else:
                    return tmp_ret
                if self.at_end(position + tmp_ret):
                    return tmp_ret
        return tmp_ret
        """

    """
    def dot_atom_text_sub(self, position):
        position = self.pos(position)
        tmp_ret = 0
        if self.this_char(position) == ".":
            tmp_ret += 1
            tmp_ret += self.simple_str(self.ATEXT, position+tmp_ret)
            if tmp_ret > 1:
                return tmp_ret
        return 0
    """

    # TODO: THIS
    @as_football
    def obs_local_part(self):
        """
            obs-local-part = word *("." word)
                    [1037]            DEPREC_COMMENT  Address contains a comment in a position that is deprecated (ISEMAIL_DEPREC)

        """

    # TODO: THIS
    @as_football
    def word(self):
        """
            word = atom / quoted-string
        """


    # TODO: THIS
    @as_football
    def atom(self):
        """
                atom = [CFWS] 1*atext [CFWS]

                // The entire local-part can be a quoted string for RFC 5321
                // If it's just one atom that is quoted then it's an RFC 5322 obsolete form
        """

    # TODO: THIS
    @as_football
    def domain(self):

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
    
         [1005]      DNSWARN_NO_MX_RECORD  Couldn't find an MX record for this domain but an A-record does exist (ISEMAIL_DNSWARN)
        [1006]         DNSWARN_NO_RECORD  Couldn't find an MX record or an A-record for this domain (ISEMAIL_DNSWARN)
        [1065]            RFC5322_DOMAIN  Address is RFC 5322 compliant but contains domain characters that are not allowed by DNS (ISEMAIL_RFC5322)
        [1068]   RFC5322_DOMAIN_TOO_LONG  The domain part is too long (ISEMAIL_RFC5322)
        [1069]    RFC5322_LABEL_TOO_LONG  The domain part contains an element that is too long (ISEMAIL_RFC5322)
        [1143]   ERR_DOMAIN_HYPHEN_START  A domain or subdomain cannot begin with a hyphen (ISEMAIL_ERR)
        [1144]     ERR_DOMAIN_HYPHEN_END  A domain or subdomain cannot end with a hyphen (ISEMAIL_ERR)

        """

    # TODO: THIS
    @as_football
    def domain_addr(self):
        """
        domain-addr = sub-domain *("." sub-domain)
        [1009]               RFC5321_TLD  Address is valid but at a Top Level Domain (ISEMAIL_RFC5321)
        [1010]       RFC5321_TLD_NUMERIC  Address is valid but the Top Level Domain begins with a number (ISEMAIL_RFC5321)

        """

    # TODO: THIS
    @as_football
    def sub_domain(self):
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


    # TODO: THIS
    @as_football
    def let_str(self):
        """
                Ldh-str        = *( ALPHA / DIGIT / "-" ) Let-dig
        """



    # TODO: THIS
    @as_football
    def domain_literal(self):
        """
        domain-literal  =   [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
        // Domain literal must be the only component

        [1070]    RFC5322_DOMAIN_LITERAL  The domain literal is not a valid RFC 5321 address literal (ISEMAIL_RFC5322)
        [1129]       ERR_EXPECTING_DTEXT  A domain literal contains a character that is not allowed (ISEMAIL_ERR)
        [1135]    ERR_ATEXT_AFTER_DOMLIT  Extra characters were found after the end of the domain literal (ISEMAIL_ERR)
        [1147]      ERR_UNCLOSED_DOM_LIT  Domain literal is missing its closing bracket (ISEMAIL_ERR)


        """

    # TODO: THIS
    @as_football
    def dtext(self):

        """
            dtext           =   %d33-90 /          ; Printable US-ASCII
                               %d94-126 /         ;  characters not including
                               obs-dtext          ;  "[", "]", or "\"
        """

    # TODO: THIS
    @as_football
    def obs_dtext(self):

        """
                obs-dtext       =   obs-NO-WS-CTL / quoted-pair
        [1071] RFC5322_DOM_LIT_OBS_DTEXT  The domain literal is not a valid RFC 5321 address literal and it contains obsolete characters (ISEMAIL_RFC5322)

        """

    # TODO: THIS
    @as_football
    def obs_domain(self):
        """
        obs-domain      =   atom *("." atom)
                [1037]            DEPREC_COMMENT  Address contains a comment in a position that is deprecated (ISEMAIL_DEPREC)

        """

    # TODO: THIS
    @as_football
    def address_literal(self):
        """
        address-literal  = "[" ( IPv4-address-literal /
                        IPv6-address-literal /
                        General-address-literal ) "]"

        [1012]   RFC5321_ADDRESS_LITERAL  Address is valid but at a literal address not a domain (ISEMAIL_RFC5321)

        """

    # TODO: THIS
    @as_football
    def general_address_literal(self):
        """
            General-address-literal  = Standardized-tag ":" 1*dcontent
        """

    # TODO: THIS
    @as_football
    def standardized_tag(self):
        """
                Standardized-tag  = Ldh-str
                                 ; Standardized-tag MUST be specified in a
                                 ; Standards-Track RFC and registered with IANA
        """

    @as_football
    def ldh_str(self, position=None):
        """
            Ldh-str = *( ALPHA / DIGIT / "-" ) Let-dig
        """
        """
        tmp_ret = self.simple_str(self.LDH_STR, position)
        while self.this_char(position+tmp_ret-1) == "-":
            tmp_ret -= 1
            if tmp_ret == 0:
                return tmp_ret
        return tmp_ret
        """

    # TODO: THIS
    @as_football
    def ipv4_address_literal(self):
        """
            IPv4-address-literal  = Snum 3("."  Snum)
        """

    @as_football
    def snum(self, position=None):
        """
                Snum           = 1*3DIGIT
                              ; representing a decimal integer
                              ; value in the range 0 through 255
        """
        """
        tmp_ret = self.simple_str(self.DIGIT, position=position, max_count=3)
        tmp_num_len = tmp_ret
        if tmp_ret == 3:
            if self.this_char(position) not in "012":
                return 0
            elif self.this_char(position) == "2":
                if self.this_char(position+1) in '012345' and self.this_char(position+1) in '012345':
                    return 3
                else:
                    return 0

        return tmp_ret
        """
    # TODO: THIS
    @as_football
    def ipv6_address_literal(self):

        """
            IPv6-address-literal  = "IPv6:" IPv6-addr
        [1013]   RFC5321_IPV6_DEPRECATED  Address is valid but contains a :: that only elides one zero group. All implementations must accept and be able to handle any legitimate RFC 4291 format. (ISEMAIL_DEPREC)
        [1072]    RFC5322_IPV6_GRP_COUNT  The IPv6 literal address contains the wrong number of groups (ISEMAIL_RFC5322)
        [1073]   RFC5322_IPV6_2X2X_COLON  The IPv6 literal address contains too many :: sequences (ISEMAIL_RFC5322)
        [1074]     RFC5322_IPV6_BAD_CHAR  The IPv6 address contains an illegal group of characters (ISEMAIL_RFC5322)
        [1075]     RFC5322_IPV6_MAX_GRPS  The IPv6 address has too many groups (ISEMAIL_RFC5322)
        [1076]   RFC5322_IPV6_COLON_STRT  IPv6 address starts with a single colon (ISEMAIL_RFC5322)
        [1077]    RFC5322_IPV6_COLON_END  IPv6 address ends with a single colon (ISEMAIL_RFC5322)

        """

    # TODO: THIS
    @as_football
    def ipv6_addr(self):

        """
                IPv6-addr      = IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp
        """

    # TODO: THIS
    @as_football
    def ipv6_hex(self):

        """
                IPv6-hex       = 1*4HEXDIG
        """
    # TODO: THIS
    @as_football
    def ipv6_full(self):
        """
                IPv6-full      = IPv6-hex 7(":" IPv6-hex)
        """
    # TODO: THIS
    @as_football
    def ipv6_comp(self):
        """
                IPv6-comp      = [IPv6-hex *5(":" IPv6-hex)] "::"
                              [IPv6-hex *5(":" IPv6-hex)]
                              ; The "::" represents at least 2 16-bit groups of
                              ; zeros.  No more than 6 groups in addition to the
                              ; "::" may be present.
        """

    # TODO: THIS
    @as_football
    def ipv6v4_full(self):
        """
                IPv6v4-full    = IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal
        """

    # TODO: THIS
    @as_football
    def ipv6v4_comp(self):
        """
                IPv6v4-comp    = [IPv6-hex *3(":" IPv6-hex)] "::"
                              [IPv6-hex *3(":" IPv6-hex) ":"]
                              IPv4-address-literal
                              ; The "::" represents at least 2 16-bit groups of
                              ; zeros.  No more than 4 groups in addition to the
                              ; "::" and IPv4-address-literal may be present.
        """


    @as_football
    def cfws(self, position):
        """
        CFWS            =   (1*([FWS] comment) [FWS]) / FWS
            // http://tools.ietf.org/html/rfc5322#section-3.4.1
            //   Comments and folding white space
            //   SHOULD NOT be used around the "@" in the addr-spec.

        """

        """
        tmp_ret = self.fws(position)
        tmp_ret += self.comment(position+tmp_ret.l)
        tmp_ret += self.fws(position + tmp_ret.l)

        if tmp_ret or tmp_ret.error:
            return tmp_ret

        return self.fws(position)
        """

        return self.try_and(position, self.fws, self.comment, self.fws)

    @as_football
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

        tmp_ret = self.simple_str(position, self.OPENPARENTHESIS, min_count=1, max_count=1, stage_name='OpenParen')

        self.add_note_trace('Return from openparen = %s' % tmp_ret.l)

        if not tmp_ret:
            return tmp_ret(set=0)

        last_was_fws = False

        # action_at = dict(name='at', string_in=self.AT, stage_name='AT', min_count=1, max_count=1)
        # action_fws = dict(name='fws', function=self.fws)
        # action_ccontent = dict(name='ccontent', function=self.ccontent)

        while True:
            action_name, tmp_loop_1 = self.try_or(position + tmp_ret.l, self.AT, self.ccontent, self.fws)

            if action_name == '':
                break

            elif action_name == self.AT:
                return tmp_ret(diag='DEPREC_CFWS_NEAR_AT', begin=position + tmp_ret.l + 1, length=tmp_ret.l)(set=0)

            elif action_name == 'fws':
                if last_was_fws:
                    tmp_ret += tmp_loop_1
                    return tmp_ret(begin=position + tmp_ret.l,
                                   diag="ERR_MULT_FWS_IN_COMMENT",
                                   length=tmp_ret.l)
                else:
                    last_was_fws = True

            elif action_name == 'ccontent':
                last_was_fws = False

            else:
                raise AttributeError('Invalid Action Name: %s' % action_name)

            tmp_ret += tmp_loop_1

        tmp_last_quote = self.simple_str(position+tmp_ret.l, self.CLOSEPARENTHESIS,
                                         min_count=1, max_count=1, stage_name='CloseParen')

        if tmp_last_quote:
            return tmp_ret(tmp_last_quote)(diag='CFWS_COMMENT', begin=position, length=tmp_ret.l)
        else:
            return tmp_ret(diag='ERR_UNCLOSED_COMMENT', begin=position, length=tmp_ret.l)

    @as_football
    def ccontent(self, position):
        """
        ccontent        =   ctext / quoted-pair / comment
    
        """
        return self.ctext(position) or self.quoted_pair(position) or self.comment(position)

    @as_football
    def ctext(self, position):
        """
        ctext           =   %d33-39 /          ; Printable US-ASCII
                           %d42-91 /          ;  characters not including
                           %d93-126 /         ;  "(", ")", or "\"
                           obs-ctext
        [1139]       ERR_EXPECTING_CTEXT  A comment contains a character that is not allowed (ISEMAIL_ERR)

        """

        tmp_ret = self.simple_str(position, self.CTEXT, stage_name='CTEXT')

        if tmp_ret:
            return tmp_ret
        else:
            return self.obs_ctext(position)

    @as_football
    def obs_ctext(self, position):
        """
            obs-ctext       =   obs-NO-WS-CTL
        [1038]              DEPREC_CTEXT  A comment contains a deprecated character (ISEMAIL_DEPREC)
        """

        tmp_ret = self.simple_str(position, self.OBS_CTEXT, stage_name='OBS_CTEXT')

        if tmp_ret:
            return tmp_ret(diag='DEPREC_CTEXT', begin=position, length=tmp_ret.l)
        return tmp_ret(set=0)

    @as_football
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

        if tmp_ret:
            tmp_ret(diag='CFWS_FWS', begin=position, length=tmp_ret.l)
        return tmp_ret

    # TODO: add error checking for @ in FWS
    @as_football
    def fws_sub(self, position=None):
        """
        FWS             =   ([*WSP CRLF] 1*WSP)
        [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign (ISEMAIL_DEPREC)
        """
        tmp_ret = ParseResultFootball(self)

        tmp_ret += self.simple_str(position, self.WSP, stage_name='WSP')

        if not tmp_ret:
            return ParseResultFootball(self)

        else:
            tmp_ret_crlf = self.crlf(position + tmp_ret.l)

            if tmp_ret_crlf.error:
                return tmp_ret.add(tmp_ret_crlf).set(0)

            if not tmp_ret_crlf:
                return tmp_ret

            tmp_ret_2 = self.simple_str(position+tmp_ret.l+tmp_ret_crlf.l, self.WSP, max_count=1, stage_name='WSP')

            if tmp_ret_2:
                return tmp_ret(tmp_ret_2).add(tmp_ret_crlf)

            else:
                return ParseResultFootball(self)

    @as_football
    def obs_fws(self, position):
        """
            obs-FWS         =   1*([CRLF] WSP)     ; As amended in erratum #1908

        [1034]                DEPREC_FWS  Address contains an obsolete form of Folding White Space (ISEMAIL_DEPREC)
        [1148]           ERR_FWS_CRLF_X2  Folding White Space contains consecutive CRLF sequences (ISEMAIL_ERR)
        [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign (ISEMAIL_DEPREC)

        """
        tmp_ret = self.crlf(position)

        if tmp_ret.error:
            return tmp_ret

        if tmp_ret:
            if self.at_end(position + tmp_ret.l):
                return tmp_ret(diag="ERR_FWS_CRLF_END", begin=position + tmp_ret.l, length=tmp_ret.l)


        if not self.at_end(position + tmp_ret.l) and self.this_char(position + tmp_ret.l) in self.WSP:
            tmp_ret += 1
            return tmp_ret(diag='DEPREC_FWS', begin=position, length=tmp_ret.l)
        else:

            return ParseResultFootball(self)

    # TODO: THIS
    @as_football
    def obs_no_ws_ctl(self):
        """
        obs-NO-WS-CTL   =   %d1-8 /            ; US-ASCII control
                           %d11 /             ;  characters that do not
                           %d12 /             ;  include the carriage
                           %d14-31 /          ;  return, line feed, and
                           %d127              ;  white space characters
        """

    # TODO: THIS
    @as_football
    def specials(self):
        '''    
        specials        =   "(" / ")" /        ; Special characters that do
                           "&lt;" / "&gt;" /        ;  not appear in atext
                           "[" / "]" /
                           ":" / ";" /
                           "@" / "\" /
                           "," / "." /
                           DQUOTE
        
        '''

    @as_football
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
        tmp_ret = self.cfws(position)
        tmp_ret += self.simple_str(position+tmp_ret.l, self.DQUOTE, min_count=1, max_count=1, stage_name='DQUOTE')

        if not tmp_ret:
            return ParseResultFootball(self)


        last_was_fws = False
        while True:

            # tmp_loop_1 = ParseResultFootball(self)
            tmp_loop_1 = self.fws(position + tmp_ret.l)

            if tmp_loop_1:
                if last_was_fws:
                    tmp_ret += tmp_loop_1
                    return tmp_ret(begin=position + tmp_ret.l,
                                   diag="ERR_MULT_FWS_IN_QS",
                                   length=tmp_ret.l)
                else:
                    last_was_fws = False

            tmp_loop_1 += self.qcontent(position + tmp_ret.l + tmp_loop_1.l)

            if tmp_loop_1:
                tmp_ret += tmp_loop_1
            else:
                break

        tmp_last_quote = self.simple_str(position+tmp_ret.l, self.DQUOTE,
                                         min_count=1, max_count=1, stage_name='DQUOTE')

        if tmp_last_quote:
            return tmp_ret(tmp_last_quote)(diag='RFC5321_QUOTED_STRING', begin=position, length=tmp_ret.l)
        else:
            return tmp_ret(diag='ERR_UNCLOSED_QUOTED_STR', begin=position, length=tmp_ret.l)

    @as_football
    def qcontent(self, position):
        """
            qcontent  =   qtext / quoted-pair
        """
        return self.qtext(position) or self.quoted_pair(position)

    @as_football
    def qtext(self, position):
        """
            qtext           =   %d33 /             ; Printable US-ASCII
                               %d35-91 /          ;  characters not including
                               %d93-126 /         ;  "\" or the quote character
                               obs-qtext
        """

        tmp_ret = self.simple_str(position, self.QTEXT, stage_name='QTEXT')

        if tmp_ret:
            return tmp_ret
        else:
            return self.obs_qtext(position)

    @as_football
    def obs_qtext(self, position):
        """
            obs-qtext       =   obs-NO-WS-CTL

        [1035]              DEPREC_QTEXT  A quoted string contains a deprecated character (ISEMAIL_DEPREC)

        """

        tmp_ret = self.simple_str(position, self.OBS_QTEXT, stage_name='OBS_QTEXT')

        if tmp_ret:
            return tmp_ret(diag='DEPREC_QTEXT', begin=position, length=tmp_ret.l)
        return ParseResultFootball(self)

    @as_football
    def quoted_pair(self, position: int) -> ParseResultFootball:
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

        tmp_ret = self.simple_str(position, self.BACKSLASH, min_count=1, max_count=1, stage_name='BACKSLASH')

        if tmp_ret and self.at_end(position+1):
            tmp_ret(diag='ERR_EXPECTING_QPAIR', length=1, begin=position)

        if tmp_ret:

            tmp_ret_1 = self.quoted_pair_sub(position + 1)

            if tmp_ret_1:
                return tmp_ret_1.add(1)
            tmp_ret_1 = self.obs_qp(position + 1)

            if tmp_ret_1:
                return tmp_ret_1.add(1)

            else:
                tmp_ret(diag='ERR_EXPECTING_QPAIR', length=1, begin=position)

        else:
            return ParseResultFootball(self)

    @as_football
    def quoted_pair_sub(self, position: int) -> ParseResultFootball:
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

        return self.simple_str(position, self.VCHAR_WSP, max_count=1, stage_name="VCHAR/WSP")

    @as_football
    def obs_qp(self, position: int) -> ParseResultFootball:
        '''
            obs-qp = (%d0 / obs-NO-WS-CTL / LF / CR)

        [1036]                 DEPREC_QP  A quoted pair contains a deprecated character (ISEMAIL_DEPREC)

        '''
        tmp_ret = self.simple_str(position, self.OBS_QP, max_count=1, stage_name="OBS_QP")
        if tmp_ret:
            return tmp_ret(diag="DEPREC_QP", begin=position, length=tmp_ret.l)
        else:
            return ParseResultFootball(self)

    @as_football
    def crlf(self, position, in_crlf=False):
        """
        [1150] ERR_CR_NO_LF  Address contains a carriage return that is not followed by a line feed (ISEMAIL_ERR)
        [1148] ERR_FWS_CRLF_X2  Folding White Space contains consecutive CRLF sequences (ISEMAIL_ERR)
        """
        tmp_ret = ParseResultFootball(self)
        if self.at_end(position):
            return tmp_ret

        if self.this_char(position) == '\r':
            if not self.at_end(position+1) and self.this_char(position+1) == '\n':
                tmp_ret += 2

                if not in_crlf:
                    tmp_crlf_2 = self.crlf(position + tmp_ret.l, in_crlf=True)
                    if tmp_crlf_2.error:
                        tmp_ret += tmp_crlf_2
                        tmp_ret(diag='ERR_FWS_CRLF_X2', begin=position, length=4)
                        return tmp_ret
                    elif tmp_crlf_2:
                        tmp_ret += 2
                        tmp_ret(diag='ERR_FWS_CRLF_X2', begin=position, length=4)
                        return tmp_ret
            else:
                return tmp_ret(diag='ERR_CR_NO_LF', begin=position, length=2)
        return tmp_ret


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
