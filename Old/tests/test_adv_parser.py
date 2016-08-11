import unittest
from adv_parser import *
# from adv_parser import _and, _or, _r, _char, _for, _look, _m, _make_meth, _opt, _rule, ParserOps, ParserAction
# from py_is_email import ParserRule, ParseString, ParserOps
# from adv_parser import _get_between, _get_simple_between, _check_enclosures, _parse_enclosure

'''

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
'''
"""

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


class l(object):
    def __init__(self, lookup_str):
        self.lookup = lookup_str

TEST_LOAD_RULES_PRELOAD = [
    ('abcd', Char, 'abcd', {}),
    ('jklm', Char, 'jklm', {}),

    ('char_rule', Char, 'abcdef', {}),
    ('char_rule2', Char, '/abcdef', {}),
    ('lookup_char_rule', Char, 'ABCD', {}),
    ('char_rule_quoted_str', Char, '"Foo"', {}),
    ('char_rule_quoted_str_case_insensitive', Word, '^"Foo"', {}),
    ('and_rule', And, ('/abcd', 'DEFG'), {}),
    ('and_rule2', And, ('/abcd', '/defg'), {}),

    ('or_rule', Or, (l('abcd'), l('jklm'))),
    ('opt_rule', Char, (['/abcd'],), {}),
    ('opt_rule2', Char, '[/abcd]', {}),
    ('c_rule', Repeat, (2, l('abcd'))),
    ('c_rule_min', Repeat, ('2*', l('abcd'))),
    ('c_rule_max', Repeat, ('*2', l('abcd'))),
    ('c_rule_min_max', Repeat, ('2*3', l('abcd'))),
    ('c_rule_unl', Repeat, ('*', l('abcd'))),
    ('c_rule_unl2', Repeat, (l('abcd'))),
    ('c_rule_inChar', Char, '2*ABCD', {}),
    ('c_rule_mult_items', Repeat, ('2*3', l('and_rule2'))),
    ('rule_rule', Rule, 'char_rule'),
    ('lookupChar', And, 'HEXDIG'),
    ('lookupChar_opt', And, ('HEXDIG', '[HEXDIG]')),
    ('quotedChar_str', And, ('HEXDIG', '"::"', 'HEXDIG')),
    ('count_rule', Count, ('3*a', '*abcde')),
    ('count_rule_qs', Count, ('1*2"ab"', '*abcde')),
    ('count_rule_opt', Count, ('[3*a]', '*abcde')),
    ('word_abcde', Word, 'abcde'),
    ('len_rule', Len, ('2*4', l('word_abcde'))),
    ('len_rule_opt', Len, ('[2*4]', l('word_abcde'))),

    # Actions :


    ('p10_f20', ParserAction, None, {'pass_diag': 'pass_10', 'fail_diag': 'fail_20'}),
    ('test_name', ParserAction, None, {'name': 'test_name'}),
    ('fail_len', ParserAction, None, {'fail_diag': 'len_fail', 'pass_diag': 'len_pass'}),
    ('fail_sb', ParserAction, None, {'fail_diag': 'has_sb', 'pass_diag': 'no_sb_there'}),
    ('pre', ParserAction, None, {'pass_diag': 'pre_pass11', 'fail_diag': 'pre_fail101', 'name': 'pre'}),
    ('post', ParserAction, None, {'pass_diag': 'post_pass11', 'fail_diag': 'post_fail101', 'name': 'post'}),
    ('data', ParserAction, None, {'pass_diag': 'data_pass11', 'fail_diag': 'data_fail101', 'name': 'data'}),
    ('osb', ParserAction, None, {'pass_diag': 'osb_pass11', 'fail_diag': 'osb_fail101', 'name': 'osb'}),
    ('csb', ParserAction, None, {'pass_diag': 'csb_pass11', 'fail_diag': 'csb_fail101', 'name': 'csb'}),



    ('m_rule_pass_fail', Char, '"start"', {'actions': l('p10_f20')}),
    ('or_alpha_space', Or, ('alpha', 'SPACE')),
    ('m_rule_element_name', Repeat, l('or_alpha_space'), {'actions': ('p10_f20, test_name')}),

    ('next_withChars', Char, 'abcde', {'next': '/fghi'}),
    ('next_with_lookup', Char, 'abcde', {'next': 'HEXDIG'}),
    ('next_with_rule', Char, 'abcde', {'next': 'char_rule_quoted_str'}),
    ('next_with_opt_action_rule', Char, 'abcde', {'next':'[m_rule_pass_fail]'}),
    ('next_with_action_rule', Char, 'abcde', {'next':'m_rule_pass_fail'}),

    ('has_at', ParserAction, None, {'pass_diag': 'has_at', 'fail_diag': 'no_at'}),
    ('has_qt', ParserAction, None, {'pass_diag': 'has_qt', 'fail_diag': 'no_qt'}),
    ('both_next_at', Char, '@', {'actions': l('has_at')}),
    ('both_next_dquote', Char, 'DQUOTE', {'actions': l('has_qt')}),
    ('both_next_and', And, (l('both_next_at'), l('both_next_dquote'))),

    ('both_next_rule', Char, 'abcde', {'next': l('both_next_and')}),
]

TEST_LOAD_RULES_RUN_NAME = None

TEST_LOAD_RULES = {}
for tr in TEST_LOAD_RULES_PRELOAD:
    TEST_LOAD_RULES[tr[0]] = tr


class TestLoadRules(unittest.TestCase):
    # rule_set = None

    def make_rule(self, key):
        tmp_item = TEST_LOAD_RULES[key]
        tmp_rule_type = tmp_item[1]
        tmp_args = tmp_item[2]
        try:
            tmp_kwargs = tmp_item[3]
        except IndexError:
            tmp_kwargs = {}

        if tmp_args is not None:
            if isinstance(tmp_args, tuple):
                tmp_new_args = []
                for a in tmp_args:
                    if isinstance(a, l):
                        tmp_new_args.append(self.make_rule(a.lookup))
                    else:
                        tmp_new_args.append(a)
            else:
                tmp_new_args = [tmp_args]
        else:
            tmp_new_args = []

        tmp_new_kwargs = {}
        for kwkey, item in tmp_kwargs.items():
            if isinstance(item, tuple):
                for a in item:
                    if isinstance(a, l):
                        tmp_new_kwargs[kwkey] = self.make_rule(a)
                    else:
                        tmp_new_kwargs[kwkey] = a
            else:
                tmp_new_kwargs[kwkey] = tmp_args

        return tmp_rule_type(*tmp_new_args, **tmp_new_kwargs)

    def test_load_rules(self):

        for tr in TEST_LOAD_RULES_PRELOAD:
            if TEST_LOAD_RULES_RUN_NAME is None or TEST_LOAD_RULES_RUN_NAME == tr[0]:
                with self.subTest(tr[0]):
                    tmp_item = self.make_rule(tr[0])


TEST_DATA_RULES = dict(
    char_rule=Char('abcdef'),
    char_rule2='/abcdef',
    lookupChar_rule='ABCD',
    char_rule_quoted_str='"Foo"',
    char_rule_quoted_str_case_insensitive='^"Foo"',
    and_rule=And('/abcd', 'DEFG'),
    or_rule=Or(Char('abcd'), Char('jklm')),
    opt_rule=['/abcd'],
    opt_rule2='[/abcd]',
    c_rule=Repeat(2, Char('abcd')),
    c_rule_min=Repeat('2*', Char('abcd')),
    c_rule_max=Repeat('*2', Char('abcd')),
    c_rule_min_max=Repeat('2*3', Char('abcd')),
    c_rule_unl=Repeat('*', Char('abcd')),
    c_rule_unl2=Repeat(Char('abcd')),
    c_rule_inChar='2*ABCD',
    c_rule_mult_items=Repeat('2*3', And('/abcd', '/defg')),
    rule_rule=Rule('char_rule'),
    lookupChar=And('HEXDIG'),
    lookupChar_opt=And('HEXDIG', '[HEXDIG]'),
    quotedChar_str=And('HEXDIG', '"::"', 'HEXDIG'),
    quotedChar_str2=And(Repeat(3, Char('foo')), 'COMMA', '"bar"'),
    complex_and=And('*5LTR_STR', [And('DOT', '*5LTR_STR')]),

    complex_or=Or(Word('abcde', exact=5), Char('fghijk')),
    complex_and_or=Or(
        And(
            Word('ALPHA', max=5),
            [And('DOT', '*ALPHA')]),
        And(
            'HEXDIG',
            [And('"::"', 'HEXDIG')])),
    complex_and_or2=Or(
        And(
            '*5ALPHA',
            Repeat([And('DOT', '2ALPHA')])),
        And(
            '5HEXDIG',
            Repeat('*3', [And('"::"', '5HEXDIG')]))),


    count_rule=Count('3*a', Char('*abcde')),
    count_rule_qs=Count('1*2"ab"', Char('*abcde')),
    count_rule_opt=Count('[3*a]', Char('*abcde')),

    len_rule=Len('2*4', Word('abcde')),
    len_rule_opt=Len('[2*4]', Word('abcde')),

    # Actions :


    p10_f20=ParserAction(pass_diag='pass_10', fail_diag='fail_20'),
    test_name=ParserAction(name='test_name'),
    fail_len=ParserAction(fail_diag='len_fail', pass_diag='len_pass'),
    fail_sb=ParserAction(fail_diag='has_sb', pass_diag='no_sb_there'),
    pre=ParserAction(pass_diag='pre_pass11', fail_diag='pre_fail101', name='pre'),
    post=ParserAction(pass_diag='post_pass11', fail_diag='post_fail101', name='post'),
    data=ParserAction(pass_diag='data_pass11', fail_diag='data_fail101', name='data'),
    osb=ParserAction(pass_diag='osb_pass11', fail_diag='osb_fail101', name='osb'),
    csb=ParserAction(pass_diag='csb_pass11', fail_diag='csb_fail101', name='csb'),



    m_rule_pass_fail=Char('"start"', actions=ParserAction(pass_diag=10, fail_diag=20)),

    m_rule_element_name=Repeat(Or('alpha', 'SPACE'), actions=('p10_f20, test_name')),

    multiple_marks_rule=Count('0/[]',
        Len('5',
            And(
                Opt('*-LTR_STR', actions='pre'),
                And(
                    Char('-OPENSQBRACKET', actions='osb'),
                    '*LTR_STR',
                    Char('-CLOSESQBRACKET', actions='csb'),
                    actions='data'),
                Opt('*-LTR_STR', actions='post')),
             actions=['p10_f20', 'fail_len']),
        actions='fail_sb'),

    next_withChars=Char('abcde', next='/fghi'),
    next_with_lookup=Char('abcde', next='HEXDIG'),
    next_with_rule=Char('abcde', next='char_rule_quoted_str'),
    next_with_opt_action_rule=Char('abcde', next='[m_rule_pass_fail]'),
    next_with_action_rule=Char('abcde', next='m_rule_pass_fail'),

    both_next_at=Char('@', actions=ParserAction(pass_diag='has_at', fail_diag='no_at')),
    both_next_dquote=Char('DQUOTE', actions=ParserAction(pass_diag='has_qt', fail_diag='no_qt')),

    both_next_rule=Char('abcde', next='both_next_at', not_next='both_next_dquote'),

)



TEST_DATA_RULES2 = dict(
    char_rule=Char('abcdef'),
    char_rule2='/abcdef',
    lookupChar_rule='ABCD',
    char_rule_quoted_str='"Foo"',
    char_rule_quoted_str_case_insensitive='^"Foo"',
    and_rule=And('/abcd', 'DEFG'),
    or_rule=Or(Char('abcd'), Char('jklm')),
    opt_rule=['/abcd'],
    opt_rule2='[/abcd]',
    c_rule=Repeat(2, Char('abcd')),
    c_rule_min=Repeat('2*', Char('abcd')),
    c_rule_max=Repeat('*2', Char('abcd')),
    c_rule_min_max=Repeat('2*3', Char('abcd')),
    c_rule_unl=Repeat('*', Char('abcd')),
    c_rule_unl2=Repeat(Char('abcd')),
    c_rule_inChar='2*ABCD',
    c_rule_mult_items=Repeat('2*3', And('/abcd', '/defg')),
    rule_rule=Rule('char_rule'),
    lookupChar=And('HEXDIG'),
    lookupChar_opt=And('HEXDIG', '[HEXDIG]'),
    quotedChar_str=And('HEXDIG', '"::"', 'HEXDIG'),
    quotedChar_str2=And(Repeat(3, Char('foo')), 'COMMA', '"bar"'),
    complex_and=And('*5LTR_STR', [And('DOT', '*5LTR_STR')]),

    complex_or=Or(Word('abcde', exact=5), Char('fghijk')),
    complex_and_or=Or(
        And(
            Word('ALPHA', max=5),
            [And('DOT', '*ALPHA')]),
        And(
            'HEXDIG',
            [And('"::"', 'HEXDIG')])),
    complex_and_or2=Or(
        And(
            '*5ALPHA',
            Repeat([And('DOT', '2ALPHA')])),
        And(
            '5HEXDIG',
            Repeat('*3', [And('"::"', '5HEXDIG')]))),


    count_rule=Count('3*a', Char('*abcde')),
    count_rule_qs=Count('1*2"ab"', Char('*abcde')),
    count_rule_opt=Count('[3*a]', Char('*abcde')),

    len_rule=Len('2*4', Word('abcde')),
    len_rule_opt=Len('[2*4]', Word('abcde')),

    # Actions :


    p10_f20=ParserAction(pass_diag='pass_10', fail_diag='fail_20'),
    test_name=ParserAction(name='test_name'),
    fail_len=ParserAction(fail_diag='len_fail', pass_diag='len_pass'),
    fail_sb=ParserAction(fail_diag='has_sb', pass_diag='no_sb_there'),
    pre=ParserAction(pass_diag='pre_pass11', fail_diag='pre_fail101', name='pre'),
    post=ParserAction(pass_diag='post_pass11', fail_diag='post_fail101', name='post'),
    data=ParserAction(pass_diag='data_pass11', fail_diag='data_fail101', name='data'),
    osb=ParserAction(pass_diag='osb_pass11', fail_diag='osb_fail101', name='osb'),
    csb=ParserAction(pass_diag='csb_pass11', fail_diag='csb_fail101', name='csb'),


    m_rule_pass_fail='("start"|:name:<10,20>)',

    # m_rule_pass_fail=Char('"start"', actions=ParserAction(pass_diag=10, fail_diag=20)),

    m_rule_element_name=Repeat(Or('alpha', 'SPACE'), actions=('p10_f20, test_name')),

    multiple_marks_rule=Count('0/[]',
        Len('5',
            And(
                Opt('*-LTR_STR', actions='pre'),
                And(
                    Char('-OPENSQBRACKET', actions='osb'),
                    '*LTR_STR',
                    Char('-CLOSESQBRACKET', actions='csb'),
                    actions='data'),
                Opt('*-LTR_STR', actions='post')),
             actions=['p10_f20', 'fail_len']),
        actions='fail_sb'),

    next_withChars=Char('abcde', next='/fghi'),
    next_with_lookup=Char('abcde', next='HEXDIG'),
    next_with_rule=Char('abcde', next='char_rule_quoted_str'),
    next_with_opt_action_rule=Char('abcde', next='[m_rule_pass_fail]'),
    next_with_action_rule=Char('abcde', next='m_rule_pass_fail'),

    both_next_at=Char('@', actions=ParserAction(pass_diag='has_at', fail_diag='no_at')),
    both_next_dquote=Char('DQUOTE', actions=ParserAction(pass_diag='has_qt', fail_diag='no_qt')),

    both_next_rule=Char('abcde', next='both_next_at', not_next='both_next_dquote'),

)


#rules = ParserOps(TEST_DATA_RULES, TEST_DATA_LOOKUPS, on_fail=2, on_rem_string=1, on_pass=0)

PASS = 0
FAIL = 2
REM = 1

TEST_SETS = [
    (1, 'char_rule', 'a', PASS, ''),
    (2, 'char_rule', 'h', FAIL, 'h'),
    (3, 'char_rule', 'abc', REM, 'bc'),
    (4, 'char_rule2', 'a', PASS, ''),
    (5, 'char_rule2', 'h', FAIL, 'h'),
    (6, 'char_rule2', 'abc', REM, 'bc'),
    (7, 'lookup_char_rule', 'a', PASS, ''),
    (8, 'lookup_char_rule', 'h', FAIL, 'h'),
    (9, 'lookup_char_rule', 'abc', REM, 'bc'),
    (10, 'char_rule_quoted_str', 'Foo', PASS, ''),
    (11, 'char_rule_quoted_str', 'Blah', FAIL, 'Blah'),
    (12, 'char_rule_quoted_str', 'Foobar', REM, 'bar'),
    (13, 'char_rule_quoted_str_case_insensitive', 'foo', PASS, ''),
    (14, 'char_rule_quoted_str_case_insensitive', 'FOO', PASS, ''),
    (15, 'char_rule_quoted_str_case_insensitive', 'foObar', REM, 'bar'),
    (16, 'and_rule', 'ad', PASS, ''),
    (17, 'and_rule', 'ha', FAIL, 'ha'),
    (18, 'and_rule', 'xx', FAIL, 'xx'),
    (19, 'and_rule', 'aa', FAIL, 'aa'),
    (20, 'and_rule', 'ade', REM, 'e'),
    (21, 'or_rule', 'a', PASS, ''),
    (22, 'or_rule', 'l', PASS, ''),
    (23, 'or_rule', 'z', FAIL, 'z'),
    (24, 'opt_rule', 'ax', REM, 'x'),
    (25, 'opt_rule', '', PASS, ''),
    (26, 'opt_rule2', 'ax', REM, 'x'),
    (27, 'opt_rule2', '', PASS, ''),
    (28, 'c_rule', 'ab', PASS, ''),
    (29, 'c_rule', 'abb', REM, 'b'),
    (30, 'c_rule', 'a', FAIL, 'a'),
    (31, 'c_rule_min', 'a', FAIL, 'a'),
    (32, 'c_rule_min', 'aa', PASS, ''),
    (33, 'c_rule_min', 'aaa', PASS, ''),
    (34, 'c_rule_max', 'a', PASS, ''),
    (35, 'c_rule_max', 'ax', REM, 'x'),
    (36, 'c_rule_max', 'aa', PASS, ''),
    (37, 'c_rule_max', 'aaa', REM, 'a'),
    (38, 'c_rule_min_max', 'a', FAIL, 'a'),
    (39, 'c_rule_min_max', 'ax', PASS, 'ax'),
    (40, 'c_rule_min_max', 'aa', PASS, ''),
    (41, 'c_rule_min_max', 'aaa', PASS, ''),
    (42, 'c_rule_min_max', 'aax', REM, 'x'),
    (43, 'c_rule_min_max', 'aaax', REM, 'x'),
    (44, 'c_rule_min_max', 'aaaa', REM, 'x'),
    (45, 'c_rule_in_char', 'a', FAIL, 'a'),
    (46, 'c_rule_in_char', 'aa', PASS, ''),
    (47, 'c_rule_in_char', 'aaa', PASS, ''),
    (48, 'c_rule_mult_items', 'ad', FAIL, 'ad'),
    (49, 'c_rule_mult_items', 'adbe', PASS, ''),
    (50, 'c_rule_mult_items', 'adbedf', PASS, ''),
    (51, 'c_rule_mult_items', 'adbexx', REM, 'xx'),
    (52, 'c_rule_unl', 'a', PASS, ''),
    (53, 'c_rule_unl', 'ax', REM, 'x'),
    (54, 'c_rule_unl', 'aa', PASS, ''),
    (55, 'c_rule_unl', 'aaa', PASS, ''),
    (56, 'c_rule_unl', 'aaabbbbbcccccdddddd', PASS, ''),
    (57, 'c_rule_unl2', 'a', PASS, ''),
    (58, 'c_rule_unl2', 'ax', REM, 'x'),
    (59, 'c_rule_unl2', 'aa', PASS, ''),
    (60, 'c_rule_unl2', 'aaa', PASS, ''),
    (61, 'c_rule_unl2', 'aaabbbbbcccccdddddd', PASS, ''),
    (62, 'rule_rule', 'a', PASS, ''),
    (63, 'rule_rule', 'h', FAIL, 'h'),
    (64, 'rule_rule', 'abc', REM, 'bc'),
    (65, 'lookup_char', 'a', PASS, ''),
    (66, 'lookup_char', '2', PASS, ''),
    (67, 'lookup_char', 'A', PASS, ''),
    (68, 'lookup_char', 'x', FAIL, 'x'),
    (69, 'lookup_char', 'ab', REM, 'b'),
    (70, 'lookup_char', 'xab', FAIL, 'xab'),
    (71, 'lookup_char_opt', 'a', PASS, ''),
    (72, 'lookup_char_opt', 'aa', PASS, ''),
    (73, 'lookup_char_opt', 'af', PASS, ''),
    (74, 'lookup_char_opt', 'aaaa', REM, 'aa'),
    (75, 'lookup_char_opt', 'xaxa', FAIL, 'xaxa'),
    (76, 'quoted_char_str', 'a::a', PASS, ''),
    (77, 'quoted_char_str', 'f::a', PASS, ''),
    (78, 'quoted_char_str', 'f::as', REM, 's'),
    (79, 'quoted_char_str', 'f', FAIL, 'f'),
    (80, 'quoted_char_str', 'f:a', FAIL, 'f:a'),
    (81, 'quoted_char_str2', 'foo,bar', PASS, ''),
    (82, 'quoted_char_str2', 'oof,bar', PASS, ''),
    (83, 'quoted_char_str2', 'oof,rab', FAIL, 'oof,rab'),
    (84, 'quoted_char_str2', 'ofo,bar', PASS, ''),
    (85, 'complex_and', 'abdxe', PASS, ''),
    (86, 'complex_and', 'abd', PASS, ''),
    (87, 'complex_and', 'abdxe.abcde', PASS, ''),
    (88, 'complex_and', 'abdxe.', REM, '.'),
    (89, 'complex_and', 'abdxeee', REM, 'ee'),
    (90, 'complex_and', 'abdxe.a', PASS, ''),
    (91, 'complex_and', 'abdxe.abcdev', REM, 'v'),
    (92, 'complex_or', 'abcde', PASS, ''),
    (93, 'complex_or', 'f', PASS, ''),
    (94, 'complex_or', 'abcd', FAIL, 'abcd'),
    (95, 'complex_or', 'abcdf', FAIL, 'abcdf'),
    (96, 'complex_or', 'ffff', REM, 'fff'),
    (97, 'complex_and_or', 'abdxe', PASS, ''),
    (98, 'complex_and_or', 'abd', PASS, ''),
    (99, 'complex_and_or', 'abdxe.abcde', PASS, ''),
    (100, 'complex_and_or', 'abdxe.', REM, '.'),
    (101, 'complex_and_or', 'abdxeee', REM, 'ee'),
    (102, 'complex_and_or', '123::a', REM, '23::a'),
    (103, 'complex_and_or', 'abdxe.abcdev', PASS, ''),
    (104, 'complex_and_or', '1::1', PASS, ''),
    (105, 'complex_and_or', ':z::z', FAIL, ':z::z'),
    (106, 'complex_and_or2', '1bcde', PASS, ''),
    (107, 'complex_and_or2', '1bcde::1bcde', PASS, ''),
    (108, 'complex_and_or2', '1bcde::1bcde::abcde', PASS, ''),
    (109, 'complex_and_or2', '1bcde::1bcde::abcde::abcde', PASS, ''),
    (110, 'complex_and_or2', '1bcde::1bcde::abcde::abcde::abcde', REM, '::abcde'),
    (111, 'complex_and_or2', 'abcdx', PASS, ''),
    (112, 'complex_and_or2', 'abcdxzz', REM, 'zz'),
    (113, 'complex_and_or2', 'xyzhk.a', REM, '.a'),
    (114, 'complex_and_or2', 'xyzhk.ab', PASS, ''),
    (115, 'complex_and_or2', 'xyzhk.ab.a', REM, '.a'),
    (116, 'complex_and_or2', 'xyzhk.ab.ax', PASS, ''),
    (117, 'complex_and_or2', 'xyzhk.ab.ax.ab.ab', PASS, ''),
    (118, 'complex_and_or2', 'xyzhk.ab.ax.ab.ab.ab.ab.', REM, '.'),
    (119, 'count_rule', 'a', FAIL, 'a'),
    (120, 'count_rule', 'aa', FAIL, 'aa'),
    (121, 'count_rule', 'aabcd', FAIL, 'aabcd'),
    (122, 'count_rule', 'aababa', PASS, ''),
    (123, 'count_rule_qs', 'a', FAIL, 'a'),
    (124, 'count_rule_qs', 'aa', FAIL, 'aa'),
    (125, 'count_rule_qs', 'aabcd', PASS, ''),
    (126, 'count_rule_qs', 'aababa', PASS, ''),
    (127, 'count_rule_qs', 'aababaab', FAIL, 'aababaab'),
    (128, 'count_rule_opt', 'a', PASS, ''),
    (129, 'count_rule_opt', 'aa', PASS, ''),
    (130, 'count_rule_opt', 'aabcd', PASS, ''),
    (131, 'count_rule_opt', 'aababa', PASS, ''),
    (132, 'count_rule_3_args', 'a', FAIL, 'a'),
    (133, 'count_rule_3_args', 'aa', FAIL, 'aa'),
    (134, 'count_rule_3_args', 'aabcd', FAIL, 'aabcd'),
    (135, 'count_rule_3_args', 'aababa', PASS, ''),
    (136, 'len_rule', 'a', FAIL, 'a'),
    (137, 'len_rule', 'aa', PASS, ''),
    (138, 'len_rule', 'aabc', PASS, ''),
    (139, 'len_rule', 'aababa', FAIL, 'aababa'),
    (140, 'len_rule_opt', 'a', PASS, ''),
    (141, 'len_rule_opt', 'aa', PASS, ''),
    (142, 'len_rule_opt', 'aabc', PASS, ''),
    (143, 'len_rule_opt', 'aababa', PASS, ''),
    (144, 'm_rule_pass_fail', 'a', 'pass_10', '', {}, {'pass_10': [1]}),
    (145, 'm_rule_pass_fail', 'x', 'fail_20', 'x', {}, {'fail_20': [0]}),
    (146, 'm_rule_element_name', 'aaa', 'pass_10', '', {'test_name': (('aaa', 0),)}),
    (147, 'm_rule_element_name', 'start this now', 'pass_10', '', {'test_name': (('start this now', 0),)}),
    (148, 'm_rule_element_name', 'aaa-aa', REM, '-aa', {'test_name': (('aaa', 0),)}),
    (149, 'next_with_chars', 'a', FAIL, 'a'),
    (150, 'next_with_chars', 'af', REM, 'f'),
    (151, 'next_with_lookup', 'af', REM, 'f'),
    (152, 'next_with_rule', 'aFoo', REM, 'Foo'),
    (153, 'next_with_action_rule', 'astart', 'pass_10', 'start'),
    (154, 'next_with_opt_action_rule', 'astart', 'pass_10', 'start'),
    (155, 'next_with_opt_action_rule', 'ablah', 'fail_20', 'blah'),
    (158, 'both_next_rule', 'a', FAIL, 'a', {}, {}),
    (159, 'both_next_rule', 'a@', REM, '@', {}, {'has_at': [1]}),
    (160, 'both_next_rule', 'a"', FAIL, '"', {}, {'has_qt': [1]}),
    (161, 'multiple_marks_rule', 'foo[bar]blah', 15, '',
        {'pre': (('foo', 0),), 'post': (('blah', 8),), 'data': (('bar', 5),)},
        {'pass': [12],
         'pre_pass': [0],
         'post_pass': [7],
         'csb_pass': [7],
         'osb_pass': [3],
         'data': [8]}),
    (162, 'multiple_marks_rule', 'foo/[bar]blah', 2, 'foo/[bar]blah', {'pre': (('foo', 0),)}, {}),
    (163, 'multiple_marks_rule', 'foo[barblah', 2, 'foo[barblah', {'pre': (('foo', 0),)}, {}),
    (164, 'multiple_marks_rule', '[bar]', 0, '', {'data': (('bar', 0),)}, {}),
    (165, 'multiple_marks_rule', '[bar]foo', 0, '', {'data': (('bar', 0),), 'post': (('foo', 5),)}, {}),

]

RUN_TEST_NUM = 2

class TestParser(unittest.TestCase):
    maxDiff = None

    def test_sets(self):
        for test in TEST_SETS:
            if RUN_TEST_NUM is None or RUN_TEST_NUM == test[0] or (isinstance(RUN_TEST_NUM, (list, tuple, range)) and test[0] in RUN_TEST_NUM):
                # print('--------------------')
                # print('[%s] RUN %s(%s)' % (test[0], test[1], test[2]))
                # print('--------------------\n')
                pem = None
                with self.subTest('[%s] RUN %s(%s)' % (test[0], test[1], test[2])):
                    pem = rules(test[2], test[1])
                    # pem = ParseString(parser=rules.parse_str, parser_start_rule=test[1])
                    tmp_resp = int(pem)
                    self.assertEqual(test[3], tmp_resp)
                if pem is not None:

                    with self.subTest('[%s] REM %s(%s)' % (test[0], test[1], test[2])):
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

