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
    VCHAR=make_char_str((33, 126)),
    WSP=' \t',
)

EMAIL_PARSER_CONSOLIDATABLE = {
    'count': ('and', 'char'),
    'mark': ('char', 'and', 'or', 'count', 'opt'),
}

EMAIL_PARSER_OPS = {}
'''
class ParserRule(object):
    parser = ParserOps()
    _def_op = ''

    def __init__(self,
                 *ops,
                 name='',
                 operation=None,
                 min_count=0,
                 max_count=None,
                 return_string=True,
                 on_pass=None,
                 on_fail=None,
                 optional=False,
                 char_set=None,
                 next_char_check=None
                 ):
        self.operation = operation or self._def_op
        self.min_count = min_count
        self.max_count = max_count
        self.return_string = return_string
        self.on_pass = on_pass
        self.on_fail = on_fail
        self.optional = optional
        self.char_set = char_set
        self.char_string = None
        self.next_char_check = next_char_check or []

    def add_ops(self, *ops):
        self.ops.extend(ops)

'''
class ParserRule(object):
    rule_type = ''
    # single_op = False
    # parser = ParserOps
    parser_ops = EMAIL_PARSER_OPS

    def __init__(self,
                 *ops,
                 meth=None,
                 **kwargs):
        self.rule_type = meth
        self.kwargs = kwargs
        self.ops = ops

    @property
    def op(self):
        return self.ops[0]

    def __repr__(self):
        if self.rule_type == 'char':
            tmp_ret = 'char(%s)' % self.kwargs['char_set']
        elif self.rule_type in ('and', 'or'):
            tmp_ret_list = []
            for r in self.ops:
                tmp_ret_list.append('%r' % r)
            tmp_ret = '%s(%s)' % (self.rule_type, ', '.join(tmp_ret_list))
        else:
            tmp_ret = 'rule(%r)' % self.op

        return tmp_ret

    def _can_consolidate(self, other_type, **kwargs):
        tmp_ret = False
        if self.rule_type in EMAIL_PARSER_CONSOLIDATABLE[other_type]:
            if other_type == 'mark' and self.rule_type == 'opt':
                if kwargs['on_fail'] is None and kwargs['on_pass'] is None and kwargs['element_name'] is None:
                    tmp_ret = True
            else:
                tmp_ret = True
        if tmp_ret:
            self.kwargs.update(kwargs)
        return tmp_ret

    def __call__(self, parser, data):
        method = getattr(parser, '_get_%s' % self.rule_type)
        return method(data, *self.ops, **self.kwargs)


def _make_meth(method, **kwargs):
    log_ddebug('          making method object for -->%r<--', method)
    if isinstance(method, str):
        if method[0] == '"' and method[-1] == '"':
            # if it is a quoted string:  "do this"
            tmp_and_set = []
            for c in method[1:-1]:
                tmp_and_set.append(_char(c))
            log_ddebug('               "QSTRING" method')
            return _and(*tmp_and_set)

        elif method[0] == '[' and method[-1] == ']':
            # if it is in square brackets:  [blah]
            tmp_opp = _make_meth(method[1:-1])
            log_ddebug('               "OPT" method')
            return _opt(tmp_opp, **kwargs)

        else:
            # this is a string set
            try:
                log_ddebug('               trying "CONST(CHAR)" method')
                return _char(EMAIL_PARSER_CONST[method])
            except KeyError:
                if method[0] == '_':
                    log_ddebug('               trying "METH" method')
                    return _meth(method)
                else:
                    log_ddebug('               trying "RULE" method')
                    return _rule(method)
    else:
        log_ddebug('               falling through, is already a method')
        return method

def _meth(meth_name, **kwargs):
    return ParserRule(meth=meth_name)

def _rule(rule_name):
    if rule_name not in EMAIL_PARSER_OPS:
        EMAIL_PARSER_OPS[rule_name] = ParserRule(
            rule_name,
            meth='rule')

    return EMAIL_PARSER_OPS[rule_name]

def _char(char_set, **kwargs):
    return ParserRule(
        meth='char',
        char_set=char_set)

def _and(*methods):
    tmp_methods = []
    for m in methods:
        tmp_methods.append(_make_meth(m))
    return ParserRule(
        *tmp_methods,
        meth='and')

def _or(*methods):
    tmp_methods = []
    for m in methods:
        tmp_methods.append(_make_meth(m))
    return ParserRule(
        *tmp_methods,
        meth='or')

def _opt(op, **kwargs):
    op = _make_meth(op)

    if op._can_consolidate('opt', optional=True):
        return op
    else:
        return ParserRule(op, meth='opt')

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

    op = _make_meth(op)

    if op._can_consolidate('count', min_count=min_count, max_count=max_count):
        return op
    else:
        return ParserRule(op, meth='count', min_count=min_count, max_count=max_count)


def _m(op, on_fail=None, on_pass=None, element_name=None, return_string=False):
    op = _make_meth(op)

    if op._can_consolidate('mark', on_fail=on_fail, on_pass=on_pass, element_name=element_name, return_string=return_string):
        return op
    else:
        return ParserRule(op, meth='mark', on_fail=on_fail, on_pass=on_pass,
                          element_name=element_name, return_string=return_string)


def _l(op, char_set, on_fail=None, on_pass=None, only_on_fail=False, only_on_pass=False):
    op = _make_meth(op)

    return ParserRule(op, meth='look', char_set=char_set, on_fail=on_fail, on_pass=on_pass,
                      only_on_pass=only_on_pass, only_on_fail=only_on_fail)

'''
def _meth(meth_name, **kwargs):
    return dict(
        meth='_get_%s' % meth_name,
        # method=getattr(ParserOps, '_get_%s' % meth_name),
        args=[],
        kwargs=kwargs)

def _rule(rule_name):
    return dict(
        meth='_get_rule',
        # method=ParserOps._get_rule,
        args=[],
        kwargs={'rule_name': rule_name})

def _char(char_set, **kwargs):
    kwargs['char_set'] = char_set
    return dict(
        meth='_get_char',
        # method=ParserOps._get_char,
        args=[],
        kwargs=kwargs)

def _and(*methods, **kwargs):
    tmp_methods = []
    for m in methods:
        tmp_methods.append(_make_meth(m))
    return dict(
        meth='_get_and',
        # method=ParserOps._get_and,
        args=tmp_methods,
        kwargs=kwargs)

def _or(*methods, **kwargs):
    tmp_methods = []
    for m in methods:
        tmp_methods.append(_make_meth(m))
    return dict(
        meth='_get_or',
        # method=ParserOps._get_or,
        args=tmp_methods,
        kwargs=kwargs)

def _opt(op, **kwargs):
    op = _make_meth(op)
    if op['meth'] == '_get_char':
        op['kwargs']['optional'] = True
        return op
    else:
        return dict(
            meth='_get_opt',
            # method=ParserOps._get_opt,
            args=(op,),
            kwargs=kwargs)

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

    op = _make_meth(op)

    if op['meth'] in ('_get_char', '_get_and'):
        op['kwargs']['min_count'] = min_count
        op['kwargs']['max_count'] = max_count
        return op
    else:
        return dict(
            meth='_get_count',
            # method=ParserOps._get_count,
            args=[],
            kwargs=dict(
                min_count=min_count,
                max_count=max_count,
                op=op
            )
        )

def _m(op, on_fail=None, on_pass=None, element_name=None, return_string=False):
    op = _make_meth(op)

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
            # method=ParserOps._get_mark,
            args=[],
            kwargs=dict(
                op=op,
                on_fail=on_fail,
                on_pass=on_pass,
                element_name=element_name,
                return_string=return_string)
        )

def _l(op, char_set, on_fail=None, on_pass=None, only_on_fail=False, only_on_pass=False):
    op = _make_meth(op)

    return dict(
        meth='_get_look',
        # method=ParserOps._get_look,
        args=[],
        kwargs=dict(
            op=op,
            char_set=char_set,
            on_fail=on_fail,
            on_pass=on_pass,
            only_on_pass=only_on_pass,
            only_on_fail=only_on_fail)
    )
'''

EMAIL_PARSER_RULES = dict(
    addr_spec=_and(
        # local-part "@" domain
        _m('local_part', on_fail='ERR_NO_LOCAL_PART', element_name=ISEMAIL_ELEMENT_LOCALPART),
        _c(1, 'AT'),
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
            _m('DQUOTE', return_string=False),
            _c('*', _and(
                    'fws',
                    _m('qcontent', return_string=True))),
            _m('[fws]', return_string=False),
            _m('DQUOTE', on_fail='UNCLOSED_QUOTED_STR', return_string=False),
            _m('[cfws]', return_string=False)),
        on_pass='QUOTED_STR', return_string=True),

    obs_local_part=_and(
        # word *("." word)
        'word',
        _c('*', _and(
            'DOT',
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
        'OPENPARENTHESIS',
        _c('*',
           _and(
                _m('[fws]', return_string=False),
                'ccontent',
                _m('[fws]', return_string=False))),
        _m('CLOSEPARENTHESIS', on_fail='UNCLOSED_COMMENT')),

    dot_atom_text=_and(
        # 1*atext *("." 1*atext)
        'ATEXT',
        _and(
            'DOT',
            'ATEXT')),

    qcontent=_or(
        # qtext / quoted-pair
        'QTEXT',
        'quoted_pair'),

    quoted_pair=_or(
        # ("\" (VCHAR / WSP)) / obs-qp
        _and(
            'BACKSLASH',
            _or(
                'VCHAR',
                'WSP')),
        'obs_gp'),

    obs_gp=_and(
        # "\" (%d0 / obs-NO-WS-CTL / LF / CR)
        'BACKSLASH',
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
            'OPENSQBRACKET',
            _and(
                '[fws]',
                'DTEXT'),
            '[fws]',
            'CLOSESQBRACKET',
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
                'DOT',
                'atom'))),

    address_literal=_and(
        #    "[" ( IPv4-address-literal /
        #    IPv6-address-literal /
        #    General-address-literal ) "]"
        'OPENSQBRACKET',
        _or(
            _m('ipv4_address_literal', element_name=ISEMAIL_ELEMENT_DOMAIN_LIT_IPV4),
            _m('ipv6_address_literal', element_name=ISEMAIL_ELEMENT_DOMAIN_LIT_IPV6),
            _m('general_address_literal', element_name=ISEMAIL_ELEMENT_DOMAIN_LIT_GEN)),
        'CLOSESQBRACKET'),

    ipv4_address_literal=_and(
        # Snum 3("."  Snum)
        'snum',
        _c('3', _and('DOT', 'snum'))),

    snum=_or(
        # 1*3DIGIT   ; representing a decimal integer value in the range 0 through 255
        'IPV4_19',
        _and('IPV4_19', 'DIGIT'),
        _or(
            _and('"1"', 'DIGIT', 'DIGIT'),
            _and('"2"', 'IPV4_04', 'DIGIT'),
            _and('"2"', '"5"', 'IPV4_05'),
        )),

    ipv6_address_literal=_and(
        # "IPv6:" IPv6-addr
        '"IPv6:"', 'ipv6_addr'),

    ipv6_addr=_or(
        # IPv6-full / IPv6-comp / IPv6v4-full / IPv6v4-comp
        'ipv6_full', 'ipv6_comp', 'ipv6v4_full', 'ipv6v4_comp'),

    ipv6_full=_and(
        # IPv6-hex 7(":" IPv6-hex)
        'ipv6_hex',
        _c(7, _and(
            'COLON',
            'ipv6_hex'))),

    ipv6_comp=_and(
        # [IPv6-hex *5(":" IPv6-hex)] "::" [IPv6-hex *5(":" IPv6-hex)]
        #
        #      ; The "::" represents at least 2 16-bit groups of
        #      ; zeros.  No more than 6 groups in addition to the
        #      ; "::" may be present.
        'ipv6_hex',
        _c('*5', _and(
            'COLON',
            'ipv6_hex')),
        '"::"',
        'ipv6_hex',
        _c('*5', _and(
            'COLON',
            'ipv6_hex'))),

    ipv6v4_full=_and(
        # IPv6-hex 5(":" IPv6-hex) ":" IPv4-address-literal
        'ipv6_hex',
        _c(5, _and(
            'COLON',
            'ipv6_hex')),
        'ipv4_address_literal'),

    ipv6v4_comp=_and(
        # [IPv6-hex *3(":" IPv6-hex)] "::" [IPv6-hex *3(":" IPv6-hex) ":"] IPv4-address-literal
        #      ; The "::" represents at least 2 16-bit groups of
        #      ; zeros.  No more than 4 groups in addition to the
        #      ; "::" and IPv4-address-literal may be present.
        'ipv6_hex',
        _c('*2', _and('COLON', 'ipv6_hex')),
        '"::"',
        'ipv6_hex',
        _c('*2', _and('COLON', 'ipv6_hex')),
        'ipv4_address_literal'),

    ipv6_hex=_or(
        # 1*4HEXDIG
        _c('1*4', 'HEXDIG')),

    general_address_literal=_and(
        # Ldh-str ":" 1*dcontent
        _c('*', 'LTR_STR'),
        'COLON',
        _c('*', 'DCONTENT')
        ),

)



class ParserOps(object):
    '''
    def __init__(self):
        self.rules = {}
        self._fix_list()
        # self.start_method = self._compile(EMAIL_PARSER_RULES['addr_spec'])
        self.start_method = self.rules['addr_spec']

    def _fix_list(self):
        for name, rule in EMAIL_PARSER_RULES.items():
            self.rules[name] = self._fix_rule_1(rule)

        for name, rule in self.rules.items():
            log_ddebug('fixing rule links in %s', name)
            self._fix_rule_2(rule)

        for name, rule in self.rules.items():
            log_ddebug('consolidating count/mark/opt items in %s', name)
            self._fix_rule_3(rule)


    def _fix_rule_1(self, rule):
        tmp_rule = rule.copy()
        meth = rule['meth']
        tmp_rule['method'] = getattr(self, meth)
        if meth in ('_get_and', '_get_or', '_get_opt'):
            tmp_rule['args'] = []
            for r in rule['args']:
                tmp_rule['args'].append(self._fix_rule_1(r))
        elif meth in ('_get_count', '_get_mark', '_get_look)'):
            tmp_rule['kwargs']['op'] = self._fix_rule_1(rule['kwargs']['op'])
        return tmp_rule

    def _fix_rule_2(self, rule):
        meth = rule['meth']
        # log_ddebug('          => %s:  %r', meth, rule)
        if meth == '_get_rule':
            tmp_name = rule['kwargs']['rule_name']
            # log_ddebug('     fixing link to rule %s', tmp_name)
            rule.clear()
            rule.update(EMAIL_PARSER_RULES[tmp_name])

        if meth in ('_get_and', '_get_or', '_get_opt'):
            for i, r in enumerate(rule['args']):
                # log_ddebug('     --- START %s ---', meth)
                self._fix_rule_2(r)
                # log_ddebug('     ---- END %s -------', meth)
        elif meth in ('_get_count', '_get_mark', '_get_look)'):
            # log_ddebug('     --- START %s ---', meth)
            self._fix_rule_2(rule['kwargs']['op'])
            # log_ddebug('     --- END %s ---', meth)

    def _fix_rule_3(self, rule):
        # log_ddebug('     => %s:  %r', rule['meth'], rule)
        if rule['meth'] == '_get_count':
            # log_ddebug('          checking consolidation (_count) for: %s', rule['kwargs']['op']['meth'])
            if rule['kwargs']['op']['meth'] in ('_get_char', '_get_and'):
                # log_ddebug('          consolidating %s rule', rule['kwargs']['op']['meth'])
                rule['kwargs']['op']['kwargs']['min_count'] = rule['kwargs']['min_count']
                rule['kwargs']['op']['kwargs']['max_count'] = rule['kwargs']['max_count']
                tmp_rule = rule['kwargs']['op']
                rule.clear()
                rule.update(tmp_rule)
            # else:
                # log_ddebug('          no consolidation needed for %s', rule['kwargs']['op']['meth'])
        elif rule['meth'] == '_get_mark':
            # log_ddebug('          checking consolidation (_mark) for: %s', rule['kwargs']['op']['meth'])
            if rule['kwargs']['op']['meth'] in ('_get_char', '_get_and', '_get_or', '_get_count'):
                # log_ddebug('          consolidating %s rule', rule['kwargs']['op']['meth'])
                rule['kwargs']['op']['kwargs']['on_fail'] = rule['kwargs']['on_fail']
                rule['kwargs']['op']['kwargs']['on_pass'] = rule['kwargs']['on_pass']
                rule['kwargs']['op']['kwargs']['element_name'] = rule['kwargs']['element_name']
                rule['kwargs']['op']['kwargs']['return_string'] = rule['kwargs']['return_string']

                tmp_rule = rule['kwargs']['op']
                rule.clear()
                rule.update(tmp_rule)

            elif rule['kwargs']['op']['meth'] == '_get_opt' and 'on_fail' not in rule['kwargs'] \
                    and 'on_pass' not in rule['kwargs'] and 'element_name' not in rule['kwargs']:
                rule['kwargs']['op']['kwargs']['return_string'] = rule['kwargs']['return_string']
                # log_ddebug('          consolidating %s rule', rule['kwargs']['op']['meth'])

                tmp_rule = rule['kwargs']['op']
                rule.clear()
                rule.update(tmp_rule)
            # else:
            #     log_ddebug('          no consolidation needed for %s', rule['kwargs']['op']['meth'])
        # else:
        #     log_ddebug('          no consolidation needed.')

        if rule['meth'] in ('_get_and', '_get_or', '_get_opt'):
            for i, r in enumerate(rule['args']):
                # log_ddebug('     --- START %s ---', rule['meth'])
                self._fix_rule_3(r)
                # log_ddebug('     ---- END %s -------', rule['meth'])
        elif rule['meth'] in ('_get_count', '_get_mark', '_get_look)'):
            # log_ddebug('     --- START %s ---', rule['meth'])
            self._fix_rule_3(rule['kwargs']['op'])
            # log_ddebug('     --- END %s ---', rule['meth'])

    '''

    '''
    def _fix_item(self, rule):
        if rule['meth'] == '_get_rule':
            return EMAIL_PARSER_RULES[rule['kwargs']['rule_name']]
        else:
            return rule
    '''

    '''
    @staticmethod
    def _make_meth(method, **kwargs):
        log_ddebug('          making method object for -->%r<--', method)
        if isinstance(method, str):
            if method[0] == '"' and method[-1] == '"':
                # if it is a quoted string:  "do this"
                tmp_and_set = []
                for c in method[1:-1]:
                    tmp_and_set.append(ParserOps._make_meth(c))
                log_ddebug('               "AND" method')
                return ParserOps._and(*tmp_and_set)

            elif method[0] == '[' and method[-1] == ']':
                # if it is in square brackets:  [blah]
                tmp_opp = ParserOps._make_meth(method[1:-1])
                log_ddebug('               "OPT" method')
                return ParserOps._opt(tmp_opp, **kwargs)

            else:
                # this is a string set
                try:
                    log_ddebug('               trying "CONST(CHAR)" method')
                    return ParserOps._char(EMAIL_PARSER_CONST[method])
                except KeyError:
                    try:
                        log_ddebug('               trying "RULE" method')
                        return ParserOps._rule(method)
                    except KeyError:
                        if method[0] == '_':
                            log_ddebug('               trying "METH" method')
                            return ParserOps._meth(method)
                        else:
                            log_ddebug('               trying "CHAR" method')
                            return ParserOps._char(method)
        else:
            log_ddebug('               falling through, is already a method')
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
    '''
    def parse_email(self, data):
        if data.rem_email is not None and data.rem_email != '':
            if isinstance(data.rem_email, str):
                data.rem_email = deque(data.rem_email)

            if '@' not in data.rem_email:
                data.add_note(diag='ERR_NO_DOMAIN_SEP', pos=0)
            else:
                try:
                    EMAIL_PARSER_OPS['addr_spec'](self, data)
                    # start_meth = EMAIL_PARSER_RULES['addr_spec']
                    # self.start_method['method'](data, *self.start_method['args'], **self.start_method['kwargs'])
                except NoElementError:
                    pass
        else:
            data.add_note(diag='ERR_EMPTY_ADDRESS', pos=0)

    '''
    @staticmethod
    def _get(data, op):
        if not isinstance(op, dict):
            op = ParserOps._make_meth(op)
        return op['method'](data, *op['args'], **op['kwargs'])
    '''

    @staticmethod
    def _get_char(data, char_set, min_count=0, max_count=None, optional=False,
                  return_string=True, on_fail=None, on_pass=None, element_name=None):
        log_debug('checking for chars in -->%r<--', char_set)
        try:
            tmp_ret = []
            for i in range(len(data.rem_email)):
                tmp_next_char = data.rem_email[0]
                log_ddebug('    checking: %r', tmp_next_char)
                if max_count is not None and i > max_count-1:
                    log_ddebug('    found, max_count (%s) met!', max_count)
                    break

                if tmp_next_char in char_set:
                    tmp_ret.append(data.rem_email.popleft())
                    log_ddebug('     found')
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

    def _get_rule(self, data, rule_name):
        log_debug('getting rule "%s"', rule_name)
        # return ParserOps._get(data, EMAIL_PARSER_RULES[rule_name])
        return EMAIL_PARSER_OPS[rule_name](self, data)

    def _get_and(self, data, *operations, min_count=1, max_count=None, optional=False, return_string=True,
                 on_fail=None, on_pass=None, element_name=None):
        tmp_ret_list = []
        log_debug('all must match---')
        try:
            for i in range(len(data.rem_email)):
                if max_count is not None and i > max_count-1:
                    break

                for op in operations:
                    try:
                        # tmp_ret = op['method'](data, *op['args'], **op['kwargs'])
                        tmp_ret = op(self, data)
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


    def _get_or(self, data, *operations, optional=False, return_string=True,
                on_fail=None, on_pass=None, element_name=None):
        tmp_ret = []
        try:
            for op in operations:
                try:
                    # tmp_ret = op['method'](data, *op['args'], **op['kwargs'])
                    tmp_ret = op(self, data)
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

    def _get_opt(self, data, op, return_string=True):
        try:
            # tmp_ret = self._get(operation, data)
            tmp_ret = op(self, data)
            # tmp_ret = op['method'](data, *op['args'], **op['kwargs'])

            if return_string:
                return tmp_ret
            else:
                return []
        except NoElementError:
            return []

    def _get_count(self, data, min_count, max_count, op, optional=False, return_string=True,
                   on_fail=None, on_pass=None, element_name=None):
        tmp_ret_list = []
        try:
            for i in range(len(data.rem_email)):
                if i > max_count-1:
                    break
                try:
                    tmp_ret = op(self, data)
                    # tmp_ret = op['method'](data, *op['args'], **op['kwargs'])

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

    def _get_mark(self, data, op, on_fail=None, on_pass=None, element_name=None, return_string=False):
        try:
            tmp_ret = op(self, data)
            # tmp_ret = op['method'](data, *op['args'], **op['kwargs'])
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

    def _get_look(self, data, op, char_set, on_fail=None, on_pass=None,
                  only_on_fail=False, only_on_pass=False):
        passed = True
        get_look = False
        tmp_ret = []
        try:
            tmp_ret = op(self, data)
            # tmp_ret = op['method'](data, *op['args'], **op['kwargs'])
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

'''
_and = ParserOps._and
_meth = ParserOps._meth
_char = ParserOps._char
_or = ParserOps._or
_opt = ParserOps._opt
_c = ParserOps._c
_m = ParserOps._m
_l = ParserOps._l
'''

parser_ops = ParserOps()
