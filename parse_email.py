from pyparsing import *

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

obs_no_ws_ctl = make_char_str((1, 8), 11, 12, (14, 31), 127)


AT = Literal('@')
BACKSLASH = Literal('\\')
CLOSEPARENTHESIS = Literal(')')
CLOSESQBRACKET = Literal(']')
COLON = Literal(':')
# CR = Literal(make_char_str(13))
# CR = Literal(srange('\x0D'))
CR = Literal('\x0D')
DOT = Literal('.')
DOUBLECOLON = Literal('::')
DQUOTE = Literal('"')
HTAB = Literal(make_char_str(9))
HYPHEN = Literal('-')
IPV6TAG = CaselessLiteral('ipv6:')
LF = Literal(make_char_str(10))
OPENPARENTHESIS = Literal('(')
OPENSQBRACKET = Literal('[')
SP = Literal(' ')
N1 = Literal('1')
N2 = Literal('2')
N5 = Literal('5')

# US-ASCII visible characters not valid for atext (http:#tools.ietf.org/html/rfc5322#section-3.2.3)

CRLF = CR | LF | (CR + LF)
DIGIT = Word('1234567890', max=1)
HEXDIG = Word('1234567890abcdefABCDEF', min=1, max=4)
IPV4_04 = Word('01234', max=1)
IPV4_05 = Word('012345', max=1)
IPV4_12 = Word('12', max=1)
IPV4_19 = Word('123456789', max=1)

OBS_NO_WS_CTL = make_char_str((1, 8), 11, 12, (14, 31), 127)
SPECIALS = '()<>[]:;@\\,."'
WSP = ' \t'

OBS_QP = Word(make_char_str(0, obs_no_ws_ctl, '\r', '\n'))
DTEXT = Word(make_char_str((33, 90), (94, 126), obs_no_ws_ctl))
VCHAR = Word(make_char_str((33, 126), ' \t'))
QTEXT = Word(make_char_str(33, (35, 91), (93, 126), obs_no_ws_ctl))
OBS_CTEXT = Word(obs_no_ws_ctl)
OBS_DTEXT = OBS_CTEXT
OBS_QTEXT = OBS_CTEXT
CTEXT = Word(make_char_str((33, 39), (42, 91), 93, 126, obs_no_ws_ctl))
DCONTENT = Word(make_char_str((33, 90), (94, 126)))

LTR_DIG = Word(make_char_str((68, 90), (48, 57), (97, 122)))
LTR_STR = Word(make_char_str((68, 90), (48, 57), (97, 122), '-'))
ATEXT = Word(make_char_str((68, 90), (48, 57), (97, 122), "!#$%&'*+- = ?^_`{|}~"))



snum_3_digit            = (N1 + DIGIT + DIGIT) | (N2 + IPV4_04 + DIGIT) | (N2 + N5 + IPV4_05)
snum                    = IPV4_19 | IPV4_19 + DIGIT | snum_3_digit
dot_snum                = DOT + snum
ipv4_address_literal    = snum + dot_snum + dot_snum + dot_snum

standard_tag            = LTR_STR + LTR_DIG
general_address_literal = standard_tag + COLON + DCONTENT

ipv6_hex                = HEXDIG
ipv6_colon_hex          = COLON + ipv6_hex
ipv6_dcolon_hex         = DOUBLECOLON + ipv6_hex
ipv6_colon_hex_x3       = ipv6_colon_hex * 3
ipv6_colon_hex_x5       = ipv6_colon_hex * 5

ipv6_comp               = ipv6_hex + OneOrMore(ipv6_colon_hex) + COLON + OneOrMore(ipv6_colon_hex)
ipv6v4_comp             = ipv6_comp + COLON + ipv4_address_literal
ipv6_full               = ipv6_hex + (ipv6_dcolon_hex * 7)
ipv6v4_full               = ipv6_hex + (ipv6_colon_hex * 5) + ipv4_address_literal

ipv6_addr               = ipv6_full | ipv6_comp | ipv6v4_full | ipv6v4_comp
ipv6_address_literal    = IPV6TAG + ipv6_addr

addr_lit                = ipv4_address_literal | ipv6_address_literal | general_address_literal
address_literal         = OPENSQBRACKET + addr_lit + CLOSESQBRACKET

obs_qp                  = BACKSLASH | OBS_QP
quoted_pair             = (BACKSLASH + VCHAR) | obs_qp

one_wsp                 = White(WSP)
zero_plus_wsp           = White(WSP, min=0)
obs_fws                 = OneOrMore(CRLF + one_wsp)
fws                     = (Optional(zero_plus_wsp + CRLF) + one_wsp) | obs_fws
opt_fws                 = Optional(fws)
comment                 = Forward()

ccontent                = CTEXT | quoted_pair | comment
cfws                    = Optional(OneOrMore(opt_fws, comment) + opt_fws) | fws

comment                 << OPENPARENTHESIS + ZeroOrMore(opt_fws + ccontent + opt_fws) + CLOSEPARENTHESIS
qcontent                = QTEXT | quoted_pair
quoted_string           = cfws + DQUOTE + OneOrMore(opt_fws + qcontent) + opt_fws + DQUOTE + cfws
dot_atom_text           = OneOrMore(ATEXT) + ZeroOrMore(DOT + ATEXT)
dot_atom                = cfws + dot_atom_text + cfws
atom                    = cfws + ATEXT + cfws
word                    = atom | quoted_string
obs_local_part          = word + ZeroOrMore(DOT + word)

obs_domain              = atom + ZeroOrMore(DOT + atom)

domain_literal          = cfws + OPENSQBRACKET + ZeroOrMore(opt_fws + DTEXT) + opt_fws + CLOSESQBRACKET + cfws

domain_part             = dot_atom | domain_literal | address_literal | obs_domain
local_part              = dot_atom | quoted_string | obs_local_part
addr_spec               = local_part + AT + domain_part


if __name__ == '__main__':
    print(AT.parseString('@'))
    print(BACKSLASH.parseString('\\'))
    print(CLOSEPARENTHESIS.parseString('))'))
    print(CLOSESQBRACKET.parseString(']'))
    print(COLON.parseString(':'))
    print(CR.parseString('\x0D'))
    print(DOT.parseString('.'))
    print(DOUBLECOLON.parseString('::'))
    print(DQUOTE.parseString('"'))
    print(HTAB.parseString(make_char_str(9)))
    print(HYPHEN.parseString('-'))
    print(IPV6TAG.parseString('ipv6:'))
    print(LF.parseString(make_char_str(10)))
    print(OPENPARENTHESIS.parseString('('))
    print(OPENSQBRACKET.parseString('['))
    print(SP.parseString(' '))
    print(N1.parseString('1'))
    print(N2.parseString('2'))
    print(N5.parseString('5'))

    '''
    # US-ASCII visible characters not valid for atext (http:#tools.ietf.org/html/rfc5322#section-3.2.3)
    
    CRLF = CR | LF | (CR + LF)
    DIGIT = Word('1234567890', max=1)
    HEXDIG = Word('1234567890abcdefABCDEF', min=1, max=4)
    IPV4_04 = Word('01234', max=1)
    IPV4_05 = Word('012345', max=1)
    IPV4_12 = Word('12', max=1)
    IPV4_19 = Word('123456789', max=1)
    
    OBS_NO_WS_CTL = make_char_str((1, 8), 11, 12, (14, 31), 127)
    SPECIALS = '()<>[]:;@\\,."'
    WSP = ' \t'
    
    OBS_QP = Word(make_char_str(0, obs_no_ws_ctl, '\r', '\n'))
    DTEXT = Word(make_char_str((33, 90), (94, 126), obs_no_ws_ctl))
    VCHAR = Word(make_char_str((33, 126), ' \t'))
    QTEXT = Word(make_char_str(33, (35, 91), (93, 126), obs_no_ws_ctl))
    OBS_CTEXT = Word(obs_no_ws_ctl)
    OBS_DTEXT = OBS_CTEXT
    OBS_QTEXT = OBS_CTEXT
    CTEXT = Word(make_char_str((33, 39), (42, 91), 93, 126, obs_no_ws_ctl))
    DCONTENT = Word(make_char_str((33, 90), (94, 126)))
    
    LTR_DIG = Word(make_char_str((68, 90), (48, 57), (97, 122)))
    LTR_STR = Word(make_char_str((68, 90), (48, 57), (97, 122), '-'))
    ATEXT = Word(make_char_str((68, 90), (48, 57), (97, 122), "!#$%&'*+- = ?^_`{|}~"))
    
    
    
    snum_3_digit            = (N1 + DIGIT + DIGIT) | (N2 + IPV4_04 + DIGIT) | (N2 + N5 + IPV4_05)
    snum                    = IPV4_19 | IPV4_19 + DIGIT | snum_3_digit
    dot_snum                = DOT + snum
    ipv4_address_literal    = snum + dot_snum + dot_snum + dot_snum
    
    standard_tag            = LTR_STR + LTR_DIG
    general_address_literal = standard_tag + COLON + DCONTENT
    
    ipv6_hex                = HEXDIG
    ipv6_colon_hex          = COLON + ipv6_hex
    ipv6_dcolon_hex         = DOUBLECOLON + ipv6_hex
    ipv6_colon_hex_x3       = ipv6_colon_hex * 3
    ipv6_colon_hex_x5       = ipv6_colon_hex * 5
    
    ipv6_comp               = ipv6_hex + OneOrMore(ipv6_colon_hex) + COLON + OneOrMore(ipv6_colon_hex)
    ipv6v4_comp             = ipv6_comp + COLON + ipv4_address_literal
    ipv6_full               = ipv6_hex + (ipv6_dcolon_hex * 7)
    ipv6v4_full               = ipv6_hex + (ipv6_colon_hex * 5) + ipv4_address_literal
    
    ipv6_addr               = ipv6_full | ipv6_comp | ipv6v4_full | ipv6v4_comp
    ipv6_address_literal    = IPV6TAG + ipv6_addr
    
    addr_lit                = ipv4_address_literal | ipv6_address_literal | general_address_literal
    address_literal         = OPENSQBRACKET + addr_lit + CLOSESQBRACKET
    
    obs_qp                  = BACKSLASH | OBS_QP
    quoted_pair             = (BACKSLASH + VCHAR) | obs_qp
    
    one_wsp                 = White(WSP)
    zero_plus_wsp           = White(WSP, min=0)
    obs_fws                 = OneOrMore(CRLF + one_wsp)
    fws                     = (Optional(zero_plus_wsp + CRLF) + one_wsp) | obs_fws
    opt_fws                 = Optional(fws)
    comment                 = Forward()
    
    ccontent                = CTEXT | quoted_pair | comment
    cfws                    = Optional(OneOrMore(opt_fws, comment) + opt_fws) | fws
    
    comment                 << OPENPARENTHESIS + ZeroOrMore(opt_fws + ccontent + opt_fws) + CLOSEPARENTHESIS
    qcontent                = QTEXT | quoted_pair
    quoted_string           = cfws + DQUOTE + OneOrMore(opt_fws + qcontent) + opt_fws + DQUOTE + cfws
    dot_atom_text           = OneOrMore(ATEXT) + ZeroOrMore(DOT + ATEXT)
    dot_atom                = cfws + dot_atom_text + cfws
    atom                    = cfws + ATEXT + cfws
    word                    = atom | quoted_string
    obs_local_part          = word + ZeroOrMore(DOT + word)
    
    obs_domain              = atom + ZeroOrMore(DOT + atom)
    
    domain_literal          = cfws + OPENSQBRACKET + ZeroOrMore(opt_fws + DTEXT) + opt_fws + CLOSESQBRACKET + cfws
    
    domain_part             = dot_atom | domain_literal | address_literal | obs_domain
    local_part              = dot_atom | quoted_string | obs_local_part
    addr_spec               = local_part + AT + domain_part
   '''
    