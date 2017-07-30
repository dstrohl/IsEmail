from unittest import TestCase
from helpers.general.test_helpers import make_param_matrix, make_msg, TestCaseApproxString


class TestMakeParams(TestCase):
    maxDiff = None
    def test_make_params(self):
        param_list = [
            {'name': 'name_1', 'options': [True, False]},
            {'name': 'name_2', 'options': [1, 2, 3], 'default': 3},
            {'name': 'name_3', 'options': ['1', '2', '3'], 'default': '3'},
        ]

        tmp_resp = "{'name_1': True, 'name_2': 1, 'name_3': '1'},\n" \
                   "{'name_1': True, 'name_2': 1, 'name_3': '2'},\n" \
                   "{'name_1': True, 'name_2': 1},\n" \
                   "{'name_1': True, 'name_2': 2, 'name_3': '1'},\n" \
                   "{'name_1': True, 'name_2': 2, 'name_3': '2'},\n" \
                   "{'name_1': True, 'name_2': 2},\n" \
                   "{'name_1': True, 'name_3': '1'},\n" \
                   "{'name_1': True, 'name_3': '2'},\n" \
                   "{'name_1': True},\n" \
                   "{'name_1': False, 'name_2': 1, 'name_3': '1'},\n" \
                   "{'name_1': False, 'name_2': 1, 'name_3': '2'},\n" \
                   "{'name_1': False, 'name_2': 1},\n" \
                   "{'name_1': False, 'name_2': 2, 'name_3': '1'},\n" \
                   "{'name_1': False, 'name_2': 2, 'name_3': '2'},\n" \
                   "{'name_1': False, 'name_2': 2},\n" \
                   "{'name_1': False, 'name_3': '1'},\n" \
                   "{'name_1': False, 'name_3': '2'},\n" \
                   "{'name_1': False},\n"

        param_format = '%r,\n'

        tmp_ret = make_param_matrix(param_list, param_format)

        tmp_msg = make_msg(expected=tmp_resp, returned=tmp_ret)

        self.assertEqual(tmp_resp, tmp_ret, tmp_msg)

class MakeParams(TestCase):
    maxDiff = None

    def test_make_params(self):
        param_list = [
            {'name': 'begin', 'options': [3]},
            {'name': 'look_for', 'options': ['def', 'd', 'DEF', 'D', '"def"', '"d"']},
            {'name': 'end', 'options': [None, '1', '2', '3'], 'default': None},
            {'name': 'min_count', 'options': [None, '1', '2', '3'], 'default': None},
            {'name': 'max_count', 'options': [None, '1', '2', '3'], 'default': None},
            {'name': 'caps_sensitive', 'options': [True, False], 'default': True},
            {'name': 'until_char', 'options': [None, 'e'], 'default': None},
        ]


        param_format = '%r,\n'

        tmp_ret = make_param_matrix(param_list, param_format)

        # print(tmp_ret)


class TestAppproxString(TestCaseApproxString):
    def test_good_str(self):
        tmp_begin = 'this is'
        tmp_end = 'of the emergency snafu'
        tmp_test = 'this is a test of the emergency snafu'

        self.assertApproxString(tmp_test, tmp_begin, tmp_end, max_skip=10, min_skip=3)

    def test_bad_str(self):
        tmp_begin = 'this is'
        tmp_end = 'of the emergency snafu'
        tmp_test = 'not this is a test of the emergency snafu'

        with self.assertRaises(AssertionError):
            self.assertApproxString(tmp_test, tmp_begin, tmp_end)

    def test_overlap(self):
        tmp_begin = 'this is a test of '
        tmp_end = 'of the emergency snafu'
        tmp_test = 'this is a test of the emergency snafu'

        with self.assertRaises(AssertionError):
            self.assertApproxString(tmp_test, tmp_begin, tmp_end)


    def test_skip_too_long(self):
        tmp_begin = 'this is a test of '
        tmp_end = 'of the emergency snafu'
        tmp_test = 'this is a test of the emergency snafu'

        with self.assertRaises(AssertionError):
            self.assertApproxString(tmp_test, tmp_begin, tmp_end, max_skip=4)

    def test_skip_too_short(self):

        tmp_begin = 'this is a test of '
        tmp_end = 'of the emergency snafu'
        tmp_test = 'this is a test of the emergency snafu'

        with self.assertRaises(AssertionError):
            self.assertApproxString(tmp_test, tmp_begin, tmp_end, min_skip=4)

