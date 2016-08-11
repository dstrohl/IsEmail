# from pyparsing import *
from pyparsing_adds import *


obs_no_ws_ctl = make_char_str((1, 8), 11, 12, (14, 31), 127)


AT = Literal('@')
BACKSLASH = Literal('\\')
CLOSEPARENTHESIS = Literal(')')
CLOSESQBRACKET = Literal(']').suppress()
COLON = Literal(':')
CR = Literal('\r').leaveWhitespace().setName('<cr>')
DOT = Literal('.')
DOUBLECOLON = Literal('::')
DQUOTE = Literal('"').suppress()
HTAB = Literal(make_char_str(9)).parseWithTabs().setName('<tab>')
HYPHEN = Literal('-')
IPV6TAG = CaselessLiteral('ipv6:')
LF = Literal('\n').leaveWhitespace().setName('<lf>')
OPENPARENTHESIS = Literal('(')
OPENSQBRACKET = Literal('[').suppress()
SP = Literal(' ')
N1 = Literal('1')
N2 = Literal('2')
N5 = Literal('5')

CRLF = MatchFirst([(CR + LF), CR, LF]).setName('CRLF')
DIGIT = Word('1234567890', max=1).leaveWhitespace()
HEXDIG = Word('1234567890abcdefABCDEF', min=1, max=4)


# ==================================================================
# IP Address Pieces  (IPv4)
# ==================================================================

# <editor-fold desc="************** Address Parsers *************************">

IPV4_0_5 = Word('012345', exact=1).setName('0-5')
IPV4_1_9 = Word('123456789', exact=1).setName('1-9')
IPV4_11_99 = Word(initChars='123456789', bodyChars='1234567890', exact=2).setName('11-99')
IPv4_100_199 = Word(initChars='1', bodyChars='1234567890', exact=3).setName('100-199')
IPv4_200_249 = And([Literal('2') + Word(initChars='01234', bodyChars='1234567890', exact=2)]).setName('200-249')
IPv4_250_255 = And([Literal('25') + IPV4_0_5]).setName('250-255')

snum                    = MatchFirst([
                                IPv4_200_249,
                                IPv4_250_255,
                                IPv4_100_199,
                                IPV4_11_99,
                                IPV4_1_9,
                                Literal('0')
                            ]).setName('ipv4_snum')

dot_snum                = DOT + snum
ipv4_address_lit_base   = Combine(snum + dot_snum + dot_snum + dot_snum).setName('ipv4_lit_addr')


# ==================================================================
# IP Address Pieces  (IPv6)
# ==================================================================


ipv6_hex                = HEXDIG.setName('hexdig')
ipv6_colon_hex          = COLON + ipv6_hex
ipv6_hex_colon          = ipv6_hex + COLON

# full ipv6 address
ipv6_full               = ipv6_hex + (ipv6_colon_hex * 7)

ipv6_comp_segment       = Optional(ipv6_hex + Optional((ipv6_colon_hex * (1, 5)))).setName('ipv6_comp_segment')

# compressed ipv6 address
ipv6_comp               = Count(CountIn(
                            (ipv6_comp_segment + DOUBLECOLON + ipv6_comp_segment),
                            COLON,
                            min=2,
                            max=7), max=12)


# ==================================================================
# IP Address Pieces  (IPv6 - v4)
# ==================================================================



# ipv6v4_comp_seg_colon    = Optional(ipv6_comp_segment + COLON).setName('ipv6_comp_seg_plus_colon')

ipv6v4_post_addr_only   = And([DOUBLECOLON, ipv4_address_lit_base]).setName('ipv6v4_post_addr_only')
ipv6v4_post_v6_then_v4  = And([DOUBLECOLON,
                               ipv6_hex,
                               COLON,
                               Optional(OneOrMore(ipv6_hex_colon)).setName('opt_more_hex_colon'),
                               ipv4_address_lit_base]).setName('ipv6v4_post_v6_then_v6')

ipv6v4_comp             = Count(ipv6_comp_segment + Or([ipv6v4_post_v6_then_v4, ipv6v4_post_addr_only]), max=12)

# debugging, can remove
# ipv6_comp_segment.setDebug()
# ipv6v4_comp_seg_colon.setDebug()
# ipv6_comp.setDebug()
# ipv6v4_comp.setDebug()
# ipv6v4_post_addr_only.setDebug()
# ipv6v4_post_v6_then_v4.setDebug()


ipv6v4_full             = ipv6_hex + (ipv6_colon_hex * 5) + COLON + Combine(ipv4_address_lit_base)


ipv6_addr               = Combine(Or([
                            ipv6v4_full.setName('ipv6v4_full'),
                            ipv6_full.setName('ipv6_full'),
                            ipv6v4_comp.setName('ipv6v4_comp'),
                            ipv6_comp.setName('ipv6_comp')]))('ipv6_address_literal')
# </editor-fold>


# ==================================================================
# Text Blocks
# ==================================================================


# control chars not including NULL / CR / LF / TAB / DEL
OBS_NO_WS_CTL = make_char_str((1, 8), 11, 12, (14, 31), 127)
WSP = ' \t'
ALPHA = make_char_str((65, 90), (97, 122))
NUM = make_char_str((48, 57))


# ----- string bases -----------------------
SPECIALS = Word('()<>[]:;@\\,."')

# all chars = obs_no_ws_ctl + NULL + CR + LF
OBS_QP = Word(make_char_str(0, obs_no_ws_ctl, '\r', '\n')).leaveWhitespace().parseWithTabs()

# printable minus "[]\" plus control chars
DTEXT_CHARS = Word(make_char_str((33, 90), (94, 126), obs_no_ws_ctl)).leaveWhitespace().parseWithTabs()

# printable chars - minus space
vchar_chars = make_char_str((33, 126))
VCHAR = Word(make_char_str((33, 126))).leaveWhitespace().parseWithTabs()

# printable - 34, 92 " "\ "  + obs_qtext(ctrl chars)
OBS_QTEXT = Word(make_char_str(33, (35, 91), (93, 126))).leaveWhitespace().parseWithTabs().setName('obs_qtext)')
current_QTEXT = Word(make_char_str(33, (35, 91), (93, 126), obs_no_ws_ctl)).leaveWhitespace().parseWithTabs().setName('current_qtext')
QTEXT = Or([OBS_QTEXT, current_QTEXT]).setName('qtext')



# printable minus "[]\" plus control chars
DCONTENT = Word(make_char_str((33, 90), (94, 126))).leaveWhitespace().parseWithTabs()

# LTR_DIG = Word(make_char_str((65, 90), (48, 57), (97, 122))).leaveWhitespace().parseWithTabs()
LTR_STR = Word(initChars=make_char_str((65, 90), (48, 57), (97, 122), '-'),
               bodyChars=make_char_str((65, 90), (48, 57), (97, 122))).leaveWhitespace().parseWithTabs()

# all printable minus specials
ATEXT = Word(make_char_str((65, 90), (48, 57), (97, 122), "!#$%&'*+- = ?^_`{|}~")).leaveWhitespace().parseWithTabs()

# WSP             =   SP / HTAB          ; white space
one_wsp                 = White(WSP).setName('1WSP')
zero_plus_wsp           = White(WSP, min=0).setName('*WSP')

#  obs-FWS         =   1*([CRLF] WSP)     ; As amended in erratum #1908
# FWS             =   ([*WSP CRLF] 1*WSP) /  obs-FWS
#                                       ; Folding white space

current_fws             = (Optional(zero_plus_wsp + CRLF) + one_wsp).leaveWhitespace().parseWithTabs().setName('current_fws')
obs_fws                 = Or((Optional(zero_plus_wsp + CRLF) + one_wsp) | OneOrMore(Optional(CRLF) + one_wsp))('obs_fws').leaveWhitespace().parseWithTabs().setName('obs_fws')
fws                     = Or([current_fws | obs_fws]).suppress().setName('fws')
opt_fws                 = Optional(fws).setName('optional_fws')


# ==================================================================
# Address Literal
# ==================================================================

standard_tag            = LTR_STR
general_address_literal = Combine(standard_tag + COLON + DCONTENT)

ipv6_address_literal    = Combine(IPV6TAG + ipv6_addr)
addr_lit                = ipv4_address_lit_base('ipv4_address_literal') | ipv6_address_literal | general_address_literal('general_address_literal')
quoted_address_literal  = And([OPENSQBRACKET + addr_lit + CLOSESQBRACKET])
address_literal         = And([quoted_address_literal])('address_literal')



# ==================================================================
# Address Blocks
# ==================================================================

# ----- Quoted Pairs -----------------

# obs-qp         =   "\" (%d0 / obs-NO-WS-CTL / LF / CR)
obs_qp                  = And([BACKSLASH.copy().suppress(), (Word(vchar_chars, exact=1) | OBS_QP)])('obs_qp')

# quoted-pair     =   ("\" (VCHAR / WSP)) / obs-qp
current_quoted_pair     = (BACKSLASH.copy().suppress() + (Word(vchar_chars, exact=1) | WSP))
quoted_pair             = Or([current_quoted_pair, obs_qp])

'''
# ----- Comments -----------------

# see below
comment                 = Forward()
# ccontent        =   ctext / quoted-pair / comment
ccontent                = Or([CTEXT, quoted_pair, comment]).setName('c_content')
ccontent                = ccontent('comment')
# CFWS            =   (1*([FWS] comment) [FWS]) / FWS
cfws                    = Optional(Or([Optional(OneOrMore(opt_fws, comment) + opt_fws), fws])).setName('cfws')

# comment         =   "(" *([FWS] ccontent) [FWS] ")"
comment                 << OPENPARENTHESIS + ZeroOrMore(opt_fws + ccontent + opt_fws) + CLOSEPARENTHESIS
comment                 = Combine(comment).setName('comment')
'''

# ----- Comments -----------------
# printable - 40, 41, 92  "()\"

OBS_CTEXT               = Word(make_char_str((33, 39), (42, 91), (93, 126), obs_no_ws_ctl)).leaveWhitespace().parseWithTabs().setName('OBS_CTEXT')
Current_CTEXT           = Word(make_char_str((33, 39), (42, 91), (93, 126))).leaveWhitespace().parseWithTabs().setName('Current_CTEXT')
CTEXT                   =  MatchFirst([current_QTEXT, OBS_CTEXT]).setName('CTEXT')('comment')


# see below
#.. comment                 = Forward()
# ccontent        =   ctext / quoted-pair / comment
#ccontent                = CTEXT.setName('c_content')
#ccontent                = ccontent('comment')
# ctext                   = CTEXT.copy().setName('ctext')('comment')
ccontent                = Optional(Combine(OneOrMore(opt_fws + CTEXT + opt_fws))).setName('ccontent')
#comment                 = nestedExpr(content=ccontent)
comment = nestedExpr()
# comment                 << OPENPARENTHESIS + ZeroOrMore(opt_fws + ccontent + opt_fws) + CLOSEPARENTHESIS
# comment                 = Combine(comment).setName('comment')


# CFWS            =   (1*([FWS] comment) [FWS]) / FWS
cfws                    = Optional(Or([Optional(OneOrMore(opt_fws, comment) + opt_fws), fws])).setName('cfws')

# comment         =   "(" *([FWS] ccontent) [FWS] ")"




#    qcontent        =   qtext / quoted-pair
#
#   quoted-string   =   [CFWS]
#                       DQUOTE *([FWS] qcontent) [FWS] DQUOTE
#                       [CFWS]
qcontent                = Or([QTEXT, quoted_pair]).setName('qcontent')
combined_qcontent       = Combine(OneOrMore(opt_fws + qcontent)).setName('quoted_content')('quoted_content')
cc1                     = DQUOTE + combined_qcontent + opt_fws + DQUOTE
quoted_string           = cfws + DQUOTE + combined_qcontent + opt_fws + DQUOTE + cfws

dot_atom_text           = OneOrMore(ATEXT) + ZeroOrMore(DOT + ATEXT)
dot_atom                = cfws + dot_atom_text + cfws
atom                    = cfws + ATEXT + cfws
word                    = atom | quoted_string
obs_local_part          = word + ZeroOrMore(DOT + word)

obs_domain              = atom + ZeroOrMore(DOT + atom)

# ----- buiding text blocks -----------------

# dtext           =   %d33-90 /          ; Printable US-ASCII
#                    %d94-126 /         ;  characters not including
#                    obs-dtext          ;  "[", "]", or "\"
#
# obs-dtext       =   obs-NO-WS-CTL / quoted-pair
dtext                   = DTEXT_CHARS | quoted_pair

domain_literal          = cfws + OPENSQBRACKET + ZeroOrMore(opt_fws + dtext) + opt_fws + CLOSESQBRACKET + cfws

# ==================================================================
# Address Elements
# ==================================================================

domain_part             = dot_atom | domain_literal | address_literal | obs_domain
local_part              = dot_atom | quoted_string | obs_local_part
addr_spec               = local_part + AT + domain_part
