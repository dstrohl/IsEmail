from ValidationParser.parser_objects import *
from ValidationParser.parser_base_chars import *
from ValidationParser.exceptions import ParsingLocalError
from ValidationParser.parser_messages import STATUS_CODES
from helpers.general import make_char_str, make_list
from ipaddress import IPv4Address, IPv6Address, AddressValueError, IPv4Network, IPv6Network
import re
from collections import namedtuple

__all__ = ['ValidateIPAddr', 'ValidateIPv4Addr', 'ValidateIPv6Addr',
           'validate_ip_addr', 'validate_ipv4_addr', 'validate_ipv6_addr']


# **********************************************************************************
# <editor-fold desc="  IP Messages  ">
# **********************************************************************************


ReservedNames = namedtuple('ReservedNames', ('prefix', 'ipv6', 'block', 'key', 'source_ok', 'destination_ok', 'forwardable', 'globally_reachable'))


# EDITING NOTE, SETS MUST be in order.
IP_RESERVED_RANGES = {
    4: {
        1: {
            '0': (
                ReservedNames('0', False, IPv4Network('0.0.0.0/8'), 'IPV4_SPEC_THIS_HOST', True, False, False, False),
            )
        },
        2: {
            '10': (
                ReservedNames('10', False, IPv4Network('10.0.0.0/8'), 'IPV4_SPEC_PRIVATE', True, True, True, False),
            )
        },
        3: {
            '100': (
                ReservedNames('100', False, IPv4Network('100.64.0.0/10'), 'IPV4_SPEC_SHARED', True, True, True, False),
            ),
            '127': (
                ReservedNames('127', False, IPv4Network('127.0.0.0/8'), 'IPV4_SPEC_LOOPBACK', False, False, False,
                              False),
            ),
            '169': (
                ReservedNames('169', False, IPv4Network('169.254.0.0/16'), 'IPV4_SPEC_LINK_LOCAL', True, True, False,
                              False),

            ),
            '172': (
                ReservedNames('172', False, IPv4Network('172.16.0.0/12'), 'IPV4_SPEC_PRIVATE', True, True, True, False),
            ),
            '192': (
                ReservedNames('192', False, IPv4Network('192.0.0.8/32'), 'IPV4_SPEC_DUMMY', True, False, False, False),
                ReservedNames('192', False, IPv4Network('192.0.0.9/32'), 'IPV4_SPEC_PC_ANYCAST', True, True, True, True),
                ReservedNames('192', False, IPv4Network('192.0.0.10/32'), 'IPV4_SPEC_NAT_ANYCAST', True, True, True, True),
                ReservedNames('192', False, IPv4Network('192.0.0.170/32'), 'IPV4_SPEC_64_DISC', False, False, False, False),
                ReservedNames('192', False, IPv4Network('192.0.0.171/32'), 'IPV4_SPEC_64_DISC', False, False, False, False),
                ReservedNames('192', False, IPv4Network('192.0.0.0/29'), 'IPV4_SPEC_SVC_CONT', True, True, True, False),
                ReservedNames('192', False, IPv4Network('192.0.0.0/24'), 'IPV4_SPEC_PROTOCAL', False, False, False, False),
                ReservedNames('192', False, IPv4Network('192.0.2.0/24'), 'IPV4_SPEC_DOC_TEST', False, False, False, False),
                ReservedNames('192', False, IPv4Network('192.31.196.0/24'), 'IPV4_SPEC_AS112', True, True, True, True),
                ReservedNames('192', False, IPv4Network('192.52.193.0/24'), 'IPV4_SPEC_AMI', True, True, True, True),
                ReservedNames('192', False, IPv4Network('192.175.48.0/24'), 'IPV4_SPEC_AS112', True, True, True, True),
                ReservedNames('192', False, IPv4Network('192.168.0.0/16'), 'IPV4_SPEC_PRIVATE', True, True, True, False),
            ),
            '198': (
                ReservedNames('198', False, IPv4Network('198.51.100.0/24'), 'IPV4_SPEC_DOC_TEST', False, False, False,
                              False),
                ReservedNames('198', False, IPv4Network('198.18.0.0/15'), 'IPV4_SPEC_BENCH', True, True, False, False),
            ),
            '2': (
                ReservedNames('255', False, IPv4Network('255.255.255.255/32'), 'IPV4_SPEC_BCAST', False, True, False,
                              False),
                ReservedNames('203', False, IPv4Network('203.0.113.0/24'), 'IPV4_SPEC_DOC_TEST', False, False, False,
                              False),
                ReservedNames('2', False, IPv4Network('224.0.0.0/4'), 'IPV4_SPEC_MULTICAST', False, True, True,
                              False),

                ReservedNames('240', False, IPv4Network('240.0.0.0/4'), 'IPV4_SPEC_RESERVED', False, False, False,
                              False),
            ),
        }
    },
    6: {
        4: {
            '0000': (
                ReservedNames('00', True, IPv6Network('::1/128'), 'IPV6_SPEC_LOOPBACK', False, False, False, False),
                ReservedNames('00', True, IPv6Network('::/128'), 'IPV6_SPEC_UNSPECIFIED', True, False, False, False),
                ReservedNames('00', True, IPv6Network('::ffff:0:0/96'), 'IPV6_SPEC_IPV4_MAP', False, False, False,
                              False),
                ReservedNames('00', True, IPv6Network('::/8'), 'IPV6_SPEC_RESERVED', True, True, True, False)),
            '0054': (
                ReservedNames('0064', True, IPv6Network('64:ff9b::/96'), 'IPV6_SPEC_IPV4_TRANS', True, True, True,
                              True),
                ReservedNames('0064', True, IPv6Network('64:ff9b:1::/48'), 'IPV6_SPEC_IPV4_TRANS', True, True, True,
                              False)),
            '01': (
                ReservedNames('01', True, IPv6Network('100::/64'), 'IPV6_SPEC_DISCARD', True, True, True, False),
                ReservedNames('01', True, IPv6Network('100::/8'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '02': (
                ReservedNames('02', True, IPv6Network('200::/7'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '03': (
                ReservedNames('03', True, IPv6Network('200::/7'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '04': (
                ReservedNames('04', True, IPv6Network('400::/6'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '05': (
                ReservedNames('05', True, IPv6Network('400::/6'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '06': (
                ReservedNames('06', True, IPv6Network('400::/6'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '07': (
                ReservedNames('07', True, IPv6Network('400::/6'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '08': (
                ReservedNames('08', True, IPv6Network('800::/5'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '09': (
                ReservedNames('09', True, IPv6Network('800::/5'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '1': (
                ReservedNames('1', True, IPv6Network('1000::/4'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '2001': (
                ReservedNames('2001', True, IPv6Network('2001:1::1/128'), 'IPV6_SPEC_PC_ANYCAST', True, True, True,
                              True),
                ReservedNames('2001', True, IPv6Network('2001:1::2/128'), 'IPV6_SPEC_NAT_ANYCAST', True, True, True,
                              True),
                ReservedNames('2001', True, IPv6Network('2001:2::/48'), 'IPV6_SPEC_BENCHMARK', True, True, True, False),
                ReservedNames('2001', True, IPv6Network('2001:4:112::/48'), 'IPV6_SPEC_AS112', True, True, True, True),
                ReservedNames('2001', True, IPv6Network('2001::/23'), 'IPV6_SPEC_PROTOCOL', False, False, False, False),
                ReservedNames('2001', True, IPv6Network('2001:3::/32'), 'IPV6_SPEC_AMT', True, True, True, True),
                ReservedNames('2001', True, IPv6Network('2001:5::/32'), 'IPV6_SPEC_LISP', True, True, True, True),
                ReservedNames('2001', True, IPv6Network('2001:20::/28'), 'IPV6_SPEC_ORCHID', True, True, True, True),
                ReservedNames('2001', True, IPv6Network('2001:db8::/32'), 'IPV6_SPEC_DOC_TEST', False, False, False,
                              False),
            ),
            '2002': (
                ReservedNames('2002', True, IPv6Network('2002::/16'), 'IPV6_SPEC_6TO4', True, True, True, False),
            ),
            '2620': (
                ReservedNames('2620', True, IPv6Network('2620:4f:8000::/48'), 'IPV6_SPEC_AS112', True, True, True,
                              True),
            ),
            '4': (
                ReservedNames('4', True, IPv6Network('4000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '5': (
                ReservedNames('5', True, IPv6Network('4000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '6': (
                ReservedNames('6', True, IPv6Network('6000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '7': (
                ReservedNames('7', True, IPv6Network('6000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '8': (
                ReservedNames('8', True, IPv6Network('8000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            '9': (
                ReservedNames('9', True, IPv6Network('8000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            'a': (
                ReservedNames('a', True, IPv6Network('A000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            'b': (
                ReservedNames('b', True, IPv6Network('A000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            'c': (
                ReservedNames('c', True, IPv6Network('C000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            'd': (
                ReservedNames('d', True, IPv6Network('C000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            'e': (
                ReservedNames('e', True, IPv6Network('E000::/4'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
            'f': (
                ReservedNames('f', True, IPv6Network('fe80::/10'), 'IPV6_SPEC_LINK_LOCAL', True, True, False, False),
                ReservedNames('f', True, IPv6Network('FEC0::/10'), 'IPV6_SPEC_SITE_LOCAL', True, True, True, False),
                ReservedNames('f', True, IPv6Network('FE00::/9'), 'IPV6_SPEC_RESERVED', True, True, True, False),
                ReservedNames('f', True, IPv6Network('ff00::/8'), 'IPV6_SPEC_MULTICAST', False, True, True, False),
                ReservedNames('f', True, IPv6Network('fc00::/7'), 'IPV6_SPEC_UNIQUE_LOCAL', True, True, True, False),
                ReservedNames('f', True, IPv6Network('F800::/6'), 'IPV6_SPEC_RESERVED', True, True, True, False),
                ReservedNames('f', True, IPv6Network('F000::/5'), 'IPV6_SPEC_RESERVED', True, True, True, False),
            ),
        },
    }


}


# TWO_DIGIT = '12'
ADDR_CHAR_IPV4 = '0123456789.'
ADDR_CHAR_IPV6 = make_char_str(CHARS.HEXDIG, CHARS.COLON)
ADDR_CHAR_IPV64 = make_char_str(CHARS.HEXDIG, ADDR_CHAR_IPV4, CHARS.COLON)


IP_MESSAGES = [
        {'key': 'EMPTY_IP_ADDRESS',
         'description': 'The address was empty',
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV4_NOT_4_OCTETS',
         'description': "Expected 4 octets",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV4_EMPTY_OCTET',
         'description': "Empty octet not permitted",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV4_INVALID_CHAR',
         'description': "Only decimal digits permitted",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV4_TOO_MANY_CHARS',
         'description': "At most 3 characters permitted in octet",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV4_NOT_INT',
         'description': "Ambiguous (octal/decimal) value not permitted",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV4_OCTAL_ABOVE_255',
         'description': "Octet > 255 not permitted",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV6_AT_LEAST_2_COLONS',
         'description': 'An IPv6 address needs at least 2 colons (3 parts).',
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV6_AT_MOST_8_COLONS',
         'description': "An IPv6 address can't have more than 8 colons (9 parts).",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV6_AT_MOST_1_DCOLON',
         'description': "Can't have more than one '::'",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV6_TOO_MANY_PARTS_WITH_DCOLON',
         'description': "Incorrect number of parts with ::",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV6_TOO_FEW_OR_MANY_PARTS',
         'description': "Incorrect number of parts without ::",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV6_DCOLON_MUST_NOT_BE_FIRST',
         'description': "There must be something before the ::",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV6_DCOLON_MUST_NOT_BE_LAST',
         'description': "There must be something after the ::",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV6_NOT_HEX_DIGITS',
         'description': "Only hex digits permitted",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV6_TOO_MANY_CHARS_IN_SEGMENT',
         'description': "At most 4 characters permitted",
         'status': STATUS_CODES.ERROR},

        {'key': 'IPV4_SPEC_THIS_HOST',
         'description': '"This host on this network"',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC1122]  Section 3.2.1.3'], },

        # 'source_ok', 'destination_ok', 'forwardable', 'globally_reachable'

        {'key': 'IP_CANNOT_BE_SOURCE',
         'description': 'This address cannot be a source address',
         'status': STATUS_CODES.WARNING,
         'references': [], },

        {'key': 'IP_CANNOT_BE_DEST',
         'description': 'This address cannot be a destination address',
         'status': STATUS_CODES.WARNING,
         'references': [], },
        {'key': 'IP_CANNOT_BE_FORWARDED',
         'description': 'This address cannot be forwarded by routers',
         'status': STATUS_CODES.WARNING,
         'references': [], },
        {'key': 'IP_NOT_GLOBALLY_REACHABLE',
         'description': 'This address cannot be reached from the internet',
         'status': STATUS_CODES.WARNING,
         'references': [], },



        {'key': 'IPV4_SPEC_PRIVATE',
         'description': 'Private-Use',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC1918]'], },
        {'key': 'IPV4_SPEC_SHARED',
         'description': 'Shared Address Space',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC6598]'], },
        {'key': 'IPV4_SPEC_LOOPBACK',
         'description': 'Loopback (Several protocols have been granted exceptions to this rule. For examples  see [RFC8029] and [RFC5884])',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC1122]  Section 3.2.1.3'], },
        {'key': 'IPV4_SPEC_LINK_LOCAL',
         'description': 'Link Local',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC3927]'], },
        {'key': 'IPV4_SPEC_PRIVATE',
         'description': 'Private-Use',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC1918]'], },
        {'key': 'IPV4_SPEC_PROTOCAL',
         'description': 'IETF Protocol Assignments',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC6890]  Section 2.1'], },
        {'key': 'IPV4_SPEC_SVC_CONT',
         'description': 'IPv4 Service Continuity Prefix',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7335]'], },
        {'key': 'IPV4_SPEC_DUMMY',
         'description': 'IPv4 dummy address',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7600]'], },
        {'key': 'IPV4_SPEC_PC_ANYCAST',
         'description': 'Port Control Protocol Anycast',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7723]'], },
        {'key': 'IPV4_SPEC_NAT_ANYCAST',
         'description': 'Traversal Using Relays around NAT Anycast',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC8155]'], },
        {'key': 'IPV4_SPEC_64_DISC',
         'description': 'NAT64/DNS64 Discovery',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7050]  Section 2.2'], },
        {'key': 'IPV4_SPEC_64_DISC',
         'description': 'NAT64/DNS64 Discovery',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7050]  Section 2.2'], },
        {'key': 'IPV4_SPEC_DOC_TEST',
         'description': 'Documentation (TEST-NET-1)',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC5737]'], },
        {'key': 'IPV4_SPEC_AS112',
         'description': 'AS112-v4',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7535]'], },
        {'key': 'IPV4_SPEC_AMI',
         'description': 'AMT',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7450]'], },
        {'key': 'IPV4_SPEC_PRIVATE',
         'description': 'Private-Use',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC1918]'], },
        {'key': 'IPV4_SPEC_AS112',
         'description': 'Direct Delegation AS112 Service',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7534]'], },
        {'key': 'IPV4_SPEC_BENCH',
         'description': 'Benchmarking',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2544]'], },
        {'key': 'IPV4_SPEC_DOC_TEST',
         'description': 'Documentation (TEST-NET-2)',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC5737]'], },
        {'key': 'IPV4_SPEC_DOC_TEST',
         'description': 'Documentation (TEST-NET-3)',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC5737]'], },
        {'key': 'IPV4_SPEC_MULTICAST',
         'description': 'Multicast Addresses',
         'status': STATUS_CODES.WARNING,
         'references': ['[3171]'], },
        {'key': 'IPV4_SPEC_RESERVED',
         'description': 'Reserved',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC1112]  Section 4'], },
        {'key': 'IPV4_SPEC_BCAST',
         'description': 'Limited Broadcast',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC8190][RFC919]  Section 7'], },
        {'key': 'IPV6_SPEC_LOOPBACK',
         'description': 'Loopback Address',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC4291]'], },
        {'key': 'IPV6_SPEC_UNSPECIFIED',
         'description': 'Unspecified Address',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC4291]'], },
        {'key': 'IPV6_SPEC_IPV4_MAP',
         'description': 'IPv4-mapped Address',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC4291]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_IPV4_TRANS',
         'description': 'IPv4-IPv6 Translat.',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC6052]'], },
        {'key': 'IPV6_SPEC_IPV4_TRANS',
         'description': 'IPv4-IPv6 Translat.',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC-ietf-v6ops-v4v6-xlat-prefix-02]'], },
        {'key': 'IPV6_SPEC_DISCARD',
         'description': 'Discard-Only Address Block',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC6666]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_PROTOCOL',
         'description': 'IETF Protocol Assignments (Unless allowed by a more specific allocation.)',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2928]'], },
        {'key': 'IPV6_SPEC_TEREDO',
         'description': 'TEREDO (See Section 5 of [RFC4380] for details.)',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC4380][RFC8190]'], },
        {'key': 'IPV6_SPEC_PC_ANYCAST',
         'description': 'Port Control Protocol Anycast',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7723]'], },
        {'key': 'IPV6_SPEC_NAT_ANYCAST',
         'description': 'Traversal Using Relays around NAT Anycast',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC8155]'], },
        {'key': 'IPV6_SPEC_BENCHMARK',
         'description': 'Benchmarking',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC5180]'], },
        {'key': 'IPV6_SPEC_AMT',
         'description': 'AMT',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7450]'], },
        {'key': 'IPV6_SPEC_AS112',
         'description': 'AS112-v6',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7535]'], },
        {'key': 'IPV6_SPEC_LISP',
         'description': 'EID Space for LISP (Managed by RIPE NCC) (Can be used as a multicast source as well. To be used as EID space by routers enabled by LISP [RFC6830].)',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7954]'], },
        {'key': 'IPV6_SPEC_ORCHID',
         'description': 'ORCHIDv2',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7343]'], },
        {'key': 'IPV6_SPEC_DOC_TEST',
         'description': 'Documentation',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC3849]'], },
        {'key': 'IPV6_SPEC_6TO4',
         'description': '6to4 (See [RFC3056] for details.)',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC3056]'], },
        {'key': 'IPV6_SPEC_AS112',
         'description': 'Direct Delegation AS112 Service',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC7534]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_UNIQUE_LOCAL',
         'description': 'Unique-Local (See [RFC4193] for more details on the routability of Unique-Local addresses.  The Unique-Local prefix is drawn from the IPv6 Global Unicast Address range  but is specified as not globally routed.)',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC4193][RFC8190]'], },
        {'key': 'IPV6_SPEC_UNIQUE_LOCAL',
         'description': 'Unique-Local (See [RFC4193] for more details on the routability of Unique-Local addresses.  The Unique-Local prefix is drawn from the IPv6 Global Unicast Address range  but is specified as not globally routed.)',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC4193][RFC8190]'], },
        {'key': 'IPV6_SPEC_LINK_LOCAL',
         'description': 'Link-Local Unicast',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC4291]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_SITE_LOCAL',
         'description': 'Site Local Unicast',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC4291]'], },
        {'key': 'IPV6_SPEC_MULTICAST',
         'description': 'Multicast Addresses',
         'status': STATUS_CODES.WARNING,
         'references': ['[RFC2373]'], },
        ]


IP_ERRORS = {
    4: {
        'EMPTY_IP_ADDRESS': re.compile(r'^Address\scannot\sbe\sempty.*'),
        'IPV4_NOT_4_OCTETS': re.compile(r'^Expected\s4\soctets\sin\s.*'),
        'IPV4_EMPTY_OCTET': re.compile(r'^Empty\soctet\snot\spermitted.*'),
        'IPV4_INVALID_CHAR': re.compile(r'^Only\sdecimal\sdigits\spermitted\sin\s.*'),
        'IPV4_TOO_MANY_CHARS': re.compile(r'^At\smost\s3\scharacters\spermitted\sin\s.*'),
        'IPV4_NOT_INT': re.compile(r'^Ambiguous\s\(octal/decimal\)\svalue\sin\s.*'),
        'IPV4_OCTAL_ABOVE_255': re.compile(r'^Octet\s\d+\s\(>\s255\)\snot\spermitted.*'),

    },
    6: {
        'EMPTY_IP_ADDRESS': re.compile(r'^Address\scannot\sbe\sempty.*'),
        'IPV6_AT_LEAST_2_COLONS': re.compile(r'^At\sleast\s\d+\sparts\sexpected\sin\s.*'),
        'IPV6_AT_MOST_8_COLONS': re.compile(r'^At\smost\s\d+\scolons\spermitted\sin\s.*'),
        'IPV6_AT_MOST_1_DCOLON': re.compile(r"^At\smost\sone\s'::'\spermitted\sin\s.*"),
        'IPV6_TOO_MANY_PARTS_WITH_DCOLON': re.compile(r"^Expected\sat\smost\s\d+\sother\sparts\swith\s'::'\sin\s.*"),
        'IPV6_TOO_FEW_OR_MANY_PARTS': re.compile(r"^Exactly\s\d+\sparts\sexpected\swithout\s'::'\sin\s.*"),
        'IPV6_DCOLON_MUST_NOT_BE_FIRST': re.compile(r"^Leading\s':'\sonly\spermitted\sas\spart\sof\s'::'\sin\s.*"),
        'IPV6_DCOLON_MUST_NOT_BE_LAST': re.compile(r"^Trailing\s':'\sonly\spermitted\sas\spart\sof\s'::'\sin\s.*"),
        'IPV6_NOT_HEX_DIGITS': re.compile(r'^Only\shex\sdigits\spermitted\sin\s.*'),
        'IPV6_TOO_MANY_CHARS_IN_SEGMENT': re.compile(r'^At\smost\s4\scharacters\spermitted\sin\s.*'),
        'IPV4_NOT_4_OCTETS': re.compile(r'^Expected\s4\soctets\sin\s.*'),
        'IPV4_EMPTY_OCTET': re.compile(r'^Empty\soctet\snot\spermitted.*'),
        'IPV4_INVALID_CHAR': re.compile(r'^Only\sdecimal\sdigits\spermitted\sin\s.*'),
        'IPV4_TOO_MANY_CHARS': re.compile(r'^At\smost\s3\scharacters\spermitted\sin\s.*'),
        'IPV4_NOT_INT': re.compile(r'^Ambiguous\s\(octal/decimal\)\svalue\sin\s.*'),
        'IPV4_OCTAL_ABOVE_255': re.compile(r'^Octet\s\d+\s\(>\s255\)\snot\spermitted.*'),}
}


#
# IP_MESSAGES = [
#     {'key': 'EMPTY_IP_ADDRESS',
#      'description': 'The address was empty',
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV6_AT_LEAST_2_COLONS',
#      'description': 'An IPv6 address needs at least 2 colons (3 parts).',
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV6_AT_MOST_8_COLONS' ,
#      'description': "An IPv6 address can't have more than 8 colons (9 parts).",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV6_AT_MOST_1_DCOLON' ,
#      'description': "Can't have more than one '::'",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV6_TOO_MANY_PARTS_WITH_DCOLON' ,
#      'description': "Incorrect number of parts with ::",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV6_TOO_FEW_OR_MANY_PARTS',
#      'description': "Incorrect number of parts without ::",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV6_DCOLON_MUST_NOT_BE_FIRST',
#      'description': "There must be something before the ::",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV6_DCOLON_MUST_NOT_BE_LAST',
#      'description': "There must be something after the ::",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV6_NOT_HEX_DIGITS',
#      'description': "Only hex digits permitted",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV6_TOO_MANY_CHARS_IN_SEGMENT',
#      'description': "At most 4 characters permitted",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV4_NOT_4_OCTETS',
#      'description': "Expected 4 octets",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV4_EMPTY_OCTET',
#      'description': "Empty octet not permitted",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV4_INVALID_CHAR',
#      'description': "Only decimal digits permitted",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV4_TOO_MANY_CHARS',
#      'description': "At most 3 characters permitted in octet",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV4_NOT_INT',
#      'description': "Ambiguous (octal/decimal) value not permitted",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IPV4_OCTAL_ABOVE_255',
#      'description': "Octet > 255 not permitted",
#      'status': RESULT_CODES.ERROR},
#
#     {'key': 'IP_IS_MULTICAST',
#      'description': "True if the address is reserved for multicast use. See RFC 3171 (for IPv4) or RFC 2373 (for IPv6).",
#      'status': RESULT_CODES.WARNING},
#
#     {'key': 'IP_IS_PRIVATE',
#      'description': "True if the address is allocated for private networks. See iana-ipv4-special-registry (for IPv4) or iana-ipv6-special-registry (for IPv6).",
#      'status': RESULT_CODES.WARNING},
#
#     {'key': 'IP_IS_GLOBAL',
#      'description': "True if the address is allocated for public networks. See iana-ipv4-special-registry (for IPv4) or iana-ipv6-special-registry (for IPv6).",
#      'status': RESULT_CODES.WARNING},
#
#     {'key': 'IP_IS_UNSPECIFIED',
#      'description': "True if the address is unspecified. See RFC 5735 (for IPv4) or RFC 2373 (for IPv6).",
#      'status': RESULT_CODES.WARNING},
#
#     {'key': 'IP_IS_RESERVED',
#      'description': "True if the address is otherwise IETF reserved.",
#      'status': RESULT_CODES.WARNING},
#
#     {'key': 'IP_IS_LOOPBACK',
#      'description': "True if this is a loopback address. See RFC 3330 (for IPv4) or RFC 2373 (for IPv6).",
#      'status': RESULT_CODES.WARNING},
#
#     {'key': 'IP_IS_LINK_LOCAL',
#      'description': "True if the address is reserved for link-local usage. See RFC 3927.",
#      'status': RESULT_CODES.WARNING},
#
#     {'key': 'IPV6_IS_SITE_LOCAL',
#      'description': "True if the address is reserved for site-local usage. Note that the site-local address space has been deprecated by RFC 3879. Use is_private to test if this address is in the space of unique local addresses as defined by RFC 4193.",
#      'status': RESULT_CODES.WARNING},
#     ]
#
#
# IP_ERROR_MATCH = {
#     'EMPTY_IP_ADDRESS': re.compile(r'^Address\scannot\sbe\sempty.*'),
#     'IPV6_AT_LEAST_2_COLONS': re.compile(r'^At\sleast\s\d+\sparts\sexpected\sin\s.*'),
#     'IPV6_AT_MOST_8_COLONS': re.compile(r'^At\smost\s\d+\scolons\spermitted\sin\s.*'),
#     'IPV6_AT_MOST_1_DCOLON': re.compile(r"^At\smost\sone\s'::'\spermitted\sin\s.*"),
#     'IPV6_TOO_MANY_PARTS_WITH_DCOLON': re.compile(r"^Expected\sat\smost\s\d+\sother\sparts\swith\s'::'\sin\s.*"),
#     'IPV6_TOO_FEW_OR_MANY_PARTS': re.compile(r"^Exactly\s\d+\sparts\sexpected\swithout\s'::'\sin\s.*"),
#     'IPV6_DCOLON_MUST_NOT_BE_FIRST': re.compile(r"^Leading\s':'\sonly\spermitted\sas\spart\sof\s'::'\sin\s.*"),
#     'IPV6_DCOLON_MUST_NOT_BE_LAST': re.compile(r"^Trailing\s':'\sonly\spermitted\sas\spart\sof\s'::'\sin\s.*"),
#     'IPV6_NOT_HEX_DIGITS': re.compile(r'^Only\shex\sdigits\spermitted\sin\s.*'),
#     'IPV6_TOO_MANY_CHARS_IN_SEGMENT': re.compile(r'^At\smost\s4\scharacters\spermitted\sin\s.*'),
#     'IPV4_NOT_4_OCTETS': re.compile(r'^Expected\s4\soctets\sin\s.*'),
#     'IPV4_EMPTY_OCTET': re.compile(r'^Empty\soctet\snot\spermitted.*'),
#     'IPV4_INVALID_CHAR': re.compile(r'^Only\sdecimal\sdigits\spermitted\sin\s.*'),
#     'IPV4_TOO_MANY_CHARS': re.compile(r'^At\smost\s3\scharacters\spermitted\sin\s.*'),
#     'IPV4_NOT_INT': re.compile(r'^Ambiguous\s\(octal/decimal\)\svalue\sin\s.*'),
#     'IPV4_OCTAL_ABOVE_255': re.compile(r'^Octet\s\d+\s\(>\s255\)\snot\spermitted.*')}
#
# IP_WARNING_FUNCS = {
#     'IP_IS_MULTICAST',
#     'IP_IS_PRIVATE',
#     'IP_IS_GLOBAL',
#     'IP_IS_UNSPECIFIED',
#     'IP_IS_RESERVED',
#     'IP_IS_LOOPBACK',
#     'IP_IS_LINK_LOCAL',
#     'IPV6_IS_SITE_LOCAL',
#
# }


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  Parse Objects  ">
# **********************************************************************************


class ValidateIPAddr(BaseParser):
    name = 'ip_address'
    messages = IP_MESSAGES
    try_v4 = True
    try_v6 = True
    # _v4_init_parse = CharNoSegment(look_for=ADDR_CHAR_IPV4)
    # _v6_init_parse = CharNoSegment(look_for=ADDR_CHAR_IPV6)
    # _v64_init_parse = CharNoSegment(look_for=ADDR_CHAR_IPV64)
    _addr_classes = {4: IPv4Address, 6: IPv6Address}
    _init_chars = {4: ADDR_CHAR_IPV4, 6: ADDR_CHAR_IPV64}
    _ip_version_str = {4: 'IPv4', 6: 'IPv6'}

    def __init__(self, *args, **kwargs):
        """
        if v4_only, will only return v4 addresses
        if v6_only, will only return v5 addresses
        otherwise will return both addresses.

        :param args:
        :param kwargs:
        """
        super(ValidateIPAddr, self).__init__(*args, **kwargs)
        if not self.try_v4 and not self.try_v6:
            raise AttributeError('either try_v4 OR try_v6 must be set.')
        if self.try_v4 and self.try_v6:
            self.try_both = True

    @staticmethod
    def _check_errors(err, check_version):

        for key, regex in IP_ERRORS[check_version].items():
            if regex.fullmatch(str(err)):
                return key
        return None

    @staticmethod
    def _check_reserved(addr_obj, check_version):
        tmp_ret = []

        exploded_str = addr_obj.exploded
        if check_version == 4:
            first_seg_len = len(exploded_str.split('.', maxsplit=1)[0])
        else:
            first_seg_len = 4

        for match_str, ranges in IP_RESERVED_RANGES[check_version][first_seg_len].items():
            if exploded_str.startswith(match_str):
                for res_addr in ranges:
                    if addr_obj in res_addr.block:
                        tmp_ret.append(res_addr.key)
                        if not res_addr.source_ok:
                            tmp_ret.append('IP_CANNOT_BE_SOURCE')
                        if not res_addr.destination_ok:
                            tmp_ret.append('IP_CANNOT_BE_DEST')
                        if not res_addr.forwardable:
                            tmp_ret.append('IP_CANNOT_BE_FORWARDED')
                        if not res_addr.globally_reachable:
                            tmp_ret.append('IP_NOT_GLOBALLY_REACHABLE')
                        break
                break
        return tmp_ret

    def _parse_v_any(self, parse_obj, position, version, addr_str=None):
        if addr_str is None:
            addr_fb = parse_obj(position, self._init_chars[version], caps_sensitive=False)
            addr_str = str(addr_fb)
        else:
            addr_fb = parse_obj.fb(position)

        if addr_str:
            try:
                addr_obj = self._addr_classes[version](addr_str)
            except AddressValueError as err:
                error_key = self._check_errors(err, version)
                if error_key:
                    addr_fb(error_key)
                else:
                    addr_fb('UNKNOWN')
                return None, addr_fb
            else:
                addr_fb(*self._check_reserved(addr_obj, version))
                addr_fb.data['ip_version'] = self._ip_version_str[version]

                return addr_obj, addr_fb
        return None, addr_fb

    def _parse_v6(self, parse_obj, position):
        addr_obj, addr_fb = self._parse_v_any(parse_obj, position, 6)
        if addr_obj is not None:
            v4_addr = None
            addr_str = str(addr_fb)
            if '.' in addr_str:
                addr_list = str(addr_fb).rsplit(':', maxsplit=1)
                v4_addr = addr_list[1]

            v4_addr = v4_addr or addr_obj.ipv4_mapped

            if v4_addr:
                v4_addr_obj, v4_fb = self._parse_v_any(parse_obj, position, 4, v4_addr)
                addr_fb(v4_fb)
                addr_fb.data['ip_version'] = 'IPv6-4'

        return addr_fb

    def _parse(self, tmp_ret, parse_obj, position, **kwargs):
        addr_v4 = None
        addr_v6 = None

        if parse_obj.at_end(position):
            raise ParsingLocalError(self, tmp_ret)

        if self.try_v4:
            junk, addr_v4 = self._parse_v_any(parse_obj, position, 4)
            if addr_v4:
                return tmp_ret(addr_v4)

        if self.try_v6:
            addr_v6 = self._parse_v6(parse_obj, position)
            if addr_v6:
                return tmp_ret(addr_v6)

        if addr_v4 is not None:
            tmp_ret(addr_v4)

        if addr_v6 is not None:
            tmp_ret(addr_v6)

        raise ParsingLocalError(self, tmp_ret)


class ValidateIPv4Addr(ValidateIPAddr):
    name = 'ipv4_address'
    try_v4 = True
    try_v6 = False


class ValidateIPv6Addr(ValidateIPAddr):
    name = 'ipv6_address'
    try_v4 = False
    try_v6 = True


validate_ip_addr = ValidateIPAddr()
validate_ipv4_addr = ValidateIPv4Addr()
validate_ipv6_addr = ValidateIPv6Addr()


# **********************************************************************************
# </editor-fold>
# **********************************************************************************
