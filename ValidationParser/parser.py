from ValidationParser.parser_responses import ParseFullResult, ParseShortResult
from ValidationParser.footballs import ParsingObj
from enum import Enum

__all__ = ['parse', 'RETURN_TYPES']


class RETURN_TYPES(Enum):
    long = 'long'
    short = 'short'
    bool = 'bool'
    football = 'football'


RETURN_TYPE_LOOKUP = {
    RETURN_TYPES.long: ParseFullResult,
    RETURN_TYPES.short: ParseShortResult,
    RETURN_TYPES.bool: bool,
    RETURN_TYPES.football: None,
    'long': ParseFullResult,
    'short': ParseShortResult,
    'bool': bool,
    'football': None
}


def parse(parse_item, init_parser,
          begin=0,
          return_type=RETURN_TYPES.short,
          def_pass_msg='VALID',
          def_fail_msg='ERROR',
          def_empty_msg='EMPTY_PARSE_STRING',
          def_unparsed_content_msg='UNPARSED_CONTENT',
          lookup_reset=False,
          **kwargs):
    if isinstance(parse_item, str):
        parse_item = ParsingObj(parse_item, **kwargs)

    if lookup_reset:
        parse_item.message_lookup.clear()

    if len(parse_item) == 0:
        tmp_ret = parse_item.fb(position=begin)
        if def_empty_msg is not None:
            tmp_ret(def_empty_msg)
    else:
        tmp_ret = init_parser(parse_item, begin)

        if tmp_ret and def_unparsed_content_msg is not None and tmp_ret.l != len(parse_item):
            tmp_ret(def_unparsed_content_msg)

        if len(tmp_ret._messages) == 0:
            if tmp_ret and def_pass_msg is not None:
                tmp_ret(def_pass_msg)
            elif def_fail_msg is not None:
                tmp_ret(def_fail_msg)

    try:
        tmp_ret_type = RETURN_TYPE_LOOKUP[return_type]
    except KeyError:
        raise AttributeError('Invalid Return Type: %s' % return_type)

    if tmp_ret_type is None:
        return tmp_ret
    else:
        return tmp_ret_type(tmp_ret)
