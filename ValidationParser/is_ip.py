from ValidationParser.parser import parse
from ValidationParser.is_ip_parsers import validate_ipv4_addr, validate_ipv6_addr, validate_ip_addr

__all__ = ['is_ip', 'is_ipv4', 'is_ipv6']


def is_ipv4(parse_item, def_empty_msg='EMPTY_IP_ADDRESS', **kwargs):

    return parse(parse_item, validate_ipv4_addr, begin=0,
                 def_empty_msg=def_empty_msg, **kwargs)


def is_ipv6(parse_item, def_empty_msg='EMPTY_IP_ADDRESS', **kwargs):

    return parse(parse_item, validate_ipv6_addr, begin=0,
                 def_empty_msg=def_empty_msg, **kwargs)


def is_ip(parse_item, def_empty_msg='EMPTY_IP_ADDRESS', **kwargs):

    return parse(parse_item, validate_ip_addr, begin=0,
                 def_empty_msg=def_empty_msg, **kwargs)
