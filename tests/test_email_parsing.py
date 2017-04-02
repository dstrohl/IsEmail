import unittest
from parse_objects import make_char_str, EmailParser
from tests.email_test_data import TESTS
from meta_data import ISEMAIL_DNS_LOOKUP_LEVELS, META_LOOKUP, ISEMAIL_RESULT_CODES
from parse_results import ParseShortResult, ParseFullResult, ParsingError

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


class ParseTestItem(object):

    def __init__(self, id_num, addr, cat, diag, codes, comment, local_comment=None, domain_comment=None, exp_exception=None):
        self.id = int(id_num)
        self.disp_addr = addr
        self.addr = self.fix_addr(addr)
        self.cat = cat
        self.diag = diag
        self.codes = codes
        self.comment = comment

        self.local_comment = local_comment or []
        self.domain_comment = domain_comment or []
        if diag in META_LOOKUP:
            self.diag_obj = META_LOOKUP[diag]
        else:
            raise AttributeError('Invalid Diag:  [#%s] %s' % (self.id, diag))
        self.status = self.diag_obj.status

        self.error = self.status == ISEMAIL_RESULT_CODES.ERROR
        self.warning = self.status == ISEMAIL_RESULT_CODES.WARNING
        self.ok = self.status == ISEMAIL_RESULT_CODES.OK

        self.bool_ret = not self.error

        if self.error and exp_exception is None:
            self.exp_exception = ParsingError
        else:
            self.exp_exception = exp_exception

        self.long_description = []
        for c in codes:
            self.long_description.append(META_LOOKUP[c].description)
        self.short_description = self.diag_obj.description

        self.current_pass = True
        self.current_msg = ''

    def reset(self):
        self.current_pass = True
        self.current_msg = '\n\n%s\n====================================\n' % self.disp_addr

    def name(self, test_type, sub_name=None):
        if sub_name is None:
            tmp_name = '[%s-%s] - %s' % (self.id, test_type, self.disp_addr)
        else:
            tmp_name = '[%s-%s-%s] - %s' % (self.id, test_type, sub_name, self.disp_addr)
        return tmp_name

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

    def compare_lists(self, list1, list2):
        """
        returns (T/F, <only in list 1>, <only in list 2>)
        """
        matching_items = []

        list1 = list1.copy()
        list2 = list2.copy()

        for item in list1:
            if item in list2:
                matching_items.append(item)

        for m in matching_items:
            for c in range(list1.count(m)):
                list1.remove(m)
            for c in range(list2.count(m)):
                list2.remove(m)
        if list1 or list2:
            tmp_match = False
        else:
            tmp_match = True
        return tmp_match, list1, list2

    def make_exp_ret_string(self, section, expected, returned):
        return '\n*****************************\n%s\n    Expected: %r\n    Returned: %r\n' % (section, expected, returned)

    def make_exp_ret_string_list(self, section, only_in_expected, only_in_returned):
        tmp_ret = '\n*****************************\n'
        tmp_ret += section + '\n'
        if only_in_expected:
            tmp_ret += '    Missing:\n        %r\n' % only_in_expected
        if only_in_returned:
            tmp_ret += '    Extra:\n        %r\n' % only_in_returned

    def check_and_make_ret(self, section, expected, returned):
        if isinstance(expected, (list, tuple)):
            tmp_pass, only_in_expected, only_in_returned = self.compare_lists(expected, returned)
            if not tmp_pass:
                self.current_msg += self.make_exp_ret_string_list(section, only_in_expected, only_in_returned)
        else:
            tmp_pass = expected == returned
            if not tmp_pass:
                self.current_msg += self.make_exp_ret_string(section, expected, returned)

        if self.current_pass and not tmp_pass:
            self.current_pass = False

    def test_ret_obj(self, verbose, ret_obj):
        self.reset()

        if verbose == 0:
            if not isinstance(ret_obj, bool):
                return False, self.make_exp_ret_string('Return object type', 'BOOL', repr(ret_obj))

        elif verbose == 1:
            if not isinstance(ret_obj, ParseShortResult):
                return False, self.make_exp_ret_string('Return object type', 'Parser Short Result', repr(ret_obj))

        elif verbose == 2:
            if ret_obj:
                if not isinstance(ret_obj, ParseFullResult):
                    return False, self.make_exp_ret_string('Return object type', 'Parser FULL Result', repr(ret_obj))
            else:
                if not isinstance(ret_obj, ParseShortResult):
                    return False, self.make_exp_ret_string('Return object type', 'Parser Short Result', repr(ret_obj))

        self.check_and_make_ret('True/False', self.bool_ret, bool(ret_obj))

        if verbose > 0:
            self.check_and_make_ret('Category', self.cat, ret_obj.diag(category=True, show_all=False))
            self.check_and_make_ret('Major Diag', self.diag, ret_obj.diag(category=False, show_all=False))
            self.check_and_make_ret('Description', self.short_description, ret_obj.description(show_all=False))
            self.check_and_make_ret('Error', self.error, ret_obj.error)
            self.check_and_make_ret('Warning', self.warning, ret_obj.warning)
            self.check_and_make_ret('OK', self.ok, ret_obj.ok)

        elif verbose > 1:
            self.check_and_make_ret('Codes', self.codes, ret_obj.diag(show_all=True))
            self.check_and_make_ret('Local Comments', self.local_comment, ret_obj.local_comments)
            self.check_and_make_ret('Domain Comments', self.domain_comment, ret_obj.domain_comments)
            self.check_and_make_ret('Long Desc', self.domain_comment, ret_obj.description(show_all=True))

        if not self.current_pass and verbose == 2:
            self.current_msg += '\n\n\n'
            self.current_msg += 'History: ' + ret_obj.history + '\n\n'
            self.current_msg += 'Trace:\n' + ret_obj.trace_str

        return self.current_pass, self.current_msg


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

    def test_full_parse(self):
        emv_0 = EmailParser(
            verbose=0,
            dns_lookup_level=ISEMAIL_DNS_LOOKUP_LEVELS.MX_RECORD,
            raise_on_error=False)

        emv_1 = EmailParser(
            verbose=1,
            dns_lookup_level=ISEMAIL_DNS_LOOKUP_LEVELS.MX_RECORD,
            raise_on_error=False)

        emv_2 = EmailParser(
            verbose=2,
            trace_filter=999,
            dns_lookup_level=ISEMAIL_DNS_LOOKUP_LEVELS.MX_RECORD,
            raise_on_error=False)

        emv_raise = EmailParser(
            verbose=0,
            trace_filter=999,
            dns_lookup_level=ISEMAIL_DNS_LOOKUP_LEVELS.MX_RECORD,
            raise_on_error=True)

        test_types = (
            (0, 0, False, emv_0),
            (1, 1, False, emv_1),
            (2, 2, False, emv_2),
            (3, 0, True, emv_raise))

        LIMIT_TO = -1

        LIMIT_TYPE = -1   # 0, 1, 2, 3=raise

        if LIMIT_TO != -1:
            with self.subTest('LIMITING TEST TO %s' % LIMIT_TO):
                self.fail('ALERT, this test is limited.')

        if LIMIT_TYPE != -1:
            with self.subTest('LIMITING TEST TO %s' % LIMIT_TYPE):
                self.fail('ALERT, this test is limited.')

        for test in TESTS:
            pti = ParseTestItem(**test)
            if LIMIT_TO == -1 or LIMIT_TO == pti.id:
                for tt in test_types:
                    if LIMIT_TYPE == -1 or LIMIT_TYPE == tt[0]:
                        with self.subTest(pti.name(tt[0])):
                            if tt[2]:
                                if pti.error:
                                    with self.assertRaises(pti.exp_exception):
                                        tmp_ret = tt[3](pti.addr)
                                else:
                                    tmp_ret = tt[3](pti.addr)
                            else:
                                with self.subTest(pti.name(tt[0], ' - return')):
                                    tmp_ret = tt[3](pti.addr)
                                    tmp_check, tmp_msg = pti.test_ret_obj(tt[1], tmp_ret)
                                    self.assertTrue(tmp_check, msg=tmp_msg)



