import unittest
from pyparsing_adds import *
from pyparsing import *
from pyparsing_adds import _consolidate_parsed_results


aword = Word(alphanums)
dot = Literal('.').suppress()
counting_in_for = Literal('o')
counting_in_for_or = Literal('o') | Literal('h')
word_dot = aword + dot
dotted_word = OneOrMore(word_dot) + aword

start_str = 'hi.hello.foo.bar.snafu.blah'
expected_ret = ['hi', 'hello', 'foo', 'bar', 'snafu', 'blah']



PYPARSING_ADD_TESTS = [
    ('count_in pass, no args', CountIn, {'match_expr': counting_in_for}, True),
    ('count_in pass, min', CountIn, {'match_expr': counting_in_for, 'min': 3}, True),
    ('count_in pass, max', CountIn, {'match_expr': counting_in_for, 'max': 4}, True),
    ('count_in pass, exact', CountIn, {'match_expr': counting_in_for, 'exact': 3}, True),

    ('count_in fail, min', CountIn, {'match_expr': counting_in_for, 'min': 5}, False),
    ('count_in fail, max', CountIn, {'match_expr': counting_in_for, 'max': 2}, False),
    ('count_in fail, exact', CountIn, {'match_expr': counting_in_for, 'exact': 44}, False),

    ('count_in_2 pass, no args', CountIn, {'match_expr': counting_in_for_or}, True),
    ('count_in_2 pass, min', CountIn, {'match_expr': counting_in_for_or, 'min': 2}, True),
    ('count_in_2 pass, max', CountIn, {'match_expr': counting_in_for_or, 'max': 10}, True),
    ('count_in_2 pass, exact', CountIn, {'match_expr': counting_in_for_or, 'exact': 6}, True),

    ('count_in_2 fail, min', CountIn, {'match_expr': counting_in_for_or, 'min': 10}, False),
    ('count_in_2 fail, max', CountIn, {'match_expr': counting_in_for_or, 'max': 4}, False),
    ('count_in_2 fail, exact', CountIn, {'match_expr': counting_in_for_or, 'exact': 3}, False),


    ('count_tokens pass, no args', Count, {}, True),
    ('count_tokens pass, min', Count, {'min': 3}, True),
    ('count_tokens pass, max', Count, {'max': 10}, True),
    ('count_tokens pass, exact', Count, {'exact': 6}, True),

    ('count_tokens fail, min', Count, {'min': 10}, False),
    ('count_tokens fail, max', Count, {'max': 4}, False),
    ('count_tokens fail, exact', Count, {'exact': 100}, False),

    ('Len pass, no args', Len, {}, True),
    ('Len pass, min', Len, {'min': 20}, True),
    ('Len pass, max', Len, {'max': 24}, True),
    ('Len pass, exact', Len, {'exact': 22}, True),

    ('Len fail, min', Len, {'min': 30}, False),
    ('Len fail, max', Len, {'max': 20}, False),
    ('Len fail, exact', Len, {'exact': 9}, False),

]    

class TestPyparsingAdds(unittest.TestCase):

    def test_parsers(self):

        for t in PYPARSING_ADD_TESTS:
            with self.subTest(t[0]):
                test_parser = t[1](dotted_word, **t[2])
                if t[3]:
                    results = test_parser.parseString(start_str)
                    self.assertEqual(results.asList(), expected_ret)
                else:
                    with self.assertRaises(ParseException):
                        results = test_parser.parseString(start_str)
                        self.assertNotEqual(results.asList(), expected_ret)


    def test_consolidate(self):

        tmp_in_dict = dict(
            t01='test01',
            t02='test02',
            t03='test03',
            t04=dict(
                t05='test05',
                t06='test06',
                t07=dict(
                    t08='test08',
                ),
                t09='test09',
                t10=dict(
                    t11='test11',
                    t12='test12',
                ),

            )
        )

        tmp_out_dict_no_combine = dict(
            t01='test01',
            t02='test02',
            t03='test03',
            t05='test05',
            t06='test06',
            t08='test08',
            t09='test09',
            t11='test11',
            t12='test12')

        tmp_out_dict_with_combine = dict(
            t01='test01',
            t02='test02',
            t03='test03',
            t04='test05test06test08test09test11test12',
            t05='test05',
            t06='test06',
            t07='test08',
            t08='test08',
            t09='test09',
            t10='test11test12',
            t11='test11',
            t12='test12',
        )

        tmp_out_dict_with_combine_dot = dict(
            t01='test01',
            t02='test02',
            t03='test03',
            t04='test05.test06.test08.test09.test11.test12',
            t05='test05',
            t06='test06',
            t07='test08',
            t08='test08',
            t09='test09',
            t10='test11.test12',
            t11='test11',
            t12='test12',
        )

        with self.subTest('no combine'):
            tmp_res_def = _consolidate_parsed_results(tmp_in_dict, combine=False)
            print('returned: ', tmp_res_def)
            print('expected: ', tmp_out_dict_no_combine, '\n')
            self.assertEqual(tmp_res_def, tmp_out_dict_no_combine)

        with self.subTest('combine'):
            tmp_res_comb = _consolidate_parsed_results(tmp_in_dict)
            print('returned: ', tmp_res_comb)
            print('expected: ', tmp_out_dict_with_combine, '\n')
            self.assertEqual(tmp_res_comb, tmp_out_dict_with_combine)

        with self.subTest('combine-dot'):
            tmp_res_comb_dot = _consolidate_parsed_results(tmp_in_dict, join_str='.')
            print('returned: ', tmp_res_comb_dot)
            print('expected: ', tmp_out_dict_with_combine_dot, '\n')
            self.assertEqual(tmp_res_comb_dot, tmp_out_dict_with_combine_dot)

