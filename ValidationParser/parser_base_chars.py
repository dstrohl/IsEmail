__all__ = ['AT', 'at',
           'BACKSLASH', 'backslash',
           'CLOSESQBRACKET', 'closesqbracket',
           'CLOSEPARENTHESIS', 'closeparenthesis',
           'COLON', 'colon',
           'COMMA', 'comma',
           'CR', 'cr',
           'CRLF', 'crlf',
           'DIGIT','digit',
           'DOT','dot',
           'DOUBLECOLON', 'double_colon',
           'DQUOTE', 'dquote',
           'HEXDIG', 'hexdig',
           'HTAB', 'htab',
           'HYPHEN', 'hyphen',
           'ALPHA', 'alpha',
           'LET_DIG', 'let_dig',
           'LF', 'lf',
           'OPENPARENTHESIS', 'openparenthesis',
           'OPENSQBRACKET', 'opensqbracket',
           'SP', 'sp'
           ]

from helpers.general.general import make_char_str
from ValidationParser.parser_objects import CharParser, SingleCharParser, StringParser


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
LF = "\n"
OPENPARENTHESIS = '('
OPENSQBRACKET = '['
SP = ' '
CRLF = '\r\n'

DIGIT = '1234567890'
HEXDIG = '1234567890abcdefABCDEF'

ALPHA = make_char_str((65, 90), (97, 122))
LET_DIG = make_char_str(ALPHA, DIGIT)

#
# class SingleDot(PHInvalidNext, PHBaseSingleChar):
#     look_for = DOT
#     invalid_next_char = DOT
#     invalid_next_char_msg = {'key': 'INVALID_NEXT_CHAR', 'description': 'Segment has two dots together'}

# single_dot = SingleDot(name='single_dot')
alpha = CharParser(look_for=ALPHA, name='ALPHA')
at = SingleCharParser(look_for=AT, name='AT')
backslash = SingleCharParser(look_for=BACKSLASH, name='BACKSLASH')
closeparenthesis = SingleCharParser(look_for=CLOSEPARENTHESIS, name='CLOSEPARENTHESIS')
closesqbracket = SingleCharParser(look_for=CLOSESQBRACKET, name='CLOSESQBRACKET')
colon = SingleCharParser(look_for=COLON, name='COLON')
comma = SingleCharParser(look_for=COMMA, name='COMMA')
cr = SingleCharParser(look_for=CR, name='CR')
crlf = StringParser(look_for=CRLF, name='CRLF')
digit = CharParser(look_for=DIGIT, name='DIGIT')
dot = SingleCharParser(look_for=DOT, name='DOT')
dquote = SingleCharParser(look_for=DQUOTE, name='DQUOTE')
hexdig = SingleCharParser(look_for=HEXDIG, name='HEXDIG')
htab = SingleCharParser(look_for=HTAB, name='HTAB')
hyphen = SingleCharParser(look_for=HYPHEN, name='HYPHEN')
lf = SingleCharParser(look_for=LF, name='LF')
openparenthesis = SingleCharParser(look_for=OPENPARENTHESIS, name='OPENPARENTHESIS')
opensqbracket = SingleCharParser(look_for=OPENSQBRACKET, name='OPENSQBRACKET')
sp = CharParser(look_for=SP, name='SP')
let_dig = CharParser(look_for=LET_DIG, name='LET_DIG')
double_colon = StringParser(look_for=DOUBLECOLON, name='DOUBLECOLON')
