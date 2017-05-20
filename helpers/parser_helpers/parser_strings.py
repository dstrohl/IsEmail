from helpers .general.general import make_char_str

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
