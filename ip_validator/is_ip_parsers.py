from ValidationParser import *
from ipaddress import IPv4Address, IPv6Address, AddressValueError, IPv4Network, IPv6Network
from helpers.general import make_char_str
import re
from ValidationParser.parser_messages import RESULT_CODES
from collections import namedtuple

__all__ = ['ValidateIPAddr', 'ValidateIPv4Addr', 'ValidateIPv6Addr',
           'validate_ip_addr', 'validate_ipv4_addr', 'validate_ipv6_addr']


# **********************************************************************************
# <editor-fold desc="  IP Messages  ">
# **********************************************************************************


ReservedNames = namedtuple('ReservedNames', ('prefix', 'ipv6', 'block', 'key', 'source_ok', 'destination_ok', 'forwardable', 'globally_reachable'))

IP_RESERVED_RANGES = (
    ReservedNames('0', False, IPv4Network('0.0.0.0/8'), 'IPV4_SPEC_THIS_HOST', True, False, False, False),
    ReservedNames('10', False, IPv4Network('10.0.0.0/8'), 'IPV4_SPEC_PRIVATE', True, True, True, False),
    ReservedNames('100', False, IPv4Network('100.64.0.0/10'), 'IPV4_SPEC_SHARED', True, True, True, False),
    ReservedNames('127', False, IPv4Network('127.0.0.0/8'), 'IPV4_SPEC_LOOPBACK', False, False, False, False),
    ReservedNames('169', False, IPv4Network('169.254.0.0/16'), 'IPV4_SPEC_LINK_LOCAL', True, True, False, False),
    ReservedNames('172', False, IPv4Network('172.16.0.0/12'), 'IPV4_SPEC_PRIVATE', True, True, True, False),
    ReservedNames('192', False, IPv4Network('192.0.0.0/24'), 'IPV4_SPEC_PROTOCAL', False, False, False, False),
    ReservedNames('192', False, IPv4Network('192.0.0.0/29'), 'IPV4_SPEC_SVC_CONT', True, True, True, False),
    ReservedNames('192', False, IPv4Network('192.0.0.8/32'), 'IPV4_SPEC_DUMMY', True, False, False, False),
    ReservedNames('192', False, IPv4Network('192.0.0.9/32'), 'IPV4_SPEC_PC_ANYCAST', True, True, True, True),
    ReservedNames('192', False, IPv4Network('192.0.0.10/32'), 'IPV4_SPEC_NAT_ANYCAST', True, True, True, True),
    ReservedNames('192', False, IPv4Network('192.0.0.170/32'), 'IPV4_SPEC_64_DISC', False, False, False, False),
    ReservedNames('192', False, IPv4Network('192.0.0.171/32'), 'IPV4_SPEC_64_DISC', False, False, False, False),
    ReservedNames('192', False, IPv4Network('192.0.2.0/24'), 'IPV4_SPEC_DOC_TEST', False, False, False, False),
    ReservedNames('192', False, IPv4Network('192.31.196.0/24'), 'IPV4_SPEC_AS112', True, True, True, True),
    ReservedNames('192', False, IPv4Network('192.52.193.0/24'), 'IPV4_SPEC_AMI', True, True, True, True),
    ReservedNames('192', False, IPv4Network('192.168.0.0/16'), 'IPV4_SPEC_PRIVATE', True, True, True, False),
    ReservedNames('192', False, IPv4Network('192.175.48.0/24'), 'IPV4_SPEC_AS112', True, True, True, True),
    ReservedNames('198', False, IPv4Network('198.18.0.0/15'), 'IPV4_SPEC_BENCH', True, True, False, False),
    ReservedNames('198', False, IPv4Network('198.51.100.0/24'), 'IPV4_SPEC_DOC_TEST', False, False, False, False),
    ReservedNames('203', False, IPv4Network('203.0.113.0/24'), 'IPV4_SPEC_DOC_TEST', False, False, False, False),
    ReservedNames('2', False, IPv4Network('224.0.0.0/4'), 'IPV4_SPEC_MULTICAST', False, True, True, False),
    ReservedNames('240', False, IPv4Network('240.0.0.0/4'), 'IPV4_SPEC_RESERVE', False, False, False, False),
    ReservedNames('255', False, IPv4Network('255.255.255.255/32'), 'IPV4_SPEC_BCAST', False, True, False, False),

    ReservedNames('00', True, IPv6Network('::1/128'), 'IPV6_SPEC_LOOPBACK', False, False, False, False),
    ReservedNames('00', True, IPv6Network('::/128'), 'IPV6_SPEC_UNSPECIFIED', True, False, False, False),
    ReservedNames('00', True, IPv6Network('::ffff:0:0/96'), 'IPV6_SPEC_IPV4_MAP', False, False, False, False),
    ReservedNames('00', True, IPv6Network('::/8'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('0064', True, IPv6Network('64:ff9b::/96'), 'IPV6_SPEC_IPV4_TRANS', True, True, True, True),
    ReservedNames('0054', True, IPv6Network('64:ff9b:1::/48'), 'IPV6_SPEC_IPV4_TRANS', True, True, True, False),
    ReservedNames('01', True, IPv6Network('100::/64'), 'IPV6_SPEC_DISCARD', True, True, True, False),
    ReservedNames('01', True, IPv6Network('100::/8'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('02', True, IPv6Network('200::/7'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('03', True, IPv6Network('200::/7'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('04', True, IPv6Network('400::/6'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('05', True, IPv6Network('400::/6'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('06', True, IPv6Network('400::/6'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('07', True, IPv6Network('400::/6'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('08', True, IPv6Network('800::/5'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('09', True, IPv6Network('800::/5'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('1', True, IPv6Network('1000::/4'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('2001', True, IPv6Network('2001::/23'), 'IPV6_SPEC_PROTOCOL', False, False, False, False),
    ReservedNames('2001', True, IPv6Network('2001::/32'), 'IPV6_SPEC_TEREDO', True, True, True, False),
    ReservedNames('2001', True, IPv6Network('2001:1::1/128'), 'IPV6_SPEC_PC_ANYCAST', True, True, True, True),
    ReservedNames('2001', True, IPv6Network('2001:1::2/128'), 'IPV6_SPEC_NAT_ANYCAST', True, True, True, True),
    ReservedNames('2001', True, IPv6Network('2001:2::/48'), 'IPV6_SPEC_BENCHMARK', True, True, True, False),
    ReservedNames('2001', True, IPv6Network('2001:3::/32'), 'IPV6_SPEC_AMT', True, True, True, True),
    ReservedNames('2001', True, IPv6Network('2001:4:112::/48'), 'IPV6_SPEC_AS112', True, True, True, True),
    ReservedNames('2001', True, IPv6Network('2001:5::/32'), 'IPV6_SPEC_LISP', True, True, True, True),
    ReservedNames('2001', True, IPv6Network('2001:20::/28'), 'IPV6_SPEC_ORCHID', True, True, True, True),
    ReservedNames('2001', True, IPv6Network('2001:db8::/32'), 'IPV6_SPEC_DOC_TEST', False, False, False, False),
    ReservedNames('2002', True, IPv6Network('2002::/16'), 'IPV6_SPEC_6TO4', True, True, True, False),
    ReservedNames('2620', True, IPv6Network('2620:4f:8000::/48'), 'IPV6_SPEC_AS112', True, True, True, True),
    ReservedNames('4', True, IPv6Network('4000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('5', True, IPv6Network('4000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('6', True, IPv6Network('6000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('7', True, IPv6Network('6000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('8', True, IPv6Network('8000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('9', True, IPv6Network('8000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('a', True, IPv6Network('A000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('b', True, IPv6Network('A000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('c', True, IPv6Network('C000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('d', True, IPv6Network('C000::/3'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('e', True, IPv6Network('E000::/4'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('f', True, IPv6Network('F000::/5'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('f', True, IPv6Network('F800::/6'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('f', True, IPv6Network('fc00::/7'), 'IPV6_SPEC_UNIQUE_LOCAL', True, True, True, False),
    ReservedNames('f', True, IPv6Network('fc00::/7'), 'IPV6_SPEC_UNIQUE_LOCAL', True, True, True, False),
    ReservedNames('f', True, IPv6Network('fe80::/10'), 'IPV6_SPEC_LINK_LOCAL', True, True, False, False),
    ReservedNames('f', True, IPv6Network('FE00::/9'), 'IPV6_SPEC_RESERVED', True, True, True, False),
    ReservedNames('f', True, IPv6Network('FEC0::/10'), 'IPV6_SPEC_SITE_LOCAL', True, True, True, False),
    ReservedNames('f', True, IPv6Network('ff00::/8'), 'IPV6_SPEC_MULTICAST', False, True, True, False),
)

# TWO_DIGIT = '12'
ADDR_CHAR_IPV4 = '0123456789.'
ADDR_CHAR_IPV6 = make_char_str(HEXDIG, COLON)
ADDR_CHAR_IPV64 = make_char_str(HEXDIG, ADDR_CHAR_IPV4, COLON)


IP_MESSAGES = [
        {'key': 'EMPTY_IP_ADDRESS',
         'description': 'The address was empty',
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV4_NOT_4_OCTETS',
         'description': "Expected 4 octets",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV4_EMPTY_OCTET',
         'description': "Empty octet not permitted",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV4_INVALID_CHAR',
         'description': "Only decimal digits permitted",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV4_TOO_MANY_CHARS',
         'description': "At most 3 characters permitted in octet",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV4_NOT_INT',
         'description': "Ambiguous (octal/decimal) value not permitted",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV4_OCTAL_ABOVE_255',
         'description': "Octet > 255 not permitted",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV6_AT_LEAST_2_COLONS',
         'description': 'An IPv6 address needs at least 2 colons (3 parts).',
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV6_AT_MOST_8_COLONS',
         'description': "An IPv6 address can't have more than 8 colons (9 parts).",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV6_AT_MOST_1_DCOLON',
         'description': "Can't have more than one '::'",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV6_TOO_MANY_PARTS_WITH_DCOLON',
         'description': "Incorrect number of parts with ::",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV6_TOO_FEW_OR_MANY_PARTS',
         'description': "Incorrect number of parts without ::",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV6_DCOLON_MUST_NOT_BE_FIRST',
         'description': "There must be something before the ::",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV6_DCOLON_MUST_NOT_BE_LAST',
         'description': "There must be something after the ::",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV6_NOT_HEX_DIGITS',
         'description': "Only hex digits permitted",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV6_TOO_MANY_CHARS_IN_SEGMENT',
         'description': "At most 4 characters permitted",
         'status': RESULT_CODES.ERROR},

        {'key': 'IPV4_SPEC_THIS_HOST',
         'description': '"This host on this network"',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC1122]  Section 3.2.1.3'], },

        # 'source_ok', 'destination_ok', 'forwardable', 'globally_reachable'

        {'key': 'IP_CANNOT_BE_SOURCE',
         'description': 'This address cannot be a source address',
         'status': RESULT_CODES.WARNING,
         'references': [], },

        {'key': 'IP_CANNOT_BE_DEST',
         'description': 'This address cannot be a destination address',
         'status': RESULT_CODES.WARNING,
         'references': [], },
        {'key': 'IP_CANNOT_BE_FORWARDED',
         'description': 'This address cannot be forwarded by routers',
         'status': RESULT_CODES.WARNING,
         'references': [], },
        {'key': 'IP_NOT_GLOBALLY_REACHABLE',
         'description': 'This address cannot be reached from the internet',
         'status': RESULT_CODES.WARNING,
         'references': [], },



        {'key': 'IPV4_SPEC_PRIVATE',
         'description': 'Private-Use',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC1918]'], },
        {'key': 'IPV4_SPEC_SHARED',
         'description': 'Shared Address Space',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC6598]'], },
        {'key': 'IPV4_SPEC_LOOPBACK',
         'description': 'Loopback (Several protocols have been granted exceptions to this rule. For examples  see [RFC8029] and [RFC5884])',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC1122]  Section 3.2.1.3'], },
        {'key': 'IPV4_SPEC_LINK_LOCAL',
         'description': 'Link Local',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC3927]'], },
        {'key': 'IPV4_SPEC_PRIVATE',
         'description': 'Private-Use',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC1918]'], },
        {'key': 'IPV4_SPEC_PROTOCAL',
         'description': 'IETF Protocol Assignments',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC6890]  Section 2.1'], },
        {'key': 'IPV4_SPEC_SVC_CONT',
         'description': 'IPv4 Service Continuity Prefix',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7335]'], },
        {'key': 'IPV4_SPEC_DUMMY',
         'description': 'IPv4 dummy address',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7600]'], },
        {'key': 'IPV4_SPEC_PC_ANYCAST',
         'description': 'Port Control Protocol Anycast',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7723]'], },
        {'key': 'IPV4_SPEC_NAT_ANYCAST',
         'description': 'Traversal Using Relays around NAT Anycast',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC8155]'], },
        {'key': 'IPV4_SPEC_64_DISC',
         'description': 'NAT64/DNS64 Discovery',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7050]  Section 2.2'], },
        {'key': 'IPV4_SPEC_64_DISC',
         'description': 'NAT64/DNS64 Discovery',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7050]  Section 2.2'], },
        {'key': 'IPV4_SPEC_DOC_TEST',
         'description': 'Documentation (TEST-NET-1)',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC5737]'], },
        {'key': 'IPV4_SPEC_AS112',
         'description': 'AS112-v4',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7535]'], },
        {'key': 'IPV4_SPEC_AMI',
         'description': 'AMT',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7450]'], },
        {'key': 'IPV4_SPEC_PRIVATE',
         'description': 'Private-Use',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC1918]'], },
        {'key': 'IPV4_SPEC_AS112',
         'description': 'Direct Delegation AS112 Service',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7534]'], },
        {'key': 'IPV4_SPEC_BENCH',
         'description': 'Benchmarking',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2544]'], },
        {'key': 'IPV4_SPEC_DOC_TEST',
         'description': 'Documentation (TEST-NET-2)',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC5737]'], },
        {'key': 'IPV4_SPEC_DOC_TEST',
         'description': 'Documentation (TEST-NET-3)',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC5737]'], },
        {'key': 'IPV4_SPEC_MULTICAST',
         'description': 'Multicast Addresses',
         'status': RESULT_CODES.WARNING,
         'references': ['[3171]'], },
        {'key': 'IPV4_SPEC_RESERVE',
         'description': 'Reserved',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC1112]  Section 4'], },
        {'key': 'IPV4_SPEC_BCAST',
         'description': 'Limited Broadcast',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC8190][RFC919]  Section 7'], },
        {'key': 'IPV6_SPEC_LOOPBACK',
         'description': 'Loopback Address',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC4291]'], },
        {'key': 'IPV6_SPEC_UNSPECIFIED',
         'description': 'Unspecified Address',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC4291]'], },
        {'key': 'IPV6_SPEC_IPV4_MAP',
         'description': 'IPv4-mapped Address',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC4291]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_IPV4_TRANS',
         'description': 'IPv4-IPv6 Translat.',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC6052]'], },
        {'key': 'IPV6_SPEC_IPV4_TRANS',
         'description': 'IPv4-IPv6 Translat.',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC-ietf-v6ops-v4v6-xlat-prefix-02]'], },
        {'key': 'IPV6_SPEC_DISCARD',
         'description': 'Discard-Only Address Block',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC6666]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_PROTOCOL',
         'description': 'IETF Protocol Assignments (Unless allowed by a more specific allocation.)',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2928]'], },
        {'key': 'IPV6_SPEC_TEREDO',
         'description': 'TEREDO (See Section 5 of [RFC4380] for details.)',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC4380][RFC8190]'], },
        {'key': 'IPV6_SPEC_PC_ANYCAST',
         'description': 'Port Control Protocol Anycast',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7723]'], },
        {'key': 'IPV6_SPEC_NAT_ANYCAST',
         'description': 'Traversal Using Relays around NAT Anycast',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC8155]'], },
        {'key': 'IPV6_SPEC_BENCHMARK',
         'description': 'Benchmarking',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC5180]'], },
        {'key': 'IPV6_SPEC_AMT',
         'description': 'AMT',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7450]'], },
        {'key': 'IPV6_SPEC_AS112',
         'description': 'AS112-v6',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7535]'], },
        {'key': 'IPV6_SPEC_LISP',
         'description': 'EID Space for LISP (Managed by RIPE NCC) (Can be used as a multicast source as well. To be used as EID space by routers enabled by LISP [RFC6830].)',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7954]'], },
        {'key': 'IPV6_SPEC_ORCHID',
         'description': 'ORCHIDv2',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7343]'], },
        {'key': 'IPV6_SPEC_DOC_TEST',
         'description': 'Documentation',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC3849]'], },
        {'key': 'IPV6_SPEC_6TO4',
         'description': '6to4 (See [RFC3056] for details.)',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC3056]'], },
        {'key': 'IPV6_SPEC_AS112',
         'description': 'Direct Delegation AS112 Service',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC7534]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_UNIQUE_LOCAL',
         'description': 'Unique-Local (See [RFC4193] for more details on the routability of Unique-Local addresses.  The Unique-Local prefix is drawn from the IPv6 Global Unicast Address range  but is specified as not globally routed.)',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC4193][RFC8190]'], },
        {'key': 'IPV6_SPEC_UNIQUE_LOCAL',
         'description': 'Unique-Local (See [RFC4193] for more details on the routability of Unique-Local addresses.  The Unique-Local prefix is drawn from the IPv6 Global Unicast Address range  but is specified as not globally routed.)',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC4193][RFC8190]'], },
        {'key': 'IPV6_SPEC_LINK_LOCAL',
         'description': 'Link-Local Unicast',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC4291]'], },
        {'key': 'IPV6_SPEC_RESERVED',
         'description': 'Reserved - Unallocated',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        {'key': 'IPV6_SPEC_SITE_LOCAL',
         'description': 'Site Local Unicast',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC4291]'], },
        {'key': 'IPV6_SPEC_MULTICAST',
         'description': 'Multicast Addresses',
         'status': RESULT_CODES.WARNING,
         'references': ['[RFC2373]'], },
        ]


IP_ERRORS = {
    'EMPTY_IP_ADDRESS': re.compile(r'^Address\scannot\sbe\sempty.*'),
    'IPV4_NOT_4_OCTETS': re.compile(r'^Expected\s4\soctets\sin\s.*'),
    'IPV4_EMPTY_OCTET': re.compile(r'^Empty\soctet\snot\spermitted.*'),
    'IPV4_INVALID_CHAR': re.compile(r'^Only\sdecimal\sdigits\spermitted\sin\s.*'),
    'IPV4_TOO_MANY_CHARS': re.compile(r'^At\smost\s3\scharacters\spermitted\sin\s.*'),
    'IPV4_NOT_INT': re.compile(r'^Ambiguous\s\(octal/decimal\)\svalue\sin\s.*'),
    'IPV4_OCTAL_ABOVE_255': re.compile(r'^Octet\s\d+\s\(>\s255\)\snot\spermitted.*'),
    'IPV6_AT_LEAST_2_COLONS': re.compile(r'^At\sleast\s\d+\sparts\sexpected\sin\s.*'),
    'IPV6_AT_MOST_8_COLONS': re.compile(r'^At\smost\s\d+\scolons\spermitted\sin\s.*'),
    'IPV6_AT_MOST_1_DCOLON': re.compile(r"^At\smost\sone\s'::'\spermitted\sin\s.*"),
    'IPV6_TOO_MANY_PARTS_WITH_DCOLON': re.compile(r"^Expected\sat\smost\s\d+\sother\sparts\swith\s'::'\sin\s.*"),
    'IPV6_TOO_FEW_OR_MANY_PARTS': re.compile(r"^Exactly\s\d+\sparts\sexpected\swithout\s'::'\sin\s.*"),
    'IPV6_DCOLON_MUST_NOT_BE_FIRST': re.compile(r"^Leading\s':'\sonly\spermitted\sas\spart\sof\s'::'\sin\s.*"),
    'IPV6_DCOLON_MUST_NOT_BE_LAST': re.compile(r"^Trailing\s':'\sonly\spermitted\sas\spart\sof\s'::'\sin\s.*"),
    'IPV6_NOT_HEX_DIGITS': re.compile(r'^Only\shex\sdigits\spermitted\sin\s.*'),
    'IPV6_TOO_MANY_CHARS_IN_SEGMENT': re.compile(r'^At\smost\s4\scharacters\spermitted\sin\s.*')}


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
    v4_only = False
    v6_only = False
    v4_and_v6 = True
    _v4_init_parse = CharNoSegment(look_for=ADDR_CHAR_IPV4)
    _v6_init_parse = CharNoSegment(look_for=ADDR_CHAR_IPV6)
    _v64_init_parse = CharNoSegment(look_for=ADDR_CHAR_IPV64)

    def __init__(self, *args, **kwargs):
        """
        if v4_only, will only return v4 addresses
        if v6_only, will only return v5 addresses
        otherwise will return both addresses.

        :param args:
        :param kwargs:
        """
        super(ValidateIPAddr, self).__init__(*args, **kwargs)
        if self.v4_only and self.v6_only:
            raise AttributeError('v4_only AND v6 only cannot be set')
        if self.v4_only or self.v6_only:
            self.v4_and_v6 = False

    @staticmethod
    def _check_errors(err, check_v4):
        for key, regex in IP_ERRORS.items():
            if check_v4 and key.startswith('IPV6'):
                continue
            if regex.fullmatch(str(err)):
                return key
        return None

    @staticmethod
    def _check_reserved(addr_obj, check_v4):
        tmp_ret = []
        exploded_str = addr_obj.exploded
        for res_addr in IP_RESERVED_RANGES:
            if check_v4 and res_addr.ipv6:
                continue
            if exploded_str.startswith(res_addr.prefix):
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
        return tmp_ret

    def _parse(self, tmp_ret, parse_obj, position, **kwargs):

        if parse_obj.at_end(position):
            raise WrapperStop(self, tmp_ret)

        if self.v4_only or self.v4_and_v6:
            addr_fb = self._v4_init_parse(parse_obj, position)
            if addr_fb:
                try:
                    addr_obj = IPv4Address(str(addr_fb))
                except AddressValueError as err:
                    error_key = self._check_errors(err, True)
                    if self.v4_only and error_key is not None:
                        return tmp_ret(error_key)
                else:
                    tmp_ret.data['ip_version'] = 'IPv4'
                    return tmp_ret(*self._check_reserved(addr_obj, True))

        addr_fb = self._v64_init_parse(parse_obj, position)
        if addr_fb:
            addr_str = str(addr_fb)
            try:
                addr_obj = IPv6Address(addr_str)
            except AddressValueError as err:
                return tmp_ret(self._check_errors(err, False))
            else:
                tmp_ret.data['ip_version'] = 'IPv6'
                tmp_ret(*self._check_reserved(addr_obj, True))

                v4_addr = None

                if '.' in addr_str:
                    addr_list = addr_str.rsplit(':', maxsplit=1)
                    v4_addr = addr_list[1]

                v4_addr = v4_addr or addr_obj.ipv4_mapped

                if v4_addr:
                    tmp_ret.data['ip_version'] = 'IPv6-4'
                    try:
                        addr_obj = IPv4Address(str(addr_fb))
                    except AddressValueError as err:
                        error_key = tmp_ret(self._check_errors(err, True))
                        if error_key is None:
                            error_key = 'UNKNOWN_ERROR'
                        return tmp_ret(error_key)
                    else:
                        return tmp_ret(*self._check_reserved(addr_obj, True))
                return tmp_ret
        else:
            raise WrapperStop(self, tmp_ret)


class ValidateIPv4Addr(ValidateIPAddr):
    name = 'ipv4_address'
    v4_only = True
    v6_only = False
    v4_and_v6 = False


class ValidateIPv6Addr(ValidateIPAddr):
    name = 'ipv6_address'
    v4_only = False
    v6_only = True
    v4_and_v6 = False


validate_ip_addr = ValidateIPAddr()
validate_ipv4_addr = ValidateIPv4Addr()
validate_ipv6_addr = ValidateIPv6Addr()


# **********************************************************************************
# </editor-fold>
# **********************************************************************************
