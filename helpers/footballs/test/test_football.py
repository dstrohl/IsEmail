import unittest

from helpers.meta_data import META_LOOKUP
from helpers.exceptions import ParsingError
from helpers.footballs.footballs import ParseResultFootball
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


class TestParseFootball(unittest.TestCase):

    def setUp(self):
        META_LOOKUP.clear_overrides()

    def test_init_options(self):
        f = ParseResultFootball(PF)
        self.assertEquals(f.length, 0)

        f += 10
        self.assertEquals(f.length, 10)

        f -= 5
        self.assertEquals(f.length, 5)

    def test_math(self):
        f = ParseResultFootball(PF)
        f2 = ParseResultFootball(PF)

        self.assertEquals(f.length, 0)

        f += 10
        self.assertEquals(f.length, 10)

        f2 += 10
        f2 += f
        self.assertEquals(f2.length, 20)

    def test_math_2(self):
        f = ParseResultFootball(PF)

        self.assertEquals(f + 2, 2)
        self.assertEquals(2 + f, 2)

        f += 10
        self.assertEquals(f + 2, 12)
        self.assertEquals(2 + f, 12)

        f2 = ParseResultFootball(PF)
        f2 += 5

        self.assertEquals(f + f2, 15)
        self.assertEquals(f2 + f, 15)

    def test_init_length(self):
        f = ParseResultFootball(PF, length=10)

        self.assertEquals(f.length, 10)

    def test_init_length_full(self):

        f = ParseResultFootball(PF, length=13, position=20, segment='hello')

        self.assertEquals(f.length, 13)

    def test_comp_with_int(self):
        f = ParseResultFootball(PF, length=10)

        self.assertTrue(f > 5)
        self.assertTrue(f >= 10)
        self.assertTrue(f == 10)
        self.assertTrue(f != 20)
        self.assertTrue(f < 21)
        self.assertTrue(f <= 10)

    def test_comp_with_fb(self):
        f = ParseResultFootball(PF, length=10)
        f10 = ParseResultFootball(PF, length=10)
        f5 = ParseResultFootball(PF, length=5)
        f20 = ParseResultFootball(PF, length=20)

        self.assertTrue(f > f5)
        self.assertTrue(f >= f10)
        self.assertTrue(f == f10)
        self.assertTrue(f != f20)
        self.assertTrue(f < f20)
        self.assertTrue(f <= f10)

    def test_add_diag_str(self):
        per = ParseResultFootball(PF)
        per.add('VALID')

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_bad_diag(self):
        per = ParseResultFootball(PF)
        with self.assertRaises(AttributeError):
            per.add('FOOBAR')

    def test_add_diag_tuple(self):
        per = ParseResultFootball(PF)
        per.add(('VALID',1))

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_diag_dict(self):
        per = ParseResultFootball(PF)
        per.add({'diag': 'VALID', 'length': 1})

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_length_set(self):
        per = ParseResultFootball(PF)
        per += 3
        self.assertEquals(per.l, 3)
        per.add('VALID', set_length=1)

        self.assertEquals(per.l, 1)

    def test_add_football(self):
        per = ParseResultFootball(PF)
        per += 1

        per2 = ParseResultFootball(PF)
        per += 3

        per.add(per2)

        self.assertEquals(per.l, 4)

    def test_add_length_add(self):
        per = ParseResultFootball(PF)
        per += 1
        self.assertEquals(per.l, 1)
        per.add('VALID', length=1)

        self.assertEquals(per.l, 2)

    def test_add_ok_result(self):
        per = ParseResultFootball(PF, 'test_email_in', position=1)

        per.add(diag='VALID')

        self.assertFalse(per.error)

    def test_add_error_result(self):
        per = ParseResultFootball(PF, 'test_email_in')

        with self.assertRaises(ParsingError):
            per.add(diag='ERR_FWS_CRLF_X2')

        self.assertTrue(per.error)

    def test_add_warn_result(self):
        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertFalse(per.error)

    def test_add_mult_result(self):
        per = ParseResultFootball(PF, 'test_email_in')

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

        with self.assertRaises(ParsingError):
            per.add(diag='ERR_FWS_CRLF_X2', begin=1, length=1)
        self.assertTrue(per.error)

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertTrue(per.error)

    def test_error_on_warn(self):

        META_LOOKUP.set_error_on_warning(True)
        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag='VALID', begin=1, length=1)
        self.assertFalse(per.error)

        with self.assertRaises(ParsingError):
            per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertTrue(per.error)

        per.add(diag='VALID', begin=1, length=1)
        self.assertTrue(per.error)

    def test_error_on_value(self):
        per = ParseResultFootball(PF, 'test_email_in')

        META_LOOKUP.set_error_on('VALID')
        per('DNSWARN_NO_MX_RECORD')
        with self.assertRaises(ParsingError):
            per.add('VALID')
        self.assertTrue(per.error)

    def test_contains(self):
        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag':'DNSWARN_NO_MX_RECORD', 'begin':1, 'length':1})
        per.add(diag='DEPREC_QTEXT')
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertIn('DNSWARN_NO_MX_RECORD', per)

        self.assertNotIn('foobar', per)

    def test_clear(self):
        per = ParseResultFootball(PF, 'test_email_in')

        self.assertEquals(len(per), 0)
        per += 10

        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag':'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
        per.add(diag='DEPREC_QTEXT', raise_on_error=False)
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertEquals(len(per), 4)
        self.assertEquals(per.l, 10)
        per.clear()

        self.assertEquals(len(per), 0)
        self.assertEquals(per.l, 0)

    def test_remove(self):
        per = ParseResultFootball(PF, 'test_email_in')

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

