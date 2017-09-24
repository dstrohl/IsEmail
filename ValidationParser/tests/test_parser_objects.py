from ValidationParser.parser_objects import *
from ValidationParser.parser_base_chars import *
from unittest import TestCase
from ValidationParser.exceptions import ParsingLocalError, ParsingFatalError
from ValidationParser.footballs import ParsingObj
from helpers.general.test_helpers import TestCaseApproxString


class abc_str(StringParser):
    look_for = 'abc'


class cab_str(StringParser):
    look_for = 'cab'


class cab(CharNoSegment):
    look_for = 'cba'  # , name = 'cba_char')


class xyz_errpr(CharParser):
    look_for = 'xyz'
    on_fail_msg = 'ERROR'


class abc_pass(CharParser):
    look_for = 'abc'
    on_pass_msg = 'VALID'


class abc_fail(StringParser):
    look_for = 'abc'
    on_fail_msg = 'ERROR'


class xyz_pass(CharParser):
    look_for = 'xyz'
    on_pass_msg = 'VALID'


class xyz_fail(StringParser):
    look_for = 'xyz'
    on_fail_msg = 'ERROR'


class TestSimpleParsers(TestCase):

    def test_colon(self):
        po = ParsingObj(':')
        tmp_ret = Colon.run(po)
        self.assertTrue(tmp_ret)

    def test_parse_str(self):
        po = ParsingObj('abcdefghi')

        tmp_ret = abc_str.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)

    def test_parse_str_fail(self):
        po = ParsingObj('abcdefghi')

        tmp_ret = cab_str.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)


class TestCustomizedBaseFunctions(TestCaseApproxString):
    def test_is_segment(self):
        po = ParsingObj('abcdefghi')
        tmp_ret = cab.run(po, 0)
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
        tmp_ret = cab.run(po, 12)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)

    def test_raise_error(self):
        po = ParsingObj('abcdefghi', raise_on_error=True)
        with self.assertRaises(ParsingLocalError):
            tmp_ret = xyz.run(po, 0)

    def test_pass_msg(self):
        po = ParsingObj('abcdefghi')
        tmp_ret = abc_pass.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        self.assertTrue('VALID' in tmp_ret)

    def test_pass_msg_on_fail(self):
        po = ParsingObj('abcdefghi')
        tmp_ret = xyz_pass.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('VALID' in tmp_ret)

    def test_fail_msg(self):
        po = ParsingObj('abcdefghi')
        tmp_ret = xyz_fail.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('ERROR' in tmp_ret)

    def test_fail_msg_on_pass(self):
        po = ParsingObj('abcdefghi')
        tmp_ret = abc_fail.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        self.assertFalse('ERROR' in tmp_ret)

    def test_history_item(self):
        po = ParsingObj('abcdefghi')
        tmp_ret = cab.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        self.assertEqual(tmp_ret.history, 'test_seg')




class fed(CharNoSegment):
    look_for='fed'  # , name='fed_char')


class ghi(CharNoSegment):
    look_for='hig'  # , name='ghi_char')


class xyz(CharNoSegment):
    look_for='zxy'  # , name='xyz_char')


class abcd(CharNoSegment):
    look_for='cbad' # , name='abcd')


class abdecg(CharNoSegment):
    look_for='abdecg' # , name='abdecg')


class and_fixture(SubParsersParser):
    parsers=(cab, fed, ghi)


class TestAnd(TestCase):
    def test_and(self):
        po = ParsingObj('abcdefghi')
        # abc = PHBaseChar('cba', name='abc')
        # fed = PHBaseChar('fde', name='fed')
        # ghi = PHBaseChar('hig', name='ghi')

        # tmp_ret = abc._and(po, 0, fed, ghi)
        tmp_ret = and_fixture.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 9)

    def test_and_fail(self):
        po = ParsingObj('abcdefxyz')
        # abc = PHBaseChar('cba')
        # fed = PHBaseChar('fde')
        # ghi = PHBaseChar('zxy')

        # tmp_ret = abc._and(po, 0, fed, ghi)
        tmp_ret = and_fixture.run(po, 0)

        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)


class or_fixture(SubParsersParser):
    parsers = (ghi, cab, fed)
    operation = 'or'


class TestOr(TestCase):
    def test_or(self):
        po = ParsingObj('abcdefghi')
        tmp_ret = or_fixture.run(po)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)

    def test_or_fail(self):
        po = ParsingObj('lmnop')

        tmp_ret = or_fixture.run(po)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)


# tmp_ret = abc._best(po, 0, abcd, ghi)


class best_fixture(SubParsersParser):
    operation = 'best'
    parsers = (xyz, cab, abcd, abdecg)


class TestBest(TestCase):
    def test_best(self):
        po = ParsingObj('abcdefghi')

        tmp_ret = best_fixture.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 5)

# abc_str = StringNoSegment(look_for='abc', name='abc_str')


# class abc_dot_fix(SubParsersParser):
#     parsers = (abc_str, dot)


class loop_fixture(SubParsersParser):
    parsers = (abc_str, Dot)
    min_loop = 2
    max_loop = 3
    should_loop = True
    

class loop_fixture_fail_msg(loop_fixture):
    max_loop_fail = True


class TestLoop(TestCase):
    def test_loop(self):
        po = ParsingObj('abc.abc.def')

        tmp_ret = loop_fixture.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 8)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)


    def test_min_loop_fail(self):
        po = ParsingObj('abc.def')

        tmp_ret = loop_fixture.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)

    def test_max_loop_no_fail(self):
        po = ParsingObj('abc.abc.abc.abc.def')

        tmp_ret = loop_fixture.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 12)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)

    def test_max_loop_fail(self):
        po = ParsingObj('abc.abc.abc.abc.def')

        tmp_ret = loop_fixture_fail_msg.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertTrue('TOO_MANY_SEGMENTS' in tmp_ret)


class single_dot(SingleCharParser):
    wrappers = InvalidNextWrapper
    name = 'single_dot'
    look_for = CHARS.DOT
    invalid_next_char = CHARS.DOT
    invalid_next_char_msg = {'key': 'INVALID_NEXT_CHAR', 'description': 'Segment has two dots together'}


class TestInvalidNext(TestCase):
    def test_invalid_next(self):
        po = ParsingObj('.f')

        tmp_ret = single_dot.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 1)
        self.assertFalse('INVALID_NEXT_CHAR' in tmp_ret)

    def test_invalid_next_fail(self):
        po = ParsingObj('..')

        tmp_ret = single_dot.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('INVALID_NEXT_CHAR' in tmp_ret)


class enclosed_fixture(CharParser):
    wrappers = EnclosedWrapper
    look_for = 'abc'
    

class TestEnclosed(TestCase):
    def test_enclosed(self):
        po = ParsingObj('"abcabc"')

        tmp_ret = enclosed_fixture.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 8)
        self.assertFalse('UNCLOSED_STRING' in tmp_ret)

    def test_unenclosed(self):
        po = ParsingObj('abcabc')

        tmp_ret = enclosed_fixture.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('UNCLOSED_STRING' in tmp_ret)

    def test_enclosed_fail(self):
        po = ParsingObj('"abcabc')

        tmp_ret = enclosed_fixture.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('UNCLOSED_STRING' in tmp_ret)


class minmax_fixture(CharParser):
    wrappers = MinMaxLenWrapper
    look_for = 'abc'
    min_length = 2
    max_length = 3


class TestMinMaxLen(TestCase):
    def test_min_max(self):
        po = ParsingObj('abc')
        tmp_ret = minmax_fixture.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        self.assertFalse('SEGMENT_TOO_LONG' in tmp_ret)
        self.assertFalse('SEGMENT_TOO_SHORT' in tmp_ret)

    def test_min_fail(self):
        po = ParsingObj('a')

        tmp_ret = minmax_fixture.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('SEGMENT_TOO_LONG' in tmp_ret)
        self.assertTrue('SEGMENT_TOO_SHORT' in tmp_ret, repr(tmp_ret))

    def test_max_fail(self):
        po = ParsingObj('abcabc')

        tmp_ret = minmax_fixture.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('SEGMENT_TOO_LONG' in tmp_ret)
        self.assertFalse('SEGMENT_TOO_SHORT' in tmp_ret)


class invalidstartstop_fixture(CharParser):
    wrappers = InvalidStartStopWrapper
    look_for = 'abc'
    invalid_start_chars = '-,.'
    invalid_end_chars = '".@'


class TestInvalidStartStop(TestCase):
    def test_invalid_start_stop(self):
        po = ParsingObj('abc')
        tmp_ret = invalidstartstop_fixture.run(po)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 3)
        self.assertFalse('INVALID_START' in tmp_ret)
        self.assertFalse('INVALID_END' in tmp_ret)

    def test_invalid_start_fail(self):
        po = ParsingObj(',abc')
        tmp_ret = invalidstartstop_fixture.run(po)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('INVALID_START' in tmp_ret)
        self.assertFalse('INVALID_END' in tmp_ret)

    def test_invalid_stop_fail(self):
        po = ParsingObj('abc@')
        tmp_ret = invalidstartstop_fixture.run(po)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('INVALID_START' in tmp_ret)
        self.assertTrue('INVALID_END' in tmp_ret)

    def test_invalid_start_stop_fail(self):
        po = ParsingObj('-abc.')
        tmp_ret = invalidstartstop_fixture.run(po)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('INVALID_START' in tmp_ret)
        self.assertFalse('INVALID_END' in tmp_ret)

# class TestCombined(TestCase):

class abc_char(CharParser):
    look_for='abc'
    on_fail_msg='ERROR'


class abc_dot_fix_seg(SubParsersParser):
    name = 'abc_dot'
    parsers = (abc_str, Dot)

# abc_dot_fix_seg = AbcDotFix()

# class AbcDotFix():
#     segment = abc_dot_fix_seg


class ComplexFixture(abc_dot_fix_seg):
    wrappers = (FullLengthWrapper, MinMaxLenWrapper, EnclosedWrapper)
    name = 'complex'
    enclosure_start = '('
    enclosure_end = ')'
    min_loop = 2
    max_loop = 3
    max_length = 15
    min_length = 8
    should_loop = True
    
complex_fixture = ComplexFixture()


class TestComplex(TestCase):
    def test_complex(self):
        po = ParsingObj('(abc.abc.)def')

        tmp_ret = complex_fixture.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 10)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)
        self.assertFalse('UNCLOSED_STRING' in tmp_ret)


    def test_min_complex_fail(self):
        po = ParsingObj('(abc.)def')

        tmp_ret = complex_fixture.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertTrue('TOO_FEW_SEGMENTS' in tmp_ret, repr(tmp_ret))
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)
        self.assertFalse('UNCLOSED_STRING' in tmp_ret)

    def test_max_complex_no_fail(self):
        po = ParsingObj('(abc.abc.abc.)abc.def')

        tmp_ret = complex_fixture.run(po, 0)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 14)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)
        self.assertFalse('UNCLOSED_STRING' in tmp_ret)

    def test_unclosed_fail(self):
        po = ParsingObj('(abc.abc.abc.abc.def')

        tmp_ret = complex_fixture.run(po, 0)
        self.assertFalse(tmp_ret)
        self.assertEqual(tmp_ret.l, 0)
        self.assertFalse('TOO_FEW_SEGMENTS' in tmp_ret)
        self.assertFalse('TOO_MANY_SEGMENTS' in tmp_ret)
        self.assertTrue('UNCLOSED_STRING' in tmp_ret)
