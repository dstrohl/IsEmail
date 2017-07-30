from ValidationParser.parser_objects import *
from ValidationParser.parser_base_chars import *
from unittest import TestCase
from ValidationParser.exceptions import ParsingError
from ValidationParser.footballs import ParsingObj
from helpers.general.test_helpers import TestCaseApproxString


class TestSimpleParsers(TestCase):

    def test_colon(self):
        po = ParsingObj(':')
        tmp_ret = colon(po)
        self.assertTrue(tmp_ret)

    def test_parse_str(self):
        po = ParsingObj('abcdefghi')
        abc = StringParser(look_for='abc')

        tmp_ret = abc(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)

    def test_parse_str_fail(self):
        po = ParsingObj('abcdefghi')
        abc = StringParser(look_for='cab')

        tmp_ret = abc(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)


class TestCustomizedBaseFunctions(TestCaseApproxString):
    def test_is_segment(self):
        po = ParsingObj('abcdefghi')
        abc = CharParser(look_for='cab', name='test_seg')
        tmp_ret = abc(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        tmp_str_start = 'TRACE 9: (2/2 records, '
        tmp_str_end = 'seconds)\n(*** Including lines 1 to 2 ***)\n' \
                  '----------------------------------------------\nBegin test_seg: scanning from 0: ->\'abcdefghi\'<-\n' \
                  'End test_seg: Found 3 "abc" : [ test_seg / OK(3)  ]\n----------------------------------------------'
        self.assertApproxString(po.trace_str, tmp_str_start, tmp_str_end, max_skip=10, min_skip=1)
        # self.assertTrue(po.trace_str.startswith(tmp_str_start), po.trace_str)
        # self.assertTrue(po.trace_str.endswith(tmp_str_end), po.trace_str)

    def test_at_end(self):
        po = ParsingObj('abcdefghi')
        abc = CharParser(look_for='cab')
        tmp_ret = abc(po, 12)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)

    def test_raise_error(self):
        po = ParsingObj('abcdefghi', raise_on_error=True)
        abc = CharParser(look_for='xyz', on_fail_msg='ERROR')
        with self.assertRaises(ParsingError):
            tmp_ret = abc(po, 0)

    def test_pass_msg(self):
        po = ParsingObj('abcdefghi')
        abc = CharParser(look_for='abc', on_pass_msg='VALID')
        tmp_ret = abc(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        self.assertTrue('VALID' in tmp_ret)

    def test_pass_msg_on_fail(self):
        po = ParsingObj('abcdefghi')
        abc = CharParser(look_for='xyz', on_pass_msg='VALID')
        tmp_ret = abc(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('VALID' in tmp_ret)

    def test_fail_msg(self):
        po = ParsingObj('abcdefghi')
        abc = StringParser(look_for='xyz', on_fail_msg='ERROR')
        tmp_ret = abc(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('ERROR' in tmp_ret)

    def test_fail_msg_on_pass(self):
        po = ParsingObj('abcdefghi')
        abc = StringParser(look_for='abc', on_fail_msg='ERROR')
        tmp_ret = abc(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        self.assertFalse('ERROR' in tmp_ret)

    def test_history_item(self):
        po = ParsingObj('abcdefghi')
        abc = CharParser(look_for='cab', name='test_seg')
        tmp_ret = abc(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        self.assertEqual(tmp_ret.history, 'test_seg')


abc = CharNoSegment(look_for='cba') # , name='cba_char')
fed = CharNoSegment(look_for='fed') # , name='fed_char')
ghi = CharNoSegment(look_for='hig') # , name='ghi_char')
xyz = CharNoSegment(look_for='zxy') # , name='xyz_char')
abcd = CharNoSegment(look_for='cbad') # , name='abcd')
abdecg = CharNoSegment(look_for='abdecg') # , name='abdecg')

and_fixture = SubParsersParser(parsers=(abc, fed, ghi))


class TestAnd(TestCase):
    def test_and(self):
        po = ParsingObj('abcdefghi')
        # abc = PHBaseChar('cba', name='abc')
        # fed = PHBaseChar('fde', name='fed')
        # ghi = PHBaseChar('hig', name='ghi')

        # tmp_ret = abc._and(po, 0, fed, ghi)
        tmp_ret = and_fixture(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 9)

    def test_and_fail(self):
        po = ParsingObj('abcdefxyz')
        # abc = PHBaseChar('cba')
        # fed = PHBaseChar('fde')
        # ghi = PHBaseChar('zxy')

        # tmp_ret = abc._and(po, 0, fed, ghi)
        tmp_ret = and_fixture(po, 0)

        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)

or_fixture = SubParsersParser(parsers=(ghi, abc, fed), operation='or')


class TestOr(TestCase):
    def test_or(self):
        po = ParsingObj('abcdefghi')
        tmp_ret = or_fixture(po)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)

    def test_or_fail(self):
        po = ParsingObj('lmnop')

        tmp_ret = or_fixture(po)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)


# tmp_ret = abc._best(po, 0, abcd, ghi)


class BestFixture(SubParsersParser):
    operation = 'best'
    parsers = (xyz, abc, abcd, abdecg)

best_fixture = BestFixture()


class TestBest(TestCase):
    def test_best(self):
        po = ParsingObj('abcdefghi')

        tmp_ret = best_fixture(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 5)

abc_str = StringNoSegment(look_for='abc', name='abc_str')


# class abc_dot_fix(SubParsersParser):
#     parsers = (abc_str, dot)


class LoopFixture(LoopMixin, SubParsersParser):
    parsers = (abc_str, dot)
    min_loop = 2
    max_loop = 3
loop_fixture = LoopFixture()


class LoopFixtureFailMsg(LoopFixture):
    max_loop_fail = True

loop_fixture_fail_msg = LoopFixtureFailMsg()


class TestLoop(TestCase):
    def test_loop(self):
        po = ParsingObj('abc.abc.def')

        tmp_ret = loop_fixture(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 8)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)


    def test_min_loop_fail(self):
        po = ParsingObj('abc.def')

        tmp_ret = loop_fixture(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)

    def test_max_loop_no_fail(self):
        po = ParsingObj('abc.abc.abc.abc.def')

        tmp_ret = loop_fixture(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 12)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)

    def test_max_loop_fail(self):
        po = ParsingObj('abc.abc.abc.abc.def')

        tmp_ret = loop_fixture_fail_msg(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertTrue('TOO_MANY_SEGMENTS' in tmp_ret)


class SingleDot(SingleCharParser):
    wrappers = InvalidNextWrapper
    name = 'single_dot'
    look_for = DOT
    invalid_next_char = DOT
    invalid_next_char_msg = {'key': 'INVALID_NEXT_CHAR', 'description': 'Segment has two dots together'}

single_dot = SingleDot()


class TestInvalidNext(TestCase):
    def test_invalid_next(self):
        po = ParsingObj('.f')

        tmp_ret = single_dot(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 1)
        self.assertFalse('INVALID_NEXT_CHAR' in tmp_ret)

    def test_invalid_next_fail(self):
        po = ParsingObj('..')

        tmp_ret = single_dot(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('INVALID_NEXT_CHAR' in tmp_ret)


class EnclosedFixture(CharParser):
    wrappers = EnclosedWrapper
    look_for = 'abc'
enclosed_fixture = EnclosedFixture()


class TestEnclosed(TestCase):
    def test_enclosed(self):
        po = ParsingObj('"abcabc"')

        tmp_ret = enclosed_fixture(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 8)
        self.assertFalse('UNCLOSED_STRING' in tmp_ret)

    def test_unenclosed(self):
        po = ParsingObj('abcabc')

        tmp_ret = enclosed_fixture(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('UNCLOSED_STRING' in tmp_ret)

    def test_enclosed_fail(self):
        po = ParsingObj('"abcabc')

        tmp_ret = enclosed_fixture(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('UNCLOSED_STRING' in tmp_ret)


class MinMaxFixture(CharParser):
    wrappers = MinMaxLenWrapper
    look_for = 'abc'
    min_length = 2
    max_length = 3

minmax_fixture = MinMaxFixture()


class TestMinMaxLen(TestCase):
    def test_min_max(self):
        po = ParsingObj('abc')
        tmp_ret = minmax_fixture(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        self.assertFalse('SEGMENT_TOO_LONG' in tmp_ret)
        self.assertFalse('SEGMENT_TOO_SHORT' in tmp_ret)

    def test_min_fail(self):
        po = ParsingObj('a')

        tmp_ret = minmax_fixture(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('SEGMENT_TOO_LONG' in tmp_ret)
        self.assertTrue('SEGMENT_TOO_SHORT' in tmp_ret, repr(tmp_ret))

    def test_max_fail(self):
        po = ParsingObj('abcabc')

        tmp_ret = minmax_fixture(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('SEGMENT_TOO_LONG' in tmp_ret)
        self.assertFalse('SEGMENT_TOO_SHORT' in tmp_ret)


class InvalidStartStopFixture(CharParser):
    wrappers = InvalidStartStopWrapper
    look_for = 'abc'
    invalid_start_chars = '-,.'
    invalid_end_chars = '".@'

invalidstartstop_fixture = InvalidStartStopFixture()


class TestInvalidStartStop(TestCase):
    def test_invalid_start_stop(self):
        po = ParsingObj('abc')
        tmp_ret = invalidstartstop_fixture(po)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        self.assertFalse('INVALID_START' in tmp_ret)
        self.assertFalse('INVALID_END' in tmp_ret)

    def test_invalid_start_fail(self):
        po = ParsingObj(',abc')
        tmp_ret = invalidstartstop_fixture(po)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('INVALID_START' in tmp_ret)
        self.assertFalse('INVALID_END' in tmp_ret)

    def test_invalid_stop_fail(self):
        po = ParsingObj('abc@')
        tmp_ret = invalidstartstop_fixture(po)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('INVALID_START' in tmp_ret)
        self.assertTrue('INVALID_END' in tmp_ret)

    def test_invalid_start_stop_fail(self):
        po = ParsingObj('-abc.')
        tmp_ret = invalidstartstop_fixture(po)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('INVALID_START' in tmp_ret)
        self.assertFalse('INVALID_END' in tmp_ret)

# class TestCombined(TestCase):

abc_char = CharParser(look_for='abc', on_fail_msg='ERROR')

# abc_str = StringParser(look_for='abc', name='abc_str')


class AbcDotFix(SubParsersParser):
    name = 'abc_dot'
    parsers = (abc_str, dot)

# abc_dot_fix_seg = AbcDotFix()

#class AbcDotFix():
#    segment = abc_dot_fix_seg


class ComplexFixture(LoopMixin, AbcDotFix):
    wrappers = (FullLengthWrapper, MinMaxLenWrapper, EnclosedWrapper)
    name = 'complex'
    enclosure_start = '('
    enclosure_end = ')'
    min_loop = 2
    max_loop = 3
    max_length = 15
    min_length = 8

complex_fixture = ComplexFixture()

class TestComplex(TestCase):
    def test_complex(self):
        po = ParsingObj('(abc.abc.)def')

        tmp_ret = complex_fixture(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 10)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)
        self.assertFalse('UNCLOSED_STRING' in tmp_ret)


    def test_min_complex_fail(self):
        po = ParsingObj('(abc.)def')

        tmp_ret = complex_fixture(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('TOO_FEW_SEGMENTS' in tmp_ret, repr(tmp_ret))
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)
        self.assertFalse('UNCLOSED_STRING' in tmp_ret)

    def test_max_complex_no_fail(self):
        po = ParsingObj('(abc.abc.abc.)abc.def')

        tmp_ret = complex_fixture(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 14)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)
        self.assertFalse('UNCLOSED_STRING' in tmp_ret)

    def test_unclosed_fail(self):
        po = ParsingObj('(abc.abc.abc.abc.def')

        tmp_ret = complex_fixture(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)
        self.assertTrue('UNCLOSED_STRING' in tmp_ret)
