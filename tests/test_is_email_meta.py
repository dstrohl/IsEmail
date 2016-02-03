import unittest

from isemail_parsers import _and, _or, _c, _char, _for, _look, _m, _make_meth, _opt, _rule, ParserOps
from py_is_email import ParseEmail, ParserRule, ParseString


TEST_DATA_RULES = dict(
    start=_char('abcdef'),
    and_rule=_and(_char('abcd'), _char('defg')),
    or_rule=_or(_char('abcd'), _char('jklm')),
    opt_rule=_opt(_char('abcd')),
    c_rule=_c(2, _char('abcd')),
    c_rule_min=_c('2*', _char('abcd')),
    c_rule_max=_c('*2', _char('abcd')),
    c_rule_unl=_c('*', _char('abcd')),
    c_rule_unl2=_c(_char('abcd')),
    m_rule=_m(_char('abcd')),
    m_rule_pass_fail=_m('start', on_fail=20, on_pass=10),
    m_rule_element_name=_m('start', element_name='test_name'),
    look_rule=_look(_char('abcd'), _for(_char('%', on_pass=10, on_fail=20))),
    rule_rule=_rule('start'),
    lookup_char=_and('HEXDIG'),
    lookup_char_opt=_and('HEXDIG', '[HEXDIG]'),
    quoted_char_str=_and('HEXDIG', '"::"', 'HEXDIG')
    
)

rules = ParserOps(TEST_DATA_RULES, on_fail=2, on_rem_string=1)

TEST_SETS = [
    (1, 'start', 'a', 0),
    (2, 'start', 'h', 2),
    (2, 'start', 'abc', 1),
    (2, 'and_rule', 'ad', 0),
    (2, 'and_rule', 'ha', 2),
    (2, 'and_rule', 'xx', 2),
    (2, 'and_rule', 'aa', 2),
    (2, 'and_rule', 'ade', 1),
    (2, 'or_rule', 'a', 0),
    (2, 'or_rule', 'l', 0),
    (2, 'or_rule', 'z', 2),
    (2, 'opt_rule', 'a', 1),
    (2, 'opt_rule', '', 0),
    (1, 'm_rule', 'a', 0),
    (2, 'm_rule', 'h', 2),
    (2, 'm_rule', 'abc', 1),
    (1, 'c_rule', 'ab', 0),
    (2, 'c_rule', 'abb', 1),
    (2, 'c_rule', 'a', 2),
    (2, 'c_rule_min', 'a', 2),
    (2, 'c_rule_min', 'aa', 0),
    (2, 'c_rule_min', 'aaa', 1),
    (2, 'c_rule_max', 'a', 0),
    (2, 'c_rule_max', 'ax', 1),
    (2, 'c_rule_max', 'aa', 0),
    (2, 'c_rule_max', 'aaa', 1),
    (2, 'c_rule_unl', 'a', 0),
    (2, 'c_rule_unl', 'ax', 1),
    (2, 'c_rule_unl', 'aa', 0),
    (2, 'c_rule_unl', 'aaa', 0),
    (2, 'c_rule_unl', 'aaabbbbbcccccdddddd', 0),
    (2, 'c_rule_unl2', 'a', 0),
    (2, 'c_rule_unl2', 'ax', 1),
    (2, 'c_rule_unl2', 'aa', 0),
    (2, 'c_rule_unl2', 'aaa', 0),
    (2, 'c_rule_unl2', 'aaabbbbbcccccdddddd', 0),
    (1, 'rule_rule', 'a', 0),
    (2, 'rule_rule', 'h', 2),
    (2, 'rule_rule', 'abc', 1),
    (1, 'lookup_char', 'a', 0),
    (2, 'lookup_char', '2', 0),
    (2, 'lookup_char', 'A', 0),
    (1, 'lookup_char', 'x', 2),
    (2, 'lookup_char', 'ab', 1),
    (2, 'lookup_char', 'xab', 2),
    (1, 'lookup_char_opt', 'a', 0),
    (2, 'lookup_char_opt', 'aa', 0),
    (2, 'lookup_char_opt', 'af', 0),
    (1, 'lookup_char_opt', 'aaaa', 1),
    (2, 'lookup_char_opt', 'axa', 2),
    (1, 'lookup_char_str', 'a::a', 0),
    (2, 'lookup_char_str', 'f::a', 0),
    (2, 'lookup_char_str', 'f::as', 2),
    (2, 'lookup_char_str', 'f', 2),
    (2, 'lookup_char_str', 'f:a', 2),
    (2, 'm_rule_pass_fail', 'a', 10),
    (2, 'm_rule_pass_fail', 'x', 20),

]

'''

    m_rule_element_name=_m('start', element_name='test_name'),
    look_rule=_look(_char('abcd'), _for(_char('%', on_pass=10, on_fail=20))),

'''

class TestParser(unittest.TestCase):

    def test_sets(self):
        for test in TEST_SETS:
            with self.subTest('[%s] %s(%s)' % (test[0], test[1], test[2])):
                pem = ParseString(parser=rules.parse_str, parser_start_rule=test[1])
                tmp_resp = pem(test[2])
                self.assertEqual(test[3], tmp_resp)