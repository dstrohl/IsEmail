import unittest
import json
from parse_results import ParseResultFootball, ParsingError
from meta_data import META_LOOKUP, ISEMAIL_RESULT_CODES, ISEMAIL_DNS_LOOKUP_LEVELS, ISEMAIL_DOMAIN_TYPE


class ParserFixture(object):
    def __init__(self, email_in='', **kwargs):
        self.email_in = email_in
        self.verbose = 3
        self.email_len = len(email_in)
        self.email_list = list(email_in)

        self.trace_str = 'This is a trace string'
        self.history_str = ''
        self.domain_type = None

        self._dns_servers = None
        self._dns_timeout = None
        self._raise_on_error = False
        self._tld_list = []
        self._dns_lookup_level = ISEMAIL_DNS_LOOKUP_LEVELS.NO_LOOKUP
        for key, item in kwargs.items():
            setattr(self, key, item)

    def mid(self, begin: int = 0, length: int = 0):
        if length > 0:
            tmp_end = min(begin + length, self.email_len)
        else:
            tmp_end = self.email_len
        tmp_str = ''.join(self.email_list[begin:tmp_end])
        return tmp_str


PF = ParserFixture()
ML = META_LOOKUP

RETURN_OBJ_L2 = {
    'inc_cat': ('cat', {'inc_cat': True, 'inc_diag': False}),
    'inc_diag': ('diag', {'inc_cat': False, 'inc_diag': True}),
    'inc_both': ('both', {'inc_cat': True, 'inc_diag': True}),
}
RETURN_OBJ_L3 = {
    'show_all': ('all', {'show_all': True}),
    'show_all_filtered': ('all-flt', {'show_all': True, 'filter': None}),
    'show_one': ('one', {'show_all': False}),
    'show_one_filtered': ('one-flt', {'show_all': False, 'filter': None}),
}

RETURN_OBJ_MD_CHANGE = {
    'document_string': ['RFC5321_QUOTED_STRING'],
}

RETURN_OBJ_TESTS = {
    'key_dict': {
        'inc_diag': {'raises': AttributeError},
        'inc_cat': {'raises': AttributeError},
        'inc_both': {
            'filter': 'RFC5321_TLD_NUMERIC',
            'show_all': {
                    'ISEMAIL_DNSWARN': [
                        'DNSWARN_INVALID_TLD'
                    ],
                    'ISEMAIL_RFC5321': [
                        'RFC5321_ADDRESS_LITERAL',
                        'RFC5321_QUOTED_STRING',
                        'RFC5321_TLD_NUMERIC',
                    ],
                    'ISEMAIL_ERR': [
                        'ERR_UNCLOSED_COMMENT'
                    ]
                },
            'show_all_filtered': {
                    'ISEMAIL_RFC5321': [
                        'RFC5321_TLD_NUMERIC'
                    ]
                },
            'show_one': {
                    'ISEMAIL_ERR': ['ERR_UNCLOSED_COMMENT']
                },
            'show_one_filtered': {
                    'ISEMAIL_RFC5321': ['RFC5321_TLD_NUMERIC']
                },
        },
            
    },
    'document_string': {
        'inc_diag': {'raises': AttributeError},
        'inc_cat'  : {'raises': AttributeError},
        'inc_both': {
            'filter'           : ('ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
            'show_all'         : ''
                    'ISEMAIL_ERR [ERROR]: Invalid Address\n'
                    '    ERR_UNCLOSED_COMMENT: Unclosed comment\n'
                    '\n'
                    'ISEMAIL_RFC5321 [WARNING]: Valid Address (unusual)\n'
                    '    RFC5321_QUOTED_STRING: [ERROR] Address is valid but contains a quoted string\n'
                    '    RFC5321_ADDRESS_LITERAL: Address is valid but at a literal address not a domain\n'
                    '    RFC5321_TLD_NUMERIC: Address is valid but the Top Level Domain begins with a number\n'
                    '\n'
                    'ISEMAIL_DNSWARN [WARNING]: Valid Address (DNS Warning)\n'
                    '    DNSWARN_INVALID_TLD: Top Level Domain is not in the list of available TLDs',

            'show_all_filtered': ''
                    'ISEMAIL_ERR [ERROR]: Invalid Address\n'
                    '    ERR_UNCLOSED_COMMENT: Unclosed comment\n'
                    '\n'
                    'ISEMAIL_RFC5321 [WARNING]: Valid Address (unusual)\n'
                    '    RFC5321_QUOTED_STRING: [ERROR] Address is valid but contains a quoted string\n'
                    '    RFC5321_ADDRESS_LITERAL: Address is valid but at a literal address not a domain\n'
                    '    RFC5321_TLD_NUMERIC: Address is valid but the Top Level Domain begins with a number',

            'show_one'         : ''
                    'ISEMAIL_ERR [ERROR]: Invalid Address\n'
                    '    ERR_UNCLOSED_COMMENT: Unclosed comment',

            'show_one_filtered': ''
                    'ISEMAIL_ERR [ERROR]: Invalid Address\n'
                    '    ERR_UNCLOSED_COMMENT: Unclosed comment',
        },

    },
    'obj_dict': {
        'inc_cat': {
            'filter': 'RFC5321_TLD_NUMERIC',
            'show_all': {
                    'ISEMAIL_DNSWARN': ML['ISEMAIL_DNSWARN'],
                    'ISEMAIL_RFC5321':  ML['ISEMAIL_RFC5321'],
                    'ISEMAIL_ERR':  ML['ISEMAIL_ERR'],
                },
            'show_all_filtered': {
                    'ISEMAIL_RFC5321': ML['ISEMAIL_RFC5321'],
                },
            'show_one': {
                    'ISEMAIL_ERR': ML['ISEMAIL_ERR'],
                },
            'show_one_filtered': {
                    'ISEMAIL_RFC5321': ML['ISEMAIL_RFC5321']
                },
        },
        'inc_diag': {
            'filter': 'RFC5321_TLD_NUMERIC',
            'show_all': {
                'DNSWARN_INVALID_TLD': ML['DNSWARN_INVALID_TLD'],
                'RFC5321_ADDRESS_LITERAL': ML['RFC5321_ADDRESS_LITERAL'],
                'RFC5321_QUOTED_STRING': ML['RFC5321_QUOTED_STRING'],
                'RFC5321_TLD_NUMERIC': ML['RFC5321_TLD_NUMERIC'],
                'ERR_UNCLOSED_COMMENT': ML['ERR_UNCLOSED_COMMENT'],                    
                },
            'show_all_filtered': {'RFC5321_TLD_NUMERIC': ML['RFC5321_TLD_NUMERIC']},
            'show_one': {'ERR_UNCLOSED_COMMENT': ML['ERR_UNCLOSED_COMMENT']},
            'show_one_filtered': {'RFC5321_TLD_NUMERIC': ML['RFC5321_TLD_NUMERIC']},
        },
        'inc_both': {'raises': AttributeError},

    },
    'object_list': {
        'inc_cat': {
            'filter': 'RFC5321_TLD_NUMERIC',
            'show_all': [
                    ML['ISEMAIL_ERR'],
                    ML['ISEMAIL_RFC5321'],
                    ML['ISEMAIL_DNSWARN'],
                ],
            'show_all_filtered': [ML['ISEMAIL_RFC5321']],
            'show_one': [ML['ISEMAIL_ERR']],
            'show_one_filtered': [ML['ISEMAIL_RFC5321']],
        },
        'inc_diag': {
            'filter': 'RFC5321_TLD_NUMERIC',
            'show_all': [
                ML['ERR_UNCLOSED_COMMENT'],
                ML['RFC5321_ADDRESS_LITERAL'],
                ML['RFC5321_QUOTED_STRING'],
                ML['RFC5321_TLD_NUMERIC'],
                ML['DNSWARN_INVALID_TLD'],
                ],
            'show_all_filtered': [ML['RFC5321_TLD_NUMERIC']],
            'show_one': [ML['ERR_UNCLOSED_COMMENT']],
            'show_one_filtered': [ML['RFC5321_TLD_NUMERIC']],
        },
        'inc_both': {'raises': AttributeError},

    },
    'key_list': {
        'inc_diag': {
            'filter': 'RFC5321_TLD_NUMERIC',
            'show_all': [
                'ERR_UNCLOSED_COMMENT',
                'RFC5321_ADDRESS_LITERAL',
                'RFC5321_QUOTED_STRING',
                'RFC5321_TLD_NUMERIC',
                'DNSWARN_INVALID_TLD',
            ],
            'show_all_filtered': ['RFC5321_TLD_NUMERIC'],
            'show_one': ['ERR_UNCLOSED_COMMENT'],
            'show_one_filtered': ['RFC5321_TLD_NUMERIC'],
        },
        'inc_cat': {
            'filter': 'RFC5321_TLD_NUMERIC',
            'show_all': [
                'ISEMAIL_ERR',
                'ISEMAIL_RFC5321',
                'ISEMAIL_DNSWARN',
                ],
            'show_all_filtered': ['ISEMAIL_RFC5321'],
            'show_one': ['ISEMAIL_ERR'],
            'show_one_filtered': ['ISEMAIL_RFC5321'],
        },
        'inc_both': {'raises': AttributeError},

    },
    'desc_list': {
        'inc_diag': {
            'filter'           : ('ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
            'show_all'         : [ 
                                 '[ERROR] Unclosed comment', 
                                 '[WARNING] Address is valid but at a literal address not a domain', 
                                 '[WARNING] Address is valid but contains a quoted string',
                                 '[WARNING] Address is valid but the Top Level Domain begins with a number',
                                 '[WARNING] Top Level Domain is not in the list of available TLDs'],
                
            'show_all_filtered': [
                                 '[ERROR] Unclosed comment',
                                 '[WARNING] Address is valid but at a literal address not a domain',
                                 '[WARNING] Address is valid but contains a quoted string',
                                 '[WARNING] Address is valid but the Top Level Domain begins with a number'],

            'show_one'         : ['[ERROR] Unclosed comment'],

            'show_one_filtered': ['[ERROR] Unclosed comment']

        },
        'inc_cat'  : {
            'filter'           : ('ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
            'show_all'         : [
                                 '[ERROR] - Invalid Address: (Address is invalid for any purpose)',
                                 '[WARNING] - Valid Address (unusual): (Address is valid for SMTP but has unusual elements)',
                                 '[WARNING] - Valid Address (DNS Warning): (Address is valid but a DNS check was not successful)'],

            'show_all_filtered': [
                                 '[ERROR] - Invalid Address: (Address is invalid for any purpose)',
                                 '[WARNING] - Valid Address (unusual): (Address is valid for SMTP but has unusual elements)'],

            'show_one'         : ['[ERROR] - Invalid Address: (Address is invalid for any purpose)'],
            'show_one_filtered': ['[ERROR] - Invalid Address: (Address is invalid for any purpose)'],

        },

        'inc_both' : {
            'filter'           : ('ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
            'show_all'         : [
                                 'Invalid Address: [ERROR]',
                                 '(Address is invalid for any purpose)',
                                 '    - Unclosed comment',
                                 'Valid Address (unusual): [WARNING]',
                                 '(Address is valid for SMTP but has unusual elements)',
                                 '    - Address is valid but at a literal address not a domain',
                                 '    - Address is valid but contains a quoted string',
                                 '    - Address is valid but the Top Level Domain begins with a number',
                                 'Valid Address (DNS Warning): [WARNING]',
                                 '(Address is valid but a DNS check was not successful)',
                                 '    - Top Level Domain is not in the list of available TLDs'],

            'show_all_filtered': [
                                 'Invalid Address: [ERROR]',
                                 '(Address is invalid for any purpose)',
                                 '    - Unclosed comment',
                                 'Valid Address (unusual): [WARNING]',
                                 '(Address is valid for SMTP but has unusual elements)',
                                 '    - Address is valid but at a literal address not a domain',
                                 '    - Address is valid but contains a quoted string',
                                 '    - Address is valid but the Top Level Domain begins with a number'],

            'show_one'         : [
                                 'Invalid Address: [ERROR]',
                                 '(Address is invalid for any purpose)',
                                 '    - Unclosed comment'],

            'show_one_filtered': [
                                 'Invalid Address: [ERROR]',
                                 '(Address is invalid for any purpose)',
                                 '    - Unclosed comment'],

        },

    },
    'formatted_string': {
        'inc_diag' : {
            'filter'           : ('ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
            'show_all'         : ''
                '[ERROR] Unclosed comment\n'
                '[WARNING] Address is valid but at a literal address not a domain\n'
                '[WARNING] Address is valid but contains a quoted string\n'
                '[WARNING] Address is valid but the Top Level Domain begins with a number\n'
                '[WARNING] Top Level Domain is not in the list of available TLDs',

            'show_all_filtered': ''
                '[ERROR] Unclosed comment\n'
                '[WARNING] Address is valid but at a literal address not a domain\n'
                '[WARNING] Address is valid but contains a quoted string\n'
                '[WARNING] Address is valid but the Top Level Domain begins with a number',

            'show_one'         : '[ERROR] Unclosed comment',

            'show_one_filtered': '[ERROR] Unclosed comment'

        },
        'inc_cat': {
            'filter'           : ('ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
            'show_all'         : ''
                '[ERROR] - Invalid Address: (Address is invalid for any purpose)\n'
                '[WARNING] - Valid Address (unusual): (Address is valid for SMTP but has unusual elements)\n'
                '[WARNING] - Valid Address (DNS Warning): (Address is valid but a DNS check was not successful)',

            'show_all_filtered': ''
                '[ERROR] - Invalid Address: (Address is invalid for any purpose)\n'
                '[WARNING] - Valid Address (unusual): (Address is valid for SMTP but has unusual elements)',

            'show_one'         : '[ERROR] - Invalid Address: (Address is invalid for any purpose)',
            'show_one_filtered': '[ERROR] - Invalid Address: (Address is invalid for any purpose)',

        },

        'inc_both': {
            'filter'           : ('ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
            'show_all'         : ''
                    'Invalid Address: [ERROR]\n'
                    '(Address is invalid for any purpose)\n'
                    '    - Unclosed comment\n'
                    '\n'
                    'Valid Address (unusual): [WARNING]\n'
                    '(Address is valid for SMTP but has unusual elements)\n'
                    '    - Address is valid but at a literal address not a domain\n'
                    '    - Address is valid but contains a quoted string\n'
                    '    - Address is valid but the Top Level Domain begins with a number\n'
                    '\n'
                    'Valid Address (DNS Warning): [WARNING]\n'
                    '(Address is valid but a DNS check was not successful)\n'
                    '    - Top Level Domain is not in the list of available TLDs',

            'show_all_filtered': ''
                    'Invalid Address: [ERROR]\n'
                    '(Address is invalid for any purpose)\n'
                    '    - Unclosed comment\n'
                    '\n'
                    'Valid Address (unusual): [WARNING]\n'
                    '(Address is valid for SMTP but has unusual elements)\n'
                    '    - Address is valid but at a literal address not a domain\n'
                    '    - Address is valid but contains a quoted string\n'
                    '    - Address is valid but the Top Level Domain begins with a number',

            'show_one'         : ''
                    'Invalid Address: [ERROR]\n'
                    '(Address is invalid for any purpose)\n'
                    '    - Unclosed comment',

            'show_one_filtered': ''
                'Invalid Address: [ERROR]\n'
                '(Address is invalid for any purpose)\n'
                '    - Unclosed comment'
        },
    },
}    

def _test_name(l1, l2=None, l3=None, suffix=None):
    tmp_ret = l1
    if l2 is not None:
        tmp_ret += '-'
        tmp_ret += RETURN_OBJ_L2[l2][0]
    if l3 is not None:
        tmp_ret += '-'
        tmp_ret += RETURN_OBJ_L3[l3][0]
    if suffix is not None:
        tmp_ret += '-'
        tmp_ret += suffix
    return tmp_ret


class TestParseFootball(unittest.TestCase):

    def setUp(self):
        META_LOOKUP.clear_overrides()

    def test_init_options(self):
        f = ParseResultFootball(PF)
        self.assertEquals(f.length, 0)

        f += 10
        self.assertEquals(f.length, 10)

        f -= 5
        self.assertEquals(f.length, 5)

    def test_math(self):
        f = ParseResultFootball(PF)
        f2 = ParseResultFootball(PF)

        self.assertEquals(f.length, 0)

        f += 10
        self.assertEquals(f.length, 10)

        f2 += 10
        f2 += f
        self.assertEquals(f2.length, 20)

    def test_math_2(self):
        f = ParseResultFootball(PF)

        self.assertEquals(f + 2, 2)
        self.assertEquals(2 + f, 2)

        f += 10
        self.assertEquals(f + 2, 12)
        self.assertEquals(2 + f, 12)

        f2 = ParseResultFootball(PF)
        f2 += 5

        self.assertEquals(f + f2, 15)
        self.assertEquals(f2 + f, 15)

    def test_init_length(self):
        f = ParseResultFootball(PF, length=10)

        self.assertEquals(f.length, 10)

    def test_init_length_full(self):

        f = ParseResultFootball(PF, length=13, position=20, segment='hello')

        self.assertEquals(f.length, 13)

    def test_comp_with_int(self):
        f = ParseResultFootball(PF, length=10)

        self.assertTrue(f > 5)
        self.assertTrue(f >= 10)
        self.assertTrue(f == 10)
        self.assertTrue(f != 20)
        self.assertTrue(f < 21)
        self.assertTrue(f <= 10)

    def test_comp_with_fb(self):
        f = ParseResultFootball(PF, length=10)
        f10 = ParseResultFootball(PF, length=10)
        f5 = ParseResultFootball(PF, length=5)
        f20 = ParseResultFootball(PF, length=20)

        self.assertTrue(f > f5)
        self.assertTrue(f >= f10)
        self.assertTrue(f == f10)
        self.assertTrue(f != f20)
        self.assertTrue(f < f20)
        self.assertTrue(f <= f10)

    def test_add_diag_str(self):
        per = ParseResultFootball(PF)
        per.add('VALID')

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_bad_diag(self):
        per = ParseResultFootball(PF)
        with self.assertRaises(AttributeError):
            per.add('FOOBAR')

    def test_add_diag_tuple(self):
        per = ParseResultFootball(PF)
        per.add(('VALID',1))

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_diag_dict(self):
        per = ParseResultFootball(PF)
        per.add({'diag': 'VALID', 'length': 1})

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_length_set(self):
        per = ParseResultFootball(PF)
        per += 3
        self.assertEquals(per.l, 3)
        per.add('VALID', set_length=1)

        self.assertEquals(per.l, 1)

    def test_add_football(self):
        per = ParseResultFootball(PF)
        per += 1

        per2 = ParseResultFootball(PF)
        per += 3

        per.add(per2)

        self.assertEquals(per.l, 4)

    def test_add_length_add(self):
        per = ParseResultFootball(PF)
        per += 1
        self.assertEquals(per.l, 1)
        per.add('VALID', length=1)

        self.assertEquals(per.l, 2)

    def test_add_ok_result(self):
        per = ParseResultFootball(PF, 'test_email_in', position=1)

        per.add(diag='VALID')

        self.assertFalse(per.error)

    def test_add_error_result(self):
        per = ParseResultFootball(PF, 'test_email_in')

        with self.assertRaises(ParsingError):
            per.add(diag='ERR_FWS_CRLF_X2')

        self.assertTrue(per.error)

    def test_add_warn_result(self):
        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertFalse(per.error)

    def test_add_mult_result(self):
        per = ParseResultFootball(PF, 'test_email_in')

        # self.assertTrue(per)
        # self.assertEquals(len(per), 0)

        per.add(diag='VALID', begin=1, length=1)
        # self.assertTrue(per)
        self.assertEquals(len(per), 1)
        self.assertFalse(per.error)

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        # self.assertTrue(per)
        self.assertEquals(len(per), 2)
        self.assertFalse(per.error)

        with self.assertRaises(ParsingError):
            per.add(diag='ERR_FWS_CRLF_X2', begin=1, length=1)
        self.assertTrue(per.error)

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertTrue(per.error)

    def test_error_on_warn(self):

        META_LOOKUP.set_error_on_warning(True)
        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag='VALID', begin=1, length=1)
        self.assertFalse(per.error)

        with self.assertRaises(ParsingError):
            per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertTrue(per.error)

        per.add(diag='VALID', begin=1, length=1)
        self.assertTrue(per.error)

    def test_error_on_value(self):
        per = ParseResultFootball(PF, 'test_email_in')

        META_LOOKUP.set_error_on('VALID')
        per('DNSWARN_NO_MX_RECORD')
        with self.assertRaises(ParsingError):
            per.add('VALID')
        self.assertTrue(per.error)

    def test_contains(self):
        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag':'DNSWARN_NO_MX_RECORD', 'begin':1, 'length':1})
        per.add(diag='DEPREC_QTEXT')
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertIn('DNSWARN_NO_MX_RECORD', per)

        self.assertNotIn('foobar', per)

    def test_clear(self):
        per = ParseResultFootball(PF, 'test_email_in')

        self.assertEquals(len(per), 0)
        per += 10

        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag':'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
        per.add(diag='DEPREC_QTEXT', raise_on_error=False)
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertEquals(len(per), 4)
        self.assertEquals(per.l, 10)
        per.clear()

        self.assertEquals(len(per), 0)
        self.assertEquals(per.l, 0)

    def test_remove(self):
        per = ParseResultFootball(PF, 'test_email_in')

        per += 10

        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag': 'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
        per.add(diag='DEPREC_QTEXT', raise_on_error=False)
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertEquals(len(per), 4)
        self.assertEquals(per.l, 10)

        per.remove(diag='VALID')
        self.assertEquals(len(per), 3)

        per.remove('DNSWARN_NO_MX_RECORD', rem_all=True)
        self.assertEquals(len(per), 1)


        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag': 'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
        per.add(diag='DEPREC_QTEXT', raise_on_error=False)
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertEquals(len(per), 5)

        per.remove('DNSWARN_NO_MX_RECORD')
        self.assertEquals(len(per), 4)


class TestFullResults(unittest.TestCase):

    COMPLEX_PARSER = dict(
        email_in='(comment1)"foobar"(comment2)@(comment3)[example.com](comment4)',
        at_loc=28,
        local_comments={0: 'comment1', 18: 'comment2'},
        domain_comments={29: 'comment3', 52: 'comment4'},
        domain_type=ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT,
    )
    LOCAL_QS_COM_PARSER = dict(
        email_in='(comment1)"foobar"(comment2)@example.com',
        at_loc=28,
        local_comments={0: 'comment1', 18: 'comment2'},
        domain_type=ISEMAIL_DOMAIN_TYPE.DNS,
    )
    DOMAIN_LIT_COM_PARSER = dict(
        email_in='foobar@(comment3)[example.com](comment4)',
        at_loc=6,
        domain_comments={7: 'comment3', 30: 'comment4'},
        domain_type=ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT,
    )
    LOCAL_QS_PARSER = dict(
        email_in='"foobar"@example.com',
        at_loc=8,
        domain_type=ISEMAIL_DOMAIN_TYPE.DNS,
    )
    DOMAIN_LIT_PARSER = dict(
        email_in='foobar@[example.com]',
        at_loc=6,
        domain_type=ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT,
    )
    NORMAL_PARSER = dict(
        email_in='foobar@example.com',
        at_loc=6,
        domain_type=ISEMAIL_DOMAIN_TYPE.DNS,
    )
    IPV4_PARSER = dict(
        email_in='"foobar"@[1.2.3.4]',
        at_loc=8,
        domain_type=ISEMAIL_DOMAIN_TYPE.IPv4,
    )
    IPV6_PARSER = dict(
        email_in='foobar@[IPV6:1::6:7:8]',
        at_loc=6,
        domain_type=ISEMAIL_DOMAIN_TYPE.IPv6,
    )
    GENERAL_LIT_PARSER = dict(
        email_in='foobar@[http:example.com]',
        at_loc=6,
        domain_type=ISEMAIL_DOMAIN_TYPE.GENERAL_LIT,
    )



    VALID = ['VALID']
    MULT_WARN = ['RFC5322_DOMAIN', 'DEPREC_COMMENT']
    WARN = ['RFC5322_DOMAIN', 'DEPREC_COMMENT']
    MULT_WARN_ERR = ['RFC5322_DOMAIN', 'DEPREC_COMMENT', 'ERR_DOT_END']
    ERR = ['ERR_DOT_END']
    COMPLEX_DIAGS = ['DNSWARN_INVALID_TLD', 'RFC5321_TLD_NUMERIC', 'RFC5321_QUOTED_STRING',
                     'RFC5321_ADDRESS_LITERAL', 'ERR_UNCLOSED_COMMENT']

    def make_parser(self, **kwargs):
        kwargs['email_in'] = kwargs.get('email_in', 'foobar@example.com')
        kwargs['verbose'] = kwargs.get('verbose', 3)
        kwargs['trace_filter'] = kwargs.get('trace_filter', 999)
        kwargs['raise_on_error'] = kwargs.get('raise_on_error', False)
        kwargs['at_loc'] = kwargs.get('at_loc', 6)
        kwargs['dns_lookup_level'] = kwargs.get('dns_lookup_level', ISEMAIL_DNS_LOOKUP_LEVELS.NO_LOOKUP)

        tmp_ret = ParserFixture(**kwargs)

        return tmp_ret

    def make_football(self, *args, parser=None, diags=None, length=6, position=0, raise_on_error=False, **kwargs):
        at_loc = None
        domain_type = None
        local_comments = None
        domain_comments = None

        if parser is None:
            parser = self.make_parser()
        if isinstance(parser, dict):
            at_loc = parser.pop('at_loc', None)
            domain_type = parser.pop('domain_type', None)
            local_comments = parser.pop('local_comments', None)
            domain_comments = parser.pop('domain_comments', None)
            parser = self.make_parser(**parser)

        if isinstance(parser, str):
            parser = self.make_parser(email_in=parser)

        tmp_fb = ParseResultFootball(parser)

        tmp_fb += length
        tmp_fb.begin = position

        if at_loc is not None:
            tmp_fb.at_loc = at_loc
        if domain_type is not None:
            tmp_fb.domain_type = domain_type
        if local_comments is not None:
            tmp_fb._local_comments = local_comments
        if domain_comments is not None:
            tmp_fb._domain_comments = domain_comments

        if kwargs or args:
            tmp_fb(*args, raise_on_error=raise_on_error, **kwargs)

        if diags is not None:
            if isinstance(diags, str):
                tmp_fb(diags, raise_on_error=raise_on_error)
            else:
                tmp_fb(*diags, raise_on_error=raise_on_error)

        else:
            tmp_fb('VALID')
        return tmp_fb

    def make_result(self, *args, parser=None, diags=None, dns_lookup_level=None, raise_on_error=False, length=6, position=0, **kwargs):
        tmp_fb = self.make_football(*args, parser=parser, diags=diags, length=length, position=position, raise_on_error=raise_on_error, **kwargs)
        tmp_ret = tmp_fb.finish(dns_lookup_level=dns_lookup_level, raise_on_error=raise_on_error)
        return tmp_ret

    def test_init(self):
        tmp_resp = self.make_result()

    def test_bool(self):
        tmp_resp = self.make_result()
        self.assertTrue(tmp_resp)

        tmp_resp = self.make_result(diags='ERR_EMPTY_ADDRESS', raise_on_error=False)
        self.assertFalse(tmp_resp)

    def test_str(self):
        tmp_resp = self.make_result()
        self.assertEqual(str(tmp_resp), 'foobar@example.com')

    def test_len(self):
        tmp_resp = self.make_result()
        self.assertEqual(len(tmp_resp), 18)

    def test_status(self):
        tmp_resp = self.make_result(diags=['ERR_EMPTY_ADDRESS', 'RFC5322_LOCAL_TOO_LONG'])
        self.assertEqual(tmp_resp.status, ISEMAIL_RESULT_CODES.ERROR)
        self.assertFalse(tmp_resp)

        tmp_resp = self.make_result(diags=['RFC5322_TOO_LONG', 'RFC5322_LOCAL_TOO_LONG'])
        self.assertEqual(tmp_resp.status, ISEMAIL_RESULT_CODES.WARNING)
        self.assertTrue(tmp_resp)

    def test_ok(self):
        tmp_resp = self.make_result()
        self.assertTrue(tmp_resp.ok)
        self.assertFalse(tmp_resp.warning)
        self.assertFalse(tmp_resp.error)

    def test_warning(self):
        tmp_resp = self.make_result(diag='RFC5322_TOO_LONG')
        self.assertFalse(tmp_resp.ok)
        self.assertTrue(tmp_resp.warning)
        self.assertFalse(tmp_resp.error)

    def test_error(self):
        tmp_resp = self.make_result(diag='ERR_EMPTY_ADDRESS')
        self.assertFalse(tmp_resp.ok)
        self.assertFalse(tmp_resp.warning)
        self.assertTrue(tmp_resp.error)

    def test_parsing_complex(self):
        """
        COMPLEX_PARSER = dict(
            email_in='(comment1)"foobar"(comment2)@(comment3)[example.com](comment4)',
            at_loc=28,
            local_comments={0: 'comment1', 18: 'comment2'},
            domain_comments={29: 'comment3', 52: 'comment4'},
        )
        """
        tmp_resp = self.make_result(parser=self.COMPLEX_PARSER)
        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, '(comment1)"foobar"(comment2)')

        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '(comment3)[example.com](comment4)')

        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, '"foobar"')

        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[example.com]')

        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')

        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')

        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, '"foobar"@[example.com]')

        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, '(comment1)"foobar"(comment2)@(comment3)[example.com](comment4)')

        with self.subTest('local_comments'):
            self.assertCountEqual(tmp_resp.local_comments, ['comment1', 'comment2'])

        with self.subTest('domain_comments'):
            self.assertCountEqual(tmp_resp.domain_comments, ['comment3', 'comment4'])

    def test_parsing_qs_com(self):
        """
        LOCAL_QS_COM_PARSER = dict(
            email_in='(comment1)"foobar"(comment2)@example.com',
            at_loc=28,
            local_comments={0: 'comment1', 18: 'comment2'},
        )
        """
        tmp_resp = self.make_result(parser=self.LOCAL_QS_COM_PARSER)

        with self.subTest('full_local'):

            self.assertEqual(tmp_resp.full_local, '(comment1)"foobar"(comment2)')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, 'example.com')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, '"foobar"')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, 'example.com')
        with self.subTest('local'):
          self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
           self.assertEqual(tmp_resp.domain, 'example.com')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, '"foobar"@example.com')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, '(comment1)"foobar"(comment2)@example.com')
        with self.subTest('local_comments'):
            self.assertCountEqual(tmp_resp.local_comments, ['comment1', 'comment2'])
        with self.subTest('domain_comments'):
            self.assertCountEqual(tmp_resp.domain_comments, [])

    def test_parsing_dom_lit_com(self):
        """
        DOMAIN_LIT_COM_PARSER = dict(
            email_in='foobar@(comment2)[example.com](comment4)',
            at_loc=6,
            domain_comments={7: 'comment3', 30: 'comment4'},
        )
        """
        tmp_resp = self.make_result(parser=self.DOMAIN_LIT_COM_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, 'foobar')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '(comment3)[example.com](comment4)')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, 'foobar')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[example.com]')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, 'foobar@[example.com]')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, 'foobar@(comment3)[example.com](comment4)')
        with self.subTest('local_comments'):
            self.assertCountEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertCountEqual(tmp_resp.domain_comments, ['comment3', 'comment4'])

    def test_parsing_qs(self):
        """
        LOCAL_QS_PARSER = dict(
            email_in='"foobar"@example.com',
            at_loc=8,
        )
        """
        tmp_resp = self.make_result(parser=self.LOCAL_QS_PARSER)


        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, '"foobar"')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, 'example.com')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, '"foobar"')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, 'example.com')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, '"foobar"@example.com')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, '"foobar"@example.com')
        with self.subTest('local_comments'):
            self.assertCountEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertCountEqual(tmp_resp.domain_comments, [])

    def test_parsing_dom_lit(self):
        """
        DOMAIN_LIT_PARSER = dict(
            email_in='foobar@[example.com]',
            at_loc=6,
        )
        """
        tmp_resp = self.make_result(parser=self.DOMAIN_LIT_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, 'foobar')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '[example.com]')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, 'foobar')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[example.com]')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, 'foobar@[example.com]')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, 'foobar@[example.com]')
        with self.subTest('local_comments'):
            self.assertEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertEqual(tmp_resp.domain_comments, [])

    def test_parsing_normal(self):
        """
        NORMAL_PARSER = dict(
            email_in='foobar@example.com',
            at_loc=6,
        )
        """
        tmp_resp = self.make_result(parser=self.NORMAL_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, 'foobar')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, 'example.com')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, 'foobar')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, 'example.com')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, 'foobar@example.com')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, 'foobar@example.com')
        with self.subTest('local_comments'):
            self.assertEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertEqual(tmp_resp.domain_comments, [])

    def test_parsing_ipv4(self):
        """
        IPV4_PARSER = dict(
            email_in='"foobar"@[1.2.3.4]',
            at_loc=8,
        )
        """

        tmp_resp = self.make_result(parser=self.IPV4_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, '"foobar"')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '[1.2.3.4]')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, '"foobar"')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[1.2.3.4]')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, '1.2.3.4')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, '"foobar"@[1.2.3.4]')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, '"foobar"@[1.2.3.4]')
        with self.subTest('local_comments'):
            self.assertEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertEqual(tmp_resp.domain_comments, [])

    def test_parsing_ipv6(self):
        """
        IPV6_PARSER = dict(
            email_in='foobar@[IPV6:1::6:7:8',
            at_loc=6,
        )
        """
        tmp_resp = self.make_result(parser=self.IPV6_PARSER)

        with self.subTest('full_local'):

            self.assertEqual(tmp_resp.full_local, 'foobar')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '[IPv6:1::6:7:8]')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, 'foobar')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[IPv6:1::6:7:8]')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, '1::6:7:8')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, 'foobar@[IPv6:1::6:7:8]')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, 'foobar@[IPV6:1::6:7:8]')
        with self.subTest('local_comments'):
            self.assertEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertEqual(tmp_resp.domain_comments, [])

    def test_parsing_gen_lit(self):
        """
        GENERAL_LIT_PARSER = dict(
            email_in='foobar@[http:example.com]',
            at_loc=6,
        )
        """
        tmp_resp = self.make_result(parser=self.GENERAL_LIT_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, 'foobar')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '[http:example.com]')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, 'foobar')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[http:example.com]')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, ['http', 'example.com'])
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, 'foobar@[http:example.com]')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, 'foobar@[http:example.com]')
        with self.subTest('local_comments'):
            self.assertEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertEqual(tmp_resp.domain_comments, [])

    def test_trace(self):
        tmp_resp = self.make_result()
        self.assertEqual(tmp_resp.trace, 'This is a trace string')

    def test_history(self):
        tmp_resp = self.make_result()

        self.assertEqual(tmp_resp.history(level=1), 'address_spec(...)')
        self.assertEqual(tmp_resp.history(level=2), 'address_spec(local_part(...), domain_part(...))')
        self.assertEqual(tmp_resp.history(), 'address_spec(local_part(dot_atom()), domain_part(blah))')

    def test_contains(self):
        tmp_resp = self.make_result(diags=self.COMPLEX_DIAGS)
        tmp_answ = 'RFC5321_ADDRESS_LITERAL' in tmp_resp
        self.assertTrue(tmp_answ)

        tmp_answ = 'foobar' in tmp_resp
        self.assertFalse(tmp_answ)

    def test_getitem(self):
        tmp_resp = self.make_result(diags=self.COMPLEX_DIAGS)
        tmp_answ = tmp_resp['RFC5321_ADDRESS_LITERAL']
        self.assertEqual(tmp_answ, ML['RFC5321_ADDRESS_LITERAL'])

    def run_ret_obj_test(self, l1, l2, l3, call_diag=False):
        tmp_res = self.make_result(diags=self.COMPLEX_DIAGS)

        kwargs = {}
        kwargs.update(RETURN_OBJ_L2[l2][1])
        kwargs.update(RETURN_OBJ_L3[l3][1])
        if 'filter' in kwargs:
            kwargs['filter'] = RETURN_OBJ_TESTS[l1][l2]['filter']

        if call_diag:
            if l1 == 'object_list':
                kwargs['return_obj'] = True
                kwargs['return_as_list'] = True

            elif l1 == 'object_dict':
                kwargs['return_obj'] = True
                kwargs['return_as_list'] = False

            elif l1 == 'key_list':
                kwargs['return_obj'] = False
                kwargs['return_as_list'] = True

            elif l1 == 'key_dict':
                kwargs['return_obj'] = False
                kwargs['return_as_list'] = False

            tmp_ret = tmp_res.diag(**kwargs)
        else:
            tmp_ret = tmp_res.report(l1, **kwargs)


        tmp_exp = RETURN_OBJ_TESTS[l1][l2][l3]

        if l1 in ['key_dict', 'key_list', 'desc_list']:
            tmp_ret_str = json.dumps(tmp_ret, indent=4)
            tmp_exp_str = json.dumps(tmp_exp, indent=4)
        elif l1 in ['document_string', 'formatted_string']:
            tmp_ret_str = tmp_ret
            tmp_exp_str = tmp_exp
        else:
            tmp_ret_str = repr(tmp_ret)
            tmp_exp_str = repr(tmp_exp)

        tmp_msg = '\n\n\nItems do not compare\n\n'
        tmp_msg += 'L1: %s\n' % l1
        tmp_msg += 'L2: %s\n' % l2
        tmp_msg += 'L3: %s\n' % l3
        tmp_msg += 'Test Name: %s\n\n' % _test_name(l1, l2, l3)

        tmp_msg += 'kwargs:\n%s\n\n' % json.dumps(kwargs, indent=4)
        tmp_msg += 'Expected:\n************************\n' \
                  '%s\n\nReturned\n************************\n%s\n\n' % (tmp_exp_str, tmp_ret_str)

        tmp_msg += '\n\n\n'
        tmp_msg += 'Expected: %r\nReturned: %r\n\n' % (tmp_exp_str, tmp_ret_str)

        self.assertEqual(tmp_ret, tmp_exp, msg=tmp_msg)

    def test_return_objects(self):
        """
        {
        L1    'report_name':
        L2        'inc_whatever':
                       'raises'
                      'filter':
        L3            'show_all':
                        'show_all_filtered'
                        'show_one'
                        'show_one_filtered'
        """
        # META_LOOKUP.set_error_on('RFC5321_QUOTED_STRING')
        LIMIT_TO = ['', '', '']
        # LIMIT_TO = ['desc_list', 'both', 'all-flt']

        if LIMIT_TO != ['', '', '']:
            with self.subTest('NOTE: Test Limited to: %r' % LIMIT_TO):
                self.fail()

        for l1 in RETURN_OBJ_TESTS.keys():
            if LIMIT_TO[0] == '' or LIMIT_TO[0] == l1:
                for l2 in RETURN_OBJ_L2.keys():
                    if LIMIT_TO[1] == '' or LIMIT_TO[1] == RETURN_OBJ_L2[l2][0]:
                        if not 'raises' in RETURN_OBJ_TESTS[l1][l2]:
                            for l3 in RETURN_OBJ_L3.keys():
                                if LIMIT_TO[2] == '' or LIMIT_TO[2] == RETURN_OBJ_L3[l3][0]:
                                    for i in RETURN_OBJ_MD_CHANGE:
                                        META_LOOKUP.clear_overrides()
                                        if _test_name(l1, l2, l3).startswith(i):
                                            META_LOOKUP.set_error_on(RETURN_OBJ_MD_CHANGE[i])
                                    with self.subTest(_test_name(l1, l2, l3)):
                                        self.run_ret_obj_test(l1, l2, l3)
                                    with self.subTest(_test_name(l1, l2, l3)+'-DIAG'):
                                        if l1 in ['object_list', 'object_dict', 'key_list', 'key_dict']:
                                            self.run_ret_obj_test(l1, l2, l3, call_diag=True)






class TestHistory(unittest.TestCase):
    PF = ParserFixture('abcdefghijklmnopqrstuvwxyz')

    def test_sinple_history(self):
        per = ParseResultFootball(self.PF, 'test_in', position=0)
        per += 10
        self.assertEquals(str(per.history), 'test_in')

    def test_simple_history_w_str(self):
        per = ParseResultFootball(self.PF, 'test_in', position=2, length=4)
        # per += 10

        self.assertEquals(str(per.history.short_desc(inc_string=True)), "test_in['cdef']")

    def test_simple_history_2(self):
        per = ParseResultFootball(self.PF, 'test_in')
        per += 10

        self.assertEquals(str(per.history.short_desc()), 'test_in')

    def test_long_history_w_str(self):
        per = ParseResultFootball(self.PF, 'test_in')
        per += 4
        self.assertEquals(str(per.history.long_desc()), "test_in   :   'abcd'")

    def test_2_level(self):
        per = ParseResultFootball(self.PF, 'lvl_1')
        per += 2
        per_2 = ParseResultFootball(self.PF, 'lvl_2')
        per_2 += 3
        per += per_2
        self.assertEquals(per.history.short_desc(), 'lvl_1(lvl_2)')

    def test_complex_history_w_str(self):
        per = ParseResultFootball(self.PF, 'lvl_1', position=0)

        per_2 = ParseResultFootball(self.PF, 'lvl_2', position=0)
        per_2 += 2
        per += per_2

        per_3 = ParseResultFootball(self.PF, 'lvl_3', position=2)
        per_3 += 2
        per += per_3

        self.assertEquals(per.history.short_desc(), 'lvl_1(lvl_2, lvl_3)')

        self.assertEquals(per.history.short_desc(inc_string=True), "lvl_1['abcd'](lvl_2['ab'], lvl_3['cd'])")

        self.assertEquals(per.history.long_desc(), "lvl_1   :   'abcd'\n    lvl_2   :   'ab'\n    lvl_3   :   'cd'")


class TestMetaLookup(unittest.TestCase):
    maxDiff = None
    # longMessage = False

    def setUp(self):
        META_LOOKUP.clear_overrides()

    def test_hash(self):
        tmp_dict = {}
        tmp_obj = META_LOOKUP['DEPREC_QTEXT']
        tmp_dict[tmp_obj] = 'foobar'
        self.assertEqual(hash('DEPREC_QTEXT'), hash(tmp_obj))
        self.assertEqual('foobar', tmp_dict[tmp_obj])

    def test_lenths(self):
        self.assertEquals(len(META_LOOKUP.categories), 7)
        self.assertEquals(len(META_LOOKUP.diags), 67)

    def test_get_by_value_diag(self):
        tmp_item = META_LOOKUP['ISEMAIL_RFC5322']
        self.assertEquals(tmp_item.name, 'Valid Address (unusable)')
        self.assertEquals(tmp_item.description, "The address is only valid according to the broad definition of RFC 5322. It is otherwise invalid.",)
        self.assertEquals(tmp_item.status, ISEMAIL_RESULT_CODES.WARNING)

    def test_get_by_key_diag(self):
        tmp_item = META_LOOKUP['DEPREC_QTEXT']
        self.assertEquals(tmp_item.value, 103500)
        self.assertEquals(tmp_item.category.value, 50000)
        self.assertEquals(tmp_item.description, "A quoted string contains a deprecated character")
        self.assertEquals(tmp_item.category.status, ISEMAIL_RESULT_CODES.WARNING)
        self.assertEquals(tmp_item.smtp, "553 5.1.3 Bad destination mailbox address syntax")

    def test_ia_error(self):
        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertFalse(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertFalse(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.set_error_on('VALID')
        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertFalse(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertTrue(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.set_error_on('DNSWARN_COMM_ERROR')
        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertTrue(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertTrue(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.clear_overrides()

        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertFalse(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertFalse(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.set_error_on('ISEMAIL_DNSWARN')
        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertTrue(META_LOOKUP.is_error('DNSWARN_NO_RECORD'))
        self.assertTrue(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertFalse(META_LOOKUP.is_error('DEPREC_COMMENT'))
        self.assertFalse(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.clear_overrides()

        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertFalse(META_LOOKUP.is_error('DNSWARN_NO_RECORD'))
        self.assertFalse(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertFalse(META_LOOKUP.is_error('DEPREC_COMMENT'))
        self.assertFalse(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.set_error_on_warning()
        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertTrue(META_LOOKUP.is_error('DNSWARN_NO_RECORD'))
        self.assertTrue(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertTrue(META_LOOKUP.is_error('DEPREC_COMMENT'))
        self.assertFalse(META_LOOKUP.is_error('VALID'))

    def run_ret_obj_test(self, l1, l2, l3):
        kwargs = {'diags': ['DNSWARN_INVALID_TLD', 'RFC5321_TLD_NUMERIC', 'RFC5321_QUOTED_STRING',
                           'RFC5321_ADDRESS_LITERAL', 'ERR_UNCLOSED_COMMENT']}

        kwargs.update(RETURN_OBJ_L2[l2][1])
        kwargs.update(RETURN_OBJ_L3[l3][1])
        if 'filter' in kwargs:
            kwargs['filter'] = RETURN_OBJ_TESTS[l1][l2]['filter']

        tmp_ret = META_LOOKUP(l1, **kwargs)
        tmp_exp = RETURN_OBJ_TESTS[l1][l2][l3]

        if l1 in ['key_dict', 'key_list', 'desc_list']:
            tmp_ret_str = json.dumps(tmp_ret, indent=4)
            tmp_exp_str = json.dumps(tmp_exp, indent=4)
        elif l1 in ['document_string', 'formatted_string']:
            tmp_ret_str = tmp_ret
            tmp_exp_str = tmp_exp
        else:
            tmp_ret_str = repr(tmp_ret)
            tmp_exp_str = repr(tmp_exp)

        tmp_msg = '\n\n\nItems do not compare\n\n'
        tmp_msg += 'L1: %s\n' % l1
        tmp_msg += 'L2: %s\n' % l2
        tmp_msg += 'L3: %s\n' % l3
        tmp_msg += 'Test Name: %s\n\n' % _test_name(l1, l2, l3)

        tmp_msg += 'kwargs:\n%s\n\n' % json.dumps(kwargs, indent=4)
        tmp_msg += 'Expected:\n************************\n' \
                  '%s\n\nReturned\n************************\n%s\n\n' % (tmp_exp_str, tmp_ret_str)

        tmp_msg += '\n\n\n'
        tmp_msg += 'Expected: %r\nReturned: %r\n\n' % (tmp_exp_str, tmp_ret_str)

        self.assertEqual(tmp_ret, tmp_exp, msg=tmp_msg)

    def run_raise_obj_test(self, l1, l2):
        kwargs = {'diags': ['DNSWARN_INVALID_TLD', 'RFC5321_TLD_NUMERIC', 'RFC5321_QUOTED_STRING',
                            'RFC5321_ADDRESS_LITERAL', 'ERR_UNCLOSED_COMMENT']}

        kwargs.update(RETURN_OBJ_L2[l2][1])

        if 'filter' in kwargs:
            kwargs['filter'] = RETURN_OBJ_TESTS[l1][l2]['filter']

        tmp_msg = '\n\n\nItems do not compare\n\n'
        tmp_msg += 'L1: %s\n' % l1
        tmp_msg += 'L2: %s\n' % l2
        tmp_msg += 'Test Name: %s\n\n' % _test_name(l1, l2)

        tmp_msg += 'kwargs:\n%s\n\n' % json.dumps(kwargs, indent=4)

        with self.assertRaises(RETURN_OBJ_TESTS[l1][l2]['raises'], msg=tmp_msg):
            tmp_ret = META_LOOKUP(l1, **kwargs)

    def test_return_objects(self):
        """
        {
        L1    'report_name':
        L2        'inc_whatever':
                       'raises'
                      'filter':
        L3            'show_all':
                        'show_all_filtered'
                        'show_one'
                        'show_one_filtered'
        """
        # META_LOOKUP.set_error_on('RFC5321_QUOTED_STRING')
        LIMIT_TO = ['', '', '']
        # LIMIT_TO = ['desc_list', 'both', 'all-flt']

        if LIMIT_TO != ['', '', '']:
            with self.subTest('NOTE: Test Limited to: %r' % LIMIT_TO):
                self.fail()

        for l1 in RETURN_OBJ_TESTS.keys():
            if LIMIT_TO[0] == '' or LIMIT_TO[0] == l1:
                for l2 in RETURN_OBJ_L2.keys():
                    if LIMIT_TO[1] == '' or LIMIT_TO[1] == RETURN_OBJ_L2[l2][0]:
                        if 'raises' in RETURN_OBJ_TESTS[l1][l2]:
                            with self.subTest(_test_name(l1, l2, suffix='raise')):
                                self.run_raise_obj_test(l1, l2)
                        else:
                            for l3 in RETURN_OBJ_L3.keys():
                                if LIMIT_TO[2] == '' or LIMIT_TO[2] == RETURN_OBJ_L3[l3][0]:
                                    with self.subTest(_test_name(l1, l2, l3)):
                                        for i in RETURN_OBJ_MD_CHANGE:
                                            META_LOOKUP.clear_overrides()
                                            if _test_name(l1, l2, l3).startswith(i):
                                                META_LOOKUP.set_error_on(RETURN_OBJ_MD_CHANGE[i])
                                        self.run_ret_obj_test(l1, l2, l3)
