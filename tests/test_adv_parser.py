import unittest

from isemail_parsers import _and, _or, _r, _char, _for, _look, _m, _make_meth, _opt, _rule, ParserOps
from py_is_email import ParserRule, ParseString, ParserOps
from adv_parser import _get_between, _get_simple_between, _check_enclosures

BASIC_BETWEENS = [
    ('foo', ('foo', '', '')),
    ('foo(bar)', ('foo', 'bar', '')),
    ('(foo)bar', ('', 'foo', 'bar')),
    ('fo(ob)ar', ('fo', 'ob', 'ar')),
    ('(foo)(bar)', ('', 'foo', '(bar)'))]

ADV_BETWEENS = [
    ('foo((ba)r)', True, ['foo', ['', 'ba', 'r'], '']),
    ('(foo(b(a(r))))', True, ['', ['foo', ['b', ['a', ['r','',''],''],''],''],'']),
    ('foo((ba)r)', False, ['foo', '(ba)r', '']),
    ('(foo(b(a(r))))', False, ['', '(foo(b(a(r)))', '']),
    ('01234(678(9012)456)890', True, ['1234', ['678', '9012','456'],'890']),
    ('01234(678(9012)456)890', False, ['1234', '678(9012)456','890'])
]

ERR_BETWEENS = [
    'te)st',
    'te(st',
    'foo(bar(foo)',
    'foo(bar))foo',
]




class TestGetBetweens(unittest.TestCase):

    def test_check_enclosures(self):
        for test in BASIC_BETWEENS:
            with self.subTest('run: %s' % test[0]):
                tmp_ret = _check_enclosures(test[0], '(', ')')
                print(tmp_ret)
                self.assertTrue(True)

        for test in ADV_BETWEENS:
            with self.subTest('run_adv: %s' % test[0]):
                tmp_ret = _check_enclosures(test[0], '(', ')')
                print(tmp_ret)
                self.assertTrue(True)

        for test in ERR_BETWEENS:
            with self.subTest('error: %s' % test):
                with self.assertRaises(AttributeError):
                    tmp_ret = _check_enclosures(test, '(', ')')
                    print(tmp_ret)


    def test_simple_between(self):
        for test in BASIC_BETWEENS:
            test_str = test[0]
            with self.subTest('run: %s' % test_str):
                tmp_ret = _get_simple_between(test_str, '(', ')')
                self.assertEqual(test[1], tmp_ret)

        for test in ERR_BETWEENS:
            with self.subTest('error: %s' % test):
                with self.assertRaises(AttributeError):
                    tmp_ret = _get_simple_between(test, '(', ')')


    def test_complex_betweens(self):
        for test in BASIC_BETWEENS:
            with self.subTest('run: %s' % test[0]):
                tmp_ret = _get_between(test[0], '(', ')')
                self.assertEqual(test[1], tmp_ret)
        for test in ADV_BETWEENS:
            with self.subTest('run_adv: %s' % test[0]):
                tmp_ret = _get_between(test[0], '(', ')', allow_recursive=test[1])
                self.assertEqual(test[2], tmp_ret)

        for test in ERR_BETWEENS:
            with self.subTest('error: %s' % test):
                with self.assertRaises(AttributeError):
                    tmp_ret = _get_between(test, '(', ')')



TEST_DATA_LOOKUPS = dict(
    ALPHA='abcdefghijklmnopqrstuvwxyz',
    ABCD='abcd',
    ABCDE='abcde',
    ABCDEF='abcdef',
    DEFG='defg',
    JKLM='jklm',
    FOO='foo',
    FGHIJK='fghijk',
)


TEST_DATA_RULES = dict(
    start='ABCDEF',
    and_rule='ABCD DEFG',
    or_rule='ABCD / JKLM',
    opt_rule='[ABCD]',
    c_rule='2ABCD',
    c_rule_min='2*ABCD',
    c_rule_max='*2ABCD',
    c_rule_min_max='2*3ABCD',
    c_rule_unl='*ABCD',
    m_rule_pass_fail='start<pass-10/fail-20>',
    m_rule_element_name='alpha / *SPACE:test_name:<pass-10^PERCENT<pass-11/fail-20>^/fail-20>',
    look_rule='ABCD^PRECENT<pass-10/fail-20>^',
    look_quoted_rule='ABCD^"fubar"<pass-10/fail-20>^',
    rule_rule='start',
    lookup_char='HEXDIG',
    lookup_char_opt='HEXDIG [HEXDIG]',
    quoted_char_str='HEXDIG "::" HEXDIG',
    quoted_char_str2='3FOO COMMA "bar"',
    complex_and='*5LTR_STR [(DOT *5LTR_STR)]',
    complex_or='5ABCDE / 1FGHIJK',
    complex_and_or='(*5ALPHA [DOT 2ALPHA]) / *3(HEXDIG ["::" 5HEXDIG])',

    multiple_marks_rule='[mmr_pre_str] mmr_o_sqb mmr_flag_str mmr_c_sqb [mmr_post_str]',
    mmr_pre_str='*LTR_STR:pre:<pre-p-11/pre-f-101>',
    mmr_o_sqb='-OPENSQBRACKET<osq-p-12/osq-f-102>',
    mmr_c_sqb='CLOSESQBRACKET<csq-p-13/csq-f-103>',
    mmr_post_str='*LTR_STR:post:<post-p-14/post-f-104>',
    mmr_ret_str='mmr_o_sqb LTR_STR -mmr_c_sqb',
    mmr_flag_str='mmr_ret_str:data:<data-p-15/data-p-105>',

    count_in_ret='*ABCD#[1*4A]<under/within/over>#',
    len_in_ret='*ABCD%[1*4]<under/within/over>%',
)

"""
parse codes:

PRE-CODES:
    -   will not pass the returned value up (removes it from the text)
    min*max  - will allow repeated testing of the rule between min and max times
    *max    - will allow repeated testing of the rule no more than max times
    min*    - will test the rule at least min times
    * allows testing of the rule unlimited times

post code groups:

    :element_name:  - will save the returned value as element name
    <pass/fail>:    (used outside of another post code group) will save this code to the diag list

advanced groups (can be used within the <pass/fail> or directly after the rule
    ^char_set<pass/fail>,char_set<pass/fail>^ - will look for (but not capture) char set in the returned value, and
                                                add <pass/fail> to the diag list
                                                (if this is in the <pass/fail> of the gorup, this will only operate if
                                                the return has passed or failed)

    #min*max char_set<under/within/over>#  - will count the occurance of
    #[min*max char_set]<pass/fail>#
                - can also enclose min*max in [] for optional counts
    %min*max<under/within/over>%
    %[min*max]<pass/fail>%


"""


'''
multiple_marks_rule=_and(
    _m(_opt(_r('LTR_STR')), element_name='pre', on_pass=11, on_fail=101),
    _m(_and(
            _m('OPENSQBRACKET', return_string=False, on_pass=12, on_fail=102),
            _r('LTR_STR'),
            _m('CLOSESQBRACKET', return_string=False, on_pass=13, on_fail=103)),
        element_name='data', on_pass=14, on_fail=104),
    _m(_opt(_r('LTR_STR')), element_name='post', on_pass=15, on_fail=105))
'''

'''

TEST_DATA_RULES = dict(
    start=('abcdef'),
    and_rule=_and(_char('abcd'), _char('defg')),
    or_rule=_or(_char('abcd'), _char('jklm')),
    opt_rule=_opt(_char('abcd')),
    c_rule=_r(2, _char('abcd')),
    c_rule_min=_r('2*', _char('abcd')),
    c_rule_max=_r('*2', _char('abcd')),
    c_rule_min_max=_r('2*3', _char('abcd')),
    c_rule_unl=_r('*', _char('abcd')),
    c_rule_unl2=_r(_char('abcd')),
    m_rule=_m(_char('abcd')),
    m_rule_pass_fail=_m('start', on_fail=20, on_pass=10),
    m_rule_element_name=_m(_or('alpha', _r('SPACE')), element_name='test_name', on_fail=20, on_pass=10),
    look_rule=_look(_char('abcd'), _for(_char('%', on_pass=10, on_fail=20))),
    rule_rule=_rule('start'),
    lookup_char=_and('HEXDIG'),
    lookup_char_opt=_and('HEXDIG', '[HEXDIG]'),
    quoted_char_str=_and('HEXDIG', '"::"', 'HEXDIG'),
    quoted_char_str2=_and(_r(3, _char('foo')), 'COMMA', '"bar"'),

    complex_and=_and(_r('*5', 'LTR_STR'), _opt(_and('DOT', _r('*5', 'LTR_STR')))),

    complex_or=_or(_r('5', _char('abcde')), _r('1', _char('fghijk'))),
    complex_and_or=_or(
        _and(
            _r('*5', 'ALPHA'),
            _opt(_and('DOT', _r('ALPHA')))),
        _and(
            'HEXDIG',
            _opt(_and('"::"', 'HEXDIG')))),
    complex_and_or2=_or(
        _and(
            _r('*5', 'ALPHA'),
            _r(_opt(_and('DOT', _r(2, 'ALPHA'))))),
        _and(
            _r(5, 'HEXDIG'),
            _r('*3', _opt(_and('"::"', _r(5, ('HEXDIG'))))))),
    multiple_marks_rule=_and(
        _m(_opt(_r('LTR_STR')), element_name='pre', on_pass=11, on_fail=101),
        _m(_and(
                _m('OPENSQBRACKET', return_string=False, on_pass=12, on_fail=102),
                _r('LTR_STR'),
                _m('CLOSESQBRACKET', return_string=False, on_pass=13, on_fail=103)),
            element_name='data', on_pass=14, on_fail=104),
        _m(_opt(_r('LTR_STR')), element_name='post', on_pass=15, on_fail=105))

)
'''
rules = ParserOps(TEST_DATA_RULES, on_fail=2, on_rem_string=1)

TEST_SETS = [
    (1, 'start', 'a', 0, ''),
    (2, 'start', 'h', 2, 'h'),
    (3, 'start', 'abc', 1, 'bc'),
    (4, 'and_rule', 'ad', 0, ''),
    (5, 'and_rule', 'ha', 2, 'ha'),
    (6, 'and_rule', 'xx', 2, 'xx'),
    (7, 'and_rule', 'aa', 2, 'aa'),
    (8, 'and_rule', 'ade', 1, 'e'),
    (9, 'or_rule', 'a', 0, ''),
    (10, 'or_rule', 'l', 0, ''),
    (11, 'or_rule', 'z', 2, 'z'),
    (12, 'opt_rule', 'ax', 1, 'x'),
    (13, 'opt_rule', '', 0, ''),
    (14, 'm_rule', 'a', 0, ''),
    (15, 'm_rule', 'h', 2, 'h'),
    (16, 'm_rule', 'abc', 1, 'bc'),
    (17, 'c_rule', 'ab', 0, ''),
    (18, 'c_rule', 'abb', 1, 'b'),
    (19, 'c_rule', 'a', 2, 'a'),
    (20, 'c_rule_min', 'a', 2, 'a'),
    (21, 'c_rule_min', 'aa', 0, ''),
    (22, 'c_rule_min', 'aaa', 0, ''),
    (23, 'c_rule_max', 'a', 0, ''),
    (24, 'c_rule_max', 'ax', 1, 'x'),
    (25, 'c_rule_max', 'aa', 0, ''),
    (26, 'c_rule_max', 'aaa', 1, 'a'),
    (27, 'c_rule_unl', 'a', 0, ''),
    (28, 'c_rule_unl', 'ax', 1, 'x'),
    (29, 'c_rule_unl', 'aa', 0, ''),
    (30, 'c_rule_unl', 'aaa', 0, ''),
    (31, 'c_rule_unl', 'aaabbbbbcccccdddddd', 0, ''),
    (32, 'c_rule_unl2', 'a', 0, ''),
    (33, 'c_rule_unl2', 'ax', 1, 'x'),
    (34, 'c_rule_unl2', 'aa', 0, ''),
    (35, 'c_rule_unl2', 'aaa', 0, ''),
    (36, 'c_rule_unl2', 'aaabbbbbcccccdddddd', 0, ''),
    (37, 'rule_rule', 'a', 0, ''),
    (38, 'rule_rule', 'h', 2, 'h'),
    (39, 'rule_rule', 'abc', 1, 'bc'),
    (40, 'lookup_char', 'a', 0, ''),
    (41, 'lookup_char', '2', 0, ''),
    (42, 'lookup_char', 'A', 0, ''),
    (43, 'lookup_char', 'x', 2, 'x'),
    (44, 'lookup_char', 'ab', 1, 'b'),
    (45, 'lookup_char', 'xab', 2, 'xab'),
    (46, 'lookup_char_opt', 'a', 0, ''),
    (47, 'lookup_char_opt', 'aa', 0, ''),
    (48, 'lookup_char_opt', 'af', 0, ''),
    (49, 'lookup_char_opt', 'aaaa', 1, 'aa'),
    (50, 'lookup_char_opt', 'xaxa', 2, 'xaxa'),
    (51, 'quoted_char_str', 'a::a', 0, ''),
    (52, 'quoted_char_str', 'f::a', 0, ''),
    (53, 'quoted_char_str', 'f::as', 1, 's'),
    (54, 'quoted_char_str', 'f', 2, 'f'),
    (55, 'quoted_char_str', 'f:a', 2, 'f:a'),
    (56, 'm_rule_pass_fail', 'a', 10, ''),
    (57, 'm_rule_pass_fail', 'x', 20, 'x'),
    (58, 'm_rule_element_name', 'aaa', 10, '', {'test_name': (('aaa', 0),)}),
    (59, 'm_rule_element_name', 'startthisnow', 10, '', {'test_name': (('startthisnow', 0),)}),
    (60, 'look_rule', 'a', 20, ''),
    (61, 'look_rule', 'x', 20, ''),
    (62, 'look_rule', 'a%', 10, ''),
    (63, 'quoted_char_str2', 'foo,bar', 0, ''),
    (64, 'quoted_char_str2', 'oof,bar', 0, ''),
    (65, 'quoted_char_str2', 'oof,rab', 2, 'oof,rab'),
    (66, 'quoted_char_str2', 'ofo,bar', 0, ''),
    (67, 'complex_and', 'abdxe', 0, ''),
    (68, 'complex_and', 'abd', 0, ''),
    (69, 'complex_and', 'abdxe.abcde', 0, ''),
    (70, 'complex_and', 'abdxe.', 1, '.'),
    (71, 'complex_and', 'abdxeee', 1, 'ee'),
    (72, 'complex_and', 'abdxe.a', 0, ''),
    (73, 'complex_and', 'abdxe.abcdev', 1, 'v'),
    (74, 'complex_or', 'abcde', 0, ''),
    (75, 'complex_or', 'f', 0, ''),
    (76, 'complex_or', 'abcd', 2, 'abcd'),
    (77, 'complex_or', 'abcdf', 2, 'abcdf'),
    (78, 'complex_or', 'ffff', 1, 'fff'),
    (79, 'complex_and_or', 'abdxe', 0, ''),
    (80, 'complex_and_or', 'abd', 0, ''),
    (81, 'complex_and_or', 'abdxe.abcde', 0, ''),
    (82, 'complex_and_or', 'abdxe.', 1, '.'),
    (83, 'complex_and_or', 'abdxeee', 1, 'ee'),
    (84, 'complex_and_or', '123::a', 1, '23::a'),
    (84, 'complex_and_or', 'abdxe.abcdev', 0, ''),
    (85, 'complex_and_or', '1::1', 0, ''),
    (86, 'complex_and_or', ':z::z', 2, ':z::z'),
    (87, 'complex_and_or2', '1bcde', 0, ''),
    (88, 'complex_and_or2', '1bcde::1bcde', 0, ''),
    (89, 'complex_and_or2', '1bcde::1bcde::abcde', 0, ''),
    (90, 'complex_and_or2', '1bcde::1bcde::abcde::abcde', 0, ''),
    (91, 'complex_and_or2', '1bcde::1bcde::abcde::abcde::abcde', 1, '::abcde'),
    (92, 'complex_and_or2', 'abcdx', 0, ''),
    (93, 'complex_and_or2', 'abcdxzz', 1, 'zz'),
    (94, 'complex_and_or2', 'xyzhk.a', 1, '.a'),
    (95, 'complex_and_or2', 'xyzhk.ab', 0, ''),
    (96, 'complex_and_or2', 'xyzhk.ab.a', 1, '.a'),
    (97, 'complex_and_or2', 'xyzhk.ab.ax', 0, ''),
    (98, 'complex_and_or2', 'xyzhk.ab.ax.ab.ab', 0, ''),
    (99, 'complex_and_or2', 'xyzhk.ab.ax.ab.ab.ab.ab.', 1, '.'),
    (100, 'multiple_marks_rule', 'foo[bar]blah', 15, '',
        {'pre': (('foo', 0),), 'post': (('blah', 8),), 'data': (('bar', 5),)},
        {0: [12],
         11: [0],
         12: [3],
         13: [7],
         14: [3],
         15: [8]}),
    (101, 'multiple_marks_rule', 'foo/[bar]blah', 2, 'foo/[bar]blah', {'pre': (('foo', 0),)}, 10),
    (102, 'multiple_marks_rule', 'foo[barblah', 2, 'foo[barblah', {'pre': (('foo', 0),)}, 11),
    (103, 'multiple_marks_rule', '[bar]', 0, '', {'data': (('bar', 0),)}, 12),
    (104, 'multiple_marks_rule', '[bar]foo', 0, '', {'data': (('bar', 0),), 'post': (('foo', 5),)}, 13),
    (105, 'c_rule_min_max', 'a', 2, 'a'),
    (106, 'c_rule_min_max', 'ab', 0, ''),
    (107, 'c_rule_min_max', 'abc', 0, ''),
    (108, 'c_rule_min_max', 'abcd', 1, 'd'),

]

RUN_TEST_NUM = 100


class TestParser(unittest.TestCase):
    maxDiff = None

    def test_sets(self):
        for test in TEST_SETS:
            if RUN_TEST_NUM is None or RUN_TEST_NUM == test[0] or (isinstance(RUN_TEST_NUM, (list, tuple, range)) and test[0] in RUN_TEST_NUM):
                print('--------------------')
                print('[%s] RUN %s(%s)' % (test[0], test[1], test[2]))
                print('--------------------\n')
                with self.subTest('[%s] RUN %s(%s)' % (test[0], test[1], test[2])):
                    pem = ParseString(parser=rules.parse_str, parser_start_rule=test[1])
                    tmp_resp = pem(test[2])
                    self.assertEqual(test[3], tmp_resp)

                with self.subTest('[%s] REN %s(%s)' % (test[0], test[1], test[2])):
                    self.assertEqual(test[4], pem.remaining())
                if len(test) > 5:
                    with self.subTest('[%s] ELEM  %s(%s)' % (test[0], test[1], test[2])):
                        tmp_elements = pem.elements()
                        tmp_expected = {}
                        for e_name, e_items in test[5].items():
                            tmp_expected[e_name] = []
                            tmp_item = {}
                            for e_item, e_pos in e_items:
                                tmp_item['element'] = e_item
                                tmp_item['pos'] = e_pos
                            tmp_expected[e_name].append(tmp_item)
                        self.assertCountEqual(tmp_expected, tmp_elements)

                if len(test) > 6:
                    with self.subTest('[%s] RESP %s(%s)' % (test[0], test[1], test[2])):
                        self.assertEqual(test[6], pem.diags(field='position'))
