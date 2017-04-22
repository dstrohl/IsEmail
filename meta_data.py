# import re
import logging
import sys
from copy import copy
from enum import IntEnum

log = logging.getLogger('EmailParser')
log.setLevel(0)
stream_handler = logging.StreamHandler(sys.stdout)
log.addHandler(stream_handler)

log_critical = log.critical
log_error = log.error
log_warning = log.warning
log_info = log.info
log_debug = log.debug


def log_ddebug(msg, *args, **kwargs):
    # print(msg % args)
    log.log(9, msg, *args, **kwargs)



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

ISEMAIL_ALLOWED_GENERAL_ADDRESS_LITERAL_STANDARD_TAGS = []


# function control
ISEMAIL_MIN_THRESHOLD = 16
ISEMAIL_MAX_THREASHOLD = 255

# Miscellaneous string constants


# Element types

'''
ISEMAIL_ELEMENT_LOCALPART = 'local_part'
ISEMAIL_ELEMENT_COMMENT = 'comment'
ISEMAIL_ELEMENT_QUOTEDSTRING = 'quoted_string'

ISEMAIL_ELEMENT_DOMAINPART = 'domain_part'
ISEMAIL_ELEMENT_DOMAIN_LIT_IPV4 = 'domain_ipv4_literal'
ISEMAIL_ELEMENT_DOMAIN_LIT_IPV6 = 'domain_ipv6_literal'
ISEMAIL_ELEMENT_DOMAIN_LIT_GEN = 'domain_general_literal'
'''

# ISEMAIL_IP_REGEX = re.compile(r'(?P<address>(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
# ISEMAIL_IP_REGEX_GOOD_CHAR = re.compile(r'^[0-9A-Fa-f]{0,4}$')
'''
ISEMAIL_MAX_REPEAT = 9999
ISEMAIL_MIN_REPEAT = 0
'''

"""
ISEMAIL_RESULTS = dict(
    ISEMAIL_OK=0,
    ISEMAIL_WARNING=100,
    ISEMAIL_ERROR=255)
"""

class ISEMAIL_RESULT_CODES(IntEnum):
    OK = 1
    WARNING = 2
    ERROR = 3


class ISEMAIL_DOMAIN_TYPE(IntEnum):
    DNS = 1
    DOMAIN_LIT = 2
    GENERAL_LIT = 3
    IPv4 = 4
    IPv6 = 5
    OTHER_NON_DNS = 6

class ISEMAIL_DNS_LOOKUP_LEVELS(IntEnum):
    NO_LOOKUP = 0
    TLD_MATCH = 1
    ANY_RECORD = 2
    MX_RECORD = 3


# <Categories>

# <editor-fold desc="Meta Data">
ISEMAIL_RESP_CATEGORIES = dict(
    ISEMAIL_VALID_CATEGORY=dict(
        name='Valid Address',
        value=100,
        description="Address is valid",
        result=ISEMAIL_RESULT_CODES.OK),
    
    ISEMAIL_DNSWARN=dict(
        name='Valid Address (DNS Warning)',
        value=107,
        description="Address is valid but a DNS check was not successful",
        result=ISEMAIL_RESULT_CODES.WARNING),

    ISEMAIL_RFC5321=dict(
        name='Valid Address (unusual)',
        value=115,
        description="Address is valid for SMTP but has unusual elements",
        result=ISEMAIL_RESULT_CODES.WARNING),

    ISEMAIL_CFWS=dict(
        name='Valid Address (limited use)',
        value=131,
        description="Address is valid within the message but cannot be used unmodified for the envelope",
        result=ISEMAIL_RESULT_CODES.WARNING),

    ISEMAIL_DEPREC=dict(
        name='Valid Address (deprecated)',
        value=500,
        description="Address contains deprecated elements but may still be valid in restricted contexts",
        result=ISEMAIL_RESULT_CODES.WARNING),

    ISEMAIL_RFC5322=dict(
        name='Valid Address (unusable)',
        value=775,
        description="The address is only valid according to the broad definition of RFC 5322. It is otherwise invalid.",
        result=ISEMAIL_RESULT_CODES.WARNING),

    ISEMAIL_ERR=dict(
        name='Invalid Address',
        value=999,
        description="Address is invalid for any purpose",
        result=ISEMAIL_RESULT_CODES.ERROR),)


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
        key = "local-part",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
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
        key = "local-part-maximum",
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.5.3.1.1",
        blockquote=''
                   'The maximum total length of a user name or other local-part is 64'
                   'octets.',
        cite='RFC 5322 section 4.5.3.1.1'),

    "obs-local-part": dict(
        key = "obs-local-part",
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
        key = "dot-atom",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'dot-atom        =   [CFWS] dot-atom-text [CFWS]'
            ''
            'dot-atom-text   =   1*atext *("." 1*atext)',
        cite='RFC 5322 section 3.4.1'),

    "quoted-string": dict(
        key = "quoted-string",
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
        key = "CFWS-near-at",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'Comments and folding white space'
            'SHOULD NOT be used around the "@" in the addr-spec.',
        cite='RFC 5322 section 3.4.1'),

    "SHOULD-NOT": dict(
        key = "SHOULD-NOT",
        blockquote_cite="http://tools.ietf.org/html/rfc2119",
        blockquote=''
            '4. SHOULD NOT   This phrase, or the phrase "NOT RECOMMENDED" mean that'
            '   there may exist valid reasons in particular circumstances when the'
            '   particular behavior is acceptable or even useful, but the full'
            '   implications should be understood and the case carefully weighed'
            '   before implementing any behavior described with this label.',

        cite='RFC 2119 section 4'),

    "atext": dict(
        key = "atext",
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
        key = "obs-domain",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'obs-domain      =   atom *("." atom)'
            ''
            'atom            =   [CFWS] 1*atext [CFWS]',
        cite='RFC 5322 section 3.4.1'),

    "domain-RFC5322": dict(
        key = "domain-RFC5322",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'domain          =   dot-atom / domain-literal / obs-domain'
            ''
            'dot-atom        =   [CFWS] dot-atom-text [CFWS]'
            ''
            'dot-atom-text   =   1*atext *("." 1*atext)',
        cite='RFC 5322 section 3.4.1'),

    "domain-RFC5321": dict(
        key = "domain-RFC5321",
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.2",
        blockquote=''
            '   Domain         = sub-domain *("." sub-domain)',
        cite='RFC 5321 section 4.1.2'),
    "sub-domain": dict(
        key = "sub-domain",
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.2",
        blockquote=''
            'Domain         = sub-domain *("." sub-domain)'
            ''
            'Let-dig        = ALPHA / DIGIT'
            ''
            'Ldh-str        = *( ALPHA / DIGIT / "-" ) Let-dig',
        cite='RFC 5321 section 4.1.2'),

    "label": dict(
        key = "label",
        blockquote_cite="http://tools.ietf.org/html/rfc1035#section-2.3.4",
        blockquote=''
            '   labels          63 octets or less',
        cite='RFC 5321 section 4.1.2'),

    "CRLF": dict(
        key = "CRLF",
        blockquote_cite="http://tools.ietf.org/html/rfc5234#section-2.3",
        blockquote='CRLF        =  %d13.10',
        cite='RFC 5234 section 2.3'),

    "CFWS": dict(
        key = "CFWS",
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
        key = "domain-literal",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote='domain-literal  =   [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]',
        cite='RFC 5322 section 3.4.1'),

    "address-literal": dict(
        key = "address-literal",
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.2",
        blockquote=''
            'address-literal  = "[" ( IPv4-address-literal /'
            '                IPv6-address-literal /'
            '                General-address-literal ) "]"',
        cite='RFC 5321 section 4.1.2'),

    "address-literal-general": dict(
        key="address-literal",
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.2",
        blockquote=''
                   ' General-address-literal  = Standardized-tag ":" 1*dcontent',
        cite='RFC 5321 section 4.1.2'),

    "address-literal-IPv4": dict(
        key = "address-literal-IPv4",
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.3",
        blockquote=''
            'IPv4-address-literal  = Snum 3("."  Snum)'
            ''
            'Snum           = 1*3DIGIT'
            '              ; representing a decimal integer'
            '              ; value in the range 0 through 255',
        cite='RFC 5321 section 4.1.3'),

    "address-literal-IPv6": dict(
        key = "address-literal-IPv6",
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
        key = "dtext",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote=''
            'dtext           =   %d33-90 /          ; Printable US-ASCII'
            '                     %d94-126 /         ;  characters not including'
            '                     obs-dtext          ;  "[", "]", or "\"',
        cite='RFC 5322 section 3.4.1'),

    "obs-dtext": dict(
        key = "obs-dtext",
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
        key = "qtext",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.2.4",
        blockquote=''
            'qtext           =   %d33 /             ; Printable US-ASCII'
            '                   %d35-91 /          ;  characters not including'
            '                   %d93-126 /         ;  "\" or the quote character'
            '                   obs-qtext',
        cite='RFC 5322 section 3.2.4'),

    "obs-qtext": dict(
        key = "obs-qtext",
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
        key = "ctext",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.2.3",
        blockquote=''
            'ctext           =   %d33-39 /          ; Printable US-ASCII'
            '                   %d42-91 /          ;  characters not including'
            '                   %d93-126 /         ;  "(", ")", or "\"'
            '                   obs-ctext',
        cite='RFC 5322 section 3.2.3'),

    "obs-ctext": dict(
        key = "obs-ctext",
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
        key = "quoted-pair",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.2.1",
        blockquote=''
            'quoted-pair     =   ("\" (VCHAR / WSP)) / obs-qp'
            ''
            'VCHAR           =  %d33-126            ; visible (printing) characters'
            'WSP             =  SP / HTAB           ; white space',
        cite='RFC 5322 section 3.2.1'),

    "obs-qp": dict(
        key = "obs-qp",
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
        key = "TLD",
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
        key = "TLD-format",
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
        key = "mailbox-maximum",
        blockquote_cite="http://www.rfc-editor.org/errata_search.php?eid=1690",
        blockquote=''
            'However, there is a restriction in RFC 2821 on the length of an'
            'address in MAIL and RCPT commands of 254 characters.  Since addresses'
            'that do not fit in those fields are not normally useful, the upper'
            'limit on address lengths should normally be considered to be 254.',
        cite='Dominic Sayers, RFC 3696 erratum 1690'),

    "domain-maximum": dict(
        key = "domain-maximum",
        blockquote_cite="http://tools.ietf.org/html/rfc1035#section-4.5.3.1.2",
        blockquote='The maximum total length of a domain name or number is 255 octets.',
        cite='RFC 5321 section 4.5.3.1.2'),

    "mailbox": dict(
        key = "mailbox",
        blockquote_cite="http://tools.ietf.org/html/rfc5321#section-4.1.2",
        blockquote='Mailbox        = Local-part "@" ( Domain / address-literal )',
        cite='RFC 5321 section 4.1.2'),

    "addr-spec": dict(
        key = "addr-spec",
        blockquote_cite="http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote='addr-spec       =   local-part "@" domain',
        cite='RFC 5322 section 3.4.1'),

    "liberal_domain": dict(
        key="liberal_domain",
        blockquote_cite=" http://tools.ietf.org/html/rfc5322#section-3.4.1",
        blockquote='domain          =   dot-atom / domain-literal / address_literal /obs-domain'
            '---------------------------------------------------------------------------------------------'
            '; NB For SMTP mail, the domain-literal is restricted by RFC5321 as follows:'
            'Mailbox        = Local-part "@" ( domain-addr / address-literal )'
            '-----------------------------------------------------------------------------------------'

            '// http://tools.ietf.org/html/rfc5322#section-3.4.1'
            '//      Note: A liberal syntax for the domain portion of addr-spec is'
            '//      given here.  However, the domain portion contains addressing'
            '//      information specified by and used in other protocols (e.g.,'
            '//      [RFC1034], [RFC1035], [RFC1123], [RFC5321]).  It is therefore'
            '//      incumbent upon implementations to conform to the syntax of'
            '//      addresses for the context in which they are used.'
            '// is_email() authors note: its not clear how to interpret this in'
            '// the context of a general email address validator. The conclusion I'
            '// have reached is this: "addressing information" must comply with'
            '// RFC 5321 (and in turn RFC 1035), anything that is "semantically'
            '// invisible" must comply only with RFC 5322.',

        cite='RFC 5322 section 3.4.1'),

}
# </editor-fold>

# ------------------------------------------------------------------------
# Diagnoses
# ------------------------------------------------------------------------

ISEMAIL_DIAG_RESPONSES = dict(

    VALID=dict(
        value=1000,
        description='Valid Email',
        category='ISEMAIL_VALID_CATEGORY',
        longdescription="Address is valid. Please note that this does not mean the address actually exists, nor even that the"
                    " domain actually exists. This address could be issued by the domain owner without breaking the rules"
                    " of any RFCs.",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5']
    ),
    DNSWARN_COMM_ERROR=dict(
        value=1003,
        category='ISEMAIL_DNSWARN',
        description="There was an error communicating with DNS",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
    ),
    DNSWARN_INVALID_TLD=dict(
        value=1004,
        category='ISEMAIL_DNSWARN',
        description="Top Level Domain is not in the list of available TLDs",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
    ),
    DNSWARN_NO_MX_RECORD=dict(
        value=1005,
        category='ISEMAIL_DNSWARN',
        description="Couldn't find an MX record for this domain but an A-record does exist",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
    ),
    DNSWARN_NO_RECORD=dict(
        value=1006,
        category='ISEMAIL_DNSWARN',
        description="Couldn't find an MX record or an A-record for this domain",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
    ),
    RFC5321_TLD=dict(
        value=1009,
        category='ISEMAIL_RFC5321',
        description="Address is valid but at a Top Level Domain",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['TLD'],
    ),
    RFC5321_TLD_NUMERIC=dict(
        value=1010,
        category='ISEMAIL_RFC5321',
        description="Address is valid but the Top Level Domain begins with a number",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['TLD-format'],
    ),
    RFC5321_QUOTED_STRING=dict(
        value=1011,
        category='ISEMAIL_RFC5321',
        description="Address is valid but contains a quoted string",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['quoted-string'],
    ),
    RFC5321_ADDRESS_LITERAL=dict(
        value=1012,
        category='ISEMAIL_RFC5321',
        description="Address is valid but at a literal address not a domain",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=(ISEMAIL_META_REFERENCES['address-literal'], ISEMAIL_META_REFERENCES['address-literal-IPv4'])
    ),
    RFC5321_IPV6_DEPRECATED=dict(
        value=1013,
        category='ISEMAIL_DEPREC',
        description="Address is valid but contains a :: that only elides one zero group. All implementations must accept"
                    " and be able to handle any legitimate RFC 4291 format.",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    CFWS_COMMENT=dict(
        value=1017,
        category='ISEMAIL_CFWS',
        description="Address contains comments",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['dot-atom'],
    ),
    CFWS_FWS=dict(
        value=1018,
        category='ISEMAIL_CFWS',
        description="Address contains FWS",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['local-part'],
    ),
    DEPREC_LOCAL_PART=dict(
        value=1033,
        category='ISEMAIL_DEPREC',
        description="The local part is in a deprecated form",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['obs-local-part'],
    ),
    DEPREC_FWS=dict(
        value=1034,
        category='ISEMAIL_DEPREC',
        description="Address contains an obsolete form of Folding White Space",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=(ISEMAIL_META_REFERENCES['obs-local-part'], ISEMAIL_META_REFERENCES['obs-domain'])
    ),
    DEPREC_QTEXT=dict(
        value=1035,
        category='ISEMAIL_DEPREC',
        description="A quoted string contains a deprecated character",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['obs-qtext'],
    ),
    DEPREC_QP=dict(
        value=1036,
        category='ISEMAIL_DEPREC',
        description="A quoted pair contains a deprecated character",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['obs-qp'],
    ),
    DEPREC_COMMENT=dict(
        value=1037,
        category='ISEMAIL_DEPREC',
        description="Address contains a comment in a position that is deprecated",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=(ISEMAIL_META_REFERENCES['obs-local-part'], ISEMAIL_META_REFERENCES['obs-domain'])
    ),
    DEPREC_CTEXT=dict(
        value=1038,
        category='ISEMAIL_DEPREC',
        description="A comment contains a deprecated character",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['obs-ctext'],
    ),
    DEPREC_CFWS_NEAR_AT=dict(
        value=1049,
        category='ISEMAIL_DEPREC',
        description="Address contains a comment or Folding White Space around the @ sign",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=(ISEMAIL_META_REFERENCES['CFWS-near-at'], ISEMAIL_META_REFERENCES['SHOULD-NOT'])
    ),
    RFC5322_DOMAIN=dict(
        value=1065,
        category='ISEMAIL_RFC5322',
        description="Address is RFC 5322 compliant but contains domain characters that are not allowed by DNS",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['domain-RFC5322'],
    ),
    RFC5322_TOO_LONG=dict(
        value=1066,
        category='ISEMAIL_RFC5322',
        description="Address is too long",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['mailbox-maximum'],
    ),
    RFC5322_LOCAL_TOO_LONG=dict(
        value=1067,
        category='ISEMAIL_RFC5322',
        description="The local part of the address is too long",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['local-part-maximum'],
    ),
    RFC5322_DOMAIN_TOO_LONG=dict(
        value=1068,
        category='ISEMAIL_RFC5322',
        description="The domain part is too long",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['domain-maximum'],
    ),
    RFC5322_LABEL_TOO_LONG=dict(
        value=1069,
        category='ISEMAIL_RFC5322',
        description="The domain part contains an element that is too long",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['label'],
    ),
    RFC5322_DOMAIN_LITERAL=dict(
        value=1070,
        category='ISEMAIL_RFC5322',
        description="The domain literal is not a valid RFC 5321 address literal",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['domain-literal'],
    ),
    RFC5322_DOM_LIT_OBS_DTEXT=dict(
        value=1071,
        category='ISEMAIL_RFC5322',
        description="The domain literal is not a valid RFC 5321 address literal and it contains obsolete characters",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['obs-dtext'],
    ),
    RFC5322_IPV6_GRP_COUNT=dict(
        value=1072,
        category='ISEMAIL_RFC5322',
        description="The IPv6 literal address contains the wrong number of groups",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_2X2X_COLON=dict(
        value=1073,
        category='ISEMAIL_RFC5322',
        description="The IPv6 literal address contains too many :: sequences",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_BAD_CHAR=dict(
        value=1074,
        category='ISEMAIL_RFC5322',
        description="The IPv6 address contains an illegal group of characters",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_MAX_GRPS=dict(
        value=1075,
        category='ISEMAIL_RFC5322',
        description="The IPv6 address has too many groups",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_COLON_STRT=dict(
        value=1076,
        category='ISEMAIL_RFC5322',
        description="IPv6 address starts with a single colon",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_COLON_END=dict(
        value=1077,
        category='ISEMAIL_RFC5322',
        description="IPv6 address ends with a single colon",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_ADDR=dict(
        value=1078,
        category='ISEMAIL_RFC5322',
        description="The address literal is an IPv6 address",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_FULL_ADDR=dict(
        value=1079,
        category='ISEMAIL_RFC5322',
        description="The address literal is a full IPv6 address",

        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_COMP_ADDR=dict(
        value=1080,
        category='ISEMAIL_RFC5322',
        description="The address literal is a compressed IPv6 address",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_IPV4_ADDR=dict(
        value=1081,
        category='ISEMAIL_RFC5322',
        description="The address literal is a full IPv6:IPv4 address",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV6_IPV4_COMP_ADDR=dict(
        value=1082,
        category='ISEMAIL_RFC5322',
        description="The address literal is a compressed IPv6:IPv4 address",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv6'],
    ),
    RFC5322_IPV4_ADDR=dict(
        value=1083,
        category='ISEMAIL_RFC5322',
        description="The address literal is an IPv6 address",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['address-literal-IPv4'],
    ),
    RFC5322_GENERAL_LITERAL=dict(
        value=1084,
        category='ISEMAIL_RFC5322',
        description="The address literal is a general address",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['address-literal-general'],
    ),
    RFC5322_LIMITED_DOMAIN=dict(
        value=1085,
        category='ISEMAIL_RFC5322',
        description="The address is valid for RFC5322, but not RFC5321",
        smtp=ISEMAIL_META_SMTP_RESP['2.1.5'],
        reference=ISEMAIL_META_REFERENCES['liberal_domain'],
    ),
    ERR_INVALID_ADDR_LITERAL=dict(
        value=1128,
        category='ISEMAIL_ERR',
        description="The address literal is not a valid address",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['address-literal'],
    ),

    ERR_EXPECTING_DTEXT=dict(
        value=1129,
        category='ISEMAIL_ERR',
        description="A domain literal contains a character that is not allowed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['dtext'],
    ),
    ERR_NO_LOCAL_PART=dict(
        value=1130,
        category='ISEMAIL_ERR',
        description="Address has no local part",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['local-part'],
    ),
    ERR_NO_DOMAIN_PART=dict(
        value=1131,
        category='ISEMAIL_ERR',
        description="Address has no domain part",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=(ISEMAIL_META_REFERENCES['addr-spec'], ISEMAIL_META_REFERENCES['mailbox'])
    ),
    ERR_CONSECUTIVE_DOTS=dict(
        value=1132,
        category='ISEMAIL_ERR',
        description="The address may not contain consecutive dots",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=(
            ISEMAIL_META_REFERENCES['local-part'],
            ISEMAIL_META_REFERENCES['domain-RFC5322'],
            ISEMAIL_META_REFERENCES['domain-RFC5321'])
    ),
    ERR_ATEXT_AFTER_CFWS=dict(
        value=1133,
        category='ISEMAIL_ERR',
        description="Address contains text after a comment or Folding White Space",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=(ISEMAIL_META_REFERENCES['local-part'], ISEMAIL_META_REFERENCES['domain-RFC5322'])
    ),
    ERR_ATEXT_AFTER_QS=dict(
        value=1134,
        category='ISEMAIL_ERR',
        description="Address contains text after a quoted string",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['local-part'],
    ),
    ERR_ATEXT_AFTER_DOMLIT=dict(
        value=1135,
        category='ISEMAIL_ERR',
        description="Extra characters were found after the end of the domain literal",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['domain-RFC5322'],
    ),
    ERR_EXPECTING_QPAIR=dict(
        value=1136,
        category='ISEMAIL_ERR',
        description="The address contains a character that is not allowed in a quoted pair",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['quoted-pair'],
    ),
    ERR_EXPECTING_ATEXT=dict(
        value=1137,
        category='ISEMAIL_ERR',
        description="Address contains a character that is not allowed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['atext'],
    ),
    ERR_EXPECTING_QTEXT=dict(
        value=1138,
        category='ISEMAIL_ERR',
        description="A quoted string contains a character that is not allowed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['qtext'],
    ),
    ERR_EXPECTING_CTEXT=dict(
        value=1139,
        category='ISEMAIL_ERR',
        description="A comment contains a character that is not allowed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=ISEMAIL_META_REFERENCES['qtext'],
    ),
    ERR_BACKSLASH_END=dict(
        value=1140,
        category='ISEMAIL_ERR',
        description="The address can't end with a backslash",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=(
            ISEMAIL_META_REFERENCES['domain-RFC5322'],
            ISEMAIL_META_REFERENCES['domain-RFC5321'],
            ISEMAIL_META_REFERENCES['quoted-pair'])
    ),
    ERR_DOT_START=dict(
        value=1141,
        category='ISEMAIL_ERR',
        description="Neither part of the address may begin with a dot",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=(
            ISEMAIL_META_REFERENCES['local-part'],
            ISEMAIL_META_REFERENCES['domain-RFC5322'],
            ISEMAIL_META_REFERENCES['domain-RFC5321'])
    ),
    ERR_DOT_END=dict(
        value=1142,
        category='ISEMAIL_ERR',
        description="Neither part of the address may end with a dot",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.1'],
        reference=(
            ISEMAIL_META_REFERENCES['local-part'],
            ISEMAIL_META_REFERENCES['domain-RFC5322'],
            ISEMAIL_META_REFERENCES['domain-RFC5321'])
    ),
    ERR_DOMAIN_HYPHEN_START=dict(
        value=1143,
        category='ISEMAIL_ERR',
        description="A domain or subdomain cannot begin with a hyphen",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['sub-domain'],
    ),
    ERR_DOMAIN_HYPHEN_END=dict(
        value=1144,
        category='ISEMAIL_ERR',
        description="A domain or subdomain cannot end with a hyphen",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['sub-domain'],
    ),
    ERR_UNCLOSED_QUOTED_STR=dict(
        value=1145,
        category='ISEMAIL_ERR',
        description="Unclosed quoted string",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['quoted-string'],
    ),
    ERR_UNCLOSED_COMMENT=dict(
        value=1146,
        category='ISEMAIL_ERR',
        description="Unclosed comment",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['CFWS'],
    ),
    ERR_UNCLOSED_DOM_LIT=dict(
        value=1147,
        category='ISEMAIL_ERR',
        description="Domain literal is missing its closing bracket",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.2'],
        reference=ISEMAIL_META_REFERENCES['domain-literal'],
    ),
    ERR_FWS_CRLF_X2=dict(
        value=1148,
        category='ISEMAIL_ERR',
        description="Folding White Space contains consecutive CRLF sequences",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['CFWS'],
    ),
    ERR_FWS_CRLF_END=dict(
        value=1149,
        category='ISEMAIL_ERR',
        description="Folding White Space ends with a CRLF sequence",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['CFWS'],
    ),
    ERR_CR_NO_LF=dict(
        value=1150,
        category='ISEMAIL_ERR',
        description="Address contains a carriage return that is not followed by a line feed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=(ISEMAIL_META_REFERENCES['CFWS'], ISEMAIL_META_REFERENCES['CRLF'])
    ),
    ERR_NO_DOMAIN_SEP=dict(
        value=1151,
        category='ISEMAIL_ERR',
        description="Address does not contain a domain seperator (@ sign)",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['domain-RFC5321']
    ),
    ERR_MULT_FWS_IN_COMMENT=dict(
        value=1152,
        category='ISEMAIL_ERR',
        description="Address contains multiple FWS in a comment",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['domain-RFC5321']
    ),
    ERR_EMPTY_ADDRESS=dict(
        value=1255,
        category='ISEMAIL_ERR',
        description="Empty Address Passed",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
        reference=ISEMAIL_META_REFERENCES['domain-RFC5321']
    ),
    ERR_UNKNOWN=dict(
        value=1256,
        category='ISEMAIL_ERR',
        description="Unknown Error parsing email",
        smtp=ISEMAIL_META_SMTP_RESP['5.1.3'],
    ),

)
# </editor-fold>  META DATA



"""
RETURN_OBJ_TEMPLATE = {
    'single': {
        'cat' : '[{status}]: {name}: ({description})',
        'diag': '[{status}] {description}',
    },
    'both': {
        'cat': '{cat_name} [{status}]\n{cat_description}\n{diag_group}',
        'diag': '    - {diag_description}',
    }}

"""


def _make_list(obj_in):
    if obj_in is None:
        return []
    if isinstance(obj_in, str):
        return [obj_in]
    if isinstance(obj_in, (list, tuple)):
        return obj_in
    if hasattr(obj_in, '__iter__'):
        return obj_in
    return [obj_in]


class MetaBase(object):
    type_name = 'Base'
    is_cat = False
    is_diag = False

    def __init__(self, key, dict_in, lookup):
        self.lookup = lookup
        self.name = dict_in.get('name', None)
        self.key = key
        self._value = dict_in['value']
        self.description = dict_in['description']
        self._override_status = None
        self._result = dict_in.get('result', None)
        self._single_desc = None
        self._both_desc = None

        self._diags = MetaList()

    def format(self, format_str=None, **kwargs):
        format_str = format_str or self.lookup.default_format
        return format_str.format(**self._fmt_dict(kwargs))

    def _fmt_dict(self, kwargs):
        raise NotImplementedError()

    def __repr__(self):
        return '%s(%s) [%s]' % (self.type_name, self.key, self.status.name)

    def __str__(self):
        return self.format()

    @property
    def _base_status(self):
        return self._result

    @property
    def value(self):
        if self.status == ISEMAIL_RESULT_CODES.ERROR:
            return self._value * 10000
        elif self.status == ISEMAIL_RESULT_CODES.WARNING:
            return self._value * 100
        else:
            return self._value

    @property
    def status(self):
        return self._override_status or self._base_status

    def set_override_status(self, new_status):
        self._override_status = new_status
        # self._single_desc = None
        # self._both_desc = None

    def reset_status(self):
        self._override_status = None
        # self._single_desc = None
        # self._both_desc = None

    def _get_other(self, other):
        if isinstance(other, str):
            return self.lookup[other].value
        elif isinstance(other, int):
            return other
        else:
            return other.value

    def __eq__(self, other):
        return self.value == self._get_other(other)

    def __ne__(self, other):
        return self.value != self._get_other(other)

    def __lt__(self, other):
        return self.value < self._get_other(other)

    def __le__(self, other):
        return self.value <= self._get_other(other)

    def __gt__(self, other):
        return self.value > self._get_other(other)

    def __ge__(self, other):
        return self.value >= self._get_other(other)

    def __hash__(self):
        return hash(self.key)

    def _in_flt_cat(self, filter_set=None, exact=False):
        return self.key in filter_set

    def _in_flt_diag(self, filter_set=None, exact=False):
        return self.key in filter_set

    def _in_flt_status(self, filter_set=None):
        return self.status.name in filter_set

    def in_filter(self, filter, exact=False):
        if filter is None:
            return True
        if isinstance(filter, dict):
            tmp_cat = self._in_flt_cat(_make_list(filter.get('cats', None)), exact)
            tmp_diag = self._in_flt_diag(_make_list(filter.get('diags', None)), exact)
            tmp_status = self._in_flt_status(_make_list(filter.get('status', None)))
            return any((tmp_cat, tmp_diag, tmp_status))
        else:
            return self.key in _make_list(filter)


class MetaCat(MetaBase):
    type_name = 'Categ'
    is_cat = False
    is_diag = True

    def add_diag(self, key, dict_in):
        tmp_diag = MetaDiag(key, dict_in, self, self.lookup)
        self._diags[key] = tmp_diag
        return tmp_diag

    def _fmt_dict(self, kwargs):
        tmp_dict = dict(
            name=self.name,
            description=self.description,
            key=self.key,
            value=self.value,
            status=self.status.name)
        tmp_dict.update(kwargs)
        return tmp_dict

    def _in_flt_diag(self, filter_set=None, exact=False):
        if exact:
            return False
        else:
            for d in self._diags.keys():
                if d.key in filter_set:
                    return True
            return False


class MetaDiag(MetaBase):
    type_name = 'Diag'
    is_cat = False
    is_diag = True

    def __init__(self, key, dict_in, cat_rec, lookup):
        super().__init__(key, dict_in, lookup)

        self.category = cat_rec
        self.smtp = dict_in['smtp']['description']
        self.reference = []
        if 'reference' in dict_in:
            tmp_refs = dict_in['reference']
            if isinstance(tmp_refs, (list, tuple)):
                for ref in dict_in['reference']:
                    self.reference.append(ref)
            else:
                self.reference.append(tmp_refs)

    def __repr__(self):
        return '%s(%s) [%s] -> %s' % (self.type_name, self.key, self.status.name, self.category.key)

    @property
    def _dif_status(self):
        if self._override_status is None:
            return ''
        else:
            return '[%s] ' % self.status.name

    def _fmt_dict(self, kwargs):
        tmp_dict = dict(
            description=self.description,
            key=self.key,
            value=self.value,
            status=self.status.name,
            cat_key=self.category.key,
            cat_name=self.category.name,
            dif_status=self._dif_status)
        tmp_dict.update(kwargs)
        return tmp_dict

    def _in_flt_cat(self, filter_set=None, exact=False):
        if exact:
            return False
        else:
            return self.category.key in filter_set

    @property
    def _base_status(self):
        return self.category.status

'''
class MetaPositionalDiag(object):
    type_name = 'Diag'
    is_cat = False
    is_diag = True

    def __init__(self, diag, begin=0, length=0):
        if isinstance(diag, str):
            self.base_diag = META_LOOKUP[diag]
        else:
            self.base_diag = diag

        self.lookup = self.base_diag.lookup
        self.key = self.base_diag.key
        self.value = self.base_diag.value
        self.description = self.base_diag.description
        self.status = self.base_diag.status

        self.category = self.base_diag.category
        self.smtp = self.base_diag.smtp
        self.reference = self.base_diag.references

        if not begin and not length:
            self.positions = []
        else:
            self.positions = [(begin, length)]

    def add(self, begin, length):
        self.positions.append((begin, length))

    def _in_flt_cat(self, filter_set=None, exact=False):
        if exact:
            return False
        else:
            return self.category.key in filter_set

    def _in_flt_diag(self, filter_set=None, exact=False):
        return self.key in filter_set

    def _in_flt_status(self, filter_set=None):
        return self.status.name in filter_set

    def in_filter(self, filter, exact=False):
        if filter is None:
            return True
        if isinstance(filter, dict):
            tmp_cat = self._in_flt_cat(_make_list(filter.get('cats', None)), exact)
            tmp_diag = self._in_flt_diag(_make_list(filter.get('diags', None)), exact)
            tmp_status = self._in_flt_status(_make_list(filter.get('status', None)))
            return any((tmp_cat, tmp_diag, tmp_status))
        else:
            return self.key in _make_list(filter)

    def __repr__(self):
        return '%s(%s) [%s] -> %s' % (self.type_name, self.key, self.status.name, self.category.key)

    @property
    def _dif_status(self):
        if self.base_diag._override_status is None:
            return ''
        else:
            return '[%s] ' % self.status.name

    def format(self, format_str, **kwargs):
        tmp_dict = dict(
            description=self.description,
            key=self.key,
            value=self.value,
            status=self.status.name,
            cat_key=self.category.key,
            cat_name=self.category.name,
            dif_status=self._dif_status)
        tmp_dict.update(kwargs)
        return format_str.format(**tmp_dict)


    def __str__(self):
        return self.key

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __le__(self, other):
        return self.value <= other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __iter__(self):
        for p in self.positions:
            yield p
'''


class MetaList(object):
    def __init__(self, data=None):
        self._keys = {}
        self._ordered = []

        if data is not None:
            self.update(data)

        self._sorted = None

    def clear(self):
        self._keys.clear()
        self._ordered.clear()
        self._sorted = None

    def sort(self, reverse=True):
        if self._sorted != repr(reverse):
            self._ordered.sort(reverse=reverse)
            self._sorted = repr(reverse)

    def update(self, dict_in):
        self._sorted = False
        for key, item in dict_in:
            self[key] = item

    def keys(self, reverse=True, show_all=True, ordered=False, filter=None, within=None):
        if isinstance(within, str):
            within = [within]
        if not show_all:
            ordered = True
        if ordered or filter is not None:
            tmp_ret = []
            for i in self.values(reverse=reverse, show_all=show_all):
                if filter is None or i.in_filter(filter):
                    if within is None or i.key in within:
                        tmp_ret.append(i.key)
            return tmp_ret
        else:
            return self._keys.keys()

    def values(self, reverse=True, show_all=True, filter=None, ordered=True, within=None):
        if isinstance(filter, str):
            filter = [filter]
        if isinstance(within, str):
            within = [within]

        if ordered or not show_all:
            self.sort(reverse=reverse)

        if filter is not None or within is not None:
            tmp_ret = []
            for i in self._ordered:
                if i.in_filter(filter):
                    if within is None or i.key in within:
                        tmp_ret.append(i)
        else:
            tmp_ret = self._ordered.copy()
        if show_all or len(tmp_ret) < 2:
            return tmp_ret
        else:
            return [tmp_ret[0]]

    def __getitem__(self, item):
        return self._keys[item]

    def __setitem__(self, key, value):
        self._sorted = None
        self._keys[key] = value
        self._ordered.append(value)

    def __iter__(self):
        self.sort(reverse=True)
        for item in self._ordered:
            yield item

    def __contains__(self, item):
        return item in self._keys

    def __bool__(self):
        return bool(self._keys)

    def __len__(self):
        return len(self._ordered)


"""

Returns:

key_dict (only both)
document_string (only both)

obj_dict (either cat or diag)
object_list (either cat or diag)
key_list (either cat or diat)

desc_list (any)
formatted_string (any)



"""


class MetaOutoutBase(object):
    report_name = ''
    only_single = False
    only_both = False

    def __init__(self, parent):
        self.parent = parent
        self.items = MetaList()
        self.sub_items = {}

    def add_item(self, diag):
        if self.inc_both:
            tmp_cat = diag.category
            if tmp_cat.key not in self.items:
                self.items[tmp_cat.key] = tmp_cat
                self.sub_items[tmp_cat.key] = MetaList()
            self.sub_items[tmp_cat.key][diag.key] = diag
        elif self.inc_cat:
            diag = diag.category
            if diag.key not in self.items:
                self.items[diag.key] = diag
        else:
            self.items[diag.key] = diag

    def _generate(self, **kwargs):
        raise NotImplementedError('_generate must be implemented in sub classes')

    def out(self, diags, **kwargs):
        self.sub_items.clear()
        self.items.clear()
        if self.only_both:
            self.inc_cat = kwargs.pop('inc_cat', True)
            self.inc_diag = kwargs.pop('inc_diag', True)
            if not self.inc_cat or not self.inc_diag:
                raise AttributeError('%s report does not support inc_cat or inc_diag' % self.report_name)
            self.inc_both = True

        elif self.only_single:
            self.inc_cat = kwargs.pop('inc_cat', False)
            self.inc_diag = kwargs.pop('inc_diag', True)
            if self.inc_cat and self.inc_diag:
                raise AttributeError('%s report does not support inc_cat or inc_diag' % self.report_name)
            self.inc_both = False
        else:
            self.inc_cat = kwargs.pop('inc_cat', False)
            self.inc_diag = kwargs.pop('inc_diag', True)
            self.inc_both = self.inc_cat and self.inc_diag

        if diags is not None:
            for item in diags:
                self.add_item(item)

        return self._generate(**kwargs)


class MR_KeyDict(MetaOutoutBase):
    report_name = 'key_dict'
    only_single = False
    only_both = True

    def _generate(self, **kwargs):
        tmp_ret = {}
        for item in self.items:
            tmp_sub_item = []
            for diag in self.sub_items[item.key]:
                tmp_sub_item.append(diag.key)
            tmp_ret[item.key] = tmp_sub_item
        return tmp_ret


class MR_ObjDict(MetaOutoutBase):
    report_name = 'obj_dict'
    only_single = True
    only_both = False

    def _generate(self, **kwargs):
        tmp_ret = {}
        for item in self.items:
            tmp_ret[item.key] = item
        return tmp_ret


class MR_ObjList(MetaOutoutBase):
    report_name = 'object_list'
    only_single = True
    only_both = False
    # object_list (either cat or diag)

    def _generate(self, **kwargs):
        tmp_ret = []
        for item in self.items:
            tmp_ret.append(item)
        return tmp_ret


class MR_KeyList(MetaOutoutBase):
    report_name = 'key_list'
    only_single = True
    only_both = False
    # key_list (either cat or diat)

    def _generate(self, **kwargs):
        tmp_ret = []
        for item in self.items:
            tmp_ret.append(item.key)
        return tmp_ret


class MR_FormattedList(MetaOutoutBase):
    report_name = 'formatted_list'
    only_single = False
    only_both = False
    # formatted_string (any)
    single_cat_format = '[{status}] - {name}: ({description})'
    single_diag_format = '[{status}] {description}'
    both_cat_format = '{name}: [{status}]((SPLIT))({description})'
    both_diag_format = '{indent}- {description}'

    def _generate(self, **kwargs):
        indent = kwargs.get('indent', 4)
        indent_str = ''.rjust(indent, ' ')
        tmp_ret = []
        if self.inc_both:
            for item in self.items:
                tmp_add = item.format(self.both_cat_format)
                tmp_ret.extend(tmp_add.split('((SPLIT))'))
                for diag in self.sub_items[item.key]:
                    tmp_add = diag.format(self.both_diag_format, indent=indent_str)
                    tmp_ret.extend(tmp_add.split('((SPLIT))'))
        else:
            if self.inc_diag:
                tmp_fmt = self.single_diag_format
            else:
                tmp_fmt = self.single_cat_format
            for item in self.items:
                tmp_ret.append(item.format(tmp_fmt, indent=indent_str))

        return tmp_ret


class MR_FormattedString(MetaOutoutBase):
    report_name = 'formatted_string'
    only_single = False
    only_both = False

    # formatting strings

    single_wrapper_format = '{items}'
    single_cat_format = '[{status}] - {name}: ({description})'
    single_diag_format = '[{status}] {description}'
    single_item_separetor = '\n'

    both_wrapper_format = '{cats}'
    both_cat_format = '{name}: [{status}]\n({description})\n{diags}'
    both_diag_format = '{indent}- {description}'
    both_diag_separetor = '\n'
    both_cat_separetor = '\n\n'

    def _generate(self, **kwargs):
        indent = kwargs.get('indent', 4)
        indent_str = ''.ljust(indent, ' ')
        if self.inc_both:
            tmp_lst = []
            for item in self.items:
                tmp_diags_list = []
                for diag in self.sub_items[item.key]:
                    tmp_diags_list.append(diag.format(self.both_diag_format, indent=indent_str))
                tmp_diags = self.both_diag_separetor.join(tmp_diags_list)
                tmp_cat = item.format(self.both_cat_format, indent=indent_str, diags=tmp_diags)
                tmp_lst.append(tmp_cat)
            tmp_ret = self.both_cat_separetor.join(tmp_lst)
            tmp_ret = self.both_wrapper_format.format(cats=tmp_ret, indent=indent_str)
            return tmp_ret
        else:
            tmp_lst = []
            if self.inc_diag:
                tmp_fmt = self.single_diag_format
            else:
                tmp_fmt = self.single_cat_format

            for item in self.items:
                tmp_lst.append(item.format(tmp_fmt))
            tmp_ret = self.single_item_separetor.join(tmp_lst)
            tmp_ret = self.single_wrapper_format.format(items=tmp_ret, indent=indent_str)
            return tmp_ret


class MR_DescList(MR_FormattedList):
    report_name = 'desc_list'
    single_cat_format = '[{status}] - {name}: ({description})'
    single_diag_format = '[{status}] {description}'
    both_cat_format = '{name}: [{status}]((SPLIT))({description})'
    both_diag_format = '{indent}- {description}'
    return_as_list = True


class MR_DocumentString(MR_FormattedString):
    report_name = 'document_string'
    only_both = True

    single_cat_format = '{key} [{status}]: {name}\n{diags}'
    single_diag_format = '{key} [{status}]: {description}'

    both_cat_format = '{key} [{status}]: {name}\n{diags}'
    both_diag_format = '{indent}{key}: {dif_status}{description}'


_meta_formatters = [MetaOutoutBase, MR_KeyDict, MR_ObjDict, MR_ObjList,
    MR_KeyList, MR_FormattedString, MR_DescList, MR_DocumentString]


class MetaLookup(object):
    default_key_format = '[{status}] {key}'
    default_desc_format = '[{status}] {description}'

    def __init__(self, error_on_warning=False, *error_on_code):
        # self.by_value = {}
        # self.by_key = {}
        self.results = ISEMAIL_RESULT_CODES
        self.categories = MetaList()
        self.diags = MetaList()
        self.lookup = MetaList()
        self.statuses = {
            'WARNING': [],
            'ERROR': [],
            'OK': []}

        self.default_format = self.default_desc_format

        # self.categories = MetaList(MetaCat, self, ISEMAIL_RESP_CATEGORIES)
        # self.diags = MetaList(MetaDiag, self, ISEMAIL_DIAG_RESPONSES)

        for key, item in ISEMAIL_RESP_CATEGORIES.items():
            tmp_cat = MetaCat(key, item, self)
            if key in self.lookup:
                raise AttributeError('%s already exists!' % key)
            self.categories[key] = tmp_cat
            self.lookup[key] = tmp_cat

        for key, item in ISEMAIL_DIAG_RESPONSES.items():
            tmp_diag = self.lookup[item['category']].add_diag(key, item)
            if key in self.lookup:
                raise AttributeError('%s already exists!' % key)
            self.diags[key] = tmp_diag
            self.lookup[key] = tmp_diag

        self.error_codes = {}

        if error_on_warning:
            self.set_error_on_warning(reload=False)
        if error_on_code:
            self.set_error_on(*error_on_code, reload=False)

        self._load_codes()

        self._formatters = {}
        for f in _meta_formatters:
            self._formatters[f.report_name] = f(self)

    def set_default_format(self, format_str=None, to_desc=False, to_key=False):
        if format_str is not None:
            self.default_format = format_str
        elif to_desc:
            self.default_format = self.default_desc_format
        elif to_key:
            self.default_format = self.default_key_format

    def __getitem__(self, item):
        return self.lookup[item]

    def __contains__(self, item):
        return item in self.lookup

    def _load_codes(self):
        self.error_codes.clear()
        for c in self.diags.values():
            if c.status == ISEMAIL_RESULT_CODES.ERROR:
                self.error_codes[c.key] = c

    def clear_overrides(self):
        self.error_codes.clear()
        for c in self.categories.values(ordered=False):
            c.reset_status()
        for c in self.diags.values():
            c.reset_status()
            if c.status == ISEMAIL_RESULT_CODES.ERROR:
                self.error_codes[c.key] = c

    def set_error_on_warning(self, set_to=True, reload=True):
        for c in self.categories.values():
            if set_to and c._base_status == ISEMAIL_RESULT_CODES.WARNING:
                c.set_override_status(ISEMAIL_RESULT_CODES.ERROR)
            else:
                c.reset_status()

        if reload:
            self._load_codes()

    def set_error_on(self, *codes_to_error, reload=True):
        for code in codes_to_error:
            self._add_eo(code)
        if reload:
            self._load_codes()

    def _add_eo(self, obj_in):
        if isinstance(obj_in, (list, tuple)):
            self.set_error_on(*obj_in)
        else:
            self[obj_in].set_override_status(ISEMAIL_RESULT_CODES.ERROR)

    def status(self, diag):
        return self[diag].status

    def is_error(self, diag):
        if diag in self:
            return diag in self.error_codes
        else:
            raise KeyError('Diag %s not in system' % diag)

    def filter(self, diags=None, filter=None, show_all=True, ordered=False, return_key=False):

        if filter is not None:
            if isinstance(filter, str):
                filter = [filter]

            filter_dict = {'diags': [], 'cats': [], 'status': []}

            for f in filter:
                f = f.upper()
                if f in self.diags:
                    filter_dict['diags'].append(f)
                elif f in self.categories:
                    filter_dict['cats'].append(f)
                elif f in ('WARNING', 'ERROR', 'OK'):
                    filter_dict['status'].append(f)
                else:
                    raise AttributeError('Invalid filter string: %s' % f)
            filter = filter_dict

        if return_key:
            return self.diags.keys(show_all=show_all, filter=filter, ordered=ordered, within=diags)

        else:
            return self.diags.values(show_all=show_all, filter=filter, ordered=ordered, within=diags)

    def get_report(self, report_name, diags=None, show_all=True, filter=None, **kwargs):
        try:
            tmp_report = self._formatters[report_name]
        except KeyError:
            raise AttributeError('Report "%s" does not exist, valid reports = %r' % (report_name, self._formatters.keys()))

        tmp_diags = self.filter(diags=diags, filter=filter, show_all=show_all, ordered=True)

        return tmp_report.out(diags=tmp_diags, **kwargs)
    __call__ = get_report

    def max(self, *args):
        return self.max_obj(*args).key

    def max_obj(self, *args):
        tmp_list = []
        for a in args:
            tmp_list.append(self[a])
        return max(tmp_list)

    def max_value(self, *args):
        return self.max_obj(*args).value

    def max_status(self, *args):
        tmp_max = self.max_obj(*args)
        return tmp_max.key, tmp_max.status


META_LOOKUP = MetaLookup()

