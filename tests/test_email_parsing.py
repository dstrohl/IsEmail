import unittest
from parse_objects import make_char_str, EmailParser
from tests.email_test_data import TESTS
from meta_data import ISEMAIL_DNS_LOOKUP_LEVELS


def full_ret_string(test_num, test_string, test_ret, extra_string=''):
    tmp_ret = '\n\n'

    tmp_ret += 'Run Number: %s\n' % test_num
    tmp_ret += 'Checked String: %r\n\n' % test_string

    tmp_ret += 'Length: %s\n' % test_ret.length

    tmp_ret += 'Error Flag: %r\n' % test_ret.error
    tmp_ret += 'Local_part: %r\n' % test_ret.local
    tmp_ret += 'Domain_part: %r\n' % test_ret.domain

    tmp_ret += 'Local_comments: %r\n' % test_ret.local_comments
    tmp_ret += 'Domain_comments: %r\n' % test_ret.domain_comments

    ret_codes = list(test_ret.diags())
    ret_codes.sort()

    tmp_ret += 'Codes: %r\n' % ret_codes

    tmp_hist = test_ret.history.short_desc()

    tmp_ret += 'History: %s\n' % tmp_hist

    tmp_ret += 'Extra Info: %r\n\n' % extra_string

    tmp_ret += 'Trace:\n%s\n\n' % test_ret.trace_str

    return tmp_ret


class TestEmailParser(unittest.TestCase):
    maxDiff = None
    """
    tmp_dict = dict(
        id_num=id_num,
        addr=addr,
        cat=category,
        diag=diag,
        codes=[],
        comment=comment)
    """

    def fix_addr(self, addr_in):
        if '{{' not in addr_in:
            return addr_in
        tmp_ret = []
        while '{{' not in addr_in and ')}' not in addr_in:

            pre_text, addr_in = addr_in.split('{{', 1)
            char_num, addr_in = addr_in.split('}}', 1)
            tmp_ret.append(pre_text)
            tmp_ret.append(chr(int(char_num)))
        tmp_ret.append(addr_in)
        return ''.join(tmp_ret)


    def test_full_parse(self):
        emv = EmailParser(
            verbose=3,
            trace_filter=999,
            dns_lookup_level=ISEMAIL_DNS_LOOKUP_LEVELS.MX_RECORD,
            raise_on_error=False)

        LIMIT_TO = -1

        if LIMIT_TO != -1:
            with self.subTest('LIMITING TEST TO %s' % LIMIT_TO):
                self.fail('ALERT, this test is limited.')

        for test in TESTS:
            test_name = '#%s - %s' % (test['id_num'], test['addr'])
            if LIMIT_TO == -1 or LIMIT_TO == int(test['id_num']):
                with self.subTest(test_name):
                    tmp_ret = emv(self.fix_addr(test['addr']))
                    tmp_ret_msg = full_ret_string(test['id_num'], test['addr'], tmp_ret)
                    tmp_diag_msg = 'DIAG Mismatch, EXPECTING: %s, received %s\n\n%s' % (test['diag'], tmp_ret.diags(), tmp_ret_msg)

                    self.assertEquals(tmp_ret.diags(), test['diag'], tmp_diag_msg)



