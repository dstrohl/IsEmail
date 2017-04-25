import unittest
from parse_objects import make_char_str, EmailParser
from tests.email_test_data import CORRECTED_TESTS
from meta_data import ISEMAIL_DNS_LOOKUP_LEVELS, META_LOOKUP, ISEMAIL_RESULT_CODES, MetaCat
from parse_results import ParseShortResult, ParseFullResult, ParsingError
import xml.etree.ElementTree as ET


XML_TEST_FILE = 'tests.xml'


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


def fix_addr(addr_in):

    addr_in = addr_in.replace('&amp;', '&')

    post_text = addr_in

    tmp_ret = []
    while post_text:
        start_pos = post_text.find('&#x')
        if start_pos == -1:
            break

        end_pos = post_text.find(';', start_pos)

        if end_pos == -1:
            break

        tmp_ret.append(post_text[0:start_pos])
        tmp_chr = post_text[start_pos+3:end_pos]
        tmp_chr = int(tmp_chr, base=16)

        if tmp_chr >= 9216:
            tmp_chr -= 9216
        tmp_ret.append(chr(tmp_chr))

        post_text = post_text[end_pos+1:]

    tmp_ret.append(post_text)
    return ''.join(tmp_ret)


META_LOOKUP.set_default_format(to_desc=True)


class ParseTestItem(object):

    def __init__(self, id_num, addr, diag, codes, comment, cat=None, local_comment=None, domain_comment=None, exp_exception=None, **kwargs):
        self.id = int(id_num)
        self.disp_addr = addr
        self.addr = fix_addr(addr)
        self.diag = diag
        self.codes = codes or [diag]

        self.comment = comment

        self.local_comment = local_comment or []
        self.domain_comment = domain_comment or []

        if diag in META_LOOKUP:
            self.diag_obj = META_LOOKUP[diag]
            if isinstance(self.diag_obj, MetaCat):
                raise AttributeError('Invalid Diag on record #%s: %s is a Category' % (self.id, diag))

        else:
            raise AttributeError('Invalid Diag on record #%s: %s' % (self.id, diag))

        self.cat = self.diag_obj.category.key

        self.status = self.diag_obj.status

        self.error = self.status == ISEMAIL_RESULT_CODES.ERROR
        self.warning = self.status == ISEMAIL_RESULT_CODES.WARNING
        self.ok = self.status == ISEMAIL_RESULT_CODES.OK

        self.bool_ret = not self.error

        if self.error and exp_exception is None:
            self.exp_exception = ParsingError
        else:
            self.exp_exception = exp_exception

        self.short_description = str(META_LOOKUP[diag])
        self.long_description = META_LOOKUP('formatted_string', diags=self.codes)

        self.current_pass = True
        self.current_msg = ''

    def reset(self, verbose):
        self.current_pass = True
        self.current_msg = '\n\nSaved EMAIL: %r\n' % self.disp_addr
        self.current_msg += 'Fixed EMAIL: %r\n' % self.addr
        self.current_msg += 'Verbosity == %s\n' % verbose
        if self.comment:
            self.current_msg += '(%s)\n' % self.comment
        self.current_msg += '====================================\n'
        self.short_msg = []

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
        while '{{' in addr_in and '}}' in addr_in:

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

        return tmp_ret

    def check_and_make_ret(self, section, expected, returned):
        if isinstance(expected, (list, tuple)):
            if isinstance(returned, (list, tuple)):
                tmp_pass, only_in_expected, only_in_returned = self.compare_lists(expected, returned)
                if not tmp_pass:
                    self.current_msg += self.make_exp_ret_string_list(section, only_in_expected, only_in_returned)
                    tmp_pass = False
            else:
                self.current_msg += self.make_exp_ret_string(section, expected=expected, returned=returned)
                tmp_pass = False
        elif isinstance(returned, (list, tuple)):
            self.current_msg += self.make_exp_ret_string(section, expected=expected, returned=returned)
            tmp_pass = False
        else:
            tmp_pass = expected == returned
            if not tmp_pass:
                self.current_msg += self.make_exp_ret_string(section, expected, returned)
                self.short_msg.append(section)

        if self.current_pass and not tmp_pass:
            self.current_pass = False

    def test_ret_obj(self, verbose, ret_obj):
        self.reset(verbose)
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

        if verbose == 1:
            self.check_and_make_ret('Error', self.error, ret_obj.error)
            self.check_and_make_ret('Warning', self.warning, ret_obj.warning)
            self.check_and_make_ret('OK', self.ok, ret_obj.ok)

            self.check_and_make_ret('Category', self.cat, ret_obj.diag(inc_cat=True, inc_diag=False))
            self.check_and_make_ret('Major Diag', self.diag, ret_obj.diag(inc_cat=False, inc_diag=True))
            self.check_and_make_ret('Description', self.short_description, ret_obj.description(show_all=False))

            # ****************** set msg postfix ****************************
            self.current_msg += '\n\n\n**********************************************\n'
            self.current_msg += '**********************************************\n'
            self.current_msg += 'Full Email:  ' + ret_obj.full_address + '\n'
            self.current_msg += 'Status:  ' + ret_obj.status.name + '\n'
            self.current_msg += 'Codes:   ' + ret_obj._major_diag + '\n'


        if verbose == 2:
            self.check_and_make_ret('Error', self.error, ret_obj.error)
            self.check_and_make_ret('Warning', self.warning, ret_obj.warning)
            self.check_and_make_ret('OK', self.ok, ret_obj.ok)

            self.check_and_make_ret('Category', self.cat, ret_obj.diag(inc_cat=True, inc_diag=False, show_all=False, return_as_list=True)[0])
            self.check_and_make_ret('Major Diag', self.diag, ret_obj.diag(inc_cat=False, inc_diag=True, return_as_list=True)[0])
            self.check_and_make_ret('Description', [self.short_description], ret_obj.description(show_all=False))

            self.check_and_make_ret('Codes', self.codes, ret_obj.diag(inc_cat=False, inc_diag=True, return_as_list=True, show_all=True))
            self.check_and_make_ret('Local Comments', self.local_comment, ret_obj.local_comments)
            self.check_and_make_ret('Domain Comments', self.domain_comment, ret_obj.domain_comments)
            self.check_and_make_ret('Long Desc', self.long_description, ret_obj.report())

            # ****************** set msg postfix ****************************
            self.current_msg += '\n\n\n**********************************************\n'
            self.current_msg += '**********************************************\n'
            self.current_msg += 'Full Email:  ' + ret_obj.full_address + '\n'
            self.current_msg += 'Status:  ' + ret_obj.status.name + '\n'
            self.current_msg += 'Codes:   ' + repr(list(ret_obj._diag_recs.keys())) + '\n'
            self.current_msg += 'History: ' + ret_obj.history() + '\n'
            self.current_msg += 'Trace:\n' + ret_obj.trace



        tmp_short_msg = '(%s}' % ' | '.join(self.short_msg)

        return self.current_pass, tmp_short_msg, self.current_msg


class EmailTestSet(object):

    def __init__(self, corrected_dict=None):
        self.tests = []

        self.corrected_dict = corrected_dict or {}

        xml_data = ET.parse(XML_TEST_FILE).getroot()

        self.xml_version = 'unknown'
        # for item in xml_data.findall('tests'):
        self.xml_version = xml_data.get('version')

        self.version_match = self.xml_version == corrected_dict['version']

        for item in xml_data.findall('test'):
            id_num = item.get('id')

            addr = item.find('address').text

            if addr is None:
                addr = ''
            else:
                addr = fix_addr(addr)

            category = item.find('category').text
            diag = item.find('diagnosis').text
            comment = item.find('comment')
            if comment is None:
                comment = ''
            else:
                comment = comment.text

            tmp_dict = dict(
                id_num=id_num,
                addr=addr,
                cat=category,
                diag=diag,
                codes=None,
                comment=comment)

            if int(id_num) in corrected_dict:
                tmp_dict.update(corrected_dict[int(id_num)])

            tmp_obj = ParseTestItem(**tmp_dict)
            self.tests.append(tmp_obj)


EMTS = EmailTestSet(CORRECTED_TESTS)


class TestFixAddr(unittest.TestCase):

    def test_fix_addr(self):
        TESTS = [
            (0, "!#$%&amp;`*+/=?^`{|}~@iana.org", "!#$%&`*+/=?^`{|}~@iana.org"),
            (1, "test&#x2400;@iana.org", "test" + chr(0)+"@iana.org"),
            (2, "test\&#x2400;@iana.org", "test\\"+chr(0)+"@iana.org"),
            (3, "&#x240D;&#x240A; test@iana.org", chr(13)+chr(10)+" test@iana.org"),
            (4, "&#x240D;&#x240A; &#x240D;&#x240A; test@iana.org", chr(13)+chr(10)+" "+chr(13)+chr(10)+" test@iana.org"),
            (5, "test@iana.org&#x240A;", "test@iana.org"+chr(10)),
            (6, "test@[RFC-5322-\&#x2407;-domain-literal]", "test@[RFC-5322-\\" + chr(7) + "-domain-literal]"),
            (7, "test@[RFC-5322-\&#x2409;-domain-literal]", "test@[RFC-5322-\\" + chr(9) + "-domain-literal]"),
            (8, "test@iana.org&#x240D;", "test@iana.org"+chr(13)),
            (9, "&#x240D;test@iana.org", chr(13)+"test@iana.org"),
            (10, "&#x240D;test@iana.org", chr(13)+"test@iana.org"),
            (11, "(&#x240D;)test@iana.org", "("+chr(13)+")test@iana.org"),
            (12, "test@iana.org(&#x240D;)", "test@iana.org("+chr(13)+")"),
            (13, "&#x240A;test@iana.org", chr(10)+"test@iana.org"),
            (14, "&#x240A;@iana.org", chr(10)+"@iana.org"),
            (15, "\&#x240A;@iana.org", "\\"+chr(10)+"@iana.org"),
            (16, "(&#x240A;)test@iana.org", "("+chr(10)+")test@iana.org"),
            (17, "&#x2407;@iana.org", chr(7)+"@iana.org"),
            (18, "test@&#x2407;.org", "test@"+chr(7)+".org"),
            (19, "&#x2407;@iana.org", chr(7)+"@iana.org"),
            (20, "\&#x2407;@iana.org", "\\"+chr(7)+"@iana.org"),
            (21, "(&#x2407;)test@iana.org", "("+chr(7)+")test@iana.org"),
            (22, "&#x240D;&#x240A;test@iana.org", chr(13)+chr(10)+"test@iana.org"),
            (23, "&#x240D;&#x240A; &#x240D;&#x240A;test@iana.org", chr(13)+chr(10)+" "+chr(13)+chr(10)+"test@iana.org"),
            (24, "&#x240D;&#x240A;test@iana.org", chr(13)+chr(10)+"test@iana.org"),
            (25, "&#x240D;&#x240A; test@iana.org", chr(13)+chr(10)+" test@iana.org"),
            (26, "&#x240D;&#x240A; &#x240D;&#x240A;test@iana.org", chr(13)+chr(10)+" "+chr(13)+chr(10)+"test@iana.org"),
            (27, "&#x240D;&#x240A;&#x240D;&#x240A;test@iana.org", chr(13)+chr(10)+chr(13)+chr(10)+"test@iana.org"),
            (28, "&#x240D;&#x240A;&#x240D;&#x240A; test@iana.org", chr(13)+chr(10)+chr(13)+chr(10)+" test@iana.org"),
            (29, "test@iana.org&#x240D;&#x240A;", "test@iana.org"+chr(13)+chr(10)+""),
            (30, "test@iana.org&#x240D;&#x240A; &#x240D;&#x240A;", "test@iana.org"+chr(13)+chr(10)+" "+chr(13)+chr(10)+""),
            (31, "test@iana.org&#x240D;&#x240A;", "test@iana.org"+chr(13)+chr(10)+""),
            (32, "test@iana.org&#x240D;&#x240A; &#x240D;&#x240A;", "test@iana.org"+chr(13)+chr(10)+" "+chr(13)+chr(10)+""),
            (33, "test@iana.org &#x240D;&#x240A;", "test@iana.org "+chr(13)+chr(10)+""),
            (34, "test@iana.org &#x240D;&#x240A;", "test@iana.org "+chr(13)+chr(10)+""),
            (35, "test@iana.org &#x240D;&#x240A; &#x240D;&#x240A;", "test@iana.org "+chr(13)+chr(10)+" "+chr(13)+chr(10)+""),
            (36, "test@iana.org &#x240D;&#x240A;&#x240D;&#x240A;", "test@iana.org "+chr(13)+chr(10)+chr(13)+chr(10)+""),
            (37, "test@iana.org &#x240D;&#x240A;&#x240D;&#x240A;", "test@iana.org "+chr(13)+chr(10)+chr(13)+chr(10)+""),
            (38, "test\&#xA9;@iana.org", "test\\"+chr(int('A9', base=16))+"@iana.org")]

        for test in TESTS:
            with self.subTest('#%s' % test[0]):
                tmp_ret = fix_addr(test[1])
                self.assertEqual(test[2], tmp_ret)



class TestEmailParser(unittest.TestCase):
    maxDiff = None
    longMessage = True
    """
    tmp_dict = dict(
        id_num=id_num,
        addr=addr,
        cat=category,
        diag=diag,
        codes=[],
        comment=comment)
    """

    def test_version(self):
        self.assertEqual(EMTS.corrected_dict['version'], EMTS.xml_version)

    def test_full_parse(self):
        emv_0 = EmailParser(
            verbose=0,
            dns_lookup_level=ISEMAIL_DNS_LOOKUP_LEVELS.MX_RECORD,
            raise_on_error=False,
            trace_filter=999)

        emv_1 = EmailParser(
            verbose=1,
            dns_lookup_level=ISEMAIL_DNS_LOOKUP_LEVELS.MX_RECORD,
            raise_on_error=False,
            trace_filter=999)

        emv_2 = EmailParser(
            verbose=2,
            dns_lookup_level=ISEMAIL_DNS_LOOKUP_LEVELS.MX_RECORD,
            raise_on_error=False,
            trace_filter=999)

        emv_raise = EmailParser(
            verbose=0,
            dns_lookup_level=ISEMAIL_DNS_LOOKUP_LEVELS.MX_RECORD,
            raise_on_error=True,
            trace_filter=999)

        test_types = (
            (0, 0, False, emv_0),
            (1, 1, False, emv_1),
            (2, 2, False, emv_2),
            (3, 0, True, emv_raise))

        LIMIT_TO = -1

        LIMIT_TYPE = 2   # 0, 1, 2, 3=raise


        if LIMIT_TO != -1:
            with self.subTest('LIMITING TEST TO %s' % LIMIT_TO):
                self.fail('ALERT, this test is limited.')

        if LIMIT_TYPE != -1:
            with self.subTest('LIMITING TEST TO %s' % LIMIT_TYPE):
                self.fail('ALERT, this test is limited.')

        for pti in EMTS.tests:
            if LIMIT_TO == -1 or LIMIT_TO == pti.id:
                META_LOOKUP.clear_overrides()
                # pti = ParseTestItem(**test)
                for tt in test_types:
                    if LIMIT_TYPE == -1 or LIMIT_TYPE == tt[0]:
                        with self.subTest(pti.name(tt[0])):
                            if tt[2]:
                                if pti.error:
                                    with self.subTest(pti.name(tt[3]) + ' NOT RAISED'):
                                        with self.assertRaises(pti.exp_exception):
                                            tmp_ret = tt[3](pti.addr)
                                else:
                                    with self.subTest(pti.name(tt[3]) + ' WAS RAISED'):
                                        tmp_ret = tt[3](pti.addr)
                            else:
                                with self.subTest(pti.name(tt[0], ' - return')):
                                    tmp_ret = tt[3](pti.addr)
                                    tmp_check, tmp_short_msg, tmp_msg = pti.test_ret_obj(tt[1], tmp_ret)
                                    with self.subTest(pti.name(tt[0], tmp_short_msg)):
                                        self.assertTrue(tmp_check, msg=tmp_msg)



