from helpers.parser_helpers import *
from unittest import TestCase

class TestSimpleParsers(TestCase):

    def test_colon(self):
        po = ParsingObj(':')
        tmp_ret = colon(po)
        self.assertTrue(tmp_ret)


"""
class PHBase(object):
    parser = True
    is_history_item = True
    is_segment_item = True

    name = None
    description = None
    references = None

    on_pass_msg = name, 'VALID'
    on_fail_msg = name, 'ERROR'

    def _parse(self, parse_obj, position, **kwargs):
        tmp_ret = parse_obj.fb(position)
        return tmp_ret

    def super_call(self, *args, **kwargs):
        try:
            tmp_ret = super().__call__(*args, **kwargs)
        except AttributeError:
            tmp_ret = self._parse(*args, **kwargs)
        return tmp_ret

    def __call__(self, parse_obj, position, **kwargs):
        tmp_err = None
        position = int(position)
        name = self.name or self.__name__

        parse_obj.begin_stage(name, position=position)

        raise_error = False

        if not parse_obj.at_end(position):
            try:
                tmp_ret = self.super_call(parse_obj, position, **kwargs)
            except ParsingError as err:
                tmp_err = err
                raise_error = True
                tmp_ret = err.results
        else:
            tmp_ret = parse_obj.fb(position)

        if tmp_ret:
            if self.is_history_item:
                tmp_ret.set_history(name)
            if self.on_pass_msg:
                if isinstance(self.on_pass_msg, str):
                    pass_d = [self.on_pass_msg]
                else:
                    pass_d = self.on_pass_msg
                tmp_ret(*pass_d)

        elif self.on_fail_msg:
            if isinstance(self.on_fail_msg, str):
                fail_d = [self.on_fail_msg]
            else:
                fail_d = self.on_fail_msg
            tmp_ret(*fail_d)

        parse_obj.end_stage(tmp_ret, raise_error=raise_error)

        if raise_error:
            raise tmp_err


class PHBaseSingleChar(PHBase):
    look_for = None
    caps_sensitive = True

    def _parse(self, parse_obj, position, **kwargs):
        tmp_ret = parse_obj.fb(position)
        if self.look_for is None:
            return tmp_ret

        if self.caps_sensitive:
            tmp_check = parse_obj[position].lower()
            parse_for = self.look_for.lower()
            if tmp_check in parse_for:
                return tmp_ret(1)
        else:
            if parse_obj[position] == self.look_for:
                return tmp_ret(1)
        return tmp_ret


class PHBaseString(PHBase):
    look_for = None
    caps_sensitive = True

    def _parse(self, parse_obj, position, **kwargs):
        tmp_ret = parse_obj.fb(position)
        if self.look_for is None:
            return tmp_ret

        tmp_len = len(self.look_for)
        tmp_check = parse_obj.mid(position, tmp_len)

        if self.caps_sensitive:
            tmp_check = tmp_check.lower()
            parse_for = self.look_for.lower()
        else:
            parse_for = self.look_for

        if tmp_check == parse_for:
            tmp_ret += tmp_len

        return tmp_ret


class PHBaseChar(PHBase):
    look_for = None
    char_until_char = None
    min_char_count = -1
    max_char_count = 9999
    min_char_count_msg = 'SEGMENT_TOO_SHORT'
    caps_sensitive = True

    def _parse(self, parse_obj, position, **kwargs):
        tmp_ret = parse_obj.fb(position)
        tmp_count = 0
        if self.look_for is None:
            return tmp_ret

        if self.char_until_char is None:
            looper = parse_obj.remaining_complex(begin=position, count=self.max_char_count)
        else:
            looper = parse_obj.remaining_complex(begin=position, count=self.max_char_count,
                                                 until_char=self.char_until_char)

        if self.caps_sensitive:
            parse_for = self.look_for.lower()
            looper = looper.lower()

        else:
            parse_for = self.look_for

        for i in looper:
            if i in parse_for:
                tmp_count += 1
            else:
                if tmp_count >= self.min_char_count:
                    return tmp_ret(tmp_count)
                else:
                    return tmp_ret(self.min_char_count_msg)

        if tmp_count >= self.min_char_count:
            return tmp_ret(tmp_count)
        return tmp_ret


class PHInvalidNext(object):
    invalid_next_char = None
    invalid_next_char_msg = 'INVALID_NEXT_CHAR'

    def __call__(self, parse_obj, position, **kwargs):
        tmp_ret = self.super_call(parse_obj, position, **kwargs)
        if tmp_ret and not parse_obj.at_end(position + 1) and parse_obj[position + 1] in self.invalid_next_char:
            tmp_ret(self.invalid_next_char_msg)
        return tmp_ret


class PHEnclosed(object):
    parser = True
    enclosure_start = '"'
    enclosure_stop = '"'
    skip_quoted = True
    unclosed_msg = 'UNCLOSED_STRING'


class PHMinLen(object):
    parser = True
    min_length = None
    min_length_msg = 'SEGMENT_TOO_LONG'


class PHMaxLen(object):
    parser = True
    max_length = None
    max_length_msg = 'SEGMENT_TOO_SHORT'


class PHInvalidStartStop(object):
    invalid_start_chars = None
    invlaid_start_chars_msg = 'INVALID_START'
    invalid_end_chars = None
    invlaid_end_chars_msg = 'INVALID_END'


class alpha(PHBaseSingleChar):
    look_for = ALPHA


class at(PHBaseSingleChar):
    look_for = AT


class backslash(PHBaseSingleChar):
    look_for = BACKSLASH


class closeparenthesis(PHBaseSingleChar):
    look_for = CLOSEPARENTHESIS


class closesqbracket(PHBaseSingleChar):
    look_for = CLOSESQBRACKET


class colon(PHBaseSingleChar):
    look_for = COLON


class comma(PHBaseSingleChar):
    look_for = COMMA


class cr(PHBaseSingleChar):
    look_for = CR


class crlf(PHBaseString):
    look_for = CRLF


class digit(PHBaseSingleChar):
    look_for = DIGIT


class dot(PHBaseSingleChar):
    look_for = DOT


class dquote(PHBaseSingleChar):
    look_for = DQUOTE


class hexdig(PHBaseSingleChar):
    look_for = HEXDIG


class htab(PHBaseSingleChar):
    look_for = HTAB


class hyphen(PHBaseSingleChar):
    look_for = HYPHEN


class lf(PHBaseSingleChar):
    look_for = LF


class openparenthesis(PHBaseSingleChar):
    look_for = OPENPARENTHESIS


class opensqbracket(PHBaseSingleChar):
    look_for = OPENSQBRACKET


class sp(PHBaseSingleChar):
    look_for = SP


class let_dig(PHBaseSingleChar):
    look_for = LET_DIG


class single_dot(PHBaseSingleChar, PHInvalidNext):
    look_for = DOT
    invalid_next_char = DOT
    invalid_next_char_msg = {'name': 'INVALID_NEXT_CHAR', 'description': ''}


class double_colon(PHBaseString):
    look_for = DOUBLECOLON

"""