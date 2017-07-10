from helpers.parser_helpers import *


# **********************************************************************************
# <editor-fold desc="  STRING CONSTANTS  ">
# **********************************************************************************

"""
TWO_DIGIT = '12'
ADDR_LIT_IPV4 = '0123456789.'
ADDR_LIT_IPV6 = make_char_str(HEXDIG, ADDR_LIT_IPV4, COLON)
"""


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


class three_digit(PHBaseChar):
    look_for = DIGIT
    max_char_count = 3


class snum(PHBase):
    def _parse(self, parse_obj, position, **kwargs):
        tmp_ret = three_digit(parse_obj, position)
        if tmp_ret:
            tmp_str = parse_obj.mid(position, tmp_ret.l)

            tmp_digit = int(tmp_str)
            if tmp_digit > 255:
                return parse_obj.fb(position)

        return tmp_ret


@email_parser(error_text=SNUM_ERRORS)
def snum(email_info, position):
    """
            Snum           = 1*3DIGIT
                          ; representing a decimal integer
                          ; value in the range 0 through 255
    """
    tmp_ret = three_digit(email_info, position)
    if tmp_ret:
        tmp_str = email_info.mid(position, tmp_ret.l)

        tmp_digit = int(tmp_str)
        if tmp_digit > 255:
            return email_info.fb(position)

    return tmp_ret


'''


def ipv6_segment(email_info, position, min_count=1, max_count=7):
    tmp_ret = email_info.fb(position)
    tmp_ret += ipv6_hex(email_info, position)

    if tmp_ret:
        if max_count == 1:
            return 1, tmp_ret

        if not email_info.at_end(position + tmp_ret.l + 1) and \
                email_info[position + tmp_ret.l] == ':' and \
                email_info[position + tmp_ret.l + 1] == ':' and \
                min_count <= 1:
            # email_info.add_note_trace('Double Colons found, exiting')
            return 1, tmp_ret

        # tmp_colon_str = {'string_in': COLON, 'min_count': 1, 'max_count': 1}
        tmp_count, tmp_ret_2 = parse_loop(
            email_info,
            position + tmp_ret,
            parse_and,
            colon,
            ipv6_hex,
            min_loop=min_count - 1,
            max_loop=max_count - 1,
            ret_count=True)
    else:
        return 0, email_info.fb(position)

    if tmp_ret_2:
        return tmp_count + 1, tmp_ret(tmp_ret_2)
    else:
        return 0, email_info.fb(position)


@email_parser(pass_diags='RFC5322_IPV4_ADDR')
def ipv4_address_literal(email_info, position):
    """
    IPv4-address-literal  = Snum 3("."  Snum)

    RFC5322_IPV4_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_ret += parse_and(email_info, position, snum, single_dot, snum, single_dot, snum, single_dot, snum)

    return tmp_ret



@email_parser(error_text=SNUM_ERRORS)
def snum(email_info, position):
    """
            Snum           = 1*3DIGIT
                          ; representing a decimal integer
                          ; value in the range 0 through 255
    """
    tmp_ret = three_digit(email_info, position)
    if tmp_ret:
        tmp_str = email_info.mid(position, tmp_ret.l)

        tmp_digit = int(tmp_str)
        if tmp_digit > 255:
            return email_info.fb(position)

    return tmp_ret

@email_parser()
def ipv6_addr(email_info, position):
    """
            IPv6-addr      = IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp
    """
    tmp_ret = email_info.fb(position)

    dot_count = email_info.count(position, DOT, until_char=CLOSESQBRACKET)
    colon_count = email_info.count(position, COLON, until_char=CLOSESQBRACKET)
    if colon_count > 0:
        dcolon_count = email_info.count(position, DOUBLECOLON, until_char=CLOSESQBRACKET)
    else:
        dcolon_count = 0

    # email_info.add_note_trace('Dot count = ' + str(dot_count))
    if dot_count:
        if dcolon_count:
            tmp_ret += ipv6v4_comp(email_info, position)
        else:
            tmp_ret += ipv6v4_full(email_info, position)
    else:
        if dcolon_count:
            tmp_ret += ipv6_comp(email_info, position)
        else:
            tmp_ret += ipv6_full(email_info, position)

    #    tmp_ret += ipv6v4_full(email_info, position) or ipv6v4_comp(email_info, position)
    # else:
    #    tmp_ret += ipv6_full(email_info, position) or ipv6_comp(email_info, position)

    return tmp_ret


@email_parser()
def ipv6_hex(email_info, position):
    """
    IPv6-hex       = 1*4HEXDIG
    """
    return hexdigit(email_info, position)


@email_parser(pass_diags='RFC5322_IPV6_FULL_ADDR')
def ipv6_full(email_info, position):
    """
    IPv6-full = IPv6-hex 7(":" IPv6-hex)
    RFC5322_IPV6_FULL_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_count, tmp_ret_2 = ipv6_segment(email_info, position, max_count=8, min_count=8)
    if tmp_ret_2:
        return tmp_ret(tmp_ret_2)
    else:
        return email_info.fb(position)


@email_parser(pass_diags='RFC5322_IPV6_COMP_ADDR')
def ipv6_comp(email_info, position):
    """
            IPv6-comp      = [IPv6-hex *5(":" IPv6-hex)] "::"
                          [IPv6-hex *5(":" IPv6-hex)]
                          ; The "::" represents at least 2 16-bit groups of
                          ; zeros.  No more than 6 groups in addition to the
                          ; "::" may be present.
          RFC5322_IPV6_COMP_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_pre_count, tmp_ret_2 = ipv6_segment(email_info, position, min_count=1, max_count=6)

    if not tmp_ret_2:
        return email_info.fb(position)
    tmp_ret += tmp_ret_2

    tmp_ret_2 = double_colon(email_info, position + tmp_ret)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2

    tmp_post_count, tmp_ret_2 = ipv6_segment(email_info, position + tmp_ret.l, min_count=1, max_count=6)

    if not tmp_ret_2:
        tmp_ret_2 = ipv6_hex(email_info, position + tmp_ret.l)
        if not tmp_ret_2:
            return email_info.fb(position)
        tmp_post_count = 1

    tmp_ret += tmp_ret_2
    if (tmp_pre_count + tmp_post_count) > 6:
        # email_info.add_note_trace('Segment count: %s + %s, exceeds 6, failing' % (tmp_pre_count, tmp_post_count))
        return email_info.fb(position)

    else:
        # email_info.add_note_trace('Segment count: %s + %s, passing' % (tmp_pre_count, tmp_post_count))
        return tmp_ret


@email_parser(pass_diags='RFC5322_IPV6_IPV4_ADDR')
def ipv6v4_full(email_info, position):
    """
    IPv6v4-full  = IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal

    RFC5322_IPV6_IPV4_ADDR

    """
    tmp_ret = email_info.fb(position)
    tmp_count, tmp_ret_2 = ipv6_segment(email_info, position, min_count=6, max_count=6)
    tmp_ret += tmp_ret_2

    if tmp_ret_2:
        tmp_ret_2 = colon(email_info, position + tmp_ret)
    else:
        return email_info.fb(position)

    if tmp_ret_2:
        tmp_ret += tmp_ret_2
        tmp_ret_2 = ipv4_address_literal(email_info, position + tmp_ret.l)
    else:
        return email_info.fb(position)

    if tmp_ret_2:
        tmp_ret += tmp_ret_2
    else:
        return email_info.fb(position)

    tmp_ret.remove('RFC5322_IPV4_ADDR')
    return tmp_ret


@email_parser(pass_diags='RFC5322_IPV6_IPV4_COMP_ADDR')
def ipv6v4_comp(email_info, position):
    """
            IPv6v4-comp    = [IPv6-hex *3(":" IPv6-hex)] "::"
                          [IPv6-hex *3(":" IPv6-hex) ":"]
                          IPv4-address-literal
                          ; The "::" represents at least 2 16-bit groups of
                          ; zeros.  No more than 4 groups in addition to the
                          ; "::" and IPv4-address-literal may be present.
            RFC5322_IPV6_IPV4_COMP_ADDR
    """
    tmp_ret = email_info.fb(position)
    tmp_pre_count, tmp_ret_2 = ipv6_segment(email_info, position, min_count=1, max_count=3)
    tmp_ret += tmp_ret_2

    if not tmp_ret:
        return email_info.fb(position)

    tmp_ret_2 = double_colon(email_info, position + tmp_ret)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2

    colon_count = email_info.count(position + tmp_ret, COLON, until_char=CLOSESQBRACKET)
    if colon_count > 3:
        return email_info.fb(position)

    tmp_post_count, tmp_ret_2 = ipv6_segment(email_info, position + tmp_ret.l,
                                             min_count=colon_count, max_count=colon_count)

    # email_info.add_note_trace('should be start of IPv4 segment')

    tmp_ret += tmp_ret_2
    tmp_ret_2 = colon(email_info, position + tmp_ret)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2
    tmp_ret_2 = ipv4_address_literal(email_info, position + tmp_ret.l)

    if not tmp_ret_2:
        return email_info.fb(position)

    tmp_ret += tmp_ret_2

    if tmp_pre_count + tmp_post_count > 4:
        # email_info.add_note_trace('Segment count: %s + %s, exceeds 4, failing' % (tmp_pre_count, tmp_post_count))
        return email_info.fb(position)

    else:
        # email_info.add_note_trace('Segment count: %s + %s, passing' % (tmp_pre_count, tmp_post_count))
        tmp_ret.remove('RFC5322_IPV4_ADDR')
        return tmp_ret
