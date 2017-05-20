import unittest
from helpers.hisatory.history_helper import HistoryHelper


class TestHistory(unittest.TestCase):

    FS = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def get_simple_history(self):
        hd = HistoryHelper('test_in', begin=0, length=1, from_string=self.FS)
        return hd

    def get_long_history(self, with_top=True):
        """
        test_1 = abcdefghijklmnopqrstuvwxyz
            test_1_1 = abcdefghijkl
                <mt> = abcdefghi
                    test_1_1_1_1 = abc
                    test_1_1_1_2 = def
                    test_1_1_1_3 = ghi
                test_1_1_2 = jkl
                    <mt> = j
                    test_1_1_2_2 = k
                    test_1_1_2_3 = l
            test_1_2 = mnop
            test_1_3 = qrstuvwxyz
                test_1_3_1 = qrstuv
                    test_1_3_1_1 = qr
                    test_1_3_1_2 = st
                    test_1_3_1_3 = uv
                <mt> = wxyz
        """

        if with_top:
            top_str = 'test_1'
        else:
            top_str = ''

        test_1_1_1_1 = HistoryHelper('test_1_1_1_1', begin=0, length=3)
        test_1_1_1_2 = HistoryHelper('test_1_1_1_2', begin=3, length=3)
        test_1_1_1_3 = HistoryHelper('test_1_1_1_3', begin=6, length=3)

        test_1_1_1 = HistoryHelper('', begin=0, length=9)
        test_1_1_1.extend((test_1_1_1_1, test_1_1_1_2, test_1_1_1_3))

        test_1_1_2_1 = HistoryHelper('', begin=9, length=1)

        test_1_1_2_2_1_1_1 = HistoryHelper('test_1_1_2_2', begin=10, length=1)

        test_1_1_2_2_1_1 = HistoryHelper('', begin=10, length=1)
        test_1_1_2_2_1_1.append(test_1_1_2_2_1_1_1)

        test_1_1_2_2_1 = HistoryHelper('', begin=10, length=1)
        test_1_1_2_2_1.append(test_1_1_2_2_1_1)

        test_1_1_2_2 = HistoryHelper('', begin=10, length=1)
        test_1_1_2_2.append(test_1_1_2_2_1)

        test_1_1_2_3 = HistoryHelper('test_1_1_2_3', begin=11, length=1)

        test_1_1_2 = HistoryHelper('test_1_1_2', begin=9, length=3)
        test_1_1_2.extend((test_1_1_2_1, test_1_1_2_2, test_1_1_2_3))

        test_1_1 = HistoryHelper('test_1_1', begin=0, length=12)
        test_1_1.append(test_1_1_1)
        test_1_1.append(test_1_1_2)

        test_1_2 = HistoryHelper('test_1_2', begin=12, length=4)

        test_1_3_1_1 = HistoryHelper('test_1_3_1_1', begin=16, length=2)
        test_1_3_1_2 = HistoryHelper('test_1_3_1_2', begin=18, length=2)
        test_1_3_1_3 = HistoryHelper('test_1_3_1_3', begin=20, length=2)

        test_1_3_1 = HistoryHelper('test_1_3_1', begin=16, length=6)
        test_1_3_1.extend((test_1_3_1_1, test_1_3_1_2, test_1_3_1_3))

        test_1_3_2 = HistoryHelper('', begin=21, length=4)

        test_1_3 = HistoryHelper('test_1_3', begin=16, length=10)
        test_1_3.extend((test_1_3_1, test_1_3_2))

        test_1 = HistoryHelper(top_str, begin=0, length=26, from_string=self.FS)
        test_1.extend((test_1_1, test_1_2, test_1_3))

        return test_1

    def test_long_history_string(self):

        TESTS = [
            # (index, depth, inc_str, inc_top, res),

            (101, 1, False, True, "test_1(...)"),
            (102, 1, True, True, "test_1['abcdefghijklmnopqrstuvwxyz'](...)"),

            (151, 1, False, False, "test_1_1(...), test_1_2, test_1_3(...)"),
            (152, 1, True, False, "test_1_1['abcdefghijkl'](...), test_1_2['mnop'], test_1_3['qrstuvwxyz'](...)"),

            (201, 2, False, True, "test_1(test_1_1(...), test_1_2, test_1_3(...))"),
            (202, 2, True, True, "test_1['abcdefghijklmnopqrstuvwxyz'](test_1_1['abcdefghijkl'](...), test_1_2['mnop'], test_1_3['qrstuvwxyz'](...))"),

            (251, 2, False, False, 'test_1_1(test_1_1_1_1, test_1_1_1_2, test_1_1_1_3, test_1_1_2(...)), test_1_2, test_1_3(test_1_3_1(...))'),
            (252, 2, True, False, "test_1_1['abcdefghijkl'](test_1_1_1_1['abc'], test_1_1_1_2['def'], test_1_1_1_3['ghi'], test_1_1_2['jkl'](...)), test_1_2['mnop'], test_1_3['qrstuvwxyz'](test_1_3_1['qrstuv'](...))"),

            (301, 3, False, True, 'test_1(test_1_1(test_1_1_1_1, test_1_1_1_2, test_1_1_1_3, test_1_1_2(...)), test_1_2, test_1_3(test_1_3_1(...)))'),
            (302, 3, True, True, "test_1['abcdefghijklmnopqrstuvwxyz'](test_1_1['abcdefghijkl'](test_1_1_1_1['abc'], test_1_1_1_2['def'], test_1_1_1_3['ghi'], test_1_1_2['jkl'](...)), test_1_2['mnop'], test_1_3['qrstuvwxyz'](test_1_3_1['qrstuv'](...)))"),

            (351, 3, False, False, 'test_1_1(test_1_1_1_1, test_1_1_1_2, test_1_1_1_3, test_1_1_2(test_1_1_2_2, test_1_1_2_3)), test_1_2, test_1_3(test_1_3_1(test_1_3_1_1, test_1_3_1_2, test_1_3_1_3))'),
            (352, 3, True, False, "test_1_1['abcdefghijkl'](test_1_1_1_1['abc'], test_1_1_1_2['def'], test_1_1_1_3['ghi'], test_1_1_2['jkl'](test_1_1_2_2['k'], test_1_1_2_3['l'])), test_1_2['mnop'], test_1_3['qrstuvwxyz'](test_1_3_1['qrstuv'](test_1_3_1_1['qr'], test_1_3_1_2['st'], test_1_3_1_3['uv']))"),

            (901, 9999, False, True,
             "test_1(test_1_1(test_1_1_1_1, test_1_1_1_2, test_1_1_1_3, test_1_1_2(test_1_1_2_2, test_1_1_2_3)), test_1_2, test_1_3(test_1_3_1(test_1_3_1_1, test_1_3_1_2, test_1_3_1_3)))"),
            (902, 9999, True, True,
             "test_1['abcdefghijklmnopqrstuvwxyz'](test_1_1['abcdefghijkl'](test_1_1_1_1['abc'], test_1_1_1_2['def'], test_1_1_1_3['ghi'], test_1_1_2['jkl'](test_1_1_2_2['k'], test_1_1_2_3['l'])), test_1_2['mnop'], test_1_3['qrstuvwxyz'](test_1_3_1['qrstuv'](test_1_3_1_1['qr'], test_1_3_1_2['st'], test_1_3_1_3['uv'])))"),

            (951, 9999, False, False,
             "test_1_1(test_1_1_1_1, test_1_1_1_2, test_1_1_1_3, test_1_1_2(test_1_1_2_2, test_1_1_2_3)), test_1_2, test_1_3(test_1_3_1(test_1_3_1_1, test_1_3_1_2, test_1_3_1_3))"),
            (952, 9999, True, False,
             "test_1_1['abcdefghijkl'](test_1_1_1_1['abc'], test_1_1_1_2['def'], test_1_1_1_3['ghi'], test_1_1_2['jkl'](test_1_1_2_2['k'], test_1_1_2_3['l'])), test_1_2['mnop'], test_1_3['qrstuvwxyz'](test_1_3_1['qrstuv'](test_1_3_1_1['qr'], test_1_3_1_2['st'], test_1_3_1_3['uv']))"),

        ]
        LIMIT = 0
        if LIMIT != 0:
            with self.subTest('LIMITED TEST'):
                self.fail('LIMITED TEST')
        for test in TESTS:
            if LIMIT == 0 or LIMIT == test[0]:
                with self.subTest( '#' +str(test[0])):
                    hd = self.get_long_history(test[3])
                    tmp_exp = test[4]
                    tmp_ret = hd(depth=test[1], with_string=test[2])

                    tmp_msg = '\n\nExpected: %r\nReturned: %r\n' % (tmp_exp, tmp_ret)

                    self.assertEqual(tmp_ret, tmp_exp, msg=tmp_msg)

    def test_sinple_history(self):
        hd = HistoryHelper('test_in')
        self.assertEquals(str(hd), 'test_in')

    def test_simple_history_w_str(self):
        hd = HistoryHelper('test_in', 0, 3, from_string='abcdef')
        self.assertEquals(hd.as_string(from_string='abcdef', with_string=True), "test_in['abc']")

    def test_clear(self):
        hd = self.get_long_history()
        self.assertEqual("test_1(...)", hd(depth=1))
        hd.clear()
        tmp_exp = ''
        tmp_ret = hd()
        self.assertEqual(tmp_ret, tmp_exp)

    def test_iter_all(self):

        TESTS = [
            # (index, is_leaf, name, begin, len)
            (0, False, 'test_1', 0, 26),
            (1, False, 'test_1_1', 0, 12),
            (2, True, 'test_1_1_1_1', 0, 3),
            (3, True, 'test_1_1_1_2', 3, 3) ,
            (4, True, 'test_1_1_1_3', 6, 3),
            (5, False, 'test_1_1_2', 9, 3),
            (6, True, 'test_1_1_2_2', 10, 1),
            (7, True, 'test_1_1_2_3', 11, 1),
            (8, True, 'test_1_2', 12, 4),
            (9, False, 'test_1_3', 16, 10),
            (10, False, 'test_1_3_1', 16, 6),
            (11, True, 'test_1_3_1_1', 16, 2),
            (12, True, 'test_1_3_1_2', 18, 2),
            (13, True, 'test_1_3_1_3', 20, 2),
        ]

        hd = self.get_long_history()
        tmp_count = 0
        for c in hd:
            test = TESTS[tmp_count]
            with self.subTest( '#' +str(test[0] ) +'-leaf'):
                self.assertEqual(test[1], c.is_leaf, msg='\n\nName: %s\n\n' % c.name)
            with self.subTest('#' + str(test[0]) + '-name'):
                self.assertEqual(test[2], c.name, msg='\n\nName: %s\n\n' % c.name)
            with self.subTest('#' + str(test[0]) + '-begin'):
                self.assertEqual(test[3], c.begin, msg='\n\nName: %s\n\n' % c.name)
            with self.subTest('#' + str(test[0]) + '-length'):
                self.assertEqual(test[4], c.length, msg='\n\nName: %s\n\n' % c.name)
            tmp_count += 1
        self.assertEqual(tmp_count, 14)

    def test_len(self):
        hd = self.get_long_history()
        self.assertEqual(14, len(hd))


