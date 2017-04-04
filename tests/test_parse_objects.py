import unittest
from parse_objects import EmailParser, make_char_str
from meta_data import META_LOOKUP, ISEMAIL_ALLOWED_GENERAL_ADDRESS_LITERAL_STANDARD_TAGS, ISEMAIL_DOMAIN_TYPE, ISEMAIL_DNS_LOOKUP_LEVELS
from dns_functions import DNSTimeoutError

ISEMAIL_ALLOWED_GENERAL_ADDRESS_LITERAL_STANDARD_TAGS.append('http')

tmp_list = list(META_LOOKUP.diags._by_key.keys())
DIAGS = tmp_list.copy()


NOT_IN_DIAGS = ['RFC5321_IPV6_DEPRECATED', 'RFC5322_IPV6_2X2X_COLON', 'RFC5322_IPV6_BAD_CHAR',
                'RFC5322_IPV6_COLON_END', 'RFC5322_IPV6_COLON_STRT', 'RFC5322_IPV6_GRP_COUNT', 'RFC5322_IPV6_MAX_GRPS',
                'DNSWARN_INVALID_TLD', 'DNSWARN_NO_MX_RECORD', 'DNSWARN_NO_RECORD', 'ERR_UNKNOWN', 'DNSWARN_COMM_ERROR']
for diag in NOT_IN_DIAGS:
    DIAGS.remove(diag)

print('\n\nDiags Count = %s\n\n' % len(DIAGS))


def full_ret_string(test_num, test_string, test_ret, extra_string=''):
    tmp_ret = '\n\n'

    tmp_ret += 'Run Number: %s\n' % test_num
    tmp_ret += 'Checked String: %r\n\n' % test_string

    tmp_ret += 'Error Flag: %r\n' % test_ret.error
    tmp_ret += 'Local_part: %r\n' % test_ret.local
    tmp_ret += 'Domain_part: %r\n' % test_ret.domain

    tmp_ret += 'Local_comments: %r\n' % test_ret.local_comments
    tmp_ret += 'Domain_comments: %r\n' % test_ret.domain_comments

    ret_codes = list(test_ret.diag(show_all=True))
    ret_codes.sort()

    tmp_ret += 'Codes: %r\n' % ret_codes

    tmp_hist = test_ret.history.short_desc()

    tmp_ret += 'History: %s\n' % tmp_hist

    tmp_ret += 'Extra Info: %r\n\n' % extra_string

    tmp_ret += 'Trace:\n%s\n\n' % test_ret.trace

    return tmp_ret

class TestMakeParseString(unittest.TestCase):

    def test_make_string(self):
        tmp_res = make_char_str('foobar')
        self.assertEqual('foobar', tmp_res)

    def test_from_int(self):
        tmp_res = make_char_str(65, 66, 67)
        self.assertEqual('ABC', tmp_res)

    def test_from_string(self):
        tmp_res = make_char_str('ABC', '123')
        self.assertEqual('ABC123', tmp_res)

    def test_from_int_range(self):
        tmp_res = make_char_str((65, 67), (97, 99))
        self.assertEqual('ABCabc', tmp_res)


class MyTestDefs(object):
    def __init__(self, method_name, ret_football=True, tests=None, limit_to=-1, history_level=999, **kwargs):
        self.method_name = method_name
        self.ret_football = ret_football
        self.kwargs = kwargs
        self.limit_to = limit_to
        self.history_level = history_level
        if tests is None:            
            self.tests = []
        else:
            self.tests = tests
        
        for t in self.tests:
            t.method_name = method_name
            t.defs = self
            
    def __iter__(self):
        for t in self.tests:
            yield t


class MyTestData(object):
    def __init__(self, 
                 test_num, 
                 string_in, 
                 result_length, 
                 position=0, 
                 codes=None,
                 error=False,
                 history_str=None,
                 **kwargs):
        self.method_name = ''        
        self.test_num = test_num
        self.string_in = string_in
        self.result_length = result_length
        self.position = position
        self.kwargs = kwargs
        self.error = error

        if history_str is None:
            if self.result_length == 0:
                self.history_str = ''
            else:
                self.history_str = '--MISSING--'
        else:
            self.history_str = history_str
        self.defs = None
        
        if codes is None:
            self.no_codes = True
        else:
            self.no_codes = False

        if codes is not None:
            if isinstance(codes, str):
                self.codes = [codes]
            else:
                self.codes = codes
        else:
            self.codes = []

    @property
    def test_name(self):
        return '#%s %s in %s (%s) should == %s' % (
            self.test_num,
            self.method_name,
            self.string_in,
            self.position,
            self.result_length
        )    

    def _full_ret_string(self, test_ret):
        tmp_ret = '\n\n'

        tmp_ret += 'Run Number: %s\n' % self.test_num
        tmp_ret += 'Test Name: %s\n' % self.test_name
        tmp_ret += 'Checked String: %r\n\n' % self.string_in

        tmp_ret += 'Length: %s\n' % test_ret.length

        tmp_ret += 'Error Flag: %r\n' % test_ret.error

        ret_codes = list(test_ret.diags())
        ret_codes.sort()

        tmp_ret += 'Codes: %r\n' % ret_codes

        tmp_hist = test_ret.history.short_desc()

        tmp_ret += 'History: %s\n' % tmp_hist
        tmp_ret += 'Trace:\n%s\n\n' % test_ret.trace_str

        return tmp_ret

    def run_test(self, tep=None):
        tmp_ret = dict(
            skip=False,
            fail=False,
            long_fail_msg='Passed all tests',
            short_fail_msg='PASSED Tests')

        if tep is None or self.defs.kwargs:
            tep = EmailParser(**self.defs.kwargs, verbose=3)

        # tmp_meth = getattr(tep, self.method_name)

        # test_ret = tep.run_method_test(tmp_meth, position=self.position, **self.kwargs)
        test_ret = tep(email_in=self.string_in, method=self.method_name, position=self.position, return_football=True, **self.kwargs)

        if not self.defs.ret_football:
            if test_ret.length == self.result_length:
                tmp_ret['short_fail_msg'] = '%s : INCORRECT LENGTH (%s != %s)' % (self.test_name, test_ret.length, self.result_length)
                tmp_ret['long_fail_msg'] = '\n\nFailed Length:\n  EXPECTED: %s\n  RETURNED: %s\n' % (self.result_length, test_ret.length)
                tmp_ret['fail'] = True
            return tmp_ret

        test_failed = False
        tmp_ret_long_list = []
        tmp_ret_short_list = []

        if test_ret.length != self.result_length:
            test_failed = True
            tmp_ret_short_list.append('LENGTH')
            tmp_ret_long_list.append('    Failed Length:')
            tmp_ret_long_list.append('        EXPECTED Length: %s' % self.result_length)
            tmp_ret_long_list.append('        RETURNED Length: %s' % test_ret.length)

        if test_ret.error != self.error:
            test_failed = True
            tmp_ret_short_list.append('ERR-FLAG')
            tmp_ret_long_list.append('    Failed Error Flag:')
            tmp_ret_long_list.append('        EXPECTED Flag: ,error=%r' % self.error)
            tmp_ret_long_list.append('        RETURNED Flag: ,error=%r' % test_ret.error)

        if self.no_codes:
            exp_codes = []
        else:
            exp_codes = list(self.codes)
            exp_codes.sort()


        ret_codes = list(test_ret.diags())
        ret_codes.sort()

        for code in ret_codes:
            try:
                DIAGS.remove(code)
            except ValueError:
                pass

        if ret_codes != exp_codes:
            test_failed = True
            tmp_ret_short_list.append('CODES')
            tmp_ret_long_list.append('    Mismatched Codes:')
            tmp_ret_long_list.append('        EXPECTED , codes=%r  ' % exp_codes)
            tmp_ret_long_list.append('        RETURNED , codes=%r  ' % ret_codes)

        if test_ret.history is None:
            tmp_hist = ''
        else:
            tmp_hist = test_ret.history.short_desc(self.defs.history_level)

        if tmp_hist != self.history_str:
            test_failed = True
            tmp_ret_short_list.append('HIST')
            tmp_ret_long_list.append('    Mismatched History:')
            tmp_ret_long_list.append('        EXPECTED , history_str=%r  ' % self.history_str)
            tmp_ret_long_list.append('        RETURNED , history_str=%r  ' % tmp_hist)

        tmp_ret_long_list.append('\n\nHistory Details:')
        tmp_ret_long_list.append(test_ret.history.long_desc())
        tmp_ret_long_list.append('\n\n')


        if test_failed:
            tmp_short = '%s:   Failures: [%s]' % (self.test_name, ', '.join(tmp_ret_short_list))
            tmp_long = 'Run Number: %s\nTest Name: %s\nChecked String: %s\n\nFailures:\n%s\n\nTrace:%s' % (
                self.test_num,
                self.test_name,
                self.string_in,
                '\n'.join(tmp_ret_long_list),
                tep.trace_str)
            tmp_ret['fail'] = True
            tmp_ret['short_fail_msg'] = tmp_short
            tmp_ret['long_fail_msg'] = tmp_long
        else:
            print(self._full_ret_string(test_ret))

        return tmp_ret


class TestEmailParser(unittest.TestCase):
    TRACE_LEVEL = 9999    
    TEP = EmailParser(verbose=3, trace_filter=TRACE_LEVEL)

    def run_test_data(self, test_defs):
        if test_defs.limit_to != -1:
            with self.subTest('LIMITING TEST %s to %s' % (test_defs.method_name, test_defs.limit_to)):
                self.fail('ALERT, this test is limited.')

        for test in test_defs:
            if test_defs.limit_to == -1 or test.test_num == test_defs.limit_to:
                with self.subTest(test.test_name):
                    tmp_result = test.run_test(self.TEP)

                    if tmp_result['fail']:
                        with self.subTest(tmp_result['short_fail_msg']):
                            self.fail(tmp_result['long_fail_msg'])

    def old_run_test_data(self, test_defs: MyTestDefs):
        if test_defs.limit_to != -1:
            with self.subTest('LIMITING TEST %s to %s' % (test_defs.method_name, test_defs.limit_to)):
                self.fail('ALERT, this test is limited.')
        
        for test in test_defs:

            if test_defs.limit_to == -1 or test_defs.limit_to == test.test_num:
                with self.subTest(test.test_name + ' run_parse'):
                    eph = EmailParser(test.string_in, **test_defs.kwargs, verbose=3)
                    tmp_meth = getattr(eph, test.method_name)
                    test_ret = eph.run_method_test(tmp_meth, position=test.position, **test.kwargs)

                if test_defs.football:
                    with self.subTest(test.test_name + ' incorrect length'):
                        self.assertEquals(test_ret.length, test.result_length, msg=eph.trace_str)
                else:
                    with self.subTest(test.test_name + ' incorrect length'):
                        self.assertEqual(test_ret, test.result_length, msg=eph.trace_str)

                if test_defs.football:

                    if test.error:
                        sub_name = test.test_name + ' Does not have Error Flag'
                    else:
                        sub_name = test.test_name + ' Does have Error Flag'

                    with self.subTest(sub_name):
                        self.assertEquals(test.error, test_ret.error, msg=eph.trace_str)
                    """
                    if test.has_code:
                        for code in test.has_code:
                            with self.subTest(test.test_name + ' has_code: %s' % code):
                                if code not in test_ret:
                                    self.fail('Missing code: %s\n\n%s' % (code, eph.trace_str))

                    if test.not_has_code:
                        for code in test.not_has_code:
                            with self.subTest(test.test_name + ' not_has_code: %s' % code):
                                if code in test_ret:
                                    self.fail('Should not have code: %s\n\n%s' % (code, eph.trace_str))

                    """
                    if test.codes:
                        with self.subTest(test.test_name + ' missing codes'):
                            self.assertCountEqual(test.codes, list(test_ret.diags()), msg=eph.trace_str)

                            for code in test_ret.diags():
                                try:
                                    self.DIAGS.remove(code)
                                except ValueError:
                                    pass

                    if test.no_codes:
                        with self.subTest(test.test_name + ' has codes (and should not)'):
                            self.assertEquals([], list(test_ret.diags()), msg=eph.trace_str)

    def test_remaining(self):
        test_ret = '12345'
        emp = EmailParser('12345')
        index = 0
        for x in emp.remaining(0):
            self.assertEqual(test_ret[index], x)
            index += 1

    def test_simple_str(self):
        emp = EmailParser('123abc')
        tmp_ret = emp.simple_char(0, '1234567890')
        self.assertEqual(tmp_ret.l, 3)

        tmp_ret = emp.simple_char(0, '21', max_count=2)
        self.assertEqual(tmp_ret.l, 2)

        tmp_ret = emp.simple_char(0, '123456', min_count=4)
        self.assertEqual(tmp_ret.l, 0)

        tmp_ret = emp.simple_char(3, 'abcdefg')
        self.assertEqual(tmp_ret.l, 3)

        tmp_ret = emp.simple_char(3, 'abgth', max_count=2)
        self.assertEqual(tmp_ret.l, 2)

        tmp_ret = emp.simple_char(3, 'abcdef', min_count=4)
        self.assertEqual(tmp_ret.l, 0)

    def test_zzzz_for_diags(self):
        tmp_len = len(DIAGS)
        DIAGS.sort()
        tmp_str = '\n\n'
        tmp_str += '\n'.join(DIAGS)
        tmp_str += '\n'
        self.assertEquals(tmp_len, 0, msg=tmp_str)

    def make_ls(self, *length, chars='X', prefix='', postfix=''):
        tmp_ret = []
        for l in length:
            tmp_ret.append(''.ljust(l, chars[0]))
        return '%s%s%s' % (prefix, '.'.join(tmp_ret), postfix)

    # ********************************************************
    #  PARSING TESTS
    # ********************************************************

    def test_address_spec(self):
        address_too_long = self.make_ls(50) + '@' + self.make_ls(50, 50, 50, 50, 50)
        domain_too_long = self.make_ls(50, 50, 50, 50, 50, 50, prefix='dan@')
        local_too_long = self.make_ls(50, 50, postfix='@test.com')
        label_too_long = self.make_ls(100,50, prefix='dan@')

        td = MyTestDefs(
            limit_to=-1,
            history_level=3,
            # trace_filter=4,
            method_name='address_spec',
            tests=[
                # valod addresses
                MyTestData(100, 'dan@example.com', 15, codes=['VALID'], history_str='address_spec(local_part(dot_atom(...)), at, domain(domain_addr(...)))'),
                MyTestData(101, '"dan"@example.com', 17,
                           codes=['RFC5321_QUOTED_STRING'],
                           history_str='address_spec(local_part(quoted_string(...)), at, domain(domain_addr(...)))'
                           ),

                # empty address

                MyTestData(201, '', 0, error=True,
                           codes=['ERR_EMPTY_ADDRESS'],
                           history_str=''
                           ),

                # address too long
                MyTestData(202, address_too_long, 305, error=False,
                           codes=['RFC5322_TOO_LONG'],
                           history_str='address_spec(local_part(dot_atom(...)), at, domain(domain_addr(...)))'
                           ),

                # local part too long
                MyTestData(203, local_too_long, 110, error=False,
                           codes=['RFC5322_LOCAL_TOO_LONG'],
                           history_str='address_spec(local_part(dot_atom(...)), at, domain(domain_addr(...)))'
                           ),


                # domain part too long
                MyTestData(204, domain_too_long, 309, error=False,
                           codes=['RFC5322_DOMAIN_TOO_LONG', 'RFC5322_TOO_LONG'],
                           history_str='address_spec(local_part(dot_atom(...)), at, domain(domain_addr(...)))'
                           ),

                # segment too long
                MyTestData(205, label_too_long, 155, error=False,
                           codes=['RFC5322_LABEL_TOO_LONG'],
                           history_str='address_spec(local_part(dot_atom(...)), at, domain(domain_addr(...)))'
                           ),

                # cfws near at (good pre-dot-atom)
                MyTestData(301, '(bef@ore)foobar(after)@example.com', 34, error=False,
                           codes=['CFWS_COMMENT', 'DEPREC_COMMENT', 'DEPREC_LOCAL_PART'],
                           history_str='address_spec(local_part(obs_local_part(...)), at, domain(domain_addr(...)))'
                           ),
                # cfws near at (good pre-QS)
                MyTestData(302, '(bef@ore)"foobar"(after)@example.com', 36, error=False,
                           codes=['CFWS_COMMENT', 'RFC5321_QUOTED_STRING'],
                           history_str='address_spec(local_part(quoted_string(...)), at, domain(domain_addr(...)))'
                           ),

                # cfws near at (good pre-obs_local_part)
                MyTestData(303, '(before)foobar(af@ter).hello@example.com', 40, error=False,
                           codes=['CFWS_COMMENT', 'DEPREC_COMMENT', 'DEPREC_LOCAL_PART'],
                           history_str='address_spec(local_part(obs_local_part(...)), at, domain(domain_addr(...)))'
                           ),

                # cfws near at (good post-dot-atom)
                MyTestData(304, 'foobar@(before)example.com(aft@er)', 34, error=False,
                           codes=['CFWS_COMMENT', 'RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='address_spec(local_part(dot_atom(...)), at, domain(dot_atom(...)))'
                           ),

                # cfws near at (good post dom_lit)
                MyTestData(305, 'foobar@(before)[example.com](aft@er)', 36, error=False,
                           codes=['CFWS_COMMENT', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='address_spec(local_part(dot_atom(...)), at, domain(domain_literal(...)))'
                           ),

                # cfws near at (good post obs_domain)
                MyTestData(306, 'foobar@another.(bef@ore)example.com(after)', 42, error=False,
                           codes=['CFWS_COMMENT', 'RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='address_spec(local_part(dot_atom(...)), at, domain(obs_domain(...)))'
                           ),

                # cfws near at (bad pre-dot-atom)
                MyTestData(351, '(before)foobar.test(afte@r)@example.com', 39, error=False,
                           codes=['CFWS_COMMENT', 'DEPREC_CFWS_NEAR_AT', 'DEPREC_COMMENT', 'DEPREC_LOCAL_PART'],
                           history_str='address_spec(local_part(obs_local_part(...)), at, domain(domain_addr(...)))'
                           ),
                # cfws near at (bad pre-QS)
                MyTestData(352, '(before)"foobar"(aft@er)@example.com', 36, error=False,
                           codes=['CFWS_COMMENT', 'DEPREC_CFWS_NEAR_AT', 'RFC5321_QUOTED_STRING'],
                           history_str='address_spec(local_part(quoted_string(...)), at, domain(domain_addr(...)))'
                           ),

                # cfws near at (bad pre-obs_local_part)
                MyTestData(353, '(before)foobar(after).(before)foobar(aft@er)@example.com', 56, error=False,
                           codes=['CFWS_COMMENT', 'DEPREC_CFWS_NEAR_AT', 'DEPREC_COMMENT', 'DEPREC_LOCAL_PART'],
                           history_str='address_spec(local_part(obs_local_part(...)), at, domain(domain_addr(...)))'
                           ),

                # cfws near at (bad post-dot-atom)
                MyTestData(354, 'foobar@(be@fore)example.com(after)', 34, error=False,
                           codes=['CFWS_COMMENT', 'DEPREC_CFWS_NEAR_AT', 'RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='address_spec(local_part(dot_atom(...)), at, domain(dot_atom(...)))'
                           ),

                # cfws near at (bad post dom_lit)
                MyTestData(355, 'foobar@(befo@re)[example.com](after)', 36, error=False,
                           codes=['CFWS_COMMENT', 'DEPREC_CFWS_NEAR_AT', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL',
                                  'RFC5322_LIMITED_DOMAIN'],
                           history_str='address_spec(local_part(dot_atom(...)), at, domain(domain_literal(...)))'
                           ),

                # cfws near at (bad post obs_domain)
                MyTestData(356, 'foobar@(bef@ore)example(after).(before)com(after)', 49, error=False,
                           codes=['CFWS_COMMENT', 'DEPREC_CFWS_NEAR_AT', 'RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='address_spec(local_part(dot_atom(...)), at, domain(obs_domain(...)))'
                           ),

                # no domain
                MyTestData(401, 'dan@', 0, error=True,
                           codes=['ERR_NO_DOMAIN_PART'],
                           history_str=''
                           ),

                # no domain sep
                MyTestData(501, 'dan.strohl', 0, error=True,
                           codes=['ERR_NO_DOMAIN_SEP'],
                           history_str=''
                           ),

                # no local part
                MyTestData(601, '@dan.com', 0, error=True,
                           codes=['ERR_NO_LOCAL_PART'],
                           history_str=''
                           ),
                # ERR_EXPECTING_QTEXT
                MyTestData(701, '" "@test.com', 0, error=True, history_str='',
                           codes=['ERR_EXPECTING_QTEXT'],
                           ),

            ]
        )
        self.run_test_data(td)

    def test_local_part(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='local_part',
            # history_level=3,
            tests=[
                # dot-atom
                MyTestData(1001, 'abc.def', 7, history_str='local_part(dot_atom(dot_atom_text(atext, single_dot, atext)))'),
                MyTestData(1002, 'abc', 3, history_str='local_part(dot_atom(dot_atom_text(atext)))'),
                MyTestData(1003, '123.456', 7, history_str='local_part(dot_atom(dot_atom_text(atext, single_dot, atext)))'),
                MyTestData(1004, '#$%.#$%', 7, history_str='local_part(dot_atom(dot_atom_text(atext, single_dot, atext)))'),
                MyTestData(1005, 'abc.123.456', 11,
                           history_str='local_part(dot_atom(dot_atom_text(atext, single_dot, atext, single_dot, atext)))'),
                MyTestData(1006, '(coment) abc.def', 16, codes=['CFWS_COMMENT', 'CFWS_FWS'],
                           history_str='local_part(dot_atom(cfws(comment(open_parenthesis, ccontent(ctext), close_parenthesis), fws(wsp)), dot_atom_text(atext, single_dot, atext)))'),
                MyTestData(1007, 'abc (comment)', 13, codes=['CFWS_COMMENT', 'CFWS_FWS'],
                           history_str='local_part(dot_atom(dot_atom_text(atext), cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), close_parenthesis))))'),
                MyTestData(1008, '\r\n123.456 ', 0, history_str='', codes=[]),
                MyTestData(1009, '\r\n#$%.#$% (comment)', 0, history_str=''),
                MyTestData(1010, '\t\r\nabc.123.456 \t', 0, history_str=''),

                MyTestData(1011, '.abc.def', 0, history_str='', error=True, codes=['ERR_DOT_START']),
                MyTestData(1012, 'abc.', 0, error=True, codes=['ERR_DOT_END']),
                MyTestData(1013, '123..456', 0, codes=['ERR_CONSECUTIVE_DOTS'], error=True),
                MyTestData(1014, '#$%.#$%..', 0, codes=['ERR_CONSECUTIVE_DOTS'], error=True),
                MyTestData(1015, ',abc.123.456', 0, history_str=''),
                MyTestData(1016, '   .abc.def', 0, history_str=''),

                MyTestData(1017, 'abc.def (comment) more@', 0, codes=['ERR_ATEXT_AFTER_CFWS'], error=True),

                # quoted_string

                # normal qs
                MyTestData(2001, '"test"', 6, codes='RFC5321_QUOTED_STRING',
                           history_str='local_part(quoted_string(double_quote, qcontent(qtext), double_quote))'),

                # qs with more words
                MyTestData(2002, '"this is a test"', 16, codes=['RFC5321_QUOTED_STRING'],
                           history_str='local_part(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))'),

                # qs with enclosed comment
                MyTestData(2003, '"this (is a) test"', 18, codes=['RFC5321_QUOTED_STRING'],
                           history_str='local_part(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))'),

                # qs with fail initially
                MyTestData(2004, ' "this is a test"', 17, codes=('RFC5321_QUOTED_STRING', 'CFWS_FWS'),
                           history_str='local_part(quoted_string(cfws(fws(wsp)), double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))'),
                MyTestData(2005, ' (this is a comment) "this is a test"', 37,
                           codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS'),
                           history_str='local_part(quoted_string(cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis), fws(wsp)), double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))'),
                MyTestData(2006, 'blah"this is a test"', 0, history_str='', error=True, codes=['ERR_EXPECTING_ATEXT']),

                # Qs with cfws after
                MyTestData(2008, '"this is a test" (this is a comment)', 36,
                           codes=['RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS'],
                           history_str='local_part(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote, cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis))))'),

                # qs with cfws both
                MyTestData(2009, ' (this is a pre comment) "this is a test" (this is a post comment)', 66,
                           codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS'),
                           history_str='local_part(quoted_string(cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis), fws(wsp)), double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote, cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis))))'),

                # unclosed qs
                MyTestData(2010, '"this is a test', 0,
                           codes=['ERR_UNCLOSED_QUOTED_STR'], error=True, history_str=''),

                # fws in qs
                MyTestData(2012, '" this\tis a test"', 17, codes='RFC5321_QUOTED_STRING',
                           history_str='local_part(quoted_string(double_quote, fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))'),

                # mult fws in qs
                MyTestData(2013, '(  this is a test)', 0, history_str=''),
                MyTestData(2014, '(this is a  test)', 0, history_str=''),

                # quoted pair in qs
                MyTestData(2015, '"this \\r\\nis a test"', 20, codes='RFC5321_QUOTED_STRING',
                           history_str='local_part(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(quoted_pair(back_slash, vchar_wsp)), qcontent(quoted_pair(back_slash, vchar_wsp)), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))'),
                MyTestData(2016, '"test"of a test', 0, history_str='', codes=['ERR_ATEXT_AFTER_QS', 'RFC5321_QUOTED_STRING'], error=True),

                # obs-local-part


                MyTestData(3002, 'word.and.another.word', 21, codes=[],
                           history_str='local_part(dot_atom(dot_atom_text(atext, single_dot, atext, single_dot, atext, single_dot, atext)))'),
                MyTestData(3003, '"this is a word"', 16, codes=['RFC5321_QUOTED_STRING'],
                           history_str='local_part(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))'),

                MyTestData(3004, '"this is (a comment) . inside a quote".test', 43,
                           codes=['RFC5321_QUOTED_STRING', 'DEPREC_LOCAL_PART'],
                           history_str='local_part(obs_local_part(word(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)), single_dot, word(atom(atext))))'),
                MyTestData(3005, 'test."this is (a comment inside a quote"', 40,
                           codes=['RFC5321_QUOTED_STRING', 'DEPREC_LOCAL_PART'],
                           history_str='local_part(obs_local_part(word(atom(atext)), single_dot, word(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))))'),
                MyTestData(3006, 'test."this is (a comment) inside a quote.test.test', 0,
                           codes=['ERR_DOT_END'], error=True, history_str=''),

                MyTestData(3007, '.word', 0, history_str='', codes=['ERR_DOT_START'], error=True),
                MyTestData(3008, '..word and another word', 0, history_str='', codes=['ERR_DOT_START'], error=True),
                MyTestData(3009, '"this is a word"..', 0, codes=['ERR_DOT_END', 'RFC5321_QUOTED_STRING'], error=True),
                MyTestData(3010, '"this is (a comment) inside a quote".', 0, error=True,
                           codes=['ERR_DOT_END', 'RFC5321_QUOTED_STRING'],
                           history_str=''),

            ]
        )
        self.run_test_data(td)

    def test_domain(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='domain',
            history_level=3,
            tests=[

                # *********************
                # DOMAIN ADDR
                # *********************
                MyTestData(1001, 'ABCdef123.abcder', 16,
                           history_str='domain(domain_addr(tld_domain(...), ...))'),
                MyTestData(1002, 'abcdef-123.acac', 15,
                           history_str='domain(domain_addr(tld_domain(...), ...))'),
                MyTestData(1003, 'abcdef-.12345', 13, codes=['RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'], history_str='domain(dot_atom(dot_atom_text(...)))'),
                MyTestData(1004, '-abcdef.abcdef-', 0, codes='ERR_DOMAIN_HYPHEN_START', error=True),
                MyTestData(1005, 'abcdef', 6, codes='RFC5321_TLD', history_str='domain(domain_addr(tld_domain(...)))'),
                MyTestData(1006, '1abcdef.abcdef', 14, codes='RFC5321_TLD_NUMERIC',
                           history_str='domain(domain_addr(let_dig, ...))'),

                # *********************
                # DOT ATOM
                # *********************
                MyTestData(2001, 'abc.def', 7, history_str='domain(domain_addr(tld_domain(...), ...))'),
                MyTestData(2002, 'abc', 3, codes=['RFC5321_TLD'], history_str='domain(domain_addr(tld_domain(...)))'),
                MyTestData(2003, '123.456', 7, codes=['RFC5321_TLD_NUMERIC'], history_str='domain(domain_addr(let_dig, ...))'),
                MyTestData(2004, '#$%.#$%', 7, codes=['RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'], history_str='domain(dot_atom(dot_atom_text(...)))'),
                MyTestData(2005, 'abc.123.456', 11,
                           history_str='domain(domain_addr(tld_domain(...), ...))'),
                MyTestData(2006, '(coment) abc.def', 16, codes=['CFWS_COMMENT', 'RFC5322_DOMAIN', 'CFWS_FWS', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(dot_atom(cfws(...), dot_atom_text(...)))'),

                MyTestData(2007, 'abc (comment)', 13, codes=['CFWS_COMMENT', 'CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(dot_atom(dot_atom_text(...), cfws(...)))'),

                MyTestData(2008, '\r\n123.456 ', 0, codes=['ERR_EXPECTING_ATEXT'], error=True),
                MyTestData(2009, ' #$%.#$% (comment)', 18, codes=['CFWS_COMMENT', 'CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'], history_str='domain(dot_atom(cfws(...), dot_atom_text(...), cfws(...)))'),
                MyTestData(2010, '\t\r\nabc.123.456 \t', 0, codes=['ERR_EXPECTING_ATEXT'], error=True),

                MyTestData(2011, '.abc.def', 0, codes=['ERR_DOT_START'], error=True),
                MyTestData(2012, 'abc.', 0, codes=['ERR_DOT_END', 'RFC5321_TLD'], error=True),
                MyTestData(2013, '123..456', 0, codes=['ERR_CONSECUTIVE_DOTS'], error=True),
                MyTestData(2014, '#$%.#$%..', 0, codes=['ERR_CONSECUTIVE_DOTS'], error=True),
                MyTestData(2015, ',abc.123.456', 0, codes=['ERR_EXPECTING_ATEXT'], error=True),
                MyTestData(2016, '   .abc.def', 0, codes=['ERR_EXPECTING_ATEXT'], error=True),

                MyTestData(2017, 'abc.def (comment) more@', 0, codes=['ERR_ATEXT_AFTER_CFWS'], error=True),

                # *********************
                # domain literal
                # *********************
                MyTestData(3001, '[test]', 6, codes=['RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(open_sq_bracket, ..., close_sq_bracket))'),
                MyTestData(3002, '[\\rtest]', 8, codes=['RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(open_sq_bracket, ..., close_sq_bracket))'),
                MyTestData(3004, '[\r\nfoo][bar', 0, codes=['ERR_EXPECTING_DTEXT'], error=True),
                MyTestData(3005, '"\r\nfoo[bar', 0, codes=['ERR_EXPECTING_ATEXT'], error=True),

                # no closing
                MyTestData(3101, '[test', 0, codes='ERR_UNCLOSED_DOM_LIT', error=True, history_str=''),
                MyTestData(3102, '[foo[bar]', 0, codes='ERR_UNCLOSED_DOM_LIT', error=True, history_str=''),

                # fws before
                MyTestData(3103, '[\t\\rtest]', 9,
                           codes=['CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(open_sq_bracket, ..., close_sq_bracket))'),
                MyTestData(3104, '[ foo-bar]', 10, codes=['CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(open_sq_bracket, ..., close_sq_bracket))'),
                MyTestData(3105, '[\t\t\r\nfoo][bar', 0, codes=['ERR_EXPECTING_DTEXT'], error=True),

                # fws after
                MyTestData(3106, '[\\rtest ]', 9,
                           codes=['CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT',
                                 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(open_sq_bracket, ..., close_sq_bracket))'),
                MyTestData(3107, '[foobar  ]', 10,
                           codes=['CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(open_sq_bracket, ..., close_sq_bracket))'),
                MyTestData(3108, '[\r\nfoo\t][bar', 0, codes=['ERR_EXPECTING_DTEXT'], error=True),

                # fws both
                MyTestData(3109, '[ \\rtest ]', 10,
                           codes=['CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT',
                                  'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(open_sq_bracket, ..., close_sq_bracket))'),
                MyTestData(3110, '[\tfoobar ]', 10, codes=['CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(open_sq_bracket, ..., close_sq_bracket))'),

                # cfws before
                MyTestData(3200, '(This is a comment)[\\rtest]', 27,
                           codes=['CFWS_COMMENT', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL',
                                  'RFC5322_DOM_LIT_OBS_DTEXT', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(cfws(...), open_sq_bracket, ..., close_sq_bracket))'),
                MyTestData(3201, '\t\t[foo[bar]', 0, codes=['ERR_UNCLOSED_DOM_LIT', 'CFWS_FWS'], error=True,
                           history_str=''),
                MyTestData(3202, ' \r\n [\r\nfoo][bar', 0, codes=['CFWS_FWS', 'ERR_EXPECTING_DTEXT'], error=True),

                # cfws after
                MyTestData(3203, '[\\rtest](this is a post comment)\r\n', 0, codes=['ERR_FWS_CRLF_END'], error=True,
                           history_str=''),
                MyTestData(3204, '[foo[bar] \r\n ', 0, codes=['ERR_UNCLOSED_DOM_LIT'], error=True, history_str=''),
                MyTestData(3205, '[\r\nfoo] \t\t [bar', 0, codes=['ERR_EXPECTING_DTEXT'], error=True),

                # cfws both
                MyTestData(3206, '(comment beore) [\\rtest] (and after)', 36,
                           codes=['CFWS_COMMENT', 'CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL',
                                  'RFC5322_DOM_LIT_OBS_DTEXT', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(cfws(...), open_sq_bracket, ..., close_sq_bracket, cfws(...)))'),
                MyTestData(3207, ' [foo[bar] \t\t', 0, codes=['ERR_UNCLOSED_DOM_LIT', 'CFWS_FWS'], error=True,
                           history_str=''),
                MyTestData(3208, '\t[\r\nfoo] [bar', 0, codes=['CFWS_FWS', 'ERR_EXPECTING_DTEXT'], error=True),

                # mixed
                MyTestData(3302, '(comment before)[ \\rtest]', 25,
                           codes=['CFWS_COMMENT', 'CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL',
                                  'RFC5322_DOM_LIT_OBS_DTEXT', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(cfws(...), open_sq_bracket, ..., close_sq_bracket))'),
                MyTestData(3303, '(comment before)[foo[bar ] ', 0, codes=['ERR_UNCLOSED_DOM_LIT', 'CFWS_COMMENT'],
                           error=True, history_str=''),
                MyTestData(3304, '\t\t[ \r\nfoo](and after)\t[bar', 0, codes=['CFWS_FWS', 'ERR_EXPECTING_DTEXT'], error=True),

                MyTestData(3401, '(comment before)[ \\rtest] blah', 0,
                           codes=['RFC5322_DOM_LIT_OBS_DTEXT', 'ERR_ATEXT_AFTER_DOMLIT', 'CFWS_COMMENT', 'CFWS_FWS'],
                           error=True),

                # *********************
                # address literal
                # *********************
                # ipv6 full  - PASS
                MyTestData(4001, '[IPv6:0:0:0:0:0:0:0:0]', 22,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4002, '[IPv6:1111:1111:1111:1111:1111:1111:1111:1111]', 46,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4003, '[IPv6:12ab:abcd:fedc:1212:0:00:000:0]', 37,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),

                # ipv6 full  - FAIL
                MyTestData(4004, '[IPv6:0:0:0:0:0:0:hhy:0]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True,
                           history_str=''),
                MyTestData(4005, '[IPv6::1111:1111:1111:1111:1111:1111:1111:1111]', 0, codes=['ERR_INVALID_ADDR_LITERAL'],
                           error=True, history_str=''),
                MyTestData(4006, '[IPv6:12aba:1abcd:fedc:1212:0:00:000:0]', 0, codes=['ERR_INVALID_ADDR_LITERAL'],
                           error=True, history_str=''),

                MyTestData(4101, '[IPv6:0::0:0:0:0:0]', 19,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4102, '[IPv6:0::0:0:0:0]', 17,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4103, '[IPv6:0::0:0:0]', 15,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4104, '[IPv6:0::0:0]', 13,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4105, '[IPv6:0::0]', 11,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),

                MyTestData(4106, '[IPv6:0:0::0:0:0:0]', 19,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4107, '[IPv6:0:0::0:0:0]', 17,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4108, '[IPv6:0:0::0:0]', 15,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4109, '[IPv6:0:0::0]', 13,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),

                MyTestData(4110, '[IPv6:0:0:0::0:0:0]', 19,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4111, '[IPv6:0:0:0::0:0]', 17,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4112, '[IPv6:0:0:0::0]', 15,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),

                MyTestData(4113, '[IPv6:0:0:0:0::0:0]', 19,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4114, '[IPv6:0:0:0:0::0]', 17,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),

                MyTestData(4115, '[IPv6:0:0:0:0:0::0]', 19,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),

                # ipv6 comp - FAIL
                MyTestData(4116, '[IPv6:0::0:0:0:0:0:0]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True,
                           history_str=''),
                MyTestData(4117, '[IPv6:0:0:0:0::0:0:0:0]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True,
                           history_str=''),

                # ipv6-4 - PASS
                MyTestData(4201, '[IPv6:0:0:0:0:0:0:1.1.1.1]', 26,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                # ipv6-4 - FAIL
                MyTestData(4203, '[IPv6:0:0:0:0:0:1.1.1.1]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True,
                           history_str=''),
                MyTestData(4205, '[IPv6:0:0:0:0:0:0:1.1.1]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True,
                           history_str=''),

                # ipv6-4 comp - PASS

                MyTestData(4301, '[IPv6:0::0:0:0:1.1.1.1]', 23,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4302, '[IPv6:0::0:0:1.1.1.1]', 21,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4303, '[IPv6:0::0:1.1.1.1]', 19,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),

                MyTestData(4304, '[IPv6:0:0::0:0:1.1.1.1]', 23,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),
                MyTestData(4305, '[IPv6:0:0::0:1.1.1.1]', 21,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),

                MyTestData(4306, '[IPv6:0:0:0::0:1.1.1.1]', 23,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket))'),

                # ipv6-4 comp - FAIL
                MyTestData(4307, '[IPv6:0:0:0::0:0:0:1.1.1.1]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True,
                           history_str=''),

                # ipv4 PASS / FAIL
                MyTestData(4401, '[1.1.1.1]', 9, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket))'),
                MyTestData(4402, '[123.123.123.123]', 17, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket))'),
                MyTestData(4403, '[13.13.255.0]', 13, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket))'),
                MyTestData(4404, '[255.255.255.255]', 17, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket))'),
                MyTestData(4405, '[0.0.0.0.]', 0, codes=['ERR_UNCLOSED_DOM_LIT'], error=True, history_str=''),
                MyTestData(4406, '[0.0.0.0]', 9, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'],
                           history_str='domain(address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket))'),
                MyTestData(4407, '[.0.0.0.0]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),
                MyTestData(4408, '[1.2.3]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),
                MyTestData(4409, '[300.2.1.1]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),
                MyTestData(4410, '[blah]', 6, codes=['RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(open_sq_bracket, ..., close_sq_bracket))'),

                # general addr PASS/FAIL
                MyTestData(4501, '[abcd:abcdeg]', 13,
                           codes=['RFC5322_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(domain_literal(open_sq_bracket, ..., close_sq_bracket))'),
                MyTestData(4502, '[http:foobar]', 13,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_DOMAIN', 'RFC5322_GENERAL_LITERAL',
                                  'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(address_literal(open_sq_bracket, general_address_literal(...), close_sq_bracket))'),

                # Enclosure fail
                MyTestData(4601, '[1.1.1.1', 0, codes=['ERR_UNCLOSED_DOM_LIT'], error=True, history_str=''),

                # no start enclosure fail
                MyTestData(4602, '1.1.1.1]', 0, history_str='', codes=['ERR_EXPECTING_ATEXT', 'RFC5321_TLD_NUMERIC'], error=True),

                # data past enclosure
                MyTestData(4603, '[1.1.1.1]foobar', 0, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR', 'ERR_ATEXT_AFTER_DOMLIT'], error=True),

                # *********************
                # OBS DOMAIN
                # *********************

                MyTestData(5001, 'thisisanatom$%^.this_is_another_one', 35, codes=['RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(dot_atom(dot_atom_text(...)))'),
                MyTestData(5002, '(this is a comment) atom (this is a comment).this_is_atom', 57,
                           codes=['CFWS_COMMENT', 'CFWS_FWS', 'RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'],
                           history_str='domain(obs_domain(atom(...), ...))'),
                MyTestData(5003, 'blah_blah_blah.(this is a comment) atom (this is a comment', 0,
                           codes=['ERR_UNCLOSED_COMMENT'], error=True, history_str=''),
                MyTestData(5004, 'blah_blah_blah.(this is a comment) atom (this is a comment' + make_char_str(0), 0,
                           codes=['ERR_EXPECTING_CTEXT'], error=True, history_str=''),
                MyTestData(5005, '(this is a comment) atom (this is a comment).this_is_atom."This_is_a_quote"', 0,
                           codes=['CFWS_COMMENT', 'CFWS_FWS', 'ERR_EXPECTING_ATEXT', 'RFC5322_DOMAIN',
                                  'RFC5322_LIMITED_DOMAIN'], error=True, history_str=''),

                # *********************
                # Misc Errors
                # *********************

                # ERR_BACKSLASH_END
                MyTestData(6001, 'test.com\\', 0, error=True, history_str='',
                           codes=['ERR_BACKSLASH_END'],
                           ),

                # ERR_DOMAIN_HYPHEN_END
                MyTestData(6002, 'test.com-', 0, error=True, history_str='',
                           codes=['ERR_DOMAIN_HYPHEN_END', 'RFC5322_DOMAIN', 'RFC5322_LIMITED_DOMAIN'],
                           ),

                # ERR_EXPECTING_DTEXT
                MyTestData(6003, '[ ]', 0, error=True, history_str='',
                           codes=['ERR_EXPECTING_DTEXT'],
                           ),


            ]
        )
        self.run_test_data(td)

    def test_dot_atom(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='dot_atom',
            # trace_filter=5,
            tests=[
                MyTestData(1, 'abc.def', 7, history_str='dot_atom(dot_atom_text(atext, single_dot, atext))'),
                MyTestData(2, 'abc', 3, history_str='dot_atom(dot_atom_text(atext))'),
                MyTestData(3, '123.456', 7, history_str='dot_atom(dot_atom_text(atext, single_dot, atext))'),
                MyTestData(4, '#$%.#$%', 7, history_str='dot_atom(dot_atom_text(atext, single_dot, atext))'),
                MyTestData(5, 'abc.123.456', 11, history_str='dot_atom(dot_atom_text(atext, single_dot, atext, single_dot, atext))'),

                MyTestData(6, '(coment) abc.def', 16, codes=['CFWS_COMMENT', 'CFWS_FWS'],
                           history_str='dot_atom(cfws(comment(open_parenthesis, ccontent(ctext), close_parenthesis), fws(wsp)), dot_atom_text(atext, single_dot, atext))'),
                MyTestData(7, 'abc (comment)', 13, codes=['CFWS_COMMENT', 'CFWS_FWS'],
                           history_str='dot_atom(dot_atom_text(atext), cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), close_parenthesis)))'),
                MyTestData(8, '\r\n123.456 ', 0, history_str=''),
                MyTestData(9, '\r\n#$%.#$% (comment)', 0, history_str=''),
                MyTestData(10, '\t\r\nabc.123.456 \t', 0, history_str=''),

                MyTestData(11, '.abc.def', 0, history_str=''),
                MyTestData(12, 'abc.', 3, history_str='dot_atom(dot_atom_text(atext))'),
                MyTestData(13, '123..456', 0, codes=['ERR_CONSECUTIVE_DOTS'], error=True),
                MyTestData(14, '#$%.#$%..', 0, codes=['ERR_CONSECUTIVE_DOTS'], error=True),
                MyTestData(15, ',abc.123.456', 0, history_str=''),
                MyTestData(16, '   .abc.def', 0, history_str=''),

                MyTestData(17, 'abc.def (comment) more@', 0, codes=['ERR_ATEXT_AFTER_CFWS'], error=True),

            ]
        )
        self.run_test_data(td)

    def test_dot_atom_text(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='dot_atom_text',
            tests=[
                MyTestData(1, 'abc.def', 7, history_str='dot_atom_text(atext, single_dot, atext)'),
                MyTestData(2, 'abc', 3, history_str='dot_atom_text(atext)'),
                MyTestData(3, '123.456', 7, history_str='dot_atom_text(atext, single_dot, atext)'),
                MyTestData(4, '#$%.#$%', 7, history_str='dot_atom_text(atext, single_dot, atext)'),
                MyTestData(5, 'abc.123.456', 11, history_str='dot_atom_text(atext, single_dot, atext, single_dot, atext)'),

                MyTestData(6, '.abc.def', 0, history_str=''),
                MyTestData(7, 'abc.', 3, history_str='dot_atom_text(atext)'),
                MyTestData(8, '123..456', 0, codes=['ERR_CONSECUTIVE_DOTS'], error=True),
                MyTestData(9, '#$%.#$%..', 0, codes=['ERR_CONSECUTIVE_DOTS'], error=True),
                MyTestData(10, ',abc.123.456', 0, history_str=''),

            ]
        )
        self.run_test_data(td)

    def test_obs_local_part(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='obs_local_part',
            tests=[
                MyTestData(1, 'word', 4, codes=['DEPREC_LOCAL_PART'], history_str='obs_local_part(word(atom(atext)))'),
                MyTestData(2, 'word.and.another.word', 21, codes=['DEPREC_LOCAL_PART'], history_str='obs_local_part(word(atom(atext)), single_dot, word(atom(atext)), single_dot, word(atom(atext)), single_dot, word(atom(atext)))'),
                MyTestData(3, '"this is a word"', 16, codes=['RFC5321_QUOTED_STRING', 'DEPREC_LOCAL_PART'], history_str='obs_local_part(word(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)))'),
                MyTestData(4, '"this is (a comment) . inside a quote".test', 43, codes=['RFC5321_QUOTED_STRING', 'DEPREC_LOCAL_PART'], history_str='obs_local_part(word(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)), single_dot, word(atom(atext)))'),
                MyTestData(5, 'test."this is (a comment inside a quote"', 40, codes=['RFC5321_QUOTED_STRING', 'DEPREC_LOCAL_PART'], history_str='obs_local_part(word(atom(atext)), single_dot, word(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)))'),
                MyTestData(6, 'test."this is (a comment) inside a quote.test.test', 0, codes=['ERR_UNCLOSED_QUOTED_STR'], error=True, history_str=''),

                MyTestData(7, '.word', 0, history_str=''),
                MyTestData(8, '..word and another word', 0, history_str=''),
                MyTestData(9, '"this is a word"..', 0, codes=['ERR_CONSECUTIVE_DOTS'], error=True),
                MyTestData(10, '"this is (a comment) inside a quote".', 36, codes=['RFC5321_QUOTED_STRING', 'DEPREC_LOCAL_PART'], history_str='obs_local_part(word(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)))'),
            ]
        )
        self.run_test_data(td)

    def test_word(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='word',
            tests=[
                MyTestData(1, 'word', 4, history_str='word(atom(atext))'),
                MyTestData(2, 'word and another word', 0, codes=['ERR_ATEXT_AFTER_CFWS'], error=True),
                MyTestData(3, '"this is a word"', 16, codes=['RFC5321_QUOTED_STRING'], history_str='word(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))'),
                MyTestData(4, '"this is (a comment) inside a quote"', 36, codes=['RFC5321_QUOTED_STRING'], history_str='word(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))'),
                MyTestData(5, '"this is (a comment inside a quote"', 35, codes=['RFC5321_QUOTED_STRING'], history_str='word(quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote))'),
                MyTestData(6, '"this is (a comment) inside a quote', 0, codes=['ERR_UNCLOSED_QUOTED_STR'], error=True, history_str=''),
            ]
        )
        self.run_test_data(td)

    def test_atom(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='atom',
            tests=[
                MyTestData(1, 'thisisanatom$%^', 15, history_str='atom(atext)'),
                MyTestData(2, '(this is a comment) atom (this is a comment)', 44, codes=['CFWS_FWS', 'CFWS_COMMENT'],
                           history_str='atom(cfws(comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis), fws(wsp)), atext, cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)))'),
                MyTestData(3, '(this is a comment) atom (this is another comment', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True),
                MyTestData(4, 'thisisatom (this is comment)atom', 0, error=True, codes=['ERR_ATEXT_AFTER_CFWS']),
                MyTestData(5, 'thisisatom (this is comment)@atom', 28, codes=['CFWS_COMMENT', 'CFWS_FWS'], history_str='atom(atext, cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)))'),

            ]
        )
        self.run_test_data(td)

    def test_domain_addr(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='domain_addr',
            tests=[
                MyTestData(1, 'ABCdef123.abcder', 16, history_str='domain_addr(tld_domain(alpha, ldh_str), single_dot, sub_domain(let_dig))'),
                MyTestData(2, 'abcdef-123.acac', 15, history_str='domain_addr(tld_domain(alpha, ldh_str), single_dot, sub_domain(let_dig))'),
                MyTestData(3, 'abcdef-.12345', 6, codes='RFC5321_TLD', history_str='domain_addr(tld_domain(alpha))'),
                MyTestData(4, '-abcdef.abcdef-', 0, history_str=''),
                MyTestData(5, 'abcdef', 6, codes='RFC5321_TLD', history_str='domain_addr(tld_domain(alpha))'),
                MyTestData(6, '1abcdef.abcdef', 14, codes='RFC5321_TLD_NUMERIC', history_str='domain_addr(let_dig, single_dot, sub_domain(let_dig))'),
            ]
        )
        self.run_test_data(td)

    def test_sub_domain(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='sub_domain',
            tests=[
                MyTestData(1, 'ABCdef123', 9, history_str='sub_domain(let_dig)'),
                MyTestData(2, 'abcdef-123', 10, history_str='sub_domain(let_dig, ldh_str)'),
                MyTestData(3, 'abcdef-', 6, history_str='sub_domain(let_dig)'),
                MyTestData(4, '-abcdef', 0, history_str=''),
            ]
        )
        self.run_test_data(td)

    def test_let_str(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='let_str',
            tests=[
                MyTestData(1, 'ABCdef123', 9, history_str='let_str(ldh_str)'),
                MyTestData(2, 'abcdef-123', 10, history_str='let_str(ldh_str)'),
                MyTestData(3, 'abcdef-', 6, history_str='let_str(ldh_str)'),
                MyTestData(4, '-abcdef', 7, history_str='let_str(ldh_str)'),
                MyTestData(5, '-abcdef-', 7, history_str='let_str(ldh_str)'),
                MyTestData(6, '-abcdef--', 7, history_str='let_str(ldh_str)'),
                MyTestData(7, '-abcdef---', 7, history_str='let_str(ldh_str)'),
                MyTestData(7, '----', 0, history_str=''),

            ]
        )
        self.run_test_data(td)

    def test_domain_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='domain_literal',
            tests=[
                MyTestData(1, '[test]', 6, codes=['RFC5322_DOMAIN_LITERAL'], history_str='domain_literal(open_sq_bracket, dtext, close_sq_bracket)'),
                MyTestData(2, '[\\rtest]', 8, codes=['RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT'], history_str='domain_literal(open_sq_bracket, dtext(obs_dtext(quoted_pair(back_slash, vchar_wsp))), close_sq_bracket)'),
                MyTestData(4, '[\r\nfoo][bar', 0, history_str='', codes=['ERR_EXPECTING_DTEXT'], error=True),
                MyTestData(5, '"\r\nfoo[bar', 0, history_str=''),

                # no closing
                MyTestData(101, '[test', 0, codes='ERR_UNCLOSED_DOM_LIT', error=True, history_str=''),
                MyTestData(102, '[foo[bar]', 0, codes='ERR_UNCLOSED_DOM_LIT', error=True, history_str=''),

                # fws before
                MyTestData(103, '[\t\\rtest]', 9, codes=['RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT', 'CFWS_FWS'], history_str='domain_literal(open_sq_bracket, fws(wsp), dtext(obs_dtext(quoted_pair(back_slash, vchar_wsp))), close_sq_bracket)'),
                MyTestData(104, '[ foo-bar]', 10, codes=['RFC5322_DOMAIN_LITERAL', 'CFWS_FWS'], history_str='domain_literal(open_sq_bracket, fws(wsp), dtext, close_sq_bracket)'),
                MyTestData(105, '[\t\t\r\nfoo][bar', 0, history_str='', codes=['ERR_EXPECTING_DTEXT'], error=True),

                # fws after
                MyTestData(106, '[\\rtest ]', 9, codes=['RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT', 'CFWS_FWS'], history_str='domain_literal(open_sq_bracket, dtext(obs_dtext(quoted_pair(back_slash, vchar_wsp))), fws(wsp), close_sq_bracket)'),
                MyTestData(107, '[foobar  ]', 10, codes=['RFC5322_DOMAIN_LITERAL', 'CFWS_FWS'], history_str='domain_literal(open_sq_bracket, dtext, fws(wsp), close_sq_bracket)'),
                MyTestData(108, '[\r\nfoo\t][bar', 0, history_str='', codes=['ERR_EXPECTING_DTEXT'], error=True),

                # fws both
                MyTestData(109, '[ \\rtest ]', 10, codes=['RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT', 'CFWS_FWS'], history_str='domain_literal(open_sq_bracket, fws(wsp), dtext(obs_dtext(quoted_pair(back_slash, vchar_wsp))), fws(wsp), close_sq_bracket)'),
                MyTestData(110, '[\tfoobar ]', 10, codes=['RFC5322_DOMAIN_LITERAL', 'CFWS_FWS'], history_str='domain_literal(open_sq_bracket, fws(wsp), dtext, fws(wsp), close_sq_bracket)'),

                # cfws before
                MyTestData(200, '(This is a comment)[\\rtest]', 27, codes=['RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT','CFWS_COMMENT'], history_str='domain_literal(cfws(comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)), open_sq_bracket, dtext(obs_dtext(quoted_pair(back_slash, vchar_wsp))), close_sq_bracket)'),
                MyTestData(201, '\t\t[foo[bar]', 0, codes=['ERR_UNCLOSED_DOM_LIT', 'CFWS_FWS'], error=True, history_str=''),
                MyTestData(202, ' \r\n [\r\nfoo][bar', 0, history_str='', codes=['CFWS_FWS', 'ERR_EXPECTING_DTEXT'], error=True),

                # cfws after
                MyTestData(203, '[\\rtest](this is a post comment)\r\n', 0, codes=['ERR_FWS_CRLF_END'], error=True, history_str=''),
                MyTestData(204, '[foo[bar] \r\n ', 0, codes=['ERR_UNCLOSED_DOM_LIT'], error=True, history_str=''),
                MyTestData(205, '[\r\nfoo] \t\t [bar', 0, history_str='', codes=['ERR_EXPECTING_DTEXT'], error=True),

                # cfws both
                MyTestData(206, '(comment beore) [\\rtest] (and after)', 36, codes=['RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT', 'CFWS_COMMENT', 'CFWS_FWS'], history_str='domain_literal(cfws(comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis), fws(wsp)), open_sq_bracket, dtext(obs_dtext(quoted_pair(back_slash, vchar_wsp))), close_sq_bracket, cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)))'),
                MyTestData(207, ' [foo[bar] \t\t', 0, codes=['ERR_UNCLOSED_DOM_LIT', 'CFWS_FWS'], error=True, history_str=''),
                MyTestData(208, '\t[\r\nfoo] [bar', 0, history_str='', codes=['CFWS_FWS', 'ERR_EXPECTING_DTEXT'], error=True),

                # mixed
                MyTestData(302, '(comment before)[ \\rtest]', 25, codes=['RFC5322_DOMAIN_LITERAL', 'RFC5322_DOM_LIT_OBS_DTEXT', 'CFWS_COMMENT', 'CFWS_FWS'], history_str='domain_literal(cfws(comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)), open_sq_bracket, fws(wsp), dtext(obs_dtext(quoted_pair(back_slash, vchar_wsp))), close_sq_bracket)'),
                MyTestData(303, '(comment before)[foo[bar ] ', 0, codes=['ERR_UNCLOSED_DOM_LIT', 'CFWS_COMMENT'], error=True, history_str=''),
                MyTestData(304, '\t\t[ \r\nfoo](and after)\t[bar', 0, history_str='', codes=['CFWS_FWS', 'ERR_EXPECTING_DTEXT'], error=True),

                MyTestData(401, '(comment before)[ \\rtest] blah', 0,
                           codes=['RFC5322_DOM_LIT_OBS_DTEXT', 'ERR_ATEXT_AFTER_DOMLIT', 'CFWS_COMMENT', 'CFWS_FWS'],
                           error=True),

            ]
        )
        self.run_test_data(td)

    def test_dtext(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='dtext',
            tests=[
                MyTestData(1, 'test', 4, history_str='dtext'),
                MyTestData(2, '\\rtest', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT', history_str='dtext(obs_dtext(quoted_pair(back_slash, vchar_wsp)))'),
                MyTestData(3, 'foo[bar', 3, history_str='dtext'),
                MyTestData(4, '\r\nfoo[bar', 0, history_str=''),
                MyTestData(5, '"\r\nfoo[bar', 1, history_str='dtext'),
            ]
        )
        self.run_test_data(td)

    def test_obs_dtext(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='obs_dtext',
            tests=[
                MyTestData(1, 'test', 4, codes='RFC5322_DOM_LIT_OBS_DTEXT', history_str='obs_dtext'),
                MyTestData(2, '\\rtest', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT', history_str='obs_dtext(quoted_pair(back_slash, vchar_wsp))'),
                MyTestData(3, 'foo[bar', 3, codes='RFC5322_DOM_LIT_OBS_DTEXT', history_str='obs_dtext'),
                MyTestData(4, '\r\nfoo[bar', 0, history_str=''),
                MyTestData(5, '"\r\nfoo[bar', 1, codes='RFC5322_DOM_LIT_OBS_DTEXT', history_str='obs_dtext'),
            ]
        )
        self.run_test_data(td)

    def test_obs_domain(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='obs_domain',
            tests=[
                MyTestData(1, 'thisisanatom$%^.this_is_another_one', 35, history_str='obs_domain(atom(atext), single_dot, atom(atext))'),
                MyTestData(2, '(this is a comment) atom (this is a comment).this_is_atom', 57, codes=['CFWS_FWS', 'CFWS_COMMENT'], history_str='obs_domain(atom(cfws(comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis), fws(wsp)), atext, cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis))), single_dot, atom(atext))'),
                MyTestData(3, 'blah_blah_blah.(this is a comment) atom (this is a comment', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True, history_str=''),
                MyTestData(4, 'blah_blah_blah.(this is a comment) atom (this is a comment'+make_char_str(0), 0, codes=['ERR_EXPECTING_CTEXT'], error=True, history_str=''),
                MyTestData(5, '(this is a comment) atom (this is a comment).this_is_atom."This_is_a_quote"', 57,
                           codes=['CFWS_FWS', 'CFWS_COMMENT'], history_str='obs_domain(atom(cfws(comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis), fws(wsp)), atext, cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis))), single_dot, atom(atext))'),

            ]
        )
        self.run_test_data(td)

    def test_address_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            trace_filter=2,
            history_level=2,
            method_name='address_literal',
            tests=[

                # ipv6 full  - PASS
                MyTestData(1, '[IPv6:0:0:0:0:0:0:0:0]', 22, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(2, '[IPv6:1111:1111:1111:1111:1111:1111:1111:1111]', 46,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(3, '[IPv6:12ab:abcd:fedc:1212:0:00:000:0]', 37,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),

                # ipv6 full  - FAIL
                MyTestData(4, '[IPv6:0:0:0:0:0:0:hhy:0]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),
                MyTestData(5, '[IPv6::1111:1111:1111:1111:1111:1111:1111:1111]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),
                MyTestData(6, '[IPv6:12aba:1abcd:fedc:1212:0:00:000:0]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),

                MyTestData(101, '[IPv6:0::0:0:0:0:0]', 19, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(102, '[IPv6:0::0:0:0:0]', 17, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(103, '[IPv6:0::0:0:0]', 15, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(104, '[IPv6:0::0:0]', 13, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(105, '[IPv6:0::0]', 11, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),

                MyTestData(106, '[IPv6:0:0::0:0:0:0]', 19, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(107, '[IPv6:0:0::0:0:0]', 17, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(108, '[IPv6:0:0::0:0]', 15, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(109, '[IPv6:0:0::0]', 13, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),

                MyTestData(110, '[IPv6:0:0:0::0:0:0]', 19, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(111, '[IPv6:0:0:0::0:0]', 17, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(112, '[IPv6:0:0:0::0]', 15, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),

                MyTestData(113, '[IPv6:0:0:0:0::0:0]', 19, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(114, '[IPv6:0:0:0:0::0]', 17, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),

                MyTestData(115, '[IPv6:0:0:0:0:0::0]', 19, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),

                # ipv6 comp - FAIL
                MyTestData(116, '[IPv6:0::0:0:0:0:0:0]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),
                MyTestData(117, '[IPv6:0:0:0:0::0:0:0:0]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),

                # ipv6-4 - PASS
                MyTestData(201, '[IPv6:0:0:0:0:0:0:1.1.1.1]', 26, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),

                # ipv6-4 - FAIL
                MyTestData(203, '[IPv6:0:0:0:0:0:1.1.1.1]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),
                MyTestData(205, '[IPv6:0:0:0:0:0:0:1.1.1]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),

                # ipv6-4 comp - PASS

                MyTestData(301, '[IPv6:0::0:0:0:1.1.1.1]', 23,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(302, '[IPv6:0::0:0:1.1.1.1]', 21, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(303, '[IPv6:0::0:1.1.1.1]', 19, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),

                MyTestData(304, '[IPv6:0:0::0:0:1.1.1.1]', 23,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),
                MyTestData(305, '[IPv6:0:0::0:1.1.1.1]', 21, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),

                MyTestData(306, '[IPv6:0:0:0::0:1.1.1.1]', 23,
                           codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR'], history_str='address_literal(open_sq_bracket, ipv6_address_literal(...), close_sq_bracket)'),

                # ipv6-4 comp - FAIL
                MyTestData(307, '[IPv6:0:0:0::0:0:0:1.1.1.1]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),

                # ipv4 PASS / FAIL
                MyTestData(401, '[1.1.1.1]', 9, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'], history_str='address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket)'),
                MyTestData(402, '[123.123.123.123]', 17, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'], history_str='address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket)'),
                MyTestData(403, '[13.13.255.0]', 13, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'], history_str='address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket)'),
                MyTestData(404, '[255.255.255.255]', 17, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'], history_str='address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket)'),
                MyTestData(405, '[0.0.0.0.]', 0, codes=['ERR_UNCLOSED_DOM_LIT'], error=True, history_str=''),
                MyTestData(406, '[0.0.0.0]', 9, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'], history_str='address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket)'),
                MyTestData(407, '[.0.0.0.0]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),
                MyTestData(408, '[1.2.3]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),
                MyTestData(409, '[300.2.1.1]', 0, codes=['ERR_INVALID_ADDR_LITERAL'], error=True, history_str=''),
                MyTestData(410, '[blah]', 0, history_str=''),
                
                # general addr PASS/FAIL
                MyTestData(501, '[abcd:abcdeg]', 0, history_str=''),
                MyTestData(502, '[http:foobar]', 13, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_GENERAL_LITERAL'], history_str='address_literal(open_sq_bracket, general_address_literal(...), close_sq_bracket)'),
                MyTestData(503, '[foobar]', 0, history_str=''),
                MyTestData(504, '[blah:]', 0, history_str=''),
                MyTestData(505, '[:snafu]', 0, history_str=''),

                # Enclosure fail
                MyTestData(601, '[1.1.1.1', 0, codes=['ERR_UNCLOSED_DOM_LIT'], error=True, history_str=''),

                # no start enclosure fail
                MyTestData(602, '1.1.1.1]', 0, history_str=''),

                # data past enclosure
                MyTestData(603, '[1.1.1.1]foobar', 9, codes=['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'], history_str='address_literal(open_sq_bracket, ipv4_address_literal(...), close_sq_bracket)'),


            ]
        )
        self.run_test_data(td)

    def test_general_address_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='general_address_literal',
            tests=[
                MyTestData(1, 'abcd:abcdeg',0, history_str=''),
                MyTestData(2, 'http:foobar', 11, codes='RFC5322_GENERAL_LITERAL', history_str='general_address_literal(standardized_tag, colon, dcontent)'),
                MyTestData(3, 'foobar', 0, history_str=''),
                MyTestData(4, 'blah:', 0, history_str=''),
                MyTestData(5, ':snafu', 0, history_str=''),
            ]
        )
        self.run_test_data(td)

    def test_ldh_str(self):

        td = MyTestDefs(
            limit_to=-1,
            method_name='ldh_str',
            tests=[
                MyTestData(1, 'abc-123', 7, history_str='ldh_str'),
                MyTestData(2, 'abc--123', 8, history_str='ldh_str'),
                MyTestData(3, 'abcdef-', 6, history_str='ldh_str'),
                MyTestData(4, 'abcdef--', 6, history_str='ldh_str'),
                MyTestData(5, 'abcdef-4', 8, history_str='ldh_str'),
                MyTestData(6, 'abc.def.', 3, history_str='ldh_str'),
                MyTestData(7, 'abc.def.ghi(blah.blah)', 4, position=12, history_str='ldh_str'),
            ]
        )
        self.run_test_data(td)

    def test_ipv4_address_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='ipv4_address_literal',
            tests=[
                MyTestData(1, '1.1.1.1', 7, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(2, '123.123.123.123', 15, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(3, '13.13.255.0', 11, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(4, '255.255.255.255', 15, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(5, '0.0.0.0.', 7, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(6, '0.0.0.0', 7, codes='RFC5322_IPV4_ADDR', history_str='ipv4_address_literal(snum, single_dot, snum, single_dot, snum, single_dot, snum)'),
                MyTestData(7, '.0.0.0.0',0, history_str=''),
                MyTestData(8, '1.2.3', 0, history_str=''),
                MyTestData(9, '300.2.1.1', 0, history_str=''),
                MyTestData(10, 'blah', 0, history_str=''),
            ]
        )
        self.run_test_data(td)

    def test_snum(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='snum',
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
            trace_filter=4,
            history_level=3,
            method_name='ipv6_address_literal',
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
            method_name='ipv6_hex',
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
            method_name='ipv6_full',
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
            method_name='ipv6_comp',
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
            method_name='ipv6v4_full',
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
            method_name='ipv6v4_comp',
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

    def test_cfws(self):
        FF = make_char_str(12)
        td = MyTestDefs(
            limit_to=-1,
            method_name='cfws',
            tests=[

                # normal comment
                MyTestData(1, '(test)', 6, codes='CFWS_COMMENT', history_str='cfws(comment(open_parenthesis, ccontent(ctext), close_parenthesis))'),

                # fws before
                MyTestData(2, ' (test)', 7, codes=['CFWS_COMMENT', 'CFWS_FWS'],
                           history_str='cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), close_parenthesis))'),

                # fws after
                MyTestData(3, '(test) ', 7, codes=['CFWS_COMMENT', 'CFWS_FWS'], history_str='cfws(comment(open_parenthesis, ccontent(ctext), close_parenthesis), fws(wsp))'),

                # fws both
                MyTestData(4, ' (test) ', 8, codes=['CFWS_COMMENT', 'CFWS_FWS'],
                           history_str='cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), close_parenthesis), fws(wsp))'),

                # fws only
                MyTestData(5, ' ', 1, codes='CFWS_FWS', history_str='cfws(fws(wsp))'),

                # mult fws before
                MyTestData(6, '  (test)', 8, codes=['CFWS_COMMENT', 'CFWS_FWS'],
                           history_str='cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), close_parenthesis))'),

                # mult fws after
                MyTestData(7, '(test)  ', 8, codes=['CFWS_COMMENT', 'CFWS_FWS'], history_str='cfws(comment(open_parenthesis, ccontent(ctext), close_parenthesis), fws(wsp))'),

                # fws with comment error
                # comment around @
                MyTestData(8, ' (this is @ test)', 17,
                           codes=['CFWS_COMMENT', 'CFWS_FWS'],
                           history_str='cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis))'),

                # unclosed comment
                MyTestData(9, ' (this is a test', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True, history_str=''),
                MyTestData(10, ' (this (is a test', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True, history_str=''),

                # near AT
                MyTestData(11, '(test)@', 6, codes=['CFWS_COMMENT'],
                           history_str='cfws(comment(open_parenthesis, ccontent(ctext), close_parenthesis))'),


            ]
        )
        self.run_test_data(td)

    def test_comment(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='comment',
            trace_filter=2,
            tests=[

                # normal comment
                MyTestData(1, '(test)', 6, codes=['CFWS_COMMENT'], history_str='comment(open_parenthesis, ccontent(ctext), close_parenthesis)'),

                # comment with more words
                MyTestData(2, '(this is a test)', 16, codes=['CFWS_COMMENT'], history_str='comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)'),

                # comment with enclosed comment
                MyTestData(3, '(this (is a) test)', 18, codes=['CFWS_COMMENT'],
                           history_str='comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)), fws(wsp), ccontent(ctext), close_parenthesis)'),

                # comment around @
                MyTestData(4, '(this is @ test)', 16, codes=['CFWS_COMMENT'], history_str='comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)'),

                # unclosed comment
                MyTestData(5, '(this is a test', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True),
                MyTestData(6, '(this (is a test', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True),

                # fws in comment
                MyTestData(7, '( this is a test)', 17, codes=['CFWS_COMMENT'], history_str='comment(open_parenthesis, fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)'),
                MyTestData(8, '( this\tis a test)', 17, codes=['CFWS_COMMENT'], history_str='comment(open_parenthesis, fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)'),

                # mult fws in comment
                MyTestData(9, '( \r\n \r\n this is a test)', 0, codes=['ERR_MULT_FWS_IN_COMMENT', 'DEPREC_FWS'], error=True),
                MyTestData(10, '(this is a \r\n  test)', 0, codes=['ERR_MULT_FWS_IN_COMMENT'], error=True),

                # quoted pair in comment
                MyTestData(11, '(this \\r\\nis a test)', 20, codes=['CFWS_COMMENT'], history_str='comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(quoted_pair(back_slash, vchar_wsp)), ccontent(quoted_pair(back_slash, vchar_wsp)), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)'),

            ]
        )
        self.run_test_data(td)

    def test_ctext(self):
        FF = make_char_str(12)
        td = MyTestDefs(
            limit_to=-1,
            method_name='ctext',
            tests=[

                # qtext
                MyTestData(31, 'foobar', 6, history_str='ctext'),
                MyTestData(33, 'foobar ', 6, history_str='ctext'),
                MyTestData(34, ' foobar', 0),
                MyTestData(35, '(foobar', 0),
                MyTestData(36, 'foobar)', 6, history_str='ctext'),

                # obs qtext
                MyTestData(41, FF, 1, codes='DEPREC_CTEXT', history_str='ctext(obs_ctext)'),

            ]
        )
        self.run_test_data(td)

    def test_sub_fws(self):

        td = MyTestDefs(
            limit_to=-1,
            method_name='fws_sub',
            tests=[
                # good tries
                MyTestData(2, '\t\r\n\t', 4, history_str='fws_sub(wsp, crlf, one_wsp)'),
                MyTestData(3, '\t\t\t\r\n\t', 6, history_str='fws_sub(wsp, crlf, one_wsp)'),
                MyTestData(4, ' ', 1, history_str='fws_sub(wsp)'),

                # no final wsp
                MyTestData(1, '\t\r\n', 0),

                # only cr
                MyTestData(5, '\r\n', 0),

                # starts with cr
                MyTestData(6, '\r\n', 0),

                # multiple wsp after crlf
                MyTestData(7, '\t\r\n\t\t', 4, history_str='fws_sub(wsp, crlf, one_wsp)'),

                # multiple wsp
                MyTestData(8, '\t\t\t', 3, history_str='fws_sub(wsp)'),

                # no pre-wsp
                MyTestData(9, '\r\n\t\t', 0),

                # crlf at end
                MyTestData(10, '\t\r\n', 0),

                # multiple crlf
                MyTestData(11, '\t\t\r\n\r\n', 0, codes='ERR_FWS_CRLF_X2', error=True),

                # crlf + cr
                MyTestData(12, '\t\t\r\n\r\t\t', 0, codes='ERR_CR_NO_LF', error=True),

            ]
        )
        self.run_test_data(td)

    def test_obs_fws(self):

        td = MyTestDefs(
            limit_to=-1,
            method_name='obs_fws',
            tests=[
                MyTestData(1, '\t', 1, codes='DEPREC_FWS', history_str='obs_fws(wsp)'),
                MyTestData(2, '\n\t', 0),
                MyTestData(3, ' ', 1, codes='DEPREC_FWS', history_str='obs_fws(wsp)'),
                MyTestData(4, '\r\n\t', 3, codes='DEPREC_FWS', history_str='obs_fws(crlf, wsp)'),
                MyTestData(5, '\r\n', 0, codes='ERR_FWS_CRLF_END', error=True, history_str=''),
            ]
        )
        self.run_test_data(td)

    def test_quoted_string(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='quoted_string',
            tests=[

                # normal qs
                MyTestData(1, '"test"', 6, codes='RFC5321_QUOTED_STRING',
                           history_str='quoted_string(double_quote, qcontent(qtext), double_quote)'),

                # qs with more words
                MyTestData(2, '"this is a test"', 16, codes=['RFC5321_QUOTED_STRING'],
                           history_str='quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)'),

                # qs with enclosed comment
                MyTestData(3, '"this (is a) test"', 18, codes=['RFC5321_QUOTED_STRING'],
                           history_str='quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)'),


                # qs with fail initially
                MyTestData(4, ' "this is a test"', 17, codes=('RFC5321_QUOTED_STRING', 'CFWS_FWS'),
                           history_str='quoted_string(cfws(fws(wsp)), double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)'),
                MyTestData(5, ' (this is a comment) "this is a test"', 37, codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS'),
                           history_str='quoted_string(cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis), fws(wsp)), double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)'),
                MyTestData(6, 'blah"this is a test"', 0, history_str=''),

                # Qs with cfws after
                MyTestData(8, '"this is a test" (this is a comment)', 36, codes=['RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS'],
                           history_str='quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote, cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)))'),

                # qs with cfws both
                MyTestData(9, ' (this is a pre comment) "this is a test" (this is a post comment)', 66,
                           codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS'),
                           history_str='quoted_string(cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis), fws(wsp)), double_quote, qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote, cfws(fws(wsp), comment(open_parenthesis, ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), fws(wsp), ccontent(ctext), close_parenthesis)))'),

                # unclosed qs
                MyTestData(10, '"this is a test', 0,
                           codes='ERR_UNCLOSED_QUOTED_STR', error=True, history_str=''),

                # fws in qs
                MyTestData(12, '" this\tis a test"', 17, codes='RFC5321_QUOTED_STRING',
                           history_str='quoted_string(double_quote, fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)'),

                # mult fws in qs
                MyTestData(13, '(  this is a test)', 0, history_str=''),
                MyTestData(14, '(this is a  test)', 0, history_str=''),

                # quoted pair in qs
                MyTestData(15, '"this \\r\\nis a test"', 20, codes='RFC5321_QUOTED_STRING',
                           history_str='quoted_string(double_quote, qcontent(qtext), fws(wsp), qcontent(quoted_pair(back_slash, vchar_wsp)), qcontent(quoted_pair(back_slash, vchar_wsp)), qcontent(qtext), fws(wsp), qcontent(qtext), fws(wsp), qcontent(qtext), double_quote)'),
                MyTestData(16, '"test"of a test', 6, codes='RFC5321_QUOTED_STRING',
                           history_str='quoted_string(double_quote, qcontent(qtext), double_quote)'),

            ]
        )
        self.run_test_data(td)

    def test_qcontent(self):
        FF = make_char_str(12)
        td = MyTestDefs(
            limit_to=-1,
            method_name='qcontent',
            tests=[

                MyTestData(1, '\\', 0, codes='ERR_EXPECTING_QPAIR', error=True, history_str=''),
                MyTestData(2, '\\\t', 2, history_str='qcontent(quoted_pair(back_slash, vchar_wsp))'),
                MyTestData(3, '\\ ', 2, history_str='qcontent(quoted_pair(back_slash, vchar_wsp))'),
                MyTestData(4, '\\a', 2, history_str='qcontent(quoted_pair(back_slash, vchar_wsp))'),
                MyTestData(5, '\t', 0),

                # obs
                MyTestData(11, '\\\r', 2, codes='DEPREC_QP', history_str='qcontent(quoted_pair(back_slash, obs_qp))'),
                MyTestData(12, '\\\n', 2, codes='DEPREC_QP', history_str='qcontent(quoted_pair(back_slash, obs_qp))'),
                MyTestData(13, make_char_str('\\', 0), 2, codes='DEPREC_QP', history_str='qcontent(quoted_pair(back_slash, obs_qp))'),

                # qtext
                MyTestData(31, 'foobar', 6, history_str='qcontent(qtext)'),
                MyTestData(33, 'foobar ', 6, history_str='qcontent(qtext)'),
                MyTestData(34, ' foobar', 0),
                MyTestData(35, '"foobar', 0),
                MyTestData(36, 'foobar"', 6, history_str='qcontent(qtext)'),

                # obs qtext
                MyTestData(41, FF, 1, codes='DEPREC_QTEXT', history_str='qcontent(qtext(obs_qtext))'),

            ]
        )
        self.run_test_data(td)

    def test_quoted_pair(self):

        td = MyTestDefs(
            limit_to=-1,
            method_name='quoted_pair',
            tests=[
                MyTestData(1, '\\', 0, codes='ERR_EXPECTING_QPAIR', error=True, history_str=''),
                MyTestData(2, '\\\t', 2, history_str='quoted_pair(back_slash, vchar_wsp)'),
                MyTestData(3, '\\ ', 2, history_str='quoted_pair(back_slash, vchar_wsp)'),
                MyTestData(4, '\\a', 2, history_str='quoted_pair(back_slash, vchar_wsp)'),
                MyTestData(5, '\t', 0),

                # obs
                MyTestData(11, '\\\r', 2, codes='DEPREC_QP', history_str='quoted_pair(back_slash, obs_qp)'),
                MyTestData(12, '\\\n', 2, codes='DEPREC_QP', history_str='quoted_pair(back_slash, obs_qp)'),
                MyTestData(13, make_char_str('\\', 0), 2, codes='DEPREC_QP', history_str='quoted_pair(back_slash, obs_qp)'),

                # MyTestData(21,  make_char_str('\\', 91), 0, not_codes='ERR_EXPECTING_QPAIR'),

            ]
        )
        self.run_test_data(td)

    def test_crlf(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='crlf',
            tests=[
                MyTestData(1, '\r', 0, codes='ERR_CR_NO_LF', error=True, history_str=''),
                MyTestData(2, '\n', 0, history_str=''),
                MyTestData(3, '\rblaj', 0, codes='ERR_CR_NO_LF', error=True, history_str=''),
                MyTestData(4, '\r\n\r\n', 0, codes='ERR_FWS_CRLF_X2', error=True, history_str=''),
                MyTestData(5, '\n\r', 0, history_str=''),
                MyTestData(5, '\r\n', 2, history_str='crlf'),
                MyTestData(5, 'blah', 0, history_str=''),
            ]
        )
        self.run_test_data(td)


class TestParseNames(unittest.TestCase):
    tep = EmailParser(trace_filter=9999, verbose=3)

    def test_parse_names(self):

        test_data = [
            # (1, 'address', 'local_part', 'domain_part', ['local comments'], ['domain_comments'], address_type),

            (100, 'dan@example.com', 'dan', 'example.com', 'dan@example.com', [], [], ISEMAIL_DOMAIN_TYPE.DNS),
            (101, '(comment1)dan@example.com', 'dan', 'example.com', 'dan@example.com', ['comment1'], [], ISEMAIL_DOMAIN_TYPE.DNS),
            (102, 'dan(comment2)@example.com', 'dan', 'example.com', 'dan@example.com', ['comment2'], [], ISEMAIL_DOMAIN_TYPE.DNS),
            (103, '(comment1)dan(comment2)@example.com', 'dan', 'example.com', 'dan@example.com', ['comment1', 'comment2'], [], ISEMAIL_DOMAIN_TYPE.DNS),

            (200, ' "dan"@example.com', 'dan', 'example.com', '"dan"@example.com', [], [], ISEMAIL_DOMAIN_TYPE.DNS),
            (201, '(comment1)" dan"@example.com', ' dan', 'example.com', '" dan"@example.com', ['comment1'], [], ISEMAIL_DOMAIN_TYPE.DNS),
            (202, '"dan"( comment2)@example.com', 'dan', 'example.com', '"dan"@example.com', [' comment2'], [], ISEMAIL_DOMAIN_TYPE.DNS),
            (203, '(comment1)"dan"(comment2)@example.com', 'dan', 'example.com', '"dan"@example.com', ['comment1', 'comment2'], [], ISEMAIL_DOMAIN_TYPE.DNS),

            (300, 'dan.strohl@example.com', 'dan.strohl', 'example.com', 'dan.strohl@example.com', [], [], True, False),
            (301, '(comment1)dan. (comment2)strohl@example.com', 'dan.strohl', 'example.com', 'dan.strohl@example.com', ['comment1', 'comment2'], [], ISEMAIL_DOMAIN_TYPE.DNS),
            (302, 'dan(comment1).(comment2)strohl@example.com', 'dan.strohl', 'example.com', 'dan.strohl@example.com', ['comment1', 'comment2'], [], ISEMAIL_DOMAIN_TYPE.DNS),
            (303, '(comment1)dan(comment2).strohl(comment3"hello")@example.com', 'dan.strohl', 'example.com', 'dan.strohl@example.com', ['comment1', 'comment2', 'comment3"hello"'], [], ISEMAIL_DOMAIN_TYPE.DNS),

            (304, 'dan@[example of a dot com]', 'dan', 'example of a dot com', 'dan@[example of a dot com]', [], [], ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT),
            (305, 'dan@(comment1)[test:example of a dot com](comment2)', 'dan', 'test:example of a dot com', 'dan@[test:example of a dot com]', [], ['comment1', 'comment2'], ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT),
            (306, 'dan@[http:example_of_a_dot_com]', 'dan', ['http', 'example_of_a_dot_com'], 'dan@[http:example_of_a_dot_com]', [], [], ISEMAIL_DOMAIN_TYPE.GENERAL_LIT),
            (307, 'dan@[1.1.1.1]', 'dan', '1.1.1.1', 'dan@[1.1.1.1]', [], [], ISEMAIL_DOMAIN_TYPE.IPv4),
            (308, 'dan@[ipv6:1:1:1:1:1:1:1:1]', 'dan', '1:1:1:1:1:1:1:1', 'dan@[ipv6:1:1:1:1:1:1:1:1]', [], [], ISEMAIL_DOMAIN_TYPE.IPv6),

            (400, 'dan@(comment1)example(comment2). (comment3)com', 'dan', 'example.com', 'dan@example.com', [], ['comment1', 'comment2', 'comment3'], ISEMAIL_DOMAIN_TYPE.OTHER_NON_DNS),
            ]

        LIMIT_TO = -1

        if LIMIT_TO != -1:
            with self.subTest('LIMITING TEST TO %s' % LIMIT_TO):
                self.fail('ALERT, this test is limited.')

        for test in test_data:
            test_name = '#%s - %s' % (test[0], test[1])
            with self.subTest(test_name):
                if LIMIT_TO == -1 or LIMIT_TO == test[0]:
                    tmp_res = self.tep(test[1])

                    with self.subTest(test_name + ' - local'):
                        self.assertEquals(tmp_res.local, test[2], full_ret_string(test[0], test[1], tmp_res))
                    with self.subTest(test_name + ' - domain'):
                        self.assertEquals(tmp_res.domain, test[3], full_ret_string(test[0], test[1], tmp_res))
                    with self.subTest(test_name + ' -  full'):
                        self.assertEquals(str(tmp_res), test[4], full_ret_string(test[0], test[1], tmp_res))
                    with self.subTest(test_name + ' - local_comments'):
                        self.assertCountEqual(tmp_res.local_comments, test[5], full_ret_string(test[0], test[1], tmp_res))
                    with self.subTest(test_name + ' - domain_comments'):
                        self.assertCountEqual(tmp_res.domain_comments, test[6], full_ret_string(test[0], test[1], tmp_res))
                    with self.subTest(test_name + ' - domain_type'):
                        self.assertEquals(tmp_res.domain_type, test[7], full_ret_string(test[0], test[1], tmp_res))


class TestDomainLookup(unittest.TestCase):

    def test_lookup(self):
        LL = ISEMAIL_DNS_LOOKUP_LEVELS
        DNS_RESP = ['DNSWARN_INVALID_TLD', 'DNSWARN_NO_RECORD', 'DNSWARN_NO_MX_RECORD', 'DNSWARN_COMM_ERROR']

        test_data = [
            # (num, domain_name, lookup_type, expected_return, raised_error, kwargs_dict)
            (1, 'dan@example.com', LL.NO_LOOKUP, ''),

            (100, 'dan@example.com', LL.TLD_MATCH, ''),
            (101, 'dan@example.foobar', LL.TLD_MATCH, 'DNSWARN_INVALID_TLD'),

            (201, 'dan@example.com', LL.ANY_RECORD, ''),
            (202, 'dan@example.foobar', LL.ANY_RECORD, 'DNSWARN_INVALID_TLD'),
            (203, 'dan@no_domain.example.com', LL.ANY_RECORD, 'DNSWARN_NO_RECORD'),

            (301, 'dan@iana.org', LL.MX_RECORD, ''),
            (302, 'dan@example.foobar', LL.MX_RECORD, 'DNSWARN_INVALID_TLD'),
            (303, 'dan@no_domain.example.com', LL.MX_RECORD, 'DNSWARN_NO_RECORD'),
            (304, 'dan@example.com', LL.MX_RECORD, 'DNSWARN_NO_MX_RECORD'),

            # comm error
            (601, 'dan@example.com', LL.ANY_RECORD, 'DNSWARN_COMM_ERROR', None, {'dns_servers': '127.0.0.1', 'dns_timeout': 1}),
            (602, 'dan@example.com', LL.ANY_RECORD, '', DNSTimeoutError, {'dns_servers': '127.0.0.1', 'dns_timeout': 1, 'raise_on_error': True}),

            # no tld list
            (701, 'dan@example.com', LL.TLD_MATCH, '', AttributeError, {'tld_list': []}),
            (702, 'dan@example.com', LL.ANY_RECORD, '', None, {'tld_list': []}),

            # manual TLD list
            (801, 'dan@example.foobar', LL.TLD_MATCH, '', None, {'tld_list': ['BLAH', 'FOOBAR']}),
            (802, 'dan@example.com', LL.TLD_MATCH, 'DNSWARN_INVALID_TLD', None, {'tld_list': ['BLAH', 'FOOBAR']}),

            # force server
            (901, 'dan@example.com', LL.ANY_RECORD, '', None, {'dns_servers': '8.8.8.8'}),

            # no dns names
            (1001, 'dan@[example.com]', LL.MX_RECORD, ''),
            (1003, 'dan@[1.2.3.4]', LL.MX_RECORD, ''),
            (1004, 'dan@[ipv6:1:1:1:1:1:1:1:1]', LL.MX_RECORD, ''),

        ]

        LIMIT_TO = -1

        if LIMIT_TO != -1:
            with self.subTest('LIMITING TEST TO %s' % LIMIT_TO):
                self.fail('ALERT, this test is limited.')

        for test in test_data:
            test_name = '#%s - %s' % (test[0], test[1])
            with self.subTest(test_name):
                if LIMIT_TO == -1 or LIMIT_TO == test[0]:
                    if len(test) > 5:
                        emv = EmailParser(verbose=2, **test[5])
                    else:
                        emv = EmailParser(verbose=2)

                    if len(test) > 4 and test[4] is not None:
                        with self.subTest(test_name + ' - Exception'):
                            with self.assertRaises(test[4]):
                                tmp_ret = emv(test[1], dns_lookup_level=test[2])
                    else:
                        tmp_ret = emv(test[1], dns_lookup_level=test[2])
                        for resp in DNS_RESP:
                            with self.subTest(test_name + ' - response - ' + resp):
                                tmp_check = resp in tmp_ret
                                if resp == test[3]:
                                    tmp_msg = full_ret_string(test[0], test[1], tmp_ret,
                                                              '%s IS NOT in the responses' % resp)
                                    self.assertTrue(tmp_check, msg=tmp_msg)
                                else:
                                    tmp_msg = full_ret_string(test[0], test[1], tmp_ret,
                                                              '%s IS in the responses (and should not be' % resp)
                                    self.assertFalse(tmp_check, msg=tmp_msg)


