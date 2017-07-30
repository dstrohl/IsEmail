from unittest import TestCase
from ValidationParser.tests.parser_test_helper import ParserTests
from ip_validator.is_ip import is_ip, is_ipv6, is_ipv4
from ValidationParser.parser_messages import RESULT_CODES


"""
Multicast: RFC-3171
 224.0.0.0   - 224.0.0.255     (224.0.0/24)  Local Network Control Block
   224.0.1.0   - 224.0.1.255     (224.0.1/24)  Internetwork Control Block
   224.0.2.0   - 224.0.255.0                   AD-HOC Block
   224.1.0.0   - 224.1.255.255   (224.1/16)    ST Multicast Groups
   224.2.0.0   - 224.2.255.255   (224.2/16)    SDP/SAP Block
   224.252.0.0 - 224.255.255.255               DIS Transient Block
   225.0.0.0   - 231.255.255.255               RESERVED
   232.0.0.0   - 232.255.255.255 (232/8)       Source Specific Multicast
                                               Block
   233.0.0.0   - 233.255.255.255 (233/8)       GLOP Block
   234.0.0.0   - 238.255.255.255               RESERVED
   239.0.0.0   - 239.255.255.255 (239/8)       Administratively Scoped
                   
                                               Block



IPv6

RFC 2373

Reserved                              0000 0000      1/256
    Unassigned                            0000 0001      1/256

    Reserved for NSAP Allocation          0000 001       1/128
    Reserved for IPX Allocation           0000 010       1/128

    Unassigned                            0000 011       1/128
    Unassigned                            0000 1         1/32
    Unassigned                            0001           1/16

    Aggregatable Global Unicast Addresses 001            1/8
    Unassigned                            010            1/8
    Unassigned                            011            1/8
    Unassigned                            100            1/8
    Unassigned                            101            1/8
    Unassigned                            110            1/8

    Unassigned                            1110           1/16
    Unassigned                            1111 0         1/32
    Unassigned                            1111 10        1/64
    Unassigned                            1111 110       1/128
    Unassigned                            1111 1110 0    1/512

    Link-Local Unicast Addresses          1111 1110 10   1/1024
    Site-Local Unicast Addresses          1111 1110 11   1/1024

    Multicast Addresses                   1111 1111      1/256

"""

class TestIPAddresses(TestCase):

    def run_parser_tests(self, tests, limit_to=None):
        if limit_to is not None:
            with self.subTest('LIMITED TEST'):
                self.fail('LIMITED_TEST')

        for test in tests:
            if limit_to is None or limit_to == test.test_id:
                with self.subTest(str(test)):
                    tmp_ret, tmp_msg = test()
                    self.assertTrue(tmp_ret, tmp_msg)

    def test_ipv4_address(self):
        td = ParserTests(
            parse_script=is_ipv4,
            tests=[
                ('001', '1.1.1.1', ['ipv4_address.IP_IS_GLOBAL'], 'w'),
                ('002', '123.123.123.123'),
                ('003', '13.13.250.0'),
                ('004', '255.255.255.255'),
                ('005', '0.0.0.0'),
                ('006', '0.0.0.0.', 0),
                ('007', '.0.0.0.0', 0),
                ('005', '1.2.3', 0),
                ('005', '200.2.1.1', 0),
                ('005', 'blah', 0),
            ]
        )

        LIMIT_TO = None
        LIMIT_TO = '001'

        self.run_parser_tests(td, LIMIT_TO)
        #
        # if LIMIT_TO is not None:
        #     with self.subTest('LIMITED TEST'):
        #         self.fail('LIMITED_TEST')
        #
        # for test in td:
        #     if LIMIT_TO is None or LIMIT_TO == test.test_id:
        #         with self.subTest(str(test)):
        #             tmp_ret, tmp_msg = test()
        #             self.assertTrue(tmp_ret, tmp_msg)
'''
    def test_ipv4_address_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            method=ipv4_address_literal,
            tests=[
                MyTestData(1, '1.1.1.1', 7, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(2, '123.123.123.123', 15, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(3, '13.13.255.0', 11, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(4, '255.255.255.255', 15, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(5, '0.0.0.0.', 7, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(6, '0.0.0.0', 7, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(7, '.0.0.0.0' ,0, history_str=''),
                MyTestData(8, '1.2.3', 0, history_str=''),
                MyTestData(9, '300.2.1.1', 0, history_str=''),
                MyTestData(10, 'blah', 0, history_str=''),
            ]
        )
        self.run_test_data(td)

    def test_snum(self):
        td = MyTestDefs(
            limit_to=-1,
            method=snum,
            tests=[
                MyTestData(1, '1', 1, history_str='snum'),
                MyTestData(2, '12', 2, history_str='snum'),
                MyTestData(3, '133', 3, history_str='snum'),
                MyTestData(4, '255', 3, history_str='snum'),
                MyTestData(5, '299', 0, history_str=''),
                MyTestData(6, '099', 3, history_str='snum'),
                MyTestData(7, '009', 3, history_str='snum'),
                MyTestData(8, '0093', 3, history_str='snum'),
                MyTestData(9, '5057', 0, history_str=''),
                MyTestData(10, '02', 2, history_str='snum'),
                MyTestData(7, '000.', 3, history_str='snum'),
                MyTestData(7, '0av', 1, history_str='snum'),
            ]
        )
        self.run_test_data(td)

    def test_ipv6_address_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            # trace_filter=4,
            history_level=3,
            method=ipv6_address_literal,
            tests=[

                # ipv6 full  - PASS
                MyTestData(1, 'IPv6:0:0:0:0:0:0:0:0', 20, codes=['RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_full(...)))'),
                MyTestData(2, 'IPv6:1111:1111:1111:1111:1111:1111:1111:1111', 44, codes=['RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_full(...)))'),
                MyTestData(3, 'IPv6:12ab:abcd:fedc:1212:0:00:000:0', 35, codes=['RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_full(...)))'),

                # ipv6 full  - FAIL
                MyTestData(4, 'IPv6:0:0:0:0:0:0:hhy:0', 0, history_str=''),
                MyTestData(5, 'IPv6::1111:1111:1111:1111:1111:1111:1111:1111', 0, history_str=''),
                MyTestData(6, 'IPv6:12aba:1abcd:fedc:1212:0:00:000:0', 0, history_str=''),

                MyTestData(101, 'IPv6:0::0:0:0:0:0', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),
                MyTestData(102, 'IPv6:0::0:0:0:0', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),
                MyTestData(103, 'IPv6:0::0:0:0', 13, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),
                MyTestData(104, 'IPv6:0::0:0', 11, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),
                MyTestData(105, 'IPv6:0::0', 9, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),

                MyTestData(106, 'IPv6:0:0::0:0:0:0', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),
                MyTestData(107, 'IPv6:0:0::0:0:0', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),
                MyTestData(108, 'IPv6:0:0::0:0', 13, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),
                MyTestData(109, 'IPv6:0:0::0', 11, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),

                MyTestData(110, 'IPv6:0:0:0::0:0:0', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),
                MyTestData(111, 'IPv6:0:0:0::0:0', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),
                MyTestData(112, 'IPv6:0:0:0::0', 13, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),

                MyTestData(113, 'IPv6:0:0:0:0::0:0', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),
                MyTestData(114, 'IPv6:0:0:0:0::0', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),

                MyTestData(115, 'IPv6:0:0:0:0:0::0', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6_comp(...)))'),

                # ipv6 comp - FAIL
                MyTestData(116, 'IPv6:0::0:0:0:0:0:0', 0, history_str=''),
                MyTestData(117, 'IPv6:0:0:0:0::0:0:0:0', 0, history_str=''),

                # ipv6-4 - PASS
                MyTestData(201, 'IPv6:0:0:0:0:0:0:1.1.1.1', 24, codes=['RFC5322_IPV6_IPV4_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6v4_full(...)))'),

                # ipv6-4 - FAIL
                MyTestData(203, 'IPv6:0:0:0:0:0:1.1.1.1', 0, history_str=''),
                MyTestData(204, 'IPv6:0:0:0:0:0:0:1:1.1.1.1', 0),
                MyTestData(205, 'IPv6:0:0:0:0:0:0:1.1.1', 0, history_str=''),

                # ipv6-4 comp - PASS

                MyTestData(301, 'IPv6:0::0:0:0:1.1.1.1', 21, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6v4_comp(...)))'),
                MyTestData(302, 'IPv6:0::0:0:1.1.1.1', 19, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6v4_comp(...)))'),
                MyTestData(303, 'IPv6:0::0:1.1.1.1', 17, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6v4_comp(...)))'),

                MyTestData(304, 'IPv6:0:0::0:0:1.1.1.1', 21, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6v4_comp(...)))'),
                MyTestData(305, 'IPv6:0:0::0:1.1.1.1', 19, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6v4_comp(...)))'),

                MyTestData(306, 'IPv6:0:0:0::0:1.1.1.1', 21, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='ipv6_address_literal(ipv6, ipv6_addr(ipv6v4_comp(...)))'),

                # ipv6-4 comp - FAIL
                MyTestData(307, 'IPv6:0:0:0::0:0:0:1.1.1.1', 0, history_str=''),
            ]
        )
        self.run_test_data(td)

    def test_ipv6_hex(self):
        td = MyTestDefs(
            limit_to=-1,
            method=ipv6_hex,
            tests=[
                MyTestData(1, '1', 1, history_str='ipv6_hex'),
                MyTestData(2, '12', 2, history_str='ipv6_hex'),
                MyTestData(3, '1234', 4, history_str='ipv6_hex'),
                MyTestData(4, '12345', 4, history_str='ipv6_hex'),
                MyTestData(5, 'ABCD', 4, history_str='ipv6_hex'),
                MyTestData(6, 'abcd', 4, history_str='ipv6_hex'),
                MyTestData(7, 'a1d4', 4, history_str='ipv6_hex'),
                MyTestData(8, '00ab', 4, history_str='ipv6_hex'),
                MyTestData(9, 'xx000', 0, history_str=''),
                MyTestData(10, 'yycx', 0, history_str=''),
            ]
        )
        self.run_test_data(td)

    def test_ipv6_full(self):
        td = MyTestDefs(
            limit_to=-1,
            method=ipv6_full,
            tests=[
                # ipv6 full  - PASS
                MyTestData(1, '0:0:0:0:0:0:0:0', 15, codes='RFC5322_IPV6_FULL_ADDR', history_str='ipv6_full(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(2, '1111:1111:1111:1111:1111:1111:1111:1111', 39, codes='RFC5322_IPV6_FULL_ADDR', history_str='ipv6_full(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(3, '12ab:abcd:fedc:1212:0:00:000:0', 30, codes='RFC5322_IPV6_FULL_ADDR', history_str='ipv6_full(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex)'),

                # ipv6 full  - FAIL
                MyTestData(4, '0:0:0:0:0:0:hhy:0', 0, history_str=''),
                MyTestData(5, ':1111:1111:1111:1111:1111:1111:1111:1111', 0, history_str=''),
                MyTestData(6, '12aba:1abcd:fedc:1212:0:00:000:0', 0, history_str=''),
            ]
        )
        self.run_test_data(td)

    def test_ipv6_comp(self):
        td = MyTestDefs(
            limit_to=-1,
            method=ipv6_comp,
            tests=[
                MyTestData(1, '0::0:0:0:0:0', 12, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(2, '0::0:0:0:0', 10, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(3, '0::0:0:0', 8, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(4, '0::0:0', 6, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(5, '0::0', 4, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, double_colon, ipv6_hex)'),


                MyTestData(6, '0:0::0:0:0:0', 12, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(7, '0:0::0:0:0', 10, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(8, '0:0::0:0', 8, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(9, '0:0::0', 6, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex)'),


                MyTestData(10, '0:0:0::0:0:0', 12, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(11, '0:0:0::0:0', 10, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(12, '0:0:0::0', 8, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex)'),


                MyTestData(13, '0:0:0:0::0:0', 12, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex)'),
                MyTestData(14, '0:0:0:0::0', 10, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex)'),

                MyTestData(15, '0:0:0:0:0::0', 12, codes='RFC5322_IPV6_COMP_ADDR', history_str='ipv6_comp(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex)'),

                # ipv6 comp - FAIL
                MyTestData(16, '0::0:0:0:0:0:0', 0, history_str=''),
                MyTestData(17, '0:0:0:0::0:0:0:0', 0, history_str=''),
            ]
        )
        self.run_test_data(td)

    def test_ipv6v4_full(self):
        td = MyTestDefs(
            limit_to=-1,
            method=ipv6v4_full,
            tests=[

                # ipv6-4 - PASS
                MyTestData(1, '0:0:0:0:0:0:1.1.1.1', 19, codes='RFC5322_IPV6_IPV4_ADDR', history_str='ipv6v4_full(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum))'),

                # ipv6-4 - FAIL
                MyTestData(3, '0:0:0:0:0:1.1.1.1', 0, history_str=''),
                MyTestData(4, '0:0:0:0:0:0:1:1.1.1.1', 0, history_str=''),
                MyTestData(5, '0:0:0:0:0:0:1.1.1', 0, history_str=''),

                MyTestData(6, '0::0:0:0:1.1.1.1', 0, history_str=''),
                MyTestData(7, '0::0:0:1.1.1.1', 0, history_str=''),
                MyTestData(8, '0::0:1.1.1.1', 0, history_str=''),

                MyTestData(9, '0:0::0:0:1.1.1.1', 0, history_str=''),
                MyTestData(10, '0:0::0:1.1.1.1', 0, history_str=''),

                MyTestData(11, '0:0:0::0:1.1.1.1', 0, history_str=''),

            ]
        )
        self.run_test_data(td)

    def test_ipv6v4_comp(self):
        td = MyTestDefs(
            limit_to=-1,
            method=ipv6v4_comp,
            tests=[
                # ipv6-4 comp - PASS

                MyTestData(1, '0::0:0:0:1.1.1.1', 16, codes='RFC5322_IPV6_IPV4_COMP_ADDR', history_str='ipv6v4_comp(ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, colon, ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum))'),
                MyTestData(2, '0::0:0:1.1.1.1', 14, codes='RFC5322_IPV6_IPV4_COMP_ADDR', history_str='ipv6v4_comp(ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex, colon, ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum))'),
                MyTestData(3, '0::0:1.1.1.1', 12, codes='RFC5322_IPV6_IPV4_COMP_ADDR', history_str='ipv6v4_comp(ipv6_hex, double_colon, ipv6_hex, colon, ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum))'),

                MyTestData(4, '0:0::0:0:1.1.1.1', 16, codes='RFC5322_IPV6_IPV4_COMP_ADDR', history_str='ipv6v4_comp(ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex, colon, ipv6_hex, colon, ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum))'),
                MyTestData(5, '0:0::0:1.1.1.1', 14, codes='RFC5322_IPV6_IPV4_COMP_ADDR', history_str='ipv6v4_comp(ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex, colon, ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum))'),

                MyTestData(6, '0:0:0::0:1.1.1.1', 16, codes='RFC5322_IPV6_IPV4_COMP_ADDR', history_str='ipv6v4_comp(ipv6_hex, colon, ipv6_hex, colon, ipv6_hex, double_colon, ipv6_hex, colon, ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum))'),

                # ipv6-4 comp - FAIL
                MyTestData(7, '0:0:0::0:0:0:1.1.1.1', 0, history_str=''),
            ]
        )
        self.run_test_data(td)
'''