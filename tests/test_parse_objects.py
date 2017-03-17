import unittest
from parse_objects import EmailParser, make_char_str


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
    def __init__(self, method_name, football=True, tests=None, limit_to=-1, **kwargs):
        self.method_name = method_name
        self.football = football
        self.kwargs = kwargs
        self.limit_to = limit_to
        if tests is None:            
            self.tests = []
        else:
            self.tests = tests
        
        for t in self.tests:
            t.method_name = method_name

    def __iter__(self):
        for t in self.tests:
            yield t


class MyTestData(object):
    def __init__(self, 
                 test_num, 
                 string_in, 
                 result_length, 
                 position=0, 
                 # codes=None,
                 # not_codes=None,
                 codes=None,
                 error=False,
                 **kwargs):
        self.method_name = ''        
        self.test_num = test_num
        self.string_in = string_in
        self.result_length = result_length
        self.position = position
        self.kwargs = kwargs
        self.error = error
        if codes is None:
            self.no_codes = True
        else:
            self.no_codes = False

        """
        if has_code is not None:
            if isinstance(has_code, str):
                self.has_code = [has_code]
            else:
                self.has_code = has_code
        else:
            self.has_code = []

        if not_has_code is not None:
            if isinstance(not_has_code, str):
                self.not_has_code = [not_has_code]
            else:
                self.not_has_code = not_has_code
        else:
            self.not_has_code = []
        """
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

class TestEmailParser(unittest.TestCase):
    RUNTEST = -1

    def setUp(self):
        self.RUNTEST = -1

    def run_test_data(self, test_defs: MyTestDefs):
        if test_defs.limit_to != -1:
            with self.subTest('LIMITING TEST %s to %s' % (test_defs.method_name, test_defs.limit_to)):
                self.fail('ALERT, this test is limited.')
        
        for test in test_defs:

            if test_defs.limit_to == -1 or test_defs.limit_to == test.test_num:
                with self.subTest(test.test_name + ' incorrect length'):
                    eph = EmailParser(test.string_in, **test_defs.kwargs, verbose=3)
                    tmp_meth = getattr(eph, test.method_name)
                    test_ret = eph.run_method_test(tmp_meth, position=test.position, **test.kwargs)

                    if test_defs.football:
                        self.assertEquals(test_ret.length, test.result_length, msg=eph.trace_str)
                    else:
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

    # ********************************************************
    #  PARSING TESTS
    # ********************************************************

    def test_address_spec(self):
        self.fail()
        td = MyTestDefs(
            limit_to=-1,
            method_name='address_spec',
            tests=[
                MyTestData(1, '', 7),
            ]
        )
        self.run_test_data(td)

    def test_local_part(self):
        self.fail()
        td = MyTestDefs(
            limit_to=-1,
            method_name='local_part',
            tests=[
                MyTestData(1, '', 7),
            ]
        )
        self.run_test_data(td)

    def test_domain(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='domain',
            tests=[
                # dot atom
                MyTestData(1, 'abc.def', 7),
                MyTestData(2, 'abc', 7),
                MyTestData(3, '123.456', 7),
                MyTestData(4, '#$%.#$%', 7),
                MyTestData(5, 'abc.123.456', 7),

                MyTestData(6, '(coment) abc.def', 7),
                MyTestData(7, 'abc (comment)', 7),
                MyTestData(8, '\r\n123.456 ', 7),
                MyTestData(9, '\r\n#$%.#$% (comment)', 7),
                MyTestData(10, '\t\r\nabc.123.456 \t', 7),

                MyTestData(11, '.abc.def', 0),
                MyTestData(12, 'abc.', 0),
                MyTestData(13, '123..456', 0),
                MyTestData(14, '#$%.#$%..', 0),
                MyTestData(15, ',abc.123.456', 0),
                MyTestData(16, '   .abc.def', 0),

                # quoted string
                MyTestData(101, 'word', 4),
                MyTestData(102, 'word.and.another.word', 21),
                MyTestData(103, '"this is a word"', 16),
                MyTestData(104, '"this is (a comment) . inside a quote".test', 36),
                MyTestData(105, 'test."this is (a comment inside a quote"', 0),
                MyTestData(106, 'test."this is (a comment) inside a quote.test.test', 0),

                MyTestData(111, '.word', 0),
                MyTestData(112, '..word and another word', 0),
                MyTestData(113, '"this is a word"..', 0),
                MyTestData(114, '"this is (a comment) inside a quote".', 0),

                # ***** obs_local_part

                # normal qs
                MyTestData(201, '"test"', 6, codes='RFC5321_QUOTED_STRING'),

                # qs with more words
                MyTestData(202, '"this is a test"', 16, codes=['RFC5321_QUOTED_STRING']),

                # qs with enclosed comment
                MyTestData(203, '"this (is a) test"', 18, codes=['RFC5321_QUOTED_STRING']),

                # qs with fail initially
                MyTestData(204, ' "this is a test"', 17, codes=('RFC5321_QUOTED_STRING', 'CFWS_FWS')),
                MyTestData(205, ' (this is a comment) "this is a test"', 37,
                           codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS')),
                MyTestData(206, 'blah"this is a test"', 0, ),

                # Qs with cfws after
                MyTestData(208, '"this is a test" (this is a comment)', 36,
                           codes=['RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS']),

                # qs with cfws both
                MyTestData(209, ' (this is a pre comment) "this is a test" (this is a post comment)', 66,
                           codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS')),

                # unclosed qs
                MyTestData(210, '"this is a test', 0,
                           codes='ERR_UNCLOSED_QUOTED_STR', error=True),

                # fws in qs
                MyTestData(212, '" this\tis a test"', 17, codes='RFC5321_QUOTED_STRING'),

                # mult fws in qs
                MyTestData(213, '(  this is a test)', 0),
                MyTestData(214, '(this is a  test)', 0),

                # quoted pair in qs
                MyTestData(215, '"this \\r\\nis a test"', 20, codes='RFC5321_QUOTED_STRING'),
                MyTestData(216, '"test"of a test', 6, codes='RFC5321_QUOTED_STRING'),

            ]
        )
        self.run_test_data(td)

    def test_dot_atom(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='dot_atom',
            tests=[
                MyTestData(1, 'abc.def', 7),
                MyTestData(2, 'abc', 7),
                MyTestData(3, '123.456', 7),
                MyTestData(4, '#$%.#$%', 7),
                MyTestData(5, 'abc.123.456', 7),

                MyTestData(6, '(coment) abc.def', 7),
                MyTestData(7, 'abc (comment)', 7),
                MyTestData(8, '\r\n123.456 ', 7),
                MyTestData(9, '\r\n#$%.#$% (comment)', 7),
                MyTestData(10, '\t\r\nabc.123.456 \t', 7),

                MyTestData(11, '.abc.def', 0),
                MyTestData(12, 'abc.', 0),
                MyTestData(13, '123..456', 0),
                MyTestData(14, '#$%.#$%..', 0),
                MyTestData(15, ',abc.123.456', 0),
                MyTestData(16, '   .abc.def', 0),
            ]
        )
        self.run_test_data(td)


    def test_dot_atom_text(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='dot_atom_text',
            tests=[
                MyTestData(1, 'abc.def', 7),
                MyTestData(2, 'abc', 3),
                MyTestData(3, '123.456', 7),
                MyTestData(4, '#$%.#$%', 7),
                MyTestData(5, 'abc.123.456', 11),

                MyTestData(6, '.abc.def', 0),
                MyTestData(7, 'abc.', 3),
                MyTestData(8, '123..456', 3),
                MyTestData(9, '#$%.#$%..', 6),
                MyTestData(10, ',abc.123.456', 0),

            ]
        )
        self.run_test_data(td)


    def test_obs_local_part(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='obs_local_part',
            tests=[
                MyTestData(1, 'word', 4),
                MyTestData(2, 'word.and.another.word', 21),
                MyTestData(3, '"this is a word"', 16),
                MyTestData(4, '"this is (a comment) . inside a quote".test', 36),
                MyTestData(5, 'test."this is (a comment inside a quote"', 0),
                MyTestData(6, 'test."this is (a comment) inside a quote.test.test', 0),

                MyTestData(1, '.word', 0),
                MyTestData(2, '..word and another word', 0),
                MyTestData(3, '"this is a word"..', 0),
                MyTestData(4, '"this is (a comment) inside a quote".', 0),
            ]
        )
        self.run_test_data(td)

    def test_word(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='word',
            tests=[
                MyTestData(1, 'word', 4),
                MyTestData(2, 'word and another word', 5, codes=['CFWS_FWS']),
                MyTestData(3, '"this is a word"', 16, codes=['RFC5321_QUOTED_STRING']),
                MyTestData(4, '"this is (a comment) inside a quote"', 36, codes=['RFC5321_QUOTED_STRING']),
                MyTestData(5, '"this is (a comment inside a quote"', 35, codes=['RFC5321_QUOTED_STRING']),
                MyTestData(6, '"this is (a comment) inside a quote', 0, codes=['ERR_UNCLOSED_QUOTED_STR'], error=True),
            ]
        )
        self.run_test_data(td)

    def test_atom(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='atom',
            tests=[
                MyTestData(1, 'thisisanatom$%^', 15),
                MyTestData(2, '(this is a comment) atom (this is a comment)', 44, codes=['CFWS_FWS', 'CFWS_COMMENT']),
                MyTestData(3, '(this is a comment) atom (this is a comment', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True)

            ]
        )
        self.run_test_data(td)

    def test_domain_addr(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='domain_addr',
            tests=[
                MyTestData(1, 'ABCdef123.abcder', 16),
                MyTestData(2, 'abcdef-123.acac', 15),
                MyTestData(3, 'abcdef-.12345', 0),
                MyTestData(3, '-abcdef.abcdef-', 0),
                MyTestData(3, 'abcdef', 0, codes='RFC5321_TLD'),
                MyTestData(3, '1abcdef.abcdef', 14, codes='RFC5321_TLD_NUMERIC'),
            ]
        )
        self.run_test_data(td)

    def test_sub_domain(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='sub_domain',
            tests=[
                MyTestData(1, 'ABCdef123', 9),
                MyTestData(2, 'abcdef-123', 10),
                MyTestData(3, 'abcdef-', 0),
                MyTestData(4, '-abcdef', 0),
            ]
        )
        self.run_test_data(td)

    def test_let_str(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='let_str',
            tests=[
                MyTestData(1, 'ABCdef123', 9),
                MyTestData(2, 'abcdef-123', 10),
                MyTestData(3, 'abcdef-', 0),
                MyTestData(3, '-abcdef', 7),
            ]
        )
        self.run_test_data(td)

    def test_domain_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='domain_literal',
            tests=[
                MyTestData(1, '[test]', 4),
                MyTestData(2, '[\\rtest]', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(4, '[\r\nfoo][bar', 5, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(5, '"\r\nfoo[bar', 0),

                # no closing
                MyTestData(101, '[test', 0),
                MyTestData(102, '[foo[bar]', 0),

                # fws before
                MyTestData(103, '[\t\\rtest]', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(104, '[ foo-bar]', 3),
                MyTestData(105, '[\t\t\r\nfoo][bar', 5, codes='RFC5322_DOM_LIT_OBS_DTEXT'),

                # fws after
                MyTestData(106, '[\\rtest ]', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(107, '[foobar  ]', 3),
                MyTestData(108, '[\r\nfoo\t][bar', 5, codes='RFC5322_DOM_LIT_OBS_DTEXT'),

                # fws both
                MyTestData(109, '[ \\rtest ]', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(110, '[\tfoobar ]', 3),

                # cfws before
                MyTestData(200, '(This is a comment)[\\rtest]', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(201, '\t\t[foo[bar]', 3),
                MyTestData(202, ' \r\n [\r\nfoo][bar', 5, codes='RFC5322_DOM_LIT_OBS_DTEXT'),

                # cfws after
                MyTestData(203, '[\\rtest](this is a post comment)\r\n', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(204, '[foo[bar] \r\n ', 3),
                MyTestData(205, '[\r\nfoo] \t\t [bar', 5, codes='RFC5322_DOM_LIT_OBS_DTEXT'),

                # cfws both
                MyTestData(206, '(comment beore) [\\rtest] (and after)', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(207, ' [foo[bar] \t\t', 3),
                MyTestData(208, '\t[\r\nfoo] [bar', 5, codes='RFC5322_DOM_LIT_OBS_DTEXT'),

                # mixed

                MyTestData(302, '(comment before)[ \\rtest]', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(303, '(comment before)[foo[bar ] ', 3),
                MyTestData(304, '\t\t[ \r\nfoo](and after)\t[bar', 5, codes='RFC5322_DOM_LIT_OBS_DTEXT'),

            ]
        )
        self.run_test_data(td)

    def test_dtext(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='dtext',
            tests=[
                MyTestData(1, 'test', 4),
                MyTestData(2, '\\rtest', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(3, 'foo[bar', 3),
                MyTestData(4, '\r\nfoo[bar', 0),
                MyTestData(5, '"\r\nfoo[bar', 1, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
            ]
        )
        self.run_test_data(td)

    def test_obs_dtext(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='obs_dtext',
            tests=[
                MyTestData(1, 'test', 4, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(2, '\\rtest', 6, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(3, 'foo[bar', 3, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
                MyTestData(4, '\r\nfoo[bar', 0),
                MyTestData(5, '"\r\nfoo[bar', 1, codes='RFC5322_DOM_LIT_OBS_DTEXT'),
            ]
        )
        self.run_test_data(td)

    def test_obs_domain(self):
        self.fail()
        td = MyTestDefs(
            limit_to=-1,
            method_name='obs_domain',
            tests=[
                MyTestData(1, '', 7),
            ]
        )
        self.run_test_data(td)


    def test_address_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            trace_filter=2,
            method_name='address_literal',
            tests=[

                # ipv6 full  - PASS
                MyTestData(1, '[IPv6:0:0:0:0:0:0:0:0]', 22, codes=['RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(2, '[IPv6:1111:1111:1111:1111:1111:1111:1111:1111]', 46,
                           codes=['RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(3, '[IPv6:12ab:abcd:fedc:1212:0:00:000:0]', 37,
                           codes=['RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR']),

                # ipv6 full  - FAIL
                MyTestData(4, '[IPv6:0:0:0:0:0:0:hhy:0]', 24, codes='RFC5322_GENERAL_LITERAL'),
                MyTestData(5, '[IPv6::1111:1111:1111:1111:1111:1111:1111:1111]', 47, codes='RFC5322_GENERAL_LITERAL'),
                MyTestData(6, '[IPv6:12aba:1abcd:fedc:1212:0:00:000:0]', 39, codes='RFC5322_GENERAL_LITERAL'),

                MyTestData(101, '[IPv6:0::0:0:0:0:0]', 19, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(102, '[IPv6:0::0:0:0:0]', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(103, '[IPv6:0::0:0:0]', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(104, '[IPv6:0::0:0]', 13, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(105, '[IPv6:0::0]', 11, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(106, '[IPv6:0:0::0:0:0:0]', 19, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(107, '[IPv6:0:0::0:0:0]', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(108, '[IPv6:0:0::0:0]', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(109, '[IPv6:0:0::0]', 13, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(110, '[IPv6:0:0:0::0:0:0]', 19, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(111, '[IPv6:0:0:0::0:0]', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(112, '[IPv6:0:0:0::0]', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(113, '[IPv6:0:0:0:0::0:0]', 19, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(114, '[IPv6:0:0:0:0::0]', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(115, '[IPv6:0:0:0:0:0::0]', 19, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                # ipv6 comp - FAIL
                MyTestData(116, '[IPv6:0::0:0:0:0:0:0]', 21, codes='RFC5322_GENERAL_LITERAL'),
                MyTestData(117, '[IPv6:0:0:0:0::0:0:0:0]', 23, codes='RFC5322_GENERAL_LITERAL'),

                # ipv6-4 - PASS
                MyTestData(201, '[IPv6:0:0:0:0:0:0:1.1.1.1]', 26, codes=['RFC5322_IPV6_IPV4_ADDR', 'RFC5322_IPV6_ADDR']),

                # ipv6-4 - FAIL
                MyTestData(203, '[IPv6:0:0:0:0:0:1.1.1.1]', 24, codes='RFC5322_GENERAL_LITERAL'),
                MyTestData(205, '[IPv6:0:0:0:0:0:0:1.1.1]', 24, codes='RFC5322_GENERAL_LITERAL'),

                # ipv6-4 comp - PASS

                MyTestData(301, '[IPv6:0::0:0:0:1.1.1.1]', 23,
                           codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(302, '[IPv6:0::0:0:1.1.1.1]', 21, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(303, '[IPv6:0::0:1.1.1.1]', 19, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(304, '[IPv6:0:0::0:0:1.1.1.1]', 23,
                           codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(305, '[IPv6:0:0::0:1.1.1.1]', 21, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(306, '[IPv6:0:0:0::0:1.1.1.1]', 23,
                           codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                # ipv6-4 comp - FAIL
                MyTestData(307, '[IPv6:0:0:0::0:0:0:1.1.1.1]', 27, codes='RFC5322_GENERAL_LITERAL'),

                # ipv4 PASS / FAIL
                MyTestData(401, '[1.1.1.1]', 9, codes='RFC5322_IPV4_ADDR'),
                MyTestData(402, '[123.123.123.123]', 17, codes='RFC5322_IPV4_ADDR'),
                MyTestData(403, '[13.13.255.0]', 13, codes='RFC5322_IPV4_ADDR'),
                MyTestData(404, '[255.255.255.255]', 17, codes='RFC5322_IPV4_ADDR'),
                MyTestData(405, '[0.0.0.0.]', 0, codes='ERR_UNCLOSED_DOM_LIT', error=True),
                MyTestData(406, '[0.0.0.0]', 9, codes='RFC5322_IPV4_ADDR'),
                MyTestData(407, '[.0.0.0.0]', 0, codes='ERR_INVALID_ADDR_LITERAL', error=True),
                MyTestData(408, '[1.2.3]', 0, codes='ERR_INVALID_ADDR_LITERAL', error=True),
                MyTestData(409, '[300.2.1.1]', 0, codes='ERR_INVALID_ADDR_LITERAL', error=True),
                MyTestData(410, '[blah]', 0, codes='ERR_INVALID_ADDR_LITERAL', error=True),
                
                # general addr PASS/FAIL
                MyTestData(501, '[abcd:abcdeg]', 13, codes='RFC5322_GENERAL_LITERAL'),
                MyTestData(502, '[http:foobar]', 13, codes='RFC5322_GENERAL_LITERAL'),
                MyTestData(503, '[foobar]', 0, codes='ERR_INVALID_ADDR_LITERAL', error=True),
                MyTestData(504, '[blah:]', 0, codes='ERR_INVALID_ADDR_LITERAL', error=True),
                MyTestData(505, '[:snafu]', 0, codes='ERR_INVALID_ADDR_LITERAL', error=True),

                # Enclosure fail
                MyTestData(601, '[1.1.1.1', 0, codes='ERR_UNCLOSED_DOM_LIT', error=True),

                # no start enclosure fail
                MyTestData(602, '1.1.1.1]', 0),

                # data past enclosure
                MyTestData(603, '[1.1.1.1]foobar', 9, codes='RFC5322_IPV4_ADDR'),


            ]
        )
        self.run_test_data(td)

    def test_general_address_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='general_address_literal',
            tests=[
                MyTestData(1, 'abcd:abcdeg', 11, codes='RFC5322_GENERAL_LITERAL'),
                MyTestData(1, 'http:foobar', 11, codes='RFC5322_GENERAL_LITERAL'),
                MyTestData(2, 'foobar', 0),
                MyTestData(2, 'blah:', 0),
                MyTestData(2, ':snafu', 0),
            ]
        )
        self.run_test_data(td)

    def test_ldh_str(self):

        td = MyTestDefs(
            limit_to=-1,
            method_name='ldh_str',
            tests=[
                MyTestData(1, 'abc-123', 7),
                MyTestData(1, 'abc--123', 8),
                MyTestData(2, 'abcdef-', 6),
                MyTestData(2, 'abcdef--', 6),
                MyTestData(2, 'abcdef-4', 8),
                MyTestData(3, 'abc.def.', 3),
                MyTestData(4, 'abc.def.ghi(blah.blah)', 4, position=12),
            ]
        )
        self.run_test_data(td)

    def test_ipv4_address_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='ipv4_address_literal',
            tests=[
                MyTestData(1, '1.1.1.1', 7, codes='RFC5322_IPV4_ADDR'),
                MyTestData(2, '123.123.123.123', 15, codes='RFC5322_IPV4_ADDR'),
                MyTestData(3, '13.13.255.0', 11, codes='RFC5322_IPV4_ADDR'),
                MyTestData(4, '255.255.255.255', 15, codes='RFC5322_IPV4_ADDR'),
                MyTestData(5, '0.0.0.0.', 7, codes='RFC5322_IPV4_ADDR'),
                MyTestData(6, '0.0.0.0', 7, codes='RFC5322_IPV4_ADDR'),
                MyTestData(7, '.0.0.0.0',0),
                MyTestData(8, '1.2.3', 0),
                MyTestData(9, '300.2.1.1', 0),
                MyTestData(10, 'blah', 0),
            ]
        )
        self.run_test_data(td)

    def test_snum(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='snum',
            tests=[
                MyTestData(1, '1', 1),
                MyTestData(2, '12', 2),
                MyTestData(3, '133', 3),
                MyTestData(4, '255', 3),
                MyTestData(5, '299', 0),
                MyTestData(6, '099', 3),
                MyTestData(7, '009', 3),
                MyTestData(8, '0093', 3),
                MyTestData(9, '5057', 0),
                MyTestData(10, '02', 2),
                MyTestData(7, '000.', 3),
                MyTestData(7, '0av', 1),
            ]
        )
        self.run_test_data(td)

    def test_ipv6_address_literal(self):
        td = MyTestDefs(
            limit_to=-1,
            trace_filter=2,
            method_name='ipv6_address_literal',
            tests=[

                # ipv6 full  - PASS
                MyTestData(1, 'IPv6:0:0:0:0:0:0:0:0', 20, codes=['RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(2, 'IPv6:1111:1111:1111:1111:1111:1111:1111:1111', 44, codes=['RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(3, 'IPv6:12ab:abcd:fedc:1212:0:00:000:0', 35, codes=['RFC5322_IPV6_FULL_ADDR', 'RFC5322_IPV6_ADDR']),

                # ipv6 full  - FAIL
                MyTestData(4, 'IPv6:0:0:0:0:0:0:hhy:0', 0),
                MyTestData(5, 'IPv6::1111:1111:1111:1111:1111:1111:1111:1111', 0),
                MyTestData(6, 'IPv6:12aba:1abcd:fedc:1212:0:00:000:0', 0),

                MyTestData(101, 'IPv6:0::0:0:0:0:0', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(102, 'IPv6:0::0:0:0:0', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(103, 'IPv6:0::0:0:0', 13, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(104, 'IPv6:0::0:0', 11, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(105, 'IPv6:0::0', 9, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(106, 'IPv6:0:0::0:0:0:0', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(107, 'IPv6:0:0::0:0:0', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(108, 'IPv6:0:0::0:0', 13, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(109, 'IPv6:0:0::0', 11, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(110, 'IPv6:0:0:0::0:0:0', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(111, 'IPv6:0:0:0::0:0', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(112, 'IPv6:0:0:0::0', 13, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(113, 'IPv6:0:0:0:0::0:0', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(114, 'IPv6:0:0:0:0::0', 15, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(115, 'IPv6:0:0:0:0:0::0', 17, codes=['RFC5322_IPV6_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                # ipv6 comp - FAIL
                MyTestData(116, 'IPv6:0::0:0:0:0:0:0', 0),
                MyTestData(117, 'IPv6:0:0:0:0::0:0:0:0', 0),

                # ipv6-4 - PASS
                MyTestData(201, 'IPv6:0:0:0:0:0:0:1.1.1.1', 24, codes=['RFC5322_IPV6_IPV4_ADDR', 'RFC5322_IPV6_ADDR']),

                # ipv6-4 - FAIL
                MyTestData(203, 'IPv6:0:0:0:0:0:1.1.1.1', 0),
                MyTestData(204, 'IPv6:0:0:0:0:0:0:1:1.1.1.1', 20, codes=['RFC5322_IPV6_FULL_ADDR','RFC5322_IPV6_ADDR']),
                MyTestData(205, 'IPv6:0:0:0:0:0:0:1.1.1', 0),

                # ipv6-4 comp - PASS

                MyTestData(301, 'IPv6:0::0:0:0:1.1.1.1', 21, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(302, 'IPv6:0::0:0:1.1.1.1', 19, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(303, 'IPv6:0::0:1.1.1.1', 17, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                MyTestData(304, 'IPv6:0:0::0:0:1.1.1.1', 21, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
                MyTestData(305, 'IPv6:0:0::0:1.1.1.1', 19, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),
        
                MyTestData(306, 'IPv6:0:0:0::0:1.1.1.1', 21, codes=['RFC5322_IPV6_IPV4_COMP_ADDR', 'RFC5322_IPV6_ADDR']),

                # ipv6-4 comp - FAIL
                MyTestData(307, 'IPv6:0:0:0::0:0:0:1.1.1.1', 0),
                ]
        )
        self.run_test_data(td)

    def test_ipv6_hex(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='ipv6_hex',
            tests=[
                MyTestData(1, '1', 1),
                MyTestData(2, '12', 2),
                MyTestData(3, '1234', 4),
                MyTestData(4, '12345', 4),
                MyTestData(5, 'ABCD', 4),
                MyTestData(6, 'abcd', 4),
                MyTestData(7, 'a1d4', 4),
                MyTestData(8, '00ab', 4),
                MyTestData(9, 'xx000', 0),
                MyTestData(10, 'yycx', 0),
            ]
        )
        self.run_test_data(td)

    def test_ipv6_full(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='ipv6_full',
            tests=[
                # ipv6 full  - PASS
                MyTestData(1, '0:0:0:0:0:0:0:0', 15, codes='RFC5322_IPV6_FULL_ADDR'),
                MyTestData(2, '1111:1111:1111:1111:1111:1111:1111:1111', 39, codes='RFC5322_IPV6_FULL_ADDR'),
                MyTestData(3, '12ab:abcd:fedc:1212:0:00:000:0', 30, codes='RFC5322_IPV6_FULL_ADDR'),

                # ipv6 full  - FAIL
                MyTestData(4, '0:0:0:0:0:0:hhy:0', 0),
                MyTestData(5, ':1111:1111:1111:1111:1111:1111:1111:1111', 0),
                MyTestData(6, '12aba:1abcd:fedc:1212:0:00:000:0', 0),
            ]
        )
        self.run_test_data(td)

    def test_ipv6_comp(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='ipv6_comp',
            tests=[
                MyTestData(1, '0::0:0:0:0:0', 12, codes='RFC5322_IPV6_COMP_ADDR'),
                MyTestData(2, '0::0:0:0:0', 10, codes='RFC5322_IPV6_COMP_ADDR'),
                MyTestData(3, '0::0:0:0', 8, codes='RFC5322_IPV6_COMP_ADDR'),
                MyTestData(4, '0::0:0', 6, codes='RFC5322_IPV6_COMP_ADDR'),
                MyTestData(5, '0::0', 4, codes='RFC5322_IPV6_COMP_ADDR'),


                MyTestData(6, '0:0::0:0:0:0', 12, codes='RFC5322_IPV6_COMP_ADDR'),
                MyTestData(7, '0:0::0:0:0', 10, codes='RFC5322_IPV6_COMP_ADDR'),
                MyTestData(8, '0:0::0:0', 8, codes='RFC5322_IPV6_COMP_ADDR'),
                MyTestData(9, '0:0::0', 6, codes='RFC5322_IPV6_COMP_ADDR'),


                MyTestData(10, '0:0:0::0:0:0', 12, codes='RFC5322_IPV6_COMP_ADDR'),
                MyTestData(11, '0:0:0::0:0', 10, codes='RFC5322_IPV6_COMP_ADDR'),
                MyTestData(12, '0:0:0::0', 8, codes='RFC5322_IPV6_COMP_ADDR'),


                MyTestData(13, '0:0:0:0::0:0', 12, codes='RFC5322_IPV6_COMP_ADDR'),
                MyTestData(14, '0:0:0:0::0', 10, codes='RFC5322_IPV6_COMP_ADDR'),

                MyTestData(15, '0:0:0:0:0::0', 12, codes='RFC5322_IPV6_COMP_ADDR'),

                # ipv6 comp - FAIL
                MyTestData(16, '0::0:0:0:0:0:0', 0),
                MyTestData(17, '0:0:0:0::0:0:0:0', 0),
            ]
        )
        self.run_test_data(td)

    def test_ipv6v4_full(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='ipv6v4_full',
            tests=[

                # ipv6-4 - PASS
                MyTestData(1, '0:0:0:0:0:0:1.1.1.1', 19, codes='RFC5322_IPV6_IPV4_ADDR'),

                # ipv6-4 - FAIL
                MyTestData(3, '0:0:0:0:0:1.1.1.1', 0),
                MyTestData(4, '0:0:0:0:0:0:1:1.1.1.1', 0),
                MyTestData(5, '0:0:0:0:0:0:1.1.1', 0),

                MyTestData(6, '0::0:0:0:1.1.1.1', 0),
                MyTestData(7, '0::0:0:1.1.1.1', 0),
                MyTestData(8, '0::0:1.1.1.1', 0),

                MyTestData(9, '0:0::0:0:1.1.1.1', 0),
                MyTestData(10, '0:0::0:1.1.1.1', 0),

                MyTestData(11, '0:0:0::0:1.1.1.1', 0),

            ]
            )
        self.run_test_data(td)

    def test_ipv6v4_comp(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='ipv6v4_comp',
            tests=[
                # ipv6-4 comp - PASS

                MyTestData(1, '0::0:0:0:1.1.1.1', 16, codes='RFC5322_IPV6_IPV4_COMP_ADDR'),
                MyTestData(2, '0::0:0:1.1.1.1', 14, codes='RFC5322_IPV6_IPV4_COMP_ADDR'),
                MyTestData(3, '0::0:1.1.1.1', 12, codes='RFC5322_IPV6_IPV4_COMP_ADDR'),

                MyTestData(4, '0:0::0:0:1.1.1.1', 16, codes='RFC5322_IPV6_IPV4_COMP_ADDR'),
                MyTestData(5, '0:0::0:1.1.1.1', 14, codes='RFC5322_IPV6_IPV4_COMP_ADDR'),

                MyTestData(6, '0:0:0::0:1.1.1.1', 16, codes='RFC5322_IPV6_IPV4_COMP_ADDR'),

                # ipv6-4 comp - FAIL
                MyTestData(7, '0:0:0::0:0:0:1.1.1.1', 0),
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
                MyTestData(1, '(test)', 6, codes='CFWS_COMMENT'),

                # fws before
                MyTestData(2, ' (test)', 7, codes=['CFWS_COMMENT', 'CFWS_FWS']),

                # fws after
                MyTestData(3, '(test) ', 7, codes=['CFWS_COMMENT', 'CFWS_FWS']),

                # fws both
                MyTestData(4, ' (test) ', 8, codes=['CFWS_COMMENT', 'CFWS_FWS']),

                # fws only
                MyTestData(5, ' ', 1, codes='CFWS_FWS'),

                # mult fws before
                MyTestData(6, '  (test)', 8, codes=['CFWS_COMMENT', 'CFWS_FWS']),

                # mult fws after
                MyTestData(7, '(test)  ', 8, codes=['CFWS_COMMENT', 'CFWS_FWS']),

                # fws with comment error
                # comment around @
                MyTestData(8, ' (this is @ test)', 17, codes=['DEPREC_CFWS_NEAR_AT', 'CFWS_COMMENT', 'CFWS_FWS']),

                # unclosed comment
                MyTestData(9, ' (this is a test', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True),
                MyTestData(10, ' (this (is a test', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True),

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
                MyTestData(1, '(test)', 6, codes=['CFWS_COMMENT']),

                # comment with more words
                MyTestData(2, '(this is a test)', 16, codes=['CFWS_COMMENT']),

                # comment with enclosed comment
                MyTestData(3, '(this (is a) test)', 18, codes=['CFWS_COMMENT']),

                # comment around @
                MyTestData(4, '(this is @ test)', 16, codes=['DEPREC_CFWS_NEAR_AT', 'CFWS_COMMENT']),

                # unclosed comment
                MyTestData(5, '(this is a test', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True),
                MyTestData(6, '(this (is a test', 0, codes=['ERR_UNCLOSED_COMMENT'], error=True),

                # fws in comment
                MyTestData(7, '( this is a test)', 17, codes=['CFWS_COMMENT']),
                MyTestData(8, '( this\tis a test)', 17, codes=['CFWS_COMMENT']),

                # mult fws in comment
                MyTestData(9, '( \r\n \r\n this is a test)', 0, codes=['ERR_MULT_FWS_IN_COMMENT', 'DEPREC_FWS'], error=True),
                MyTestData(10, '(this is a \r\n  test)', 0, codes=['ERR_MULT_FWS_IN_COMMENT'], error=True),

                # quoted pair in comment
                MyTestData(11, '(this \\r\\nis a test)', 20, codes=['CFWS_COMMENT']),

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
                MyTestData(31, 'foobar', 6),
                MyTestData(33, 'foobar ', 6),
                MyTestData(34, ' foobar', 0),
                MyTestData(35, '(foobar', 0),
                MyTestData(36, 'foobar)', 6),

                # obs qtext
                MyTestData(41, FF, 1, codes='DEPREC_CTEXT'),

            ]
        )
        self.run_test_data(td)

    def test_sub_fws(self):

        td = MyTestDefs(
            limit_to=-1,
            method_name='fws_sub',
            tests=[
                # good tries
                MyTestData(2, '\t\r\n\t', 4),
                MyTestData(3, '\t\t\t\r\n\t', 6),
                MyTestData(4, ' ', 1),

                # no final wsp
                MyTestData(1, '\t\r\n', 0),

                # only cr
                MyTestData(5, '\r\n', 0),

                # starts with cr
                MyTestData(6, '\r\n', 0),

                # multiple wsp after crlf
                MyTestData(7, '\t\r\n\t\t', 4),

                # multiple wsp
                MyTestData(8, '\t\t\t', 3),

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
                MyTestData(1, '\t', 1, codes='DEPREC_FWS'),
                MyTestData(2, '\n\t', 0),
                MyTestData(3, ' ', 1, codes='DEPREC_FWS'),
                MyTestData(4, '\r\n\t', 3, codes='DEPREC_FWS'),
                MyTestData(5, '\r\n', 0, codes='ERR_FWS_CRLF_END', error=True),
            ]
        )
        self.run_test_data(td)

    def test_quoted_string(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='quoted_string',
            tests=[

                # normal qs
                MyTestData(1, '"test"', 6, codes='RFC5321_QUOTED_STRING'),

                # qs with more words
                MyTestData(2, '"this is a test"', 16, codes=['RFC5321_QUOTED_STRING']),

                # qs with enclosed comment
                MyTestData(3, '"this (is a) test"', 18, codes=['RFC5321_QUOTED_STRING']),


                # qs with fail initially
                MyTestData(4, ' "this is a test"', 17, codes=('RFC5321_QUOTED_STRING', 'CFWS_FWS')),
                MyTestData(5, ' (this is a comment) "this is a test"', 37, codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS')),
                MyTestData(6, 'blah"this is a test"', 0,),

                # Qs with cfws after
                MyTestData(8, '"this is a test" (this is a comment)', 36, codes=['RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS']),

                # qs with cfws both
                MyTestData(9, ' (this is a pre comment) "this is a test" (this is a post comment)', 66,
                           codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT', 'CFWS_FWS')),

                # unclosed qs
                MyTestData(10, '"this is a test', 0,
                           codes='ERR_UNCLOSED_QUOTED_STR', error=True),

                # fws in qs
                MyTestData(12, '" this\tis a test"', 17, codes='RFC5321_QUOTED_STRING'),

                # mult fws in qs
                MyTestData(13, '(  this is a test)', 0),
                MyTestData(14, '(this is a  test)', 0),

                # quoted pair in qs
                MyTestData(15, '"this \\r\\nis a test"', 20, codes='RFC5321_QUOTED_STRING'),
                MyTestData(16, '"test"of a test', 6, codes='RFC5321_QUOTED_STRING'),

            ]
        )
        self.run_test_data(td)

    def test_qcontent(self):
        FF = make_char_str(12)
        td = MyTestDefs(
            limit_to=-1,
            method_name='qcontent',
            tests=[

                MyTestData(1, '\\', 0, codes='ERR_EXPECTING_QPAIR', error=True),
                MyTestData(2, '\\\t', 2),
                MyTestData(3, '\\ ', 2),
                MyTestData(4, '\\a', 2),
                MyTestData(5, '\t', 0),

                # obs
                MyTestData(11, '\\\r', 2, codes='DEPREC_QP'),
                MyTestData(12, '\\\n', 2, codes='DEPREC_QP'),
                MyTestData(13, make_char_str('\\', 0), 2, codes='DEPREC_QP'),

                # qtext
                MyTestData(31, 'foobar', 6),
                MyTestData(33, 'foobar ', 6),
                MyTestData(34, ' foobar', 0),
                MyTestData(35, '"foobar', 0),
                MyTestData(36, 'foobar"', 6),

                # obs qtext
                MyTestData(41, FF, 1, codes='DEPREC_QTEXT'),

            ]
        )
        self.run_test_data(td)

    def test_quoted_pair(self):

        td = MyTestDefs(
            limit_to=-1,
            method_name='quoted_pair',
            tests=[
                MyTestData(1, '\\', 0, codes='ERR_EXPECTING_QPAIR', error=True),
                MyTestData(2, '\\\t', 2),
                MyTestData(3, '\\ ', 2),
                MyTestData(4, '\\a', 2),
                MyTestData(5, '\t', 0),

                # obs
                MyTestData(11, '\\\r', 2, codes='DEPREC_QP'),
                MyTestData(12, '\\\n', 2, codes='DEPREC_QP'),
                MyTestData(13, make_char_str('\\', 0), 2, codes='DEPREC_QP'),

                # MyTestData(21,  make_char_str('\\', 91), 0, not_codes='ERR_EXPECTING_QPAIR'),

            ]
        )
        self.run_test_data(td)

    def test_crlf(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='crlf',
            tests=[
                MyTestData(1, '\r', 0, codes='ERR_CR_NO_LF', error=True),
                MyTestData(2, '\n', 0),
                MyTestData(3, '\rblaj', 0, codes='ERR_CR_NO_LF', error=True),
                MyTestData(4, '\r\n\r\n', 0, codes='ERR_FWS_CRLF_X2', error=True),
                MyTestData(5, '\n\r', 0),
                MyTestData(5, '\r\n', 2),
                MyTestData(5, 'blah', 0),
            ]
        )
        self.run_test_data(td)
