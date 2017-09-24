from helpers.general.general import make_char_str
from ValidationParser.parser_objects import CharParser, SingleCharParser, StringParser, register_parser

__all__ = ['CHARS', 'At', 'Backslash', 'CloseParenthesis', 'CloseSqBracket', 'Colon', 'Comma', 'Cr', 'CrLf', 'Digit',
           'Dot', 'Double_Colon', 'Dquote', 'Hexdig', 'Htab', 'Hyphen', 'Alpha', 'Let_Dig', 'Lf', 'OpenParenthesis',
           'OpenSqBracket', 'Sp'
           ]


class CHARS(object):
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

@register_parser
class Alpha(CharParser): 
    look_for = CHARS.ALPHA
    name = 'ALPHA'
    
@register_parser
class At(SingleCharParser):
    look_for = CHARS.AT
    name = 'AT'
    
    
@register_parser
class Backslash(SingleCharParser):
    look_for = CHARS.BACKSLASH
    name = 'BACKSLASH'


@register_parser
class CloseParenthesis(SingleCharParser):
    look_for = CHARS.CLOSEPARENTHESIS 
    name = 'CLOSEPARENTHESIS'


@register_parser
class CloseSqBracket(SingleCharParser):
    look_for = CHARS.CLOSESQBRACKET 
    name = 'CLOSESQBRACKET'


@register_parser
class Colon(SingleCharParser):
    look_for = CHARS.COLON 
    name = 'COLON'


@register_parser
class Comma(SingleCharParser):
    look_for = CHARS.COMMA
    name = 'COMMA'


@register_parser
class Cr(SingleCharParser):
    look_for = CHARS.CR 
    name = 'CR'


@register_parser
class CrLf(StringParser):
    look_for = CHARS.CRLF 
    name = 'CRLF'


@register_parser
class Digit(CharParser):
    look_for = CHARS.DIGIT 
    name = 'DIGIT'


@register_parser
class Dot(SingleCharParser):
    look_for = CHARS.DOT 
    name = 'DOT'


@register_parser
class Dquote(SingleCharParser):
    look_for = CHARS.DQUOTE 
    name = 'DQUOTE'


@register_parser
class Hexdig(SingleCharParser):
    look_for = CHARS.HEXDIG 
    name = 'HEXDIG'


@register_parser
class Htab(SingleCharParser):
    look_for = CHARS.HTAB 
    name = 'HTAB'


@register_parser
class Hyphen(SingleCharParser):
    look_for = CHARS.HYPHEN 
    name = 'HYPHEN'


@register_parser
class Lf(SingleCharParser):
    look_for = CHARS.LF 
    name = 'LF'


@register_parser
class OpenParenthesis(SingleCharParser):
    look_for = CHARS.OPENPARENTHESIS 
    name = 'OPENPARENTHESIS'


@register_parser
class OpenSqBracket(SingleCharParser):
    look_for = CHARS.OPENSQBRACKET 
    name = 'OPENSQBRACKET'


@register_parser
class Sp(CharParser):
    look_for = CHARS.SP 
    name = 'SP'


@register_parser
class Let_Dig(CharParser):
    look_for = CHARS.LET_DIG 
    name = 'LET_DIG'


@register_parser
class Double_Colon(StringParser):
    look_for = CHARS.DOUBLECOLON 
    name = 'DOUBLECOLON'
