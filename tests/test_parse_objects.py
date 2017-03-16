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

    """
    def run_tests(self, test_data, method_name):
        for test in test_data:

            if len(test) == 4:
                position = test[3]
            else:
                position = 0

            if self.RUNTEST == -1 or self.RUNTEST == test[0]:
                with self.subTest('#%s: %s @ pos: %s' % (test[0], test[1], position)):
                    eph = EmailParser(test[1])
                    tmp_meth = getattr(eph, method_name)
                    test_ret = tmp_meth(position=position)
                    self.assertEqual(test_ret, test[2])

                    if len(test) == 5:
                        self.assertEquals(eph.test_text, test[4])
                    else:
                        self.assertEquals(eph.test_text, "")

    def run_complex_tests(self, test_data, method_name):
        for test in test_data:
            if self.RUNTEST == -1 or self.RUNTEST == test['index']:
                with self.subTest('#%s' % test['index']):
                    eph = EmailParser(test['string_in'])
                    tmp_meth = getattr(eph, method_name)
                    test_ret = tmp_meth(**test['kwargs'])
                    self.assertEqual(test_ret, test['result'])

    """
    def run_test_data(self, test_defs: MyTestDefs):
        if test_defs.limit_to != -1:
            with self.subTest('LIMITING TEST %s to %s' % (test_defs.method_name, test_defs.limit_to)):
                self.fail('ALERT, this test is limited.')
        
        for test in test_defs:

            if test_defs.limit_to == -1 or test_defs.limit_to == test.test_num:
                with self.subTest(test.test_name + ' Base'):
                    eph = EmailParser(test.string_in, **test_defs.kwargs, verbose=3)
                    tmp_meth = getattr(eph, test.method_name)
                    test_ret = eph.run_method_test(tmp_meth, position=test.position, **test.kwargs)

                    if test_defs.football:
                        self.assertEquals(test_ret.length, test.result_length, msg=eph.trace_str)
                    else:
                        self.assertEqual(test_ret, test.result_length, msg=eph.trace_str)

                    if test_defs.football:

                        with self.subTest(test.test_name + ' Error fail'):
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
                            with self.subTest(test.test_name + 'should have all codes'):
                                self.assertCountEqual(test.codes, list(test_ret.diags()), msg=eph.trace_str)

                        if test.no_codes:
                            with self.subTest(test.test_name + 'should not codes'):
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
        tmp_ret = emp.simple_str(0, '1234567890')
        self.assertEqual(tmp_ret.l, 3)

        tmp_ret = emp.simple_str(0, '21', max_count=2)
        self.assertEqual(tmp_ret.l, 2)

        tmp_ret = emp.simple_str(0, '123456', min_count=4)
        self.assertEqual(tmp_ret.l, 0)

        tmp_ret = emp.simple_str(3, 'abcdefg')
        self.assertEqual(tmp_ret.l, 3)

        tmp_ret = emp.simple_str(3, 'abgth', max_count=2)
        self.assertEqual(tmp_ret.l, 2)

        tmp_ret = emp.simple_str(3, 'abcdef', min_count=4)
        self.assertEqual(tmp_ret.l, 0)
    """
    def test_ordered_str(self):
        test_data = [
            # defaults
            {
                'index': 1,
                'string_in': 'abcdefg',
                'kwargs': {
                    'parse_for': 'abc',
                    'position': None,
                    'min_count': 1,
                    'max_count': 1,
                },
                'result': 3
            },
            {
                'index'    : 2,
                'string_in': 'abcabcabc',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'position': None,
                    'min_count': 1,
                    'max_count': 1,
                },
                'result'   : 3
            },
            {
                'index'    : 3,
                'string_in': 'cbacbb',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'position': None,
                    'min_count': 1,
                    'max_count': 1,
                },
                'result'   : 0
            },
            # has Min / max
            {
                'index'    : 4,
                'string_in': 'abcdefg',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'position': None,
                    'min_count': 2,
                    'max_count': 2,
                },
                'result'   : 0
            },
            {
                'index'    : 5,
                'string_in': 'abcabcabc',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'position': None,
                    'min_count': 2,
                    'max_count': 3,
                },
                'result'   : 9
            },
            {
                'index'    : 6,
                'string_in': 'abcabcdef',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'position': None,
                    'min_count': 2,
                    'max_count': 2,
                },
                'result'   : 6
            },

            {
                'index'    : 7,
                'string_in': 'abcabcabc',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'position': None,
                    'min_count': 1,
                    'max_count': 2,
                },
                'result'   : 6
            },
            # has position

            {
                'index'    : 8,
                'string_in': 'abcabcabc',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'position': 3,
                    'min_count': 1,
                    'max_count': 1,
                },
                'result'   : 3
            },
            {
                'index'    : 9,
                'string_in': 'abdcdr',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'position': 2,
                    'min_count': 1,
                    'max_count': 1,
                },
                'result'   : 0
            },
        ]

        # self.RUNTEST = 4
        self.run_complex_tests(test_data, 'ordered_str')
        with self.assertRaises(AttributeError):
            eph = EmailParser('abcd')
            test = eph.ordered_str('abc', min_count=10, max_count=2)
    """
    """
        def test_parse_str(self):
        test_data = [
            # base
            {
                'index': 1,
                'string_in': 'abcdefg',
                'kwargs': {
                    'parse_for': 'abc',
                    'prefix': None,
                    'postfix': None,
                },
                'result': 3
            },
            {
                'index'    : 2,
                'string_in': 'abcabcabc',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix': None,
                    'postfix': None,
                },
                'result'   : 9
            },
            {
                'index'    : 3,
                'string_in': 'cbaxxx',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix': None,
                    'postfix': None,
                },
                'result'   : 3
            },
            {
                'index': 4,
                'string_in': 'abcdefg',
                'kwargs': {
                    'parse_for': P4Ord('abc'),
                    'prefix': None,
                    'postfix': None,
                },
                'result': 3
            },
            # prefix
            {
                'index'    : 11,
                'string_in': '!abcdefg!',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix': '!',
                    'postfix': None,
                },
                'result'   : 4
            },
            {
                'index'    : 12,
                'string_in': 'abcabcabc',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix': P4Char('"', optional=True),
                    'postfix': None,
                },
                'result'   : 9
            },
            {
                'index'    : 13,
                'string_in': 'abcabcdef',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix': '"',
                    'postfix': None,
                },
                'result'   : 0
            },
            {
                'index'    : 14,
                'string_in': '"abcabcdef',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix'   : P4Char('"', include_str=False),
                    'postfix'  : None,
                },
                'result'   : 6
            },

            # has postfix

            {
                'index'    : 21,
                'string_in': 'abc!defg!',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix'   : None,
                    'postfix'  : '!',
                },
                'result'   : 4
            },
            {
                'index'    : 22,
                'string_in': 'abcabcabc',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix'   : None,
                    'postfix'  : P4Char('"', optional=True),
                },
                'result'   : 9
            },
            {
                'index'    : 23,
                'string_in': 'abcabcdef',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix'   : None,
                    'postfix'  : '"',
                },
                'result'   : 0
            },
            {
                'index'    : 24,
                'string_in': 'abcabc"def',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'postfix'   : P4Char('"', include_str=False),
                    'prefix'  : None,
                },
                'result'   : 6
            },

            # has pre-post

            {
                'index'    : 31,
                'string_in': '!defg!dde',
                'kwargs'   : {
                    'parse_for': 'defg',
                    'prefix'   : '!',
                    'postfix'  : '!',
                },
                'result'   : 6
            },
            {
                'index'    : 32,
                'string_in': 'abcabcabc',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix'   : P4Char('"', optional=True),
                    'postfix'  : P4Char('"', optional=True),
                },
                'result'   : 9
            },
            {
                'index'    : 33,
                'string_in': '"abcabcdef',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix'   : '"',
                    'postfix'  : '"',
                },
                'result'   : 0
            },
            {
                'index'    : 34,
                'string_in': 'abcabc"def',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'prefix'   : '"',
                    'postfix'  : '"',
                },
                'result'   : 0
            },
            {
                'index'    : 35,
                'string_in': '"abcabc"def',
                'kwargs'   : {
                    'parse_for': 'abc',
                    'postfix'  : P4Char('"', include_str=False),
                    'prefix'   : P4Char('"', include_str=False),
                },
                'result'   : 6
            },

        ]

        # self.RUNTEST = 11
        self.run_complex_tests(test_data, 'parse')
        with self.assertRaises(AttributeError):
            eph = EmailParser('abcd')
            test = eph.ordered_str('abc', min_count=10, max_count=2)

    """
    """

    def test_address_spec(self):
        self.fail()

    def test_local_part(self):
        self.fail()

    def test_dot_atom(self):
        self.fail()

    """
    def test_dot_atom_text(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='dot_atom_text',
            tests=[
                MyTestData(1, 'abc.def', 7),
                MyTestData(2, '.abc.def', 0),
                MyTestData(3, 'abc.def.', 7),
                MyTestData(4, 'abc.def.ghi(blah.blah)', 11),
                MyTestData(5, 'abc.def"ghu".jkl', 7)
            ]
        )
        self.run_test_data(td)


    """"
    def test_obs_local_part(self):
        self.fail()

    def test_word(self):
        self.fail()

    def test_atom(self):
        self.fail()

    def test_domain(self):
        self.fail()

    def test_domain_addr(self):
        self.fail()

    def test_sub_domain(self):
        self.fail()

    def test_let_str(self):
        self.fail()

    def test_domain_literal(self):
        self.fail()

    def test_dtext(self):
        self.fail()

    def test_obs_dtext(self):
        self.fail()

    def test_obs_domain(self):
        self.fail()

    def test_address_literal(self):
        self.fail()

    def test_general_address_literal(self):
        self.fail()

    def test_standardized_tag(self):
        self.fail()

    """
    def test_ldh_str(self):

        td = MyTestDefs(
            limit_to=-1,
            method_name='ldh_str',
            tests=[
                MyTestData(1, 'abc-123', 7),
                MyTestData(2, 'abcdef-', 6),
                MyTestData(3, 'abc.def.', 3),
                MyTestData(4, 'abc.def.ghi(blah.blah)', 4, position=12),
            ]
        )
        self.run_test_data(td)

    """
    def test_ipv4_address_literal(self):
        self.fail()

    """
    def test_snum(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='ldh_str',
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
            ]
        )
        self.run_test_data(td)


    """
    def test_ipv6_address_literal(self):
        self.fail()

    def test_ipv6_addr(self):
        self.fail()

    def test_ipv6_hex(self):
        self.fail()

    def test_ipv6_full(self):
        self.fail()

    def test_ipv6_comp(self):
        self.fail()

    def test_ipv6v4_full(self):
        self.fail()

    def test_ipv6v4_comp(self):
        self.fail()

    """

    def test_cfws(self):
        FF = make_char_str(12)
        td = MyTestDefs(
            limit_to=-1,
            method_name='cfws',
            tests=[

                # normal comment
                MyTestData(1, '(test)', 6, codes='CFWS_COMMENT'),

                # fws before
                MyTestData(2, ' (test)', 7, codes='CFWS_COMMENT'),

                # fws after
                MyTestData(3, '(test) ', 7, codes='CFWS_COMMENT'),

                # fws both
                MyTestData(4, ' (test) ', 8, codes='CFWS_COMMENT'),

                # fws only
                MyTestData(5, ' ', 1, not_codes='CFWS_COMMENT'),

                # mult fws before
                MyTestData(6, '  (test)', 0, not_codes='CFWS_COMMENT'),

                # mult fws after
                MyTestData(7, '(test)  ', 7, codes='CFWS_COMMENT'),

                # fws with comment error
                # comment around @
                MyTestData(8, ' (this is @ test)', 0, codes='DEPREC_CFWS_NEAR_AT'),

                # unclosed comment
                MyTestData(9, ' (this is a test', 0, codes='ERR_UNCLOSED_COMMENT', ),
                MyTestData(10, ' (this (is a test', 0, codes='ERR_UNCLOSED_COMMENT'),

            ]
        )
        self.run_test_data(td)




    def test_comment(self):
        FF = make_char_str(12)
        td = MyTestDefs(
            limit_to=-1,
            method_name='comment',
            trace_filter=2,
            tests=[

                # normal comment
                MyTestData(1, '(test)', 6, codes=['CFWS_COMMENT']),

                # comment with more words
                MyTestData(2, '(this is a test)', 16, codes=['CFWS_COMMENT', 'CFWS_FWS']),

                # comment with enclosed comment
                MyTestData(3, '(this (is a) test)', 18, codes=['CFWS_COMMENT', 'CFWS_FWS']),

                # comment around @
                MyTestData(4, '(this is @ test)', 0, codes=['DEPREC_CFWS_NEAR_AT', 'CFWS_FWS']),

                # unclosed comment
                MyTestData(5, '(this is a test', 0, codes=['ERR_UNCLOSED_COMMENT', 'CFWS_FWS'], error=True),
                MyTestData(6, '(this (is a test', 0, codes=['ERR_UNCLOSED_COMMENT', 'CFWS_FWS'], error=True),

                # fws in comment
                MyTestData(7, '( this is a test)', 17, codes=['CFWS_COMMENT', 'CFWS_FWS']),
                MyTestData(8, '( this\tis a test)', 17, codes=['CFWS_COMMENT', 'CFWS_FWS']),

                # mult fws in comment
                MyTestData(9, '( \r\n \r\n this is a test)', 0, codes=['ERR_MULT_FWS_IN_COMMENT', 'CFWS_FWS', 'DEPREC_FWS'], error=True),
                MyTestData(10, '(this is a \r\n  test)', 0, codes=['ERR_MULT_FWS_IN_COMMENT', 'CFWS_FWS'], error=True),

                # quoted pair in comment
                MyTestData(11, '(this \\r\\nis a test)', 20, codes=['CFWS_COMMENT', 'CFWS_FWS']),

            ]
        )
        self.run_test_data(td)
    """
    def test_ccontent(self):
        self.fail()
    """

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

    """
    def test_obs_ctext(self):
        self.fail()
    """


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


    """
    def test_specials(self):
        self.fail()
    """

    def test_quoted_string(self):
        td = MyTestDefs(
            limit_to=-1,
            method_name='quoted_string',
            tests=[

                # normal qs
                MyTestData(1, '"test"', 6, codes='RFC5321_QUOTED_STRING'),

                # qs with more words
                MyTestData(2, '"this is a test"', 16, codes='RFC5321_QUOTED_STRING'),

                # qs with enclosed comment
                MyTestData(3, '"this (is a) test"', 18, codes='RFC5321_QUOTED_STRING'),


                # qs with fail initially
                MyTestData(4, ' "this is a test"', 17, codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT')),
                MyTestData(5, ' (this is a comment) "this is a test"', 37, codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT')),
                MyTestData(6, 'blah"this is a test"', 0, not_codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT')),

                # Qs with cfws after
                MyTestData(8, '"this is a test" (this is a comment)', 16, codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT')),

                # qs with cfws both
                MyTestData(9, ' (this is a pre comment) "this is a test" (this is a post comment)', 66,
                           codes=('RFC5321_QUOTED_STRING', 'CFWS_COMMENT')),

                # unclosed qs
                MyTestData(10, '"this is a test', 0, not_codes='RFC5321_QUOTED_STRING',
                           codes='ERR_UNCLOSED_QUOTED_STR'),

                # fws in qs
                MyTestData(12, '" this\tis a test"', 17, codes='RFC5321_QUOTED_STRING'),

                # mult fws in qs
                MyTestData(13, '(  this is a test)', 0, not_codes='ERR_MULT_FWS_IN_QS'),
                MyTestData(14, '(this is a  test)', 0, not_codes='ERR_MULT_FWS_IN_QS'),

                # quoted pair in qs
                MyTestData(15, '"this \\r\\nis a test"', 20, codes='RFC5321_QUOTED_STRING'),

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
