import re


class BrokenRange(object):

    def __init__(self, *ranges):
        self._ranges = []
        for r in ranges:
            self.add_range(r)

    def add_range(self, r):
        if isinstance(r, int):
            self._ranges.append((r,))
        if isinstance(r, (list, tuple)):
            self._ranges.append(range(r[0], r[1]))
        if isinstance(r, BrokenRange):
            self._ranges.extend(r._ranges)
        if isinstance(r, range):
            self._ranges.append(r)

    def __iter__(self):
        for r in self._ranges:
            for i in r:
                yield i

    def __contains__(self, item):
        for r in self._ranges:
            if item in r:
                return True
        return False


def broken_range(*ranges):
    return BrokenRange(*ranges)


"""
 * To validate an email address according to RFCs 5321, 5322 and others
 *
 * Copyright © 2008-2011, Dominic Sayers
 * Test schema documentation Copyright © 2011, Daniel Marschall
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 *     - Redistributions of source code must retain the above copyright notice,
 *       this list of conditions and the following disclaimer.
 *     - Redistributions in binary form must reproduce the above copyright notice,
 *       this list of conditions and the following disclaimer in the documentation
 *       and/or other materials provided with the distribution.
 *     - Neither the name of Dominic Sayers nor the names of its contributors may be
 *       used to endorse or promote products derived from this software without
 *       specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * @package    is_email
 * @author    Dominic Sayers <dominic@sayers.cc>
 * @copyright    2008-2011 Dominic Sayers
 * @license    http:#www.opensource.org/licenses/bsd-license.php BSD License
 * @link    http:#www.dominicsayers.com/isemail
 * @version    3.04.1 - Changed my link to http:#isemail.info throughout

Based on the above source, converted to Python by Dan Strohl
"""

'''
# :diagnostic constants start:

# This part of the code is generated using data from test/meta.xml. Beware of making manual alterations
# Categories
ISEMAIL_VALID_CATEGORY = 1
ISEMAIL_DNSWARN = 7
ISEMAIL_RFC5321 = 15
ISEMAIL_CFWS = 31
ISEMAIL_DEPREC = 63
ISEMAIL_RFC5322 = 127
ISEMAIL_ERR = 255

# Diagnoses
# Address is valid
ISEMAIL_VALID = 0
# Address is valid but a DNS check was not successful
ISEMAIL_DNSWARN_NO_MX_RECORD = 5
ISEMAIL_DNSWARN_NO_RECORD = 6
# Address is valid for SMTP but has unusual elements
ISEMAIL_RFC5321_TLD = 9
ISEMAIL_RFC5321_TLDNUMERIC = 10
ISEMAIL_RFC5321_QUOTEDSTRING = 11
ISEMAIL_RFC5321_ADDRESSLITERAL = 12
ISEMAIL_RFC5321_IPV6DEPRECATED = 13
# Address is valid within the message but cannot be used unmodified for the envelope
ISEMAIL_CFWS_COMMENT = 17
ISEMAIL_CFWS_FWS = 18
# Address contains deprecated elements but may still be valid in restricted contexts
ISEMAIL_DEPREC_LOCALPART = 33
ISEMAIL_DEPREC_FWS = 34
ISEMAIL_DEPREC_QTEXT = 35
ISEMAIL_DEPREC_QP = 36
ISEMAIL_DEPREC_COMMENT = 37
ISEMAIL_DEPREC_CTEXT = 38
ISEMAIL_DEPREC_CFWS_NEAR_AT = 49
# The address is only valid according to the broad definition of RFC 5322. It is otherwise invalid.
ISEMAIL_RFC5322_DOMAIN = 65
ISEMAIL_RFC5322_TOOLONG = 66
ISEMAIL_RFC5322_LOCAL_TOOLONG = 67
ISEMAIL_RFC5322_DOMAIN_TOOLONG = 68
ISEMAIL_RFC5322_LABEL_TOOLONG = 69
ISEMAIL_RFC5322_DOMAINLITERAL = 70
ISEMAIL_RFC5322_DOMLIT_OBSDTEXT = 71
ISEMAIL_RFC5322_IPV6_GRPCOUNT = 72
ISEMAIL_RFC5322_IPV6_2X2XCOLON = 73
ISEMAIL_RFC5322_IPV6_BADCHAR = 74
ISEMAIL_RFC5322_IPV6_MAXGRPS = 75
ISEMAIL_RFC5322_IPV6_COLONSTRT = 76
ISEMAIL_RFC5322_IPV6_COLONEND = 77
# Address is invalid for any purpose
ISEMAIL_ERR_EXPECTING_DTEXT = 129
ISEMAIL_ERR_NOLOCALPART = 130
ISEMAIL_ERR_NODOMAIN = 131
ISEMAIL_ERR_CONSECUTIVEDOTS = 132
ISEMAIL_ERR_ATEXT_AFTER_CFWS = 133
ISEMAIL_ERR_ATEXT_AFTER_QS = 134
ISEMAIL_ERR_ATEXT_AFTER_DOMLIT = 135
ISEMAIL_ERR_EXPECTING_QPAIR = 136
ISEMAIL_ERR_EXPECTING_ATEXT = 137
ISEMAIL_ERR_EXPECTING_QTEXT = 138
ISEMAIL_ERR_EXPECTING_CTEXT = 139
ISEMAIL_ERR_BACKSLASHEND = 140
ISEMAIL_ERR_DOT_START = 141
ISEMAIL_ERR_DOT_END = 142
ISEMAIL_ERR_DOMAINHYPHENSTART = 143
ISEMAIL_ERR_DOMAINHYPHENEND = 144
ISEMAIL_ERR_UNCLOSEDQUOTEDSTR = 145
ISEMAIL_ERR_UNCLOSEDCOMMENT = 146
ISEMAIL_ERR_UNCLOSEDDOMLIT = 147
ISEMAIL_ERR_FWS_CRLF_X2 = 148
ISEMAIL_ERR_FWS_CRLF_END = 149
ISEMAIL_ERR_CR_NO_LF = 150
'''
# :diagnostic constants start:

# This part of the code is generated using data from test/meta.xml. Beware of making manual alterations
# Categories

ISEMAIL_VALID_CATEGORY  = 'VALID_CATEGORY'
ISEMAIL_DNSWARN  = 'DNSWARN'
ISEMAIL_RFC5321  = 'RFC5321'
ISEMAIL_CFWS  = 'CFWS'
ISEMAIL_DEPREC  = 'DEPREC'
ISEMAIL_RFC5322  = 'RFC5322'
ISEMAIL_ERR  = 'ERR'

# Diagnoses
# Address is valid
ISEMAIL_VALID  = 'VALID'
# Address is valid but a DNS check was not successful
ISEMAIL_DNSWARN_NO_MX_RECORD  = 'DNSWARN_NO_MX_RECORD'
ISEMAIL_DNSWARN_NO_RECORD  = 'DNSWARN_NO_RECORD'
# Address is valid for SMTP but has unusual elements
ISEMAIL_RFC5321_TLD  = 'RFC5321_TLD'
ISEMAIL_RFC5321_TLD_NUMERIC  = 'RFC5321_TLD_NUMERIC'
ISEMAIL_RFC5321_QUOTED_STRING  = 'RFC5321_QUOTED_STRING'
ISEMAIL_RFC5321_ADDRESS_LITERAL  = 'RFC5321_ADDRESS_LITERAL'
ISEMAIL_RFC5321_IPV6_DEPRECATED  = 'RFC5321_IPV6_DEPRECATED'
ISEMAIL_RFC5321_UNNEEDED_QUOTED_PAIR = 'RFC5321_UNNEEDED_QUOTED_PAIR'

# Address is valid within the message but cannot be used unmodified for the envelope
ISEMAIL_CFWS_COMMENT  = 'CFWS_COMMENT'
ISEMAIL_CFWS_FWS  = 'CFWS_FWS'
# Address contains deprecated elements but may still be valid in restricted contexts
ISEMAIL_DEPREC_LOCAL_PART  = 'DEPREC_LOCAL_PART'
ISEMAIL_DEPREC_FWS  = 'DEPREC_FWS'
ISEMAIL_DEPREC_QTEXT  = 'DEPREC_QTEXT'
ISEMAIL_DEPREC_QP  = 'DEPREC_QP'
ISEMAIL_DEPREC_COMMENT  = 'DEPREC_COMMENT'
ISEMAIL_DEPREC_CTEXT  = 'DEPREC_CTEXT'
ISEMAIL_DEPREC_CFWS_NEAR_AT  = 'DEPREC_CFWS_NEAR_AT'
# The address is only valid according to the broad definition of RFC 5322. It is otherwise invalid.
ISEMAIL_RFC5322_DOMAIN  = 'RFC5322_DOMAIN'
ISEMAIL_RFC5322_TOO_LONG  = 'RFC5322_TOO_LONG'
ISEMAIL_RFC5322_LOCAL_TOO_LONG  = 'RFC5322_LOCAL_TOO_LONG'
ISEMAIL_RFC5322_DOMAIN_TOO_LONG  = 'RFC5322_DOMAIN_TOO_LONG'
ISEMAIL_RFC5322_LABEL_TOO_LONG  = 'RFC5322_LABEL_TOO_LONG'
ISEMAIL_RFC5322_DOMAIN_LITERAL  = 'RFC5322_DOMAIN_LITERAL'
ISEMAIL_RFC5322_DOM_LIT_OBS_DTEXT  = 'RFC5322_DOM_LIT_OBS_DTEXT'
ISEMAIL_RFC5322_IPV6_GRP_COUNT  = 'RFC5322_IPV6_GRP_COUNT'
ISEMAIL_RFC5322_IPV6_2X2XCOLON  = 'RFC5322_IPV6_2X2XCOLON'
ISEMAIL_RFC5322_IPV6_BAD_CHAR  = 'RFC5322_IPV6_BAD_CHAR'
ISEMAIL_RFC5322_IPV6_MAX_GRPS  = 'RFC5322_IPV6_MAX_GRPS'
ISEMAIL_RFC5322_IPV6_COLON_STRT  = 'RFC5322_IPV6_COLON_STRT'
ISEMAIL_RFC5322_IPV6_COLON_END  = 'RFC5322_IPV6_COLON_END'

ISEMAIL_ERR_EXPECTING_DTEXT  = 'ERR_EXPECTING_DTEXT'
ISEMAIL_ERR_NO_LOCAL_PART  = 'ERR_NO_LOCAL_PART'
ISEMAIL_ERR_NO_DOMAIN  = 'ERR_NO_DOMAIN'
ISEMAIL_ERR_CONSECUTIVE_DOTS  = 'ERR_CONSECUTIVE_DOTS'
ISEMAIL_ERR_ATEXT_AFTER_CFWS  = 'ERR_ATEXT_AFTER_CFWS'
ISEMAIL_ERR_ATEXT_AFTER_QS  = 'ERR_ATEXT_AFTER_QS'
ISEMAIL_ERR_ATEXT_AFTER_DOMLIT  = 'ERR_ATEXT_AFTER_DOMLIT'
ISEMAIL_ERR_EXPECTING_QPAIR  = 'ERR_EXPECTING_QPAIR'
ISEMAIL_ERR_EXPECTING_ATEXT  = 'ERR_EXPECTING_ATEXT'
ISEMAIL_ERR_EXPECTING_QTEXT  = 'ERR_EXPECTING_QTEXT'
ISEMAIL_ERR_EXPECTING_CTEXT  = 'ERR_EXPECTING_CTEXT'
ISEMAIL_ERR_BACKSLASH_END  = 'ERR_BACKSLASH_END'
ISEMAIL_ERR_DOT_START  = 'ERR_DOT_START'
ISEMAIL_ERR_DOT_END  = 'ERR_DOT_END'
ISEMAIL_ERR_DOMAIN_HYPHEN_START  = 'ERR_DOMAIN_HYPHEN_START'
ISEMAIL_ERR_DOMAIN_HYPHEN_END  = 'ERR_DOMAIN_HYPHEN_END'
ISEMAIL_ERR_UNCLOSED_QUOTED_STR  = 'ERR_UNCLOSED_QUOTED_STR'
ISEMAIL_ERR_UNCLOSED_COMMENT  = 'ERR_UNCLOSED_COMMENT'
ISEMAIL_ERR_UNCLOSED_DOM_LIT  = 'ERR_UNCLOSED_DOM_LIT'
ISEMAIL_ERR_FWS_CRLF_X2  = 'ERR_FWS_CRLF_X2'
ISEMAIL_ERR_FWS_CRLF_END  = 'ERR_FWS_CRLF_END'
ISEMAIL_ERR_CR_NO_LF  = 'ERR_CR_NO_LF'
# End of generated code
# :diagnostic constants end:


# function control
ISEMAIL_THRESHOLD = 16

# Email components
ISEMAIL_COMPONENT_LOCALPART = 0
ISEMAIL_COMPONENT_DOMAIN = 1

# Email context
ISEMAIL_COMPONENT_LITERAL = 2
ISEMAIL_CONTEXT_COMMENT = 3
ISEMAIL_CONTEXT_FWS = 4
ISEMAIL_CONTEXT_QUOTEDSTRING = 5
ISEMAIL_CONTEXT_QUOTEDPAIR = 6

ISEMAIL_EXCLUDE_FROM_PART = [ISEMAIL_CONTEXT_COMMENT, ISEMAIL_CONTEXT_FWS]
ISEMAIL_ENCLOSED_CONTEXT = [ISEMAIL_COMPONENT_LITERAL, ISEMAIL_CONTEXT_COMMENT,
                            ISEMAIL_CONTEXT_FWS, ISEMAIL_CONTEXT_QUOTEDSTRING,
                            ISEMAIL_CONTEXT_QUOTEDPAIR]


# Miscellaneous string constants
ISEMAIL_STRING_AT = '@'
ISEMAIL_STRING_BACKSLASH = '\\'
ISEMAIL_STRING_DOT = '.'
ISEMAIL_STRING_DQUOTE = '"'
ISEMAIL_STRING_OPENPARENTHESIS = '('
ISEMAIL_STRING_CLOSEPARENTHESIS = ')'
ISEMAIL_STRING_OPENSQBRACKET = '['
ISEMAIL_STRING_CLOSESQBRACKET = ']'
ISEMAIL_STRING_HYPHEN = '-'
ISEMAIL_STRING_COLON = ':'
ISEMAIL_STRING_DOUBLECOLON = '::'
ISEMAIL_STRING_SP = ' '
ISEMAIL_STRING_HTAB = "\t"
ISEMAIL_WSP = ' \t'
ISEMAIL_STRING_CR = "\r"
ISEMAIL_STRING_LF = "\n"
ISEMAIL_STRING_IPV6TAG = 'ipv6:'
# US-ASCII visible characters not valid for atext (http:#tools.ietf.org/html/rfc5322#section-3.2.3)
ISEMAIL_STRING_SPECIALS = '()<>[]:;@\\,."'


# Character Ranges
ISEMAIL_RANGE_OBS_NO_WS_CTL = broken_range((1, 8), 11, 12, (14, 31), 127)
ISEMAIL_RANGE_CTEXT = broken_range((33, 39), (42, 91), (93, 126), ISEMAIL_RANGE_OBS_NO_WS_CTL)
ISEMAIL_RANGE_DTEXT = broken_range((33,126))
ISEMAIL_RANGE_QTEXT = broken_range(33, (35,91), (93,126), ISEMAIL_RANGE_OBS_NO_WS_CTL)

# State Flags
ISEMAIL_ELEMENT_BEG_ALL = 0
ISEMAIL_ELEMENT_BEG_ELEMENT = 1
ISEMAIL_ELEMENT_IN_ELEMENT = 2

# Element types
ISEMAIL_ELEMENT_LOCAL_DOT_ATOM = 0

ISEMAIL_DOMAIN_LIT_NONE = 0
ISEMAIL_DOMAIN_LIT_UNK = 1
ISEMAIL_DOMAIN_LIT_IPV4 = 4
ISEMAIL_DOMAIN_LIT_IPV6 = 6
ISEMAIL_DOMAIN_LIT_GEN = 99

ISEMAIL_IP_REGEX = re.compile(r'(?P<address>(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
ISEMAIL_IP_REGEX_GOOD_CHAR = re.compile(r'^[0-9A-Fa-f]{0,4}$')

'''
 * Check that an email address conforms to RFCs 5321, 5322 and others
 *
 * As of Version 3.0, we are now distinguishing clearly between a Mailbox
 * as defined by RFC 5321 and an addr-spec as defined by RFC 5322. Depending
 * on the context, either can be regarded as a valid email address. The
 * RFC 5321 Mailbox specification is more restrictive (comments, white space
 * and obsolete forms are not allowed)
 *
 * @param string    email        The email address to check
 * @param boolean    checkDNS    If True then a DNS check for MX records will be made
 * @param mixed        errorlevel    Determines the boundary between valid and invalid addresses.
 *                     Status codes above this number will be returned as-is,
 *                     status codes below will be returned as ISEMAIL_VALID. Thus the
 *                     calling program can simply look for ISEMAIL_VALID if it is
 *                     only interested in whether an address is valid or not. The
 *                     errorlevel will determine how "picky" is_email() is about
 *                     the address.
 *
 *                     If omitted or passed as False then is_email() will return
 *                     True or False rather than an integer error or warning.
 *
 *                     NB Note the difference between errorlevel = False and
 *                     errorlevel = 0
 * @param array        parsedata    If passed, returns the parsed address components
 '''
# /*.mixed. function is_email(email, checkDNS = False, errorlevel = False, &parsedata = array()) {


"""
Definitions:

Part (local/domain): everything before/after the "@"
DotAtoms = parts between dots (in hello.dan@example.com, labels are 'hello', 'dan', 'example', and 'com'
Elements = parts of the address that are distinguishable (comments, literals, dot_atoms, etc)
Context = Current element we are working on.
Atom = characters in a string

Response Data Includes:

raw_email = (this is a comment)"literal"/xemail@(another comment)hello.(comment again)com
local_part =
    raw = (this is a comment)"literal"/xemail
    flags = [('has comment', 0), ('has literal',14), ('has quoted_char',20)]
    valid = True
    max_message = 'has comment'
domain_part =
    raw = (another comment)hello.(comment again)com
    flags = [('has comment',30),('has comment', 40), ('full fqdn',45)]
    valid = True
    max_message = 'has_comment'
valid = True
max_message = has_comment
"""

class ValidatedPart(object):
    def __init__(self):
        self.raw = []
        self.clean = []
        self.flags = []
        self.valid = False
        self.max_flag = 0

class ValidatedEmail(object):
    def __init__(self, email, flag_data=None):
        self.raw = email
        self.local = ValidatedPart()
        self.domain = ValidatedPart()
        self.flag_data = flag_data
        self.valid = False
        self.max_flag = 0
        self.part = self.local


class ElementClass(object):
    def __init__(self, parent, element_type, start_pos):
        self.atoms = []
        self.element_type = element_type
        self.start_pos = start_pos
        self.cur_pos = start_pos
        self.parent = parent
        # self.length = 0
        # self.elements = 0

    def __iadd__(self, item):
        # self.length += 1
        # self.parent.length += 1
        # self.parent.element_len += 1
        self.atoms.append(item)

    def __str__(self):
        return ''.join(self.atoms)

    def __bool__(self):
        return bool(self.atoms)

    def __getitem__(self, item):
        return self.atoms[item]

    def __len__(self):
        return len(self.atoms)


"""
class FlagClass(object):
    default_priority = 0
    max_priority = 0

    def __init__(self, parent, flag_data=None):
        self.flag_data = flag_data or {}
        self.flags = []
        self.parent = parent

    def add(self, flag, position=None):
        position = position or self.parent.position
        self.flags = (flag, position)

        if flag in self.flag_data:
            self.max_priority = max(self.max_priority, self.flag_data[flag]['priority'])
        else:
            self.max_priority = max(self.max_priority, self.default_priority)

    def __iadd__(self, flag):
        self.add(flag)

class PartClass(object):
    def __init__(self, parent, flag_data=None, part_name=None):
        self.parent = parent
        self.raw = []
        self.part_name = part_name
        self.flags = FlagClass(parent, flag_data)
        self.elements = []
        self.atoms = []
        self.element_stack = []
        self.element = None
        self.element_prior = self.new_element(self.part_name)

    @property
    def max_flag(self):
        return self.flags.max_priority

    def add_flag(self, flag, position=None):
        position = position or self.element.start_pos
        self.flags.add(flag, position)

    def push_element(self, element_type):
        self.element_stack.append(self.element)
        self.element_prior = self.element
        self.element = self.new_element(element_type)

    def pop_element(self):
        self.element_prior = self.element
        self.element = self.element_stack.pop()

    def new_element(self, element_type):
        tmp_element = ElementClass(self, element_type, self.parent.position)
        self.elements.append(tmp_element)
        return tmp_element

    def add_flag_by_state(self, beg_all_elements=None, beg_cur_element=None,
                          in_element=None, anywhere=None, position=None):

        if anywhere is not None:
            self.add_flag(anywhere, position)

        if len(self.elements) == 1 and len(self.element) == 0:
            if beg_all_elements is not None:
                self.add_flag(beg_all_elements, position)
        elif len(self.element) == 0:
            if beg_cur_element is not None:
                self.add_flag(beg_cur_element, position)
        else:
            if in_element is not None:
                self.add_flag(in_element, position)
            return True

        return False

    def add(self, item=None, flag=None, skip=False):

        if flag is not None:
            self.add_flag(flag)
        if item is not None:
            self.raw.append(item)
            if not skip:
                self.element += item
                if self.element.element_type not in ISEMAIL_EXCLUDE_FROM_PART:
                    self.atoms.append(item)

    @property
    def context(self):
        return self.element.element_type

"""
        
class CheckEmailDataClass(object):
    def __init__(self, raw_email, flag_data):
        self.response_data = ValidatedEmail(raw_email, flag_data)
        # self.local_part = PartClass(self, flag_data, ISEMAIL_COMPONENT_LOCALPART)
        # self.domain_part = PartClass(self, flag_data, ISEMAIL_COMPONENT_DOMAIN)

        self.position = 0
        self.flag_data = flag_data
        self.default_flag_priority = 0
        # self.part_name = part_name
        # self.flags = FlagClass(parent, flag_data)
        self.elements = []
        self.atoms = []
        self.element_stack = []
        self.element = None
        self.element_prior = self.new_element(ISEMAIL_COMPONENT_LOCALPART)

        self.component = ISEMAIL_COMPONENT_LOCALPART
        # self.responses = []
        # self.response_positions = []
        # self.element_stack = []
        # self.element_len = 0
        # self.element_count = 0
        # self.element = None

        self.raw_email = raw_email
        self.raw_length = len(raw_email)
        # self.local_part = []
        # self.domain_part = []
        # self.domain_literal = 0
        # self.display_name = ''
        # self.length = 0
        # self.part_types = {}
        # self.part = self.local_part
        # self.context_prior = -1
 

    @property
    def token(self):
        return self.raw_email[self.position]
    
    @property
    def prior_token(self):
        return self.raw_email[self.position-1]
    
    @property
    def is_local_part(self):
        return self.component == ISEMAIL_COMPONENT_LOCALPART

    @property
    def in_enclosed_element(self):
        return self.context in ISEMAIL_ENCLOSED_CONTEXT

    def set_at(self):
        self.response_data.part = self.response_data.domain
        self.elements = []
        self.element_stack = []
        self.element = None
        self.element_prior = self.new_element(ISEMAIL_COMPONENT_DOMAIN)
        self.component = ISEMAIL_COMPONENT_DOMAIN

    def add_flag(self, flag, position=None):
        """
        :param str flag: the flag to set
        :param position: if None, will set position a the beginning of the current element
            otherwise will set position for flag
        """
        position = position or self.element.start_pos

        self.response_data.part.flags.append = (flag, position)

        try:            
            self.response_data.part.max_flag = max(self.response_data.part.max_flag, self.flag_data[flag]['priority'])
        except KeyError:
            self.response_data.part.max_flag = max(self.response_data.part.max_flag, self.default_flag_priority)

    def push_element(self, element_type):
        self.element_stack.append(self.element)
        self.element_prior = self.element
        self.element = self.new_element(element_type)

    def pop_element(self):
        self.element_prior = self.element
        self.element = self.element_stack.pop()

    def new_element(self, element_type):
        tmp_element = ElementClass(self, element_type, self.position)
        self.elements.append(tmp_element)
        return tmp_element

    def add_flag_by_state(self, beg_all_elements=None, beg_cur_element=None,
                          in_element=None, anywhere=None, position=None):

        if anywhere is not None:
            self.add_flag(anywhere, position)

        if len(self.elements) == 1 and len(self.element) == 0:
            if beg_all_elements is not None:
                self.add_flag(beg_all_elements, position)
        elif len(self.element) == 0:
            if beg_cur_element is not None:
                self.add_flag(beg_cur_element, position)
        else:
            if in_element is not None:
                self.add_flag(in_element, position)
            return True

        return False

    def add_token(self, token=None, skip=False):
        token = token or self.token
        self.response_data.part.raw.append(token)
        if not skip:
            self.element += token
            if self.element.element_type not in ISEMAIL_EXCLUDE_FROM_PART:
                self.response_data.part.clean.append(token)

    @property
    def context(self):
        return self.element.element_type

    @property
    def local_str(self):
        return ''.join(self.response_data.local.raw)

    @property
    def domain_str(self):
        return ''.join(self.response_data.domain.raw)

    def __str__(self):
        return '%s@%s' % (self.local_str, self.domain_str)


def check_email(email_string, flag_data=None):
    data = CheckEmailDataClass(email_string, flag_data=flag_data)





"""

class CheckEmailDataClass(object):
    def __init__(self, raw_email, flag_data):
        self.response_data = ValidatedEmail()
        # self.local_part = PartClass(self, flag_data, ISEMAIL_COMPONENT_LOCALPART)
        # self.domain_part = PartClass(self, flag_data, ISEMAIL_COMPONENT_DOMAIN)

        self.position = 0
        self.raw = []
        
        # self.part_name = part_name
        # self.flags = FlagClass(parent, flag_data)
        self.elements = []
        self.atoms = []
        self.element_stack = []
        self.element = None
        self.element_prior = self.new_element(self.part_name)

        # self.component = ISEMAIL_COMPONENT_LOCALPART
        # self.responses = []
        # self.response_positions = []
        # self.element_stack = []
        # self.element_len = 0
        # self.element_count = 0
        # self.element = None

        self.raw_email = raw_email
        # self.local_part = []
        # self.domain_part = []
        # self.domain_literal = 0
        # self.display_name = ''
        # self.length = 0
        # self.part_types = {}
        # self.part = self.local_part
        # self.context_prior = -1

        self.part = self.local_part

    @property
    def token(self):
        return self.raw[self.position]

    @property
    def element(self):
        return self.part.element
    
    @property
    def component(self):
        return self.part.part_name

    @property
    def is_local_part(self):
        return self.part.part_name == ISEMAIL_COMPONENT_LOCALPART

    @property
    def in_enclosed_element(self):


    @property
    def max_flag(self):
        return max(self.local_part.max_flag, self.domain_part.max_flag)

    def set_at(self):
        self.part = self.domain_part

    def push_element(self, element_type):
        self.part.push_element(element_type)

    def pop_element(self):
        self.part.pop_element()

    def new_element(self, element_type):
        self.part.new_element(element_type)

    @property
    def elements(self):
        return self.part.elements

    @property
    def context(self):
        return self.part.element.element_type
    '''
    def flag_by_state(self, response_dict):
        tmp_state = self.state
        if tmp_state in response_dict:
            self.add_response(response_dict[tmp_state])
        return tmp_state
    '''
    '''
    def inc_elements(self):
        self.element_count += 1
        self.element_len = 0
    '''

    def add_flag_by_state(self, *args, **kwargs):
        return self.part.add_flag_by_state(*args, **kwargs)

    @property
    def local_str(self):
        return ''.join(self.local_part.raw)

    @property
    def domain_str(self):
        return ''.join(self.domain_part.raw)

    def add(self, item=None, flag=None, skip=False):
        self.part.add(item=item, flag=flag, skip=skip)

    def __iadd__(self, item):
        self.part += item

    def __str__(self):
        return '%s@%s' % (self.local_str, self.domain_str)

    def __getitem__(self, item):
        return self.elements[item]
    '''
    def __init__(self, parent, flag_data=None, part_name=None):
        self.parent = parent
        self.raw = []
        self.part_name = part_name
        self.flags = FlagClass(parent, flag_data)
        self.elements = []
        self.atoms = []
        self.element_stack = []
        self.element = None
        self.element_prior = self.new_element(self.part_name)

    @property
    def max_flag(self):
        return self.flags.max_priority

    def add_flag(self, flag, position=None):
        position = position or self.element.start_pos
        self.flags.add(flag, position)

    def push_element(self, element_type):
        self.element_stack.append(self.element)
        self.element_prior = self.element
        self.element = self.new_element(element_type)

    def pop_element(self):
        self.element_prior = self.element
        self.element = self.element_stack.pop()

    def new_element(self, element_type):
        tmp_element = ElementClass(self, element_type, self.parent.position)
        self.elements.append(tmp_element)
        return tmp_element

    def add_flag_by_state(self, beg_all_elements=None, beg_cur_element=None,
                          in_element=None, anywhere=None, position=None):

        if anywhere is not None:
            self.add_flag(anywhere, position)

        if len(self.elements) == 1 and len(self.element) == 0:
            if beg_all_elements is not None:
                self.add_flag(beg_all_elements, position)
        elif len(self.element) == 0:
            if beg_cur_element is not None:
                self.add_flag(beg_cur_element, position)
        else:
            if in_element is not None:
                self.add_flag(in_element, position)
            return True

        return False

    def add(self, item=None, flag=None, skip=False):

        if flag is not None:
            self.add_flag(flag)
        if item is not None:
            self.raw.append(item)
            if not skip:
                self.element += item
                if self.element.element_type not in ISEMAIL_EXCLUDE_FROM_PART:
                    self.atoms.append(item)

    @property
    def context(self):
        return self.element.element_type
    '''
    '''
    def __len__(self):
        if self.domain_part:
            return self.length + 1
        else:
            return self.length

    def __int__(self):
        return self.max_response()

    '''

"""



"""
class AddressClass(object):
    def __init__(self, raw_email):

        self.component = ISEMAIL_COMPONENT_LOCALPART
        self.responses = []
        self.response_positions = []
        self.element_stack = []
        self.element_len = 0
        self.element_count = 0
        self.element = None

        self.raw_email = raw_email
        self.local_part = []
        self.domain_part = []
        self.domain_literal = 0
        self.display_name = ''
        self.length = 0
        self.part_types = {}
        self.part = self.local_part
        self.context_prior = -1

    def set_at(self):
        self.component = ISEMAIL_COMPONENT_DOMAIN
        self.element_count = 0
        self.element_len = 0
        self.element_stack = []

    def max_response(self):
        if self.responses:
            return max(self.responses)
        else:
            return ISEMAIL_VALID

    def push_element(self, element_type):
        self.element_stack.append(self.element)
        self.context_prior = int(self.context)
        self.element = self.new_element(element_type)

    def pop_element(self):
        self.context_prior = int(self.context)
        self.element = self.element_stack.pop()

    def new_element(self, element_type):
        tmp_element = ElementClass(self, element_type)
        self.elements.append(tmp_element)
        self.inc_elements()
        return tmp_element

    @property
    def elements(self):
        if self.component == ISEMAIL_COMPONENT_DOMAIN:
            return self.domain_part
        else:
            return self.local_part

    @property
    def context(self):
        return self.element.element_type

    @property
    def state(self):
        if self.element_count == 0:
            return ISEMAIL_ELEMENT_BEG_ALL
        elif self.element_len == 0:
            return ISEMAIL_ELEMENT_BEG_ELEMENT
        else:
            return ISEMAIL_ELEMENT_IN_ELEMENT

    def response_by_state(self, response_dict):
        tmp_state = self.state
        if tmp_state in response_dict:
            self.add_response(response_dict[tmp_state])
        return tmp_state

    def inc_elements(self):
        self.element_count += 1
        self.element_len = 0

    def add_response(self, response_code, position=None):
        self.responses.append(response_code)
        if position is None:
            position = self.length
        if isinstance(position, str):
            if position[0] == '-':
                position = self.length - len(position)
            elif position[0] == '+':
                position = self.length + len(position)
        self.response_positions.append(position)


    @property
    def local_str(self):
        return ''.join(self.local_part)

    @property
    def domain_str(self):
        return ''.join(self.domain_part)

    def __iadd__(self, item):
        if isinstance(item, int):
            self.add_response(item)
        else:
            self.element += item

    def __str__(self):
        return '%s@%s' % (self.local_str, self.domain_str)

    def __getitem__(self, item):
        return self.elements[item]

    def __len__(self):
        if self.domain_part:
            return self.length + 1
        else:
            return self.length

    def __int__(self):
        return self.max_response()

"""
"""
Response Data Includes:

raw_email = (this is a comment)"literal"/xemail@(another comment)hello.(comment again)com
local_part =
    raw = (this is a comment)"literal"/xemail
    flags = [('has comment', 0), ('has literal',14), ('has quoted_char',20)]
    valid = True
    max_message = 'has comment'
domain_part =
    raw = (another comment)hello.(comment again)com
    flags = [('has comment',30),('has comment', 40), ('full fqdn',45)]
    valid = True
    max_message = 'has_comment'
valid = True
max_message = has_comment
"""

'''
def check_domain_lit(domain_lit_):
                tmp_max = data.max_response()
                if tmp_max < ISEMAIL_DEPREC:

                    # Could be a valid RFC 5321 address literal, so let's check
                    #
                    # http:#tools.ietf.org/html/rfc5321#section-4.1.2
                    #   address-literal  = "[" ( IPv4-address-literal /
                    #                    IPv6-address-literal /
                    #                    General-address-literal ) "]"
                    #                    ; See Section 4.1.3
                    #
                    # http:#tools.ietf.org/html/rfc5321#section-4.1.3
                    #   IPv4-address-literal  = Snum 3("."  Snum)
                    #
                    #   IPv6-address-literal  = "IPv6:" IPv6-addr
                    #
                    #   General-address-literal  = Standardized-tag ":" 1*dcontent
                    #
                    #   Standardized-tag  = Ldh-str
                    #                     ; Standardized-tag MUST be specified in a
                    #                     ; Standards-Track RFC and registered with IANA
                    #
                    #   dcontent       = %d33-90 / ; Printable US-ASCII
                    #                  %d94-126 ; excl. "[", "\", "]"
                    #
                    #   Snum           = 1*3DIGIT
                    #                  ; representing a decimal integer
                    #                  ; value in the range 0 through 255
                    #
                    #   IPv6-addr      = IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp
                    #
                    #   IPv6-hex       = 1*4HEXDIG
                    #
                    #   IPv6-full      = IPv6-hex 7(":" IPv6-hex)
                    #
                    #   IPv6-comp      = [IPv6-hex *5(":" IPv6-hex)] "::"
                    #                  [IPv6-hex *5(":" IPv6-hex)]
                    #                  ; The "::" represents at least 2 16-bit groups of
                    #                  ; zeros.  No more than 6 groups in addition to the
                    #                  ; "::" may be present.
                    #
                    #   IPv6v4-full    = IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal
                    #
                    #   IPv6v4-comp    = [IPv6-hex *3(":" IPv6-hex)] "::"
                    #                  [IPv6-hex *3(":" IPv6-hex) ":"]
                    #                  IPv4-address-literal
                    #                  ; The "::" represents at least 2 16-bit groups of
                    #                  ; zeros.  No more than 4 groups in addition to the
                    #                  ; "::" and IPv4-address-literal may be present.
                    #
                    # is_email() author's note: We can't use ip2long() to validate
                    # IPv4 addresses because it accepts abbreviated addresses
                    # (xxx.xxx.xxx), expanding the last group to complete the address.
                    # filter_var() validates IPv6 address inconsistently (up to PHP 5.3.3
                    # at least) -- see http:#bugs.php.net/bug.php?id=53236 for example

                    max_groups = 8
                    matchesIP = []
                    index = False
                    addressliteral = str(data.element)

                    # Extract IPv4 part from the end of the address-literal (if there is one)

                    address_match = IP_REGEX.search(addressliteral)
                    # :TODO Figure this out and fix!!!
                    if address_match is not None:
                        addressliteral = address_match.group('address') + '0.0'


                        # if (preg_match(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)' = addressliteral, matchesIP) > 0)
                        #    index = strrpos(addressliteral, matchesIP[0]
                        #    if index != 0:
                        #        addressliteral = substr(addressliteral, 0, index) + '0:0' # Convert IPv4 part to IPv6 format for further testing
                        # }


                    if index == 0:
                        # Nothing there except a valid IPv4 address, so...
                        return_status.append(ISEMAIL_RFC5321_ADDRESSLITERAL)
                    elif ISEMAIL_STRING_IPV6TAG in addressliteral.lower():
                        return_status.append(ISEMAIL_RFC5322_DOMAINLITERAL)
                    else:
                        IPv6 = addressliteral[5:]
                        matchesIP = IPv6.split(ISEMAIL_STRING_COLON)    # Revision 2.7: Daniel Marschall's new IPv6 testing strategy
                        groupCount = len(matchesIP)
                        index = IPv6.find(ISEMAIL_STRING_DOUBLECOLON)

                        if index > -1:
                            # We need exactly the right number of groups
                            if groupCount != max_groups:
                                return_status.append(ISEMAIL_RFC5322_IPV6_GRPCOUNT)
                        else:
                            if index != IPv6.find(ISEMAIL_STRING_DOUBLECOLON):
                                return_status.append(ISEMAIL_RFC5322_IPV6_2X2XCOLON)
                            else:
                                if index == 0 or index == (len(IPv6) - 2):
                                    max_groups += 1    # RFC 4291 allows :: at the start or end of an address with 7 other groups in addition

                                if groupCount > max_groups:
                                    return_status.append(ISEMAIL_RFC5322_IPV6_MAXGRPS)
                                elif groupCount == max_groups:
                                    return_status.append(ISEMAIL_RFC5321_IPV6DEPRECATED)    # Eliding a single "::"

                        # Revision 2.7: Daniel Marschall's new IPv6 testing strategy
                        if IPv6[0] == ISEMAIL_STRING_COLON and IPv6[1] != ISEMAIL_STRING_COLON:
                            return_status.append(ISEMAIL_RFC5322_IPV6_COLONSTRT)    # Address starts with a single colon
                        elif IPv6[-1] == ISEMAIL_STRING_COLON and IPv6[-2] != ISEMAIL_STRING_COLON:
                            return_status.append(ISEMAIL_RFC5322_IPV6_COLONEND)    # Address ends with a single colon
                        elif not IP_REGEX_GOOD_CHAR.match(matchesIP):
                            # elif (count(preg_grep('/^[0-9A-Fa-f]{0,4}/ = matchesIP, PREG_GREP_INVERT)) !== 0)
                            return_status.append(ISEMAIL_RFC5322_IPV6_BADCHAR)    # Check for unmatched characters
                        else:
                            return_status.append(ISEMAIL_RFC5321_ADDRESSLITERAL)
                else:
                    return_status.append(ISEMAIL_RFC5322_DOMAINLITERAL)


                parsedata[ISEMAIL_COMPONENT_DOMAIN] += token
                atomlist[ISEMAIL_COMPONENT_DOMAIN][element_count] += token
                element_len += 1
                context_prior = context
                context = context_stack.pop()
'''

class Old_EmailCheck(object):
    def __init__(self,
                 dns_checker=None,
                 addr_lit_checker=None,
                 return_data_object=None,
                 fail_above=None,
                 flag_data=None
                 ):
        """
        :param DnsChecker dns_checker: if none will use the default of
        :param AddrLitChecker addr_lit_checker: if None will use the default of
        :param return_data_object: if None will use the default of
        """
        self.flag_data = flag_data or {}
        self.dns_checker = dns_checker
        self.addr_lit_checker = addr_lit_checker
        self.return_data_object = return_data_object
        self.fail_above = fail_above or ISEMAIL_VALID


    def _parse_email(self, data):
        pass






    def _parse_quoted_pair(self, data):
        data.push_element(ISEMAIL_CONTEXT_QUOTEDPAIR)
        data.add_token()

        if data.context == ISEMAIL_COMPONENT_LITERAL:
            data.add_flag(ISEMAIL_RFC5322_DOM_LIT_OBS_DTEXT)


        # -------------------------------------------------------------
        # Quoted pair
        # -------------------------------------------------------------
        # http:#tools.ietf.org/html/rfc5322#section-3.2.1
        #   quoted-pair = ("\" (VCHAR / WSP)) / obs-qp
        #
        #   VCHAR = %d33-126             visible (printing) characters
        #   WSP = SP / HTAB            white space
        #
        #   obs-qp = "\" (%d0 / obs-NO-WS-CTL / LF / CR)
        #
        #   obs-NO-WS-CTL = %d1-8 /             US-ASCII control
        #                       %d11 /               characters that do not
        #                       %d12 /               include the carriage
        #                       %d14-31 /            return, line feed, and
        #                       %d127                white space characters
        #
        # i.e. obs-qp = "\" (%d0-8, %d10-31 / %d127)
        data.position += 1
        ord_chr = ord(data.token)
    
        if ord_chr not in range(33, 127) or ord_chr not in ISEMAIL_WSP:
            data.add_flag(ISEMAIL_ERR_EXPECTING_QPAIR)  # Fatal error
            return
        elif ord_chr in ISEMAIL_RANGE_OBS_NO_WS_CTL:
            data.add_flag(ISEMAIL_DEPREC_QP)

        # At this point we know where this qpair occurred so
        # we could check to see if the character actually
        # needed to be quoted at all.
        # http:#tools.ietf.org/html/rfc5321#section-4.1.2
        #   the sending system SHOULD transmit the
        #   form that uses the minimum quoting possible.
        
        data.pop_element()
    
        if data.context == ISEMAIL_COMPONENT_LITERAL and ord_chr in ISEMAIL_RANGE_DTEXT:
            data.add_flag(ISEMAIL_RFC5321_UNNEEDED_QUOTED_PAIR, position=data.position)

        elif data.context == ISEMAIL_CONTEXT_COMMENT and ord_chr in ISEMAIL_RANGE_CTEXT:
            data.add_flag(ISEMAIL_RFC5321_UNNEEDED_QUOTED_PAIR, position=data.position)

        elif data.context == ISEMAIL_CONTEXT_QUOTEDSTRING and ord_chr in ISEMAIL_RANGE_QTEXT:
            data.add_flag(ISEMAIL_RFC5321_UNNEEDED_QUOTED_PAIR, position=data.position)

        # context_prior = context
        # context = context_stack.pop()    # End of qpair
        # data.add_token = ISEMAIL_STRING_BACKSLASH + data.token
    
        data.add_token()


    def _parse_fws(self, data):
        data.add_token()
        if data.token == ISEMAIL_STRING_CR:
            data.position += 1
            if data.position == data.raw_length:
                data.add_flag(ISEMAIL_ERR_CR_NO_LF)
            elif data.token != ISEMAIL_STRING_LF:
                data.add_flag(ISEMAIL_ERR_CR_NO_LF, position=data.position)
                data.position -= 1
            else:
                data.add_token()
        data.push_element(ISEMAIL_CONTEXT_FWS)

    def _parse_domain_literal(self, data):
        # TODO: FIX this to check domain literals
        pass

    def _is_email(self, email):
        """
        :param str email:
        :param AddressClass response_obj:
        :return:
        """


        # def is_email(email, check_dns=False, errorlevel=None, all_errors=False):
        """
        # Check that email is a valid address. Read the following RFCs to understand the constraints:
        #     (http:#tools.ietf.org/html/rfc5321)
        #     (http:#tools.ietf.org/html/rfc5322)
        #     (http:#tools.ietf.org/html/rfc4291#section-2.2)
        #     (http:#tools.ietf.org/html/rfc1123#section-2.1)
        #     (http:#tools.ietf.org/html/rfc3696) (guidance only)
        # version 2.0: Enhance diagnose parameter to errorlevel
        # version 3.0: Introduced status categories
        # revision 3.1: BUG: parsedata was passed by value instead of by reference

        :param str email:  email address to check
        :param check_dns: should we validate dns exists as well
        :param errorlevel: errorlevel to break at.
        :param parsedata:
        :return:
        """

        '''
        diagnose = True
        threshold = 0
        return_status = [ISEMAIL_VALID]
        '''
        data = CheckEmailDataClass(email, self.flag_data)

        # Parse the address into components, character by character
        raw_length = len(email)

        '''
        context = ISEMAIL_COMPONENT_LOCALPART    # Where we are
        context_stack = [context]        # Where we have been
        context_prior = ISEMAIL_COMPONENT_LOCALPART    # Where we just came from
        '''

        crlf_count = 0

        # For the dot-atom elements of the address
        '''
        atomlist = {
            ISEMAIL_COMPONENT_LOCALPART: [''],
            ISEMAIL_COMPONENT_DOMAIN: ['']
        }
        '''

        '''
        element_count = 0
        element_len = 0
        '''

        hyphen_flag = False  # Hyphen cannot occur at the end of a subdomain
        end_or_die = False  # CFWS can only appear at the end of the element

        while data.position <= raw_length:
            data.position += 1

            if not data.in_enclosed_element:

                if data.token == ISEMAIL_STRING_OPENPARENTHESIS:  # is a comment
                    data.push_element(ISEMAIL_CONTEXT_COMMENT)
                    data.add_token(data.token)

                    if data.is_local_part:
                        bae = ISEMAIL_CFWS_COMMENT
                    else:
                        bae = ISEMAIL_DEPREC_CFWS_NEAR_AT


                    # We can't start a comment in the middle of an element, so this better be the end
                    end_or_die = data.add_flag_by_state(
                        beg_all_elements = bae,
                        beg_cur_element = ISEMAIL_DEPREC_COMMENT,
                        in_element = ISEMAIL_CFWS_COMMENT)


                elif data.token == ISEMAIL_STRING_DOT: # is a "."
                    data.add_token(data.token)
                    # Next dot-atom element

                    # Another dot, already?
                    if data.add_flag_by_state(
                        beg_all_elements = ISEMAIL_ERR_DOT_START,
                        beg_cur_element = ISEMAIL_ERR_CONSECUTIVE_DOTS):

                        # The entire local-part can be a quoted string for RFC 5321
                        # If it's just one atom that is quoted then it's an RFC 5322 obsolete form

                        if data.is_local_part:

                            if end_or_die:
                                data.add_flag(ISEMAIL_DEPREC_LOCAL_PART)
                            end_or_die = False  # CFWS & quoted strings are OK again now we're at the beginning of an element (although they are obsolete forms)

                        else:
                            if hyphen_flag:
                                data.add_flag(ISEMAIL_ERR_DOMAIN_HYPHEN_END)
                            else:
                                # Nowhere in RFC 5321 does it say explicitly that the
                                # domain part of a Mailbox must be a valid domain according
                                # to the DNS standards set out in RFC 1035, but this *is*
                                # implied in several places. For instance, wherever the idea
                                # of host routing is discussed the RFC says that the domain
                                # must be looked up in the DNS. This would be nonsense unless
                                # the domain was designed to be a valid DNS domain. Hence we
                                # must conclude that the RFC 1035 restriction on label length
                                # also applies to RFC 5321 domains.
                                #
                                # http:#tools.ietf.org/html/rfc1035#section-2.3.4
                                # labels          63 octets or less
                                if data.element_len > 63:
                                    data.add_flag(ISEMAIL_RFC5322_LABEL_TOO_LONG)

                                end_or_die = False  # CFWS is OK again now we're at the beginning of an element (although it may be obsolete CFWS)


                elif data.token == ISEMAIL_STRING_DQUOTE:  # Quoted string
                    if data.add_flag_by_state(
                        beg_all_elements = ISEMAIL_RFC5321_QUOTED_STRING,
                        beg_cur_element = ISEMAIL_DEPREC_LOCAL_PART,
                        in_element = ISEMAIL_ERR_EXPECTING_ATEXT):

                        # The entire local-part can be a quoted string for RFC 5321
                        # If it's just one atom that is quoted then it's an RFC 5322 obsolete form
                        break

                    else:
                        data.add_token(data.token)
                        end_or_die = True  # Quoted string must be the entire element
                        data.push_element(ISEMAIL_CONTEXT_QUOTEDSTRING)

                elif data.token in (ISEMAIL_STRING_CR, ISEMAIL_STRING_SP, ISEMAIL_STRING_HTAB):
                    # Folding White Space
                    self._parse_fws(data)
                    '''
                    if data.token == ISEMAIL_STRING_CR and (data.position+1 == raw_length or email[data.position+1] != ISEMAIL_STRING_LF):
                        data.add_flag(ISEMAIL_ERR_CR_NO_LF)
                        break  # Fatal error

                    data.push_element(ISEMAIL_CONTEXT_FWS)
                    token_prior = data.token
                    '''
                    if data.is_local_part:
                        end_or_die = data.add_flag_by_state(
                            beg_all_elements = ISEMAIL_CFWS_FWS,
                            beg_cur_element = ISEMAIL_DEPREC_LOCAL_PART)
                            # We can't start FWS in the middle of an element, so this better be the end
                    else:
                        end_or_die = data.add_flag_by_state(
                            beg_all_elements=ISEMAIL_DEPREC_CFWS_NEAR_AT,
                            beg_cur_element=ISEMAIL_DEPREC_FWS,
                            in_element=ISEMAIL_CFWS_FWS)
                        # We can't start FWS in the middle of an element, so this better be the end

                elif data.token == ISEMAIL_STRING_AT:
                    # @
                    # At this point we should have a valid local-part

                    if data.is_local_part:

                        if len(data.element_stack) != 1:
                            raise AttributeError('Unexpected item on context stack: %s' % data.element_stack)

                        tmp_local_str = data.local_str
                        if tmp_local_str == '':
                            data.add_flag(ISEMAIL_ERR_NO_LOCAL_PART)

                        elif len(data.element) == 0:
                            data += ISEMAIL_ERR_DOT_END  # Fatal error

                        elif len(tmp_local_str) > 64:
                            # http:#tools.ietf.org/html/rfc5321#section-4.5.3.1.1
                            #   The maximum total length of a user name or other local-part is 64
                            #   octets.
                            data.add_flag(ISEMAIL_RFC5322_LOCAL_TOO_LONG)
                        elif data.context_prior == ISEMAIL_CONTEXT_COMMENT or data.context_prior == ISEMAIL_CONTEXT_FWS:
                            # http:#tools.ietf.org/html/rfc5322#section-3.4.1
                            #   Comments and folding white space
                            #   SHOULD NOT be used around the "@" in the addr-spec.
                            #
                            # http:#tools.ietf.org/html/rfc2119
                            # 4. SHOULD NOT   This phrase, or the phrase "NOT RECOMMENDED" mean that
                            #    there may exist valid reasons in particular circumstances when the
                            #    particular behavior is acceptable or even useful, but the full
                            #    implications should be understood and the case carefully weighed
                            #    before implementing any behavior described with this label.
                            data.add_flag(ISEMAIL_DEPREC_CFWS_NEAR_AT)

                        # Clear everything down for the domain parsing
                        data.set_at()
                        end_or_die = False  # CFWS can only appear at the end of the element
                    else:
                        raise ValueError('"@" found in domain part not in comment or literal.')

                elif data.token == ISEMAIL_STRING_OPENSQBRACKET and not data.in_local_part:
                    # Domain literal
                    if data.domain_str == '':
                        end_or_die = True  # Domain literal must be the only component
                        data.push_element(ISEMAIL_COMPONENT_LITERAL)
                        # data.domain_literal = ISEMAIL_DOMAIN_LIT_UNK
                        data.add_token(data.token)
                    else:
                        data.add_flag(ISEMAIL_ERR_EXPECTING_ATEXT)  # Fatal error

                else:  # item text IN LOCAL PART
                    # atext
                    # http:#tools.ietf.org/html/rfc5322#section-3.2.3
                    #    atext           = ALPHA / DIGIT /    ; Printable US-ASCII
                    #                        "!" / "#" /        ;  characters not including
                    #                        "" / "%" /        ;  specials.  Used for atoms.
                    #                        "&" / "'" /
                    #                        "*" / "+" /
                    #                        "-" / "/" /
                    #                        "=" / "?" /
                    #                        "^" / "_" /
                    #                        "`" / "{" /
                    #                        "|" / "}" /
                    #                        "~"

                    # FOR DOMAINS:
                    #   But RFC 5321 only allows letter-digit-hyphen to comply with DNS rules (RFCs 1034 & 1123)
                    #   http:#tools.ietf.org/html/rfc5321#section-4.1.2
                    #      sub-domain     = Let-dig [Ldh-str]
                    #
                    #      Let-dig        = ALPHA / DIGIT
                    #
                    #      Ldh-str        = *( ALPHA / DIGIT / "-" ) Let-dig
                    #



                    if end_or_die:
                        # We have encountered atext where it is no longer valid
                        data.add_token(data.token, skip=True)
                        if data.element_prior.element_type in (ISEMAIL_CONTEXT_COMMENT, ISEMAIL_CONTEXT_FWS):
                            data.add_flag(ISEMAIL_ERR_ATEXT_AFTER_CFWS)
                            break
                        elif data.element_prior == ISEMAIL_CONTEXT_QUOTEDSTRING:
                            data.add_flag(ISEMAIL_ERR_ATEXT_AFTER_QS)
                            break
                        elif data.context_prior == ISEMAIL_COMPONENT_LITERAL:
                            data.add_flag(ISEMAIL_ERR_ATEXT_AFTER_DOMLIT)
                            break

                        else:
                            raise ValueError(
                                "More atext found where none is allowed, but unrecognised prior context: %s" % data.element_prior)

                    else:
                        if data.is_local_part:
                            # context_prior = context
                            ord_chr = ord(data.token)

                            if ord_chr in range(33, 126) or ord_chr == 10 or data.token in ISEMAIL_STRING_SPECIALS:
                                data.add_flag(ISEMAIL_ERR_EXPECTING_ATEXT)  # Fatal error

                        else:
                            ord_chr = ord(data.token)
                            hyphen_flag = False  # Assume this token isn't a hyphen unless we discover it is

                            if ord_chr not in range(33, 126) or data.token in ISEMAIL_STRING_SPECIALS:
                                data.add_flag(ISEMAIL_ERR_EXPECTING_ATEXT)  # Fatal error
                            elif data.token == ISEMAIL_STRING_HYPHEN:
                                if data.element_len == 0:
                                    # Hyphens can't be at the beginning of a subdomain
                                    data.add_flag(ISEMAIL_ERR_DOMAIN_HYPHEN_START)  # Fatal error
                                hyphen_flag = True

                            elif ord_chr not in broken_range((47, 58), (64, 91), (96, 123)):
                                # elif not (47 < ord_chr < 58) or (64 < ord_chr < 91) or (96 < ord_chr < 123):
                                # Not an RFC 5321 subdomain, but still OK by RFC 5322
                                data.add_flag(ISEMAIL_RFC5322_DOMAIN)

                        data.add_token(data.token)

            elif data.context == ISEMAIL_COMPONENT_LITERAL:
                # -------------------------------------------------------------
                # Domain literal
                # -------------------------------------------------------------
                # http:#tools.ietf.org/html/rfc5322#section-3.4.1
                #   domain-literal  = [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
                #
                #   dtext           = %d33-90 /          ; Printable US-ASCII
                #                       %d94-126 /         ;  characters not including
                #                       obs-dtext          ;  "[", "]", or "\"
                #
                #   obs-dtext       = obs-NO-WS-CTL / quoted-pair
                # End of domain literal
                if data.token == ISEMAIL_STRING_CLOSESQBRACKET:
                    self._parse_domain_literal(data)

                elif data.token == ISEMAIL_STRING_BACKSLASH:
                    self._parse_quoted_pair(data)
                    # data.push_element(ISEMAIL_CONTEXT_QUOTEDPAIR)
                    # data += data.token
                    # data += ISEMAIL_RFC5322_DOMLIT_OBS_DTEXT
                    # context_stack.append(context)
                    # context = ISEMAIL_CONTEXT_QUOTEDPAIR
                    # break
                # Folding White Space
                elif data.token in (ISEMAIL_STRING_CR, ISEMAIL_STRING_SP, ISEMAIL_STRING_HTAB):
                    self._parse_fws(data)
                    '''
                    if data.token == ISEMAIL_STRING_CR and (++i == raw_length or email[i] != ISEMAIL_STRING_LF):
                        data += ISEMAIL_ERR_CR_NO_LF
                    data += data.token
                    data.push_element(ISEMAIL_CONTEXT_FWS)
                    data += ISEMAIL_CFWS_FWS
                    # context_stack.append(context)
                    # context = ISEMAIL_CONTEXT_FWS
                    token_prior = data.token
                    # break
                    '''
                else:
                    # dtext

                    # http:#tools.ietf.org/html/rfc5322#section-3.4.1
                    #   dtext = %d33-90 /           Printable US-ASCII
                    #                       %d94-126 /           characters not including
                    #                       obs-dtext            "[", "]", or "\"
                    #
                    #   obs-dtext = obs-NO-WS-CTL / quoted-pair
                    #
                    #   obs-NO-WS-CTL = %d1-8 /             US-ASCII control
                    #                       %d11 /               characters that do not
                    #                       %d12 /               include the carriage
                    #                       %d14-31 /            return, line feed, and
                    #                       %d127                white space characters
                    ord_chr = ord(data.token)

                    # CR, LF, SP & HTAB have already been parsed above
                    if ord_chr > 127 or ord_chr == 0 or data.token == ISEMAIL_STRING_OPENSQBRACKET:
                        data += ISEMAIL_ERR_EXPECTING_DTEXT  # Fatal error
                        # break
                    elif ord_chr < 33 or ord_chr == 127:
                        data += ISEMAIL_RFC5322_DOMLIT_OBSDTEXT

                    data += data.token

                    # parsedata[ISEMAIL_COMPONENT_LITERAL] += token
                    # parsedata[ISEMAIL_COMPONENT_DOMAIN] += token
                    # atomlist[ISEMAIL_COMPONENT_DOMAIN][element_count] += token
                    # element_len += 1
                    # break

            elif data.context == ISEMAIL_CONTEXT_QUOTEDSTRING:
                # -------------------------------------------------------------
                # Quoted string
                # -------------------------------------------------------------
                # http:#tools.ietf.org/html/rfc5322#section-3.2.4
                #   quoted-string = [CFWS]
                #                       DQUOTE *([FWS] qcontent) [FWS] DQUOTE
                #                       [CFWS]
                #
                #   qcontent = qtext / quoted-pair
                # Quoted pair
                if data.token == ISEMAIL_STRING_BACKSLASH:
                    self._parse_quoted_pair(data)
                    '''
                    # data.push_element(ISEMAIL_CONTEXT_QUOTEDPAIR)
                    # context_stack.append(context)
                    # context = ISEMAIL_CONTEXT_QUOTEDPAIR
                    # break
                    '''

                # Folding White Space
                # Inside a quoted string, spaces are allowed as regular characters.
                # It's only FWS if we include HTAB or CRLF
                elif data.token == ISEMAIL_STRING_CR or data.token == ISEMAIL_STRING_HTAB:
                    if data.token == ISEMAIL_STRING_CR and (++i == raw_length or email[i] != ISEMAIL_STRING_LF):
                        data += ISEMAIL_ERR_CR_NO_LF
                        # break    # Fatal error

                    # http:#tools.ietf.org/html/rfc5322#section-3.2.2
                    #   Runs of FWS, comment, or CFWS that occur between lexical tokens in a
                    #   structured header field are semantically interpreted as a single
                    #   space character.

                    # http:#tools.ietf.org/html/rfc5322#section-3.2.4
                    #   the CRLF in any FWS/CFWS that appears within the quoted-string [is]
                    #   semantically "invisible" and therefore not part of the quoted-string
                    # parsedata[ISEMAIL_COMPONENT_LOCALPART] += ISEMAIL_STRING_SP
                    # atomlist[ISEMAIL_COMPONENT_LOCALPART][element_count] += ISEMAIL_STRING_SP
                    # element_len += 1

                    data += ISEMAIL_CFWS_FWS
                    data.push_element(ISEMAIL_CONTEXT_FWS)
                    # return_status.append(ISEMAIL_CFWS_FWS)
                    # context_stack.append(context)
                    # context = ISEMAIL_CONTEXT_FWS
                    token_prior = data.token
                    # break

                elif data.token == ISEMAIL_STRING_DQUOTE:
                    # End of quoted string
                    data += data.token
                    # atomlist[ISEMAIL_COMPONENT_LOCALPART][element_count] += token
                    # element_len += 1
                    context_prior = context
                    data.pop_element()
                    # context = context_stack.pop()
                    # break
                else:
                    # qtext
                    # http:#tools.ietf.org/html/rfc5322#section-3.2.4
                    #   qtext = %d33 /              Printable US-ASCII
                    #                       %d35-91 /            characters not including
                    #                       %d93-126 /           "\" or the quote character
                    #                       obs-qtext
                    #
                    #   obs-qtext = obs-NO-WS-CTL
                    #
                    #   obs-NO-WS-CTL = %d1-8 /             US-ASCII control
                    #                       %d11 /               characters that do not
                    #                       %d12 /               include the carriage
                    #                       %d14-31 /            return, line feed, and
                    #                       %d127                white space characters
                    ord_chr = ord(data.token)

                    if ord_chr > 127 or ord_chr == 0 or ord_chr == 10:
                        data += ISEMAIL_ERR_EXPECTING_QTEXT  # Fatal error
                    elif ord_chr < 32 or ord_chr == 127:
                        data += ISEMAIL_DEPREC_QTEXT

                    data += data.token
                    # atomlist[ISEMAIL_COMPONENT_LOCALPART][element_count] += token
                    # element_len += 1

                    # http:#tools.ietf.org/html/rfc5322#section-3.4.1
                    #   If the
                    #   string can be represented as a dot-atom (that is, it contains no
                    #   characters other than atext characters or "." surrounded by atext
                    #   characters), then the dot-atom form SHOULD be used and the quoted-
                    #   string form SHOULD NOT be used.

                    # To do :

                    # break
            elif data.context == ISEMAIL_CONTEXT_QUOTEDPAIR:
                # -------------------------------------------------------------
                # Quoted pair
                # -------------------------------------------------------------
                # http:#tools.ietf.org/html/rfc5322#section-3.2.1
                #   quoted-pair = ("\" (VCHAR / WSP)) / obs-qp
                #
                #   VCHAR = %d33-126             visible (printing) characters
                #   WSP = SP / HTAB            white space
                #
                #   obs-qp = "\" (%d0 / obs-NO-WS-CTL / LF / CR)
                #
                #   obs-NO-WS-CTL = %d1-8 /             US-ASCII control
                #                       %d11 /               characters that do not
                #                       %d12 /               include the carriage
                #                       %d14-31 /            return, line feed, and
                #                       %d127                white space characters
                #
                # i.e. obs-qp = "\" (%d0-8, %d10-31 / %d127)
                ord_chr = ord(data.token)

                if ord_chr > 127:
                    data += ISEMAIL_ERR_EXPECTING_QPAIR  # Fatal error
                elif ord_chr in broken_range((1, 8), (11, 11), (12, 12), (14, 31), (127, 127)):
                    data += ISEMAIL_DEPREC_QP
                '''
                elif (ord_chr < 31 and ord_chr != 9) or ord_chr == 127:    # SP & HTAB are allowed
                    return_status.append(ISEMAIL_DEPREC_QP)
                '''
                # At this point we know where this qpair occurred so
                # we could check to see if the character actually
                # needed to be quoted at all.
                # http:#tools.ietf.org/html/rfc5321#section-4.1.2
                #   the sending system SHOULD transmit the
                #   form that uses the minimum quoting possible.

                # Todo: check whether the character needs to be quoted (escaped) in this context

                data.pop_element()

                # context_prior = context
                # context = context_stack.pop()    # End of qpair
                data.token = ISEMAIL_STRING_BACKSLASH + data.token

                if data.context == ISEMAIL_CONTEXT_COMMENT:
                    pass
                elif data.context in (ISEMAIL_CONTEXT_QUOTEDSTRING, ISEMAIL_COMPONENT_LITERAL):
                    data += data.token
                    data.element_len += 1
                    # atomlist[ISEMAIL_COMPONENT_LOCALPART][element_count] += token
                    # element_len += 2    # The maximum sizes specified by RFC 5321 are octet counts, so we must include the backslash
                    # break
                else:
                    raise ValueError("Quoted pair logic invoked in an invalid context: context")
                    # break

            elif data.context == ISEMAIL_CONTEXT_COMMENT:
                # -------------------------------------------------------------
                # Comment
                # -------------------------------------------------------------
                # http:#tools.ietf.org/html/rfc5322#section-3.2.2
                #   comment = "(" *([FWS] ccontent) [FWS] ")"
                #
                #   ccontent = ctext / quoted-pair / comment
                # Nested comment
                if data.token == ISEMAIL_STRING_OPENPARENTHESIS:
                    # Nested comments are OK
                    data.push_element(ISEMAIL_CONTEXT_COMMENT)
                    # context_stack.append(context)
                    # context = ISEMAIL_CONTEXT_COMMENT
                    # break
                # End of comment
                elif data.token == ISEMAIL_STRING_CLOSEPARENTHESIS:
                    data.pop_element()
                    # context_prior = context
                    # context = context_stack.pop()

                    # http:#tools.ietf.org/html/rfc5322#section-3.2.2
                    #   Runs of FWS, comment, or CFWS that occur between lexical tokens in a
                    #   structured header field are semantically interpreted as a single
                    #   space character.
                    #
                    # is_email() author's note: This *cannot* mean that we must add a
                    # space to the address wherever CFWS appears. This would result in
                    # any addr-spec that had CFWS outside a quoted string being invalid
                    # for RFC 5321.


                    #                if ((context == ISEMAIL_COMPONENT_LOCALPART) or (context == ISEMAIL_COMPONENT_DOMAIN)) {
                    #                    parsedata[context] += ISEMAIL_STRING_SP
                    #                    atomlist[context][element_count] += ISEMAIL_STRING_SP
                    #                    element_len++
                    #                }

                    # break
                elif data.token == ISEMAIL_STRING_BACKSLASH:
                    # Quoted pair
                    data.push_element(ISEMAIL_CONTEXT_QUOTEDPAIR)
                    # context_stack.append(context)
                    # context = ISEMAIL_CONTEXT_QUOTEDPAIR
                    # break
                elif data.token in (ISEMAIL_STRING_CR, ISEMAIL_STRING_SP, ISEMAIL_STRING_HTAB):
                    # Folding White Space
                    if data.token == ISEMAIL_STRING_CR and (++i == raw_length or email[i] != ISEMAIL_STRING_LF):
                        data += ISEMAIL_ERR_CR_NO_LF
                        # break    # Fatal error

                    data += ISEMAIL_CFWS_FWS
                    data.push_element(ISEMAIL_CONTEXT_FWS)
                    # context_stack.append(context)
                    # context = ISEMAIL_CONTEXT_FWS
                    token_prior = data.token
                    # break
                else:
                    # ctext
                    # http:#tools.ietf.org/html/rfc5322#section-3.2.3
                    #   ctext = %d33-39 /           Printable US-ASCII
                    #                       %d42-91 /            characters not including
                    #                       %d93-126 /           "(", ")", or "\"
                    #                       obs-ctext
                    #
                    #   obs-ctext = obs-NO-WS-CTL
                    #
                    #   obs-NO-WS-CTL = %d1-8 /             US-ASCII control
                    #                       %d11 /               characters that do not
                    #                       %d12 /               include the carriage
                    #                       %d14-31 /            return, line feed, and
                    #                       %d127                white space characters
                    ord_chr = ord(data.token)

                    if ord_chr > 127 or ord_chr == 0 or ord_chr == 10:
                        data += ISEMAIL_ERR_EXPECTING_CTEXT  # Fatal error
                        # break
                    elif ord_chr < 32 or ord_chr == 127:
                        data += ISEMAIL_DEPREC_CTEXT
                        # return_status.append()
                        # break
            elif context == ISEMAIL_CONTEXT_FWS:
                # -------------------------------------------------------------
                # Folding White Space
                # -------------------------------------------------------------
                # http:#tools.ietf.org/html/rfc5322#section-3.2.2
                #   FWS = ([*WSP CRLF] 1*WSP) /  obs-FWS
                #                                           Folding white space

                # But note the erratum:
                # http:#www.rfc-editor.org/errata_search.php?rfc=5322&eid=1908:
                #   In the obsolete syntax, any amount of folding white space MAY be
                #   inserted where the obs-FWS rule is allowed.  This creates the
                #   possibility of having two consecutive "folds" in a line, and
                #   therefore the possibility that a line which makes up a folded header
                #   field could be composed entirely of white space.
                #
                #   obs-FWS = 1*([CRLF] WSP)
                if token_prior == ISEMAIL_STRING_CR:
                    if data.token == ISEMAIL_STRING_CR:
                        data += ISEMAIL_ERR_FWS_CRLF_X2  # Fatal error
                        # break
                    crlf_count += 1
                    if crlf_count > 1:
                        data += ISEMAIL_DEPREC_FWS  # Multiple folds = obsolete FWS

                if data.token == ISEMAIL_STRING_CR:
                    if ++i == raw_length or email[i] != ISEMAIL_STRING_LF:
                        data += ISEMAIL_ERR_CR_NO_LF  # Fatal error
                        # break
                elif data.token == ISEMAIL_STRING_SP or data.token == ISEMAIL_STRING_HTAB:
                    pass
                else:
                    if token_prior == ISEMAIL_STRING_CR:
                        data += ISEMAIL_ERR_FWS_CRLF_END  # Fatal error
                        # break

                    crlf_count = 0
                    # if (isset(crlf_count)) unset(crlf_count

                    # context_prior = context
                    # context = context_stack.pop()    # End of FWS

                    data.pop_element()
                    # http:#tools.ietf.org/html/rfc5322#section-3.2.2
                    #   Runs of FWS, comment, or CFWS that occur between lexical tokens in a
                    #   structured header field are semantically interpreted as a single
                    #   space character.
                    #
                    # is_email() author's note: This *cannot* mean that we must add a
                    # space to the address wherever CFWS appears. This would result in
                    # any addr-spec that had CFWS outside a quoted string being invalid
                    # for RFC 5321.

                    #                if ((context == ISEMAIL_COMPONENT_LOCALPART) or (context == ISEMAIL_COMPONENT_DOMAIN)) {
                    #                    parsedata[context] += ISEMAIL_STRING_SP
                    #                    atomlist[context][element_count] += ISEMAIL_STRING_SP
                    #                    element_len++
                    #                }

                    i -= 1  # Look at this token again in the parent context

                token_prior = data.token
                # break

                # -echo "<td>context|",((end_or_die) ? 'True' : 'False'),"|token|" . max(return_status) . "</td></tr>" # debug
            elif max(data.max_response()) > ISEMAIL_RFC5322:
                if not all_errors:
                    break  # No point going on if we've got a fatal error

            else:
                # -------------------------------------------------------------
                # A context we aren't expecting (something we screwed up)
                # -------------------------------------------------------------
                raise ValueError("Unknown context: context")


        # Some simple final tests
        if max(data.max_response()) < ISEMAIL_RFC5322:
            if data.context == ISEMAIL_CONTEXT_QUOTEDSTRING:
                data += ISEMAIL_ERR_UNCLOSEDQUOTEDSTR  # Fatal error
            elif data.context == ISEMAIL_CONTEXT_QUOTEDPAIR:
                data += ISEMAIL_ERR_BACKSLASHEND  # Fatal error
            elif data.context == ISEMAIL_CONTEXT_COMMENT:
                data += ISEMAIL_ERR_UNCLOSEDCOMMENT  # Fatal error
            elif data.context == ISEMAIL_COMPONENT_LITERAL:
                data += ISEMAIL_ERR_UNCLOSEDDOMLIT  # Fatal error
            elif data.token == ISEMAIL_STRING_CR:
                data += ISEMAIL_ERR_FWS_CRLF_END  # Fatal error
            elif data.domain_str == '':
                data += ISEMAIL_ERR_NODOMAIN  # Fatal error
            elif data.element_len == 0:
                data += ISEMAIL_ERR_DOT_END  # Fatal error
            elif hyphen_flag:
                data += ISEMAIL_ERR_DOMAINHYPHENEND  # Fatal error
            elif len(data.domain_str) > 255:
                # http:#tools.ietf.org/html/rfc5321#section-4.5.3.1.2
                #   The maximum total length of a domain name or number is 255 octets.
                data += ISEMAIL_RFC5322_DOMAIN_TOOLONG
            elif len(data) > 254:
                # http:#tools.ietf.org/html/rfc5321#section-4.1.2
                #   Forward-path = Path
                #
                #   Path = "<" [ A-d-l ":" ] Mailbox ">"
                #
                # http:#tools.ietf.org/html/rfc5321#section-4.5.3.1.3
                #   The maximum total length of a reverse-path or forward-path is 256
                #   octets (including the punctuation and element separators).
                #
                # Thus, even without (obsolete) routing information, the Mailbox can
                # only be 254 characters long. This is confirmed by this verified
                # erratum to RFC 3696:
                #
                # http:#www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690
                #   However, there is a restriction in RFC 2821 on the length of an
                #   address in MAIL and RCPT commands of 254 characters.  Since addresses
                #   that do not fit in those fields are not normally useful, the upper
                #   limit on address lengths should normally be considered to be 254.

                data += ISEMAIL_RFC5322_TOOLONG

            elif data.element_len > 63:
                data += ISEMAIL_RFC5322_LABEL_TOOLONG
                # http:#tools.ietf.org/html/rfc1035#section-2.3.4
                # labels          63 octets or less

        # Check DNS?
        dns_checked = False
        '''
        if check_dns and max(return_status) < ISEMAIL_DNSWARN:  # and function_exists('dns_get_record'):
            # http:#tools.ietf.org/html/rfc5321#section-2.3.5
            #   Names that can
            #   be resolved to MX RRs or address (i.e., A or AAAA) RRs (as discussed
            #   in Section 5) are permitted, as are CNAME RRs whose targets can be
            #   resolved, in turn, to MX or address RRs.
            #
            # http:#tools.ietf.org/html/rfc5321#section-5.1
            #   The lookup first attempts to locate an MX record associated with the
            #   name.  If a CNAME record is found, the resulting name is processed as
            #   if it were the initial name. ... If an empty list of MXs is returned,
            #   the address is treated as if it was associated with an implicit MX
            #   RR, with a preference of 0, pointing to that host.
            #
            # is_email() author's note: We will regard the existence of a CNAME to be
            # sufficient evidence of the domain's existence. For performance reasons
            # we will not repeat the DNS lookup for the CNAME's target, but we will
            # raise a warning because we didn't immediately find an MX record.
            if element_count == 0:
                parsedata[ISEMAIL_COMPONENT_DOMAIN] += '.'        # Checking TLD DNS seems to work only if you explicitly check from the root

            # todo fix this for python
            # result = @dns_get_record(parsedata[ISEMAIL_COMPONENT_DOMAIN], DNS_MX    # Not using checkdnsrr because of a suspected bug in PHP 5.3 (http:#bugs.php.net/bug.php?id=51844)
            result = []

            if not result:
                return_status.append(ISEMAIL_DNSWARN_NO_RECORD)            # Domain can't be found in DNS
            else:
                if len(result) == 0:
                    return_status.append(ISEMAIL_DNSWARN_NO_MX_RECORD)        # MX-record for domain can't be found

                    # todo: fix this for python
                    # result = @dns_get_record(parsedata[ISEMAIL_COMPONENT_DOMAIN], DNS_A + DNS_CNAME
                    result = []

                    if len(result) == 0:
                        return_status.append(ISEMAIL_DNSWARN_NO_RECORD)        # No usable records for the domain can be found
                else:
                    dns_checked = True
        '''
        # Check for TLD addresses
        # -----------------------
        # TLD addresses are specifically allowed in RFC 5321 but they are
        # unusual to say the least. We will allocate a separate
        # status to these addresses on the basis that they are more likely
        # to be typos than genuine addresses (unless we've already
        # established that the domain does have an MX record)
        #
        # http:#tools.ietf.org/html/rfc5321#section-2.3.5
        #   In the case
        #   of a top-level domain used by itself in an email address, a single
        #   string is used without any dots.  This makes the requirement,
        #   described in more detail below, that only fully-qualified domain
        #   names appear in SMTP transactions on the public Internet,
        #   particularly important where top-level domains are involved.
        #
        # TLD format
        # ----------
        # The format of TLDs has changed a number of times. The standards
        # used by IANA have been largely ignored by ICANN, leading to
        # confusion over the standards being followed. These are not defined
        # anywhere, except as a general component of a DNS host name (a label).
        # However, this could potentially lead to 123.123.123.123 being a
        # valid DNS name (rather than an IP address) and thereby creating
        # an ambiguity. The most authoritative statement on TLD formats that
        # the author can find is in a (rejected!) erratum to RFC 1123
        # submitted by John Klensin, the author of RFC 5321:
        #
        # http:#www.rfc-editor.org/errata_search.php?rfc=1123&eid=1353
        #   However, a valid host name can never have the dotted-decimal
        #   form #.#.#.#, since this change does not permit the highest-level
        #   component label to start with a digit even if it is not all-numeric.
        if not dns_checked and (max(data.max_response()) < ISEMAIL_DNSWARN):
            if data.element_count == 0:
                data += ISEMAIL_RFC5321_TLD

            # TODO: add this back
            '''
            if atomlist[ISEMAIL_COMPONENT_DOMAIN][element_count][0].isnumeric():
                return_status.append(ISEMAIL_RFC5321_TLDNUMERIC)
            '''
        '''
        return_status = set(return_status)
        final_status = max(return_status)
        # if len(return_status) != 1:
        #     array_shift(return_status) # remove redundant ISEMAIL_VALID

        parsedata['status'] = return_status

        if final_status < threshold:
            final_status = ISEMAIL_VALID

        if diagnose:
            return final_status
        else:
            return final_status < ISEMAIL_THRESHOLD
        '''


    def is_email(self, *args):



def is_email(email, check_dns=False, errorlevel=None, all_errors=False):
    """
    # Check that email is a valid address. Read the following RFCs to understand the constraints:
    #     (http:#tools.ietf.org/html/rfc5321)
    #     (http:#tools.ietf.org/html/rfc5322)
    #     (http:#tools.ietf.org/html/rfc4291#section-2.2)
    #     (http:#tools.ietf.org/html/rfc1123#section-2.1)
    #     (http:#tools.ietf.org/html/rfc3696) (guidance only)
    # version 2.0: Enhance diagnose parameter to errorlevel
    # version 3.0: Introduced status categories
    # revision 3.1: BUG: parsedata was passed by value instead of by reference

    :param str email:  email address to check
    :param check_dns: should we validate dns exists as well
    :param errorlevel: errorlevel to break at.
    :param parsedata:
    :return:
    """

    if errorlevel is not None:
        threshold = ISEMAIL_VALID
        diagnose = errorlevel
    else:
        diagnose = True
        threshold = 0

    # return_status = [ISEMAIL_VALID]

    # Parse the address into components, character by character
    raw_length = len(email)
    # context = ISEMAIL_COMPONENT_LOCALPART    # Where we are
    # context_stack = [context]        # Where we have been
    # context_prior = ISEMAIL_COMPONENT_LOCALPART    # Where we just came from
    token = ''                # The current character
    token_prior = ''                # The previous character

    crlf_count = 0

    # For the components of the address
    data = AddressClass(raw_email=email)

    # For the dot-atom elements of the address
    '''
    atomlist = {
        ISEMAIL_COMPONENT_LOCALPART: [''],
        ISEMAIL_COMPONENT_DOMAIN: ['']
    }
    '''
    # element_count = 0
    # element_len = 0
    hyphen_flag = False            # Hyphen cannot occur at the end of a subdomain
    end_or_die = False            # CFWS can only appear at the end of the element

    # -echo "<table style=\"clear:left;\">"; # debug
    # for (i = 0; i < raw_length; i++) {
    #     token = email[i];
    # -echo "<tr><td><strong>context|",((end_or_die) ? 'True' : 'False'),"|token|" . max(return_status) . "</strong></td>"; # debug

    for i, token in enumerate(email):
        # position = int(i)

        if data.context == ISEMAIL_COMPONENT_LOCALPART:
            # -------------------------------------------------------------
            # local-part
            # -------------------------------------------------------------

            # http:#tools.ietf.org/html/rfc5322#section-3.4.1
            #   local-part      = dot-atom / quoted-string / obs-local-part
            #
            #   dot-atom        = [CFWS] dot-atom-text [CFWS]
            #
            #   dot-atom-text   = 1*atext *("." 1*atext)
            #
            #   quoted-string   = [CFWS]
            #                       DQUOTE *([FWS] qcontent) [FWS] DQUOTE
            #                       [CFWS]
            #
            #   obs-local-part  = word *("." word)
            #
            #   word            = atom / quoted-string
            #
            #   atom            = [CFWS] 1*atext [CFWS]

            if token == ISEMAIL_STRING_OPENPARENTHESIS:
                # is a comment
                part_state = data.response_by_state({
                    ISEMAIL_ELEMENT_BEG_ALL: ISEMAIL_CFWS_COMMENT,
                    ISEMAIL_ELEMENT_BEG_ELEMENT: ISEMAIL_DEPREC_COMMENT,
                    ISEMAIL_ELEMENT_IN_ELEMENT: ISEMAIL_CFWS_COMMENT
                })
                if part_state == ISEMAIL_ELEMENT_IN_ELEMENT:
                    end_or_die = True  # We can't start a comment in the middle of an element, so this better be the end

                '''
                if element_len == 0:
                    # Comments are OK at the beginning of an element
                    if element_count == 0:
                        return_status.append(ISEMAIL_CFWS_COMMENT)
                    else:
                        return_status.append(ISEMAIL_DEPREC_COMMENT)
                else:
                    return_status.append(ISEMAIL_CFWS_COMMENT)
                    end_or_die = True    # We can't start a comment in the middle of an element, so this better be the end
                '''
                data.push_element(ISEMAIL_CONTEXT_COMMENT)
                data += token
                # context_stack.append(context)
                # context = ISEMAIL_CONTEXT_COMMENT
                # break
            elif token == ISEMAIL_STRING_DOT:
                # Next dot-atom element
                part_state = data.response_by_state({
                    ISEMAIL_ELEMENT_BEG_ALL: ISEMAIL_ERR_DOT_START,
                    ISEMAIL_ELEMENT_BEG_ELEMENT: ISEMAIL_ERR_CONSECUTIVEDOTS,
                })
                if part_state == ISEMAIL_ELEMENT_IN_ELEMENT:

                    '''
                    if element_len == 0:
                        # Another dot, already?
                        if element_count == 0:
                            return_status.append(ISEMAIL_ERR_DOT_START)
                        else:
                            return_status.append(ISEMAIL_ERR_CONSECUTIVEDOTS)
                        break
                    else:
                    '''
                    # The entire local-part can be a quoted string for RFC 5321
                    # If it's just one atom that is quoted then it's an RFC 5322 obsolete form
                    if end_or_die:
                        data += ISEMAIL_DEPREC_LOCALPART
                        # return_status.append(ISEMAIL_DEPREC_LOCALPART)
                    end_or_die = False    # CFWS & quoted strings are OK again now we're at the beginning of an element (although they are obsolete forms)
                    # element_len = 0
                    # element_count += 1
                    data += token
                    # parsedata[ISEMAIL_COMPONENT_LOCALPART] += token
                    # atomlist[ISEMAIL_COMPONENT_LOCALPART].append('')

                # break
            elif token == ISEMAIL_STRING_DQUOTE:
                # Quoted string
                part_state = data.response_by_state({
                    ISEMAIL_ELEMENT_BEG_ALL: ISEMAIL_RFC5321_QUOTEDSTRING,
                    ISEMAIL_ELEMENT_BEG_ELEMENT: ISEMAIL_DEPREC_LOCALPART,
                    ISEMAIL_ELEMENT_IN_ELEMENT: ISEMAIL_ERR_EXPECTING_ATEXT,
                })
                # The entire local-part can be a quoted string for RFC 5321
                # If it's just one atom that is quoted then it's an RFC 5322 obsolete form

                if part_state in (ISEMAIL_ELEMENT_BEG_ALL, ISEMAIL_ELEMENT_BEG_ELEMENT):
                    data += token
                    end_or_die = True    # Quoted string must be the entire element
                    data.push_element(ISEMAIL_CONTEXT_QUOTEDSTRING)

                elif part_state == ISEMAIL_ELEMENT_IN_ELEMENT:
                    break
                '''
                if element_len == 0:
                    if element_count == 0:
                        return_status.append(ISEMAIL_RFC5321_QUOTEDSTRING)
                    else:
                        return_status.append(ISEMAIL_DEPREC_LOCALPART)

                    parsedata[ISEMAIL_COMPONENT_LOCALPART] += token
                    atomlist[ISEMAIL_COMPONENT_LOCALPART][element_count] += token
                    element_len += 1
                    end_or_die = True    # Quoted string must be the entire element
                    context_stack.append(context)
                    context = ISEMAIL_CONTEXT_QUOTEDSTRING
                else:
                    return_status.append(ISEMAIL_ERR_EXPECTING_ATEXT)    # Fatal error

                    break
                '''
            elif token in (ISEMAIL_STRING_CR, ISEMAIL_STRING_SP, ISEMAIL_STRING_HTAB):
                # Folding White Space
                if token == ISEMAIL_STRING_CR and (++i == raw_length or email[i] != ISEMAIL_STRING_LF):
                    data += ISEMAIL_ERR_CR_NO_LF
                    break    # Fatal error

                part_state = data.response_by_state({
                    ISEMAIL_ELEMENT_BEG_ALL: ISEMAIL_CFWS_FWS,
                    ISEMAIL_ELEMENT_BEG_ELEMENT: ISEMAIL_DEPREC_LOCALPART,
                })
                if part_state == ISEMAIL_ELEMENT_IN_ELEMENT:
                    end_or_die = True    # We can't start FWS in the middle of an element, so this better be the end

                '''
                if element_len == 0:
                    if element_count == 0:
                        return_status.append(ISEMAIL_CFWS_FWS)
                    else:
                        return_status.append(ISEMAIL_DEPREC_FWS)
                else:
                '''
                data.push_element(ISEMAIL_CONTEXT_FWS)
                #  context_stack.append(context)
                #  context = ISEMAIL_CONTEXT_FWS
                token_prior = token

                # break
            elif token == ISEMAIL_STRING_AT:
                # @
                # At this point we should have a valid local-part
                if len(data.element_stack) != 1:
                    raise AttributeError('Unexpected item on context stack: %s' % data.element_stack)
                '''
                if parsedata[ISEMAIL_COMPONENT_LOCALPART] == '':
                    return_status.append(ISEMAIL_ERR_NOLOCALPART)    # Fatal error
                '''
                tmp_local_str = data.local_str
                if tmp_local_str == '':
                    data += ISEMAIL_ERR_NOLOCALPART

                elif data.element_len == 0:
                    data += ISEMAIL_ERR_DOT_END    # Fatal error

                elif len(tmp_local_str) > 64:
                    # http:#tools.ietf.org/html/rfc5321#section-4.5.3.1.1
                    #   The maximum total length of a user name or other local-part is 64
                    #   octets.
                    data += ISEMAIL_RFC5322_LOCAL_TOOLONG
                elif data.context_prior == ISEMAIL_CONTEXT_COMMENT or data.context_prior == ISEMAIL_CONTEXT_FWS:
                    # http:#tools.ietf.org/html/rfc5322#section-3.4.1
                    #   Comments and folding white space
                    #   SHOULD NOT be used around the "@" in the addr-spec.
                    #
                    # http:#tools.ietf.org/html/rfc2119
                    # 4. SHOULD NOT   This phrase, or the phrase "NOT RECOMMENDED" mean that
                    #    there may exist valid reasons in particular circumstances when the
                    #    particular behavior is acceptable or even useful, but the full
                    #    implications should be understood and the case carefully weighed
                    #    before implementing any behavior described with this label.
                    data += ISEMAIL_DEPREC_CFWS_NEAR_AT

                # Clear everything down for the domain parsing
                data.set_at()
                # context = ISEMAIL_COMPONENT_DOMAIN    # Where we are
                # context_stack = [context]       # Where we have been
                # element_count = 0
                # element_len = 0
                end_or_die = False            # CFWS can only appear at the end of the element
                # break

            else:
                # atext
                # http:#tools.ietf.org/html/rfc5322#section-3.2.3
                #    atext           = ALPHA / DIGIT /    ; Printable US-ASCII
                #                        "!" / "#" /        ;  characters not including
                #                        "" / "%" /        ;  specials.  Used for atoms.
                #                        "&" / "'" /
                #                        "*" / "+" /
                #                        "-" / "/" /
                #                        "=" / "?" /
                #                        "^" / "_" /
                #                        "`" / "{" /
                #                        "|" / "}" /
                #                        "~"
                if end_or_die:
                    # We have encountered atext where it is no longer valid
                    if data.context_prior in (ISEMAIL_CONTEXT_COMMENT, ISEMAIL_CONTEXT_FWS):
                        data += ISEMAIL_ERR_ATEXT_AFTER_CFWS
                        break
                    elif data.context_prior == ISEMAIL_CONTEXT_QUOTEDSTRING:
                        data += ISEMAIL_ERR_ATEXT_AFTER_QS
                        break
                    else:
                        raise ValueError("More atext found where none is allowed, but unrecognised prior context: context_prior")
                else:
                    # context_prior = context
                    ord_chr = ord(token)

                    if ord_chr in range(33, 126) or ord_chr == 10 or token in ISEMAIL_STRING_SPECIALS:
                        data += ISEMAIL_ERR_EXPECTING_ATEXT    # Fatal error

                    data += token

                    # parsedata[ISEMAIL_COMPONENT_LOCALPART] += token
                    # atomlist[ISEMAIL_COMPONENT_LOCALPART][element_count] += token
                    # element_len += 1

                # break
        elif data.component == ISEMAIL_COMPONENT_DOMAIN:
            # -------------------------------------------------------------
            # Domain
            # -------------------------------------------------------------
            # http:#tools.ietf.org/html/rfc5322#section-3.4.1
            #   domain          = dot-atom / domain-literal / obs-domain
            #
            #   dot-atom        = [CFWS] dot-atom-text [CFWS]
            #
            #   dot-atom-text   = 1*atext *("." 1*atext)
            #
            #   domain-literal  = [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
            #
            #   dtext           = %d33-90 /          ; Printable US-ASCII
            #                       %d94-126 /         ;  characters not including
            #                       obs-dtext          ;  "[", "]", or "\"
            #
            #   obs-domain      = atom *("." atom)
            #
            #   atom            = [CFWS] 1*atext [CFWS]


            # http:#tools.ietf.org/html/rfc5321#section-4.1.2
            #   Mailbox        = Local-part "@" ( Domain / address-literal )
            #
            #   Domain         = sub-domain *("." sub-domain)
            #
            #   address-literal  = "[" ( IPv4-address-literal /
            #                    IPv6-address-literal /
            #                    General-address-literal ) "]"
            #                    ; See Section 4.1.3

            # http:#tools.ietf.org/html/rfc5322#section-3.4.1
            #      Note: A liberal syntax for the domain portion of addr-spec is
            #      given here.  However, the domain portion contains addressing
            #      information specified by and used in other protocols (e.g.,
            #      [RFC1034], [RFC1035], [RFC1123], [RFC5321]).  It is therefore
            #      incumbent upon implementations to conform to the syntax of
            #      addresses for the context in which they are used.
            # is_email() author's note: it's not clear how to interpret this in
            # the context of a general email address validator. The conclusion I
            # have reached is this: "addressing information" must comply with
            # RFC 5321 (and in turn RFC 1035), anything that is "semantically
            # invisible" must comply only with RFC 5322.
            if token == ISEMAIL_STRING_OPENPARENTHESIS:
                # token is a Comment
                part_state = data.response_by_state({
                    ISEMAIL_ELEMENT_BEG_ALL: ISEMAIL_DEPREC_CFWS_NEAR_AT,
                    ISEMAIL_ELEMENT_BEG_ELEMENT: ISEMAIL_DEPREC_COMMENT,
                    ISEMAIL_ELEMENT_IN_ELEMENT: ISEMAIL_CFWS_COMMENT,
                })
                if part_state == ISEMAIL_ELEMENT_IN_ELEMENT:
                    end_or_die = True    # We can't start a comment in the middle of an element, so this better be the end
                '''
                if element_len == 0:
                    # Comments at the start of the domain are deprecated in the text
                    # Comments at the start of a subdomain are obs-domain
                    # (http:#tools.ietf.org/html/rfc5322#section-3.4.1)
                    if element_count == 0:
                        return_status.append(ISEMAIL_DEPREC_CFWS_NEAR_AT)
                    else:
                        return_status.append(ISEMAIL_DEPREC_COMMENT)
                else:
                    return_status.append(ISEMAIL_CFWS_COMMENT)
                    end_or_die = True    # We can't start a comment in the middle of an element, so this better be the end
                '''
                data.push_element(ISEMAIL_CONTEXT_COMMENT)
                # context_stack = context
                # context = ISEMAIL_CONTEXT_COMMENT
                # break
            elif token == ISEMAIL_STRING_DOT:
                # Next dot-atom element
                part_state = data.response_by_state({
                    ISEMAIL_ELEMENT_BEG_ALL: ISEMAIL_ERR_DOT_START,
                    ISEMAIL_ELEMENT_BEG_ELEMENT: ISEMAIL_ERR_CONSECUTIVEDOTS,
                })

                if part_state == ISEMAIL_ELEMENT_IN_ELEMENT:
                    if hyphen_flag:
                        data += ISEMAIL_ERR_DOMAINHYPHENEND
                    else:
                        # Nowhere in RFC 5321 does it say explicitly that the
                        # domain part of a Mailbox must be a valid domain according
                        # to the DNS standards set out in RFC 1035, but this *is*
                        # implied in several places. For instance, wherever the idea
                        # of host routing is discussed the RFC says that the domain
                        # must be looked up in the DNS. This would be nonsense unless
                        # the domain was designed to be a valid DNS domain. Hence we
                        # must conclude that the RFC 1035 restriction on label length
                        # also applies to RFC 5321 domains.
                        #
                        # http:#tools.ietf.org/html/rfc1035#section-2.3.4
                        # labels          63 octets or less
                        if data.element_len > 63:
                            data += ISEMAIL_RFC5322_LABEL_TOOLONG

                        end_or_die = False    # CFWS is OK again now we're at the beginning of an element (although it may be obsolete CFWS)
                        data += token


                '''
                if element_len == 0:
                    # Another dot, already?
                    if element_count == 0:
                        return_status.append(ISEMAIL_ERR_DOT_START)
                    else:
                        return_status.append(ISEMAIL_ERR_CONSECUTIVEDOTS)    # Fatal error
                elif hyphen_flag:
                    # Previous subdomain ended in a hyphen
                    return_status.append(ISEMAIL_ERR_DOMAINHYPHENEND)    # Fatal error
                else:
                    # Nowhere in RFC 5321 does it say explicitly that the
                    # domain part of a Mailbox must be a valid domain according
                    # to the DNS standards set out in RFC 1035, but this *is*
                    # implied in several places. For instance, wherever the idea
                    # of host routing is discussed the RFC says that the domain
                    # must be looked up in the DNS. This would be nonsense unless
                    # the domain was designed to be a valid DNS domain. Hence we
                    # must conclude that the RFC 1035 restriction on label length
                    # also applies to RFC 5321 domains.
                    #
                    # http:#tools.ietf.org/html/rfc1035#section-2.3.4
                    # labels          63 octets or less
                    if element_len > 63:
                        return_status.append(ISEMAIL_RFC5322_LABEL_TOOLONG)

                    end_or_die = False    # CFWS is OK again now we're at the beginning of an element (although it may be obsolete CFWS)
                    element_len = 0
                    element_count += 1
                    atomlist[ISEMAIL_COMPONENT_DOMAIN].append('')
                    parsedata[ISEMAIL_COMPONENT_DOMAIN] += token
                '''
                # break
            elif token == ISEMAIL_STRING_OPENSQBRACKET:
                # Domain literal
                if data.domain_str == '':
                    end_or_die = True    # Domain literal must be the only component
                    data.push_element(ISEMAIL_COMPONENT_LITERAL)
                    data.domain_literal = ISEMAIL_DOMAIN_LIT_UNK
                    data += token
                else:
                    data += ISEMAIL_ERR_EXPECTING_ATEXT    # Fatal error


                '''
                if parsedata[ISEMAIL_COMPONENT_DOMAIN] == '':

                    end_or_die = True    # Domain literal must be the only component
                    element_len += 1
                    context_stack.append(context)
                    context = ISEMAIL_COMPONENT_LITERAL
                    parsedata[ISEMAIL_COMPONENT_DOMAIN] += token
                    atomlist[ISEMAIL_COMPONENT_DOMAIN][element_count] += token
                    parsedata[ISEMAIL_COMPONENT_LITERAL] = ''
                else:
                    return_status.append(ISEMAIL_ERR_EXPECTING_ATEXT)    # Fatal error
                '''
                # break
            elif token in (ISEMAIL_STRING_CR, ISEMAIL_STRING_SP, ISEMAIL_STRING_HTAB):
                # Folding White Space
                if (token == ISEMAIL_STRING_CR) and (++i == raw_length or email[i] != ISEMAIL_STRING_LF):
                    data += ISEMAIL_ERR_CR_NO_LF
                    # return_status.append(ISEMAIL_ERR_CR_NO_LF)
                    # break    # Fatal error

                part_state = data.response_by_state({
                    ISEMAIL_ELEMENT_BEG_ALL: ISEMAIL_DEPREC_CFWS_NEAR_AT,
                    ISEMAIL_ELEMENT_BEG_ELEMENT: ISEMAIL_DEPREC_FWS,
                    ISEMAIL_ELEMENT_IN_ELEMENT: ISEMAIL_CFWS_FWS,
                })
                if part_state == ISEMAIL_ELEMENT_IN_ELEMENT:
                    end_or_die = True
                '''
                if data.element_len == 0:
                    if element_count == 0:
                        return_status.append(ISEMAIL_DEPREC_CFWS_NEAR_AT)
                    else:
                        return_status.append(ISEMAIL_DEPREC_FWS)
                else:
                    return_status.append(ISEMAIL_CFWS_FWS)
                    end_or_die = True    # We can't start FWS in the middle of an element, so this better be the end
                '''
                data.push_element(ISEMAIL_CONTEXT_FWS)
                data += token
                # context_stack.append(context)
                # context = ISEMAIL_CONTEXT_FWS
                token_prior = token
                # break
            else:
                # atext

                # RFC 5322 allows any atext...
                # http:#tools.ietf.org/html/rfc5322#section-3.2.3
                #    atext           = ALPHA / DIGIT /    ; Printable US-ASCII
                #                        "!" / "#" /        ;  characters not including
                #                        "" / "%" /        ;  specials.  Used for atoms.
                #                        "&" / "'" /
                #                        "*" / "+" /
                #                        "-" / "/" /
                #                        "=" / "?" /
                #                        "^" / "_" /
                #                        "`" / "{" /
                #                        "|" / "}" /
                #                        "~"

                # But RFC 5321 only allows letter-digit-hyphen to comply with DNS rules (RFCs 1034 & 1123)
                # http:#tools.ietf.org/html/rfc5321#section-4.1.2
                #   sub-domain     = Let-dig [Ldh-str]
                #
                #   Let-dig        = ALPHA / DIGIT
                #
                #   Ldh-str        = *( ALPHA / DIGIT / "-" ) Let-dig
                #
                if end_or_die:
                    # We have encountered atext where it is no longer valid
                    if data.context_prior == ISEMAIL_CONTEXT_COMMENT or data.context_prior == ISEMAIL_CONTEXT_FWS:
                        data += ISEMAIL_ERR_ATEXT_AFTER_CFWS
                        break
                    elif data.context_prior == ISEMAIL_COMPONENT_LITERAL:
                        data += ISEMAIL_ERR_ATEXT_AFTER_DOMLIT
                        break
                    else:
                        raise ValueError("More atext found where none is allowed, but unrecognised prior context: context_prior")

                ord_chr = ord(token)
                hyphen_flag = False   # Assume this token isn't a hyphen unless we discover it is

                if ord_chr not in range(33, 126) or token in ISEMAIL_STRING_SPECIALS:
                    data += ISEMAIL_ERR_EXPECTING_ATEXT    # Fatal error
                elif token == ISEMAIL_STRING_HYPHEN:
                    if data.element_len == 0:
                        # Hyphens can't be at the beginning of a subdomain
                        data += ISEMAIL_ERR_DOMAINHYPHENSTART    # Fatal error
                    hyphen_flag = True

                elif ord_chr not in broken_range((47, 58), (64, 91), (96, 123)):
                    #elif not (47 < ord_chr < 58) or (64 < ord_chr < 91) or (96 < ord_chr < 123):
                    # Not an RFC 5321 subdomain, but still OK by RFC 5322
                    data += ISEMAIL_RFC5322_DOMAIN

                data += token

                # parsedata[ISEMAIL_COMPONENT_DOMAIN] += token
                # atomlist[ISEMAIL_COMPONENT_DOMAIN][element_count] += token
                # element_len += 1

            # break
        elif data.context == ISEMAIL_COMPONENT_LITERAL:
            #-------------------------------------------------------------
            # Domain literal
            #-------------------------------------------------------------
            # http:#tools.ietf.org/html/rfc5322#section-3.4.1
            #   domain-literal  = [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
            #
            #   dtext           = %d33-90 /          ; Printable US-ASCII
            #                       %d94-126 /         ;  characters not including
            #                       obs-dtext          ;  "[", "]", or "\"
            #
            #   obs-dtext       = obs-NO-WS-CTL / quoted-pair
            # End of domain literal
            if token == ISEMAIL_STRING_CLOSESQBRACKET:
                # TODO: FIX this to check domain literals
                pass
               # break
            elif token == ISEMAIL_STRING_BACKSLASH:
                data.push_element(ISEMAIL_CONTEXT_QUOTEDPAIR)
                data += token
                data += ISEMAIL_RFC5322_DOMLIT_OBSDTEXT
                # context_stack.append(context)
                # context = ISEMAIL_CONTEXT_QUOTEDPAIR
                # break
            # Folding White Space
            elif token in (ISEMAIL_STRING_CR, ISEMAIL_STRING_SP, ISEMAIL_STRING_HTAB):
                if token == ISEMAIL_STRING_CR and (++i == raw_length or email[i] != ISEMAIL_STRING_LF):
                    data += ISEMAIL_ERR_CR_NO_LF
                data += token
                data.push_element(ISEMAIL_CONTEXT_FWS)
                data += ISEMAIL_CFWS_FWS
                # context_stack.append(context)
                # context = ISEMAIL_CONTEXT_FWS
                token_prior = token
                # break
            else:
                # dtext
                
                # http:#tools.ietf.org/html/rfc5322#section-3.4.1
                #   dtext = %d33-90 /           Printable US-ASCII
                #                       %d94-126 /           characters not including
                #                       obs-dtext            "[", "]", or "\"
                #
                #   obs-dtext = obs-NO-WS-CTL / quoted-pair
                #
                #   obs-NO-WS-CTL = %d1-8 /             US-ASCII control
                #                       %d11 /               characters that do not
                #                       %d12 /               include the carriage
                #                       %d14-31 /            return, line feed, and
                #                       %d127                white space characters
                ord_chr = ord(token)

                # CR, LF, SP & HTAB have already been parsed above
                if ord_chr > 127 or ord_chr == 0 or token == ISEMAIL_STRING_OPENSQBRACKET:
                    data += ISEMAIL_ERR_EXPECTING_DTEXT    # Fatal error
                    # break
                elif ord_chr < 33 or ord_chr == 127:
                    data += ISEMAIL_RFC5322_DOMLIT_OBSDTEXT

                data += token

                # parsedata[ISEMAIL_COMPONENT_LITERAL] += token
                # parsedata[ISEMAIL_COMPONENT_DOMAIN] += token
                # atomlist[ISEMAIL_COMPONENT_DOMAIN][element_count] += token
                # element_len += 1
            # break

        elif data.context == ISEMAIL_CONTEXT_QUOTEDSTRING:
            #-------------------------------------------------------------
            # Quoted string
            #-------------------------------------------------------------
            # http:#tools.ietf.org/html/rfc5322#section-3.2.4
            #   quoted-string = [CFWS]
            #                       DQUOTE *([FWS] qcontent) [FWS] DQUOTE
            #                       [CFWS]
            #
            #   qcontent = qtext / quoted-pair
            # Quoted pair
            if token == ISEMAIL_STRING_BACKSLASH:
                data.push_element(ISEMAIL_CONTEXT_QUOTEDPAIR)
                # context_stack.append(context)
                # context = ISEMAIL_CONTEXT_QUOTEDPAIR
                # break
            # Folding White Space
            # Inside a quoted string, spaces are allowed as regular characters.
            # It's only FWS if we include HTAB or CRLF
            elif token == ISEMAIL_STRING_CR or token == ISEMAIL_STRING_HTAB:
                if token == ISEMAIL_STRING_CR and (++i == raw_length or email[i] != ISEMAIL_STRING_LF): 
                    data += ISEMAIL_ERR_CR_NO_LF
                    # break    # Fatal error

                # http:#tools.ietf.org/html/rfc5322#section-3.2.2
                #   Runs of FWS, comment, or CFWS that occur between lexical tokens in a
                #   structured header field are semantically interpreted as a single
                #   space character.

                # http:#tools.ietf.org/html/rfc5322#section-3.2.4
                #   the CRLF in any FWS/CFWS that appears within the quoted-string [is]
                #   semantically "invisible" and therefore not part of the quoted-string
                # parsedata[ISEMAIL_COMPONENT_LOCALPART] += ISEMAIL_STRING_SP
                # atomlist[ISEMAIL_COMPONENT_LOCALPART][element_count] += ISEMAIL_STRING_SP
                # element_len += 1

                data += ISEMAIL_CFWS_FWS
                data.push_element(ISEMAIL_CONTEXT_FWS)
                # return_status.append(ISEMAIL_CFWS_FWS)
                #context_stack.append(context)
                # context = ISEMAIL_CONTEXT_FWS
                token_prior = token
                # break

            elif token == ISEMAIL_STRING_DQUOTE:
                # End of quoted string
                data += token
                # atomlist[ISEMAIL_COMPONENT_LOCALPART][element_count] += token
                # element_len += 1
                context_prior = context
                data.pop_element()
                # context = context_stack.pop()
                # break
            else:
                # qtext
                # http:#tools.ietf.org/html/rfc5322#section-3.2.4
                #   qtext = %d33 /              Printable US-ASCII
                #                       %d35-91 /            characters not including
                #                       %d93-126 /           "\" or the quote character
                #                       obs-qtext
                #
                #   obs-qtext = obs-NO-WS-CTL
                #
                #   obs-NO-WS-CTL = %d1-8 /             US-ASCII control
                #                       %d11 /               characters that do not
                #                       %d12 /               include the carriage
                #                       %d14-31 /            return, line feed, and
                #                       %d127                white space characters
                ord_chr = ord(token)

                if ord_chr > 127 or ord_chr == 0 or ord_chr == 10:
                    data += ISEMAIL_ERR_EXPECTING_QTEXT    # Fatal error
                elif ord_chr < 32 or ord_chr == 127:
                    data += ISEMAIL_DEPREC_QTEXT

                data += token
                # atomlist[ISEMAIL_COMPONENT_LOCALPART][element_count] += token
                # element_len += 1

            # http:#tools.ietf.org/html/rfc5322#section-3.4.1
            #   If the
            #   string can be represented as a dot-atom (that is, it contains no
            #   characters other than atext characters or "." surrounded by atext
            #   characters), then the dot-atom form SHOULD be used and the quoted-
            #   string form SHOULD NOT be used.
            
            # To do :
            
            # break
        elif data.context == ISEMAIL_CONTEXT_QUOTEDPAIR:
            #-------------------------------------------------------------
            # Quoted pair
            #-------------------------------------------------------------
            # http:#tools.ietf.org/html/rfc5322#section-3.2.1
            #   quoted-pair = ("\" (VCHAR / WSP)) / obs-qp
            #
            #   VCHAR = %d33-126             visible (printing) characters
            #   WSP = SP / HTAB            white space
            #
            #   obs-qp = "\" (%d0 / obs-NO-WS-CTL / LF / CR)
            #
            #   obs-NO-WS-CTL = %d1-8 /             US-ASCII control
            #                       %d11 /               characters that do not
            #                       %d12 /               include the carriage
            #                       %d14-31 /            return, line feed, and
            #                       %d127                white space characters
            #
            # i.e. obs-qp = "\" (%d0-8, %d10-31 / %d127)
            ord_chr = ord(token)

            if ord_chr > 127:
                data += ISEMAIL_ERR_EXPECTING_QPAIR    # Fatal error
            elif ord_chr in broken_range((1, 8), (11, 11), (12, 12), (14, 31), (127, 127)):
                data += ISEMAIL_DEPREC_QP
            '''
            elif (ord_chr < 31 and ord_chr != 9) or ord_chr == 127:    # SP & HTAB are allowed
                return_status.append(ISEMAIL_DEPREC_QP)
            '''
            # At this point we know where this qpair occurred so
            # we could check to see if the character actually
            # needed to be quoted at all.
            # http:#tools.ietf.org/html/rfc5321#section-4.1.2
            #   the sending system SHOULD transmit the
            #   form that uses the minimum quoting possible.

            # Todo: check whether the character needs to be quoted (escaped) in this context

            data.pop_element()

            # context_prior = context
            # context = context_stack.pop()    # End of qpair
            token = ISEMAIL_STRING_BACKSLASH + token

            if data.context == ISEMAIL_CONTEXT_COMMENT:
                pass
            elif data.context in (ISEMAIL_CONTEXT_QUOTEDSTRING, ISEMAIL_COMPONENT_LITERAL):
                data += token
                data.element_len += 1
                # atomlist[ISEMAIL_COMPONENT_LOCALPART][element_count] += token
                # element_len += 2    # The maximum sizes specified by RFC 5321 are octet counts, so we must include the backslash
                # break
            else:
                raise ValueError("Quoted pair logic invoked in an invalid context: context")
            # break
            
        elif data.context == ISEMAIL_CONTEXT_COMMENT:
            #-------------------------------------------------------------
            # Comment
            #-------------------------------------------------------------
            # http:#tools.ietf.org/html/rfc5322#section-3.2.2
            #   comment = "(" *([FWS] ccontent) [FWS] ")"
            #
            #   ccontent = ctext / quoted-pair / comment
            # Nested comment
            if token == ISEMAIL_STRING_OPENPARENTHESIS:
                # Nested comments are OK
                data.push_element(ISEMAIL_CONTEXT_COMMENT)
                # context_stack.append(context)
                # context = ISEMAIL_CONTEXT_COMMENT
                # break
            # End of comment
            elif token == ISEMAIL_STRING_CLOSEPARENTHESIS:
                data.pop_element()
                # context_prior = context
                # context = context_stack.pop()

                # http:#tools.ietf.org/html/rfc5322#section-3.2.2
                #   Runs of FWS, comment, or CFWS that occur between lexical tokens in a
                #   structured header field are semantically interpreted as a single
                #   space character.
                #
                # is_email() author's note: This *cannot* mean that we must add a
                # space to the address wherever CFWS appears. This would result in
                # any addr-spec that had CFWS outside a quoted string being invalid
                # for RFC 5321.


                #                if ((context == ISEMAIL_COMPONENT_LOCALPART) or (context == ISEMAIL_COMPONENT_DOMAIN)) {
                #                    parsedata[context] += ISEMAIL_STRING_SP
                #                    atomlist[context][element_count] += ISEMAIL_STRING_SP
                #                    element_len++
                #                }

                # break
            elif token == ISEMAIL_STRING_BACKSLASH:
                # Quoted pair
                data.push_element(ISEMAIL_CONTEXT_QUOTEDPAIR)
                # context_stack.append(context)
                # context = ISEMAIL_CONTEXT_QUOTEDPAIR
                # break
            elif token in (ISEMAIL_STRING_CR, ISEMAIL_STRING_SP, ISEMAIL_STRING_HTAB):
                # Folding White Space
                if token == ISEMAIL_STRING_CR and (++i == raw_length or email[i] != ISEMAIL_STRING_LF):
                    data += ISEMAIL_ERR_CR_NO_LF
                    # break    # Fatal error

                data += ISEMAIL_CFWS_FWS
                data.push_element(ISEMAIL_CONTEXT_FWS)
                # context_stack.append(context)
                # context = ISEMAIL_CONTEXT_FWS
                token_prior = token
                # break
            else:
                # ctext
                # http:#tools.ietf.org/html/rfc5322#section-3.2.3
                #   ctext = %d33-39 /           Printable US-ASCII
                #                       %d42-91 /            characters not including
                #                       %d93-126 /           "(", ")", or "\"
                #                       obs-ctext
                #
                #   obs-ctext = obs-NO-WS-CTL
                #
                #   obs-NO-WS-CTL = %d1-8 /             US-ASCII control
                #                       %d11 /               characters that do not
                #                       %d12 /               include the carriage
                #                       %d14-31 /            return, line feed, and
                #                       %d127                white space characters
                ord_chr = ord(token)

                if ord_chr > 127 or ord_chr == 0 or ord_chr == 10:
                    data += ISEMAIL_ERR_EXPECTING_CTEXT    # Fatal error
                    # break
                elif ord_chr < 32 or ord_chr == 127:
                    data += ISEMAIL_DEPREC_CTEXT
                    # return_status.append()
                    # break
        elif context == ISEMAIL_CONTEXT_FWS:
            #-------------------------------------------------------------
            # Folding White Space
            #-------------------------------------------------------------
            # http:#tools.ietf.org/html/rfc5322#section-3.2.2
            #   FWS = ([*WSP CRLF] 1*WSP) /  obs-FWS
            #                                           Folding white space

            # But note the erratum:
            # http:#www.rfc-editor.org/errata_search.php?rfc=5322&eid=1908:
            #   In the obsolete syntax, any amount of folding white space MAY be
            #   inserted where the obs-FWS rule is allowed.  This creates the
            #   possibility of having two consecutive "folds" in a line, and
            #   therefore the possibility that a line which makes up a folded header
            #   field could be composed entirely of white space.
            #
            #   obs-FWS = 1*([CRLF] WSP)
            if token_prior == ISEMAIL_STRING_CR:
                if token == ISEMAIL_STRING_CR:
                    data += ISEMAIL_ERR_FWS_CRLF_X2    # Fatal error
                    # break
                crlf_count += 1
                if crlf_count > 1:
                    data += ISEMAIL_DEPREC_FWS    # Multiple folds = obsolete FWS

            if token == ISEMAIL_STRING_CR:
                if ++i == raw_length or email[i] != ISEMAIL_STRING_LF:
                    data += ISEMAIL_ERR_CR_NO_LF    # Fatal error
                    # break
            elif token == ISEMAIL_STRING_SP or token == ISEMAIL_STRING_HTAB:
                pass
            else:
                if token_prior == ISEMAIL_STRING_CR:
                    data += ISEMAIL_ERR_FWS_CRLF_END    # Fatal error
                    # break
                
                crlf_count = 0
                # if (isset(crlf_count)) unset(crlf_count

                # context_prior = context
                # context = context_stack.pop()    # End of FWS

                data.pop_element()
                # http:#tools.ietf.org/html/rfc5322#section-3.2.2
                #   Runs of FWS, comment, or CFWS that occur between lexical tokens in a
                #   structured header field are semantically interpreted as a single
                #   space character.
                #
                # is_email() author's note: This *cannot* mean that we must add a
                # space to the address wherever CFWS appears. This would result in
                # any addr-spec that had CFWS outside a quoted string being invalid
                # for RFC 5321.

                #                if ((context == ISEMAIL_COMPONENT_LOCALPART) or (context == ISEMAIL_COMPONENT_DOMAIN)) {
                #                    parsedata[context] += ISEMAIL_STRING_SP
                #                    atomlist[context][element_count] += ISEMAIL_STRING_SP
                #                    element_len++
                #                }

                i -= 1    # Look at this token again in the parent context

            token_prior = token
            # break

            #-echo "<td>context|",((end_or_die) ? 'True' : 'False'),"|token|" . max(return_status) . "</td></tr>" # debug
        elif max(data.max_response()) > ISEMAIL_RFC5322:
            if not all_errors:
                break    # No point going on if we've got a fatal error

        else:
            #-------------------------------------------------------------
            # A context we aren't expecting
            #-------------------------------------------------------------
            raise ValueError("Unknown context: context")
    

    # Some simple final tests
    if max(data.max_response()) < ISEMAIL_RFC5322:
        if data.context == ISEMAIL_CONTEXT_QUOTEDSTRING:
            data += ISEMAIL_ERR_UNCLOSEDQUOTEDSTR    # Fatal error
        elif data.context == ISEMAIL_CONTEXT_QUOTEDPAIR:
            data += ISEMAIL_ERR_BACKSLASHEND        # Fatal error
        elif data.context == ISEMAIL_CONTEXT_COMMENT:
            data += ISEMAIL_ERR_UNCLOSEDCOMMENT        # Fatal error
        elif data.context == ISEMAIL_COMPONENT_LITERAL:
            data += ISEMAIL_ERR_UNCLOSEDDOMLIT        # Fatal error
        elif token == ISEMAIL_STRING_CR:
            data += ISEMAIL_ERR_FWS_CRLF_END        # Fatal error
        elif data.domain_str == '':
            data += ISEMAIL_ERR_NODOMAIN            # Fatal error
        elif data.element_len == 0:
            data += ISEMAIL_ERR_DOT_END            # Fatal error
        elif hyphen_flag:
            data += ISEMAIL_ERR_DOMAINHYPHENEND        # Fatal error
        elif len(data.domain_str) > 255:
            # http:#tools.ietf.org/html/rfc5321#section-4.5.3.1.2
            #   The maximum total length of a domain name or number is 255 octets.
            data += ISEMAIL_RFC5322_DOMAIN_TOOLONG
        elif len(data) > 254:
            # http:#tools.ietf.org/html/rfc5321#section-4.1.2
            #   Forward-path = Path
            #
            #   Path = "<" [ A-d-l ":" ] Mailbox ">"
            #
            # http:#tools.ietf.org/html/rfc5321#section-4.5.3.1.3
            #   The maximum total length of a reverse-path or forward-path is 256
            #   octets (including the punctuation and element separators).
            #
            # Thus, even without (obsolete) routing information, the Mailbox can
            # only be 254 characters long. This is confirmed by this verified
            # erratum to RFC 3696:
            #
            # http:#www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690
            #   However, there is a restriction in RFC 2821 on the length of an
            #   address in MAIL and RCPT commands of 254 characters.  Since addresses
            #   that do not fit in those fields are not normally useful, the upper
            #   limit on address lengths should normally be considered to be 254.

            data += ISEMAIL_RFC5322_TOOLONG

        elif data.element_len > 63:
            data += ISEMAIL_RFC5322_LABEL_TOOLONG
            # http:#tools.ietf.org/html/rfc1035#section-2.3.4
            # labels          63 octets or less

    # Check DNS?
    dns_checked = False
    '''
    if check_dns and max(return_status) < ISEMAIL_DNSWARN:  # and function_exists('dns_get_record'):
        # http:#tools.ietf.org/html/rfc5321#section-2.3.5
        #   Names that can
        #   be resolved to MX RRs or address (i.e., A or AAAA) RRs (as discussed
        #   in Section 5) are permitted, as are CNAME RRs whose targets can be
        #   resolved, in turn, to MX or address RRs.
        #
        # http:#tools.ietf.org/html/rfc5321#section-5.1
        #   The lookup first attempts to locate an MX record associated with the
        #   name.  If a CNAME record is found, the resulting name is processed as
        #   if it were the initial name. ... If an empty list of MXs is returned,
        #   the address is treated as if it was associated with an implicit MX
        #   RR, with a preference of 0, pointing to that host.
        #
        # is_email() author's note: We will regard the existence of a CNAME to be
        # sufficient evidence of the domain's existence. For performance reasons
        # we will not repeat the DNS lookup for the CNAME's target, but we will
        # raise a warning because we didn't immediately find an MX record.
        if element_count == 0:
            parsedata[ISEMAIL_COMPONENT_DOMAIN] += '.'        # Checking TLD DNS seems to work only if you explicitly check from the root

        # todo fix this for python
        # result = @dns_get_record(parsedata[ISEMAIL_COMPONENT_DOMAIN], DNS_MX    # Not using checkdnsrr because of a suspected bug in PHP 5.3 (http:#bugs.php.net/bug.php?id=51844)
        result = []

        if not result:
            return_status.append(ISEMAIL_DNSWARN_NO_RECORD)            # Domain can't be found in DNS
        else:
            if len(result) == 0:
                return_status.append(ISEMAIL_DNSWARN_NO_MX_RECORD)        # MX-record for domain can't be found
                
                # todo: fix this for python
                # result = @dns_get_record(parsedata[ISEMAIL_COMPONENT_DOMAIN], DNS_A + DNS_CNAME
                result = []

                if len(result) == 0:
                    return_status.append(ISEMAIL_DNSWARN_NO_RECORD)        # No usable records for the domain can be found
            else:
                dns_checked = True
    '''
    # Check for TLD addresses
    # -----------------------
    # TLD addresses are specifically allowed in RFC 5321 but they are
    # unusual to say the least. We will allocate a separate
    # status to these addresses on the basis that they are more likely
    # to be typos than genuine addresses (unless we've already
    # established that the domain does have an MX record)
    #
    # http:#tools.ietf.org/html/rfc5321#section-2.3.5
    #   In the case
    #   of a top-level domain used by itself in an email address, a single
    #   string is used without any dots.  This makes the requirement,
    #   described in more detail below, that only fully-qualified domain
    #   names appear in SMTP transactions on the public Internet,
    #   particularly important where top-level domains are involved.
    #
    # TLD format
    # ----------
    # The format of TLDs has changed a number of times. The standards
    # used by IANA have been largely ignored by ICANN, leading to
    # confusion over the standards being followed. These are not defined
    # anywhere, except as a general component of a DNS host name (a label).
    # However, this could potentially lead to 123.123.123.123 being a
    # valid DNS name (rather than an IP address) and thereby creating
    # an ambiguity. The most authoritative statement on TLD formats that
    # the author can find is in a (rejected!) erratum to RFC 1123
    # submitted by John Klensin, the author of RFC 5321:
    #
    # http:#www.rfc-editor.org/errata_search.php?rfc=1123&eid=1353
    #   However, a valid host name can never have the dotted-decimal
    #   form #.#.#.#, since this change does not permit the highest-level
    #   component label to start with a digit even if it is not all-numeric.
    if not dns_checked and (max(data.max_response()) < ISEMAIL_DNSWARN):
        if data.element_count == 0:
            data += ISEMAIL_RFC5321_TLD

        # TODO: add this back
        '''
        if atomlist[ISEMAIL_COMPONENT_DOMAIN][element_count][0].isnumeric():
            return_status.append(ISEMAIL_RFC5321_TLDNUMERIC)
        '''
    '''
    return_status = set(return_status)
    final_status = max(return_status)
    # if len(return_status) != 1:
    #     array_shift(return_status) # remove redundant ISEMAIL_VALID

    parsedata['status'] = return_status

    if final_status < threshold:
        final_status = ISEMAIL_VALID

    if diagnose:
        return final_status
    else:
        return final_status < ISEMAIL_THRESHOLD
    '''