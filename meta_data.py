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
ISEMAIL_THRESHOLD = 16

# Email components
ISEMAIL_COMPONENT_LOCALPART = 0
ISEMAIL_COMPONENT_DOMAIN = 1

# Email context
ISEMAIL_COMPONENT_LITERAL = 2
ISEMAIL_CONTEXT_COMMENT = 3
ISEMAIL_CONTEXT_FWS = 4
ISEMAIL_CONTEXT_QUOTEDSTRING = 5
ISEMAIL_CONTEXT_QUOTEDPAIR = 6

# Miscellaneous string constants
ISEMAIL_STRING_AT = '@'
ISEMAIL_STRING_BACKSLASH = '\\'
ISEMAIL_STRING_DOT = '.'
ISEMAIL_STRING_DQUOTE = '"'
ISEMAIL_STRING_OPENPARENTHESIS = '('
ISEMAIL_STRING_CLOSEPARENTHESIS = ')'
ISEMAIL_STRING_OPENSQBRACKET = '['
ISEMAIL_STRING_CLOSESQBRACKET = ']'
ISEMAIL_STRING_HYPHEN = '-'
ISEMAIL_STRING_COLON = ':'
ISEMAIL_STRING_DOUBLECOLON = '::'
ISEMAIL_STRING_SP = ' '
ISEMAIL_STRING_HTAB = "\t"
ISEMAIL_STRING_CR = "\r"
ISEMAIL_STRING_LF = "\n"
ISEMAIL_STRING_IPV6TAG = 'ipv6:'

# US-ASCII visible characters not valid for atext (http:#tools.ietf.org/html/rfc5322#section-3.2.3)
ISEMAIL_SET_SPECIALS = '()<>[]:;@\\,."'
ISEMAIL_SET_WSP = ' \t'
ISEMAIL_SET_CRLF = '\r\n'
ISEMAIL_SET_OBS_NO_WS_CTL = make_char_str((1, 8), 11, 12, (14, 31), 127)
ISEMAIL_SET_CTEXT = make_char_str((33, 39), (42, 91), 93, 126, ISEMAIL_SET_OBS_NO_WS_CTL)
ISEMAIL_SET_OBS_CTEXT = ISEMAIL_SET_OBS_NO_WS_CTL
ISEMAIL_SET_OBS_QTEXT = ISEMAIL_SET_OBS_NO_WS_CTL
ISEMAIL_SET_QTEXT = make_char_str(33, (35, 91), (93, 126), ISEMAIL_SET_OBS_QTEXT)
ISEMAIL_SET_VTEXT = make_char_str((33, 126))
ISEMAIL_SET_OBS_DTEXT = ISEMAIL_SET_OBS_NO_WS_CTL
ISEMAIL_SET_DCONTENT = make_char_str((33, 90), (94, 126))
ISEMAIL_SET_DTEXT = make_char_str(ISEMAIL_SET_DCONTENT, ISEMAIL_SET_OBS_DTEXT)
ISEMAIL_SET_OBS_QP = make_char_str(0, ISEMAIL_SET_OBS_NO_WS_CTL, '\r', '\n' )
ISEMAIL_SET_LTR_STR = make_char_str((68, 90), (48, 57), (97, 122))
ISEMAIL_SET_ATEXT = make_char_str(ISEMAIL_SET_LTR_STR, "!#$%&'*+-=?^_`{|}~")
ISEMAIL_SET_DIGIT = '1234567890'
ISEMAIL_SET_HEXDIG = '1234567890abcdefABCDEF'
ISEMAIL_SET_IPV4_12 = '12'
ISEMAIL_SET_IPV4_05 = '012345'
ISEMAIL_SET_IPV4_04 = '01234'
ISEMAIL_SET_IPV4_19 = '123456789'
ISEMAIL_SET_COUNT = '1234567890*'


# State Flags
ISEMAIL_ELEMENT_BEG_ALL = 0
ISEMAIL_ELEMENT_BEG_ELEMENT = 1
ISEMAIL_ELEMENT_IN_ELEMENT = 2

# Element types
ISEMAIL_ELEMENT_LOCAL_DOT_ATOM = 0

ISEMAIL_DOMAIN_LIT_NONE = 0
ISEMAIL_DOMAIN_LIT_UNK = 1
ISEMAIL_DOMAIN_LIT_IPV4 = 4
ISEMAIL_DOMAIN_LIT_IPV6 = 6
ISEMAIL_DOMAIN_LIT_GEN = 99

ISEMAIL_IP_REGEX = re.compile(r'(?P<address>(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
ISEMAIL_IP_REGEX_GOOD_CHAR = re.compile(r'^[0-9A-Fa-f]{0,4}$')


ISEMAIL_MAX_COUNT = 9999
ISEMAIL_MIN_COUNT = 0

class MetaInfo(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __int__(self):
        try:
            return self.value
        except AttributeError:
            return 0

# <Categories>
ISEMAIL_VALID_CATEGORY = MetaInfo(
    value=1,
    description="Address is valid")

ISEMAIL_DNSWARN = MetaInfo(
    value=7,
    description="Address is valid but a DNS check was not successful")

ISEMAIL_RFC5321 = MetaInfo(
    value=15,
    description="Address is valid for SMTP but has unusual elements")

ISEMAIL_CFWS = MetaInfo(
    value=31,
    description="Address is valid within the message but cannot be used unmodified for the envelope")

ISEMAIL_DEPREC = MetaInfo(
    value=63,
    description="Address contains deprecated elements but may still be valid in restricted contexts")

ISEMAIL_RFC5322 = MetaInfo(
    value=127,
    description="The address is only valid according to the broad definition of RFC 5322. It is otherwise invalid.")

ISEMAIL_ERR = MetaInfo(
    value=255,
    description="Address is invalid for any purpose")


# <SMTP>
ISEMAIL_META_SMTP_RESP = {
    '215': "250 2.1.5 ok",
    '510': "553 5.1.0 Other address status",
    '511': "553 5.1.1 Bad destination mailbox address",
    '512': "553 5.1.2 Bad destination system address",
    '513': "553 5.1.3 Bad destination mailbox address syntax"}


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

# ------------------------------------------------------------------------
# Diagnoses
# ------------------------------------------------------------------------

ISEMAIL_VALID = MetaInfo(
    value=0,
    category=ISEMAIL_VALID_CATEGORY,
    description="Address is valid. Please note that this does not mean the address actually exists, nor even that the"
                " domain actually exists. This address could be issued by the domain owner without breaking the rules"
                " of any RFCs.",
    smtp=ISEMAIL_META_SMTP_RESP['215'],
)
ISEMAIL_DNSWARN_NO_MX_RECORD = MetaInfo(
    value=5,
    category=ISEMAIL_DNSWARN,
    description="Couldn't find an MX record for this domain but an A-record does exist",
    smtp=ISEMAIL_META_SMTP_RESP['215'],
)
ISEMAIL_DNSWARN_NO_RECORD = MetaInfo(
    value=6,
    category=ISEMAIL_DNSWARN,
    description="Couldn't find an MX record or an A-record for this domain",
    smtp=ISEMAIL_META_SMTP_RESP['215'],
)
ISEMAIL_RFC5321_TLD = MetaInfo(
    value=9,
    category=ISEMAIL_RFC5321,
    description="Address is valid but at a Top Level Domain",
    smtp=ISEMAIL_META_SMTP_RESP['215'],
    reference=ISEMAIL_META_REFERENCES['TLD'],
)
ISEMAIL_RFC5321_TLDNUMERIC = MetaInfo(
    value=10,
    category=ISEMAIL_RFC5321,
    description="Address is valid but the Top Level Domain begins with a number",
    smtp=ISEMAIL_META_SMTP_RESP['215'],
    reference=ISEMAIL_META_REFERENCES['TLD-format'],
)
ISEMAIL_RFC5321_QUOTEDSTRING = MetaInfo(
    value=11,
    category=ISEMAIL_RFC5321,
    description="Address is valid but contains a quoted string",
    smtp=ISEMAIL_META_SMTP_RESP['215'],
    reference=ISEMAIL_META_REFERENCES['quoted-string'],
)
ISEMAIL_RFC5321_ADDRESSLITERAL = MetaInfo(
    value=12,
    category=ISEMAIL_RFC5321,
    description="Address is valid but at a literal address not a domain",
    smtp=ISEMAIL_META_SMTP_RESP['215'],
    reference=(ISEMAIL_META_REFERENCES['address-literal'], ISEMAIL_META_REFERENCES['address-literal-IPv4'])
)
ISEMAIL_RFC5321_IPV6DEPRECATED = MetaInfo(
    value=13,
    category=ISEMAIL_DEPREC,
    description="Address is valid but contains a :: that only elides one zero group. All implementations must accept"
                " and be able to handle any legitimate RFC 4291 format.",
    smtp=ISEMAIL_META_SMTP_RESP['215'],
    reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
)
ISEMAIL_CFWS_COMMENT = MetaInfo(
    value=17,
    category=ISEMAIL_CFWS,
    description="Address contains comments",
    smtp=ISEMAIL_META_SMTP_RESP['215'],
    reference=ISEMAIL_META_REFERENCES['dot-atom'],
)
ISEMAIL_CFWS_FWS = MetaInfo(
    value=18,
    category=ISEMAIL_CFWS,
    description="Address contains Folding White Space",
    smtp=ISEMAIL_META_SMTP_RESP['215'],
    reference=ISEMAIL_META_REFERENCES['local-part'],
)
ISEMAIL_DEPREC_LOCALPART = MetaInfo(
    value=33,
    category=ISEMAIL_DEPREC,
    description="The local part is in a deprecated form",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=ISEMAIL_META_REFERENCES['obs-local-part'],
)
ISEMAIL_DEPREC_FWS = MetaInfo(
    value=34,
    category=ISEMAIL_DEPREC,
    description="Address contains an obsolete form of Folding White Space",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=(ISEMAIL_META_REFERENCES['obs-local-part'], ISEMAIL_META_REFERENCES['obs-domain'])
)
ISEMAIL_DEPREC_QTEXT = MetaInfo(
    value=35,
    category=ISEMAIL_DEPREC,
    description="A quoted string contains a deprecated character",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['obs-qtext'],
)
ISEMAIL_DEPREC_QP = MetaInfo(
    value=36,
    category=ISEMAIL_DEPREC,
    description="A quoted pair contains a deprecated character",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['obs-qp'],
)
ISEMAIL_DEPREC_COMMENT = MetaInfo(
    value=37,
    category=ISEMAIL_DEPREC,
    description="Address contains a comment in a position that is deprecated",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=(ISEMAIL_META_REFERENCES['obs-local-part'], ISEMAIL_META_REFERENCES['obs-domain'])
)
ISEMAIL_DEPREC_CTEXT = MetaInfo(
    value=38,
    category=ISEMAIL_DEPREC,
    description="A comment contains a deprecated character",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['obs-ctext'],
)
ISEMAIL_DEPREC_CFWS_NEAR_AT = MetaInfo(
    value=49,
    category=ISEMAIL_DEPREC,
    description="Address contains a comment or Folding White Space around the @ sign",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=(ISEMAIL_META_REFERENCES['CFWS-near-at'], ISEMAIL_META_REFERENCES['SHOULD-NOT'])
)
ISEMAIL_RFC5322_DOMAIN = MetaInfo(
    value=65,
    category=ISEMAIL_RFC5322,
    description="Address is RFC 5322 compliant but contains domain characters that are not allowed by DNS",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=ISEMAIL_META_REFERENCES['domain-RFC5322'],
)
ISEMAIL_RFC5322_TOOLONG = MetaInfo(
    value=66,
    category=ISEMAIL_RFC5322,
    description="Address is too long",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['mailbox-maximum'],
)
ISEMAIL_RFC5322_LOCAL_TOOLONG = MetaInfo(
    value=67,
    category=ISEMAIL_RFC5322,
    description="The local part of the address is too long",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=ISEMAIL_META_REFERENCES['local-part-maximum'],
)
ISEMAIL_RFC5322_DOMAIN_TOOLONG = MetaInfo(
    value=68,
    category=ISEMAIL_RFC5322,
    description="The domain part is too long",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=ISEMAIL_META_REFERENCES['domain-maximum'],
)
ISEMAIL_RFC5322_LABEL_TOOLONG = MetaInfo(
    value=69,
    category=ISEMAIL_RFC5322,
    description="The domain part contains an element that is too long",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=ISEMAIL_META_REFERENCES['label'],
)
ISEMAIL_RFC5322_DOMAINLITERAL = MetaInfo(
    value=70,
    category=ISEMAIL_RFC5322,
    description="The domain literal is not a valid RFC 5321 address literal",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['domain-literal'],
)
ISEMAIL_RFC5322_DOMLIT_OBSDTEXT = MetaInfo(
    value=71,
    category=ISEMAIL_RFC5322,
    description="The domain literal is not a valid RFC 5321 address literal and it contains obsolete characters",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['obs-dtext'],
)
ISEMAIL_RFC5322_IPV6_GRPCOUNT = MetaInfo(
    value=72,
    category=ISEMAIL_RFC5322,
    description="The IPv6 literal address contains the wrong number of groups",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
)
ISEMAIL_RFC5322_IPV6_2X2XCOLON = MetaInfo(
    value=73,
    category=ISEMAIL_RFC5322,
    description="The IPv6 literal address contains too many :: sequences",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
)
ISEMAIL_RFC5322_IPV6_BADCHAR = MetaInfo(
    value=74,
    category=ISEMAIL_RFC5322,
    description="The IPv6 address contains an illegal group of characters",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
)
ISEMAIL_RFC5322_IPV6_MAXGRPS = MetaInfo(
    value=75,
    category=ISEMAIL_RFC5322,
    description="The IPv6 address has too many groups",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
)
ISEMAIL_RFC5322_IPV6_COLONSTRT = MetaInfo(
    value=76,
    category=ISEMAIL_RFC5322,
    description="IPv6 address starts with a single colon",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
)
ISEMAIL_RFC5322_IPV6_COLONEND = MetaInfo(
    value=77,
    category=ISEMAIL_RFC5322,
    description="IPv6 address ends with a single colon",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
)
ISEMAIL_ERR_EXPECTING_DTEXT = MetaInfo(
    value=129,
    category=ISEMAIL_ERR,
    description="A domain literal contains a character that is not allowed",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=ISEMAIL_META_REFERENCES['dtext'],
)
ISEMAIL_ERR_NOLOCALPART = MetaInfo(
    value=130,
    category=ISEMAIL_ERR,
    description="Address has no local part",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=ISEMAIL_META_REFERENCES['local-part'],
)
ISEMAIL_ERR_NODOMAIN = MetaInfo(
    value=131,
    category=ISEMAIL_ERR,
    description="Address has no domain part",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=(ISEMAIL_META_REFERENCES['addr-spec'], ISEMAIL_META_REFERENCES['mailbox'])
)
ISEMAIL_ERR_CONSECUTIVEDOTS = MetaInfo(
    value=132,
    category=ISEMAIL_ERR,
    description="The address may not contain consecutive dots",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=(
        ISEMAIL_META_REFERENCES['local-part'],
        ISEMAIL_META_REFERENCES['domain-RFC5322'],
        ISEMAIL_META_REFERENCES['domain-RFC5321'])
)
ISEMAIL_ERR_ATEXT_AFTER_CFWS = MetaInfo(
    value=133,
    category=ISEMAIL_ERR,
    description="Address contains text after a comment or Folding White Space",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=(ISEMAIL_META_REFERENCES['local-part'], ISEMAIL_META_REFERENCES['domain-RFC5322'])
)
ISEMAIL_ERR_ATEXT_AFTER_QS = MetaInfo(
    value=134,
    category=ISEMAIL_ERR,
    description="Address contains text after a quoted string",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=ISEMAIL_META_REFERENCES['local-part'],
)
ISEMAIL_ERR_ATEXT_AFTER_DOMLIT = MetaInfo(
    value=135,
    category=ISEMAIL_ERR,
    description="Extra characters were found after the end of the domain literal",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=ISEMAIL_META_REFERENCES['domain-RFC5322'],
)
ISEMAIL_ERR_EXPECTING_QPAIR = MetaInfo(
    value=136,
    category=ISEMAIL_ERR,
    description="The address contains a character that is not allowed in a quoted pair",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=ISEMAIL_META_REFERENCES['quoted-pair'],
)
ISEMAIL_ERR_EXPECTING_ATEXT = MetaInfo(
    value=137,
    category=ISEMAIL_ERR,
    description="Address contains a character that is not allowed",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=ISEMAIL_META_REFERENCES['atext'],
)
ISEMAIL_ERR_EXPECTING_QTEXT = MetaInfo(
    value=138,
    category=ISEMAIL_ERR,
    description="A quoted string contains a character that is not allowed",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=ISEMAIL_META_REFERENCES['qtext'],
)
ISEMAIL_ERR_EXPECTING_CTEXT = MetaInfo(
    value=139,
    category=ISEMAIL_ERR,
    description="A comment contains a character that is not allowed",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=ISEMAIL_META_REFERENCES['qtext'],
)
ISEMAIL_ERR_BACKSLASHEND = MetaInfo(
    value=140,
    category=ISEMAIL_ERR,
    description="The address can't end with a backslash",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=(
        ISEMAIL_META_REFERENCES['domain-RFC5322'],
        ISEMAIL_META_REFERENCES['domain-RFC5321'],
        ISEMAIL_META_REFERENCES['quoted-pair'])
)
ISEMAIL_ERR_DOT_START = MetaInfo(
    value=141,
    category=ISEMAIL_ERR,
    description="Neither part of the address may begin with a dot",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=(
        ISEMAIL_META_REFERENCES['local-part'],
        ISEMAIL_META_REFERENCES['domain-RFC5322'],
        ISEMAIL_META_REFERENCES['domain-RFC5321'])
)
ISEMAIL_ERR_DOT_END = MetaInfo(
    value=142,
    category=ISEMAIL_ERR,
    description="Neither part of the address may end with a dot",
    smtp=ISEMAIL_META_SMTP_RESP['511'],
    reference=(
        ISEMAIL_META_REFERENCES['local-part'],
        ISEMAIL_META_REFERENCES['domain-RFC5322'],
        ISEMAIL_META_REFERENCES['domain-RFC5321'])
)
ISEMAIL_ERR_DOMAINHYPHENSTART = MetaInfo(
    value=143,
    category=ISEMAIL_ERR,
    description="A domain or subdomain cannot begin with a hyphen",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=ISEMAIL_META_REFERENCES['sub-domain'],
)
ISEMAIL_ERR_DOMAINHYPHENEND = MetaInfo(
    value=144,
    category=ISEMAIL_ERR,
    description="A domain or subdomain cannot end with a hyphen",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=ISEMAIL_META_REFERENCES['sub-domain'],
)
ISEMAIL_ERR_UNCLOSEDQUOTEDSTR = MetaInfo(
    value=145,
    category=ISEMAIL_ERR,
    description="Unclosed quoted string",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=ISEMAIL_META_REFERENCES['quoted-string'],
)
ISEMAIL_ERR_UNCLOSEDCOMMENT = MetaInfo(
    value=146,
    category=ISEMAIL_ERR,
    description="Unclosed comment",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=ISEMAIL_META_REFERENCES['CFWS'],
)
ISEMAIL_ERR_UNCLOSEDDOMLIT = MetaInfo(
    value=147,
    category=ISEMAIL_ERR,
    description="Domain literal is missing its closing bracket",
    smtp=ISEMAIL_META_SMTP_RESP['512'],
    reference=ISEMAIL_META_REFERENCES['domain-literal'],
)
ISEMAIL_ERR_FWS_CRLF_X2 = MetaInfo(
    value=148,
    category=ISEMAIL_ERR,
    description="Folding White Space contains consecutive CRLF sequences",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['CFWS'],
)
ISEMAIL_ERR_FWS_CRLF_END = MetaInfo(
    value=149,
    category=ISEMAIL_ERR,
    description="Folding White Space ends with a CRLF sequence",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=ISEMAIL_META_REFERENCES['CFWS'],
)
ISEMAIL_ERR_CR_NO_LF = MetaInfo(
    value=150,
    category=ISEMAIL_ERR,
    description="Address contains a carriage return that is not followed by a line feed",
    smtp=ISEMAIL_META_SMTP_RESP['513'],
    reference=(ISEMAIL_META_REFERENCES['CFWS'], ISEMAIL_META_REFERENCES['CRLF'])
)
