from parse_email import *
from unittest import TestCase
from tests.validator_inet_test_data import *

PYPARSING_EMAIL_OBJECT_TESTS = [
    (1, AT, '@'),
    (2, BACKSLASH, '\\'),
    (3, AT, '@'),
    (4, BACKSLASH, '\\'),
    (5, CLOSEPARENTHESIS, ')'),
    (6, CLOSESQBRACKET, ']', ''),
    (7, COLON, ':'),
    (8, CR, '\r'),
    (9, DOT, '.'),
    (10, DOUBLECOLON, '::'),
    (11, DQUOTE, '"', ''),
    (12, HTAB, make_char_str(9)),
    (13, HYPHEN, '-'),
    (14, IPV6TAG, 'ipv6:'),
    (15, LF, '\x0A'),
    (16, OPENPARENTHESIS, '('),
    (17, OPENSQBRACKET, '[', ''),
    (18, SP, ' '),
    (19, N1, '1'),
    (20, N2, '2'),
    (21, N5, '5'),
    (22, CRLF, '\x0D'),
    (23, CRLF, '\x0A'),
    (24, CRLF, '\r\n'),
    (25, DIGIT, '1'),
    (26, DIGIT, '2'),
    # (27, DIGIT, 'x', ''),
    #(28, DIGIT, '23', '2'),
    (29, HEXDIG, '1234'),
    (30, HEXDIG, '5678'),
    (31, HEXDIG, 'ab23'),
    (32, snum, '1'),
    (33, snum, '100'),
    (34, snum, '200'),
    (35, snum, '234'),
    (36, snum, '255'),
    (37, snum, '34'),
    (38, snum, '99'),
    (39, snum, '209'),
    (40, dot_snum, '.1'),
    (41, dot_snum, '.100'),
    (42, dot_snum, '.200'),
    (43, dot_snum, '.234'),
    (44, dot_snum, '.255'),
    (45, dot_snum, '.34'),
    (46, dot_snum, '.99'),
    (47, dot_snum, '.209'),
    (48, ipv4_address_lit_base, '1.1.1.1'),
    (49, ipv4_address_lit_base, '255.255.255.255'),
    (50, ipv4_address_lit_base, '1.10.100.200'),
    (51, standard_tag, 'abcde12345'),
    (52, general_address_literal, 'test:abcdefg'),
    (53, ipv6_colon_hex, ':1'),
    (54, ipv6_colon_hex, ':1a'),
    (55, ipv6_colon_hex, ':1ab'),
    (56, ipv6_colon_hex, ':1334'),
    (57, ipv6_full, '1234:1334:1234:1234:1234:1334:1234:1234'),
    (57, ipv6v4_full, '1234:1334:1234:1234:1234:1234:1.2.3.4'),
    (60, ipv6v4_comp, '1:2:3:4::5:1.2.3.4'),

    (61, addr_lit, '1.2.3.4', None, {'ipv4_address_literal': '1.2.3.4'}),
    (62, addr_lit, 'ipv6:1:2:3:4:5:6:7:8', None, {'ipv6_address_literal': '1:2:3:4:5:6:7:8'}),
    (63, addr_lit, 'test:text', None, {'general_address_literal': 'test:text'}),

    (64, address_literal, '[1.2.3.4]', '1.2.3.4', {'ipv4_address_literal': '1.2.3.4'}),
    (65, address_literal, '[ipv6:1:2:3:4:5:6:7:8]', 'ipv6:1:2:3:4:5:6:7:8', {'ipv6_address_literal': '1:2:3:4:5:6:7:8'}),
    (66, address_literal, '[test:text]', 'test:text', {'general_address_literal': 'test:text'}),

    (67, DTEXT_CHARS, 'abcdefg'),
    (68, DTEXT_CHARS, 'abcdefg+!@#$%^&*()'),
    (69, DTEXT_CHARS, 'abcdefg""-=+'),

    (70, VCHAR, 'abcdefg[]'),
    (71, VCHAR, 'abcdefg+!@#$%^&*()'),
    (72, VCHAR, 'abcdefg""-=+\\'),

    (73, QTEXT, 'abcdefg'),
    (74, QTEXT, 'abcdefg+!@#$%^&*()'),
    (75, QTEXT, 'abcdefg-=+'),

    (76, CTEXT, 'abcdefg'),
    (77, CTEXT, 'abcdefg+!@#$%^&*[]'),
    (78, CTEXT, 'abcdefg-=+"'),

    (79, DCONTENT, 'abcdefg'),
    (80, DCONTENT, 'abcdefg+!@#$%^&*()'),
    (81, DCONTENT, 'abcdefg""-=+'),

    (79, ATEXT, 'abcdefg'),
    (80, ATEXT, 'abcdefg+!#$%^&*'),
    (81, ATEXT, 'abcdefg-=+'),

    (82, quoted_pair, '\\1', '1'),
    (83, quoted_pair, '\\<', '<'),

    (84, obs_qp, '\\\x0D', '\x0D'),  # , {'obs_qp': '\x0D'})

    (85, fws, ' ', ''),
    (86, fws, '\t', ''),

    (87, fws, ' \x0D ', ''),
    (88, fws, '\t\x0A ', ''),
    (89, fws, '  \x0D ', ''),
    (89, fws, '  \x0D ', ''),
    (89, fws, '  \x0D ', ''),
    (90, fws, '\x0D \x0D \x0D ', ''),
    (91, comment, '(abcdefg)'),   # , None, {'comment': '(abcdefg)'})
    (92, comment, '(abc\\(defg)', '(abc(defg)'),
    (93, comment, '(abc(d)efg)', '(abc(d)efg)'),


    # (94, quoted_string, '"abcdefg"', 'abcdefg'),



]


"""

qcontent                = QTEXT | quoted_pair
quoted_string           = cfws + DQUOTE + OneOrMore(opt_fws + qcontent) + opt_fws + DQUOTE + cfws
dot_atom_text           = OneOrMore(ATEXT) + ZeroOrMore(DOT + ATEXT)
dot_atom                = cfws + dot_atom_text + cfws
atom                    = cfws + ATEXT + cfws
word                    = atom | quoted_string
obs_local_part          = word + ZeroOrMore(DOT + word)

obs_domain              = atom + ZeroOrMore(DOT + atom)

domain_literal          = cfws + OPENSQBRACKET + ZeroOrMore(opt_fws + DTEXT) + opt_fws + CLOSESQBRACKET + cfws

domain_part             = dot_atom | domain_literal | address_literal | obs_domain
local_part              = dot_atom | quoted_string | obs_local_part
addr_spec               = local_part + AT + domain_part


"""

PYPARSING_EMAIL_OBJECT_FAIL_TESTS = [
    (10, dot_snum, '.444'),
    (11, standard_tag, '1.10.100.300'),
    (12, standard_tag, 'abcdef--x`'),
    (13, general_address_literal, 'test/abcdef1'),
    (14, ipv6_colon_hex, ':1xc'),
    (15, ipv6_colon_hex, ':1addd'),
    (16, ipv6_colon_hex, ':'),
    (18, ipv6_full, '1234:1334:1234:1234:1234:1334:1234:1234:1234'),
    (19, ipv6_full, 'FF02:0000:0000:0000:0000:0000:0000:0000:0001'),
    (20, ipv6_comp, '1234:1334::1234:1234:1334:1234:1234'),
    (21, ipv6_comp, '1111:2222:3333:4444::6666:7777:8888'),
    (22, DTEXT_CHARS, '[blah]'),
    (23, DTEXT_CHARS, '\\foobar'),
    (24, VCHAR, ' foobar'),

    (25, QTEXT, '"blah"'),
    (26, QTEXT, '\\foobar'),
    (27, CTEXT, '(blah)'),
    (28, CTEXT, '\\foobar'),

    (29, DCONTENT, '[blah]'),
    (30, DCONTENT, '\\foobar'),

    (31, ATEXT, '('),
    (32, ATEXT, ')'),
    (33, ATEXT, '<'),
    (34, ATEXT, '>'),
    (35, ATEXT, '['),
    (36, ATEXT, ']'),
    (37, ATEXT, ':'),
    (38, ATEXT, ';'),
    (39, ATEXT, '@'),
    (40, ATEXT, '\\'),
    (41, ATEXT, ','),
    (42, ATEXT, '.'),
    (43, ATEXT, '"'),

    (44, quoted_pair, '\\'),
    (45, fws, 'a'),
    (46, fws, '   \x0D\x0D  \t'),
    (47, fws, '[]'),
    (48, comment, 'abcde'),
    # (49, quoted_string, 'abcde'),

]

"""

1:2:3:4:5:6:7:8

remove 2
::3:4:5:6:7:8
1::4:5:6:7:8
1:2::5:6:7:8
1:2:3::6:7:8
1:2:3:4::7:8
1:2:3:4:5::8
1:2:3:4:5:6::

remote 3
::4:5:6:7:8
1::5:6:7:8
1:2::6:7:8
1:2:3::7:8
1:2:3:4::8
1:2:3:4:5::

remove 4:
::5:6:7:8
1::6:7:8
1:2:3::8
1:2:3:4::


remove 5:
::6:7:8
1::7:8
1:2::8
1:2:3::


remove 6:

::7:8
1::8
1:2::

remove 7:
::8
1::

remove 8:
::


v4v6:


remove 2
1:2:3:4:5:6:1.2.3.4
::3:4:5:6:6:1.2.3.4
1::4:5:6:6:1.2.3.4
1:2::5:6:6:1.2.3.4
1:2:3::6:6:1.2.3.4
1:2:3:4::6:1.2.3.4

remote 3
::4:5:6:6:1.2.3.4
1::5:6:6:1.2.3.4
1:2::6:6:1.2.3.4
1:2:3::6:1.2.3.4
1:2:3:4::1.2.3.4

remove 4:
::5:6:1.2.3.4
1::6:1.2.3.4
1:2::1.2.3.4


remove 5:
::6:1.2.3.4
1::1.2.3.4


remove 6:

::1.2.3.4


"""

PARSING_STUFF_TEST_NUM = None

PARSING_STUFF_FAIL_TEST_NUM = None

PARSING_IPADDR_NUM = None

class TestPyParsingStuff(TestCase):


    maxDiff = None
    '''
    def test_numbers(self):

        for i in range(2000):
            s_i = str(i)
            # snum.setDebug(True)
            with self.subTest(s_i):
                if -1 < i < 256:
                    test_snum = Combine(snum)
                    returned = test_snum.parseString(s_i, parseAll=True)
                    self.assertEqual(returned[0], s_i)
                else:

                    with self.assertRaises(ParseBaseException):
                        returned = snum.parseString(s_i, parseAll=True)
                        self.assertEqual(returned[0], '')
    '''
    def test_items(self):
        for t in PYPARSING_EMAIL_OBJECT_TESTS:
            if PARSING_STUFF_TEST_NUM is None or PARSING_STUFF_TEST_NUM == t[0]:
                if PARSING_STUFF_TEST_NUM is not None:
                    t[1].setDebug(True)
                else:
                    t[1].setDebug(False)

                test_str = t[2]
                expected = t[2]

                if len(t) > 3 and t[3] is not None:
                    test_str = t[2]
                    expected = t[3]

                with self.subTest('%s:  %r' % (t[0], t[1])):
                    test_obj = Combine(t[1]).leaveWhitespace().parseWithTabs()

                    returned = test_obj.parseString(test_str, parseAll=True)
                    if returned[0] != expected:
                        print('returned[0]:  ', returned[0], 'expected: ', expected)
                        print(returned.dump(), '\n', '\n')
                    self.assertEqual(returned[0], expected)

                    if len(t) > 4:
                        with self.subTest('%s-TOKENS:  %r' % (t[0], t[1])):
                            tmp_results = flatten_results(returned)
                            for key, item in t[4].items():
                                try:
                                    tmp_ret = tmp_results[key]
                                except KeyError:

                                    print(key, ':', item, ' not in ', tmp_results)
                                    print('from:', returned.dump())
                                else:
                                    if tmp_ret != item:
                                        print('dump: (tmp_ret=%r)' % tmp_ret)
                                        print(returned.dump())
                                self.assertEqual(tmp_results[key], item)

    '''

    def test_fails(self):
        for t in PYPARSING_EMAIL_OBJECT_FAIL_TESTS:
            if PARSING_STUFF_FAIL_TEST_NUM is None or PARSING_STUFF_FAIL_TEST_NUM == t[0]:
                if PARSING_STUFF_FAIL_TEST_NUM is not None:
                    t[1].setDebug(True)
                else:
                    t[1].setDebug(False)

                with self.subTest('%s:  %r' % (t[0], t[1])):
                    with self.assertRaises(ParseException):
                        test_obj = Combine(t[1]).leaveWhitespace().parseWithTabs()

                        returned = test_obj.parseString(t[2], parseAll=True)
                        self.assertEqual(returned[0], '')


    def test_ip_addresses(self):

        for addr in IP_ADDRESS_BASIC_TESTS:
            if PARSING_IPADDR_NUM is None or PARSING_IPADDR_NUM == int(addr['name']):
                if PARSING_IPADDR_NUM is not None:
                    debug_flag = True
                    ipv4_address_lit_base.setDebug(True)
                    ipv6_addr.setDebug(True)
                else:
                    debug_flag = False
                    ipv4_address_lit_base.setDebug(False)
                    ipv6_addr.setDebug(False)
                if addr['valid_v4']:
                    with self.subTest('%s: V4-Valid: %s' % (addr['name'], addr['test_value'])):
                        tmp_ret = ipv4_address_lit_base.parseString(addr['test_value'], parseAll=True)
                        if debug_flag:
                            print('%r' % tmp_ret)
                        self.assertEqual(tmp_ret[0], addr['test_value'])
                else:
                    with self.subTest('%s: V4-Invalid: %s' % (addr['name'], addr['test_value'])):
                        with self.assertRaises(ParseException):
                            tmp_ret = ipv4_address_lit_base.parseString(addr['test_value'], parseAll=True)
                            self.assertNotEqual(tmp_ret[0], addr['test_value'])
                if debug_flag:
                    print('')
                if addr['valid_v6']:
                    with self.subTest('%s: V6-Valid: %s' % (addr['name'], addr['test_value'])):
                        tmp_ret = ipv6_addr.parseString(addr['test_value'], parseAll=True)
                        if debug_flag:
                            print('%r' % tmp_ret)
                        self.assertEqual(tmp_ret[0], addr['test_value'])
                else:
                    with self.subTest('%s: V6-Invalid: %s' % (addr['name'], addr['test_value'])):
                        with self.assertRaises(ParseException):
                            tmp_ret = ipv6_addr.parseString(addr['test_value'], parseAll=True)
                            self.assertNotEqual(tmp_ret[0], addr['test_value'])

    '''
