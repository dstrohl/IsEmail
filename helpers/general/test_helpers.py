from unittest import TestCase


class TestCaseApproxString(TestCase):
    def assertApproxString(self, returned, begin, end, max_skip=None, min_skip=None, msg=None):
        returned = str(returned)
        begin = str(begin)
        end = str(end)
        len_begin = len(begin)
        len_end = len(end)
        len_exp = len(returned)
        len_skipped = len_exp - len_begin - len_end
        if len_begin + len_end > len_exp:
            tmp_msg = 'overlapping begin and end string'
            if msg:
                tmp_msg += '\n' + str(msg)
            self.fail(tmp_msg)

        # print('Skipped: %r' % returned[len_begin:-len_end])

        if max_skip is not None and len_exp - len_begin - len_end > max_skip:
            tmp_msg = 'Too many skip chars: %r' % returned[len_begin:-len_end]
            if msg:
                tmp_msg += '\n' + str(msg)
            self.fail(tmp_msg)

        if min_skip is not None and len_exp - len_begin - len_end < min_skip:
            tmp_msg = 'Too few skip chars: %r' % returned[len_begin:-len_end]
            if msg:
                tmp_msg += '\n' + str(msg)
            self.fail(tmp_msg)

        has_begin = returned.startswith(begin)
        has_end = returned.endswith(end)

        if not (has_begin and has_end):
            print(str(len_skipped))
            tmp_exp = '%s%s%s' % (begin, ''.ljust(len_skipped, '*'), end)
            tmp_msg = '\n\nExpected: %r\nReturned: %r' % (tmp_exp, returned)
            if msg:
                tmp_msg += '\n\n' + str(msg)
            self.fail(tmp_msg)


def make_msg(expected, returned, header=None, extra_top_lines=1, line_padding=4):
    tmp_ret = []
    line_padding = ''.ljust(line_padding)
    for i in range(extra_top_lines):
        tmp_ret.append('')
    if header is not None:
        tmp_ret.append('%s:' % header)
    tmp_ret.append('%sExpected: %r' % (line_padding, expected))
    tmp_ret.append('%sReturned: %r' % (line_padding, returned))

    if isinstance(expected, str) and isinstance(returned, str) and max(len(expected), len(returned)) >60:
        tmp_ret.append('%s--------' % line_padding)
        tmp_ret.append('%sExpected:\n%s%s' % (line_padding, line_padding, expected))
        tmp_ret.append('%sReturned:\n%s%s' % (line_padding, line_padding, returned))

    return '\n'.join(tmp_ret)

def _compare_(l_obj, r_obj, comp_str):
    if comp_str == '==':
        return l_obj == r_obj
    elif comp_str == '!=':
        return l_obj != r_obj
    elif comp_str == '>':
        return l_obj > r_obj
    elif comp_str == '<':
        return l_obj < r_obj
    elif comp_str == '>=':
        return l_obj >= r_obj
    elif comp_str == '<=':
        return l_obj <= r_obj


def _make_actual_compare_str(l_key, l_value, l_obj, r_key, r_value, r_obj):
    tmp_ret = 'UNKNOWN'
    try:
        if l_obj == r_obj:
            tmp_ret = 'EQ'
    except TypeError:
        tmp_ret = 'UNCOMPARABLE'
    try:
        if l_obj < r_obj:
            tmp_ret = 'LT'
        else:
            tmp_ret = 'GT'
    except TypeError:
        tmp_ret = 'NE'

    return '%s (%r) %s %s (%r)' % (l_key, l_value, tmp_ret, r_key, r_value)


def _fix_limit_str(l_key, r_key, comp_str, limit_str):
    if limit_str is None:
        return None
    if '.' in limit_str:
        limit_str = limit_str.replace('.', comp_str)
    if '*' == limit_str[0]:
        limit_str = limit_str.replace('*', l_key, 1)
    if '*' == limit_str[-1]:
        limit_str = limit_str.replace('*', r_key)
    limit_str = limit_str.replace(' ', '')
    return limit_str


class TestCaseCompare(TestCase):

    def assertComparisons(self, compare_table, limit=None, sub_test_key=None, msg=None, check_none=False, tests=None):
        """
        :param compare_table: table of
            (item_key, compare_item, compare_value),
        :param limit: item key to limit the test to (or None to not limit it)
        :param sub_test_key: string to put before the sub-test names
        :param msg: additional message to add to the end of each item
        :param check_none:
            set to True if item should be compared with None (will only use "==" and "!=")
            set to False will skip comparisons if either item is None
        :param tests: list containing the comparisons to run.
        :return:
        """
        if tests is None:
            tests = ['==', '!=', '>', '>=', '<', '<=']

        none_tests = []
        if check_none:
            if '==' in tests:
                none_tests.append('==')
            if '!=' in tests:
                none_tests.append('!=')

        if limit is not None:
            with self.subTest('LIMITED TEST'):
                self.fail()

        for l_key, l_item, l_value in compare_table:
            for r_key, r_item, r_value in compare_table:
                l_key = str(l_key)
                r_key = str(r_key)

                if check_none and (r_item is None or l_item is None):
                    tmp_tests = none_tests
                else:
                    tmp_tests = tests

                for test in tmp_tests:
                    tmp_limit = _fix_limit_str(l_key, r_key, test, limit)

                    if tmp_limit is not None and tmp_limit != '%s%s%s' % (l_key, test, r_key):
                        continue

                    if sub_test_key:
                        sub_test_str = '%s: %s %s %s' % (sub_test_key, l_key, test, r_key)
                    else:
                        sub_test_str = '%s %s %s' % (l_key, test, r_key)

                    tmp_exp = _compare_(l_value, r_value, test)
                    tmp_ret = _compare_(l_item, r_item, test)
                    tmp_msg = '\n\n%s:\n%r %s %r\nactual: %r' % (sub_test_str, l_item, test, r_item,
                                                                 _make_actual_compare_str(l_key, l_value, l_item,
                                                                                          r_key, r_value, r_item))
                    if msg:
                        tmp_msg += '\n' + msg

                    with self.subTest(sub_test_str):
                        self.assertEqual(tmp_exp, tmp_ret, tmp_msg)
                        

EXAMPLE_PARAM_DICT = [
    {'name': 'name_1', 'options': [True, False], 'default': True},
    {'name': 'name_2', 'options': [1, 2, 3], 'default': 3},
    {'name': 'name_3', 'options': ['1', '2', '3'], 'default': '1'},
]

"""
{'name_1': True, 'name_2': 1, 'name_3: '1'}
{'name_1': True, 'name_2': 1, 'name_3: '2'}
{'name_1': True, 'name_2': 1, 'name_3: '3'}

{'name_1': True, 'name_2': 2, 'name_3: '1'}
{'name_1': True, 'name_2': 2, 'name_3: '2'}
{'name_1': True, 'name_2': 2, 'name_3: '3'}

{'name_1': True, 'name_2': 3, 'name_3: '1'}
{'name_1': True, 'name_2': 3, 'name_3: '2'}
{'name_1': True, 'name_2': 3, 'name_3: '3'}

{'name_1': False, 'name_2': 1, 'name_3: '1'}
{'name_1': False, 'name_2': 1, 'name_3: '2'}
{'name_1': False, 'name_2': 1, 'name_3: '3'}

{'name_1': False, 'name_2': 2, 'name_3: '1'}
{'name_1': False, 'name_2': 2, 'name_3: '2'}
{'name_1': False, 'name_2': 2, 'name_3: '3'}

{'name_1': False, 'name_2': 3, 'name_3: '1'}
{'name_1': False, 'name_2': 3, 'name_3: '2'}
{'name_1': False, 'name_2': 3, 'name_3: '3'}


"""


EXAMPLE_PARAMETER_FORMAT = '(1, %r, True, True),'


def make_param_matrix(param_list_in, format_str=None, depth=0):
    ret_list = []

    if depth < len(param_list_in) -1:
        sub_list = make_param_matrix(param_list_in, format_str=None, depth=depth + 1)
    else:
        sub_list = []

    cur_param = param_list_in[depth]
    for opt in cur_param['options']:
        if 'default' in cur_param and opt == cur_param['default']:
            tmp_dict = {}
        else:
            tmp_dict = {cur_param['name']: opt}
        if sub_list:
            for sub_opt in sub_list:
                tmp_dict_2 = tmp_dict.copy()
                tmp_dict_2.update(sub_opt)
                ret_list.append(tmp_dict_2)
        else:
            ret_list.append(tmp_dict)

    if depth == 0:

        format_str = format_str or '%r'
        for index in range(len(ret_list)):
            ret_list[index] = format_str % ret_list[index]
        ret_list = ''.join(ret_list)

    return ret_list
