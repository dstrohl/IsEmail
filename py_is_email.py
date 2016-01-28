import re
from collections import deque
from meta_data import *

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
# /*.mixed. function is_email(email, checkDNS = False, errorlevel = False, &parsedata = array()) {

'''
class ElementClass(object):
    def __init__(self, parent, element_type):
        self.atoms = []
        self.element_type = element_type
        self.parent = parent
        # self.length = 0
        self.elements = 0

    def __iadd__(self, item):
        # self.length += 1
        self.parent.length += 1
        self.parent.element_len += 1
        self.atoms.append(item)

    def __str__(self):
        return ''.join(self.atoms)

    def __bool__(self):
        return bool(self.atoms)

    def __getitem__(self, item):
        return self.atoms[item]

    def __len__(self):
        return len(self.atoms)

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
        self.local_string = ''

        self.domain_part = []
        self.domain_string = ''

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
'''

class AddressItem(object):

    def __init__(self, threashold=None):
        self._threashold = threashold or 0
        self._elements = {}
        self._responses = []
        self._max_code = 0

    def add_element(self, element_code, element):
        self._elements[element_code] = element

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

class NoElementError(Exception):
    def __init__(self, is_email_obj, popped_text=None, fail_flag=None, position=None):
        if popped_text is not None:
            is_email_obj._rem_email.extendleft(popped_text)
        if fail_flag is not None:
            is_email_obj._add_response(response_code=fail_flag, position=position)


# AND = 'and'
# OR = 'or'
# OPT = 'opt'



def _meth(meth_name, **kwargs):
    return dict(
        meth='_get_%s' % meth_name,
        args=[],
        kwargs=kwargs)

def _char(char_set, **kwargs):
    kwargs['char_set'] = char_set
    return dict(
        meth='_get_set',
        args=[],
        kwargs=kwargs)

def _and(*methods, **kwargs):
    tmp_methods = []
    for m in methods:
        tmp_methods.append(_make_meth(m))
    return dict(
        meth='_get_and',
        args=tmp_methods,
        kwargs=kwargs)

def _or(*methods, **kwargs):
    tmp_methods = []
    for m in methods:
        tmp_methods.append(_make_meth(m))
    return dict(
        meth='_get_or',
        args=tmp_methods,
        kwargs=kwargs)

def _opt(method, **kwargs):
    method = _make_meth(method)
    return dict(
        meth='_get_opt',
        args=(method,),
        kwargs=kwargs)

def _c(*args):

    if len(args) == 1:
        min_count = ISEMAIL_MIN_COUNT
        max_count = ISEMAIL_MAX_COUNT
        opp = args[0]
    else:
        opp = args[1]
        first_arg = args[0]
        if isinstance(first_arg, int) or first_arg.isdigit():
            min_count = first_arg
            max_count = first_arg
        else:
            if '*' in first_arg:
                min_count, max_count = first_arg.split('*')
                if min_count == '':
                    min_count = ISEMAIL_MIN_COUNT
                if max_count == '':
                    max_count = ISEMAIL_MAX_COUNT
            else:
                raise AttributeError('"*" not in %s' % first_arg)

        min_count = int(min_count)
        max_count = int(max_count)

    opp = _make_meth(opp)

    return dict(
        meth='_get_count',
        args=[],
        kwargs=dict(
            min_count=min_count,
            max_count=max_count,
            opp=opp
        )
    )


def _make_meth(method, **kwargs):
    if isinstance(method, str):
        if '_get_%s' % method in IsEmail.__dict__:
            return _meth(method, **kwargs)

        elif method[0] == '"' and method[-1] == '"':
            # if it is a quoted string:  "do this"
            tmp_and_set = []
            for c in method[1:-1]:
                tmp_and_set.append(_make_meth(c))
            return _and(*tmp_and_set)

        elif method[0] in ISEMAIL_SET_COUNT:
            # if it has a counter in front: 1*2
            if method[1] in ISEMAIL_SET_COUNT:
                if method[2] in ISEMAIL_SET_COUNT:
                    return _c(method[:3], method[3:])
                else:
                    return _c(method[:2], method[2:])
            else:
                return _c(method[:1], method[1:])
        elif method [0] == '[' and method[-1] == ']':
            # if it is in square brackets:  [blah]
            tmp_opp = _make_meth(method[1:-1])
            return _opt(tmp_opp, **kwargs)

        else:
            # this is a string set
            return _char(method)
    else:
        return method




'''
class Get(object):
    def __call__(self, func_name, max_count=1):
        self.func_name = func_name
        self.max_count=max_count

class And(object):
    def __call__(self, methods):
        self.methods = methods

class Or(And):
    pass

class Opt(And):
    pass

'''
class IsEmail(object):

    def _setup(self):
        self._data = AddressItem()
        self._rem_email = None
        self._position = 0

    '''
    def _try(self, function, *args, pass_flag=None, element_code=None, fail_flag=None, **kwargs):
        tmp_ret = []
        try:
            function(tmp_ret, *args, **kwargs)
        except NoElementError:
            self._rem_email.extendleft(tmp_ret)
            if fail_flag is not None:
                self._add_response(response_code=fail_flag)
            raise

        if pass_flag is not None:
            self._add_response(response_code=pass_flag)

        if element_code is not None:
            self._add_element(element_code=element_code, element=tmp_ret)

        self._position += len(tmp_ret)
        return tmp_ret
    '''

    def __call__(self, email_in):
        self._setup()
        self.get_addr_spec(email_in)
        return self._data

    def _add_response(self, response_code, position=None):
        if position is None:
            position == self._raw_length - len(self._rem_email)
        if isinstance(response_code, str):
            response_code = META_LOOKUP.diags[response_code]['value']
        self._data.add_response(response_code, position)

    def _add_element(self, element_code, element):
        element = ''.join(element)
        self._data.add_element(element_code, element)

    def get_addr_spec(self, addr_in):
        """
            local-part "@" domain
        """
        self._raw_length = len(addr_in)
        self._data.raw_email = addr_in
        self._rem_email = deque(str(addr_in))

        if '@' not in self._data.raw_email:
            self._add_response('ERR_NODOMAIN', 0)
        else:
            try:
                self._get(_and('local_part', '1*@', 'domain_part'))
            except NoElementError:
                pass

    def _get_local_part(self):
        """
            dot-atom / quoted-string / obs-local-part
        """
        try:
            self._get(_or('dot_atom', 'quoted_string', 'obs_local_part'))
        except NoElementError as err:
            self._add_response('ERR_NOLOCALPART')
        # self._add_element(ISEMAIL_COMPONENT_LOCALPART, tmp_ret)
        # return tmp_ret

    def get_domain_part(self, max_count=1):
        """
            dot-atom / address-literal / obs-domain
        """
        try:
            tmp_ret = self._get(_or('dot_atom', 'address_literal', 'domain_literal', 'obs_domain'))
            self._add_element(ISEMAIL_COMPONENT_DOMAIN, tmp_ret)
        except NoElementError:
            self._add_response('ERR_NODOMAIN')


    def _get_dot_atom(self):
        """
        [CFWS] dot-atom-text [CFWS]
        """
        tmp_ret = self._get(_and('[cfws]', 'dot_atom_text', '[cfws]'))
        return tmp_ret

    def _get_quoted_string(self):
        """
            [CFWS] DQUOTE *([FWS] qcontent) [FWS] DQUOTE [CFWS]
        """
        self._get(_and(
                '[cfws]', '"',
                _c('*', _and('[fws]', 'qcontent')),
                '[fws]', '"', '[cfws]'))

    def _get_obs_local_part(self):
        """
            word *("." word)
        """
        tmp_ret = self._get(_and('word', _c('*', _and('.', 'word'))))
        self._add_element(ISEMAIL_COMPONENT_LOCALPART, tmp_ret)

    def _get_cfws(self):
        """
            (1*([FWS] comment) [FWS]) / FWS
        """
        self._get(_or(
            _c('1*', _and('[fws]', 'comment', '[fws]')),
            'fws'))

    def _get_fws(self):
        """
        ([*WSP CRLF] 1*WSP) /  obs-FWS
        """
        self._get(_or(_and(_opt(_and(_c('*','wsp'), 'crlf')),_c('1*','wsp')),'obs_fws'))

    def _get_obs_fws(self):
        """
            1*([CRLF] WSP)
        """
        self._get(_c('1*',_and('[crlf]', 'wsp')))

    def _get_ccontent(self):
        """
        ctext / quoted-pair / comment
        """
        tmp_ret = self._get(_or('ctext', 'quoted_pair', 'comment'))
        self._add_element(ISEMAIL_CONTEXT_COMMENT, tmp_ret)

    def _get_comment(self):
        """
         "(" *([FWS] ccontent) [FWS] ")"
        """
        self._get(_and(
            '(',
            _c('*', _and('[fws]', 'ccontent', '[fws]')),
            ')')
            )

    def _get_dot_atom_text(self):
        """
        1*atext *("." 1*atext)
        """
        tmp_ret = self._get(_and('atext', _and('.', 'atext')))
        self._add_element(ISEMAIL_COMPONENT_LOCALPART, tmp_ret)

    def get_qcontent(self):
        """
            qtext / quoted-pair
        """
        tmp_ret = self._get(_or('qtext', 'quoted_pair'))
        return tmp_ret

    def _get_quoted_pair(self):
        """
        ("\" (VCHAR / WSP)) / obs-qp
        """
        return self._get(_or(_and('\\',_or('vchar', 'wsp')), 'obs_gp'))


    def _get_obs_gp(self):
        """
        "\" (%d0 / obs-NO-WS-CTL / LF / CR)
        """
        tmp_ret = self._get(_and('\\', ISEMAIL_SET_OBS_QP))
        if tmp_ret:
            self._add_element(ISEMAIL_CONTEXT_COMMENT, tmp_ret)
            self._add_response(ISEMAIL_SET_OBS_QP)

    def _get_word(self, max_count=1):
        """
            atom / quoted-string
        """
        return self._get(_or('atom', 'quoted_string'))

    def _get_atom(self, max_count=1):
        """
            [CFWS] 1*atext [CFWS]
        """
        return self._get(_and(_opt('cfws'), 'atext', '[cfws]'))


    def _get_domain_literal(self, max_count=1):
        """
        [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
        """
        tmp_ret = self._get(_and('[cfws]', '[', _and('[fws]','dtext'), '[fws]', ']', '[cfws]'))
        self._add_response(ISEMAIL_RFC5322_DOMAINLITERAL)
        return tmp_ret

    def _get_dtext(self):
        """
            %d33-90 /          ; Printable US-ASCII
            %d94-126 /         ;  characters not including
            obs-dtext          ;  "[", "]", or "\"

            obs-dtext       =   obs-NO-WS-CTL / quoted-pair
        """
        tmp_ret = self._get(_or(ISEMAIL_SET_DTEXT, 'quoted_pair'))
        return tmp_ret

    def _get_obs_domain(self):
        """
        atom *("." atom)
        """
        tmp_ret = self._get(_and('atom', _c('*', _and('.', 'atom'))))
        self._add_element(ISEMAIL_COMPONENT_LOCALPART, tmp_ret)

    def _get_address_literal(self):
        """
            "[" ( IPv4-address-literal /
            IPv6-address-literal /
            General-address-literal ) "]"
        :return:
        """
        tmp_ret = self._get(_and('[', _or('ipv4_address_literal', 'ipv6_address_literal', 'general_address_literal'), ']'))
        self._add_response(ISEMAIL_RFC5321_ADDRESSLITERAL)
        return tmp_ret

    def _get_ipv4_address_literal(self):
        """
            Snum 3("."  Snum)
        """
        tmp_ret = self._get(_and('snum', _c('3', _and('.', 'snum'))))
        if tmp_ret:
            self._add_element(ISEMAIL_DOMAIN_LIT_IPV4)
            self._add_response(ISEMAIL_DOMAIN_LIT_IPV4)

    def _get_snum(self):
        """
            1*3DIGIT
                ; representing a decimal integer
                ; value in the range 0 through 255
        """
        tmp_ret = self._get(_or(
            ISEMAIL_SET_IPV4_19,
            _and(ISEMAIL_SET_IPV4_19, ISEMAIL_SET_DIGIT),
            _or(
                _and('1', ISEMAIL_SET_DIGIT, ISEMAIL_SET_DIGIT),
                _and('2', ISEMAIL_SET_IPV4_04, ISEMAIL_SET_DIGIT),
                _and('2', '5', ISEMAIL_SET_IPV4_05),
            )))
        return tmp_ret

    def _get_ipv6_address_literal(self):
        """
            "IPv6:" IPv6-addr
        """
        tmp_ret = self._get(_and('IPv6:', 'ipv6_addr'))

    def _get_ipv6_addr(self):
        """
            IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp
        """
        tmp_ret = self._get(_or('ipv6_full', 'ipv6_comp', 'ipv6v4_full', 'ipv6v4_comp'))

        # TODO: Validate IPv6 Address

        self._add_element(ISEMAIL_DOMAIN_LIT_IPV6, tmp_ret)

    def _get_ipv6_full(self):
        """
        IPv6-hex 7(":" IPv6-hex)
        """
        return self._get(_and('ipv6_hex', _c(7, _and(':', 'ipv6_hex'))))

    def _get_ipv6_comp(self):
        """
        [IPv6-hex *5(":" IPv6-hex)] "::" [IPv6-hex *5(":" IPv6-hex)]

              ; The "::" represents at least 2 16-bit groups of
              ; zeros.  No more than 6 groups in addition to the
              ; "::" may be present.
        """
        return self._get(_and(
            'ipv6_hex', _c('*5', _and(':', 'ipv6_hex')),
            '::',
            'ipv6_hex', _c('*5', _and(':', 'ipv6_hex')))),


    def _get_ipv6v4_full(self):
        """
        IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal
        """
        return self._get(_and('ipv6_hex', _c(5, _and(':', 'ipv6_hex')),'ipv4_address_literal'))

    def _get_ipv6v4_comp(self):
        """
        [IPv6-hex *3(":" IPv6-hex)] "::" [IPv6-hex *3(":" IPv6-hex) ":"] IPv4-address-literal
              ; The "::" represents at least 2 16-bit groups of
              ; zeros.  No more than 4 groups in addition to the
              ; "::" and IPv4-address-literal may be present.
        """
        return self._get(_and(
            'ipv6_hex', _c('*2', _and(':', 'ipv6_hex')),
            '::',
            'ipv6_hex', _c('*2', _and(':', 'ipv6_hex')),'ipv4_address_literal')),


    def _get_ipv6_hex(self):
        tmp_ret = self._get(
            _or(
                _c(1, ISEMAIL_SET_HEXDIG),
                _c(2, ISEMAIL_SET_HEXDIG),
                _c(3, ISEMAIL_SET_HEXDIG),
                _c(4, ISEMAIL_SET_HEXDIG))
        )
        return tmp_ret

    def get_general_address_literal(self):
        """
        Ldh-str ":" 1*dcontent
        """
        tmp_ret = self._get(_and(
            _c('*', ISEMAIL_SET_LTR_STR),
            ':',
            _c('*', 'dcontent')
        ))
        return tmp_ret

    def _get_wsp(self):
        return self._get_set(ISEMAIL_SET_WSP)

    def _get_ctext(self):
        tmp_ret = self._get_set(ISEMAIL_SET_CTEXT)
        self._add_element(ISEMAIL_CONTEXT_COMMENT, tmp_ret)

    def _get_qtext(self):
        return self._get_set(ISEMAIL_SET_QTEXT)

    def _get_atext(self):
        return self._get_set(ISEMAIL_SET_ATEXT)

    def _get_specials(self):
        return self._get_set(ISEMAIL_SET_SPECIALS)


    def _get_obs_no_ws_ctl(self):
        return self._get_set(ISEMAIL_SET_OBS_NO_WS_CTL)
    _get_obs_qtext = _get_obs_no_ws_ctl
    _get_obs_ctext = _get_obs_no_ws_ctl

    def _get_vchar(self):
        """
        %x21-7E            ; visible (printing) characters
        """
        tmp_ret = self._get(_c('*', ISEMAIL_SET_VTEXT))
        self._add_element(ISEMAIL_CONTEXT_COMMENT, tmp_ret)

    def _get_crlf(self):
        return self._get(ISEMAIL_SET_CRLF)

    def _get_count(self, min_count, max_count, opp):
        tmp_ret_list = []
        for i in range(len(self._rem_email)):
            if i > max_count-1:
                break
            try:
                tmp_ret = self._get(opp)
            except NoElementError:
                if i < min_count:
                    raise NoElementError(self, popped_text=tmp_ret_list)
            else:
                tmp_ret_list.append(tmp_ret)
        return tmp_ret_list


    def _get_set(self, char_set, count=0):
        tmp_ret = []
        for i in range(len(self._rem_email)):
            if self._rem_email[0] in char_set:
                tmp_ret.append(self._rem_email.popleft())
                if count-1 == i:
                    break
            else:
                break
        if tmp_ret:
            self._position += len(tmp_ret)
        else:
            raise NoElementError(self)
        return tmp_ret

    def _get(self, opp):
        opp = _make_meth(opp)
        '''
        if isinstance(opp, str):
            tmp_meth = getattr(self, opp)
            return tmp_meth()

        else:
        '''
        tmp_meth = getattr(self, opp['meth'])
        return tmp_meth(*opp['args'], **opp['kwargs'])

    def _get_and(self, *args, count=1):
        tmp_ret_list = []
        for i in range(len(self._rem_email)):
            for arg in args:
                try:
                    tmp_ret = self._get(arg)
                except NoElementError:
                    raise NoElementError(self, popped_text=tmp_ret_list)
                else:
                    if tmp_ret is not None:
                        tmp_ret_list.extend(tmp_ret)

            if count-1 == i:
                break

        if not tmp_ret_list:
            raise NoElementError(self)
        return tmp_ret_list

    def _get_or(self, *args, count=0):
        for arg in args:
            try:
                return self._get(arg)
            except NoElementError:
                pass
        raise NoElementError(self)

    def _get_opt(self, arg, count=0):
        """
        pass args as follows:

        ('_get_and','blah')
        ('_get_and',('blah',1)
        '_get_blah'
        ('_get_blah', 1)

        :param self:
        :param args:
        :return:
        """
        try:
            return self._get(arg)
        except NoElementError:
            return []


is_email = IsEmail()
