import unittest

from isemail_parsers import _and, _or, _c, _char, _for, _look, _m, _make_meth, _opt, _rule, ParserOps
from py_is_email import ParseEmail, ParserRule

TEST_SET_simple = dict(
    start=_char('abcdef'),
    and_rule=_and(_char('abcd'), _char('defg')),
    or_rule=_or(_char('abcd'), _char('jklm'))
)



rules = ParserOps(TEST_SET_simple)


class TestOperations(unittest.TestCase):
    def test_char(self):
        pem = ParseEmail(parser=rules.parse_gen, parser_start_rule='and_rule')

        tmp = pem('ag')

        print(tmp)


