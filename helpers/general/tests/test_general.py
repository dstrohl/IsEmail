import unittest
from helpers.general.general import make_char_str, adv_getattr


class TF2(object):
    test = 'tf2_test'
    tl = ['tf2_1', 'tf2_2', 'tf2_3']

    def __eq__(self, other):
        return self.test == other.test

class TF1(object):
    test = 'tf1_test'
    t2 = TF2()
    tl = ['tf1_1', 'tf1_2', TF2()]

    def __eq__(self, other):
        return self.test == other.test

tf1 = TF1()


class TestAdvGetAttr(unittest.TestCase):

    def test_adv_get_attr(self):
        TESTS = [
            (1, 'string', '[2]', 'r'),
            (2, tf1, 'test', 'tf1_test'),
            (3, tf1, 't2', TF2),
            (4, tf1, 't2.test', 'tf2_test'),
            (5, tf1, 'test[2]', '1'),
            (6, tf1, 'tl[2].test', 'tf2_test'),
            (7, tf1, 't2.tl[0]', 'tf2_1'),
        ]

        for test in TESTS:
            with self.subTest(str(test[0])):
                self.assertEqual(adv_getattr(test[1], test[2]), test[3])


class TestMakeParseString(unittest.TestCase):

    def test_make_string(self):
        tmp_res = make_char_str('foobar')
        self.assertEqual('foobar', tmp_res)

    def test_from_int(self):
        tmp_res = make_char_str(65, 66, 67)
        self.assertEqual('ABC', tmp_res)

    def test_from_string(self):
        tmp_res = make_char_str('ABC', '123')
        self.assertEqual('ABC123', tmp_res)

    def test_from_int_range(self):
        tmp_res = make_char_str((65, 67), (97, 99))
        self.assertEqual('ABCabc', tmp_res)
