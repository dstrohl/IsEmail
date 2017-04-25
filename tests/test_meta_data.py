import unittest
import json
from parse_results import ParseResultFootball, ParsingError, ParseHistoryData
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
    'inc_cat' : ('cat', {'inc_cat': True, 'inc_diag': False}),
    'inc_diag': ('diag', {'inc_cat': False, 'inc_diag': True}),
    'inc_both': ('both', {'inc_cat': True, 'inc_diag': True}),
}
RETURN_OBJ_L3 = {
    'show_all'         : ('all', {'show_all': True}),
    'show_all_filtered': ('all-flt', {'show_all': True, 'filter': None}),
    'show_one'         : ('one', {'show_all': False}),
    'show_one_filtered': ('one-flt', {'show_all': False, 'filter': None}),
}

RETURN_OBJ_MD_CHANGE = {
    'document_string': ['RFC5321_QUOTED_STRING'],
}

RETURN_OBJ_TESTS = {
    'key_dict'        : {
        'inc_diag': {'raises': AttributeError},
        'inc_cat' : {'raises': AttributeError},
        'inc_both': {
            'filter'           : 'RFC5321_TLD_NUMERIC',
            'show_all'         : {
                'ISEMAIL_DNSWARN': [
                    'DNSWARN_INVALID_TLD'
                ],
                'ISEMAIL_RFC5321': [
                    'RFC5321_ADDRESS_LITERAL',
                    'RFC5321_QUOTED_STRING',
                    'RFC5321_TLD_NUMERIC',
                ],
                'ISEMAIL_ERR'    : [
                    'ERR_UNCLOSED_COMMENT'
                ]
            },
            'show_all_filtered': {
                'ISEMAIL_RFC5321': [
                    'RFC5321_TLD_NUMERIC'
                ]
            },
            'show_one'         : {
                'ISEMAIL_ERR': ['ERR_UNCLOSED_COMMENT']
            },
            'show_one_filtered': {
                'ISEMAIL_RFC5321': ['RFC5321_TLD_NUMERIC']
            },
        },

    },
    'document_string' : {
        'inc_diag': {'raises': AttributeError},
        'inc_cat' : {'raises': AttributeError},
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
    'obj_dict'        : {
        'inc_cat' : {
            'filter'           : 'RFC5321_TLD_NUMERIC',
            'show_all'         : {
                'ISEMAIL_DNSWARN': ML['ISEMAIL_DNSWARN'],
                'ISEMAIL_RFC5321': ML['ISEMAIL_RFC5321'],
                'ISEMAIL_ERR'    : ML['ISEMAIL_ERR'],
            },
            'show_all_filtered': {
                'ISEMAIL_RFC5321': ML['ISEMAIL_RFC5321'],
            },
            'show_one'         : {
                'ISEMAIL_ERR': ML['ISEMAIL_ERR'],
            },
            'show_one_filtered': {
                'ISEMAIL_RFC5321': ML['ISEMAIL_RFC5321']
            },
        },
        'inc_diag': {
            'filter'           : 'RFC5321_TLD_NUMERIC',
            'show_all'         : {
                'DNSWARN_INVALID_TLD'    : ML['DNSWARN_INVALID_TLD'],
                'RFC5321_ADDRESS_LITERAL': ML['RFC5321_ADDRESS_LITERAL'],
                'RFC5321_QUOTED_STRING'  : ML['RFC5321_QUOTED_STRING'],
                'RFC5321_TLD_NUMERIC'    : ML['RFC5321_TLD_NUMERIC'],
                'ERR_UNCLOSED_COMMENT'   : ML['ERR_UNCLOSED_COMMENT'],
            },
            'show_all_filtered': {'RFC5321_TLD_NUMERIC': ML['RFC5321_TLD_NUMERIC']},
            'show_one'         : {'ERR_UNCLOSED_COMMENT': ML['ERR_UNCLOSED_COMMENT']},
            'show_one_filtered': {'RFC5321_TLD_NUMERIC': ML['RFC5321_TLD_NUMERIC']},
        },
        'inc_both': {'raises': AttributeError},

    },
    'object_list'     : {
        'inc_cat' : {
            'filter'           : 'RFC5321_TLD_NUMERIC',
            'show_all'         : [
                ML['ISEMAIL_ERR'],
                ML['ISEMAIL_RFC5321'],
                ML['ISEMAIL_DNSWARN'],
            ],
            'show_all_filtered': [ML['ISEMAIL_RFC5321']],
            'show_one'         : [ML['ISEMAIL_ERR']],
            'show_one_filtered': [ML['ISEMAIL_RFC5321']],
        },
        'inc_diag': {
            'filter'           : 'RFC5321_TLD_NUMERIC',
            'show_all'         : [
                ML['ERR_UNCLOSED_COMMENT'],
                ML['RFC5321_ADDRESS_LITERAL'],
                ML['RFC5321_QUOTED_STRING'],
                ML['RFC5321_TLD_NUMERIC'],
                ML['DNSWARN_INVALID_TLD'],
            ],
            'show_all_filtered': [ML['RFC5321_TLD_NUMERIC']],
            'show_one'         : [ML['ERR_UNCLOSED_COMMENT']],
            'show_one_filtered': [ML['RFC5321_TLD_NUMERIC']],
        },
        'inc_both': {'raises': AttributeError},

    },
    'key_list'        : {
        'inc_diag': {
            'filter'           : 'RFC5321_TLD_NUMERIC',
            'show_all'         : [
                'ERR_UNCLOSED_COMMENT',
                'RFC5321_ADDRESS_LITERAL',
                'RFC5321_QUOTED_STRING',
                'RFC5321_TLD_NUMERIC',
                'DNSWARN_INVALID_TLD',
            ],
            'show_all_filtered': ['RFC5321_TLD_NUMERIC'],
            'show_one'         : ['ERR_UNCLOSED_COMMENT'],
            'show_one_filtered': ['RFC5321_TLD_NUMERIC'],
        },
        'inc_cat' : {
            'filter'           : 'RFC5321_TLD_NUMERIC',
            'show_all'         : [
                'ISEMAIL_ERR',
                'ISEMAIL_RFC5321',
                'ISEMAIL_DNSWARN',
            ],
            'show_all_filtered': ['ISEMAIL_RFC5321'],
            'show_one'         : ['ISEMAIL_ERR'],
            'show_one_filtered': ['ISEMAIL_RFC5321'],
        },
        'inc_both': {'raises': AttributeError},

    },
    'desc_list'       : {
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
        'inc_cat' : {
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

        'inc_both': {
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
        'inc_diag': {
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
        'inc_cat' : {
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
        self.assertEquals(tmp_item.description,
                          "The address is only valid according to the broad definition of RFC 5322. It is otherwise invalid.", )
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
