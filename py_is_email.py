import re
from collections import deque
from meta_data import *
from isemail_parsers import *
import sys

'''
class BrokenRange(object):

    def __init__(self, *ranges):
        self._ranges = []
        for r in ranges:
            self.add_range(*r)

    def add_range(self, *args):
        self._ranges.append(range(*args))

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
'''
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


class AddressItem(object):

    def __init__(self, threashold=None):
        self._threashold = threashold or 0
        self._elements = {}
        self._responses = []
        self._max_code = 0
        self.local_part = None
        self.domain_part = None

    def add_element(self, element_code, element):
        if element_code == ISEMAIL_ELEMENT_LOCALPART:
            self.local_part = element
        elif element_code == ISEMAIL_ELEMENT_DOMAINPART:
            self.local_part = element
        elif element_code in self._elements:
            self._elements[element_code].append(element)
        else:
            self._elements[element_code] = [element]

    def add_response(self, response_code, position):

        self._max_code = max(response_code, self._max_code)
        self._responses.append((response_code, position))

    def __int__(self):
        return self._max_code

    def responses(self, max_code=None, min_code=None, response_type='string_list'):
        """

        :param max_code:
        :type max_code:
        :param min_code:
        :type min_code:
        :param response_type: 'string_list'|'code_list'|'detailed_string'|'key_list'
        :type response_type: str
        :return:
        :rtype:
        """
        min_code = min_code or self._threashold
        max_code = max_code or ISEMAIL_MAX_THREASHOLD

        if response_type == 'code_list':
            return self._responses
        elif response_type == 'string_list':
            tmp_ret = []
            for i, pos in self._responses:
                tmp_ret.append(META_LOOKUP.diags[i]['description'])
            return tmp_ret
        elif response_type == 'key_list':
            tmp_ret = []
            for i, pos in self._responses:
                tmp_ret.append(META_LOOKUP.diags[i]['key'])
            return tmp_ret

    def __getitem__(self, item):
        try:
            return self._elements[item]
        except KeyError:
            return 'Unknown / Unfound'


class WorkQueue(object):
    def __init__(self):
        self.queue = []
        self.done = []
        self.length = 0

    def push(self, item):
        self.queue.append(item)
        self.length += 1

    def pop(self, count=1):
        if count > self.length:
            count = self.length

        for i in range(count):
            self.done.append(self.queue.pop())

        self.length -= count
        return self.last(count)

    def last(self, count=1):
        if count > self.length:
            count = self.length
        if count == 1:
            return self.done[1]
        else:
            return self.done[count:]

    def clear(self):
        self.queue = []
        self.done = []
        self.length = 0

    def __getitem__(self, item):
        return self.done[item]

class ParseString(object):

    def __init__(self,
                 raw_string=None,
                 parser=None,
                 parser_start_rule=None,
                 diag_codes=None):

        self.parser = parser or parser_ops.parse_email
        self.parser_start_rule = parser_start_rule or 'start'

        self.rem_string = deque()
        self.raw_string = None
        self.raw_length = 0
        self._diag_count = 0
        self._elements = {}
        self._diags = {}
        self.work = WorkQueue()
        self._max_diag = 0
        if raw_string is not None:
            self.parse(raw_string)

    def reset(self):
        self.rem_string.clear()
        self._elements.clear()
        self._diags.clear()
        self.work.clear()
        self._max_diag = 0

    def parse(self, raw_email):
        log_debug('Parse: %s', raw_email)
        self.reset()
        self.rem_string.extend(raw_email)
        self.raw_length = len(raw_email)
        self.parser(self, rule=self.parser_start_rule)

    @property
    def position(self):
        return self.raw_length - len(self.rem_string)

    def add_note(self, diag=None, position=None, element_name=None, element=None, element_pos=None):
        position = position or self.position

        if diag is not None:
            self._diag_count += 1
            tmp_diag = dict(
                position=position,
                count=self._diag_count)
            log_ddebug('adding diag: %s (%r)', diag, tmp_diag)
            if diag in self._diags:
                self._diags[diag].append(tmp_diag)
            else:
                self._diags[diag] = [tmp_diag]
            if diag > self._max_diag:
                self._max_diag = diag

        if element_name is not None:
            element_pos = element_pos or position-len(element)
            if isinstance(element, list):
                element = ''.join(element)

            if element_name in self._elements:
                self._elements[element_name].append(dict(
                    element=element,
                    pos=element_pos,
                ))
                log_ddebug('adding element: %s (%r)', element_name, self._elements[element_name])

            else:
                self._elements[element_name] = [dict(
                    element=element,
                    pos=element_pos,
                )]
                log_ddebug('adding element: %s (%r)', element_name, self._elements[element_name])


    def __int__(self):
        return self._max_diag

    def elements(self, element_name=None):
        if element_name is None:
            return self._elements.copy()
        else:
            return self._elements.get(element_name, [])

    def all_elements(self):
        return self._elements

    def diags(self, max_code=None, min_code=None, field=None, diag_code=None):
        min_code = min_code or -1
        max_code = max_code or sys.maxsize

        if diag_code is None:
            tmp_ret = {}
            for diag, items in self._diags.items():
                if min_code < diag < max_code:
                    if field is None:
                        tmp_ret[diag] = items
                    else:
                        tmp_ret[diag] = []
                        for i in items:
                            tmp_ret[diag].append(i[field])
            return tmp_ret
        else:
            if field is None:
                return self._diags[diag_code]
            else:
                tmp_ret = []
                for i in self._diags[diag_code]:
                    tmp_ret.append(i[field])
                return tmp_ret


    def remaining(self):
        return ''.join(self.rem_string)

    def __getitem__(self, item):
        return self.elements(element_name=item)

    def __call__(self, email_in):
        self.parse(email_in)
        return self._max_diag

'''
class ParseEmail(object):

    def __init__(self, raw_email=None, threashold=None, parser=None, parser_start_rule=None):

        self.parser = parser or parser_ops.parse_email
        self.parser_start_rule = parser_start_rule or 'start'

        self.rem_email = deque()
        self.raw_email = None
        self.raw_length = 0
        self.threashold = threashold or 0
        self._elements = {}
        self._diags = []
        self.work = WorkQueue()
        self._max_diag = {'value': 0}
        self.local_part = None
        self.domain_part = None
        self._parsing_local_part = False
        self._parsing_domain_part = False
        self._current_context = ISEMAIL_ELEMENT_LOCALPART
        self._element_pos = 0
        self._element_context_pos = 0

        if raw_email is not None:
            self.parse(raw_email)

    def reset(self):
        self.rem_email.clear()
        self._elements.clear()
        self._diags.clear()
        self.work.clear()
        self._max_diag = {'value': 0}
        self.local_part = None
        self.domain_part = None
        self._parsing_local_part = False
        self._parsing_domain_part = False
        self._current_context = ISEMAIL_ELEMENT_LOCALPART
        self._element_pos = 0
        self._element_context_pos = 0

    def parse(self, raw_email):
        log_debug('Parse: %s', raw_email)
        self.reset()
        self.rem_email.extend(raw_email)
        self.raw_length = len(raw_email)
        self._parsing_local_part = True
        self.parser(self, rule=self.parser_start_rule)

    def add_note(self, diag=None, position=None, element_name=None, element=None):
        if diag is not None:
            tmp_diag = dict(
                position=position or self.raw_length - len(self.rem_email),
                diag=META_LOOKUP.diags[diag])
            self._diags.append(tmp_diag)
            if tmp_diag['diag']['value'] > self._max_diag['value']:
                self._max_diag = tmp_diag

        if element_name is not None:
            if isinstance(element, list):
                element = ''.join(element)

            if element_name == ISEMAIL_ELEMENT_LOCALPART:
                self._parsing_local_part = False
                self._parsing_domain_part = True
                self.local_part = element
                self._element_context_pos = 0
                self._current_context = ISEMAIL_ELEMENT_DOMAINPART

            elif element_name == ISEMAIL_ELEMENT_DOMAINPART:
                self.local_part = element
                self._parsing_domain_part = False

            self._element_context_pos += 1
            self._element_pos += 1

            self._elements.append(dict(
                name=element_name,
                element=element,
                pos=self._element_pos,
                context_pos=self._element_context_pos,
                context=self._current_context
            ))

    def __int__(self):
        return self._max_diag['value']

    def elements(self, element_name=None, context=None, position=None):
        tmp_elements = []
        tmp_ret = []
        if element_name is None:
            tmp_elements = self._elements.copy()
        else:
            for e in self._elements:
                if e['name'] == element_name:
                    tmp_elements.append(e)

        for e in tmp_elements:

            if context is not None:
                if e['context'] == context:
                    tmp_ret.append(e['element'])
            else:
                    tmp_ret.append(e['element'])

        if position is not None:
            return tmp_ret[position]
        else:
            return tmp_ret

    def all_elements(self):
        return self._elements

    def diags(self, max_code=None, min_code=None, response_field=None):
        min_code = min_code or self.threashold
        max_code = max_code or ISEMAIL_MAX_THREASHOLD

        tmp_ret = []
        for i in self._diags:
            if min_code < i['value'] < max_code:
                if response_field is None:
                    tmp_ret.append(i)
                else:
                    tmp_ret.append(i[response_field])
        return tmp_ret

    def __getitem__(self, item):
        if item == ISEMAIL_ELEMENT_LOCALPART:
            return self.local_part
        elif item == ISEMAIL_ELEMENT_DOMAINPART:
            return self.domain_part
        else:
            try:
                return self.elements(element_name=item)
            except KeyError:
                return 'Unknown / Unfound'

    def __call__(self, email_in):
        self.parse(email_in)
        return self._max_diag
'''
