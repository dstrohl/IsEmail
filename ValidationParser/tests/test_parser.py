from unittest import TestCase
from ValidationParser import *
from ValidationParser.footballs import ParseResultFootball, ParsingObj
from ValidationParser.parser_responses import ParseFullResult, ParseShortResult
from ValidationParser.parser_messages import RESULT_CODES
from helpers.general.test_helpers import TestCaseApproxString
from ValidationParser.tests.parser_test_helper import ParserTests

abc = CharParser(look_for='abc', on_fail_msg='ERROR')

abc_str = StringParser(look_for='abc', name='abc_str')


class AbcDotFix(SubParsersParser):
    name = 'abc_dot'
    parsers = (abc_str, dot)

# abc_dot_fix_seg = AbcDotFix()

#class AbcDotFix():
#    segment = abc_dot_fix_seg


class ComplexFixture(LoopMixin, AbcDotFix):
    wrappers = (EnclosedWrapper, MinMaxLenWrapper, FullLengthWrapper)
    name = 'complex'
    enclosure_start = '('
    enclosure_end = ')'
    min_loop = 2
    max_loop = 3
    max_length = 15
    min_length = 8

complex_fixture = ComplexFixture()


class TestParse(TestCaseApproxString):
    def test_base_parse(self):
        tmp_ret = parse('abcdef', abc)

        self.assertTrue(tmp_ret)
        self.assertEqual(len(tmp_ret), 3)
        self.assertEqual(str(tmp_ret), 'abc')
        self.assertEqual(tmp_ret.parsed_str, 'abc')
        self.assertEqual(tmp_ret.parse_str, 'abcdef')

    def test_pass_obj(self):
        po = ParsingObj('cab')
        tmp_ret = parse(po, abc)

        self.assertTrue(tmp_ret)
        self.assertEqual(len(tmp_ret), 3)
        self.assertEqual(str(tmp_ret), 'cab')

    def test_pass_kwarg(self):
        with self.assertRaises(ParsingError):
            tmp_ret = parse('xyz', abc, raise_on_error=True)

    def test_ret_short_good(self):
        tmp_ret = parse('(abc.abc.)', complex_fixture)

        self.assertIsInstance(tmp_ret, ParseShortResult)

        with self.subTest('bool'):
            self.assertTrue(tmp_ret, repr(tmp_ret))

        with self.subTest('status'):
            self.assertEqual(RESULT_CODES.OK, tmp_ret.status, repr(tmp_ret))

        with self.subTest('history_str'):
            self.assertEqual(tmp_ret.history_str, 'complex(abc_str, DOT, abc_str, DOT)', repr(tmp_ret.history_str))

        with self.subTest('max_message'):
            self.assertEqual(tmp_ret.max_message.key, 'VALID')

    def test_ret_short_errors(self):
        tmp_ret = parse('(abc.abc.abc.', complex_fixture)

        self.assertIsInstance(tmp_ret, ParseShortResult)

        with self.subTest('bool'):
            self.assertFalse(tmp_ret)

        with self.subTest('status'):
            self.assertEqual(RESULT_CODES.ERROR, tmp_ret.status)

        with self.subTest('history_str'):
            exp_str = 'complex(abc_str, DOT, abc_str, DOT, abc_str, DOT)'
            self.assertEqual(tmp_ret.history_str, exp_str, repr(tmp_ret.history_str))

        with self.subTest('max_message'):
            self.assertEqual(tmp_ret.max_message.key, 'INVALID_CHAR')

    def test_ret_long(self):
        tmp_ret = parse('(abc.abc.)', complex_fixture, return_type=RETURN_TYPES.long)

        self.assertIsInstance(tmp_ret, ParseFullResult)

        with self.subTest('contains'):
            self.assertTrue('abc_str' in tmp_ret)

        with self.subTest('bool'):
            self.assertTrue(tmp_ret)

        with self.subTest('status'):
            self.assertEqual(RESULT_CODES.OK, tmp_ret.status)

        with self.subTest('history_str'):
            self.assertEqual(tmp_ret.history_str, 'complex(abc_str, DOT, abc_str, DOT)', repr(tmp_ret.history_str))

        with self.subTest('max_message'):
            self.assertEqual(tmp_ret.max_message.key, 'VALID')

        with self.subTest('messages'):
            self.assertEqual(str(tmp_ret.messages), 'complex(VALID)', repr(tmp_ret.messages))

        with self.subTest('trace'):
            exp_trace_begin = 'TRACE 10: (12/12 records,'
            exp_trace_end = 'seconds)\n' \
                            '(*** Including lines 1 to 12 ***)\n' \
                            '----------------------------------------------\n' \
                            'Begin complex: scanning from 0: ->\'(abc.abc.)\'<-\n' \
                            '    Begin abc_str: scanning from 1: ->\'abc.abc.)\'<-\n' \
                            '    End abc_str: Found 3 "abc" : [ abc_str / OK(3)  ]\n' \
                            '    Begin DOT: scanning from 4: ->\'.abc.)\'<-\n' \
                            '    End DOT: Found 1 "." : [ DOT / OK(1)  ]\n' \
                            '    Begin abc_str: scanning from 5: ->\'abc.)\'<-\n' \
                            '    End abc_str: Found 3 "abc" : [ abc_str / OK(3)  ]\n' \
                            '    Begin DOT: scanning from 8: ->\'.)\'<-\n' \
                            '    End DOT: Found 1 "." : [ DOT / OK(1)  ]\n' \
                            '    Begin abc_str: scanning from 9: ->\')\'<-\n' \
                            '    End abc_str: UN-MATCHED : [ abc_str / ERROR((not found))  ]\n' \
                            'End complex: Found 10 "(abc.abc.)" : [ complex / OK(10) / complex(VALID) ]\n' \
                            '----------------------------------------------'

            self.assertApproxString(tmp_ret.trace, exp_trace_begin, exp_trace_end, max_skip=10, min_skip=1, msg=repr(str(tmp_ret.trace)))
            # self.assertEqual(tmp_ret.trace, '', tmp_ret.trace)

        with self.subTest('data'):
            self.assertEqual(tmp_ret.data['loops'], 2)

    def test_ret_bool(self):
        tmp_full = parse('(abc.abc.foobar)', complex_fixture, return_type=RETURN_TYPES.long)
        tmp_ret = parse('(abc.abc.)', complex_fixture, return_type=RETURN_TYPES.bool)

        self.assertIsInstance(tmp_ret, bool)
        self.assertTrue(tmp_ret)

        tmp_ret = parse('(abc.abc.foobar)', complex_fixture, return_type=RETURN_TYPES.bool)

        self.assertIsInstance(tmp_ret, bool)
        self.assertFalse(tmp_ret, repr(tmp_full))

    def test_ret_football(self):
        tmp_ret = parse('(abc.abc.)', complex_fixture, return_type=RETURN_TYPES.football)

        self.assertIsInstance(tmp_ret, ParseResultFootball)
        self.assertTrue(tmp_ret)
        self.assertEqual(tmp_ret.l, 10)


class TestParserTestsHelper(TestCase):

    def test_parser_test_helper(self):

        tmp_tests = ParserTests(
            parse_script_parser=complex_fixture,  # required
            parse_return_type='all',  # [bool, short, long]
            tests=[
                dict(
                    test_id='good_ret',  # required
                    parse_string='(abc.abc.)',
                    contains_parsers=['abc_str'],
                    status=RESULT_CODES.OK,
                    history_str='complex(abc_str, DOT, abc_str, DOT)',
                    history_level=None,
                    max_message='VALID',
                    messages='complex.VALID',
                    data={'loop_count': 2}),
                dict(
                    test_id='bad_ret',  # required
                    parse_string='(abc.abc.abc.',
                    parsed_string_len=0,
                    contains_parsers=['abc_str'],
                    history_str='complex(abc_str, DOT, abc_str, DOT, abc_str, DOT)',
                    history_level=None,
                    max_message='INVALID_CHAR',
                    messages=[('complex', 'INVALID_CHAR')],
                    data={'loop_count': 3}),
                ('test_list_1', '(abc.abc.)'),
                ('test_list_2', '(abc.abc.)', 10),
                ('test_list_3', '(abc.abc.', 0),
                ('test_list_4', '(abc.abc.)', 10, 'complex(abc_str, DOT, abc_str, DOT)'),
                ('test_list_5', '(abc.abc.)', 10, 'complex(abc_str, DOT, abc_str, DOT)', ['complex.VALID']),
                ('test_list_6', '(abc.abc.)', 10, 'complex(abc_str, DOT, abc_str, DOT)', ['complex.VALID'], {'data': {'loop_count': 2}}),
            ]
        )

        LIMIT_TO = None
        # LIMIT_TO = 'test_list_3'

        if LIMIT_TO is not None:
            with self.subTest('LIMITED TEST'):
                self.fail('LIMITED_TEST')

        for test in tmp_tests:
            if LIMIT_TO is None or LIMIT_TO == test.test_id:
                with self.subTest(str(test)):
                    tmp_ret, tmp_msg = test()
                    self.assertTrue(tmp_ret, tmp_msg)

