from functools import wraps
from helpers.exceptions import ParsingError
from helpers.meta_data import ISEMAIL_DOMAIN_TYPE, ISEMAIL_ALLOWED_GENERAL_ADDRESS_LITERAL_STANDARD_TAGS
from helpers.general.general import make_char_str
from helpers.footballs import ParseResultFootball

"""
Address Specifications (summary):
    address-spec = local-part "@" domain
        local-part = dot-atom / quoted-string / obs-local-part
            dot-atom = [CFWS] dot-atom-text [CFWS]
                dot-atom-text = 1*atext *("." 1*atext)

            quoted-string = [CFWS] DQUOTE *([FWS] qcontent) [FWS] DQUOTE [CFWS]

            obs-local-part = word *("." word)
                word = atom / quoted-string
                    quoted-string = [CFWS] DQUOTE *([FWS] qcontent) [FWS] DQUOTE [CFWS]
                    atom = [CFWS] 1*atext [CFWS]


        domain = domain-addr / address-literal / dot-atom / domain-literal / obs-domain

            domain-addr = sub-domain *("." sub-domain)
                sub-domain = Let-dig [Ldh-str]

            address-literal = "[" ( IPv4-address-literal / IPv6-address-literal / General-address-literal ) "]"

            dot-atom = [CFWS] dot-atom-text [CFWS]
                dot-atom-text = 1*atext *("." 1*atext)
                    atext = <atext>

            domain-literal = [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]

            obs-domain = atom *("." atom)
                atom = [CFWS] 1*atext [CFWS]

"""

# **********************************************************************************
# <editor-fold desc="  STRING CONSTANTS  ">
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
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  WRAPPERS  ">
# **********************************************************************************


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

                    tmp_char = email_info.this_char(position)
                    if tmp_char == HYPHEN:
                        return tmp_ret('ERR_DOMAIN_HYPHEN_START')
                    elif tmp_char == DOT:
                        return tmp_ret('ERR_DOT_START')

                    if not email_info.at_end(position + tmp_ret):
                        tmp_ret(extra_text_err)
                    else:
                        if tmp_ret > 255:
                            tmp_ret('RFC5322_DOMAIN_TOO_LONG')

                        last_char = email_info.this_char(-1)

                        if last_char == HYPHEN:
                            tmp_ret('ERR_DOMAIN_HYPHEN_END')
                        elif last_char == BACKSLASH:
                            tmp_ret('ERR_BACKSLASH_END')
                        elif last_char == DOT:
                            tmp_ret('ERR_DOT_END')

                if full_local:

                    if email_info.this_char(position) == DOT:
                        return tmp_ret('ERR_DOT_START')

                    if email_info.flags.at_in_cfws:
                        tmp_ret('DEPREC_CFWS_NEAR_AT')

                    if email_info.this_char(position + tmp_ret) != AT:
                        tmp_ret(extra_text_err)

                        if not email_info.find(position + tmp_ret, AT, skip_quoted_str=True):
                            tmp_ret('ERR_NO_DOMAIN_SEP')

                    else:
                        if tmp_ret > 64:
                            tmp_ret('RFC5322_LOCAL_TOO_LONG')

                        last_char = email_info.this_char(-1)

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


def wrapped_parser(str_wrapper=None, cfws_wrapper=False, no_end_error=''):  # , bad_text_error=''):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(email_info, position, *args, stw=str_wrapper, cfwsw=cfws_wrapper,
                         init_cfws=None, init_start=None, **kwargs):
            
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

            if cfwsw:
                wrapped_stage.append('cfws')

            wrapped_stage_name = 'wrapping in %s' % '/'.join(wrapped_stage)
            email_info.begin_stage(wrapped_stage_name, position)

            tmp_ret = email_info.fb(position)
            
            if cfwsw:
                if init_cfws is None:
                    init_cfws = cfws(email_info, position)
                if init_cfws:
                    init_cfws.flags.CFWS_LAST = False
                tmp_ret += init_cfws

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

            if cfwsw:
                tmp_cfws = cfws(email_info, position + tmp_ret)
                tmp_ret += tmp_cfws

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


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  INITIAL PARSER">
# **********************************************************************************

@email_parser()  # skip=true
def address_spec(email_info, position):
    """
    addr-spec = local-part "@" domain
    """
    email_info.in_local_part = True
    email_info.in_domain_part = False
    email_info.near_at_flag = False
    tmp_ret = email_info.fb(position)

    # email_info.add_note_trace('Address Length: ' + str(email_info.email_len))

    if email_info.email_len == 0:
        # email_info.add_note_trace('Empty address')
        return tmp_ret('ERR_EMPTY_ADDRESS')

    tmp_ret += local_part(email_info, position)

    if not tmp_ret:
        tmp_ret += at(email_info, position)
        if tmp_ret:
            return tmp_ret('ERR_NO_LOCAL_PART')
        else:
            return tmp_ret('ERR_UNKNOWN')

    email_info.in_local_part = False

    tmp_ret_2 = at(email_info, position + tmp_ret)

    email_info.near_at_flag = True
    email_info.in_domain_part = True

    if tmp_ret_2:
        tmp_ret_2.at_loc = position + tmp_ret

        tmp_ret_3 = domain(email_info, position + tmp_ret + tmp_ret_2)

        if tmp_ret_3:
            tmp_ret += tmp_ret_2
            tmp_ret += tmp_ret_3
        else:
            return tmp_ret(tmp_ret_2, 'ERR_NO_DOMAIN_PART')

    elif not email_info.find(position + tmp_ret, AT, skip_quoted_str=True):
        tmp_ret('ERR_NO_DOMAIN_SEP')
    else:
        return tmp_ret

    if tmp_ret > 254:
        tmp_ret('RFC5322_TOO_LONG')

    if not tmp_ret.results:
        tmp_ret('VALID')

    return tmp_ret

# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  LOCAL PARSERS  ">
# **********************************************************************************


@email_parser()
def local_part(email_info, position):

    tmp_ret = email_info.fb(position)

    tmp_dot_atom = dot_atom(email_info, position)
    if tmp_dot_atom:
        return tmp_dot_atom

    tmp_qstring = quoted_string(email_info, position)
    if tmp_qstring:
        return tmp_qstring

    tmp_obs_lpart = obs_local_part(email_info, position)
    if tmp_obs_lpart:
        return tmp_obs_lpart

    # return email_info.football_max(tmp_dot_atom, tmp_qstring, tmp_obs_lpart,
    #                          names=['dot-atom', 'quoted_string', 'obs_local_part'])

    tmp_ret += parse_best(email_info, position, tmp_dot_atom, tmp_qstring, tmp_obs_lpart)

    # else:
    #     if 'CFWS_LAST' in tmp_ret.flags:
    #         extra_text_error = 'ERR_ATEXT_AFTER_CFWS'
    #     else:
    #        extra_text_error = 'ERR_EXPECTING_ATEXT'

    # if email_info.at_in_cfws:
    #     tmp_ret('DEPREC_CFWS_NEAR_AT')

    return tmp_ret


@email_parser(name='dot_atom', full_local_part=True, extra_text_error='ERR_EXPECTING_ATEXT')
@wrapped_parser(cfws_wrapper=True)
def dot_atom_local(email_info, position):
    """
    dot-atom        =   [CFWS] dot-atom-text [CFWS]
    """
    tmp_ret = email_info.fb(position)
    email_info.flags.near_at_flag = False
    email_info.flags.at_in_cfws = False

    tmp_ret += dot_atom_text(email_info, position + tmp_ret)

    return tmp_ret


@email_parser(pass_diags='DEPREC_LOCAL_PART', full_local_part=True, extra_text_error='')
def obs_local_part(email_info, position):
    """
    obs-local-part = word *("." word)
    """
    tmp_word = email_info.word(position)
    tmp_ret = email_info.fb(position)

    if not tmp_word:
        return tmp_ret

    tmp_ret += tmp_word

    tmp_ret += parse_loop(email_info, position, parse_and, single_dot, word)

    if 'CFWS_COMMENT' in tmp_ret:
        tmp_ret('DEPREC_COMMENT')

    return tmp_ret


@email_parser(name='quoted_string', full_local_part=True, extra_text_error='ERR_ATEXT_AFTER_QS')
def quoted_string_local(email_info, position):
    return quoted_string(email_info, position, is_history_item=False)

# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  DOMAIN PARSERS  ">
# **********************************************************************************

'''
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
'''


@email_parser()
def domain(email_info, position):

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

    [1005]      DNSWARN_NO_MX_RECORD  Couldn't find an MX record for this domain but an A-record does exist
                                        (ISEMAIL_DNSWARN)
    [1006]         DNSWARN_NO_RECORD  Couldn't find an MX record or an A-record for this domain (ISEMAIL_DNSWARN)
    [1065]            RFC5322_DOMAIN  Address is RFC 5322 compliant but contains domain characters that are not allowed
                                        by DNS (ISEMAIL_RFC5322)
    [1068]   RFC5322_DOMAIN_TOO_LONG  The domain part is too long (ISEMAIL_RFC5322)
    [1069]    RFC5322_LABEL_TOO_LONG  The domain part contains an element that is too long (ISEMAIL_RFC5322)
    [1143]   ERR_DOMAIN_HYPHEN_START  A domain or subdomain cannot begin with a hyphen (ISEMAIL_ERR)
    [1144]     ERR_DOMAIN_HYPHEN_END  A domain or subdomain cannot end with a hyphen (ISEMAIL_ERR)
    """

    # tmp_ret = email_info.fb(position)

    only_domain_lit = False
    is_literal = False
    # has_cfws = False

    # lit_init = email_info.fb(position)
    init_sb = open_sq_bracket(email_info, position)

    if init_sb:
        is_literal = True
        init_cfws = None
    else:
        init_cfws = cfws(email_info, position)
        if init_cfws:
            init_sb += open_sq_bracket(email_info, position + init_cfws)
            if init_sb:
                is_literal = True
                only_domain_lit = True

    if is_literal:
        if not only_domain_lit:
            tmp_addr_lit = address_literal(email_info, position, init_start=init_sb)
            if tmp_addr_lit and email_info.at_end(position + tmp_addr_lit):
                return tmp_addr_lit
        else:
            tmp_addr_lit = email_info.fb(position)

        tmp_dom_lit = domain_literal(email_info, position, init_start=init_sb, init_cfws=init_cfws)
        if tmp_dom_lit and email_info.at_end(position + tmp_addr_lit):
            return tmp_dom_lit

        return parse_best(email_info, position, tmp_addr_lit, tmp_dom_lit)

    else:
        if init_cfws is None:
            tmp_domain_addr = domain_addr(email_info, position)
            if tmp_domain_addr and email_info.at_end(position + tmp_domain_addr):
                return tmp_domain_addr
        else:
            tmp_domain_addr = email_info.fb(position)

        tmp_dot_atom = dot_atom_domain(email_info, position, init_cfws=init_cfws)
        if tmp_dot_atom and email_info.at_end(position + tmp_dot_atom):
            return tmp_dot_atom

        tmp_obs_domain = obs_domain(email_info, position, init_cfws=init_cfws)
        if tmp_obs_domain and email_info.at_end(position + tmp_obs_domain):
            return tmp_obs_domain

        # return email_info.football_max(tmp_domain_addr, tmp_dot_atom, tmp_obs_domain,
        #                         names=['domain_addr', 'dot_atom', 'obs_domain'])

        return parse_best(email_info, position, tmp_domain_addr, tmp_dot_atom, tmp_obs_domain)


# if is_literal:
#     extra_text_error = 'ERR_ATEXT_AFTER_DOMLIT'
# elif 'RFC5322_LIMITED_DOMAIN' in tmp_ret:
#     if 'CFWS_LAST' in tmp_ret.flags:
#         extra_text_error = 'ERR_ATEXT_AFTER_CFWS'
#     else:
#         extra_text_error = 'ERR_EXPECTING_ATEXT'
# else:
#     extra_text_error = 'ERR_EXPECTING_DTEXT'

# return tmp_ret


@email_parser(name='dot_atom', full_domain_part=True, extra_text_error='ERR_EXPECTING_ATEXT',
              pass_diags=('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN'))
@wrapped_parser(cfws_wrapper=True)
def dot_atom_domain(email_info, position):
    """
    dot-atom        =   [CFWS] dot-atom-text [CFWS]
    """
    tmp_ret = email_info.fb(position)
    email_info.flags.near_at_flag = False
    email_info.flags.at_in_cfws = False

    tmp_ret += dot_atom_text(email_info, position + tmp_ret)
    tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.DNS

    return tmp_ret


@email_parser(full_domain_part=True, extra_text_error='ERR_EXPECTING_DTEXT')
def domain_addr(email_info, position):
    """
    domain-addr = sub-domain *("." sub-domain)
    [1009]               RFC5321_TLD  Address is valid but at a Top Level Domain (ISEMAIL_RFC5321)
    [1010]       RFC5321_TLD_NUMERIC  Address is valid but the Top Level Domain begins with a number (ISEMAIL_RFC5321)

    """
    last_dom_pos = position
    tmp_ret = email_info.fb(position)
    tmp_ret += sub_domain(email_info, position)

    if not tmp_ret:
        return tmp_ret

    tmp_ret_2 = parse_loop(email_info, position + tmp_ret, parse_and, single_dot, sub_domain)

    if tmp_ret_2:
        tmp_ret += tmp_ret_2
    else:
        tmp_ret('RFC5321_TLD')

    if email_info.this_char(last_dom_pos) in DIGIT:
        tmp_ret('RFC5321_TLD_NUMERIC')
        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.OTHER_NON_DNS
    else:
        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.DNS

    return tmp_ret


@email_parser(fail_diags='ERR_EXPECTING_DTEXT',
              pass_diags=('RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_LIMITED_DOMAIN'),
              extra_text_error='ERR_ATEXT_AFTER_DOMLIT',
              full_domain_part=True)
@wrapped_parser('[]', cfws_wrapper=True, no_end_error='ERR_UNCLOSED_DOM_LIT')  # , bad_text_error='ERR_EXPECTING_DTEXT')
def domain_literal(email_info, position):
    """
    domain-literal  =   [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
    // Domain literal must be the only component

    [1070]    RFC5322_DOMAIN_LITERAL  The domain literal is not a valid RFC 5321 address literal (ISEMAIL_RFC5322)
    [1129]       ERR_EXPECTING_DTEXT  A domain literal contains a character that is not allowed (ISEMAIL_ERR)
    [1147]      ERR_UNCLOSED_DOM_LIT  Domain literal is missing its closing bracket (ISEMAIL_ERR)
    """
    tmp_ret = email_info.fb(position)

    email_info.near_at_flag = False

    tmp_ret_fws = fws(email_info, position)
    tmp_ret_dtext = dtext(email_info, position + tmp_ret_fws)

    if tmp_ret_dtext:
        tmp_ret += tmp_ret_fws
        tmp_ret += tmp_ret_dtext
    else:
        return tmp_ret('ERR_EXPECTING_DTEXT')

    tmp_ret += parse_loop(email_info, position + tmp_ret, parse_and, fws, dtext)
    tmp_ret += fws(email_info, position + tmp_ret)
    tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT

    return tmp_ret


@email_parser(pass_diags='RFC5321_ADDRESS_LITERAL', full_domain_part=True, extra_text_error='')
@wrapped_parser('[]', no_end_error='ERR_UNCLOSED_DOM_LIT')  # , bad_text_error='ERR_INVALID_ADDR_LITERAL')
def address_literal(email_info, position, init_start):
    """
    address-literal  = "[" ( IPv4-address-literal /
                    IPv6-address-literal /
                    General-address-literal ) "]"

    [1012]   RFC5321_ADDRESS_LITERAL  Address is valid but at a literal address not a domain (ISEMAIL_RFC5321)
    ERR_UNCLOSED_DOM_LIT  Unclosed domain literal.

    ERR_INVALID_ADDR_LITERAL
    """

    tmp_ret = email_info.fb(position)

    tmp_ipv6 = ipv6_address_literal(email_info, position + tmp_ret + init_start)
    if tmp_ipv6 and email_info.at_end(position + tmp_ipv6):
        return tmp_ret(init_start, tmp_ipv6)

    tmp_ipv4 = ipv4_address_literal(email_info, position + tmp_ret + init_start)
    if tmp_ipv4 and email_info.at_end(position + tmp_ipv4):
        return tmp_ret(init_start, tmp_ipv4)

    tmp_gen_lit = general_address_literal(email_info, position + tmp_ret + init_start)
    if tmp_gen_lit and email_info.at_end(position + tmp_gen_lit):
        tmp_ret('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN')
        return tmp_ret(init_start, tmp_gen_lit)

    # tmp_ret = email_info.football_max(tmp_ipv4, tmp_ipv6, tmp_gen_lit, names=['ipv4', 'ipv6', 'gen_lit'])

    return tmp_ret


@email_parser(pass_diags=('RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN'), full_domain_part=True,
              extra_text_error='ERR_EXPECTING_DTEXT')
def obs_domain(email_info, position, init_cfws=None):
    """
    obs-domain = atom *("." atom)
            [1037]            DEPREC_COMMENT  Address contains a comment in a position that is deprecated
                                (ISEMAIL_DEPREC)
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += atom(email_info, position, init_cfws=init_cfws)

    if not tmp_ret:
        return tmp_ret('ERR_EXPECTING_ATEXT')

    tmp_ret += parse_loop(email_info, position + tmp_ret, parse_and, single_dot, atom, min_loop=0, max_loop=256)

    tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.OTHER_NON_DNS

    return tmp_ret


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  IP ADDRESS PARSERS  ">
# **********************************************************************************


@email_parser(pass_diags='RFC5322_GENERAL_LITERAL')
def general_address_literal(email_info, position):
    """
    General-address-literal  = Standardized-tag ":" 1*dcontent

            RFC5322_GENERAL_LITERAL

    """
    tmp_ret = email_info.fb(position)
    tmp_ret_2 = parse_and(email_info, position, standardized_tag, colon, dcontent)

    if tmp_ret_2:
        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.GENERAL_LIT
        return tmp_ret(tmp_ret_2)
    else:
        return tmp_ret


@email_parser()
def standardized_tag(email_info, position):
    """
        Standardized-tag  = Ldh-str
                         ; Standardized-tag MUST be specified in a
                         ; Standards-Track RFC and registered with IANA
    """
    if simple_str(email_info, position, 'IPv6:', False):
        return email_info.fb(position)

    tmp_ret = ldh_str(email_info, position)
    tmp_str = email_info.mid(position, tmp_ret.l)

    if tmp_str in ISEMAIL_ALLOWED_GENERAL_ADDRESS_LITERAL_STANDARD_TAGS:
        return tmp_ret
    else:
        return email_info.fb(position)


def ipv6_segment(email_info, position, min_count=1, max_count=7):
    tmp_ret = email_info.fb(position)
    tmp_ret += ipv6_hex(email_info, position)

    if tmp_ret:
        if max_count == 1:
            return 1, tmp_ret

        if not email_info.at_end(position + tmp_ret.l + 1) and \
                email_info.this_char(position + tmp_ret.l) == ':' and \
                email_info.this_char(position + tmp_ret.l + 1) == ':' and \
                min_count <= 1:
            # email_info.add_note_trace('Double Colons found, exiting')
            return 1, tmp_ret

        # tmp_colon_str = {'string_in': COLON, 'min_count': 1, 'max_count': 1}
        tmp_count, tmp_ret_2 = parse_loop(
            email_info,
            position + tmp_ret,
            parse_and,
            colon,
            ipv6_hex,
            min_loop=min_count - 1,
            max_loop=max_count - 1,
            ret_count=True)
    else:
        return 0, email_info.fb(position)

    if tmp_ret_2:
        return tmp_count + 1, tmp_ret(tmp_ret_2)
    else:
        return 0, email_info.fb(position)


@email_parser(pass_diags='RFC5322_IPV4_ADDR')
def ipv4_address_literal(email_info, position):
    """
    IPv4-address-literal  = Snum 3("."  Snum)

    RFC5322_IPV4_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += parse_and(email_info, position, snum, single_dot, snum, single_dot, snum, single_dot, snum)

    if tmp_ret:
        tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.IPv4
    return tmp_ret


@email_parser()
def snum(email_info, position):
    """
            Snum           = 1*3DIGIT
                          ; representing a decimal integer
                          ; value in the range 0 through 255
    """
    tmp_ret = three_digit(email_info, position)
    if tmp_ret:
        tmp_str = email_info.mid(position, tmp_ret.l)

        tmp_digit = int(tmp_str)
        if tmp_digit > 255:
            return email_info.fb(position)

    return tmp_ret


@email_parser(pass_diags='RFC5322_IPV6_ADDR')
def ipv6_address_literal(email_info, position):
    """
        IPv6-address-literal  = "IPv6:" IPv6-addr
    [1013]   RFC5321_IPV6_DEPRECATED  Address is valid but contains a :: that only elides one zero group. All
                                        implementations must accept and be able to handle any legitimate RFC 4291
                                        format. (ISEMAIL_DEPREC)
    [1072]    RFC5322_IPV6_GRP_COUNT  The IPv6 literal address contains the wrong number of groups (ISEMAIL_RFC5322)
    [1073]   RFC5322_IPV6_2X2X_COLON  The IPv6 literal address contains too many :: sequences (ISEMAIL_RFC5322)
    [1074]     RFC5322_IPV6_BAD_CHAR  The IPv6 address contains an illegal group of characters (ISEMAIL_RFC5322)
    [1075]     RFC5322_IPV6_MAX_GRPS  The IPv6 address has too many groups (ISEMAIL_RFC5322)
    [1076]   RFC5322_IPV6_COLON_STRT  IPv6 address starts with a single colon (ISEMAIL_RFC5322)
    [1077]    RFC5322_IPV6_COLON_END  IPv6 address ends with a single colon (ISEMAIL_RFC5322)

    RFC5322_IPV6_ADDR
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += ipv6(email_info, position)

    if tmp_ret:
        tmp_ret_2 = ipv6_addr(email_info, position + tmp_ret)

        if tmp_ret_2:
            tmp_ret += tmp_ret_2
            tmp_ret.domain_type = ISEMAIL_DOMAIN_TYPE.IPv6
            return tmp_ret

    return email_info.fb(position)


@email_parser()
def ipv6_addr(email_info, position):
    """
            IPv6-addr      = IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp
    """
    tmp_ret = email_info.fb(position)

    dot_count = email_info.count(position, email_info.DOT, stop_for=email_info.CLOSESQBRACKET)

    # email_info.add_note_trace('Dot count = ' + str(dot_count))
    if dot_count:
        tmp_ret += ipv6v4_full(position) or ipv6v4_comp(position)
    else:
        tmp_ret += ipv6_full(position) or ipv6_comp(position)

    return tmp_ret


@email_parser()
def ipv6_hex(email_info, position):
    """
    IPv6-hex       = 1*4HEXDIG
    """
    return hexdigit(email_info, position)


@email_parser(pass_diags='RFC5322_IPV6_FULL_ADDR')
def ipv6_full(email_info, position):
    """
    IPv6-full = IPv6-hex 7(":" IPv6-hex)
    RFC5322_IPV6_FULL_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_count, tmp_ret_2 = ipv6_segment(email_info, position, max_count=8, min_count=8)
    if tmp_ret_2:
        return tmp_ret(tmp_ret_2)
    else:
        return email_info.fb(position)


@email_parser(pass_diags='RFC5322_IPV6_COMP_ADDR')
def ipv6_comp(email_info, position):
    """
            IPv6-comp      = [IPv6-hex *5(":" IPv6-hex)] "::"
                          [IPv6-hex *5(":" IPv6-hex)]
                          ; The "::" represents at least 2 16-bit groups of
                          ; zeros.  No more than 6 groups in addition to the
                          ; "::" may be present.
          RFC5322_IPV6_COMP_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_pre_count, tmp_ret_2 = ipv6_segment(email_info, position, min_count=1, max_count=6)

    if not tmp_ret_2:
        return email_info.fb(position)
    tmp_ret += tmp_ret_2

    tmp_ret_2 = double_colon(email_info, position + tmp_ret)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2

    tmp_post_count, tmp_ret_2 = ipv6_segment(email_info, position + tmp_ret.l, min_count=1, max_count=6)

    if not tmp_ret_2:
        tmp_ret_2 = ipv6_hex(email_info, position + tmp_ret.l)
        if not tmp_ret_2:
            return email_info.fb(position)
        tmp_post_count = 1

    tmp_ret += tmp_ret_2
    if (tmp_pre_count + tmp_post_count) > 6:
        # email_info.add_note_trace('Segment count: %s + %s, exceeds 6, failing' % (tmp_pre_count, tmp_post_count))
        return email_info.fb(position)

    else:
        # email_info.add_note_trace('Segment count: %s + %s, passing' % (tmp_pre_count, tmp_post_count))
        return tmp_ret


@email_parser(pass_diags='RFC5322_IPV6_IPV4_ADDR')
def ipv6v4_full(email_info, position):
    """
    IPv6v4-full  = IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal

    RFC5322_IPV6_IPV4_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_count, tmp_ret_2 = ipv6_segment(email_info, position, min_count=6, max_count=6)
    tmp_ret += tmp_ret_2

    if tmp_ret_2:
        tmp_ret_2 = colon(email_info, position + tmp_ret)
    else:
        return email_info.fb(position)

    if tmp_ret_2:
        tmp_ret += tmp_ret_2
        tmp_ret_2 = ipv4_address_literal(email_info, position + tmp_ret.l)
    else:
        return email_info.fb(position)

    if tmp_ret_2:
        tmp_ret += tmp_ret_2
    else:
        return email_info.fb(position)

    tmp_ret.remove('RFC5322_IPV4_ADDR')
    return tmp_ret


@email_parser(pass_diags='RFC5322_IPV6_IPV4_COMP_ADDR')
def ipv6v4_comp(email_info, position):
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
    tmp_pre_count, tmp_ret_2 = ipv6_segment(email_info, position, min_count=1, max_count=3)
    tmp_ret += tmp_ret_2

    if not tmp_ret:
        return email_info.fb(position)

    tmp_ret_2 = double_colon(email_info, position + tmp_ret)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2

    colon_count = email_info.count(position + tmp_ret, COLON, stop_for=CLOSESQBRACKET)
    if colon_count > 3:
        return email_info.fb(position)

    tmp_post_count, tmp_ret_2 = ipv6_segment(email_info, position + tmp_ret.l,
                                             min_count=colon_count, max_count=colon_count)

    # email_info.add_note_trace('should be start of IPv4 segment')

    tmp_ret += tmp_ret_2
    tmp_ret_2 = colon(email_info, position + tmp_ret)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2
    tmp_ret_2 = ipv4_address_literal(email_info, position + tmp_ret.l)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2

    if tmp_pre_count + tmp_post_count > 4:
        # email_info.add_note_trace('Segment count: %s + %s, exceeds 4, failing' % (tmp_pre_count, tmp_post_count))
        return email_info.fb(position)

    else:
        # email_info.add_note_trace('Segment count: %s + %s, passing' % (tmp_pre_count, tmp_post_count))
        tmp_ret.remove('RFC5322_IPV4_ADDR')
        return tmp_ret


# **********************************************************************************
# </editor-fold>
# **********************************************************************************

# **********************************************************************************
# <editor-fold desc="  MISC PARSERS  ">
# **********************************************************************************


@email_parser()
def ldh_str(email_info, position):
    """
    Ldh-str = *( ALPHA / DIGIT / "-" ) Let-dig
    """
    tmp_ret = sub_ldh_str(email_info, position)

    while email_info.this_char(position + tmp_ret - 1) == "-":
        tmp_ret -= 1
        if tmp_ret == 0:
            return tmp_ret
    return tmp_ret


@email_parser()
def dtext(email_info, position):
    """
        dtext = %d33-90 / %d94-126 / obs-dtext
        Printable US-ASCII characters not including "[", "]", or "\"
    """
    tmp_ret = email_info.fb(position)

    tmp_ret += parse_loop(email_info, position, parse_or, DTEXT, obs_dtext)

    return tmp_ret


@email_parser(pass_diags='RFC5322_DOM_LIT_OBS_DTEXT')
def obs_dtext(email_info, position):
    """
    obs-dtext = obs-NO-WS-CTL / quoted-pair
    [1071] RFC5322_DOM_LIT_OBS_DTEXT  The domain literal is not a valid RFC 5321 address literal and it contains
            obsolete characters (ISEMAIL_RFC5322)
    """
    tmp_ret = email_info.fb(position)

    while True:
        tmp_ret_2 = obs_dtext_sub(email_info, position + tmp_ret)
        tmp_ret_2 += quoted_pair(email_info, position + tmp_ret + tmp_ret_2)

        if tmp_ret_2:
            tmp_ret += tmp_ret_2
        else:
            break

    return tmp_ret


@email_parser()
def sub_domain(email_info, position):
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
    tmp_ret += let_dig(email_info, position)
    if tmp_ret:
        tmp_ret += ldh_str(email_info, position + tmp_ret)

        if tmp_ret.l > 63:
            tmp_ret('RFC5322_LABEL_TOO_LONG')

        return tmp_ret
    else:
        return email_info.fb(position)


@email_parser()
def word(email_info, position):
    """
        word = atom / quoted-string

        // The entire local-part can be a quoted string for RFC 5321
        // If it's just one atom that is quoted then it's an RFC 5322 obsolete form

    """
    email_info.at_in_cfws = False
    tmp_ret = email_info.fb(position)
    # tmp_act, tmp_ret2 = email_info.try_or(position,
    #                       email_info.atom,
    #                       email_info.quoted_string)

    tmp_ret_2 = atom(email_info, position)
    if tmp_ret_2:
        return tmp_ret(tmp_ret_2)

    tmp_ret_3 = quoted_string(email_info, position)
    if tmp_ret_3:
        return tmp_ret(tmp_ret_3)

    # return tmp_ret(email_info.football_max(tmp_ret_2, tmp_ret_3, names=['atom', 'quoted_string']))
    tmp_ret += parse_best(email_info, position, tmp_ret_2, tmp_ret_3)
    return tmp_ret


@email_parser()
@wrapped_parser(cfws_wrapper=True)
def atom(email_info, position):
    """
    atom = [CFWS] 1*atext [CFWS]
    """

    tmp_ret = email_info.fb(position)

    email_info.flags.near_at_flag = False

    tmp_ret_2 = atext(email_info, position + tmp_ret)

    if not tmp_ret_2:
        return tmp_ret('ERR_EXPECTING_ATEXT')

    # if tmp_ret and tmp_ret_cfws:
    #     if not (email_info.at_end(position + tmp_ret + tmp_ret_cfws) or
    #                     email_info.this_char(position + tmp_ret + tmp_ret_cfws) == AT or
    #                     email_info.this_char(position + tmp_ret + tmp_ret_cfws) == DOT):
    #       tmp_ret('ERR_ATEXT_AFTER_CFWS', raise_on_error=False)

    # if not tmp_ret or tmp_ret.error:
    #     email_info.near_at_flag = tmp_near_at_flag

    return tmp_ret


@email_parser()
@wrapped_parser(cfws_wrapper=True)
def dot_atom(email_info, position):
    """
    dot-atom        =   [CFWS] dot-atom-text [CFWS]
    """
    tmp_ret = email_info.fb(position)
    email_info.flags.near_at_flag = False
    email_info.flags.at_in_cfws = False

    tmp_ret += dot_atom_text(email_info, position + tmp_ret)

    return tmp_ret


@email_parser()
def dot_atom_text(email_info, position):
    """
    dot-atom-text   =   1*atext *("." 1*atext)
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.atext(position)

    if email_info.at_end(position + tmp_ret) or not tmp_ret:
        return tmp_ret

    tmp_ret += parse_loop(email_info, position, parse_and, single_dot, atext)

    return tmp_ret


@email_parser()  # was skip=true
def cfws(email_info, position):
    """
    CFWS = (1*([FWS] comment) [FWS]) / FWS
        // http://tools.ietf.org/html/rfc5322#section-3.4.1
        //   Comments and folding white space
        //   SHOULD NOT be used around the "@" in the addr-spec.

    """
    tmp_ret = email_info.fb(position)

    if not pre_cfws(email_info, position):
        return tmp_ret

    tmp_ret_fws = fws(email_info, position)
    tmp_ret_comment = comment(email_info, position + tmp_ret_fws)
    if tmp_ret_comment:
        tmp_ret += tmp_ret_fws
        tmp_ret += tmp_ret_comment
        tmp_ret += fws(email_info, position + tmp_ret)

    if 'CFWS_LAST' in tmp_ret.flags and AT in email_info.mid(position, tmp_ret.l):
        tmp_ret('DEPREC_CFWS_NEAR_AT')

    if tmp_ret:
        tmp_ret.flags += 'CFWS_LAST'

    return tmp_ret


@email_parser(is_history_item=False)
def sub_cfws(email_info, position):
    """
    sub_CFWS = (1*([FWS] comment) [FWS])
        // http://tools.ietf.org/html/rfc5322#section-3.4.1
        //   Comments and folding white space
        //   SHOULD NOT be used around the "@" in the addr-spec.

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += fws(email_info, position)
    tmp_ret += no_at(email_info, position + tmp_ret)
    tmp_ret += comment(email_info, position + tmp_ret)
    if tmp_ret:
        tmp_ret += no_at(email_info, position + tmp_ret)
        tmp_ret += fws(email_info, position + tmp_ret)
    return tmp_ret


@email_parser(pass_diags='CFWS_COMMENT', is_comment=True)
@wrapped_parser('()', no_end_error='ERR_UNCLOSED_COMMENT')  # bad_text_error='ERR_EXPECTING_CTEXT',
def comment(email_info, position):
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
    [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign
                                        (ISEMAIL_DEPREC)
    [1146]      ERR_UNCLOSED_COMMENT  Unclosed comment (ISEMAIL_ERR)
    [1152]     ERR_MULT_FWS_IN_COMMENT Address contains multiple FWS in a comment (ISEMAIL_ERR)

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += fws(email_info, position)
    tmp_content = ccontent(email_info, position)
    if not tmp_content:
        return email_info.fb(position)

    tmp_ret += parse_loop(email_info, position, parse_and, fws, ccontent)

    tmp_ret += fws(email_info, position)

    return tmp_ret


@email_parser()
def ccontent(email_info, position):
    """
    ccontent        =   ctext / quoted-pair / comment
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += ctext(email_info, position) or quoted_pair(email_info, position) or comment(email_info, position)
    return tmp_ret


@email_parser()
def ctext(email_info, position):
    """
    ctext           =   %d33-39 /          ; Printable US-ASCII
                       %d42-91 /          ;  characters not including
                       %d93-126 /         ;  "(", ")", or "\"
                       obs-ctext
    [1139]       ERR_EXPECTING_CTEXT  A comment contains a character that is not allowed (ISEMAIL_ERR)

    """
    tmp_ret = email_info.fb(position)
    return tmp_ret(sub_ctext(email_info, position) or obs_ctext(email_info, position))


@email_parser(pass_diags='DEPREC_CTEXT')
def obs_ctext(email_info, position):
    """
        obs-ctext       =   obs-NO-WS-CTL
    [1038]              DEPREC_CTEXT  A comment contains a deprecated character (ISEMAIL_DEPREC)
    """
    return simple_char(email_info, position, OBS_CTEXT)


@email_parser(pass_diags='CFWS_FWS')
def fws(email_info, position=None):
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
    tmp_ret = email_info.fb(position)
    tmp_ret += fws_sub(email_info, position) or obs_fws(email_info, position)
    return tmp_ret


@email_parser()
def fws_sub(email_info, position=None):
    """
    FWS             =   ([*WSP CRLF] 1*WSP)
    [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign
                                        (ISEMAIL_DEPREC)
    """
    tmp_ret = email_info.fb(position)

    tmp_ret += wsp(email_info, position)

    if not tmp_ret:
        return email_info.fb(position)

    else:
        tmp_ret_crlf = crlf(email_info, position + tmp_ret)

        if tmp_ret_crlf.error:
            return tmp_ret(tmp_ret_crlf).set(0)

        if not tmp_ret_crlf:
            return tmp_ret

        tmp_ret += tmp_ret_crlf

        tmp_ret_2 = one_wsp(email_info, position + tmp_ret)

        if tmp_ret_2:
            return tmp_ret(tmp_ret_2)

        else:
            return email_info.fb(position)


@email_parser(pass_diags='DEPREC_FWS')
def obs_fws(email_info, position):
    """
        obs-FWS         =   1*([CRLF] WSP)     ; As amended in erratum #1908

    [1034]                DEPREC_FWS  Address contains an obsolete form of Folding White Space (ISEMAIL_DEPREC)
    [1148]           ERR_FWS_CRLF_X2  Folding White Space contains consecutive CRLF sequences (ISEMAIL_ERR)
    [1049]       DEPREC_CFWS_NEAR_AT  Address contains a comment or Folding White Space around the @ sign
                                        (ISEMAIL_DEPREC)
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += crlf(position)

    if tmp_ret.error:
        return tmp_ret

    if tmp_ret:
        if email_info.at_end(position + tmp_ret.l):
            return tmp_ret("ERR_FWS_CRLF_END")

    tmp_ret_2 = wsp(email_info, position + tmp_ret)
    if tmp_ret_2:
        return tmp_ret(tmp_ret_2)
    else:

        return email_info.fb(position)


@email_parser(is_history_item=False, pass_diags='RFC5321_QUOTED_STRING')
@wrapped_parser('"', cfws_wrapper=True, no_end_error='ERR_UNCLOSED_QUOTED_STR')  # bad_text_error='ERR_EXPECTING_QTEXT')
def quoted_string(email_info, position):
    """
            quoted-string = [CFWS] DQUOTE *([FWS] qcontent) [FWS] DQUOTE [CFWS]

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
    email_info.flags.near_at_flag = False

    last_was_fws = False
    # has_qtext = False
    while True:

        tmp_loop_1 = email_info.fws(email_info, position + tmp_ret)

        if tmp_loop_1:
            tmp_loop_1.remove('CFWS_FWS')
            if last_was_fws:
                tmp_ret += tmp_loop_1
                return tmp_ret(("ERR_MULT_FWS_IN_QS", position + tmp_ret, tmp_ret))
            else:
                last_was_fws = False

        tmp_loop_2 = email_info.qcontent(email_info, position + tmp_ret + tmp_loop_1)

        if tmp_loop_2:
            tmp_ret += tmp_loop_1
            tmp_ret += tmp_loop_2
            # has_qtext = True
        else:
            break

    return tmp_ret


@email_parser()
def qcontent(email_info, position):
    """
        qcontent  =   qtext / quoted-pair
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += qtext(email_info, position) or quoted_pair(email_info, position)
    return tmp_ret


@email_parser()
def qtext(email_info, position):
    """
        qtext           =   %d33 /             ; Printable US-ASCII
                           %d35-91 /          ;  characters not including
                           %d93-126 /         ;  "\" or the quote character
                           obs-qtext
    """
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.simple_char(email_info, position, QTEXT) or obs_qtext(email_info, position)
    return tmp_ret


@email_parser(pass_diags='DEPREC_QTEXT')
def obs_qtext(email_info, position):
    """
        obs-qtext       =   obs-NO-WS-CTL

    [1035]              DEPREC_QTEXT  A quoted string contains a deprecated character (ISEMAIL_DEPREC)

    """
    return email_info.simple_char(email_info, position, OBS_QTEXT)


@email_parser()
def quoted_pair(email_info, position):
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

    [1136]       ERR_EXPECTING_QPAIR  The address contains a character that is not allowed in a quoted pair
                                        (ISEMAIL_ERR)

    """

    tmp_ret = email_info.fb(position)

    tmp_ret += back_slash(email_info, position)

    if tmp_ret and email_info.at_end(position + 1):
        tmp_ret('ERR_EXPECTING_QPAIR')

    if tmp_ret:

        tmp_ret_1 = vchar_wsp(email_info, position + 1)

        if tmp_ret_1:
            return tmp_ret(tmp_ret_1)
        tmp_ret_1 = obs_qp(email_info, position + 1)

        if tmp_ret_1:
            return tmp_ret(tmp_ret_1)

        else:
            tmp_ret('ERR_EXPECTING_QPAIR')

    else:
        return email_info.fb(position)


@email_parser()
def vchar_wsp(email_info, position):
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
    return email_info.simple_char(position, VCHAR_WSP, max_count=1)


@email_parser(pass_diags='DEPREC_QP')
def obs_qp(email_info, position):
    """
        obs-qp = (%d0 / obs-NO-WS-CTL / LF / CR)

    [1036]                 DEPREC_QP  A quoted pair contains a deprecated character (ISEMAIL_DEPREC)

    """
    return email_info.simple_char(email_info, position, OBS_QP, max_count=1)


@email_parser()
def crlf(email_info, position, in_crlf=False):
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
                tmp_crlf_2 = crlf(email_info, position + tmp_ret.l, in_crlf=True)
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


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="    SIMPLE STRINGS    ">
# **********************************************************************************


@email_parser(is_history_item=False, pass_diags='DEPREC_CFWS_NEAR_AT')
def no_at(email_info, position):
    return email_info.simple_char(email_info, position, AT, max_count=1)


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


@email_parser(is_history_item=False)
def sub_ldh_str(email_info, position):
    return simple_char(email_info, position, LDH_STR)


@email_parser()
def open_sq_bracket(email_info, position):
    return single_char(email_info, position, OPENSQBRACKET)


@email_parser()
def close_sq_bracket(email_info, position):
    return single_char(email_info, position, CLOSESQBRACKET)


@email_parser(is_history_item=False)
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


@email_parser(is_history_item=False)
def pre_cfws(email_info, position):
    return simple_char(email_info, position, PRE_CFWS)


@email_parser()
def ipv6(email_info, position):
    return simple_str(email_info, position, "IPv6:", caps_sensitive=False)


@email_parser()
def three_digit(email_info, position):
    return simple_char(email_info, position, DIGIT, max_count=3)


@email_parser(is_history_item=False)
def hexdigit(email_info, position):
    return simple_char(email_info, position, HEXDIG, min_count=-1, max_count=4)


@email_parser()
def open_parenthesis(email_info, position):
    return single_char(email_info, position, OPENPARENTHESIS)


@email_parser()
def close_parenthesis(email_info, position):
    return single_char(email_info, position, CLOSEPARENTHESIS)


@email_parser(is_history_item=False)
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


# **********************************************************************************
# </editor-fold>
# **********************************************************************************
