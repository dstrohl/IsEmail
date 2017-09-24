from ValidationParser.parser_responses import ParseFullResult, ParseShortResult
from ValidationParser.footballs import ParsingObj
from ValidationParser.parser_objects import BaseParser
from ValidationParser.parser_messages import MessageLookup
from enum import Enum
from typing import Union

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
    'football': None,
    2: ParseFullResult,
    1: ParseShortResult,
    0: bool,
    3: None
}


def parse(parse_item: Union[str, ParsingObj],
          init_parser: Union[BaseParser, ],
          begin: int = 0,
          verbose: int = 1,
          def_pass_msg: Union[str, None] = 'VALID',
          def_fail_msg: Union[str, None] = 'ERROR',
          def_empty_msg: Union[str, None] = 'EMPTY_PARSE_STRING',
          def_unparsed_content_msg: Union[str, None] = 'UNPARSED_CONTENT',
          lookup_reset: bool = False,
          trace_level: int = -1,
          raise_on_error: bool = False,
          message_lookup: Union[MessageLookup, dict, None] = None,
          local_msg_overrides: Union[str, list, dict, None] = None,
          **kwargs) -> Union[bool, ParseShortResult, ParseFullResult]:

    if isinstance(parse_item, str):
        parse_item = ParsingObj(
            parse_item,
            verbose=verbose,
            trace_level=trace_level,
            raise_on_error=raise_on_error,
            message_lookup=message_lookup,
            local_msg_overrides=local_msg_overrides)

    # if lookup_reset:
    #     parse_item.message_lookup.clear()

    if not init_parser.is_segment:
        raise AttributeError('Initial parser must be a segment type: %r' % init_parser)

    if len(parse_item) == 0:
        tmp_ret = parse_item.fb(position=begin)
        if def_empty_msg is not None:
            tmp_ret(def_empty_msg)
    else:
        tmp_ret = init_parser.run(parse_item, begin, **kwargs)

        if tmp_ret and def_unparsed_content_msg is not None and tmp_ret.l < len(parse_item):
            tmp_ret(def_unparsed_content_msg)

        if len(tmp_ret._messages) == 0:
            if tmp_ret and def_pass_msg is not None:
                tmp_ret(def_pass_msg)
            elif def_fail_msg is not None:
                tmp_ret(def_fail_msg)

    try:
        tmp_ret_type = RETURN_TYPE_LOOKUP[verbose]
    except KeyError:
        raise AttributeError('Invalid verbose_level: %s' % verbose)

    if tmp_ret_type is None:
        return tmp_ret
    else:
        return tmp_ret_type(tmp_ret)
