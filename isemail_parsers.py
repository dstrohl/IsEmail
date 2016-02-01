from meta_data import *
from collections import deque
# import logging

# log = logging.getLogger(__name__)

class NoElementError(Exception):
    def __init__(self, is_email_obj=None, popped_text=None, fail_flag=None, position=None):
        if popped_text is not None:
            is_email_obj.rem_email.extendleft(popped_text)
        if fail_flag is not None:
            is_email_obj.add_note(diag=fail_flag, pos=position)


def make_char_str(*chars_in):
    tmp_ret = []
    for char in chars_in:
        if isinstance(char, str):
            tmp_ret.append(char)
        elif isinstance(char, int):
            tmp_ret.append(chr(char))
        elif isinstance(char, tuple):
            for c in range(char[0], char[1]):
                tmp_ret.append(chr(c))
    return ''.join(tmp_ret)

obs_no_ws_ctl = make_char_str((1, 8), 11, 12, (14, 31), 127)

EMAIL_PARSER_CONST = dict(
    AT='@',
    BACKSLASH='\\',
    CLOSEPARENTHESIS=')',
    CLOSESQBRACKET=']',
    COLON=':',
    CR="\r",
    DOT='.',
    DOUBLECOLON='::',
    DQUOTE='"',
    HTAB="\t",
    HYPHEN='-',
    IPV6TAG='ipv6:',
    LF="\n",
    OPENPARENTHESIS='(',
    OPENSQBRACKET='[',
    SP=' ',

    # US-ASCII visible characters not valid for atext (http:#tools.ietf.org/html/rfc5322#section-3.2.3)

    ATEXT=make_char_str((68, 90), (48, 57), (97, 122), "!#$%&'*+-=?^_`{|}~"),
    CRLF='\r\n',
    CTEXT=make_char_str((33, 39), (42, 91), 93, 126, obs_no_ws_ctl),
    DCONTENT=make_char_str((33, 90), (94, 126)),
    DIGIT='1234567890',
    DTEXT=make_char_str((33, 90), (94, 126), obs_no_ws_ctl),
    HEXDIG='1234567890abcdefABCDEF',
    IPV4_04='01234',
    IPV4_05='012345',
    IPV4_12='12',
    IPV4_19='123456789',
    LTR_STR=make_char_str((68, 90), (48, 57), (97, 122)),
    OBS_CTEXT=obs_no_ws_ctl,
    OBS_DTEXT=obs_no_ws_ctl,
    OBS_NO_WS_CTL=make_char_str((1, 8), 11, 12, (14, 31), 127),
    OBS_QP=make_char_str(0, obs_no_ws_ctl, '\r', '\n'),
    OBS_QTEXT=obs_no_ws_ctl,
    QTEXT=make_char_str(33, (35, 91), (93, 126), obs_no_ws_ctl),
    REPEAT_FLAGS='1234567890*',
    SPECIALS='()<>[]:;@\\,."',
    VTEXT=make_char_str((33, 126)),
    WSP=' \t',
)


class ParserOps(object):

    @staticmethod
    def _make_meth(method, **kwargs):
        if isinstance(method, str):
            if method[0] == '"' and method[-1] == '"':
                # if it is a quoted string:  "do this"
                tmp_and_set = []
                for c in method[1:-1]:
                    tmp_and_set.append(ParserOps._make_meth(c))
                return ParserOps._and(*tmp_and_set)

            elif method[0] == '[' and method[-1] == ']':
                # if it is in square brackets:  [blah]
                tmp_opp = ParserOps._make_meth(method[1:-1])
                return ParserOps._opt(tmp_opp, **kwargs)

            else:
                # this is a string set
                try:
                    return ParserOps._char(EMAIL_PARSER_CONST[method])
                except KeyError:
                    try:
                        return ParserOps._rule(method)
                    except KeyError:
                        if method[0] == '_':
                            return ParserOps._meth(method)
                        else:
                            return ParserOps._char(method)
        else:
            return method

    @staticmethod
    def _meth(meth_name, **kwargs):
        return dict(
            meth='_get_%s' % meth_name,
            method=getattr(ParserOps, '_get_%s' % meth_name),
            args=[],
            kwargs=kwargs)

    @staticmethod
    def _rule(rule_name):
        return dict(
            meth='_get_rule',
            method=ParserOps._get_rule,
            args=[],
            kwargs={'rule_name': rule_name})

    @staticmethod
    def _char(char_set, **kwargs):
        kwargs['char_set'] = char_set
        return dict(
            meth='_get_char',
            method=ParserOps._get_char,
            args=[],
            kwargs=kwargs)

    @staticmethod
    def _and(*methods, **kwargs):
        tmp_methods = []
        for m in methods:
            tmp_methods.append(ParserOps._make_meth(m))
        return dict(
            meth='_get_and',
            method=ParserOps._get_and,
            args=tmp_methods,
            kwargs=kwargs)

    @staticmethod
    def _or(*methods, **kwargs):
        tmp_methods = []
        for m in methods:
            tmp_methods.append(ParserOps._make_meth(m))
        return dict(
            meth='_get_or',
            method=ParserOps._get_or,
            args=tmp_methods,
            kwargs=kwargs)

    @staticmethod
    def _opt(op, **kwargs):
        op = ParserOps._make_meth(op)
        if op['meth'] == '_get_char':
            op['kwargs']['optional'] = True
            return op
        else:
            return dict(
                meth='_get_opt',
                method=ParserOps._get_opt,
                args=(op,),
                kwargs=kwargs)

    @staticmethod
    def _c(*args):

        if len(args) == 1:
            min_count = ISEMAIL_MIN_COUNT
            max_count = ISEMAIL_MAX_COUNT
            op = args[0]
        else:
            op = args[1]
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

        op = ParserOps._make_meth(op)

        if op['meth'] in ('_get_char', '_get_and'):
            op['kwargs']['min_count'] = min_count
            op['kwargs']['max_count'] = max_count
            return op
        else:
            return dict(
                meth='_get_count',
                method=ParserOps._get_count,
                args=[],
                kwargs=dict(
                    min_count=min_count,
                    max_count=max_count,
                    op=op
                )
            )

    @staticmethod
    def _m(op, on_fail=None, on_pass=None, element_name=None, return_string=False):
        op = ParserOps._make_meth(op)

        if op['meth'] in ('_get_char', '_get_and', '_get_or', '_get_count'):
            op['kwargs']['on_fail'] = on_fail
            op['kwargs']['on_pass'] = on_pass
            op['kwargs']['element_name'] = element_name
            op['kwargs']['return_string'] = return_string

            return op

        elif op['meth'] == '_get_opt' and on_fail is None and on_pass is None and element_name is None:
            op['return_string'] = return_string
            return op

        else:
            return dict(
                meth='_get_mark',
                method=ParserOps._get_mark,
                args=[],
                kwargs=dict(
                    op=op,
                    on_fail=on_fail,
                    on_pass=on_pass,
                    element_name=element_name,
                    return_string=return_string)
            )

    @staticmethod
    def _l(op, char_set, on_fail=None, on_pass=None, only_on_fail=False, only_on_pass=False):
        op = ParserOps._make_meth(op)

        return dict(
            meth='_get_look',
            method=ParserOps._get_look,
            args=[],
            kwargs=dict(
                op=op,
                char_set=char_set,
                on_fail=on_fail,
                on_pass=on_pass,
                only_on_pass=only_on_pass,
                only_on_fail=only_on_fail)
        )

    @staticmethod
    def parse_email(data):
        if data.rem_email is not None and data.rem_email != '':
            if isinstance(data.rem_email, str):
                data.rem_email = deque(data.rem_email)

            if '@' not in data.rem_email:
                data.add_note(diag='ERR_NO_DOMAIN_SEP', pos=0)
            else:
                try:
                    start_meth = EMAIL_PARSER_RULES['addr_spec']
                    start_meth['method'](data, *start_meth['args'], **start_meth['kwargs'])
                except NoElementError:
                    pass
        else:
            data.add_note(diag='ERR_EMPTY_ADDRESS', pos=0)

    @staticmethod
    def _get(data, op):
        if not isinstance(op, dict):
            op = ParserOps._make_meth(op)
        return op['method'](data, *op['args'], **op['kwargs'])

    @staticmethod
    def _get_char(data, char_set, min_count=0, max_count=None, optional=False,
                  return_string=True, on_fail=None, on_pass=None, element_name=None):
        log_debug('checking for chars in -->%s<--', char_set)
        try:
            tmp_ret = []
            for i in range(len(data.rem_email)):
                tmp_next_char = data.rem_email[0]
                log_ddebug('    checking: %s', tmp_next_char)
                if max_count is not None and i > max_count-1:
                    log_ddebug('    found, max_count (%s) met!', max_count)
                    break

                if tmp_next_char in char_set:
                    tmp_ret.append(data.rem_email.popleft())
                    log_ddebug('     found', tmp_next_char)
                elif i < min_count-1:
                    log_ddebug('     missed, min_count (%s) not met!', min_count)
                    raise NoElementError(data, popped_text=tmp_ret)
                else:
                    log_ddebug('    missed')
                    break
            if tmp_ret:
                data.position += len(tmp_ret)
                if on_pass or element_name:
                    data.add_note(diag=on_pass, element_name=element_name, element=tmp_ret)
                if return_string:
                    return tmp_ret
                else:
                    return []
            else:
                raise NoElementError(data)
        except NoElementError:
            if not optional:
                raise NoElementError(data, fail_flag=on_fail)

    @staticmethod
    def _get_rule(data, rule_name):
        log_debug('getting rule "%s"', rule_name)
        return ParserOps._get(data, EMAIL_PARSER_RULES[rule_name])

    @staticmethod
    def _get_and(data, *operations, min_count=1, max_count=None, optional=False, return_string=True,
                 on_fail=None, on_pass=None, element_name=None):
        tmp_ret_list = []
        log_debug('all must match---')
        try:
            for i in range(len(data.rem_email)):
                if max_count is not None and i > max_count-1:
                    break

                for op in operations:
                    try:
                        tmp_ret = op['method'](data, *op['args'], **op['kwargs'])
                        # tmp_ret = self._get(op, data)
                    except NoElementError:
                        raise NoElementError(data, popped_text=tmp_ret_list)
                    else:
                        if tmp_ret is not None:
                            tmp_ret_list.extend(tmp_ret)

                if i < min_count-1:
                    raise NoElementError(data, popped_text=tmp_ret_list)

            if not tmp_ret_list:
                raise NoElementError()

            if on_pass or element_name:
                data.add_note(diag=on_pass, element_name=element_name, element=tmp_ret_list)
            log_debug('end of and-------, returning: %s', tmp_ret_list)
            if return_string:
                return tmp_ret_list
            else:
                return []

        except NoElementError:
            if not optional:
                raise NoElementError(data, fail_flag=on_fail)


    @staticmethod
    def _get_or(data, *operations, optional=False, return_string=True,
                on_fail=None, on_pass=None, element_name=None):
        tmp_ret = []
        try:
            for op in operations:
                try:
                    # tmp_ret = self._get(op, data)
                    tmp_ret = op['method'](data, *op['args'], **op['kwargs'])
                    break
                except NoElementError:
                    pass

            if tmp_ret:
                if on_pass or element_name:
                    data.add_note(diag=on_pass, element_name=element_name, element=tmp_ret)

                if return_string:
                    return tmp_ret
                else:
                    return []

            raise NoElementError(data)
        except NoElementError:
            if not optional:
                raise NoElementError(data, fail_flag=on_fail)

    @staticmethod
    def _get_opt(data, op, return_string=True):
        try:
            # tmp_ret = self._get(operation, data)
            tmp_ret = op['method'](data, *op['args'], **op['kwargs'])

            if return_string:
                return tmp_ret
            else:
                return []
        except NoElementError:
            return []

    @staticmethod
    def _get_count(data, min_count, max_count, op, optional=False, return_string=True,
                   on_fail=None, on_pass=None, element_name=None):
        tmp_ret_list = []
        try:
            for i in range(len(data.rem_email)):
                if i > max_count-1:
                    break
                try:
                    tmp_ret = op['method'](data, *op['args'], **op['kwargs'])

                    # tmp_ret = self._get(op, data)
                except NoElementError:
                    if i < min_count-1:
                        raise NoElementError(data, popped_text=tmp_ret_list)
                else:
                    tmp_ret_list.append(tmp_ret)

            if tmp_ret_list:
                if on_pass or element_name:
                    data.add_note(diag=on_pass, element_name=element_name, element=tmp_ret_list)
                if return_string:
                    return tmp_ret_list
            else:
                return []

        except NoElementError:
            if not optional:
                raise NoElementError(fail_flag=on_fail)

    @staticmethod
    def _get_mark(data, op, on_fail=None, on_pass=None, element_name=None, return_string=False):
        try:
            tmp_ret = op['method'](data, *op['args'], **op['kwargs'])
            # tmp_ret = self._get(op, data)
        except NoElementError:
            if on_fail is not None:
                data.add_note(diag=on_fail)
            raise
    
        if on_pass is not None:
            data.add_note(diag=on_pass)
    
        if element_name is not None:
            data.add_note(element_name=element_name, element=tmp_ret)
    
        if return_string:
            return tmp_ret

    @staticmethod
    def _get_look(data, op, char_set, on_fail=None, on_pass=None,
                  only_on_fail=False, only_on_pass=False):
        passed = True
        get_look = False
        tmp_ret = []
        try:
            tmp_ret = op['method'](data, *op['args'], **op['kwargs'])
        except NoElementError:
            passed = False

        if only_on_fail or only_on_pass:
            if passed and only_on_pass:
                get_look = True
            elif not passed and only_on_fail:
                get_look = True
        else:
            get_look = True

        if get_look:
            if data.rem_email[0] in char_set:
                if on_pass is not None:
                    data.add_note(diag=on_pass)
            else:
                if on_fail is not None:
                    data.add_note(diag=on_fail)
        return tmp_ret


_and = ParserOps._and
_meth = ParserOps._meth
_char = ParserOps._char
_or = ParserOps._or
_opt = ParserOps._opt
_c = ParserOps._c
_m = ParserOps._m
_l = ParserOps._l


EMAIL_PARSER_RULES = dict(
    addr_spec=_and(
        # local-part "@" domain
        _m('local_part', on_fail='ERR_NO_LOCAL_PART', element_name=ISEMAIL_ELEMENT_LOCALPART),
        '1@',
        _m('domain_part', on_fail='ERR_NO_DOMAIN_PART', element_name=ISEMAIL_ELEMENT_DOMAINPART)),

    local_part=_or(
        _m('dot_atom', element_name=ISEMAIL_ELEMENT_LOCALPART, return_string=True),
        _m('quoted_string', on_pass='RFC5321_QUOTED_STRING', return_string=True),
        _m('obs_local_part', on_pass='DEPREC_LOCAL_PART', return_string=True)),

    domain_part=_or(
        # dot-atom / address-literal / obs-domain
        'dot_atom', 'address_literal', 'domain_literal', 'obs_domain'),

    dot_atom=_and(
        # [CFWS] dot-atom-text [CFWS]
        _m('[cfws]', return_string=False),
        _m('dot_atom_text', return_string=True),
        _m('[cfws]', return_string=False)),

    quoted_string=_m(
        # [CFWS] DQUOTE *([FWS] qcontent) [FWS] DQUOTE [CFWS]
        _and(
            _m('[cfws]', return_string=False),
            _m('"', return_string=False),
            _c('*', _and(
                    'fws',
                    _m('qcontent', return_string=True))),
            _m('[fws]', return_string=False),
            _m('"', on_fail='UNCLOSED_QUOTED_STR', return_string=False),
            _m('[cfws]', return_string=False)),
        on_pass='QUOTED_STR', return_string=True),

    obs_local_part=_and(
        # word *("." word)
        'word',
        _c('*', _and(
            '.',
            'word'))),

    cfws=_or(
        # (1*([FWS] comment) [FWS]) / FWS
        _c('1*', _and(
            _m('[fws]', return_string=False),
            _m('comment', return_string=True),
            _m('[fws]', return_string=False))),
        _m('fws', return_string=False)),

    fws=_or(
        # ([*WSP CRLF] 1*WSP) /  obs-FWS
        _and(
            _opt(
                _and(
                    _c('*', 'WSP'),
                    'CRLF')),
            _c('1*', 'WSP')),
        _m('obs_fws', on_pass='DEPREC_FWS')),

    obs_fws=_c(
        # 1*([CRLF] WSP)
        '1*',
        _and(
            '[CRLF]',
            'WSP')),

    ccontent=_or(
        # ctext / quoted-pair / comment
        _m('CTEXT', return_string=True),
        _m('quoted_pair', return_string=True, on_pass='QUOTED_PAIR'),
        _m('comment', return_string=True)),

    comment=_and(
        #  "(" *([FWS] ccontent) [FWS] ")"
        '(',
        _c('*',
           _and(
                _m('[fws]', return_string=False),
                'ccontent',
                _m('[fws]', return_string=False))),
        _m(')', on_fail='UNCLOSED_COMMENT')),

    dot_atom_text=_and(
        # 1*atext *("." 1*atext)
        'ATEXT',
        _and(
            '.',
            'ATEXT')),

    qcontent=_or(
        # qtext / quoted-pair
        'QTEXT',
        'quoted_pair'),

    quoted_pair=_or(
        # ("\" (VCHAR / WSP)) / obs-qp
        _and(
            '\\',
            _or(
                'VCHAR',
                'WSP')),
        'obs_gp'),

    obs_gp=_and(
        # "\" (%d0 / obs-NO-WS-CTL / LF / CR)
        '\\',
        _m('OBS_QP', element_name=ISEMAIL_ELEMENT_QUOTEDSTRING, on_pass='OBS_QP')),

    word=_or(
        # atom / quoted-string
        'atom', 'quoted_string'),

    atom=_and(
        # [CFWS] 1*atext [CFWS]
        _opt('cfws'),
        'ATEXT',
        '[cfws]'),

    domain_literal=_m(
        # [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
        _and(
            '[cfws]',
            '[',
            _and(
                '[fws]',
                'DTEXT'),
            '[fws]',
            ']',
            '[cfws]'),
        on_pass='DOMAIN_LITERAL'),

    dtext=_or(
        #    %d33-90 /          ; Printable US-ASCII
        #    %d94-126 /         ;  characters not including
        #    obs-dtext          ;  "[", "]", or "\"

        #    obs-dtext       =   obs-NO-WS-CTL / quoted-pair
        'DTEXT',
        'quoted_pair'),

    obs_domain=_and(
        # atom *("." atom)
        'atom',
        _c('*',
           _and(
                '.',
                'atom'))),

    address_literal=_and(
        #    "[" ( IPv4-address-literal /
        #    IPv6-address-literal /
        #    General-address-literal ) "]"
        '[',
        _or(
            _m('ipv4_address_literal', element_name=ISEMAIL_ELEMENT_DOMAIN_LIT_IPV4),
            _m('ipv6_address_literal', element_name=ISEMAIL_ELEMENT_DOMAIN_LIT_IPV6),
            _m('general_address_literal', element_name=ISEMAIL_ELEMENT_DOMAIN_LIT_GEN)),
        ']'),

    ipv4_address_literal=_and(
        # Snum 3("."  Snum)
        'snum',
        _c('3', _and('.', 'snum'))),

    snum=_or(
        # 1*3DIGIT   ; representing a decimal integer value in the range 0 through 255
        'IPV4_19',
        _and('IPV4_19', 'DIGIT'),
        _or(
            _and('1', 'DIGIT', 'DIGIT'),
            _and('2', 'IPV4_04', 'DIGIT'),
            _and('2', '5', 'IPV4_05'),
        )),

    ipv6_address_literal=_and(
        # "IPv6:" IPv6-addr
        'IPv6:', 'ipv6_addr'),

    ipv6_addr=_or(
        # IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp
        'ipv6_full', 'ipv6_comp', 'ipv6v4_full', 'ipv6v4_comp'),

    ipv6_full=_and(
        # IPv6-hex 7(":" IPv6-hex)
        'ipv6_hex',
        _c(7, _and(
            ':',
            'ipv6_hex'))),

    ipv6_comp=_and(
        # [IPv6-hex *5(":" IPv6-hex)] "::" [IPv6-hex *5(":" IPv6-hex)]
        #
        #      ; The "::" represents at least 2 16-bit groups of
        #      ; zeros.  No more than 6 groups in addition to the
        #      ; "::" may be present.
        'ipv6_hex',
        _c('*5', _and(
            ':',
            'ipv6_hex')),
        '::',
        'ipv6_hex',
        _c('*5', _and(
            ':',
            'ipv6_hex'))),

    ipv6v4_full=_and(
        # IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal
        'ipv6_hex',
        _c(5, _and(
            ':',
            'ipv6_hex')),
        'ipv4_address_literal'),

    ipv6v4_comp=_and(
        # [IPv6-hex *3(":" IPv6-hex)] "::" [IPv6-hex *3(":" IPv6-hex) ":"] IPv4-address-literal
        #      ; The "::" represents at least 2 16-bit groups of
        #      ; zeros.  No more than 4 groups in addition to the
        #      ; "::" and IPv4-address-literal may be present.
        'ipv6_hex', _c('*2', _and(':', 'ipv6_hex')),
        '::',
        'ipv6_hex', _c('*2', _and(':', 'ipv6_hex')),
        'ipv4_address_literal'),

    ipv6_hex=_or(
        # 1*4HEXDIG
        _c('1*4', 'HEXDIG')),

    general_address_literal=_and(
        # Ldh-str ":" 1*dcontent
        _c('*', 'LTR_STR'),
        ':',
        _c('*', 'dcontent')
        ),

)
