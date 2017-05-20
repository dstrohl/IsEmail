from unittest import TestCase

from helpers.flag_manager.flag_helper import FlagHelper


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

    def test_rem_item_dict(self):
        fm = FlagHelper('+test', '+test2')
        fm -= {'test': False}
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
        fm += ('+test1', '+test2', '-test3')
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
        self.assertFalse(fm)

        fm._clear()
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
        self.assertEqual(str(fm), '(-)test1, (-)test2, (-)test3')

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
        fm = FlagHelper('+test1', '+test2', '-test3', lock_fields=True)
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test3)

    def test_add_item(self):
        fm = FlagHelper('-test1', '+test2', '-test3', lock_fields=True)
        fm['test1'] = True
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test3)

    def test_add_item_obj_raises(self):
        fm = FlagHelper('+test1', '+test2', lock_fields=True)
        fm2 = FlagHelper('-test2', '+test3', lock_fields=True)
        with self.assertRaises(AttributeError):
            fm += fm2

    def test_add_item_obj(self):
        fm = FlagHelper('-test1', '-test2', lock_fields=True)
        fm2 = FlagHelper('+test1', lock_fields=True)
        fm += fm2
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)

    def test_add_item_invalid(self):
        with self.assertRaises(AttributeError):
            fm = FlagHelper('-thjis is a test1', '+test2', '-test3', lock_fields=True)
        with self.assertRaises(AttributeError):
            fm = FlagHelper('-_foobar', '+test2', '-test3', lock_fields=True)

    def test_rem_item(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_fields=True)
        self.assertTrue(fm.test1)
        fm('-test1')
        self.assertFalse(fm.test1)
        self.assertFalse(fm.test3)

        with self.assertRaises(AttributeError):
            fm['test5'] = True

    def test_rem_item_obj(self):
        fm = FlagHelper('+test', '+test2', lock_fields=True)
        fm2 = FlagHelper('+test', '-test2', lock_fields=True)
        with self.assertRaises(AttributeError):
            fm -= fm2
        self.assertFalse(fm.test)
        self.assertFalse(fm.test2)

    def test_rem_item_dict(self):
        fm = FlagHelper('+test', '+test2', lock_fields=True)
        with self.assertRaises(AttributeError):
            fm -= {'test': False}
        self.assertFalse(fm.test)
        self.assertTrue(fm.test2)

    def test_add_on_init(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_fields=True)
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        with self.assertRaises(AttributeError):
            exp = fm.test4

    def test_rem_by_method(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_fields=True)
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)

        fm.test2 = False
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)

    def test_add_by_iadd(self):
        fm = FlagHelper(test1=True, test2=True, test3=False, lock_fields=True)
        self.assertFalse(fm.test3)
        fm.test3 = True
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test3, repr(fm))

    def test_rem_by_isub(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_fields=True)
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)

        fm(test2=False)
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)

    def test_add_mult_by_iadd(self):
        fm = FlagHelper('-test1', '-test2', '-test3', lock_fields=True)
        fm += ('test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)

        fm -= ('test1', '-test2', '+test3')
        self.assertFalse(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)

    def test_contains(self):
        fm = FlagHelper('-test1', '-test2', '-test3', lock_fields=True)
        self.assertFalse(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)
        with self.assertRaises(AttributeError):
            self.assertFalse(fm.test4)

        fm('test1')

        tmp_test = 'test1' in fm
        self.assertTrue(tmp_test)

        tmp_test = 'test3' in fm
        self.assertFalse(tmp_test)

        tmp_test = 'test5' in fm
        self.assertFalse(tmp_test)

    def test_iterate(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_fields=True)
        tmp_lst = list(fm)

        self.assertCountEqual(tmp_lst, ['test1', 'test2', 'test3'])

    def test_clear(self):
        fm = FlagHelper('+test1', '+test2', '+test3', lock_fields=True)
        self.assertEqual(len(fm), 3)
        self.assertTrue(fm)
        fm.test1 = False
        self.assertFalse(fm['test1'])
        self.assertFalse(fm)
        fm._clear()
        self.assertTrue(fm)
        self.assertTrue(fm.test1)
        self.assertEqual(len(fm), 3)

    def test_get(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_fields=True)
        tmp_lst = list(fm)
        self.assertCountEqual(tmp_lst, ['test1', 'test2', 'test3'])

        tmp_lst = list(fm)
        self.assertCountEqual(tmp_lst, ['test1', 'test3'])

        tmp_lst = fm._get(filter_for=False)
        self.assertCountEqual(tmp_lst, ['test2'])

    def test_get_dict(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_fields=True)
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_get_dict_true(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_fields=True)
        tmp_lst = fm._get_dict(filter_for=True)
        tmp_exp = {'test1': True, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_get_dict_false(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_fields=True)
        tmp_lst = fm._get_dict(filter_for=False)
        tmp_exp = {'test2': False}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_copy(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_fields=True)
        fm('-test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        fm2 = fm.__copy__()
        tmp_lst = fm2._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        self.assertEqual(fm, fm2)

        with self.assertRaises(AttributeError):
            fm2 -= 'test1'
        self.assertTrue(fm.test1)
        self.assertFalse(fm2.test1)

        self.assertNotEqual(fm, fm2)

    def test_copy_default(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_fields=True)
        fm('-test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        fm2 = fm.__copy__()
        tmp_lst = fm2._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

        fm2 -= 'test1'
        self.assertTrue(fm.test1)
        self.assertFalse(fm2.test1)

        self.assertNotEquals(fm, fm2)

    def test_copy_true(self):
        fm = FlagHelper('+test1', 'test2', '+test3', lock_fields=True)
        fm('-test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        fm2 = fm.__copy__()
        tmp_lst = fm2._get_dict()
        tmp_exp = {'test1': True, 'test2': True, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

        fm2 -= 'test1'
        self.assertTrue(fm.test1)
        self.assertFalse(fm2.test1)

        self.assertNotEquals(fm, fm2)

    def test_copy_false(self):
        fm = FlagHelper('+test1', 'test2', '+test3', lock_fields=True)
        fm('-test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        fm2 = fm.__copy__()
        tmp_lst = fm2._get_dict()
        tmp_exp = {'test1': False, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        fm2 -= 'test1'
        self.assertTrue(fm.test1)
        self.assertFalse(fm2.test1)

        self.assertNotEquals(fm, fm2)

    def test_reset_default(self):
        fm = FlagHelper('+test1', 'test2', '+test3', lock_fields=True)
        fm('-test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        fm._clear()
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_reset_true(self):
        fm = FlagHelper('+test1', 'test2', '+test3', lock_fields=True)
        fm('-test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': False}
        self.assertEqual(tmp_lst, tmp_exp)

        fm._clear()
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': True, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_call(self):
        fm = FlagHelper('+test1', '+test2', '-test3', lock_fields=True)
        fm('-test2', 'test3')
        self.assertCountEqual(list(fm), ['test1', 'test3'])

    def test_str(self):
        fm = FlagHelper('+test1', '-test2', '+test3', lock_fields=True)
        self.assertEqual(str(fm), '(+)test1, (-)test2, (+)test3')

    def test_and_1(self):
        fm1 = FlagHelper('-test1', '+test2', '+test3', lock_fields=True)
        fm2 = FlagHelper('+test3', '+test4', '-test5', lock_fields=True)

        fm = fm1 & fm2

        exp_ret = ['test3']
        self.assertCountEqual(fm._get_str(with_icons=True), exp_ret)

    def test_and_2(self):
        fm1 = FlagHelper('+test1', '+test2', '+test3', lock_fields=True)
        fm2 = FlagHelper('+test1', '+test2', '-test3', lock_fields=True)

        fm = fm1 & fm2

        exp_ret = ['test1', 'test2']
        self.assertCountEqual(fm._get_str(with_icons=True), exp_ret)

    def test_or_1(self):
        fm1 = FlagHelper('-test1', '+test2', '-test3', lock_fields=True)
        fm2 = FlagHelper('-test3', '+test4', '+test5', lock_fields=True)

        fm = fm1 | fm2
        exp_ret = ['test2']
        self.assertCountEqual(fm._get_str(with_icons=True), exp_ret)

    def test_or_2(self):
        fm1 = FlagHelper('+test1', '+test2', '+test3', lock_fields=True)
        fm2 = FlagHelper('+test1', '+test2', '-test3', lock_fields=True)

        fm = fm1 | fm2
        exp_ret = ['test1', 'test2', 'test3']
        self.assertCountEqual(fm._get_str(with_icons=True), exp_ret)

    def test_and_3(self):
        fm1 = FlagHelper('-test1', '+test2', '+test3', lock_fields=True)
        fm2 = FlagHelper('+test3', '+test4', '-test5')

        fm = fm1 | fm2

        exp_ret = ['test3']
        self.assertCountEqual(fm._get_str(with_icons=True), exp_ret)

    def test_and_4(self):
        fm1 = FlagHelper('+test1', '+test2', '+test3', lock_fields=True)
        fm2 = FlagHelper('+test1', '+test2', '-test3')

        fm = fm2 | fm1

        exp_ret = ['test1', 'test2']
        self.assertCountEqual(fm._get_str(with_icons=True), exp_ret)

    def test_or_3(self):
        fm1 = FlagHelper('+test1', '+test2', '-test3', lock_fields=True)
        fm2 = FlagHelper('+test1', '+test4', '-test3')

        fm = fm1 | fm2
        exp_ret = ['test1', 'test2']
        self.assertCountEqual(fm._get_str(with_icons=True), exp_ret)

    def test_or_4(self):

        fm1 = FlagHelper('+test1', '+test4', '-test3', lock_fields=True)
        fm2 = FlagHelper('+test3', '+test4', '+test5')

        fm = fm2 | fm1
        exp_ret = ['test1', 'test3', 'test4', 'test5']
        self.assertCountEqual(fm._get_str(with_icons=True), exp_ret)
