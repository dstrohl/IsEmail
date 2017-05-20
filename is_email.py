import email_parsers as p
from helpers.email_dns_helper.dns_functions import dns_lookup
from helpers.footballs.footballs import ParsingError, ParseShortResult, ParseFullResult, EmailInfo
from helpers.meta_data.meta_data import ISEMAIL_DNS_LOOKUP_LEVELS, ISEMAIL_DOMAIN_TYPE


def parse(email_in, parser=None, **kwargs):
    return_football = kwargs.pop('return_football', False)
    position = kwargs.pop('position', 0)

    if email_in is None:
        email_in = ''

    email_info = EmailInfo(email_in=str(email_in), **kwargs)

    if email_in == '':
        tmp_ret = email_info.fb(0)
        tmp_ret('ERR_EMPTY_ADDRESS')
        if return_football:
            return tmp_ret
        return finish(email_info, tmp_ret)

    if parser is None:
        parser = p.address_spec

    elif isinstance(parser, str):
        parser = getattr(position, parser)

    try:
        tmp_ret = parser(0, **kwargs)
    except ParsingError as err:
        tmp_ret = err.results

    if return_football:
        return tmp_ret

    return tmp_ret.finish(email_info, tmp_ret)


def finish(email_obj, results):
    if email_obj.verbose == 0:
        if email_obj.dns_lookup_level == ISEMAIL_DNS_LOOKUP_LEVELS.NO_LOOKUP or email_obj.domain_type != ISEMAIL_DOMAIN_TYPE.DNS:
            if email_obj.raise_on_error and results.error:
                raise ParsingError(results)
            return not results.error

    parts = dict(
        local_part=[],
        domain_part=[],
        clean_local_part=[],
        clean_domain_part=[],
        full_local_part=[],
        full_domain_part=[])

    if results and email_obj.at_loc is not None:
        in_local = True
        in_literal = False
        index = 0

        while index < len(email_obj.email_in):

            tmp_char = email_obj.email_in[index]

            if index == email_obj.at_loc:
                in_local = False
            elif index in email_obj.local_comments:
                parts['full_local_part'].append('(%s)' % email_obj.local_comments[index])
                index += len(email_obj.local_comments[index]) + 1
            elif index in email_obj.domain_comments:
                parts['full_domain_part'].append('(%s)' % email_obj.domain_comments[index])
                index += len(email_obj.domain_comments[index]) + 1

            elif tmp_char in '"[]':
                if in_local:
                    parts['clean_local_part'].append(tmp_char)
                    parts['full_local_part'].append(tmp_char)
                else:
                    parts['clean_domain_part'].append(tmp_char)
                    parts['full_domain_part'].append(tmp_char)
                if in_literal:
                    in_literal = False
                else:
                    if email_obj.domain_type == ISEMAIL_DOMAIN_TYPE.IPv6 and tmp_char == '[':
                        parts['clean_domain_part'].extend('IPv6:')
                        parts['full_domain_part'].extend('IPv6:')
                        index += 5
                    in_literal = True

            elif not in_literal and tmp_char in ' \t\r\n':
                pass
            else:
                if in_local:
                    parts['local_part'].append(tmp_char)
                    parts['clean_local_part'].append(tmp_char)
                    parts['full_local_part'].append(tmp_char)
                else:
                    parts['domain_part'].append(tmp_char)
                    parts['clean_domain_part'].append(tmp_char)
                    parts['full_domain_part'].append(tmp_char)
            index += 1

        parts['local_part'] = ''.join(parts['local_part'])
        parts['domain_part'] = ''.join(parts['domain_part'])
        parts['clean_local_part'] = ''.join(parts['clean_local_part'])
        parts['clean_domain_part'] = ''.join(parts['clean_domain_part'])
        parts['full_local_part'] = ''.join(parts['full_local_part'])
        parts['full_domain_part'] = ''.join(parts['full_domain_part'])

        if email_obj.domain_type == ISEMAIL_DOMAIN_TYPE.GENERAL_LIT:
            parts['domain_part'] = parts['domain_part'].split(':', 1)

        elif email_obj.domain_type == ISEMAIL_DOMAIN_TYPE.DNS:
            if 'VALID' in email_obj:
                tmp_dns = dns_lookup(
                    parts['clean_domain_part'],
                    email_obj.dns_lookup_level,
                    servers=email_obj.dns_servers,
                    timeout=email_obj.dns_timeout,
                    raise_on_comm_error=email_obj.raise_on_error,
                    tld_list=email_obj.tld_list,
                )

                if tmp_dns:
                    results(tmp_dns)
                    results.remove(diag='VALID')
                    # email_obj._fix_result(email_obj.results[-1])

    else:
        parts = None

    if email_obj.raise_on_error and results.error:
        raise ParsingError(email_obj)

    if email_obj.verbose == 0:
        return not email_obj.error
    elif email_obj.verbose == 1:
        return ParseShortResult(
            email_in=email_obj.email_in,
            parts=parts,
            results=email_obj.results)
    else:
        return ParseFullResult(
            email_in=email_obj.email_in,
            parts=parts,
            results=results,
            history=results._history,
            local_comments=email_obj.local_comments,
            domain_comments=email_obj.domain_comments,
            domain_type=email_obj.domain_type,
            email_info=email_obj
        )

