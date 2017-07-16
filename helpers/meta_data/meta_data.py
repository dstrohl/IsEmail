from enum import IntEnum

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




GENERAL ERRORS:
    Invalid Character
    Invalid Length - Too Long
    Invalid Length - Too Short
    Unclosed String
    Invalid Location
    Missing Character
    Invalid End Character
    Invalid Start Character
    Missing Segment

GENERAL WARNINGS:
    Deprecated Content
    Potential Error




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

# ------------------------------------------------------------------------
# References
# ------------------------------------------------------------------------

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
# <editor-fold "Diagnoses">

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
# </editor-fold>
# </editor-fold>  META DATA
