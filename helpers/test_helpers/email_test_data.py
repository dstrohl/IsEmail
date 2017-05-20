from helpers.meta_data import META_LOOKUP, ISEMAIL_DNS_LOOKUP_LEVELS

CORRECTED_TESTS = {
    'version': '4.00',
    3: {
        'diag'  : 'ERR_NO_DOMAIN_SEP',
        'was': 'ERR_NO_DOMAIN_PART',
        'reason': 'I find the lack of the domain sep first, then error out.'
    },
    6: {
        'diag': 'RFC5321_TLD',
        'was': 'VALID_CATEGORY',
        'reason': 'while it is a valid email, it still justifies a warning that it is a TLD domain.'
    },
    13: {
        'diag'  : 'DNSWARN_INVALID_TLD',
        'was': 'DNSWARN_NO_RECORD',
        'reason': 'We do not bother trying to lookup domains that are not listed in the TLD list.'
    },
    18: {
        'diag'  : 'ERR_NO_DOMAIN_SEP',
        'was': 'ERR_NO_DOMAIN_PART',
        'reason': 'I find the lack of the domain sep first, then error out.'
    },
    22: {
        'diag'  : 'DNSWARN_NO_MX_RECORD',
        'was'   : 'VALID_CATEGORY',
        'reason': "I guess they don't do mail there any more."
    },
    31: {
        'diag'  : 'RFC5322_LIMITED_DOMAIN',
        'codes': ['RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN'],
        'was'   : 'ERR_DOMAIN_HYPHEN_END',
        'reason': "while not valid for normal DNS, it's legal by RFC5322 (dot-atom)"
    },
    33: {
        'diag'  : 'DNSWARN_INVALID_TLD',
        'was'   : 'DNSWARN_NO_RECORD',
        'reason': 'We do not bother trying to lookup domains that are not listed in the TLD list.'
    },
    37: {
        'diag'  : 'DNSWARN_INVALID_TLD',
        'was'   : 'DNSWARN_NO_RECORD',
        'reason': 'We do not bother trying to lookup domains that are not listed in the TLD list.'
    },
    38: {
        'diag'  : 'DNSWARN_INVALID_TLD',
        'was'   : 'DNSWARN_NO_RECORD',
        'reason': 'We do not bother trying to lookup domains that are not listed in the TLD list.'
    },
    41: {
        'codes'  : ['RFC5322_DOMAIN_TOO_LONG', 'RFC5322_TOO_LONG'],
        'reason': 'We can return multiple warnings'
    },
    44: {
        'diag': 'ERR_ATEXT_AFTER_QS',
        'codes'  : ['RFC5321_QUOTED_STRING', 'ERR_ATEXT_AFTER_QS'],
        'was'   : 'ERR_EXPECTING_ATEXT',
        'reason': "We saw the quoted string close OK, then detected that there was somethign else."
    },
    51: {
        'codes' : ['ERR_ATEXT_AFTER_QS', 'RFC5321_QUOTED_STRING'],
        'reason': 'We can return multiple diagnosis codes'
    },
    53: {
        'diag'  : 'ERR_ATEXT_AFTER_QS',
        'codes' : ['RFC5321_QUOTED_STRING', 'ERR_ATEXT_AFTER_QS'],
        'was'   : 'ERR_EXPECTING_ATEXT',
        'reason': "We saw the quoted string close OK, then detected that there was somethign else."
    },
    54: {
        'codes' : ['RFC5321_QUOTED_STRING', 'DEPREC_LOCAL_PART'],
        'reason': 'We can return multiple diagnosis codes'
    },
    56: {
        'codes' : ['RFC5321_QUOTED_STRING', 'DEPREC_LOCAL_PART'],
        'reason': 'We can return multiple diagnosis codes'
    },
    58: {
        'addr' : '"test\\&#x2401;"@iana.org',
        'codes': ['RFC5321_QUOTED_STRING', 'DEPREC_QP'],
        'reason': 'the chr(00) is not allowed, so we return a different error'
    },
    59: {
        'codes' : ['RFC5321_QUOTED_STRING', 'RFC5322_LOCAL_TOO_LONG'],
        'reason': 'We can return multiple diagnosis codes'
    },
    60: {
        'codes' : ['RFC5321_QUOTED_STRING', 'RFC5322_LOCAL_TOO_LONG'],
        'reason': 'We can return multiple diagnosis codes'
    },
    61: {
        'diag': 'RFC5322_IPV4_ADDR',
        'was': 'RFC5321_ADDRESS_LITERAL',
        'codes' : ['RFC5321_ADDRESS_LITERAL', 'RFC5322_IPV4_ADDR'],
        'reason': 'new diagnosis code'
    },
    62: {
        'codes' : ['ERR_EXPECTING_ATEXT', 'RFC5321_TLD'],
        'reason': 'We can return multiple diagnosis codes'
    },
    63: {
        'diag'  : 'RFC5322_LIMITED_DOMAIN',
        'was'   : 'RFC5322_DOMAIN_LITERAL',
        'codes' : ['RFC5322_LIMITED_DOMAIN', 'RFC5322_DOMAIN_LITERAL', 'RFC5322_DOMAIN'],
        'reason': 'new diagnosis code'
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

