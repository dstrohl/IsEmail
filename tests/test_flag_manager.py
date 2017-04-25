from unittest import TestCase
from flag_manager import FlagManager, LockedFlagManager


class TestOpenFlagManager(TestCase):
    maxDiff = None

    def test_init(self):
        fm = FlagManager()
        fm.test = True
        self.assertTrue(fm.test)
        self.assertFalse(fm.test3)

    def test_add_item(self):
        fm = FlagManager()
        fm['test'] = True
        self.assertTrue(fm.test)
        self.assertFalse(fm.test3)

    def test_rem_item(self):
        fm = FlagManager('test')
        self.assertTrue(fm.test)
        fm['test'] = False
        self.assertFalse(fm.test)
        self.assertFalse(fm.test3)


    def test_add_on_init(self):
        fm = FlagManager('test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

    def test_rem_by_method(self):
        fm = FlagManager('test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

        fm.test2 = False
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

    def test_add_by_iadd(self):
        fm = FlagManager()
        fm += 'test'
        self.assertTrue(fm.test)
        self.assertFalse(fm.test3)

    def test_rem_by_isub(self):
        fm = FlagManager('test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

        fm -= 'test2'
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

    def test_add_mult_by_iadd(self):
        fm = FlagManager()
        fm += ('+test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

        fm -= ('test1', '-test2', '+test3')
        self.assertFalse(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

    def test_contains(self):
        fm = FlagManager()
        fm += ('+test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        self.assertFalse(fm.test4)

        tmp_test = 'test1' in fm
        self.assertTrue(tmp_test)

        tmp_test = 'test3' in fm
        self.assertFalse(tmp_test)

    def test_iterate(self):
        fm = FlagManager('test1', 'test2', 'test3')
        tmp_lst = list(fm)

        self.assertCountEqual(tmp_lst, ['test1', 'test2', 'test3'])

    def test_clear(self):
        fm = FlagManager('test1', 'test2', 'test3')
        self.assertEqual(len(fm), 3)
        self.assertTrue(fm)
        fm._clear()
        self.assertEqual(len(fm), 0)
        self.assertFalse(fm)

    def test_get(self):
        fm = FlagManager()
        fm('test1', 'test2', 'test3')
        tmp_lst = fm._get()

        self.assertCountEqual(tmp_lst, ['test1', 'test2', 'test3'])

    def test_get_dict(self):
        fm = FlagManager('test1', 'test2', 'test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': True, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_copy(self):
        fm = FlagManager('test1', 'test2', 'test3')
        tmp_lst = fm._get()
        tmp_exp = ['test1', 'test2', 'test3']
        self.assertCountEqual(tmp_lst, tmp_exp)

        fm2 = fm.__copy__()
        tmp_lst = fm._get()
        tmp_exp = ['test1', 'test2', 'test3']
        self.assertCountEqual(tmp_lst, tmp_exp)

        fm2 -= 'test1'
        self.assertTrue(fm.test1)
        self.assertFalse(fm2.test1)

    def test_call(self):
        fm = FlagManager()
        tmp_list = fm('test1', 'test2', 'test3')
        self.assertCountEqual(tmp_list, ['test1', 'test2', 'test3'])

    def test_str(self):
        fm = FlagManager()
        fm('test1', 'test2', 'test3')
        self.assertEqual(str(fm), 'test1, test2, test3')

    def test_and(self):
        fm1 = FlagManager('test1', 'test2', 'test3')
        fm2 = FlagManager('test3', 'test4', 'test5')

        fm = fm1._and(fm2)

        exp_ret = ['test3']
        self.assertCountEqual(list(fm), exp_ret)

    def test_or(self):
        fm1 = FlagManager('test1', 'test2', 'test3')
        fm2 = FlagManager('test3', 'test4', 'test5')

        fm = fm1._or(fm2)
        exp_ret = ['test1', 'test2', 'test3', 'test4', 'test5']
        self.assertCountEqual(list(fm), exp_ret)


class TestLockedFlagManager(TestCase):


    def test_init(self):
        fm = LockedFlagManager('test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test3)

    def test_add_item(self):
        fm = LockedFlagManager('-test1', 'test2', '-test3')
        fm['test1'] = True
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test3)

    def test_rem_item(self):
        fm = LockedFlagManager('test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        fm['test1'] = False
        self.assertFalse(fm.test1)
        self.assertFalse(fm.test3)

        with self.assertRaises(KeyError):
            fm['test5'] = True

    def test_add_on_init(self):
        fm = LockedFlagManager('test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)
        with self.assertRaises(AttributeError):
            exp = fm.test4

    def test_rem_by_method(self):
        fm = LockedFlagManager('test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)

        fm.test2 = False
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)

    def test_add_by_iadd(self):
        fm = LockedFlagManager(test1=True, test2=True, test3=False)
        self.assertFalse(fm.test3)
        fm += 'test3'
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test3)

    def test_rem_by_isub(self):
        fm = LockedFlagManager('test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)

        fm -= 'test2'
        self.assertTrue(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)

    def test_add_mult_by_iadd(self):
        fm = LockedFlagManager('-test1', '-test2', '-test3')
        fm += ('test1', 'test2', '-test3')
        self.assertTrue(fm.test1)
        self.assertTrue(fm.test2)
        self.assertFalse(fm.test3)

        fm -= ('test1', '-test2', '+test3')
        self.assertFalse(fm.test1)
        self.assertFalse(fm.test2)
        self.assertFalse(fm.test3)

    def test_contains(self):
        fm = LockedFlagManager('-test1', '-test2', '-test3')
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
        fm = LockedFlagManager('test1', 'test2', '-test3')
        tmp_lst = list(fm)

        self.assertCountEqual(tmp_lst, ['test1', 'test2'])

    def test_clear(self):
        fm = LockedFlagManager('test1', 'test2', 'test3')
        self.assertEqual(len(fm), 3)
        self.assertTrue(fm)
        fm.test1 = False
        self.assertFalse(fm)
        self.assertFalse(fm.test1)
        fm._clear()
        self.assertTrue(fm)
        self.assertTrue(fm.test1)
        self.assertEqual(len(fm), 3)

    def test_get(self):
        fm = LockedFlagManager('test1', '-test2', 'test3')
        tmp_lst = fm._get()
        self.assertCountEqual(tmp_lst, ['test1', 'test2', 'test3'])

        tmp_lst = fm._get(filter_for=True)
        self.assertCountEqual(tmp_lst, ['test1', 'test3'])

        tmp_lst = fm._get(filter_for=False)
        self.assertCountEqual(tmp_lst, ['test2'])


    def test_get_dict(self):
        fm = LockedFlagManager('test1', '-test2', 'test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

    def test_copy(self):
        fm = LockedFlagManager('test1', '-test2', 'test3')
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

        fm2 = fm.__copy__()
        tmp_lst = fm._get_dict()
        tmp_exp = {'test1': True, 'test2': False, 'test3': True}
        self.assertEqual(tmp_lst, tmp_exp)

        fm2 -= 'test1'
        self.assertTrue(fm.test1)
        self.assertFalse(fm2.test1)

    def test_call(self):
        fm = LockedFlagManager('test1', 'test2', '-test3')
        tmp_list = fm('-test2', 'test3')
        self.assertCountEqual(tmp_list, ['test1', 'test3'])

    def test_str(self):
        fm = LockedFlagManager('test1', '-test2', 'test3')
        self.assertEqual(str(fm), '(+)test1, (-)test2, (+)test3')

    def test_and_1(self):
        fm1 = LockedFlagManager('-test1', 'test2', 'test3')
        fm2 = LockedFlagManager('test3', 'test4', '-test5')

        fm = fm1._and(fm2)

        exp_ret = []
        self.assertCountEqual(list(fm), exp_ret)

    def test_and_2(self):
        fm1 = LockedFlagManager('test1', 'test2', 'test3')
        fm2 = LockedFlagManager('test1', 'test2', '-test3')

        fm = fm1._and(fm2)

        exp_ret = ['test1', 'test2']
        self.assertCountEqual(list(fm), exp_ret)

    def test_or_1(self):
        fm1 = LockedFlagManager('test1', 'test2', '-test3')
        fm2 = LockedFlagManager('test3', 'test4', 'test5')

        fm = fm1._or(fm2)
        exp_ret = ['test3']
        self.assertCountEqual(list(fm), exp_ret)

    def test_or_2(self):
        fm1 = LockedFlagManager('test1', 'test2', 'test3')
        fm2 = LockedFlagManager('test1', 'test2', '-test3')

        fm = fm1._or(fm2)
        exp_ret = ['test1', 'test2', 'test3']
        self.assertCountEqual(list(fm), exp_ret)


    def test_and_3(self):
        fm1 = LockedFlagManager('-test1', 'test2', 'test3')
        fm2 = FlagManager('test3', 'test4', '-test5')

        fm = fm1._and(fm2)

        exp_ret = ['test3']
        self.assertCountEqual(list(fm), exp_ret)

    def test_and_4(self):
        fm1 = LockedFlagManager('test1', 'test2', 'test3')
        fm2 = FlagManager('test1', 'test2', '-test3')

        fm = fm2._and(fm1)

        exp_ret = ['test1', 'test2']
        self.assertCountEqual(list(fm), exp_ret)

    def test_or_3(self):
        fm1 = LockedFlagManager('test1', 'test2', 'test3')
        fm2 = FlagManager('test1', 'test4', '-test3')

        fm = fm1._or(fm2)
        exp_ret = ['test1', 'test3']
        self.assertCountEqual(list(fm), exp_ret)

    def test_or_4(self):

        fm1 = LockedFlagManager('test1', 'test4', '-test3')
        fm2 = FlagManager('test3', 'test4', 'test5')

        fm = fm2._or(fm1)
        exp_ret = ['test1', 'test3', 'test4', 'test5']
        self.assertCountEqual(list(fm), exp_ret)

