from unittest import TestCase

from helpers.flag_manager.flag_helper import FlagHelper
from copy import copy, deepcopy

class TestOpenFlagManager(TestCase):
    maxDiff = None

    def test_init(self):
        fm = FlagHelper()
        fm.test = True
        self.assertTrue(fm.test)
        self.assertFalse(fm.test3)

    def test_add_item(self):
        fm = FlagHelper()
        fm['test'] = True
        self.assertTrue(fm.test)
        self.assertFalse(fm.test3)

    def test_add_item_obj(self):
        fm = FlagHelper('+test1', '+test2')
        fm2 = FlagHelper('-test2', '+test3')
        fm3 = fm + fm2
        self.assertTrue(fm3.test1)
        self.assertFalse(fm3.test2)
        self.assertTrue(fm3.test3)

    def test_add_item_invalid(self):
        fm = FlagHelper('-test1', '+test2', '-test3')
        with self.assertRaises(AttributeError):
            fm['This is a test'] = True
        with self.assertRaises(AttributeError):
            fm['_test1'] = True

    def test_rem_item(self):
        fm = FlagHelper('+test')
        self.assertTrue(fm.test)
        fm -= '+test'
        self.assertFalse(fm.test, repr(fm))
        self.assertFalse(fm.test3, repr(fm))

    def test_rem_item_obj(self):
        fm = FlagHelper('+test', '+test2')
        fm2 = FlagHelper('test')
        fm -= fm2
        self.assertFalse(fm.test)
        self.assertTrue(fm.test2)

    def test_add_on_init(self):
        fm = FlagHelper('+test1', '+test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

    def test_rem_by_method(self):
        fm = FlagHelper(test1=True, test2=True, test3=False)
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

        fm.test2 = False
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

    # def test_add_by_iadd(self):
    #     fm = FlagHelper()
    #     fm += 'test'
    #     self.assertTrue(fm.test)
    #     self.assertFalse(fm.test3)

    def test_rem_by_isub(self):
        fm = FlagHelper('+test1', '+test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

        fm(test2=False)
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

    def test_add_mult_by_call(self):
        fm = FlagHelper()
        fm += ('+test1', '+test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

        fm('+test1', '-test2', '+test3')
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertTrue(fm.test3)
        self.assertFalse(fm.test4)

    def test_contains(self):
        fm = FlagHelper()
        fm += {'test1': True, 'test2': True, 'test3': False}
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

        tmp_test = 'test1' in fm
        self.assertTrue(tmp_test)

        tmp_test = 'test6' in fm
        self.assertFalse(tmp_test)

    def test_iterate(self):
        fm = FlagHelper('+test1', '+test2', 'test3')
        tmp_lst = list(fm)

        self.assertCountEqual(tmp_lst, ['test1', 'test2', 'test3'])

    def test_clear(self):
        fm = FlagHelper('+test1', '+test2', '+test3')
        self.assertEqual(len(fm), 3)
        self.assertTrue(fm)
        fm.test2 = False
        test_bool = bool(fm)
        self.assertFalse(test_bool)

        fm._reset()
        self.assertEqual(len(fm), 3)
        self.assertTrue(fm)

    def test_get(self):
        fm = FlagHelper()
        fm('test1', 'test2', 'test3')
        tmp_lst = list(fm)

        self.assertCountEqual(tmp_lst, ['test1', 'test2', 'test3'])

    def test_get_dict(self):
        fm = FlagHelper('+test1', '+test2', '+test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': True, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_copy(self):
        fm = FlagHelper('+test1', '+test2', '+test3')
        tmp_lst = list(fm)
        tmp_exp = ['test1', 'test2', 'test3']
        self.assertCountEqual(tmp_lst, tmp_exp)

        fm2 = fm.__copy__()
        tmp_lst = list(fm2)
        tmp_exp = ['test1', 'test2', 'test3']
        self.assertCountEqual(tmp_lst, tmp_exp)

        fm2 -= 'test1'
        self.assertTrue(fm.test1)
        self.assertFalse(fm2.test1)

    def test_call(self):
        fm = FlagHelper()
        fm('test1', 'test2', 'test3')
        self.assertCountEqual(list(fm), ['test1', 'test2', 'test3'])

    def test_str(self):
        fm = FlagHelper()
        fm('test1', 'test2', 'test3')
        self.assertEqual(str(fm), '-/-|test1, -/-|test2, -/-|test3')

    def test_and(self):
        fm1 = FlagHelper('+test1', '+test2', '+test3')
        fm2 = FlagHelper('+test3', '+test4', '+test5')

        fm = fm1 & fm2
        # fm = fm1._and(fm2)

        exp_ret = ['test3']
        self.assertCountEqual(list(fm), exp_ret)

    def test_or(self):
        fm1 = FlagHelper('+test1', '+test2', '+test3')
        fm2 = FlagHelper('+test3', '+test4', '+test5')

        fm = fm1 | fm2
        exp_ret = ['test1', 'test2', 'test3', 'test4', 'test5']
        self.assertCountEqual(list(fm), exp_ret)


class TestLockedFlagManager(TestCase):

    def test_init(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_flags=True)
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test3)

    def test_add_item(self):
        fm = FlagHelper('-test1', '+test2', '-test3', lock_flags=True)
        fm['test1'] = True
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test3)

    def test_add_item_obj_raises(self):
        fm = FlagHelper('+test1', '+test2', lock_flags=True)
        fm2 = FlagHelper('-test2', '+test3', lock_flags=True)
        with self.assertRaises(AttributeError):
            fm += fm2

    def test_add_item_obj(self):
        fm = FlagHelper('-test1', '-test2', lock_flags=True)
        fm2 = FlagHelper('+test1', lock_flags=True)
        fm += fm2
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)

    def test_add_item_invalid(self):
        with self.assertRaises(AttributeError):
            fm = FlagHelper('-thjis is a test1', '+test2', '-test3', lock_flags=True)
        with self.assertRaises(AttributeError):
            fm = FlagHelper('-_foobar', '+test2', '-test3', lock_flags=True)

    def test_rem_item(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_flags=True)
        self.assertTrue(fm.test1)
        fm('-test1')
        self.assertFalse(fm.test1)
        self.assertFalse(fm.test3)

        with self.assertRaises(AttributeError):
            fm['test5'] = True

    def test_rem_item_obj(self):
        fm = FlagHelper('+test', '+test2', lock_flags=True)
        fm2 = FlagHelper('+test', '-test2', lock_flags=True)
        with self.assertRaises(AttributeError):
            fm -= fm2

    def test_add_on_init(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_flags=True)
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        with self.assertRaises(AttributeError):
            exp = fm.test4

    def test_rem_by_method(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_flags=True)
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)

        fm.test2 = False
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)

    def test_add_by_iadd(self):
        fm = FlagHelper(test1=True, test2=True, test3=False, lock_flags=True)
        self.assertFalse(fm.test3)
        fm.test3 = True
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test3, repr(fm))

    def test_rem_by_isub(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_flags=True)
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)

        fm(test2=False)
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)

    def test_add_mult_by_iadd(self):
        fm = FlagHelper('test1', 'test2', 'test3', lock_flags=True)
        fm += ('+test1', '+test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)

        with self.assertRaises(AttributeError):
            fm -= ('test1', '-test2', '+test3')

    def test_contains(self):
        fm = FlagHelper('-test1', '-test2', '-test3', lock_flags=True)
        self.assertFalse(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)
        with self.assertRaises(AttributeError):
            self.assertFalse(fm.test4)

        fm('test1')

        tmp_test = 'test1' in fm
        self.assertTrue(tmp_test)

        tmp_test = 'test3' in fm
        self.assertTrue(tmp_test)

        tmp_test = 'test5' in fm
        self.assertFalse(tmp_test)

    def test_iterate(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_flags=True)
        tmp_lst = list(fm)

        self.assertCountEqual(tmp_lst, ['test1', 'test2', 'test3'])

    def test_reset(self):
        fm = FlagHelper('+test1', '+test2', '+test3', lock_flags=True)
        self.assertEqual(len(fm), 3)
        self.assertTrue(fm)
        fm.test1 = False
        self.assertFalse(fm['test1'])
        self.assertFalse(fm)
        fm._reset()
        self.assertTrue(fm)
        self.assertTrue(fm.test1)
        self.assertEqual(len(fm), 3)

    def test_get_dict(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_flags=True)
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_get_dict_true(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_flags=True)
        tmp_lst = fm._get_dict(filter_for=True)
        tmp_exp = {'test1': True, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_get_dict_false(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_flags=True)
        tmp_lst = fm._get_dict(filter_for=False)
        tmp_exp = {'test2': False}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_copy(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_flags=True)
        fm('-test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        fm2 = copy(fm)
        tmp_lst = fm2._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        self.assertEqual(fm, fm2)

        self.assertTrue(fm.test1)
        self.assertTrue(fm2.test1)

        fm2.test1 = False

        self.assertTrue(fm.test1)
        self.assertFalse(fm2.test1)

        self.assertNotEqual(fm, fm2)

    def test_clear(self):
        fm = FlagHelper('+test1', '*-test2', '+test3', lock_flags=True)
        fm('-test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        fm._clear()
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': False, 'test2': None, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_call(self):
        fm = FlagHelper('+test1', '+test2', '+test3', lock_flags=True)
        fm('-test2', 'test3')
        self.assertEqual(str(fm), '+/+|test1, -/-|test2, -/-|test3')

    def test_str(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_flags=True)
        self.assertEqual(str(fm), '+/+|test1, -/-|test2, +/+|test3')

    def test_and_1(self):
        fm1 = FlagHelper('-test1', '+test2', '+test3', lock_flags=True)
        fm2 = FlagHelper('+test3', '+test4', '-test5', lock_flags=True)

        fm = fm1 & fm2

        exp_ret = '+/+|test3'
        self.assertEqual(str(fm), exp_ret)

    def test_and_2(self):
        fm1 = FlagHelper('+test1', '+test2', '+test3', lock_flags=True)
        fm2 = FlagHelper('+test1', '+test2', '-test3', lock_flags=True)

        fm = fm1 & fm2

        exp_ret = '+/+|test1, +/+|test2'
        self.assertEqual(str(fm), exp_ret)

    def test_or_1(self):
        fm1 = FlagHelper('-test1', '+test2', '-test3', lock_flags=True)
        fm2 = FlagHelper('-test3', '+test4', '+test5', lock_flags=True)

        fm = fm1 | fm2
        exp_ret = '+/+|test2, +/+|test4, +/+|test5'
        self.assertEqual(str(fm), exp_ret)

    def test_or_2(self):
        fm1 = FlagHelper('+test1', '+test2', '+test3', lock_flags=True)
        fm2 = FlagHelper('+test1', '+test2', '-test3', lock_flags=True)

        fm = fm1 | fm2
        exp_ret = '+/+|test1, +/+|test2, +/+|test3'
        self.assertEqual(str(fm), exp_ret)

    def test_and_3(self):
        fm1 = FlagHelper('-test1', '+test2', '+test3', lock_flags=True)
        fm2 = FlagHelper('+test3', '+test4', '-test5')

        fm = fm1 & fm2

        exp_ret = '+/+|test3'
        self.assertEqual(str(fm), exp_ret)

    def test_and_4(self):
        fm1 = FlagHelper('+test1', '+test2', '+test3', lock_flags=True)
        fm2 = FlagHelper('+test1', '+test2', '-test3')

        fm = fm2 & fm1

        exp_ret = '+/+|test1, +/+|test2'
        self.assertEqual(str(fm), exp_ret)

    def test_or_3(self):
        fm1 = FlagHelper('+test1', '+test2', '-test3', lock_flags=True)
        fm2 = FlagHelper('+test1', '+test4', '-test3')

        fm = fm1 | fm2
        exp_ret = '+/+|test1, +/+|test2, +/+|test4'
        self.assertEqual(str(fm), exp_ret)

    def test_or_4(self):

        fm1 = FlagHelper('+test1', '+test4', '-test3', lock_flags=True)
        fm2 = FlagHelper('+test3', '+test4', '+test5')

        fm = fm2 | fm1
        exp_ret = '+/+|test3, +/+|test4, +/+|test5, +/+|test1'
        self.assertEqual(str(fm), exp_ret)


def check_flag_set(flag_helper, **kwargs):
    tmp_ret_msg = ['', '', '%r' % flag_helper]
    tmp_good_template = '  %s: is %r'
    tmp_bad_template = '* %s: is %r <= INVALID, should be %r'
    passed_all = True


    for flag, value in kwargs.items():
        tmp_ret = getattr(flag_helper, flag)

        # if value is None and tmp_ret is None:
        #     tmp_ret_msg.append(tmp_good_template % (flag, value))
        if tmp_ret == value:
            tmp_ret_msg.append(tmp_good_template % (flag, tmp_ret))
        else:
            passed_all = False
            tmp_ret_msg.append(tmp_bad_template % (flag, tmp_ret, value))

    return passed_all, '\n'.join(tmp_ret_msg)

MTA = []
MTK = {}

DN = {'ts1': None, 'ts2': None, 'ts3': None, 'test_set': False}
D0 = {'ts1': False, 'ts2': False, 'ts3': False, 'test_set': False}
D1 = {'ts1': True, 'ts2': False, 'ts3': False, 'test_set': True}
D2 = {'ts1': False, 'ts2': True, 'ts3': False, 'test_set': True}
D3 = {'ts1': False, 'ts2': False, 'ts3': True, 'test_set': True}

IN = ['test_set', ('*', 'ts1', 'ts2', 'ts3')]
INN = ['test_set', ('*-', 'ts1', 'ts2', 'ts3')]
IN1 = ['test_set', ('*-', '+ts1', '-ts2', '-ts3')]

I0 = ['test_set', ('-', 'ts1', 'ts2', 'ts3')]
I10 = ['test_set', ('-', '+ts1', '-ts2', '-ts3')]
I01 = ['test_set', ('-', '-+ts1', '--ts2', '--ts3')]

I1 = ['test_set', ('+ts1', '-ts2', '-ts3')]
I2 = ['test_set', ('-ts1', '+ts2', '-ts3')]
I3 = ['test_set', ('ts1', 'ts2', 'ts3')]

I31 = ['test_set', ('-+ts1', '--ts2', '+-ts3')]

'''
UN = ('*', 'us1', 'us2', 'us3')
UNN = ('*-', 'us1', 'us2', 'us3')
UN1 = ('*-', '++us1', '--us2', '--us3')

U0 = ('-', 'us1', 'us2', 'us3')
U10 = ('-', '+-us1', '-us2', '-us3')
U01 = ('-', '-+us1', '--us2', '--us3')

U1 = ('+us1', '-us2', '-us3')
U2 = ('-us1', '+us2', '-us3')
U3 = ('us1', 'us2', 'us3')

U31 = ('-+us1', 'us2', '+-us3')
'''

TT1x = '+test1'
TT1F = '+-|test1'

TF1x = '-test1'
TF1T = '-/+|test1'

TN1N = '*test1'
TN1T = '*+test1'
TN1F = '*-test1'

TT2x = '+test2'
TT2F = '+-test2'

TF2x = '-test2'
TF2T = '-+test2'

TN2N = '*test2'
TN2T = '*+test2'
TN2F = '*-test2'

T2T = {'test2': True}
T2F = {'test2': False}
T2N = {'test2': None}

FLAG_SET_TESTS = (
    # (test_number, args, kwargs, initial_dict, reset_dict, clear_dict, (
    #   (step_number, field, set_to, expected_dict),
    #   (step_number, field, set_to, expected_dict))

    # IN = ['test_set', ('*', 'ts1', 'ts2', 'ts3')]
    (100, [IN], MTK, DN, DN, DN, (
        (0, 'ts1', True, D1),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, AttributeError),
        (3, 'ts3', False, AttributeError),
    )),

    # IN = ['test_set', ('*', 'ts1', 'ts2', 'ts3')]
    (101, [IN], MTK, DN, DN, DN, (
        (0, 'ts1', False, AttributeError),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, AttributeError),
        (3, 'ts3', False, AttributeError),
    )),
    # INN = ['test_set', ('*-', 'ts1', 'ts2', 'ts3')]
    (110, [INN], MTK, DN, DN, DN, (
        (0, 'ts1', True, D1),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, D3),
        (3, 'ts3', False, D0),
    )),

    # INN = ['test_set', ('*-', 'ts1', 'ts2', 'ts3')]
    (111, [INN], MTK, DN, DN, DN, (
        (0, 'ts1', False, D0),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, D3),
        (3, 'ts3', False, D0),
    )),

    # IN1 = ['test_set', ('*-', '+ts1', 'ts2', 'ts3')]
    (120, [IN1], MTK, D1, D1, DN, (
        (0, 'ts1', False, D0),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, D3),
        (3, 'ts3', False, D0),
    )),

    # I0 = ['test_set', ('-', 'ts1', 'ts2', 'ts3')]
    (130, [I0], MTK, D0, D0, D0, (
        (0, 'ts1', True, D1),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, D3),
        (3, 'ts3', False, D0),
    )),
    # I0 = ['test_set', ('-', 'ts1', 'ts2', 'ts3')]
    (140, [I0], MTK, D0, D0, D0, (
        (0, 'ts1', False, D0),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, D3),
        (3, 'ts3', False, D0),
    )),

    # I10 = ['test_set', ('-', '+ts1', 'ts2', 'ts3')]
    (150, [I10], MTK, D1, D1, D0, (
        (0, 'ts1', True, D1),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, D3),
        (3, 'ts3', False, D0),
    )),

    # I01 = ['test_set', ('-', 'ts1+', 'ts2', 'ts3')]
    (160, [I01], MTK, D1, D0, D0, (
        (0, 'ts1', False, D0),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, D3),
        (3, 'ts3', False, D0),
    )),

    # I1 = ['test_set', ('+ts1', 'ts2', 'ts3')]
    (200, [I1], MTK, D1, D1, D1, (
        (0, 'ts1', True, D1),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, AttributeError),
        (3, 'ts3', False, AttributeError),
    )),
    # I2 = ['test_set', ('ts1', '+ts2', 'ts3')]
    (210, [I2], MTK, D2, D2, D2, (
        (0, 'ts1', True, D1),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, AttributeError),
        (3, 'ts3', False, AttributeError),
    )),
    # I3 = ['test_set', ('ts1', 'ts2', 'ts3')]
    (220, [I3], MTK, D3, D3, D3, (
        (0, 'ts1', True, D1),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, AttributeError),
        (3, 'ts3', False, AttributeError),
    )),

    # I31 = ['test_set', ('ts1+', 'ts2', '+ts3')]
    (230, [I31], MTK, D1, D3, D3, (
        (0, 'ts1', True, D1),
        (1, 'ts3', True, D3),
        (2, 'ts2', False, AttributeError),
        (3, 'ts3', False, AttributeError),
    )),

    (400, MTA, {'test_set': '* ts1 ts2 ts3'}, DN, D3, DN, ()),

    (500, MTA, {'test_set': I0[1]}, D0, D0, D0, ()),

    # TT2x = '+test2'
    (600, [TT2x], MTK, T2T, T2T, T2F, (
        (0, 'test2', True, T2T),
        (1, 'test2', False, T2F),
        (2, 'test2', None, T2F),
    )),

    # TT2F = '+-test2'
    (601, [TT2F], MTK, T2F, T2T, T2F, (
        (0, 'test2', True, T2T),
        (1, 'test2', False, T2F),
        (2, 'test2', None, T2F),

    )),
    # TF2x = '-test2'
    (602, [TF2x], MTK, T2F, T2F, T2F, (
        (0, 'test2', True, T2T),
        (1, 'test2', False, T2F),
        (2, 'test2', None, T2F),

    )),
    # TF2T = '-+test2'
    (603, [TF2T], MTK, T2T, T2F, T2F, (
        (0, 'test2', True, T2T),
        (1, 'test2', False, T2F),
        (2, 'test2', None, T2F),

    )),
    # TN2N = '*test2'
    (604, [TN2N], MTK, T2N, T2N, T2N, (
        (0, 'test2', True, T2T),
        (1, 'test2', False, T2F),
        (2, 'test2', None, T2F),

    )),
    # TN2T = '*+test2'
    (605, [TN2T], MTK, T2T, T2N, T2N, (
        (0, 'test2', True, T2T),
        (1, 'test2', False, T2F),
        (2, 'test2', None, T2F),

    )),
    # TN2F = '*-test2'
    (606, [TN2F], MTK, T2F, T2N, T2N, (
        (0, 'test2', True, T2T),
        (1, 'test2', False, T2F),
        (2, 'test2', None, T2F),

    )),

    (607, ['*-+test2'], MTK, T2T, T2F, T2N, (
        (0, 'test2', True, T2T),
        (1, 'test2', False, T2F),
        (2, 'test2', None, T2F),

    )),
    (608, ['*+*test2'], MTK, T2N, T2T, T2N, (
        (0, 'test2', True, T2T),
        (1, 'test2', False, T2F),
        (2, 'test2', None, T2F),

    )),
    (609, ['*+-test2'], MTK, T2F, T2T, T2N, (
        (0, 'test2', True, T2T),
        (1, 'test2', False, T2F),
        (2, 'test2', None, T2F),

    )),

)



"""

TT2x = '+test2'
TT2F = '+test2-'

TF2x = '-test2'
TF2T = '-test2+'

TN2N = '*test2'
TN2T = '*test2+'
TN2F = '*test2-'

T2T = {'test2': True}
T2F = {'test2': False}
T2N = {'test2': None}
"""



def make_msg(test_data, step_data, operation_name, msg_in, pre_repr, post_repr):
    tmp_ret = ['','']
    tmp_ret.append('Test: %r\nInitial Args: %r\nInitial Kwargs: %r' % (test_data[0], test_data[1], test_data[2]))
    if step_data is not None:
        tmp_ret.append('Step: %r' % step_data[0])

    tmp_ret.append('\n************************')
    if pre_repr is not None:
        tmp_ret.append('Pre Action: %s' % pre_repr)

    if operation_name == 'set':
        operation_name += ' %s to %r' % (step_data[1], step_data[2])
    tmp_ret.append(operation_name)
    tmp_ret.append('Post Action: %s' % post_repr)
    tmp_ret.append(msg_in)
    tmp_ret.append('\n************************')
    return '\n'.join(tmp_ret)


class TestFlagSetManagerSettings(TestCase):
    maxDiff = None

    def test_sets(self):

        LIMIT_TO = -1

        if LIMIT_TO != -1:
            with self.subTest('LIMITED TEST!'):
                self.fail()

        for test in FLAG_SET_TESTS:
            num, args, kwargs, init_set, reset_set, clear_set, steps = test
            if LIMIT_TO == -1 or LIMIT_TO == num:
                with self.subTest('test # %s: init' % str(num)):
                    fm = FlagHelper(*args, **kwargs)
                    test_pass, msg = check_flag_set(fm, **init_set)
                    msg = make_msg(test, None, 'init', msg, None, repr(fm))
                    self.assertTrue(test_pass, msg)

                    for snum, field, set_to, exp_set in steps:
                        if isinstance(exp_set, dict):
                            with self.subTest('test #%s: step #%s: set' % (str(num), str(snum))):
                                pre_repr = repr(fm)
                                fm[field] = set_to
                                test_pass, msg = check_flag_set(fm, **exp_set)
                                msg = make_msg(test, (snum, field, set_to), 'set', msg, pre_repr, repr(fm))
                                self.assertTrue(test_pass, msg)

                            with self.subTest('test #%s: step #%s: copy' % (str(num), str(snum))):
                                pre_repr = repr(fm)
                                fm2 = copy(fm)
                                test_pass, msg = check_flag_set(fm2, **exp_set)
                                msg = make_msg(test, (snum, field, set_to), 'copy', msg, pre_repr, repr(fm2))
                                self.assertTrue(test_pass, msg)

                            with self.subTest('test #%s: step #%s: clear' % (str(num), str(snum))):
                                pre_repr = repr(fm2)
                                fm2._clear()
                                test_pass, msg = check_flag_set(fm2, **clear_set)
                                msg = make_msg(test, (snum, field, set_to), 'clear', msg, pre_repr, repr(fm2))
                                self.assertTrue(test_pass, msg)

                            with self.subTest('test #%s: step #%s: copy_default' % (str(num), str(snum))):
                                pre_repr = repr(fm)
                                fm2 = fm._copy_default()
                                test_pass, msg = check_flag_set(fm2, **reset_set)
                                msg = make_msg(test, (snum, field, set_to), 'copy_default', msg, pre_repr, repr(fm2))
                                self.assertTrue(test_pass, msg)

                            with self.subTest('test #%s: step #%s: reset' % (str(num), str(snum))):
                                pre_repr = repr(fm2)
                                fm2._reset()
                                test_pass, msg = check_flag_set(fm2, **reset_set)
                                msg = make_msg(test, (snum, field, set_to), 'reset', msg, pre_repr, repr(fm2))
                                self.assertTrue(test_pass, msg)

                            with self.subTest('test #%s: step #%s: deepcopy' % (str(num), str(snum))):
                                pre_repr = repr(fm)
                                fm2 = deepcopy(fm)
                                test_pass, msg = check_flag_set(fm2, **exp_set)
                                msg = make_msg(test, (snum, field, set_to), 'deepcopy', msg, pre_repr, repr(fm2))
                                self.assertTrue(test_pass, msg)

                        else:
                            with self.subTest('test #%s: step #%s: raises' % (str(num), str(snum))):
                                msg = '\n\n%r\n\nSet %s to %r' % (fm, field, set_to)
                                msg = make_msg(test, (snum, field, set_to), 'raise', msg, repr(fm), 'N/A')
                                with self.assertRaises(exp_set, msg=msg):
                                    fm[field] = set_to


class TestFlagManagerStrings(TestCase):
    def test_strings(self):
        fm = FlagHelper('-test1+', '*test2', ['test_set', ('*-', '+ts1', '-ts2', '-ts3')], ('test_set_2', ('-+us1', '--us2', '+-us3')))
        
        FLAG_STR_OPTIONS = (
            # (name, args, kwargs)
            ('full', (), {}, '-/+|test1, */*/*|test2, test_set(*/+/+|ts1, */-/-|ts2, */-/-|ts3), test_set_2(-/+|us1, -/-|us2, +/-|us3)'),
            ('only_current', (), {'show_default': False}, '+|test1, *|test2, test_set(+|ts1, -|ts2, -|ts3), test_set_2(+|us1, -|us2, -|us3)'),
            ('only_default', (), {'show_state': False}, 'test1, test2, test_set(ts1, ts2, ts3), test_set_2(us1, us2, us3)'),
            ('not_pretty', (), {'pretty': False}, '-+|test1, ***|test2, test_set(*++|ts1, *--|ts2, *--|ts3), test_set_2(-+|us1, --|us2, +-|us3)'),
            ('no_sets', (), {'inc_sets': False}, '-/+|test1, */*/*|test2'),
            ('flat', (), {'flat': True}, '-/+|test1, */*/*|test2, */+/+|ts1, */-/-|ts2, */-/-|ts3, -/+|us1, -/-|us2, +/-|us3'),
            ('no_names', (), {'show_name': False}, '-/+|test1, */*/*|test2, (*/+/+|ts1, */-/-|ts2, */-/-|ts3), (-/+|us1, -/-|us2, +/-|us3)'),
            ('filter_true', (), {'filter_for': True}, '-/+|test1, test_set(*/+/+|ts1), test_set_2(-/+|us1)'),
            ('filter_false', (), {'filter_for': False}, 'test_set(*/-/-|ts2, */-/-|ts3), test_set_2(-/-|us2, +/-|us3)'),
            ('filter_none', (), {'filter_for': None}, '*/*/*|test2'),
            ('filter_TF', (), {'filter_for': (True, False)}, '-/+|test1, test_set(*/+/+|ts1, */-/-|ts2, */-/-|ts3), test_set_2(-/+|us1, -/-|us2, +/-|us3)'),
            ('field_list', ('test1', 'test2'), {}, '-/+|test1, */*/*|test2'),
            ('field_list_w_set_name', ('test1', 'test_set'), {}, '-/+|test1, test_set(*/+/+|ts1, */-/-|ts2, */-/-|ts3)'),
            ('field_list_w_set_field_name', ('test1', 'ts1', 'us3'), {}, '-/+|test1, test_set(*/+/+|ts1), test_set_2(+/-|us3)'))
        
        for test in FLAG_STR_OPTIONS:
            with self.subTest(test[0]):
                tmp_ret = fm._str(*test[1], **test[2])
                tmp_msg = '\n\nReturned: %r\nExpected: %r\n\n' % (tmp_ret, test[3])

                self.assertEqual(tmp_ret, test[3], tmp_msg)


class TestFlagManagerDicts(TestCase):
    def test_strings(self):
        fm = FlagHelper('-test1+', '*test2', ['test_set', ('*-', '+ts1', '-ts2', '-ts3')])

        FLAG_DICT_OPTIONS = (
            # (name, args, kwargs)
            ('full', (), {}, {'test1': True, 'test2': None, 'test_set': {'ts1': True, 'ts2': False, 'ts3': False}}),
            ('no_sets', (), {'inc_sets': False}, {'test1':True, 'test2': None}),
            ('flat', (), {'flat': True}, {'test1': True, 'test2': None, 'ts1': True, 'ts2': False, 'ts3': False}),
            ('filter_true', (), {'filter_for': True}, {'test1': True, 'test_set': {'ts1': True}}),
            ('filter_false', (), {'filter_for': False}, {'test_set': {'ts2': False, 'ts3': False}}),
            ('filter_none', (), {'filter_for': None}, {'test2': None}),
            ('filter_TF', (), {'filter_for': (True, False)}, {'test1': True, 'test_set': {'ts1': True, 'ts2': False, 'ts3': False}}),
            ('field_list', ('test1', 'test2'), {}, {'test1': True, 'test2': None}),
            ('field_list_w_set_name', ('test1', 'test_set'), {}, {'test1': True, 'test_set': {'ts1': True, 'ts2': False, 'ts3': False}}),
            ('field_list_w_set_field_name', ('test1', 'ts1'), {}, {'test1': True, 'test_set': {'ts1': True}})
        )

        for test in FLAG_DICT_OPTIONS:
            with self.subTest(test[0]):
                tmp_ret = fm._get_dict(*test[1], **test[2])
                tmp_msg = '\n\nReturned: %r\nExpected: %r\n\n' % (tmp_ret, test[3])

                self.assertDictEqual(tmp_ret, test[3], tmp_msg)
