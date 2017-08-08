from unittest import TestCase
from ValidationParser.tests.parser_test_helper import ParserTests
from ip_validator.is_ip import is_ipv6, is_ipv4, is_ip


ipv4_data = {'data': {'ip_version': 'IPv4'}}
ipv6_data = {'data': {'ip_version': 'IPv6'}}
ipv64_data = {'data': {'ip_version': 'IPv6-4'}}
ipv6_unspec_msg = ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED', 'IP_NOT_GLOBALLY_REACHABLE', 'IPV6_SPEC_UNSPECIFIED']

class TestIPAddresses(TestCase):

    # def run_parser_tests(self, tests, limit_to=None):
    #     if limit_to is not None:
    #         with self.subTest('LIMITED TEST'):
    #             self.fail('LIMITED_TEST')
    #
    #     for test in tests:
    #         if limit_to is None or limit_to == test.test_id:
    #             with self.subTest(str(test)):
    #                 tmp_ret, tmp_msg = test()
    #                 self.assertTrue(tmp_ret, tmp_msg)

    def test_ipv4_address(self):
        td = ParserTests(
            parse_script=is_ipv4,
            tests=[
                (1, '1.1.1.1', ipv4_data),
                (2, '123.123.123.123', ipv4_data),
                (3, '13.13.250.0', ipv4_data),
                (4, '255.255.255.255', ['IP_CANNOT_BE_FORWARDED', 'IP_CANNOT_BE_SOURCE',
                                            'IP_NOT_GLOBALLY_REACHABLE', 'IPV4_SPEC_BCAST'], 'w', ipv4_data),
                (5, '0.0.0.0', [('ipv4_address', ('IP_CANNOT_BE_DEST',
                                                      'IP_CANNOT_BE_FORWARDED',
                                                      'IP_NOT_GLOBALLY_REACHABLE',
                                                      'IPV4_SPEC_THIS_HOST'))], 'w', ipv4_data),
                (6, '0.0.0.0.', 0, ['IPV4_NOT_4_OCTETS'], 'e'),
                (7, '.0.0.0.0', 0, ['IPV4_NOT_4_OCTETS'], 'e'),
                (8, '1.2.3', 0, ['IPV4_NOT_4_OCTETS'], 'e'),
                (9, '200.2.1.1'),
                (10, '300.2.1.1', 0, ['IPV4_OCTAL_ABOVE_255'], 'e'),
                (11, '127.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED',
                                      'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                      'IPV4_SPEC_LOOPBACK'], 'w', ipv4_data),
                (12, '240.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED',
                                      'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                      'IPV4_SPEC_RESERVED'], 'w', ipv4_data),
                (13, 'blah', 0, [], 'e'),

                (51, '0:0:0:0:0:0:0:0', 0, ['IPV4_NOT_4_OCTETS']),
                (52, '1111:1111:1111:1111:1111:1111:1111:1111', 0, ['IPV4_NOT_4_OCTETS']),
                (53, '12ab:abcd:fedc:1212:0:00:000:0', 0, ['IPV4_NOT_4_OCTETS']),
            ]
        )

        LIMIT_TO = None
        # LIMIT_TO = 13

        LIMIT_RET_TYPE = None
        # LIMIT_RET_TYPE = 'long'

        for test in td.items(limit_to=LIMIT_TO, limit_ret_type=LIMIT_RET_TYPE):
            with self.subTest(str(test)):
                self.assertTrue(*test())

    def test_ipv6_comp(self):
        td = ParserTests(
            parse_script=is_ipv6,
            tests=[
                
                (1, '0::0:0:0:0:0', 12, ipv6_unspec_msg, 'w', ipv6_data),
                (2, '0::0:0:0:0', 10, ipv6_unspec_msg, 'w', ipv6_data),
                (3, '0::0:0:0', 8, ipv6_unspec_msg, 'w', ipv6_data),
                (4, '0::0:0', 6, ipv6_unspec_msg, 'w', ipv6_data),
                (5, '0::0', 4, ipv6_unspec_msg, 'w', ipv6_data),

                (6, '0:0::0:0:0:0', 12, ipv6_unspec_msg, 'w', ipv6_data),
                (7, '0:0::0:0:0', 10, ipv6_unspec_msg, 'w', ipv6_data),
                (8, '0:0::0:0', 8, ipv6_unspec_msg, 'w', ipv6_data),
                (9, '0:0::0', 6, ipv6_unspec_msg, 'w', ipv6_data),

                (10, '0:0:0::0:0:0', 12, ipv6_unspec_msg, 'w', ipv6_data),
                (11, '0:0:0::0:0', 10, ipv6_unspec_msg, 'w', ipv6_data),
                (12, '0:0:0::0', 8, ipv6_unspec_msg, 'w', ipv6_data),

                (13, '0:0:0:0::0:0', 12, ipv6_unspec_msg, 'w', ipv6_data),
                (14, '0:0:0:0::0', 10, ipv6_unspec_msg, 'w', ipv6_data),

                (15, '0:0:0:0:0::0', 12, ipv6_unspec_msg, 'w', ipv6_data),

                # ipv6 comp - FAIL
                (16, '0::0:0:0:0:0:0:0', 0, ['IPV6_TOO_MANY_PARTS_WITH_DCOLON']),
                (17, '::0:0:0:0::0:0:0:0', 0, ['IPV6_AT_MOST_8_COLONS']),
                (18, '0::0:0:0:0::0:0:0', 0, ['IPV6_AT_MOST_8_COLONS']),
                (19, ':::0:0:0:0:0:0:0', 0, ['IPV6_AT_MOST_8_COLONS']),
                (20, '0:0:0:0:0:0:0:0::', 0, ['IPV6_AT_MOST_8_COLONS']),
                
            ]
        )

        LIMIT_TO = None
        # LIMIT_TO = '004'

        LIMIT_RET_TYPE = None
        # LIMIT_RET_TYPE = 'long'

        for test in td.items(limit_to=LIMIT_TO, limit_ret_type=LIMIT_RET_TYPE):
            with self.subTest(str(test)):
                self.assertTrue(*test())

    def test_ipv6_full(self):
        td = ParserTests(
            parse_script=is_ipv6,
            tests=[
                # ipv6 full  - PASS
                (1, '0:0:0:0:0:0:0:0', ipv6_unspec_msg, 'w', ipv6_data),
                (2, '1111:1111:1111:1111:1111:1111:1111:1111', ['IP_NOT_GLOBALLY_REACHABLE', 'IPV6_SPEC_RESERVED'], 'w', ipv6_data),
                (3, '12ab:abcd:fedc:1212:0:00:000:0', ['IP_NOT_GLOBALLY_REACHABLE', 'IPV6_SPEC_RESERVED'], 'w', ipv6_data),

                # ipv6 full  - FAIL
                (4, '0:0:0:0:0:0:hhy:0', 0, ['IPV6_TOO_FEW_OR_MANY_PARTS']),
                (5, ':1111:1111:1111:1111:1111:1111:1111:1111', 0, ['IPV6_TOO_FEW_OR_MANY_PARTS']),
                (6, '12aba:1abcd:fedc:1212:0:00:000:0', 0, ['IPV6_TOO_MANY_CHARS_IN_SEGMENT']),

                (7, 'f000:0:0:0:0:1:0:1', ['IPV6_SPEC_RESERVED', 'IP_NOT_GLOBALLY_REACHABLE'], 'w', ipv6_data),
                (8, 'f800:0:0:0:0:0:0:0', ['IPV6_SPEC_RESERVED', 'IP_NOT_GLOBALLY_REACHABLE'], 'w', ipv6_data),
                (9, 'fc00:0:0:0:0:0:1:0', ['IPV6_SPEC_UNIQUE_LOCAL', 'IP_NOT_GLOBALLY_REACHABLE'], 'w', ipv6_data),
                (10, 'fe80:0:0:0:0:0:0:0', ['IPV6_SPEC_LINK_LOCAL', 'IP_NOT_GLOBALLY_REACHABLE','IP_CANNOT_BE_FORWARDED'], 'w', ipv6_data),
                (11, 'fec0:0:0:0:0:1:0:0', ['IPV6_SPEC_SITE_LOCAL', 'IP_NOT_GLOBALLY_REACHABLE'], 'w', ipv6_data),
                (12, 'ff10:0:0:0:0:1:0:0', ['IPV6_SPEC_MULTICAST', 'IP_NOT_GLOBALLY_REACHABLE', 'IP_CANNOT_BE_SOURCE'], 'w', ipv6_data),
                (50, '1.1.1.1', 0, ['IPV6_AT_LEAST_2_COLONS']),
                (51, '123.123.123.123', 0, ['IPV6_AT_LEAST_2_COLONS']),
                (52, '13.13.250.0', 0, ['IPV6_AT_LEAST_2_COLONS']),
                (53, '255.255.255.255', 0, ['IPV6_AT_LEAST_2_COLONS']),
                (54, '0.0.0.0', 0, ['IPV6_AT_LEAST_2_COLONS']),
            ]
        )

        LIMIT_TO = None
        # LIMIT_TO = 7

        LIMIT_RET_TYPE = None
        # LIMIT_RET_TYPE = 'long'

        for test in td.items(limit_to=LIMIT_TO, limit_ret_type=LIMIT_RET_TYPE):
            with self.subTest(str(test)):
                self.assertTrue(*test())

    def test_ipv6v4_full(self):
        td = ParserTests(
            parse_script=is_ipv6,
            tests=[
                # ipv6-4 - PASS
                (1, '0:0:0:0:0:0:1.1.1.1', 19, ['IP_NOT_GLOBALLY_REACHABLE', 'IPV6_SPEC_RESERVED'], 'w', ipv64_data),

                (2, '0:0:0:0:0:0:255.255.255.255', ['IP_CANNOT_BE_FORWARDED', 'IP_CANNOT_BE_SOURCE', 'IPV6_SPEC_RESERVED',
                                                        'IP_NOT_GLOBALLY_REACHABLE', 'IPV4_SPEC_BCAST'], 'w', ipv64_data),
                (3, '0:0:0:0:0:0:127.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED', 'IPV6_SPEC_RESERVED',
                                                  'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                                  'IPV4_SPEC_LOOPBACK'], 'w', ipv64_data),
                (4, '0:0:0:0:0:0:240.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED', 'IPV6_SPEC_RESERVED',
                                                  'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                                  'IPV4_SPEC_RESERVED'], 'w', ipv64_data),

                # ipv64 - FAIL
                (10, '0:0:0:0:0:0:300.2.1.1', 0, ['IPV4_OCTAL_ABOVE_255'], 'e'),
                (11, ':0:0:0:0:0:1.1.1.1', 0, ['IPV6_DCOLON_MUST_NOT_BE_FIRST']),
                (12, '0:0:0:0:0:0:1:1.1.1.1', 0, ['IPV6_TOO_FEW_OR_MANY_PARTS']),
                (13, '0:0:0:0:0:0:1.1.1.1.1.1', 0, ['IPV4_NOT_4_OCTETS']),

                (14, '0:0:0:0:0:0:1.1.1', 0, ['IPV4_NOT_4_OCTETS']),
                (15, '0:0:0:0:0:0:1.1', 0, ['IPV4_NOT_4_OCTETS']),
                (16, '0:0:0:0:0:0:1.abc.1', 0, ['IPV4_NOT_4_OCTETS']),


            ]
        )

        LIMIT_TO = None
        # LIMIT_TO = 2

        LIMIT_RET_TYPE = None
        # LIMIT_RET_TYPE = 'long'

        for test in td.items(limit_to=LIMIT_TO, limit_ret_type=LIMIT_RET_TYPE):
            with self.subTest(str(test)):
                self.assertTrue(*test())

    def test_ipv6v4_comp(self):
        td = ParserTests(
            parse_script=is_ipv6,
            tests=[
                # ipv6-4 - PASS
                (1, '0:0::0:0:1.1.1.1', 19, ['IP_NOT_GLOBALLY_REACHABLE', 'IPV6_SPEC_RESERVED'], 'w', ipv64_data),

                (2, '0:::0:0:255.255.255.255', 0, ['IPV6_AT_MOST_1_DCOLON'], 'e'),
                (3, '0:0::0:127.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED', 'IPV6_SPEC_RESERVED',
                                                  'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                                  'IPV4_SPEC_LOOPBACK'], 'w', ipv64_data),
                (4, '0:0:0:0::0:240.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED',
                                                  'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                                  'IPV4_SPEC_RESERVED', 'IPV6_SPEC_RESERVED'], 'w', ipv64_data),

                # ipv6-4 - FAIL
                (10, '0:0::0:0:300.2.1.1', 0, ['IPV4_OCTAL_ABOVE_255'], 'e'),

                (11, '0:0:0::0:0:0:1.1.1.1', 0, ['IPV6_TOO_MANY_PARTS_WITH_DCOLON']),

            ]
        )

        LIMIT_TO = None
        # LIMIT_TO = '004'

        LIMIT_RET_TYPE = None
        # LIMIT_RET_TYPE = 'long'

        for test in td.items(limit_to=LIMIT_TO, limit_ret_type=LIMIT_RET_TYPE):
            with self.subTest(str(test)):
                self.assertTrue(*test())

    def test_any_address(self):
        td = ParserTests(
            parse_script=is_ip,
            tests=[
                (1, '1.1.1.1', ipv4_data),
                (2, '123.123.123.123', ipv4_data),
                (3, '13.13.250.0', ipv4_data),
                (4, '255.255.255.255', ['IP_CANNOT_BE_FORWARDED', 'IP_CANNOT_BE_SOURCE',
                                        'IP_NOT_GLOBALLY_REACHABLE', 'IPV4_SPEC_BCAST'], 'w', ipv4_data),
                (5, '0.0.0.0', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED', 'IP_NOT_GLOBALLY_REACHABLE',
                                'IPV4_SPEC_THIS_HOST'], 'w', ipv4_data),
                (6, '0.0.0.0.', 0, ['IPV4_NOT_4_OCTETS', 'IPV6_AT_LEAST_2_COLONS'], 'e'),
                (7, '.0.0.0.0', 0, ['IPV4_NOT_4_OCTETS', 'IPV6_AT_LEAST_2_COLONS'], 'e'),
                (8, '1.2.3', 0, ['IPV4_NOT_4_OCTETS', 'IPV6_AT_LEAST_2_COLONS'], 'e'),
                (9, '200.2.1.1'),
                (10, '300.2.1.1', 0, ['IPV4_OCTAL_ABOVE_255', 'IPV6_AT_LEAST_2_COLONS'], 'e'),
                (11, '127.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED',
                                   'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                   'IPV4_SPEC_LOOPBACK'], 'w', ipv4_data),
                (12, '240.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED',
                                   'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                   'IPV4_SPEC_RESERVED'], 'w', ipv4_data),
                (13, 'blah', 0, ['IPV6_AT_LEAST_2_COLONS'], 'e'),

                # ipv6 comp
                (101, '0::0:0:0:0:0', 12, ipv6_unspec_msg, 'w', ipv6_data),
                (102, '0::0:0:0:0', 10, ipv6_unspec_msg, 'w', ipv6_data),
                (103, '0::0:0:0', 8, ipv6_unspec_msg, 'w', ipv6_data),
                (104, '0::0:0', 6, ipv6_unspec_msg, 'w', ipv6_data),
                (105, '0::0', 4, ipv6_unspec_msg, 'w', ipv6_data),

                (106, '0:0::0:0:0:0', 12, ipv6_unspec_msg, 'w', ipv6_data),
                (107, '0:0::0:0:0', 10, ipv6_unspec_msg, 'w', ipv6_data),
                (108, '0:0::0:0', 8, ipv6_unspec_msg, 'w', ipv6_data),
                (109, '0:0::0', 6, ipv6_unspec_msg, 'w', ipv6_data),

                (110, '0:0:0::0:0:0', 12, ipv6_unspec_msg, 'w', ipv6_data),
                (111, '0:0:0::0:0', 10, ipv6_unspec_msg, 'w', ipv6_data),
                (112, '0:0:0::0', 8, ipv6_unspec_msg, 'w', ipv6_data),

                (113, '0:0:0:0::0:0', 12, ipv6_unspec_msg, 'w', ipv6_data),
                (114, '0:0:0:0::0', 10, ipv6_unspec_msg, 'w', ipv6_data),

                (115, '0:0:0:0:0::0', 12, ipv6_unspec_msg, 'w', ipv6_data),

                # ipv6 comp - FAIL
                (116, '0::0:0:0:0:0:0:0', 0, ['IPV6_TOO_MANY_PARTS_WITH_DCOLON', 'IPV4_NOT_4_OCTETS']),
                (117, '::0:0:0:0::0:0:0:0', 0, ['IPV6_AT_MOST_8_COLONS']),
                (118, '0::0:0:0:0::0:0:0', 0, ['IPV6_AT_MOST_8_COLONS', 'IPV4_NOT_4_OCTETS']),
                (119, ':::0:0:0:0:0:0:0', 0, ['IPV6_AT_MOST_8_COLONS']),
                (120, '0:0:0:0:0:0:0:0::', 0, ['IPV6_AT_MOST_8_COLONS', 'IPV4_NOT_4_OCTETS']),


                # ipv6 full  - PASS
                (201, '0:0:0:0:0:0:0:0', ipv6_unspec_msg, 'w', ipv6_data),
                (202, '1111:1111:1111:1111:1111:1111:1111:1111', ['IP_NOT_GLOBALLY_REACHABLE', 'IPV6_SPEC_RESERVED'], 'w',
                 ipv6_data),
                (203, '12ab:abcd:fedc:1212:0:00:000:0', ['IP_NOT_GLOBALLY_REACHABLE', 'IPV6_SPEC_RESERVED'], 'w',
                 ipv6_data),

                # ipv6 full  - FAIL
                (204, '0:0:0:0:0:0:hhy:0', 0, ['IPV6_TOO_FEW_OR_MANY_PARTS', 'IPV4_NOT_4_OCTETS']),
                (205, ':1111:1111:1111:1111:1111:1111:1111:1111', 0, ['IPV6_TOO_FEW_OR_MANY_PARTS']),
                (206, '12aba:1abcd:fedc:1212:0:00:000:0', 0, ['IPV6_TOO_MANY_CHARS_IN_SEGMENT', 'IPV4_NOT_4_OCTETS']),

                (207, 'f000:0:0:0:0:1:0:1', ['IPV6_SPEC_RESERVED', 'IP_NOT_GLOBALLY_REACHABLE'], 'w', ipv6_data),
                (208, 'f800:0:0:0:0:0:0:0', ['IPV6_SPEC_RESERVED', 'IP_NOT_GLOBALLY_REACHABLE'], 'w', ipv6_data),
                (209, 'fc00:0:0:0:0:0:1:0', ['IPV6_SPEC_UNIQUE_LOCAL', 'IP_NOT_GLOBALLY_REACHABLE'], 'w', ipv6_data),
                (210, 'fe80:0:0:0:0:0:0:0',
                 ['IPV6_SPEC_LINK_LOCAL', 'IP_NOT_GLOBALLY_REACHABLE', 'IP_CANNOT_BE_FORWARDED'], 'w', ipv6_data),
                (211, 'fec0:0:0:0:0:1:0:0', ['IPV6_SPEC_SITE_LOCAL', 'IP_NOT_GLOBALLY_REACHABLE'], 'w', ipv6_data),
                (212, 'ff10:0:0:0:0:1:0:0', ['IPV6_SPEC_MULTICAST', 'IP_NOT_GLOBALLY_REACHABLE', 'IP_CANNOT_BE_SOURCE'],
                 'w', ipv6_data),

                # ipv6 4 full
                (301, '0:0:0:0:0:0:1.1.1.1', 19, ['IP_NOT_GLOBALLY_REACHABLE', 'IPV6_SPEC_RESERVED'], 'w', ipv64_data),

                (302, '0:0:0:0:0:0:255.255.255.255',
                 ['IP_CANNOT_BE_FORWARDED', 'IP_CANNOT_BE_SOURCE', 'IPV6_SPEC_RESERVED',
                  'IP_NOT_GLOBALLY_REACHABLE', 'IPV4_SPEC_BCAST'], 'w', ipv64_data),
                (303, '0:0:0:0:0:0:127.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED', 'IPV6_SPEC_RESERVED',
                                              'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                              'IPV4_SPEC_LOOPBACK'], 'w', ipv64_data),
                (304, '0:0:0:0:0:0:240.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED', 'IPV6_SPEC_RESERVED',
                                              'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                              'IPV4_SPEC_RESERVED'], 'w', ipv64_data),

                # ipv64 - FAIL
                (310, '0:0:0:0:0:0:300.2.1.1', 0, ['IPV4_OCTAL_ABOVE_255', 'IPV4_NOT_4_OCTETS'], 'e'),
                (311, ':0:0:0:0:0:1.1.1.1', 0, ['IPV6_DCOLON_MUST_NOT_BE_FIRST']),
                (312, '0:0:0:0:0:0:1:1.1.1.1', 0, ['IPV6_TOO_FEW_OR_MANY_PARTS', 'IPV4_NOT_4_OCTETS']),
                (313, '0:0:0:0:0:0:1.1.1.1.1.1', 0, ['IPV4_NOT_4_OCTETS']),

                (314, '0:0:0:0:0:0:1.1.1', 0, ['IPV4_NOT_4_OCTETS']),
                (315, '0:0:0:0:0:0:1.1', 0, ['IPV4_NOT_4_OCTETS']),
                (316, '0:0:0:0:0:0:1.abc.1', 0, ['IPV4_NOT_4_OCTETS']),

                # ipv6-4 comp
                (401, '0:0::0:0:1.1.1.1', 19, ['IP_NOT_GLOBALLY_REACHABLE', 'IPV6_SPEC_RESERVED'], 'w', ipv64_data),

                (402, '0:::0:0:255.255.255.255', 0, ['IPV6_AT_MOST_1_DCOLON', 'IPV4_NOT_4_OCTETS'], 'e'),
                (403, '0:0::0:127.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED', 'IPV6_SPEC_RESERVED',
                                         'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                         'IPV4_SPEC_LOOPBACK'], 'w', ipv64_data),
                (404, '0:0:0:0::0:240.2.1.1', ['IP_CANNOT_BE_DEST', 'IP_CANNOT_BE_FORWARDED',
                                             'IP_CANNOT_BE_SOURCE', 'IP_NOT_GLOBALLY_REACHABLE',
                                             'IPV4_SPEC_RESERVED', 'IPV6_SPEC_RESERVED'], 'w', ipv64_data),

                # ipv6-4 - FAIL
                (410, '0:0::0:0:300.2.1.1', 0, ['IPV4_OCTAL_ABOVE_255', 'IPV4_NOT_4_OCTETS'], 'e'),

                (411, '0:0:0::0:0:0:1.1.1.1', 0, ['IPV6_TOO_MANY_PARTS_WITH_DCOLON', 'IPV4_NOT_4_OCTETS']),

            ]
        )

        LIMIT_TO = None
        # LIMIT_TO = '004'

        LIMIT_RET_TYPE = None
        # LIMIT_RET_TYPE = 'long'

        for test in td.items(limit_to=LIMIT_TO, limit_ret_type=LIMIT_RET_TYPE):
            with self.subTest(str(test)):
                self.assertTrue(*test())
