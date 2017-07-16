from unittest import TestCase



def make_msg(expected, returned):
    tmp_ret = ['','']
    tmp_ret.append('Expected: %r' % expected)
    tmp_ret.append('Returned: %r' % returned)

    if isinstance(expected, str) and isinstance(returned, str):
        tmp_ret.append('')
        tmp_ret.append('Strings:')
        tmp_ret.append('Expected:\n%s' % expected)
        tmp_ret.append('Returned:\n%s' % returned)

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


def _make_actual_compare_str(l_obj, r_obj):
    try:
        if l_obj == r_obj:
            return 'EQ'
    except TypeError:
        return 'UNCOMPARABLE'
    try:
        if l_obj < r_obj:
            return 'LT'
        else:
            return 'GT'
    except TypeError:
        return 'NE'


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
                    tmp_msg = '\n\n%s:\n%r %s %r\nreturns: %r' % (sub_test_str, l_item, test, r_item, _make_actual_compare_str(l_item, r_item))
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
