
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

