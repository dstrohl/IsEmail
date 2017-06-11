from unittest import TestCase
from helpers.parser_helpers_old.parser_helpers import simple_char, simple_str, single_char, parse_and, parse_or, parse_best, parse_loop
from helpers.parser_helpers_old.parser_wrappers import email_parser, wrapped_parser, is_comment, pass_diags, fail_diags
from helpers.footballs import EmailInfo
from helpers.exceptions import ParsingError


def ei(email='abcdefghijk', **kwargs):
    return EmailInfo(email, **kwargs)


def abc(email_info, position=0):
    return simple_char(email_info, position, 'abc')

def fed(email_info, position=0):
    return simple_char(email_info, position, 'fed')

def ghi(email_info, position=0):
    return simple_char(email_info, position, 'ghi')

def xyz(email_info, position=0):
    return simple_char(email_info, position, 'xyz')


class TestParserHelpers(TestCase):

    def test_single_char(self):
        tmp_ret = single_char(ei(), 5, 'f')
        self.assertEqual(tmp_ret.l, 1)

    def test_single_char_missing(self):
        tmp_ret = single_char(ei(), 4, 'g')
        self.assertEqual(tmp_ret.l, 0)

    def test_single_char_has_mult(self):
        tmp_ret = single_char(ei('abcdefgggg'), 6, 'g')
        self.assertEqual(tmp_ret.l, 1)

    def test_simple_single_char(self):
        tmp_ret = simple_char(ei(), 5, 'f')
        self.assertEqual(tmp_ret.l, 1)

    def test_simple_single_char_missing(self):
        tmp_ret = simple_char(ei(), 4, 'g')
        self.assertEqual(tmp_ret.l, 0)

    def test_simple_char(self):
        tmp_ret = simple_char(ei('abcdefgggg'), 6, 'g')
        self.assertEqual(tmp_ret.l, 4)

    def test_simple_char_at_end(self):
        tmp_ret = simple_char(ei('abcdefgggg'), 6, 'g')
        self.assertEqual(tmp_ret.l, 4)

    def test_simple_char_mult_chars(self):
        tmp_ret = simple_char(ei('abcdefghij'), 6, 'ghi')
        self.assertEqual(tmp_ret.l, 3)

    def test_simple_char_min_count(self):
        tmp_ret = simple_char(ei('abcdefghij'), 1, 'abcdefghi', min_count=3)
        self.assertEqual(tmp_ret.l, 8)

    def test_simple_char_min_count_fail(self):
        tmp_ret = simple_char(ei('abcdefghij'), 1, 'abcdefghi', min_count=19)
        self.assertEqual(tmp_ret.l, 0)

    def test_simple_char_max_count(self):
        tmp_ret = simple_char(ei('abcdefghij'), 6, 'ghi', max_count=3)
        self.assertEqual(tmp_ret.l, 3)

    def test_simple_char_max_count_fail(self):
        tmp_ret = simple_char(ei('abcdefghij'), 6, 'ghijkl', max_count=2)
        self.assertEqual(tmp_ret.l, 2)

    def test_simple_char_until_char(self):
        tmp_ret = simple_char(ei('abcdefghij'), 0, 'abcdefghijklm', parse_until='e')
        self.assertEqual(tmp_ret.l, 4)

    def test_simple_char_not_found(self):
        tmp_ret = simple_char(ei('abcdefghij'), 10, 'ghi')
        self.assertEqual(tmp_ret.l, 0)

    def test_simple_str(self):
        tmp_ret = simple_str(ei('abcdefghij'), 6, 'ghi')
        self.assertEqual(tmp_ret.l, 3)

    def test_simple_str_cap_sen(self):
        tmp_ret = simple_str(ei('abcdefghij'), 6, 'GHI', caps_sensitive=False)
        self.assertEqual(tmp_ret.l, 3)

    def test_simple_str_not_found(self):
        tmp_ret = simple_str(ei('abcdefghij'), 5, 'ihg')
        self.assertEqual(tmp_ret.l, 0)

    def test_and_pass(self):
        tmp_ei = ei('abcdefghij')
        tmp_ret = parse_and(tmp_ei, 0, abc, fed, ghi)
        self.assertEqual(tmp_ret.l, 9)

    def test_and_pass_parser(self):
        tmp_ei = ei('abcdefghij')
        tmp_ret = parse_and(tmp_ei, 0, 'abc', 'def', '"ghi"')
        self.assertEqual(tmp_ret.l, 9)

    def test_and_pass_string_fail(self):
        tmp_ei = ei('abcdefghij')
        tmp_ret = parse_and(tmp_ei, 0, 'abc', 'def', '"igh"')
        self.assertEqual(tmp_ret.l, 0)

    def test_or_pass(self):
        tmp_ei = ei('abcdefghij')
        tmp_ret = parse_or(tmp_ei, 0, xyz, abc, fed, ghi)
        self.assertEqual(tmp_ret.l, 3)

    def test_and_fail(self):
        tmp_ei = ei('abcdefghij')
        tmp_ret = parse_and(tmp_ei, 0, abc, fed, ghi, xyz)
        self.assertEqual(tmp_ret.l, 0)

    def test_or_fail(self):
        tmp_ei = ei('abcdefghij')
        tmp_ret = parse_and(tmp_ei, 0, xyz, xyz)
        self.assertEqual(tmp_ret.l, 0)

    def test_loop(self):
        tmp_ei = ei('abc.abc.abc')
        tmp_ret = parse_loop(tmp_ei, 0, parse_and, abc, '.')
        self.assertEqual(tmp_ret.l, 8)

    def test_loop_min(self):
        tmp_ei = ei('abc.abc.defghi')
        tmp_ret = parse_loop(tmp_ei, 0, parse_and, abc, '.', min_loop=2)
        self.assertEqual(tmp_ret.l, 8)

    def test_loop_min_fail(self):
        tmp_ei = ei('abc.abc.defghi')
        tmp_ret = parse_loop(tmp_ei, 0, parse_and, abc, '.', min_loop=3)
        self.assertEqual(tmp_ret.l, 0)

    def test_loop_max(self):
        tmp_ei = ei('abc.abc.abc.')
        tmp_ret = parse_loop(tmp_ei, 0, parse_and, abc, '.', max_loop=2)
        self.assertEqual(tmp_ret.l, 8)

    def test_loop_min_max(self):
        tmp_ei = ei('abc.abc.abc')
        tmp_ret = parse_loop(tmp_ei, 0, parse_and, abc, '.', max_loop=2, min_loop=2)
        self.assertEqual(tmp_ret.l, 8)

    def test_loop_min_max_fail(self):
        tmp_ei = ei('abc.def.abcabc')
        tmp_ret = parse_loop(tmp_ei, 0, parse_and, abc, '.', max_loop=2, min_loop=2)
        self.assertEqual(tmp_ret.l, 0)

    def test_best(self):
        tmp_ei = ei('abc.defghij')
        tmp_ret = parse_best(tmp_ei, 0, abc, 'abc.d')
        self.assertEqual(tmp_ret.l, 5)

    def test_best_2(self):
        tmp_ei = ei('abcdefghij')
        tmp_ret = parse_best(tmp_ei, 0, 'abcde', 'abcd')
        self.assertEqual(tmp_ret.l, 5)



@is_comment
def wrapped_comment_fixture(email_info, position):
    return simple_char(email_info, position, 'edcba')


@pass_diags('ERR_ATEXT_AFTER_CFWS')
def pass_diag_fixture(email_info, position):
    return simple_char(email_info, position, 'edcba')


@fail_diags('ERR_ATEXT_AFTER_QS')
def fail_diag_fixture(email_info, position):
    return simple_char(email_info, position, 'edcba')


@email_parser()
def email_parser_fixture(email_info, position):
    return simple_char(email_info, position, 'edcba')


@email_parser()
def email_parser_raise_fixture(email_info, position):
    tmp_ret = simple_char(email_info, position, 'edcba')
    tmp_ret('ERR_NO_DOMAIN_PART')
    raise ParsingError(results=tmp_ret)


@email_parser(name='test_parser')
def email_named_parser_fixture(email_info, position):
    return simple_char(email_info, position, 'edcba')


@email_parser(is_history_item=False, name='test_parser')
def email_no_hist_parser_fixture(email_info, position):
    return simple_char(email_info, position, 'edcba')


@wrapped_parser('(', ')', 'ERR_CONSECUTIVE_DOTS', 'ERR_NO_DOMAIN_PART')
def wrapped_paren_parser_fixture(email_info, position):
    return simple_char(email_info, position, 'edcba')


@wrapped_parser('"', no_end_error='ERR_CONSECUTIVE_DOTS', bad_text_error='ERR_NO_DOMAIN_PART')
def wrapped_quote_parser_fixture(email_info, position):
    return simple_char(email_info, position, 'edcba')


@wrapped_parser('"', no_end_error='ERR_CONSECUTIVE_DOTS', bad_text_error='ERR_NO_DOMAIN_PART')
def wrapped_quote_parser_fixture_w_quote(email_info, position):
    tmp_ret = parse_loop(email_info, position, parse_or, 'abcdef', r'"\""')
    return tmp_ret



@is_comment
@pass_diags('ERR_ATEXT_AFTER_CFWS')
@fail_diags('ERR_ATEXT_AFTER_QS')
@email_parser()
@wrapped_parser('(', ')', 'ERR_CONSECUTIVE_DOTS', 'ERR_NO_DOMAIN_PART')
def mult_wrapper_fixture(email_info, position):
    return simple_char(email_info, position, 'edcba')


class TestWrappers(TestCase):
    maxDiff = None

    def test_comment_wrapper_found(self):
        tmp_ei = ei()
        tmp_ret = wrapped_comment_fixture(tmp_ei, 0)
        tmp_exp = (0, 5, 'bcd')
        self.assertEqual(len(tmp_ei.local_comments), 1)
        self.assertEqual(tmp_ei.local_comments[0], tmp_exp)

    def test_comment_wrapper_not_found(self):
        tmp_ei = ei()
        tmp_ret = wrapped_comment_fixture(ei(), 0)
        self.assertEqual(len(tmp_ei.local_comments), 0)

    def test_pass_wrapper_pass(self):
        tmp_ret = pass_diag_fixture(ei(), 0)
        self.assertTrue('ERR_ATEXT_AFTER_CFWS' in tmp_ret, repr(tmp_ret))

    def test_pass_wrapper_fail(self):
        tmp_ret = pass_diag_fixture(ei('zzzzz'), 0)
        self.assertFalse('ERR_ATEXT_AFTER_CFWS' in tmp_ret)

    def test_fail_wrapper_pass(self):
        tmp_ret = fail_diag_fixture(ei('zzzzzz'), 0)
        self.assertTrue('ERR_ATEXT_AFTER_QS' in tmp_ret)

    def test_fail_wrapper_fail(self):
        tmp_ret = fail_diag_fixture(ei(), 0)
        self.assertFalse('ERR_ATEXT_AFTER_QS' in tmp_ret)
        self.assertEqual(tmp_ret.history, '')

    def test_parser_wrapper_good(self):
        tmp_ei = ei()
        tmp_ret = email_parser_fixture(tmp_ei, 0)
        self.assertEqual(tmp_ret.l, 5)

    def test_parser_wrapper_bad(self):
        tmp_ei = ei('zzzz')
        tmp_ret = email_parser_fixture(tmp_ei, 0)
        self.assertEqual(tmp_ret.l, 0)
        self.assertEqual(tmp_ret.history, '')

    def test_parser_wrapper_named_kwargs(self):
        tmp_ei = ei()
        tmp_ret = email_named_parser_fixture(tmp_ei, 0)
        self.assertEqual(tmp_ret.l, 5)
        self.assertEqual(tmp_ret.history, 'test_parser')

    def test_parser_wrapper_named_param(self):
        tmp_ei = ei()
        tmp_ret = email_parser_fixture(tmp_ei, 0, name='tp2')
        self.assertEqual(tmp_ret.l, 5)
        self.assertEqual(tmp_ret.history, 'tp2')

    def test_parser_wrapper_good_no_history(self):
        tmp_ei = ei()
        tmp_ret = email_no_hist_parser_fixture(tmp_ei, 0)
        self.assertEqual(tmp_ret.l, 5)
        self.assertEqual(tmp_ret.history, '')

    def test_parser_wrapper_raised_return(self):
        tmp_ei = ei()
        try:
            tmp_ret = email_parser_raise_fixture(tmp_ei, 0)
            self.fail()
        except ParsingError as err:
            tmp_ret = err.results
            self.assertEqual(tmp_ret.l, 0)
            self.assertEqual(tmp_ret.history, '')

    def test_wrapped_parser_good(self):
        tmp_ei = ei('(abcde)fghijk')
        tmp_ret = wrapped_paren_parser_fixture(tmp_ei, 0)
        self.assertEqual(tmp_ret.l, 7)

    def test_wrapped_parser_no_end(self):
        tmp_ei = ei('"abcde"fghijk')
        tmp_ret = wrapped_quote_parser_fixture(tmp_ei, 0)
        self.assertEqual(tmp_ret.l, 7)

    def test_wrapped_parser_skipping_qs(self):
        tmp_ei = ei(r'"a\"bcde"fghijk')
        tmp_ret = wrapped_quote_parser_fixture_w_quote(tmp_ei, 0)
        self.assertEqual(tmp_ret.l, 9)

    def test_wrapped_parser_no_close_fail(self):
        tmp_ei = ei('(abcde')
        tmp_ret = wrapped_paren_parser_fixture(tmp_ei, 0)
        self.assertTrue('ERR_CONSECUTIVE_DOTS' in tmp_ret)
        self.assertEqual(tmp_ret.l, 0)

    def test_wrapped_parser_bad_text_fail(self):
        tmp_ei = ei('(abcdefghi')
        tmp_ret = wrapped_paren_parser_fixture(tmp_ei, 0)
        self.assertTrue('ERR_NO_DOMAIN_PART' in tmp_ret)
        self.assertEqual(tmp_ret.l, 0)


