from unittest import TestCase, SkipTest
from helpers.general.wildcard_dict import *
from helpers.general import show_compared_items
from helpers.general.test_helpers import TestCaseCompare, make_msg
from copy import deepcopy, copy
from pprint import pformat


def print_results(expected, returned):
    expected = pformat(expected, indent=4)
    returned = pformat(returned, indent=4)
    return '\n\nExpected:\n%s\n\nReturned:\n%s' % (expected, returned)

def parse_key_args(*args, as_key1=True):
    if as_key1:
        tmp_ret = KeyObj(*args, default_key=1)

    else:
        tmp_ret = KeyObj(*args, default_key=2)

    return tmp_ret.key1, tmp_ret.key2, tmp_ret.key_data

class TestParseKeyArgs(TestCaseCompare):

    def test_parse_key_args(self):

        # text_k1 = 'k1'
        # text_k2 = 'k2'
        # text_st = '*'
        text_k1_k2 = 'k1.k2'
        text_k1_st = 'k1.*'
        text_st_k2 = '*.k2'
        text_st_st = '*.*'
        
        text_dot_k2 = '.k2'        
        text_k1_dot = 'k1.'

        # text_x1 = 'x1'
        # text_x2 = 'x2'
        text_x1_x2 = 'x1.x2'

        # dict_k1 = dict(key=text_k1)
        # dict_k2 = dict(key=text_k2)
        # dict_st = dict(key=text_st)
        dict_k1_k2 = dict(key=text_k1_k2)
        dict_k1_st = dict(key=text_k1_st)
        dict_st_k2 = dict(key=text_st_k2)

        dict_x1_x2 = dict(key=text_x1_x2)

        dict_dot_k2 = dict(key=text_dot_k2)
        dict_k1_dot = dict(key=text_k1_dot)

        dict_no_key = dict(foobar=text_k1_k2)        

        ko_k1_k2 = KeyObj(text_k1_k2)
        ko_k1_st = KeyObj(text_k1_st)
        ko_st_k2 = KeyObj(text_st_k2)

        resp_12 = ('k1', 'K2')
        resp_1s = ('k1', '*')
        resp_s2 = ('*', 'K2')
        resp_ss = ('*', '*')

        data_1 = {'field1': 'dd1.1', 'field2': 'dd1.2'}
        data_2 = {'field1': 'dd2.1', 'field3': 'dd2.3'}
        data_3 = {'field1': 'dd3.1', 'field4': 'dd3.4'}
        data_4 = {'field1': 'dd4.1', 'field5': 'dd4.5'}


        raise_error = None

        TESTS = (
            # (index, (arg1, arg2), (key1, key2))
            ### GOOD
            #### 2 params

            # text, text
            # (101, (text_k1, text_k2), resp_12),
            
            # dict, text
            # (102, (dict_k1, text_k2), resp_12),
            
            # dict(k), dict(k)
            # (103, (dict_k1, dict_k2), resp_12),
            
            # ko, ko
            (104, (ko_k1_k2, ko_k1_k2), resp_12),
            
            # none, text
            # (105, (None, text_k2), resp_s2),
            
            # none, text(k.k)
            (106, (None, text_k1_k2), resp_12),
            
            # none, dict(k)
            # (107, (None, dict_k2), resp_s2),
            
            # none, dict(k.k)
            (108, (None, dict_k1_k2), resp_12),
            
            # none, ko
            (109, (None, ko_k1_k2), resp_12),
            
            # *, text
            # (110, (text_st, text_k2), resp_s2),
            
            # *, text(k.k)
            # (111, (text_st, text_k1_k2), resp_12),
            
            # *, dict(k.k)
            # (112, (text_st, dict_k1_k2), resp_12),
            
            # *, ko
            # (113, (text_st, ko_k1_k2), resp_12),
            
            # text, text(.k)
            # (114, (text_k1, text_dot_k2), resp_12),
            
            # text, dict(.k)
            # (115, (text_k1, dict_dot_k2), resp_12),
            
            # text(k.), text
            # (116, (text_k1_dot, text_k2), resp_12),
            
            # dict(k.), text
            # (117, (dict_k1_dot, text_k2), resp_12),
            
            # text, text(*.k)
            # (118, (text_k1, text_dot_k2), resp_12),
            
            # text, dict(*.k)
            # (118, (text_k1, dict_st_k2), resp_12),
            
            # text, ko(*.k)
            # (120, (text_k1, ko_st_k2), resp_12),
            
            # text, *
            # (121, (text_k1, text_st), resp_1s),
            
            # text(k.k), *
            # (122, (text_k1_k2,text_st), resp_12),
            
            # dict(k.k), *
            # (123, (dict_k1_k2, text_st), resp_12),
            
            # ko, *
            # (124, (ko_k1_k2, text_st), resp_12),
            
            # text(k.*), text
            # (125, (text_k1_st, text_k2), resp_12),
            
            # dict(k.*), text
            # (126, (dict_k1_st, text_k2), resp_12),
            
            # ko(k.*), text
            # (127, (ko_k1_st, text_k2), resp_12),
            
            ### one param - as_key_1 = False
            
            # text(k)
            # (200, [text_k2, False], resp_s2),
            
            # text (k.k)
            (201, [text_k1_k2, False], resp_12),
            
            # text (*.k)
            (202, [text_st_k2, False], resp_s2),
            
            # text (k.*)
            (203, [text_k1_st, False], resp_1s),
            
            # dict(*.k)
            (204, [dict_st_k2, False], resp_s2),
            
            # dict(k.*)
            (206, [dict_k1_st, False], resp_1s),
            
            # dict(k)
            # (207, [dict_k2, False], resp_s2),
            
            # dict(k.k)
            (208, [dict_k1_k2, False], resp_12),
            
            # ko
            (209, [ko_k1_k2, False], resp_12),

            # just *
            # (210, [text_st, False], resp_ss),

            ### one param - as key1 = True

            # text(k)
            # (300, [text_k1, True], resp_1s),

            # text (k.k)
            (301, [text_k1_k2, True], resp_12),

            # text (*.k)
            (302, [text_st_k2, True], resp_s2),

            # text (k.*)
            (303, [text_k1_st, True], resp_1s),

            # dict(*.k)
            (304, [dict_st_k2, True], resp_s2),

            # dict(k.*)
            (306, [dict_k1_st, True], resp_1s),

            # dict(k)
            # (307, [dict_k1, True], resp_1s),

            # dict(k.k)
            (308, [dict_k1_k2, True], resp_12),

            # ko
            (309, [ko_k1_k2, True], resp_12),

            # just *
            # (310, [text_st, True], resp_ss),

            ## Data items
            # text_ks, data_1_sk
            (400, [text_k1_st, (data_1, text_st_k2)], resp_12, [data_1]),

            # text_kk, data_1_nk
            (401, [text_k1_k2, data_1], resp_12, [data_1]),

            # data_1_kk, text_ks
            (402, [(data_1, text_k1_k2), text_k1_st], resp_12, [data_1]),

            # data_1_kk, data2
            (403, [(data_1, text_k1_k2), data_2], resp_12, [data_1, data_2]),

            # data_1_sk, data2_ks, data_3
            (404, [(data_1, text_st_k2), (data_2, text_k1_st), data_3], resp_12, [data_1, data_2, data_3]),

            # data_1_sk, data_2_kk, data_3
            (405, [(data_1, text_st_k2), (data_2, text_k1_k2), data_3], resp_12, [data_1, data_2, data_3]),

            # data_1, data_2_kk, _data_3
            (406, [data_1, (data_2, text_k1_k2), data_3], resp_12, [data_1, data_2, data_3]),

            ### BAD

            # no parameters
            (3990, [], resp_ss),

            # three parameters
            # (901, [text_k1, text_k2, text_st], raise_error),

            ## one param

            # dict (no key)
            (902, [dict_no_key], raise_error),

            ## two params

            # text, dict(no key)
            # (903, [text_k1, dict_no_key], raise_error),

            # dict (no key), text
            # (904, [dict_no_key, text_k2], raise_error),

            # dict (with key.key),  diff text
            (905, [dict_k1_k2, text_x1_x2], raise_error),

            # diff text, dict(with key.key)
            # (906, [text_x1, dict_k1_k2], raise_error),

            # dict(with key.key), dict(with key.key)
            (907, [dict_k1_k2, dict_x1_x2], raise_error),

            # ko, diff text
            # (908, [ko_k1_k2, text_x1_x2], raise_error),

            # diff text, ko
            # (909, [text_x1, ko_k1_k2], raise_error),
        )

        LIMIT_TO = None
        # LIMIT_TO = 116

        if LIMIT_TO is not None:
            with self.subTest('LIMITED TEST'):
                self.fail()

        for test in TESTS:
            if len(test) == 3:
                test_key, test_info, response = test
                resp_data = {}
            else:
                test_key, test_info, response, resp_data = test

            if LIMIT_TO is None or LIMIT_TO == test_key:
                with self.subTest(str(test_key)):
                    # if len(test[1]) == 2:
                    #     name = '#%s - (%r, %r)' % (test_key, test[1][0], test[1][1])
                    # elif len(test[1]) == 1:
                    #     name = '#%s - (%r, )' % (test_key, test[1][0])
                    # else:
                    #     name = '#%s - (, )' % test_key
                    test_args = []
                    for arg in test_info:
                        if isinstance(arg, (list, tuple)):
                            tmp_arg = {}
                            for a in arg:
                                if isinstance(a, str):
                                    tmp_arg['key'] = a
                                else:
                                    tmp_arg.update(a)
                            test_args.append(tmp_arg)
                        else:
                            test_args.append(arg)

                    if isinstance(resp_data, (list, tuple)):
                        tmp_resp_data = {}
                        for r in resp_data:
                            try:
                                tmp_resp_data.update(r)
                            except ValueError as err:
                                raise ValueError('%s\nelement = %r from %r from %r' % (err, r, resp_data, response))
                        resp_data = tmp_resp_data
                    if response is None:
                        with self.assertRaises(AttributeError):
                            ret_resp = parse_key_args(*test_args)
                    else:
                        if len(test_args) == 2 and isinstance(test_args[1], bool):
                            ret_resp = parse_key_args(test_args[0], as_key1=test_args[1])
                            self.assertEqual(response, ret_resp[:2])
                            self.assertEqual(resp_data, ret_resp[2])
                        else:
                            ret_resp = parse_key_args(*test_args)
                            self.assertEqual(response, ret_resp[:2])
                            self.assertEqual(resp_data, ret_resp[2])


class TestKeyObj(TestCaseCompare):
    
    def test_ks(self):
        kt = KeyObj('k1.*')
        self.assertEqual(kt.key1, 'k1')
        self.assertEqual(kt.key2, '*')
        self.assertEqual(str(kt), 'k1.*')
        self.assertEqual(repr(kt), 'KeyObj(k1.*)')
        self.assertTrue(kt)
        self.assertTrue(kt.has_key1)
        self.assertFalse(kt.has_key2)
        self.assertFalse(kt.is_exact)
        self.assertFalse(kt.is_any)

    def test_sk(self):
        kt = KeyObj('*.k2')
        self.assertEqual(kt.key1, '*')
        self.assertEqual(kt.key2, 'K2')
        self.assertEqual(str(kt), '*.K2')
        self.assertEqual(repr(kt), 'KeyObj(*.K2)')
        self.assertTrue(kt)
        self.assertFalse(kt.has_key1)
        self.assertTrue(kt.has_key2)
        self.assertFalse(kt.is_exact)
        self.assertFalse(kt.is_any)

    def test_kk(self):
        kt = KeyObj('k1.k2')
        self.assertEqual(kt.key1, 'k1')
        self.assertEqual(kt.key2, 'K2')
        self.assertEqual(str(kt), 'k1.K2')
        self.assertEqual(repr(kt), 'KeyObj(k1.K2)')
        self.assertTrue(kt)
        self.assertTrue(kt.has_key1)
        self.assertTrue(kt.has_key2)
        self.assertTrue(kt.is_exact)
        self.assertFalse(kt.is_any)

    def test_ss(self):
        kt = KeyObj('*.*')
        self.assertEqual(kt.key1, '*')
        self.assertEqual(kt.key2, '*')
        self.assertEqual(str(kt), '*.*')
        self.assertEqual(repr(kt), 'KeyObj(*.*)')
        self.assertFalse(kt)
        self.assertFalse(kt.has_key1)
        self.assertFalse(kt.has_key2)
        self.assertFalse(kt.is_exact)
        self.assertTrue(kt.is_any)

    def test_def1(self):
        kt = KeyObj('*', _key1_default='s1')
        self.assertEqual(str(kt), 's1.*')

        kt = KeyObj('bar', _key1_default='s1')
        self.assertEqual(str(kt), 's1.BAR')

        kt = KeyObj('k1.*', _key1_default='s1')
        self.assertEqual(str(kt), 'k1.*')

        kt = KeyObj('*.k2', _key1_default='s1')
        self.assertEqual(str(kt), '*.K2')

        kt = KeyObj('k1.k2', _key1_default='s1')
        self.assertEqual(str(kt), 'k1.K2')

        kt = KeyObj('*.*', _key1_default='s1')
        self.assertEqual(str(kt), '*.*')

    def test_def2(self):
        kt = KeyObj('*', _key2_default='s1')
        self.assertEqual(str(kt), '*.S1')

        kt = KeyObj('foo', _key2_default='s1')
        self.assertEqual(str(kt), 'foo.S1')

        kt = KeyObj('k1.*', _key2_default='s1')
        self.assertEqual(str(kt), 'k1.*')

        kt = KeyObj('*.k2', _key2_default='s1')
        self.assertEqual(str(kt), '*.K2')

        kt = KeyObj('k1.k2', _key2_default='s1')
        self.assertEqual(str(kt), 'k1.K2')

        kt = KeyObj('*.*', _key2_default='s1')
        self.assertEqual(str(kt), '*.*')


    def test_mt(self):
        kt = KeyObj()
        self.assertEqual(kt.key1, '*')
        self.assertEqual(kt.key2, '*')
        self.assertEqual(str(kt), '*.*')
        self.assertEqual(repr(kt), 'KeyObj(*.*)')
        self.assertFalse(kt)
        self.assertFalse(kt.has_key1)
        self.assertFalse(kt.has_key2)
        self.assertFalse(kt.is_exact)
        self.assertTrue(kt.is_any)

    def test_add(self):
        oNone = KeyObj()
        o1 = KeyObj('k1.*')
        o2 = KeyObj('*.k2')
        o12 = KeyObj('k1.k2') 
        o1x = KeyObj('k1.x2')
        ox2 = KeyObj('x1.k2') 

        kN = '*.*'
        k1 = 'k1.*'
        k2 = '*.K2'
        k12 = 'k1.K2'
        k1x = 'k1.X2'
        kx2 = 'x1.K2'

        TESTS = (
            (10, oNone, oNone, kN),
            (11, oNone, o1, k1),
            (12, oNone, o2, k2),
            (13, oNone, o12, k12),
            (14, oNone, o1x, k1x),
            (15, oNone, ox2, kx2),

            (20, o1, oNone, k1),
            (21, o1, o1, k1),
            (22, o1, o2, k12),
            (23, o1, o12, k12),
            (24, o1, o1x, k1x),
            (25, o1, ox2, None),

            (30, o2, oNone, k2),
            (31, o2, o1, k12),
            (32, o2, o2, k2),
            (33, o2, o12, k12),
            (34, o2, o1x, None),
            (35, o2, ox2, kx2),

            (40, o12, oNone, k12),
            (41, o12, o1, k12),
            (42, o12, o2, k12),
            (43, o12, o12, k12),
            (44, o12, o1x, None),
            (45, o12, ox2, None),

            (50, o1x, oNone, k1x),
            (51, o1x, o1, k1x),
            (52, o1x, o2, None),
            (53, o1x, o12, None),
            (54, o1x, o1x, k1x),
            (55, o1x, ox2, None),

            (60, ox2, oNone, kx2),
            (61, ox2, o1, None),
            (62, ox2, o2, kx2),
            (63, ox2, o12, None),
            (64, ox2, o1x, None),
            (65, ox2, ox2, kx2),
        )

        LIMIT_TO = None
        # LIMIT_TO = 116

        if LIMIT_TO is not None:
            with self.subTest('LIMITED TEST'):
                self.fail()

        for test in TESTS:
            if LIMIT_TO is None or LIMIT_TO == test[0]:
                name = '#%s ( %s + %s )' % (test[0], test[1], test[2])
                exp_ret = test[3]
                with self.subTest(name):
                    if exp_ret is None:
                        with self.assertRaises(AttributeError):
                            test_1 = copy(test[1])
                            test_2 = copy(test[2])
                            ret_resp = test_1 + test_2
                    else:
                        with self.subTest(name + '- plus'):
                            test_1 = copy(test[1])
                            test_2 = copy(test[2])
                            ret_resp = test_1 + test_2
                            self.assertEqual(exp_ret, str(ret_resp), make_msg(expected=exp_ret, returned=str(ret_resp)))
                        with self.subTest(name + '- plus-eq'):
                            test_1 = copy(test[1])
                            test_2 = copy(test[2])
                            test_1 += test_2
                            self.assertEqual(exp_ret, str(test_1), make_msg(expected=exp_ret, returned=str(test_1)))

    def test_compare(self):
        TESTS = (
            # (item_key, compare_item, compare_value)
            (1, KeyObj('a.b'), 3),
            (2, KeyObj('b.a'), 5),
            (3, KeyObj('c.d'), 6),
            (4, KeyObj('b.*'), 4),
            (5, KeyObj('*.a'), 2),
            (6, KeyObj('*.*'), 1),
        )
        self.assertComparisons(TESTS, tests=['>', '<', '>=', '<='])

    def test_compare_eq(self):
        test_objs = dict(
            ab=KeyObj('a.b'),
            bb=KeyObj('b.b'),
            cd=KeyObj('c.d'),
            xs=KeyObj('a.*'),
            sb=KeyObj('*.b'),
            ss=KeyObj('*.*'),
        )
        TESTS = {
            'ab': ['ab', 'xs', 'ss', 'sb'],
            'bb': ['ss', 'sb', 'bb'],
            'cd': ['ss', 'cd'],
            'xs': ['ss', 'ab', 'xs', 'sb'],
            'sb': ['ss', 'ab', 'bb', 'sb', 'xs'],
            'ss': ['ss', 'ab', 'bb', 'cd', 'xs', 'sb'],
        }

        LIMIT_TO = None
        # LIMIT_TO = ('bb', 'sb')

        if LIMIT_TO is not None:
            with self.subTest('LIMITED TEST'):
                self.fail()
        for key_1, ko_1 in test_objs.items():
            for key_2, ko_2 in test_objs.items():
                if LIMIT_TO is None or LIMIT_TO[0] == key_1 and LIMIT_TO[1] == key_2:
                    test_list = TESTS[key_1]
                    if key_2 in test_list:
                        with self.subTest('%s == %s' % (key_1, key_2)):
                            self.assertEqual(ko_1, ko_2)
                    else:
                        with self.subTest('%s != %s' % (key_1, key_2)):
                            self.assertNotEqual(ko_1, ko_2)

    def test_sort(self):
        test_list = [
            KeyObj('a.b'),
            KeyObj('b.a'),
            KeyObj('c.d'),
            KeyObj('b.*'),
            KeyObj('*.a'),
            KeyObj('*.*')]

        exp_ret = ['*.*', '*.A', 'a.B', 'b.*', 'b.A', 'c.D']
        test_list.sort()
        ret_list = list(map(str, test_list))

        self.assertEqual(exp_ret, ret_list)

    def test_keys(self):
        xx = (False, False)
        lx = (True, False)
        xs = (False, True)
        ls = (True, True)

        TESTS = (
            # (item_key, compare_item, compare_value)
            (10, KeyObj('a.B'), ls, ['a.B', '*.B', 'a.*', '*.*']),
            (11, KeyObj('a.B'), lx, ['a.B', '*.*']),
            (12, KeyObj('a.B'), xs, ['a.B', '*.B', 'a.*']),
            (13, KeyObj('a.B'), xx, ['a.B']),

            (20, KeyObj('a.*'), ls, ['a.*', '*.*']),
            (21, KeyObj('a.*'), lx, ['*.*']),
            (22, KeyObj('a.*'), xs, ['a.*']),
            (23, KeyObj('a.*'), xx, []),

            (30, KeyObj('*.B'), ls, ['*.B', '*.*']),
            (31, KeyObj('*.B'), lx, ['*.*']),
            (32, KeyObj('*.B'), xs, ['*.B']),
            (33, KeyObj('*.B'), xx, []),

            (40, KeyObj('*.*'), ls, ['*.*']),
            (41, KeyObj('*.*'), lx, ['*.*']),
            (42, KeyObj('*.*'), xs, []),
            (43, KeyObj('*.*'), xx, []),
        )

        LIMIT_TO = None
        # LIMIT_TO = 10

        if LIMIT_TO is not None:
            with self.subTest('LIMITED TEST'):
                self.fail()
        for test in TESTS:
            if LIMIT_TO is None or LIMIT_TO == test[0]:
                with self.subTest(str(test[0])):
                    tmp_ret = list(test[1].keys(*test[2]))
                    self.assertCountEqual(tmp_ret, test[3])


class WCMTest(WildCardMergeDict):
    fields = (
        ('key1', {'flags': ['key']}),
        'simple_str',
        ('field1', 'ss1'),
        ('field2', 'ss2'),
        ('field3', 'ss3'),
        ('field4', 'ss4'),
        ('field5', 'ss5'),
        ('simple_list', []),
        ('simple_dict', {}),
        ('replace_list', {'add': '_add_default', 'merge': '_merge_default', 'default': [], 'flags': ['deepcopy']}),
        ('locked_str', {'flags': ['locked']}),
        ('comb_str', {'merge': '_merge_combine_string', 'default': ''}),
        ('comb_key_str', {'merge': '_merge_combine_string_by_key', 'default': ''}),
        ('comb_key_str_2', {'merge': '_merge_combine_string_by_key', 'default': 'test_cks'})
    )

WCMTest_base_return = dict(
    field1='ss1',
    field2='ss2',
    field3='ss3',
    field4='ss4',
    field5='ss5',
    simple_list=[],
    simple_dict={},
    replace_list=[],
    comb_str='',
    comb_key_str='',
    comb_key_str_2=''
)


class TestWildcardDictBasic(TestCase):

    def test_lookups(self):
        cd = {'key1': 'c.d', 'field1': 'cd', 'field2': 'cd'}
        sd = {'key1': '*.d', 'field1': 'sd', 'field3': 'sd'}
        cs = {'key1': 'c.*', 'field1': 'cs', 'field4': 'cs'}
        ov = {'field1': 'ov', 'field5': 'ov'}

        TESTS = [
            # (index, req, resp_key, override, data, return_any_data, return_partial_raise, return_full_raise)
            # request c.d
            (101, 'c.d', '*.*', {}, [], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], True, True),

            (121, 'c.d', 'c.d', {}, [cd], ['cd', 'cd', 'ss3', 'ss4', 'ss5'], False, False),
            (122, 'c.d', '*.d', {}, [sd], ['sd', 'ss2', 'sd', 'ss4', 'ss5'], False, True),
            (123, 'c.d', 'c.*', {}, [cs], ['cs', 'ss2', 'ss3', 'cs', 'ss5'], False, True),

            (131, 'c.d', 'c.d', {}, [cd, cs], ['cd', 'cd', 'ss3', 'cs', 'ss5'], False, False),
            (132, 'c.d', 'c.d', {}, [sd, cs], ['cs', 'ss2', 'sd', 'cs', 'ss5'], False, True),
            (133, 'c.d', 'c.d', {}, [sd, cd], ['cd', 'cd', 'sd', 'ss4', 'ss5'], False, False),

            (141, 'c.d', 'c.d', {}, [cd, sd, cs], ['cd', 'cd', 'sd', 'cs', 'ss5'], False, False),

            # request c.*
            (201, 'c.*', '*.*', {}, [], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], True, True),

            (221, 'c.*', 'c.d', {}, [cd], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], True, True),
            (222, 'c.*', '*.d', {}, [sd], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], True, True),
            (223, 'c.*', 'c.*', {}, [cs], ['cs', 'ss2', 'ss3', 'cs', 'ss5'], False, False),

            (231, 'c.*', 'c.d', {}, [cd, cs], ['cs', 'ss2', 'ss3', 'cs', 'ss5'], False, False),
            (232, 'c.*', 'c.d', {}, [sd, cs], ['cs', 'ss2', 'ss3', 'cs', 'ss5'], False, False),
            (233, 'c.*', 'c.d', {}, [sd, cd], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], True, True),

            (241, 'c.*', 'c.d', {}, [cd, sd, cs], ['cs', 'ss2', 'ss3', 'cs', 'ss5'], False, False),

            # request *.d
            (301, '*.d', '*.*', {}, [], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], True, True),

            (321, '*.d', 'c.d', {}, [cd], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], True, True),
            (322, '*.d', '*.d', {}, [sd], ['sd', 'ss2', 'sd', 'ss4', 'ss5'], False, False),
            (323, '*.d', 'c.*', {}, [cs], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], True, True),

            (331, '*.d', 'c.d', {}, [cd, cs], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], True, True),
            (332, '*.d', 'c.d', {}, [sd, cs], ['sd', 'ss2', 'sd', 'ss4', 'ss5'], False, False),
            (333, '*.d', 'c.d', {}, [sd, cd], ['sd', 'ss2', 'sd', 'ss4', 'ss5'], False, False),

            (341, '*.d', 'c.d', {}, [cd, sd, cs], ['sd', 'ss2', 'sd', 'ss4', 'ss5'], False, False),

            # request *.*
            (401, '*.*', '*.*', {}, [], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], False, False),

            (421, '*.*', 'c.d', {}, [cd], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], False, False),
            (422, '*.*', '*.d', {}, [sd], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], False, False),
            (423, '*.*', 'c.*', {}, [cs], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], False, False),

            (431, '*.*', 'c.d', {}, [cd, cs], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], False, False),
            (432, '*.*', 'c.d', {}, [sd, cs], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], False, False),
            (433, '*.*', 'c.d', {}, [sd, cd], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], False, False),

            (441, '*.*', 'c.d', {}, [cd, sd, cs], ['ss1', 'ss2', 'ss3', 'ss4', 'ss5'], False, False),

            ## Overridden data

            (1101, 'c.d', '*.*', ov, [], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], True, True),

            (1121, 'c.d', 'c.d', ov, [cd], ['ov', 'cd', 'ss3', 'ss4', 'ov'], False, False),
            (1122, 'c.d', '*.d', ov, [sd], ['ov', 'ss2', 'sd', 'ss4', 'ov'], False, True),
            (1123, 'c.d', 'c.*', ov, [cs], ['ov', 'ss2', 'ss3', 'cs', 'ov'], False, True),

            (1131, 'c.d', 'c.d', ov, [cd, cs], ['ov', 'cd', 'ss3', 'cs', 'ov'], False, False),
            (1132, 'c.d', 'c.d', ov, [sd, cs], ['ov', 'ss2', 'sd', 'cs', 'ov'], False, True),
            (1133, 'c.d', 'c.d', ov, [sd, cd], ['ov', 'cd', 'sd', 'ss4', 'ov'], False, False),

            (1141, 'c.d', 'c.d', ov, [cd, sd, cs], ['ov', 'cd', 'sd', 'cs', 'ov'], False, False),

            # request c.*
            (1201, 'c.*', '*.*', ov, [], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], True, True),

            (1221, 'c.*', 'c.d', ov, [cd], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], True, True),
            (1222, 'c.*', '*.d', ov, [sd], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], True, True),
            (1223, 'c.*', 'c.*', ov, [cs], ['ov', 'ss2', 'ss3', 'cs', 'ov'], False, False),

            (1231, 'c.*', 'c.d', ov, [cd, cs], ['ov', 'ss2', 'ss3', 'cs', 'ov'], False, False),
            (1232, 'c.*', 'c.d', ov, [sd, cs], ['ov', 'ss2', 'ss3', 'cs', 'ov'], False, False),
            (1233, 'c.*', 'c.d', ov, [sd, cd], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], True, True),

            (1241, 'c.*', 'c.d', ov, [cd, sd, cs], ['ov', 'ss2', 'ss3', 'cs', 'ov'], False, False),

            # request *.d
            (1301, '*.d', '*.*', ov, [], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], True, True),

            (1321, '*.d', 'c.d', ov, [cd], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], True, True),
            (1322, '*.d', '*.d', ov, [sd], ['ov', 'ss2', 'sd', 'ss4', 'ov'], False, False),
            (1323, '*.d', 'c.*', ov, [cs], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], True, True),

            (1331, '*.d', 'c.d', ov, [cd, cs], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], True, True),
            (1332, '*.d', 'c.d', ov, [sd, cs], ['ov', 'ss2', 'sd', 'ss4', 'ov'], False, False),
            (1333, '*.d', 'c.d', ov, [sd, cd], ['ov', 'ss2', 'sd', 'ss4', 'ov'], False, False),

            (1341, '*.d', 'c.d', ov, [cd, sd, cs], ['ov', 'ss2', 'sd', 'ss4', 'ov'], False, False),

            # request *.*
            (1401, '*.*', '*.*', ov, [], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], False, False),

            (1421, '*.*', 'c.d', ov, [cd], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], False, False),
            (1422, '*.*', '*.d', ov, [sd], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], False, False),
            (1423, '*.*', 'c.*', ov, [cs], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], False, False),

            (1431, '*.*', 'c.d', ov, [cd, cs], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], False, False),
            (1432, '*.*', 'c.d', ov, [sd, cs], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], False, False),
            (1433, '*.*', 'c.d', ov, [sd, cd], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], False, False),

            (1441, '*.*', 'c.d', ov, [cd, sd, cs], ['ov', 'ss2', 'ss3', 'ss4', 'ov'], False, False),
        ]


        LIMIT_TO = None
        # LIMIT_TO = 1101

        LIMIT_LOOP = None
        # LIMIT_LOOP = 'any'

        if LIMIT_TO is not None or LIMIT_LOOP is not None:
            with self.subTest('LIMITED TEST'):
                raise SkipTest('Limited Test')

        for index, req, resp_key, override, data, return_any_data, return_partial_raise, return_full_raise in TESTS:
            if LIMIT_TO is None or LIMIT_TO == index:
                loop = (
                    ('any', False),
                    ('partial', return_partial_raise),
                    ('full', return_full_raise))

                td = WCMTest(data)
                expected = deepcopy(WCMTest_base_return)
                expected.update(dict(
                    field1=return_any_data[0],
                    field2=return_any_data[1],
                    field3=return_any_data[2],
                    field4=return_any_data[3],
                    field5=return_any_data[4],
                    key1=KeyObj(resp_key),
                ))

                for req_type, should_raise in loop:
                    if LIMIT_LOOP is None or LIMIT_LOOP == req_type:
                        td._cache.clear()
                        td.return_on = req_type
                        if should_raise:
                            with self.subTest('#%s - %s - td[%s] -> RAISE' % (index, req_type, req)):
                                with self.assertRaises(KeyError):
                                    tmp_ret = td[req]

                        elif not override:
                            with self.subTest('#%s - %s - td[%s]' % (index, req_type, req)):
                                tmp_ret = td[req]
                                if tmp_ret != expected:
                                    self.fail(print_results(tmp_ret, expected))
                                # self.assertEqual(tmp_ret, expected)
                        else:
                            with self.subTest('#%s - %s - td.get(%s, OV)' % (index, req_type, req)):
                                tmp_ret = td.get(req, override)
                                if tmp_ret != expected:
                                    self.fail(print_results(tmp_ret, expected))
                                # self.assertEqual(tmp_ret, expected)

    def test_replace_list(self):
        td = WCMTest()
        td['a.b'] = {'replace_list': ['u', 'v']}
        td['a.b'] = {'replace_list': ['w', 'x']}
        td['*.b'] = {'replace_list': ['y', 'z']}

        tmp_ret = td['a.b']
        self.assertEqual(tmp_ret['replace_list'], ['w', 'x'])

    def test_update_list(self):
        td = WCMTest()
        td['a.b'] = {'simple_list': ['u', 'v']}
        td['a.*'] = {'simple_list': ['w', 'x']}
        td['*.b'] = {'simple_list': ['y', 'z']}

        tmp_ret = td['a.b']
        self.assertCountEqual(tmp_ret['simple_list'], ['u', 'v', 'w', 'x', 'y', 'z'])

    def test_comb_str(self):
        td = WCMTest()
        td['a.b'] = {'comb_str': 'uv'}
        td['a.*'] = {'comb_str': 'wx'}
        td['*.b'] = {'comb_str': 'yz'}

        tmp_ret = td['a.b']
        self.assertEqual(tmp_ret['comb_str'], 'uv\nwx\nyz')

    def test_comb_key_str(self):
        td = WCMTest()
        td['a.*'] = {'comb_key_str': 'wx'}
        td['*.b'] = {'comb_key_str': 'yz'}

        tmp_ret = td['a.b']
        self.assertEqual(tmp_ret['comb_key_str'], 'wx - yz')

    def test_comb_key_str_2(self):
        td = WCMTest()
        td['a.b'] = {'comb_key_str_2': 'uv'}
        td['a.*'] = {'comb_key_str_2': 'wx'}
        td['*.b'] = {'comb_key_str_2': 'yz'}

        tmp_ret = td['a.b']
        self.assertEqual(tmp_ret['comb_key_str_2'], 'test_cks: wx - uv')

    def test_update_dict(self):
        td = WCMTest()
        td['a.b'] = {'simple_dict': {'f1': 1, 'f2': 2}}
        td['a.*'] = {'simple_dict': {'f1': 10, 'f3': 3}}
        td['*.b'] = {'simple_dict': {'f1': 100, 'f4': 4}}

        tmp_ret = td['a.b']
        self.assertEqual(tmp_ret['simple_dict'], {'f1': 1, 'f2': 2, 'f3': 3, 'f4': 4})

    def test_locked_raise(self):
        td = WCMTest()
        td['a.b'] = {'locked_str': 'test1'}
        td['a.*'] = {'locked_str': 'test2'}
        td['*.b'] = {'locked_str': 'test3'}

        with self.assertRaises(AttributeError):
            tmp_ret = td['a.b']

    def test_locked_pass(self):
        td = WCMTest()
        td['a.b'] = {'locked_str': 'test1'}
        td['a.*'] = {'field1': 'test2'}
        td['*.b'] = {'field2': 'test3'}
        tmp_ret = td['a.b']
        self.assertEqual(tmp_ret['locked_str'], 'test1')

    def test_len(self):
        td = WCMTest()
        td['a.b'] = {'simple_list': ['u', 'v']}
        td['a.*'] = {'simple_list': ['w', 'x']}
        td['*.b'] = {'simple_list': ['y', 'z']}

        self.assertEqual(len(td), 4)

    def test_contains(self):
        td = WCMTest()
        td['a.b'] = {'simple_list': ['u', 'v']}
        td['a.*'] = {'simple_list': ['w', 'x']}
        td['*.b'] = {'simple_list': ['y', 'z']}

        self.assertEqual('a.b' in td, True)
        self.assertEqual('x.b' in td, True)
        self.assertEqual('a.a' in td, True)
        self.assertEqual('a.*' in td, True)
        self.assertEqual('*.b' in td, True)
        self.assertEqual('*.*' in td, True)

        self.assertEqual('x.*' in td, False)
        self.assertEqual('x.y' in td, False)
        self.assertEqual('*.y' in td, False)

    def test_iter(self):
        td = WCMTest()
        td['a.b'] = {'simple_list': ['u', 'v']}
        td['a.*'] = {'simple_list': ['w', 'x']}
        td['*.b'] = {'simple_list': ['y', 'z']}

        tmp_ret = list(td)

        self.assertCountEqual(tmp_ret, ['*.*', 'a.B', '*.B', 'a.*'])






