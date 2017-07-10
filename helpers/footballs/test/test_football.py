import unittest

from helpers.meta_data import META_LOOKUP
from helpers.exceptions import ParsingError
from helpers.footballs.footballs import ParseResultFootball, ParsingObj
from helpers.test_helpers import *


def _test_name(l1, l2=None, l3=None, suffix=None):
    tmp_ret = l1
    if l2 is not None:
        tmp_ret += '-'
        tmp_ret += RETURN_OBJ_L2[l2][0]
    if l3 is not None:
        tmp_ret += '-'
        tmp_ret += RETURN_OBJ_L3[l3][0]
    if suffix is not None:
        tmp_ret += '-'
        tmp_ret += suffix
    return tmp_ret


class TestEmailInfo(unittest.TestCase):

    def make_ei(self, email_in='abcde"fghi"jk(lm)nop', **kwargs):
        return ParsingObj(email_in=email_in, **kwargs)

    def test_init(self):
        ei = self.make_ei()
        self.assertEqual(str(ei), 'abcde"fghi"jk(lm)nop')

    def test_get_item(self):
        ei = self.make_ei()
        self.assertEqual(ei[:3], 'abc')

    def test_at_end(self):
        ei = self.make_ei()
        self.assertFalse(ei.at_end(19))
        self.assertTrue(ei.at_end(20))
        self.assertTrue(ei.at_end(21))
        self.assertTrue(ei.at_end(40))

    def test_is_last(self):
        ei = self.make_ei()
        self.assertFalse(ei.is_last(19))
        self.assertTrue(ei.is_last(20))
        self.assertFalse(ei.is_last(21))
        self.assertFalse(ei.is_last(40))

    def test_len(self):
        ei = self.make_ei()
        self.assertEqual(len(ei), 20)

    def test_mid(self):
        ei = self.make_ei()
        self.assertEqual(ei.mid(0, 2), 'ab')
        self.assertEqual(ei.mid(length=10), 'abcde"fghi')
        self.assertEqual(ei.mid(19), 'p')
        self.assertEqual(ei.mid(7, 4), 'ghi"')

    def test_slice(self):
        ei = self.make_ei()
        self.assertEqual(ei.slice(0, 2), 'ab')
        self.assertEqual(ei.slice(0,10), 'abcde"fghi')
        self.assertEqual(ei.slice(19), 'p')
        self.assertEqual(ei.slice(13, -2), '(lm)n')

    def test_remaining(self):
        ei = self.make_ei()
        test_exp = list('"fghi"jk(lm)nop')
        test_ret = list(ei(5))
        self.assertEqual(test_exp, test_ret)

    def test_remaining_complex(self):
        ei = self.make_ei('abcde\\"fghi\\"jk(lm)nop')
        test_exp = list('\\"fghi\\"jk(lm)n')
        test_ret = list(ei(5, end=-2))
        self.assertEqual(test_exp, test_ret)

        test_exp = list('\\"fghi\\"jk(l')
        test_ret = list(ei(5, end=-2, until_char='m'))
        self.assertEqual(test_exp, test_ret)

        test_exp = list('fghijk(l')
        test_ret = list(ei(5, end=-2, until_char='m', skip_quoted=True))
        self.assertEqual(test_exp, test_ret)

    def test_count(self):
        ei = self.make_ei('abcde\\"fghi\\"jk(lm)nop')
        self.assertEqual(ei.count(5, '"'), 2)
        self.assertEqual(ei.count(18, '"'), 0)
        self.assertEqual(ei.count(5, 'f'), 1)
        self.assertEqual(ei.count(5, '"', skip_quoted=True), 0)
        self.assertEqual(ei.count(5, '"', until_char='g'), 1)

    def test_find(self):
        ei = self.make_ei('abcde\\"fghi\\"jk(lm)nop')
        self.assertEqual(ei.find(0, 'c'), 2)
        self.assertEqual(ei.find(5, 'c'), -1)
        self.assertEqual(ei.find(5, '"', skip_quoted=True), -1)
        self.assertEqual(ei.find(5, '"', until_char='g'), 6)

    def test_flags(self):
        ei = self.make_ei()
        self.assertFalse(ei.flags.in_crlf)
        self.assertFalse(ei.flags.at_in_cfws)
        self.assertFalse(ei.flags.near_at_flag)

        ei.flags.in_crlf = True
        ei.flags.at_in_cfws = False
        ei.flags.near_at_flag = False

        self.assertTrue(ei.flags.in_crlf)
        self.assertFalse(ei.flags.at_in_cfws)
        self.assertFalse(ei.flags.near_at_flag)

    def test_trace(self):
        ei = self.make_ei()


class TestParseFootball(unittest.TestCase):

    def fb(self, email_in='abcdefghijklmnop', stage='test', begin=0, length=0, **kwargs):
        ei = ParsingObj(email_in, **kwargs)
        fb = ParseResultFootball(ei, stage, begin)
        if length:
            fb.set_length(length)
        return fb

    def setUp(self):
        META_LOOKUP.clear_overrides()

    def test_init_options(self):
        f = self.fb()
        self.assertEquals(f.length, 0)

        f += 10
        self.assertEquals(f.length, 10)

        f -= 5
        self.assertEquals(f.length, 5)

    def test_math(self):
        f = self.fb()
        f2 = self.fb()

        self.assertEquals(f.length, 0)

        f += 10
        self.assertEquals(f.length, 10)

        f2 += 10
        f2 += f
        self.assertEquals(f2.length, 20)

    def test_math_2(self):
        f = self.fb()

        self.assertEquals(f + 2, 2)
        self.assertEquals(2 + f, 2)

        f += 10
        self.assertEquals(f + 2, 12)
        self.assertEquals(2 + f, 12)

        f2 = self.fb()
        f2 += 5

        self.assertEquals(f + f2, 15)
        self.assertEquals(f2 + f, 15)

    def test_init_length(self):
        f = self.fb(length=10)

        self.assertEquals(f.length, 10)

    def test_init_length_full(self):

        f = self.fb(length=13, begin=20, stage='hello')

        self.assertEquals(f.length, 13)

    def test_comp_with_int(self):
        f = self.fb(length=10)

        self.assertTrue(f > 5)
        self.assertTrue(f >= 10)
        self.assertTrue(f == 10)
        self.assertTrue(f != 20)
        self.assertTrue(f < 21)
        self.assertTrue(f <= 10)

    def test_comp_with_fb(self):
        f = self.fb(length=10)
        f10 = self.fb(length=10)
        f5 = self.fb(length=5)
        f20 = self.fb(length=20)

        self.assertTrue(f > f5)
        self.assertTrue(f >= f10)
        self.assertTrue(f == f10)
        self.assertTrue(f != f20)
        self.assertTrue(f < f20)
        self.assertTrue(f <= f10)

    def test_add_diag_str(self):
        per = self.fb()
        per.add('VALID')

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_bad_diag(self):
        per = self.fb()
        with self.assertRaises(AttributeError):
            per.add('FOOBAR')

    def test_add_diag_tuple(self):
        per = self.fb()
        per.add(('VALID',1))

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_diag_dict(self):
        per = self.fb()
        per.add({'diag': 'VALID', 'length': 1})

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_length_set(self):
        per = self.fb()
        per += 3
        self.assertEquals(per.l, 3)
        per.add('VALID', set_length=1)

        self.assertEquals(per.l, 1)

    def test_add_football(self):
        per = self.fb()
        per += 1

        per2 = self.fb()
        per += 3

        per.add(per2)

        self.assertEquals(per.l, 4)

    def test_add_length_add(self):
        per = self.fb()
        per += 1
        self.assertEquals(per.l, 1)
        per.add('VALID', length=1)

        self.assertEquals(per.l, 2)

    def test_add_ok_result(self):
        per = self.fb('test_email_in', begin=1)

        per.add(diag='VALID')

        self.assertFalse(per.error)

    def test_add_error_result(self):
        per = self.fb('test_email_in')

        with self.assertRaises(ParsingError):
            per.add(diag='ERR_FWS_CRLF_X2', raise_on_error=True)

        per.add(diag='ERR_FWS_CRLF_X2')
        self.assertTrue(per.error)
        self.assertFalse(per)

    def test_add_warn_result(self):
        per = self.fb('test_email_in')

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertFalse(per.error)

    def test_add_mult_result(self):
        per = self.fb('test_email_in')

        # self.assertTrue(per)
        # self.assertEquals(len(per), 0)

        per.add(diag='VALID', begin=1, length=1)
        # self.assertTrue(per)
        self.assertEquals(len(per), 1)
        self.assertFalse(per.error)

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        # self.assertTrue(per)
        self.assertEquals(len(per), 2)
        self.assertFalse(per.error)

        per.add(diag='ERR_FWS_CRLF_X2', begin=1, length=1)
        self.assertTrue(per.error)

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertTrue(per.error)

    def test_error_on_warn(self):

        META_LOOKUP.set_error_on_warning(True)
        per = self.fb('test_email_in')

        per.add(diag='VALID', begin=1, length=1)
        self.assertFalse(per.error)

        with self.assertRaises(ParsingError):
            per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1, raise_on_error=True)
        self.assertTrue(per.error)

        per.add(diag='VALID', begin=1, length=1)
        self.assertTrue(per.error)

    def test_error_on_value(self):
        per = self.fb('test_email_in')

        META_LOOKUP.set_error_on('VALID')
        per('DNSWARN_NO_MX_RECORD')
        with self.assertRaises(ParsingError):
            per.add('VALID', raise_on_error=True)
        self.assertTrue(per.error)

    def test_contains(self):
        per = self.fb('test_email_in')

        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag':'DNSWARN_NO_MX_RECORD', 'begin':1, 'length':1})
        per.add(diag='DEPREC_QTEXT')
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertIn('DNSWARN_NO_MX_RECORD', per)

        self.assertNotIn('foobar', per)

    # def test_clear(self):
    #     per = self.fb('test_email_in')
    #
    #     self.assertEquals(len(per), 0)
    #     per += 10
    #
    #     per.add(diag=('VALID', 1, 1))
    #     per.add(diag={'diag':'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
    #     per.add(diag='DEPREC_QTEXT', raise_on_error=False)
    #     per.add(diag='DNSWARN_NO_MX_RECORD')
    #
    #     self.assertEquals(len(per), 4)
    #     self.assertEquals(per.l, 10)
    #     per.clear()
    #
    #     self.assertEquals(len(per), 0)
    #     self.assertEquals(per.l, 0)

    def test_remove(self):
        per = self.fb('test_email_in')

        per += 10

        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag': 'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
        per.add(diag='DEPREC_QTEXT', raise_on_error=False)
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertEquals(len(per), 4)
        self.assertEquals(per.l, 10)

        per.remove(diag='VALID')
        self.assertEquals(len(per), 3)

        per.remove('DNSWARN_NO_MX_RECORD', rem_all=True)
        self.assertEquals(len(per), 1)


        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag': 'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
        per.add(diag='DEPREC_QTEXT', raise_on_error=False)
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertEquals(len(per), 5)

        per.remove('DNSWARN_NO_MX_RECORD')
        self.assertEquals(len(per), 4)

    def test_max_first_good_second_bad(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_1 += 10

        self.assertEqual(per_1.l, 10)
        self.assertEqual(per_2.l, 0)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 10)
        self.assertEqual(per_ret.history, 'p1')

    def test_max_second_good_first_bad(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_2 += 10

        self.assertEqual(per_2.l, 10)
        self.assertEqual(per_1.l, 0)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 10)
        self.assertEqual(per_ret.history, 'p2')

    def test_max_both_good_equal(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_2 += 10
        per_1 += 10

        self.assertEqual(per_2.l, 10)
        self.assertEqual(per_1.l, 10)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 10)
        self.assertEqual(per_ret.history, 'p1')

    def test_max_both_good_one_longer(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_2 += 10
        per_1 += 5

        self.assertEqual(per_2.l, 10)
        self.assertEqual(per_1.l, 5)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 10)
        self.assertEqual(per_ret.history, 'p2')

    def test_max_both_good_equal_different_codes(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_2 += 10
        per_1 += 10
        per_1('DNSWARN_NO_MX_RECORD')
        per_2('DNSWARN_NO_RECORD')

        self.assertEqual(per_2.l, 10)
        self.assertEqual(per_1.l, 10)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 10)
        self.assertEqual(per_ret.history, 'p2')

    def test_max_both_good_equal_different_codes_2(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_2 += 10
        per_1 += 10
        per_2('DNSWARN_NO_MX_RECORD')
        per_1('DNSWARN_NO_RECORD')

        self.assertEqual(per_2.l, 10)
        self.assertEqual(per_1.l, 10)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 10)
        self.assertEqual(per_ret.history, 'p1')


    def test_max_both_bad_different_codes(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_2 += 10
        per_1 += 10
        per_2('ERR_CONSECUTIVE_DOTS')
        per_1('ERR_ATEXT_AFTER_CFWS')

        self.assertEqual(per_2.l, 0)
        self.assertEqual(per_1.l, 0)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 0)
        self.assertEqual(per_ret.history, 'p1')


    def test_max_both_bad_different_codes_2(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_2 += 10
        per_1 += 10
        per_1('ERR_CONSECUTIVE_DOTS')
        per_2('ERR_ATEXT_AFTER_CFWS')

        self.assertEqual(per_2.l, 0)
        self.assertEqual(per_1.l, 0)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 0)
        self.assertEqual(per_ret.history, 'p2')


    def test_max_both_bad_different_max_lengths(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_2 += 10
        per_1 += 5
        per_1('ERR_CONSECUTIVE_DOTS')
        per_2('ERR_CONSECUTIVE_DOTS')

        self.assertEqual(per_2.l, 0)
        self.assertEqual(per_1.l, 0)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 0)
        self.assertEqual(per_ret.history, 'p2')

    def test_max_both_bad_different_max_lengths_2(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_1 += 10
        per_2 += 5
        per_1('ERR_CONSECUTIVE_DOTS')
        per_2('ERR_CONSECUTIVE_DOTS')

        self.assertEqual(per_2.l, 0)
        self.assertEqual(per_1.l, 0)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 0)
        self.assertEqual(per_ret.history, 'p1')

    def test_max_both_equal(self):
        per_1 = self.fb('test_email_in')
        per_1.set_history('p1', 0)
        per_2 = self.fb('test_email_in')
        per_2.set_history('p2', 0)

        per_2 += 10
        per_1 += 10
        per_1('ERR_CONSECUTIVE_DOTS')
        per_2('ERR_CONSECUTIVE_DOTS')

        self.assertEqual(per_2.l, 0)
        self.assertEqual(per_1.l, 0)

        per_ret = per_1.max(per_2)

        self.assertEqual(per_ret.l, 0)
        self.assertEqual(per_ret.history, 'p1')
