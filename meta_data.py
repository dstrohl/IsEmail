import re
"""
If you update this metadata, don't forget to change the actual version number
attribute in the <sections> element below!

Date       Diagnoses    Version Notes
.......... ............ ....... ...............................................
2010-11-15 #0-#151      3.0
2010-11-15 #0           3.03    Clarified definition of Valid for numpties
2013-11-30 #13          3.05    Changed category of ISEMAIL_RFC5321_IPV6DEPRECATED to ISEMAIL_DEPREC
-->
<meta version="3.03">
"""
'''
old_methods = [
    '_get_fws',
    '_get_ctext',
    '_get_atext',
    '_get_qtext',
    '_get_specials',
    '_get_obs_no_ws_ctl',
    '_get_obs_ctext',
    '_get_obs_qtext',
    '_get_vchar',
    '_get_crlf',
]
'''
parser_methods = [
    '_get_quoted_string',
    '_get_domain_part',
    '_get_comment',
    '_get_obs_local_part',
    '_get_ipv4_address_literal',
    '_get_obs_fws',
    '_get_ipv6_address_literal',
    '_get_and',
    '_get_dot_atom',
    '_get_ipv6v4_full',
    '_get_count',
    '_get_domain_literal',
    '_get_local_part',
    '_get_mark',
    '_get_char',
    '_get_ipv6_addr',
    '_get_obs_domain',
    '_get_snum',
    '_get_obs_gp',
    '_get_dot_atom_text',
    '_get_ipv6_hex',
    '_get_ipv6v4_comp',
    '_get_quoted_pair',
    '_get_general_address_literal',
    '_get_dtext',
    '_get_or',
    '_get_ipv6_comp',
    '_get_atom',
    '_get_cfws',
    '_get_ccontent',
    '_get_opt',
    '_get_word',
    '_get_address_literal',
    '_get_ipv6_full',
    '_get_qcontent',
    '_get_wsp',]

def make_char_str(*chars_in):
    tmp_ret = []
    for char in chars_in:
        if isinstance(char, str):
            tmp_ret.append(char)
        elif isinstance(char, int):
            tmp_ret.append(chr(char))
        elif isinstance(char, tuple):
            for c in range(char[0], char[1]):
                tmp_ret.append(chr(c))
    return ''.join(tmp_ret)

def _meth(meth_name, **kwargs):
    return dict(
        meth='_get_%s' % meth_name,
        args=[],
        kwargs=kwargs)


def _char(char_set, **kwargs):
    kwargs['char_set'] = char_set
    return dict(
        meth='_get_char',
        args=[],
        kwargs=kwargs)


def _and(*methods, **kwargs):
    tmp_methods = []
    for m in methods:
        tmp_methods.append(_make_meth(m))
    return dict(
        meth='_get_and',
        args=tmp_methods,
        kwargs=kwargs)


def _or(*methods, **kwargs):
    tmp_methods = []
    for m in methods:
        tmp_methods.append(_make_meth(m))
    return dict(
        meth='_get_or',
        args=tmp_methods,
        kwargs=kwargs)


def _opt(opp, **kwargs):
    opp = _make_meth(opp)
    if opp['meth'] == '_get_char':
        opp['kwargs']['optional'] = True
        return opp
    else:
        return dict(
            meth='_get_opt',
            args=(opp,),
            kwargs=kwargs)


def _c(*args):

    if len(args) == 1:
        min_count = ISEMAIL_MIN_COUNT
        max_count = ISEMAIL_MAX_COUNT
        opp = args[0]
    else:
        opp = args[1]
        first_arg = args[0]
        if isinstance(first_arg, int) or first_arg.isdigit():
            min_count = first_arg
            max_count = first_arg
        else:
            if '*' in first_arg:
                min_count, max_count = first_arg.split('*')
                if min_count == '':
                    min_count = ISEMAIL_MIN_COUNT
                if max_count == '':
                    max_count = ISEMAIL_MAX_COUNT
            else:
                raise AttributeError('"*" not in %s' % first_arg)

        min_count = int(min_count)
        max_count = int(max_count)

    opp = _make_meth(opp)

    if opp['meth'] == '_get_char':
        opp['kwargs']['min_count'] = min_count
        opp['kwargs']['max_count'] = max_count
        return opp
    else:
        return dict(
            meth='_get_count',
            args=[],
            kwargs=dict(
                min_count=min_count,
                max_count=max_count,
                opp=opp
            )
        )


def _m(opp, on_fail=None, on_pass=None, element_name=None, return_string=False):
    opp = _make_meth(opp)


    return dict(
        meth='_get_mark',
        args=[],
        kwargs=dict(
            opp=_make_meth(opp),
            on_fail=on_fail,
            on_pass=on_pass,
            element_name=element_name,
            return_string=return_string)
    )



def _make_meth(method, **kwargs):
    if isinstance(method, str):
        if '_get_%s' % method in parser_methods:
            return _meth(method, **kwargs)

        elif method[0] == '"' and method[-1] == '"':
            # if it is a quoted string:  "do this"
            tmp_and_set = []
            for c in method[1:-1]:
                tmp_and_set.append(_make_meth(c))
            return _and(*tmp_and_set)

        elif method[0] in ISEMAIL_CONSTANTS['REPEAT_FLAGS']:
            # if it has a counter in front: 1*2
            if method[1] in ISEMAIL_CONSTANTS['REPEAT_FLAGS']:
                if method[2] in ISEMAIL_CONSTANTS['REPEAT_FLAGS']:
                    return _c(method[:3], method[3:])
                else:
                    return _c(method[:2], method[2:])
            else:
                return _c(method[:1], method[1:])
        elif method[0] == '[' and method[-1] == ']':
            # if it is in square brackets:  [blah]
            tmp_opp = _make_meth(method[1:-1])
            return _opt(tmp_opp, **kwargs)

        else:
            # this is a string set
            try:
                return _char(ISEMAIL_CONSTANTS[method])
            except KeyError:
                return _char(method)
    else:
        return method




"""
 * To validate an email address according to RFCs 5321, 5322 and others
 *
 * Copyright © 2008-2011, Dominic Sayers
 * Test schema documentation Copyright © 2011, Daniel Marschall
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 *     - Redistributions of source code must retain the above copyright notice,
 *       this list of conditions and the following disclaimer.
 *     - Redistributions in binary form must reproduce the above copyright notice,
 *       this list of conditions and the following disclaimer in the documentation
 *       and/or other materials provided with the distribution.
 *     - Neither the name of Dominic Sayers nor the names of its contributors may be
 *       used to endorse or promote products derived from this software without
 *       specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * @package    is_email
 * @author    Dominic Sayers <dominic@sayers.cc>
 * @copyright    2008-2011 Dominic Sayers
 * @license    http:#www.opensource.org/licenses/bsd-license.php BSD License
 * @link    http:#www.dominicsayers.com/isemail
 * @version    3.04.1 - Changed my link to http:#isemail.info throughout

Based on the above source, converted to Python by Dan Strohl
"""
'''
# Categories
ISEMAIL_VALID_CATEGORY = 1
ISEMAIL_DNSWARN = 7
ISEMAIL_RFC5321 = 15
ISEMAIL_CFWS = 31
ISEMAIL_DEPREC = 63
ISEMAIL_RFC5322 = 127
ISEMAIL_ERR = 255

# Diagnoses
# Address is valid
ISEMAIL_VALID = 0
# Address is valid but a DNS check was not successful
ISEMAIL_DNSWARN_NO_MX_RECORD = 5
ISEMAIL_DNSWARN_NO_RECORD = 6
# Address is valid for SMTP but has unusual elements
ISEMAIL_RFC5321_TLD = 9
ISEMAIL_RFC5321_TLDNUMERIC = 10
ISEMAIL_RFC5321_QUOTEDSTRING = 11
ISEMAIL_RFC5321_ADDRESSLITERAL = 12
ISEMAIL_RFC5321_IPV6DEPRECATED = 13
# Address is valid within the message but cannot be used unmodified for the envelope
ISEMAIL_CFWS_COMMENT = 17
ISEMAIL_CFWS_FWS = 18
# Address contains deprecated elements but may still be valid in restricted contexts
ISEMAIL_DEPREC_LOCALPART = 33
ISEMAIL_DEPREC_FWS = 34
ISEMAIL_DEPREC_QTEXT = 35
ISEMAIL_DEPREC_QP = 36
ISEMAIL_DEPREC_COMMENT = 37
ISEMAIL_DEPREC_CTEXT = 38
ISEMAIL_DEPREC_CFWS_NEAR_AT = 49
# The address is only valid according to the broad definition of RFC 5322. It is otherwise invalid.
ISEMAIL_RFC5322_DOMAIN = 65
ISEMAIL_RFC5322_TOOLONG = 66
ISEMAIL_RFC5322_LOCAL_TOOLONG = 67
ISEMAIL_RFC5322_DOMAIN_TOOLONG = 68
ISEMAIL_RFC5322_LABEL_TOOLONG = 69
ISEMAIL_RFC5322_DOMAINLITERAL = 70
ISEMAIL_RFC5322_DOMLIT_OBSDTEXT = 71
ISEMAIL_RFC5322_IPV6_GRPCOUNT = 72
ISEMAIL_RFC5322_IPV6_2X2XCOLON = 73
ISEMAIL_RFC5322_IPV6_BADCHAR = 74
ISEMAIL_RFC5322_IPV6_MAXGRPS = 75
ISEMAIL_RFC5322_IPV6_COLONSTRT = 76
ISEMAIL_RFC5322_IPV6_COLONEND = 77
# Address is invalid for any purpose
ISEMAIL_ERR_EXPECTING_DTEXT = 129
ISEMAIL_ERR_NOLOCALPART = 130
ISEMAIL_ERR_NODOMAIN = 131
ISEMAIL_ERR_CONSECUTIVEDOTS = 132
ISEMAIL_ERR_ATEXT_AFTER_CFWS = 133
ISEMAIL_ERR_ATEXT_AFTER_QS = 134
ISEMAIL_ERR_ATEXT_AFTER_DOMLIT = 135
ISEMAIL_ERR_EXPECTING_QPAIR = 136
ISEMAIL_ERR_EXPECTING_ATEXT = 137
ISEMAIL_ERR_EXPECTING_QTEXT = 138
ISEMAIL_ERR_EXPECTING_CTEXT = 139
ISEMAIL_ERR_BACKSLASHEND = 140
ISEMAIL_ERR_DOT_START = 141
ISEMAIL_ERR_DOT_END = 142
ISEMAIL_ERR_DOMAINHYPHENSTART = 143
ISEMAIL_ERR_DOMAINHYPHENEND = 144
ISEMAIL_ERR_UNCLOSEDQUOTEDSTR = 145
ISEMAIL_ERR_UNCLOSEDCOMMENT = 146
ISEMAIL_ERR_UNCLOSEDDOMLIT = 147
ISEMAIL_ERR_FWS_CRLF_X2 = 148
ISEMAIL_ERR_FWS_CRLF_END = 149
ISEMAIL_ERR_CR_NO_LF = 150
# End of generated code
# :diagnostic constants end:
'''

# function control
ISEMAIL_MIN_THRESHOLD = 16
ISEMAIL_MAX_THREASHOLD = 255

# Miscellaneous string constants

obs_no_ws_ctl = make_char_str((1, 8), 11, 12, (14, 31), 127)

ISEMAIL_CONSTANTS = dict(
    AT='@',
    BACKSLASH='\\',
    DOT='.',
    DQUOTE='"',
    OPENPARENTHESIS='(',
    CLOSEPARENTHESIS=')',
    OPENSQBRACKET='[',
    CLOSESQBRACKET=']',
    HYPHEN='-',
    COLON=':',
    DOUBLECOLON='::',
    SP=' ',
    HTAB="\t",
    CR="\r",
    LF="\n",
    IPV6TAG='ipv6:',

    # US-ASCII visible characters not valid for atext (http:#tools.ietf.org/html/rfc5322#section-3.2.3)

    SPECIALS='()<>[]:;@\\,."',
    WSP=' \t',
    CRLF='\r\n',
    OBS_NO_WS_CTL=make_char_str((1, 8), 11, 12, (14, 31), 127),
    CTEXT=make_char_str((33, 39), (42, 91), 93, 126, obs_no_ws_ctl),
    OBS_CTEXT=obs_no_ws_ctl,
    OBS_QTEXT=obs_no_ws_ctl,
    QTEXT=make_char_str(33, (35, 91), (93, 126), obs_no_ws_ctl),
    VTEXT=make_char_str((33, 126)),
    OBS_DTEXT=obs_no_ws_ctl,
    DCONTENT=make_char_str((33, 90), (94, 126)),
    DTEXT=make_char_str((33, 90), (94, 126), obs_no_ws_ctl),
    OBS_QP=make_char_str(0, obs_no_ws_ctl, '\r', '\n'),
    LTR_STR=make_char_str((68, 90), (48, 57), (97, 122)),
    ATEXT=make_char_str((68, 90), (48, 57), (97, 122), "!#$%&'*+-=?^_`{|}~"),
    DIGIT='1234567890',
    HEXDIG='1234567890abcdefABCDEF',
    IPV4_12='12',
    IPV4_05='012345',
    IPV4_04='01234',
    IPV4_19='123456789',
    REPEAT_FLAGS='1234567890*',
)

# Element types

ISEMAIL_ELEMENT_LOCALPART = 'local_part'
ISEMAIL_ELEMENT_LOCAL_COMMENT = 'comment'
ISEMAIL_ELEMENT_LOCAL_QUOTEDSTRING = 'local_quoted_string'

ISEMAIL_ELEMENT_DOMAINPART = 'domain_part'
ISEMAIL_ELEMENT_DOMAIN_COMMENT = 'domain_comment'
ISEMAIL_ELEMENT_DOMAIN_QUOTEDSTRING = 'domain_quoted_string'
ISEMAIL_ELEMENT_DOMAIN_LIT_IPV4 = 'domain_ipv4_literal'
ISEMAIL_ELEMENT_DOMAIN_LIT_IPV6 = 'domain_ipv6_literal'
ISEMAIL_ELEMENT_DOMAIN_LIT_GEN = 'domain_general_literal'

# ISEMAIL_IP_REGEX = re.compile(r'(?P<address>(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
# ISEMAIL_IP_REGEX_GOOD_CHAR = re.compile(r'^[0-9A-Fa-f]{0,4}$')


ISEMAIL_MAX_COUNT = 9999
ISEMAIL_MIN_COUNT = 0




EMAIL_PARSER_RULES = dict(

    addr_spec=_and(
        # local-part "@" domain
        _m('local_part', on_fail='ERR_NO_LOCAL_PART', element_name=ISEMAIL_ELEMENT_LOCALPART),
        '1@',
        _m('domain_part', on_fail='ERR_NO_DOMAIN_PART', element_name=ISEMAIL_ELEMENT_DOMAINPART)),

    local_part=_or(
        _m('dot_atom', element_name=ISEMAIL_ELEMENT_LOCALPART, return_string=True),
        _m('quoted_string', on_pass='RFC5321_QUOTED_STRING', return_string=True),
        _m('obs_local_part', on_pass='DEPREC_LOCAL_PART', return_string=True)),

    domain_part=_or(
        # dot-atom / address-literal / obs-domain
        'dot_atom', 'address_literal', 'domain_literal', 'obs_domain'),

    dot_atom=_and(
        # [CFWS] dot-atom-text [CFWS]
        _m('[cfws]', return_string=False),
        _m('dot_atom_text', return_string=True),
        _m('[cfws]', return_string=False)),

    quoted_string=_m(
        # [CFWS] DQUOTE *([FWS] qcontent) [FWS] DQUOTE [CFWS]
        _and(
            _m('[cfws]', return_string=False),
            _m('"', return_string=False),
            _c('*', _and(
                    'fws',
                    _m('qcontent', return_string=True))),
            _m('[fws]', return_string=False),
            _m('"', on_fail='UNCLOSED_QUOTED_STR', return_string=False),
            _m('[cfws]', return_string=False)),
        on_pass='QUOTED_STR', return_string=True),

    obs_local_part=_and(
        # word *("." word)
        'word',
        _c('*', _and(
            '.',
            'word'))),

    cfws=_or(
        # (1*([FWS] comment) [FWS]) / FWS
        _c('1*', _and(
            _m('[fws]', return_string=False),
            _m('comment', return_string=True),
            _m('[fws]', return_string=False))),
        _m('fws', return_string=False)),

    fws=_or(
        # ([*WSP CRLF] 1*WSP) /  obs-FWS
        _and(
            _opt(
                _and(
                    _c('*', 'wsp'),
                    'crlf')),
            _c('1*', 'wsp')),
        _m('obs_fws', on_pass='DEPREC_FWS')),

    obs_fws=_c(
        # 1*([CRLF] WSP)
        '1*',
        _and(
            '[crlf]',
            'wsp')),

    ccontent=_or(
        # ctext / quoted-pair / comment
        _m('ctext', return_string=True),
        _m('quoted_pair', return_string=True, on_pass='QUOTED_PAIR'),
        _m('comment', return_string=True)),

    comment=_and(
        #  "(" *([FWS] ccontent) [FWS] ")"
        '(',
        _c('*',
           _and(
                _m('[fws]', return_string=False),
                'ccontent',
                _m('[fws]', return_string=False))),
        _m(')', on_fail='UNCLOSED_COMMENT')),

    dot_atom_text=_and(
        # 1*atext *("." 1*atext)
        'atext',
        _and(
            '.',
            'atext')),

    qcontent=_or(
        # qtext / quoted-pair
        'qtext',
        'quoted_pair'),

    quoted_pair=_or(
        # ("\" (VCHAR / WSP)) / obs-qp
        _and(
            '\\',
            _or(
                'vchar',
                'wsp')),
        'obs_gp'),

    obs_gp=_and(
        # "\" (%d0 / obs-NO-WS-CTL / LF / CR)
        '\\',
        _m('OBS_QP', element_name=ISEMAIL_ELEMENT_LOCAL_QUOTEDSTRING, on_pass='OBS_QP')),

    word=_or(
        # atom / quoted-string
        'atom', 'quoted_string'),

    atom=_and(
        # [CFWS] 1*atext [CFWS]
        _opt('cfws'),
        'atext',
        '[cfws]'),

    domain_literal=_m(
        # [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
        _and(
            '[cfws]',
            '[',
            _and(
                '[fws]',
                'dtext'),
            '[fws]',
            ']',
            '[cfws]'),
        on_pass='DOMAIN_LITERAL'),

    dtext=_or(
        #    %d33-90 /          ; Printable US-ASCII
        #    %d94-126 /         ;  characters not including
        #    obs-dtext          ;  "[", "]", or "\"

        #    obs-dtext       =   obs-NO-WS-CTL / quoted-pair
        'DTEXT',
        'quoted_pair'),

    obs_domain=_and(
        # atom *("." atom)
        'atom',
        _c('*',
           _and(
                '.',
                'atom'))),

    address_literal=
        """
            "[" ( IPv4-address-literal /
            IPv6-address-literal /
            General-address-literal ) "]"
        :return:
        """
        tmp_ret = self._get(_and('[', _or('ipv4_address_literal', 'ipv6_address_literal', 'general_address_literal'), ']'))
        self._add_response('RFC5321_ADDRESS_LITERAL')
        return tmp_ret

    ipv4_address_literal=
        """
            Snum 3("."  Snum)
        """
        tmp_ret = self._get(_and('snum', _c('3', _and('.', 'snum'))))
        if tmp_ret:
            self._add_element(ISEMAIL_ELEMENT_DOMAIN_LIT_IPV4)
            self._add_response('DOMAIN_LIT_IPV4')

    snum=
        """
            1*3DIGIT
                ; representing a decimal integer
                ; value in the range 0 through 255
        """
        tmp_ret = self._get(_or(
            'IPV4_19',
            _and('IPV4_19', 'DIGIT'),
            _or(
                _and('1', 'DIGIT', 'DIGIT'),
                _and('2', 'IPV4_04', 'DIGIT'),
                _and('2', '5', 'IPV4_05'),
            )))
        return tmp_ret

    ipv6_address_literal=
        """
            "IPv6:" IPv6-addr
        """
        return self._get(_and('IPv6:', 'ipv6_addr'))

    ipv6_addr=
        """
            IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp
        """
        tmp_ret = self._get(_or('ipv6_full', 'ipv6_comp', 'ipv6v4_full', 'ipv6v4_comp'))

        # TODO: Validate IPv6 Address

        self._add_element(ISEMAIL_ELEMENT_DOMAIN_LIT_IPV6, tmp_ret)
        return tmp_ret

    ipv6_full=
        """
        IPv6-hex 7(":" IPv6-hex)
        """
        return self._get(_and('ipv6_hex', _c(7, _and(':', 'ipv6_hex'))))

    ipv6_comp=
        """
        [IPv6-hex *5(":" IPv6-hex)] "::" [IPv6-hex *5(":" IPv6-hex)]

              ; The "::" represents at least 2 16-bit groups of
              ; zeros.  No more than 6 groups in addition to the
              ; "::" may be present.
        """
        return self._get(_and(
            'ipv6_hex', _c('*5', _and(':', 'ipv6_hex')),
            '::',
            'ipv6_hex', _c('*5', _and(':', 'ipv6_hex')))),


    ipv6v4_full=
        """
        IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal
        """
        return self._get(_and('ipv6_hex', _c(5, _and(':', 'ipv6_hex')), 'ipv4_address_literal'))

    ipv6v4_comp=
        """
        [IPv6-hex *3(":" IPv6-hex)] "::" [IPv6-hex *3(":" IPv6-hex) ":"] IPv4-address-literal
              ; The "::" represents at least 2 16-bit groups of
              ; zeros.  No more than 4 groups in addition to the
              ; "::" and IPv4-address-literal may be present.
        """
        return self._get(_and(
            'ipv6_hex', _c('*2', _and(':', 'ipv6_hex')),
            '::',
            'ipv6_hex', _c('*2', _and(':', 'ipv6_hex')),'ipv4_address_literal')),


    ipv6_hex=
        tmp_ret = self._get(
            _or(
                _c(1, 'HEXDIG'),
                _c(2, 'HEXDIG'),
                _c(3, 'HEXDIG'),
                _c(4, 'HEXDIG'))
        )
        return tmp_ret

    general_address_literal=
        """
        Ldh-str ":" 1*dcontent
        """
        tmp_ret = self._get(_and(
            _c('*', 'LTR_STR'),
            ':',
            _c('*', 'dcontent')
        ))
        return tmp_ret



)


'''
class MetaInfo(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __int__(self):
        try:
            return self.value
        except AttributeError:
            return 0
'''

class MetaList(object):
    def __init__(self, dict_in):
        self._by_value = {}
        self._by_key = {}
        for key, item in dict_in.items():
            item['key'] = key
            self._by_key[key] = item
            try:
                self._by_value[item['value']] = item
            except KeyError:
                pass

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._by_key[item]
        else:
            return self._by_value[item]


class MetaLookup(object):
    def __init__(self, categories, smtp, diags, references):
        self.cat = MetaList(categories)
        self.smtp = MetaList(smtp)
        self.diags = MetaList(diags)
        self.ref = MetaList(references)

    def __getitem__(self, item):
        return self.diags[item]

# <Categories>
ISEMAIL_RESP_CATEGORIES = dict(
    ISEMAIL_VALID_CATEGORY=dict(
        name='Valid Address',
        value=1,
        description="Address is valid"),
    ISEMAIL_DNSWARN = dict(
        name='Valid Address (DNS Warning)',
        value=7,
        description="Address is valid but a DNS check was not successful"),

    ISEMAIL_RFC5321 = dict(
        name='Valid Address (unusual)',
        value=15,
        description="Address is valid for SMTP but has unusual elements"),

    ISEMAIL_CFWS = dict(
        name='Valid Address (limited use)',
        value=31,
        description="Address is valid within the message but cannot be used unmodified for the envelope"),

    ISEMAIL_DEPREC = dict(
        name='Valid Address (deprecated)',
        value=63,
        description="Address contains deprecated elements but may still be valid in restricted contexts"),

    ISEMAIL_RFC5322 = dict(
        name='Valid Address (unusable)',
        value=127,
        description="The address is only valid according to the broad definition of RFC 5322. It is otherwise invalid."),

    ISEMAIL_ERR = dict(
        name='Invalid Address',
        value=255,
        description="Address is invalid for any purpose"),
)
# <SMTP>
ISEMAIL_META_SMTP_RESP = {
    '2.1.5': {'value': 0, 'description': "250 2.1.5 ok"},
    '5.1.0': {'value': 0, 'description': "553 5.1.0 Other address status"},
    '5.1.1': {'value': 0, 'description': "553 5.1.1 Bad destination mailbox address"},
    '5.1.2': {'value': 0, 'description': "553 5.1.2 Bad destination system address"},
    '5.1.3': {'value': 0, 'description': "553 5.1.3 Bad destination mailbox address syntax"}}


# <editor-fold desc="References">
# 	<References>
ISEMAIL_META_REFERENCES = {
    "local-part": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote = ''
            ''
            'local-part      =   dot-atom / quoted-string / obs-local-part'
            ''
            'dot-atom        =   [CFWS] dot-atom-text [CFWS]'
            ''
            'dot-atom-text   =   1*atext *("." 1*atext)'
            ''
            'quoted-string   =   [CFWS]'
            '                    DQUOTE *([FWS] qcontent) [FWS] DQUOTE'
            '                    [CFWS]'
            ''
            'obs-local-part  =   word *("." word)'
            ''
            'word            =   atom / quoted-string'
            ''
            'atom            =   [CFWS] 1*atext [CFWS]',
        cite="RFC 5322 section 3.4.1"),

    "local-part-maximum": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.5.3.1.1",
        blockquote=''
            'The maximum total length of a user name or other local-part is 64'
            'octets.',
        cite='RFC 5322 section 4.5.3.1.1'),

    "obs-local-part": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'obs-local-part  =   word *("." word)'
            ''
            'word            =   atom / quoted-string'
            ''
            'atom            =   [CFWS] 1*atext [CFWS]'
            ''
            'quoted-string   =   [CFWS]'
            '                   DQUOTE *([FWS] qcontent) [FWS] DQUOTE'
            '                   [CFWS]',
        cite='RFC 5322 section 3.4.1'),

    "dot-atom": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'dot-atom        =   [CFWS] dot-atom-text [CFWS]'
            ''
            'dot-atom-text   =   1*atext *("." 1*atext)',
        cite='RFC 5322 section 3.4.1'),

    "quoted-string": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'quoted-string   =   [CFWS]'
            '                   DQUOTE *([FWS] qcontent) [FWS] DQUOTE'
            '                   [CFWS]'
            ''
            'qcontent        =   qtext / quoted-pair'
            ''
            'qtext           =   %d33 /             ; Printable US-ASCII'
            '                   %d35-91 /          ;  characters not including'
            '                   %d93-126 /         ;  "\" or the quote character'
            '                   obs-qtext'
            ''
            'quoted-pair     =   ("\" (VCHAR / WSP)) / obs-qp',
        cite='RFC 5322 section 3.4.1'),

    "CFWS-near-at": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'Comments and folding white space'
            'SHOULD NOT be used around the "@" in the addr-spec.',
        cite='RFC 5322 section 3.4.1'),

    "SHOULD-NOT": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc2119",
        blockquote=''
            '4. SHOULD NOT   This phrase, or the phrase "NOT RECOMMENDED" mean that'
            '   there may exist valid reasons in particular circumstances when the'
            '   particular behavior is acceptable or even useful, but the full'
            '   implications should be understood and the case carefully weighed'
            '   before implementing any behavior described with this label.',

        cite='RFC 2119 section 4'),

    "atext": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.2.3",
        blockquote=''
            'atext           =   ALPHA / DIGIT /    ; Printable US-ASCII'
            '                    "!" / "#" /        ;  characters not including'
            '                    "$" / "%" /        ;  specials.  Used for atoms.'
            '                    "&amp;" / "\'" /'
            '                    "*" / "+" /'
            '                    "-" / "/" /'
            '                    "=" / "?" /'
            '                    "^" / "_" /'
            '                    "`" / "{" /'
            '                    "|" / "}" /'
            '                    "~"',
        cite='RFC 5322 section 3.2.3'),

    "obs-domain": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'obs-domain      =   atom *("." atom)'
            ''
            'atom            =   [CFWS] 1*atext [CFWS]',
        cite='RFC 5322 section 3.4.1'),

    "domain-RFC5322": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'domain          =   dot-atom / domain-literal / obs-domain'
            ''
            'dot-atom        =   [CFWS] dot-atom-text [CFWS]'
            ''
            'dot-atom-text   =   1*atext *("." 1*atext)',
        cite='RFC 5322 section 3.4.1'),

    "domain-RFC5321": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.2",
        blockquote=''
            '   Domain         = sub-domain *("." sub-domain)',
        cite='RFC 5321 section 4.1.2'),
    "sub-domain": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.2",
        blockquote=''
            'Domain         = sub-domain *("." sub-domain)'
            ''
            'Let-dig        = ALPHA / DIGIT'
            ''
            'Ldh-str        = *( ALPHA / DIGIT / "-" ) Let-dig',
        cite='RFC 5321 section 4.1.2'),

    "label": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc1035#section-2.3.4",
        blockquote=''
            '   labels          63 octets or less',
        cite='RFC 5321 section 4.1.2'),

    "CRLF": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5234#section-2.3",
        blockquote='CRLF        =  %d13.10',
        cite='RFC 5234 section 2.3'),

    "CFWS": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.2.2",
        blockquote=''
            'CFWS            =   (1*([FWS] comment) [FWS]) / FWS'
            ''
            'FWS             =   ([*WSP CRLF] 1*WSP) /  obs-FWS'
            '                                      ; Folding white space'
            ''
            'comment         =   "(" *([FWS] ccontent) [FWS] ")"'
            ''
            'ccontent        =   ctext / quoted-pair / comment'
            ''
            'ctext           =   %d33-39 /          ; Printable US-ASCII'
            '                   %d42-91 /          ;  characters not including'
            '                   %d93-126 /         ;  "(", ")", or "\"'
            '                   obs-ctext',

        cite='RFC 5322 section 3.2.2'),

    "domain-literal": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote='domain-literal  =   [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]',
        cite='RFC 5322 section 3.4.1'),

    "address-literal": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.2",
        blockquote=''
            'address-literal  = "[" ( IPv4-address-literal /'
            '                IPv6-address-literal /'
            '                General-address-literal ) "]"',
        cite='RFC 5321 section 4.1.2'),

    "address-literal-IPv4": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.3",
        blockquote=''
            'IPv4-address-literal  = Snum 3("."  Snum)'
            ''
            'Snum           = 1*3DIGIT'
            '              ; representing a decimal integer'
            '              ; value in the range 0 through 255',
        cite='RFC 5321 section 4.1.3'),

    "address-literal-IPv6": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.3",
        blockquote=''
            'IPv6-address-literal  = "IPv6:" IPv6-addr'
            ''
            'IPv6-addr      = IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp'
            ''
            'IPv6-hex       = 1*4HEXDIG'
            ''
            'IPv6-full      = IPv6-hex 7(":" IPv6-hex)'
            ''
            'IPv6-comp      = [IPv6-hex *5(":" IPv6-hex)] "::"'
            '              [IPv6-hex *5(":" IPv6-hex)]'
            '              ; The "::" represents at least 2 16-bit groups of'
            '              ; zeros.  No more than 6 groups in addition to the'
            '              ; "::" may be present.'
            ''
            'IPv6v4-full    = IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal'
            ''
            'IPv6v4-comp    = [IPv6-hex *3(":" IPv6-hex)] "::"'
            '              [IPv6-hex *3(":" IPv6-hex) ":"]'
            '              IPv4-address-literal'
            '              ; The "::" represents at least 2 16-bit groups of'
            '              ; zeros.  No more than 4 groups in addition to the'
            '              ; "::" and IPv4-address-literal may be present.',
        cite='RFC 5321 section 4.1.3'),

    "dtext": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'dtext           =   %d33-90 /          ; Printable US-ASCII'
            '                     %d94-126 /         ;  characters not including'
            '                     obs-dtext          ;  "[", "]", or "\"',
        cite='RFC 5322 section 3.4.1'),

    "obs-dtext": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'obs-dtext       =   obs-NO-WS-CTL / quoted-pair'
            ''
            'obs-NO-WS-CTL   =   %d1-8 /            ; US-ASCII control'
            '                   %d11 /             ;  characters that do not'
            '                   %d12 /             ;  include the carriage'
            '                   %d14-31 /          ;  return, line feed, and'
            '                   %d127              ;  white space characters',
        cite='RFC 5322 section 3.4.1'),

    "qtext": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.2.4",
        blockquote=''
            'qtext           =   %d33 /             ; Printable US-ASCII'
            '                   %d35-91 /          ;  characters not including'
            '                   %d93-126 /         ;  "\" or the quote character'
            '                   obs-qtext',
        cite='RFC 5322 section 3.2.4'),

    "obs-qtext": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-4.1",
        blockquote=''
            'obs-qtext       =   obs-NO-WS-CTL'
            ''
            'obs-NO-WS-CTL   =   %d1-8 /            ; US-ASCII control'
            '                   %d11 /             ;  characters that do not'
            '                   %d12 /             ;  include the carriage'
            '                   %d14-31 /          ;  return, line feed, and'
            '                   %d127              ;  white space characters',
        cite='RFC 5322 section 4.1'),

    "ctext": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.2.3",
        blockquote=''
            'ctext           =   %d33-39 /          ; Printable US-ASCII'
            '                   %d42-91 /          ;  characters not including'
            '                   %d93-126 /         ;  "(", ")", or "\"'
            '                   obs-ctext',
        cite='RFC 5322 section 3.2.3'),

    "obs-ctext": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-4.1",
        blockquote=''
            'obs-qtext       =   obs-NO-WS-CTL'
            ''
            'obs-NO-WS-CTL   =   %d1-8 /            ; US-ASCII control'
            '                   %d11 /             ;  characters that do not'
            '                   %d12 /             ;  include the carriage'
            '                   %d14-31 /          ;  return, line feed, and'
            '                   %d127              ;  white space characters',
        cite='RFC 5322 section 4.1'),

    "quoted-pair": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.2.1",
        blockquote=''
            'quoted-pair     =   ("\" (VCHAR / WSP)) / obs-qp'
            ''
            'VCHAR           =  %d33-126            ; visible (printing) characters'
            'WSP             =  SP / HTAB           ; white space',
        cite='RFC 5322 section 3.2.1'),

    "obs-qp": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-4.1",
        blockquote=''
            'obs-qp          =   "\" (%d0 / obs-NO-WS-CTL / LF / CR)'
            ''
            'obs-NO-WS-CTL   =   %d1-8 /            ; US-ASCII control'
            '                   %d11 /             ;  characters that do not'
            '                   %d12 /             ;  include the carriage'
            '                   %d14-31 /          ;  return, line feed, and'
            '                   %d127              ;  white space characters',
        cite='RFC 5322 section 4.1'),

    "TLD": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-2.3.5",
        blockquote=''
            'In the case'
            'of a top-level domain used by itself in an email address, a single'
            'string is used without any dots.  This makes the requirement,'
            'described in more detail below, that only fully-qualified domain'
            'names appear in SMTP transactions on the public Internet,'
            'particularly important where top-level domains are involved.',
        cite='RFC 5321 section 2.3.5'),

    "TLD-format": dict(
        blockquote_cite="http://www.rfc-editor.org/errata_search.php?eid=1353",
        blockquote=''
            'Errata ID 1081, reported 2007-11-20, identifies a problem with the'
            'evolution of naming of top-level domains and the text of RFC 1123.'
            'It reads:'
            ''
            'Section 2.1 says:'
            ''
            '                       However, a valid host name can never'
            'have the dotted-decimal form #.#.#.#, since at least the'
            'highest-level component label will be alphabetic.'
            ''
            'It should say:'
            ''
            '                       However, a valid host name can never'
            'have the dotted-decimal form #.#.#.#, since at least the'
            'highest-level component label will be not all-numeric.'
            ''
            'Notes:'
            ''
            'RFC 3696 section 2 states: "There is an additional rule that'
            'essentially requires that top-level domain names not be'
            'all-numeric." The eleven IDN test TLDs created in'
            'September 2007 contain hyphen-minus as specified in the'
            'IDNA RFCs.'
            'It should say:'
            ''
            'However, a valid host name can never have the dotted-decimal'
            'form #.#.#.#, since this change does not permit the highest-level'
            'component label to start with a digit even if it is not all-numeric.'
            'Notes:'
            ''
            'This is a correct identification of the problem, but the wrong fix.'
            'RFC 3696, which ID 1081 cites, is an informational document that is'
            'deliberately relaxed about the fine details and says so. It is not'
            'relevant to determination of the text that should have been (with'
            'perfect knowledge of the future) in 1123.'
            ''
            'Based on discussions when we were doing RFC 1591 and subsequently,'
            'the expectation then (and presumably when 1123 was written) was'
            'that the name of any new TLD would follow the rules for the'
            'existing ones, i.e., that they would be exactly two or three'
            'characters long and be all-alphabetic (which is exactly what 1123'
            'says). The slightly-odd "will be" language in 1123 was, I believe,'
            'because that restriction was expected to be enforced by IANA,'
            'rather than being a protocol issue. ICANN, with a different set of'
            'assignment policies, effectively eliminated the length rule with'
            'the TLDs allocated in 2000. IDNA (RFC 3490) uses a syntax for IDNs'
            'that requires embedded hyphens in TLDs if there were ever to be an'
            'actual IDN TLD (hence the comment in ID 1081 about the IANA IDN'
            'testbed).'
            ''
            'While the proposed correction in Errata ID 1081 would fix the'
            'problem by imposing the narrowest possible restriction ("not'
            'all-numeric"), the original host name rule and the original'
            'statement in 1123 both assume the possibility of a minimal check'
            'to differentiate between domain names and IP addresses, i.e.,'
            'checking the first digit only. Because I believe that there are'
            'probably implementations that depend on such minimal parsing --some'
            'probably ancient and embedded-- it would appear to be wise to relax'
            'the rule as little as possible and, in particular, to restrict the'
            '"leading digit" exception to domains below the top-level, as 1123'
            'effectively does.'
            ''
            'The suggested text above reflects that reasoning. Because of the'
            'possible consequences of this issue, I would hope that it would be'
            'discussed with the relevant DNS-related WGs, the Root Server Advisory'
            'Committee (RSAC), and with IANA for comment and as a heads-up. This'
            'issue is substantive enough that it should probably be dealt with by'
            'a document that explicitly updates 1123 and that is processed on the'
            'Standards Track, but an accurate statement in the errata is the'
            'next-best option until that can be done. In the interim and while'
            'this suggestion is being discussed, Errata ID 1081 should probably'
            'be taken out of "validated" status.'
            '',
        cite='John Klensin, RFC 1123 erratum 1353'),

    "mailbox-maximum": dict(
        blockquote_cite="http://www.rfc-editor.org/errata_search.php?eid=1690",
        blockquote=''
            'However, there is a restriction in RFC 2821 on the length of an'
            'address in MAIL and RCPT commands of 254 characters.  Since addresses'
            'that do not fit in those fields are not normally useful, the upper'
            'limit on address lengths should normally be considered to be 254.',
        cite='Dominic Sayers, RFC 3696 erratum 1690'),

    "domain-maximum": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc1035#section-4.5.3.1.2",
        blockquote='The maximum total length of a domain name or number is 255 octets.',
        cite='RFC 5321 section 4.5.3.1.2'),

    "mailbox": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.2",
        blockquote='Mailbox        = Local-part "@" ( Domain / address-literal )',
        cite='RFC 5321 section 4.1.2'),

    "addr-spec": dict(
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote='addr-spec       =   local-part "@" domain',
        cite='RFC 5322 section 3.4.1'),
}
# </editor-fold>

# ------------------------------------------------------------------------
# Diagnoses
# ------------------------------------------------------------------------

ISEMAIL_DIAG_RESPONSES = dict(

    VALID=dict(
        value=0,
        description='Valid Email',
        category='VALID_CATEGORY',
        longdescription="Address is valid. Please note that this does not mean the address actually exists, nor even that the"
                    " domain actually exists. This address could be issued by the domain owner without breaking the rules"
                    " of any RFCs.",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
    ),
    DNSWARN_NO_MX_RECORD=dict(
        value=5,
        category='DNSWARN',
        description="Couldn't find an MX record for this domain but an A-record does exist",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
    ),
    DNSWARN_NO_RECORD=dict(
        value=6,
        category='DNSWARN',
        description="Couldn't find an MX record or an A-record for this domain",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
    ),
    RFC5321_TLD=dict(
        value=9,
        category='RFC5321',
        description="Address is valid but at a Top Level Domain",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['TLD'],
    ),
    RFC5321_TLD_NUMERIC=dict(
        value=10,
        category='RFC5321',
        description="Address is valid but the Top Level Domain begins with a number",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['TLD-format'],
    ),
    RFC5321_QUOTED_STRING=dict(
        value=11,
        category='RFC5321',
        description="Address is valid but contains a quoted string",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['quoted-string'],
    ),
    RFC5321_ADDRESS_LITERAL=dict(
        value=12,
        category='RFC5321',
        description="Address is valid but at a literal address not a domain",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=(ISEMAIL_META_REFERENCES['address-literal'], ISEMAIL_META_REFERENCES['address-literal-IPv4'])
    ),
    RFC5321_IPV6_DEPRECATED=dict(
        value=13,
        category='DEPREC',
        description="Address is valid but contains a :: that only elides one zero group. All implementations must accept"
                    " and be able to handle any legitimate RFC 4291 format.",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    CFWS_COMMENT=dict(
        value=17,
        category='CFWS',
        description="Address contains comments",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['dot-atom'],
    ),
    CFWS_FWS=dict(
        value=18,
        category='CFWS',
        description="Address contains FWS",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['local-part'],
    ),
    DEPREC_LOCAL_PART=dict(
        value=33,
        category='DEPREC',
        description="The local part is in a deprecated form",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['obs-local-part'],
    ),
    DEPREC_FWS=dict(
        value=34,
        category='DEPREC',
        description="Address contains an obsolete form of Folding White Space",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=(ISEMAIL_META_REFERENCES['obs-local-part'], ISEMAIL_META_REFERENCES['obs-domain'])
    ),
    DEPREC_QTEXT=dict(
        value=35,
        category='DEPREC',
        description="A quoted string contains a deprecated character",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['obs-qtext'],
    ),
    DEPREC_QP=dict(
        value=36,
        category='DEPREC',
        description="A quoted pair contains a deprecated character",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['obs-qp'],
    ),
    DEPREC_COMMENT=dict(
        value=37,
        category='DEPREC',
        description="Address contains a comment in a position that is deprecated",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=(ISEMAIL_META_REFERENCES['obs-local-part'], ISEMAIL_META_REFERENCES['obs-domain'])
    ),
    DEPREC_CTEXT=dict(
        value=38,
        category='DEPREC',
        description="A comment contains a deprecated character",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['obs-ctext'],
    ),
    DEPREC_CFWS_NEAR_AT=dict(
        value=49,
        category='DEPREC',
        description="Address contains a comment or Folding White Space around the @ sign",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=(ISEMAIL_META_REFERENCES['CFWS-near-at'], ISEMAIL_META_REFERENCES['SHOULD-NOT'])
    ),
    RFC5322_DOMAIN=dict(
        value=65,
        category='RFC5322',
        description="Address is RFC 5322 compliant but contains domain characters that are not allowed by DNS",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['domain-RFC5322'],
    ),
    RFC5322_TOO_LONG=dict(
        value=66,
        category='RFC5322',
        description="Address is too long",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['mailbox-maximum'],
    ),
    RFC5322_LOCAL_TOO_LONG=dict(
        value=67,
        category='RFC5322',
        description="The local part of the address is too long",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['local-part-maximum'],
    ),
    RFC5322_DOMAIN_TOO_LONG=dict(
        value=68,
        category='RFC5322',
        description="The domain part is too long",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['domain-maximum'],
    ),
    RFC5322_LABEL_TOO_LONG=dict(
        value=69,
        category='RFC5322',
        description="The domain part contains an element that is too long",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['label'],
    ),
    RFC5322_DOMAIN_LITERAL=dict(
        value=70,
        category='RFC5322',
        description="The domain literal is not a valid RFC 5321 address literal",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['domain-literal'],
    ),
    RFC5322_DOM_LIT_OBS_DTEXT=dict(
        value=71,
        category='RFC5322',
        description="The domain literal is not a valid RFC 5321 address literal and it contains obsolete characters",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['obs-dtext'],
    ),
    RFC5322_IPV6_GRP_COUNT=dict(
        value=72,
        category='RFC5322',
        description="The IPv6 literal address contains the wrong number of groups",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_2X2X_COLON=dict(
        value=73,
        category='RFC5322',
        description="The IPv6 literal address contains too many :: sequences",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_BAD_CHAR=dict(
        value=74,
        category='RFC5322',
        description="The IPv6 address contains an illegal group of characters",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_MAX_GRPS=dict(
        value=75,
        category='RFC5322',
        description="The IPv6 address has too many groups",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_COLON_STRT=dict(
        value=76,
        category='RFC5322',
        description="IPv6 address starts with a single colon",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_COLON_END=dict(
        value=77,
        category='RFC5322',
        description="IPv6 address ends with a single colon",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    ERR_EXPECTING_DTEXT=dict(
        value=129,
        category='ERR',
        description="A domain literal contains a character that is not allowed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['dtext'],
    ),
    ERR_NO_LOCAL_PART=dict(
        value=130,
        category='ERR',
        description="Address has no local part",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['local-part'],
    ),
    ERR_NO_DOMAIN_PART=dict(
        value=131,
        category='ERR',
        description="Address has no domain part",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=(ISEMAIL_META_REFERENCES['addr-spec'], ISEMAIL_META_REFERENCES['mailbox'])
    ),
    ERR_CONSECUTIVE_DOTS=dict(
        value=132,
        category='ERR',
        description="The address may not contain consecutive dots",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=(
            ISEMAIL_META_REFERENCES['local-part'],
            ISEMAIL_META_REFERENCES['domain-RFC5322'],
            ISEMAIL_META_REFERENCES['domain-RFC5321'])
    ),
    ERR_ATEXT_AFTER_CFWS=dict(
        value=133,
        category='ERR',
        description="Address contains text after a comment or Folding White Space",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=(ISEMAIL_META_REFERENCES['local-part'], ISEMAIL_META_REFERENCES['domain-RFC5322'])
    ),
    ERR_ATEXT_AFTER_QS=dict(
        value=134,
        category='ERR',
        description="Address contains text after a quoted string",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['local-part'],
    ),
    ERR_ATEXT_AFTER_DOMLIT=dict(
        value=135,
        category='ERR',
        description="Extra characters were found after the end of the domain literal",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['domain-RFC5322'],
    ),
    ERR_EXPECTING_QPAIR=dict(
        value=136,
        category='ERR',
        description="The address contains a character that is not allowed in a quoted pair",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['quoted-pair'],
    ),
    ERR_EXPECTING_ATEXT=dict(
        value=137,
        category='ERR',
        description="Address contains a character that is not allowed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['atext'],
    ),
    ERR_EXPECTING_QTEXT=dict(
        value=138,
        category='ERR',
        description="A quoted string contains a character that is not allowed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['qtext'],
    ),
    ERR_EXPECTING_CTEXT=dict(
        value=139,
        category='ERR',
        description="A comment contains a character that is not allowed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['qtext'],
    ),
    ERR_BACKSLASH_END=dict(
        value=140,
        category='ERR',
        description="The address can't end with a backslash",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=(
            ISEMAIL_META_REFERENCES['domain-RFC5322'],
            ISEMAIL_META_REFERENCES['domain-RFC5321'],
            ISEMAIL_META_REFERENCES['quoted-pair'])
    ),
    ERR_DOT_START=dict(
        value=141,
        category='ERR',
        description="Neither part of the address may begin with a dot",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=(
            ISEMAIL_META_REFERENCES['local-part'],
            ISEMAIL_META_REFERENCES['domain-RFC5322'],
            ISEMAIL_META_REFERENCES['domain-RFC5321'])
    ),
    ERR_DOT_END=dict(
        value=142,
        category='ERR',
        description="Neither part of the address may end with a dot",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=(
            ISEMAIL_META_REFERENCES['local-part'],
            ISEMAIL_META_REFERENCES['domain-RFC5322'],
            ISEMAIL_META_REFERENCES['domain-RFC5321'])
    ),
    ERR_DOMAIN_HYPHEN_START=dict(
        value=143,
        category='ERR',
        description="A domain or subdomain cannot begin with a hyphen",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['sub-domain'],
    ),
    ERR_DOMAIN_HYPHEN_END=dict(
        value=144,
        category='ERR',
        description="A domain or subdomain cannot end with a hyphen",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['sub-domain'],
    ),
    ERR_UNCLOSED_QUOTED_STR=dict(
        value=145,
        category='ERR',
        description="Unclosed quoted string",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['quoted-string'],
    ),
    ERR_UNCLOSED_COMMENT=dict(
        value=146,
        category='ERR',
        description="Unclosed comment",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['CFWS'],
    ),
    ERR_UNCLOSED_DOM_LIT=dict(
        value=147,
        category='ERR',
        description="Domain literal is missing its closing bracket",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['domain-literal'],
    ),
    ERR_FWS_CRLF_X2=dict(
        value=148,
        category='ERR',
        description="Folding White Space contains consecutive CRLF sequences",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['CFWS'],
    ),
    ERR_FWS_CRLF_END=dict(
        value=149,
        category='ERR',
        description="Folding White Space ends with a CRLF sequence",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['CFWS'],
    ),
    ERR_CR_NO_LF=dict(
        value=150,
        category='ERR',
        description="Address contains a carriage return that is not followed by a line feed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=(ISEMAIL_META_REFERENCES['CFWS'], ISEMAIL_META_REFERENCES['CRLF'])
    ),
    ERR_NO_DOMAIN_SEP=dict(
        value=151,
        category='ERR',
        description="Address does not contain a domain seperator (@ sign)",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['domain-RFC5321']
    ),
    ERR_EMPTY_ADDRESS=dict(
        value=255,
        category='ERR',
        description="Empty Address Passed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['domain-RFC5321']
    ),

)

META_LOOKUP = MetaLookup(
    categories=ISEMAIL_RESP_CATEGORIES,
    smtp=ISEMAIL_META_SMTP_RESP,
    references=ISEMAIL_META_REFERENCES,
    diags=ISEMAIL_DIAG_RESPONSES,
)
