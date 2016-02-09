from meta_data import *
from collections import deque
# import logging

# log = logging.getLogger(__name__)


class SpaceText(object):
    def __init__(self, indent=2):
        self.indent_size = indent
        self.indent = 0

    @property
    def push(self):
        self.indent += self.indent_size
        return str(self)

    @property
    def pop(self):
        self.indent -= self.indent_size
        return str(self)

    def __str__(self):
        return ''.ljust(self.indent)

space_text = SpaceText()


class NoElementError(Exception):
    def __init__(self, is_email_obj=None, popped_text=None, fail_flag=None, position=None):
        if popped_text is not None:
            print('adding %r back to %r ' % (popped_text, is_email_obj.rem_string))
            popped_text.reverse()
            is_email_obj.rem_string.extendleft(popped_text)
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
            for c in range(char[0], char[1]+1):
                tmp_ret.append(chr(c))
    return ''.join(tmp_ret)

_PARSER_CONST = dict(
    AT='@',
    BACKSLASH='\\',
    CLOSEPARENTHESIS=')',
    CLOSESQBRACKET=']',
    COLON=':',
    COMMA=',',
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
    CRLF='\r\n',
    DIGIT='1234567890',
    HEXDIG='1234567890abcdefABCDEF',
    LTR_STR=make_char_str((65, 90), (97, 122), (48, 57)),
    REPEAT_FLAGS='1234567890*',
)

_EMAIL_PARSER_CONSOLIDATABLE = {
   'char': ('min_repeat', 'max_repeat', 'optional', 'return_string', 'on_fail', 'on_pass', 'element_name'),
   'rule': set(),
   'and': ('min_repeat', 'max_repeat', 'optional', 'return_string', 'on_fail', 'on_pass', 'element_name'),
   'or': ('optional', 'return_string', 'on_fail', 'on_pass', 'element_name'),
   'opt': ('optional', 'return_string'),
   'repeat': ('min_repeat', 'max_repeat', 'optional', 'return_string', 'on_fail', 'on_pass', 'element_name'),
   'mark': ('return_string', 'on_fail', 'on_pass', 'element_name'),
   'look': set(),
}

_EMAIL_PARSER_DO_NOT_CONSOLIDATE = {
    'opt': ('repeat',),
}



PARSER_DEFAULT_FAIL_CODE = 255
PARSER_DEFAULT_REMAINING_STR_CODE = 254
PARSER_DEFAULT_PASS_CODE = 0
PARSER_DEFAULT_START_RULE = 'start'

class ParserOps(object):

    def __init__(self,
                 rules,
                 char_sets=None,
                 on_fail=None,
                 on_rem_string=None,
                 on_pass=None,
                 start_rule=None):
        self.start_rule = start_rule or PARSER_DEFAULT_START_RULE
        self.ruleset = rules
        self.charsets = char_sets or {}
        self.on_fail = on_fail
        self.on_rem_string = on_rem_string
        self.on_pass = on_pass
        self.charsets.update(_PARSER_CONST)

    '''
    def parse_email(self, data, rule=None):
        rule = rule or 'start'
        if data.rem_string is not None and data.rem_string != '':
            if isinstance(data.rem_string, str):
                data.rem_string = deque(data.rem_string)

            if '@' not in data.rem_string:
                data.add_note(diag='ERR_NO_DOMAIN_SEP', position=0)
            else:
                try:
                    self.ruleset[rule](self, data)
                    # start_meth = EMAIL_PARSER_RULES['addr_spec']
                    # self.start_method['method'](data, *self.start_method['args'], **self.start_method['kwargs'])
                except NoElementError:
                    if self._on_fail is not None:
                        data.add_note(diag=self._on_fail)
        else:
            data.add_note(diag='ERR_EMPTY_ADDRESS', position=0)
    '''
    def parse_str(self, data, rule=None):
        rule = rule or self.start_rule
        if isinstance(data.rem_string, str):
            data.rem_string = deque(data.rem_string)

        try:
            self.ruleset[rule](self, data)
        except NoElementError:
            if self.on_fail is not None:
                data.add_note(diag=self.on_fail, position=0)
        else:
            if data.rem_string and self.on_rem_string is not None:
                data.add_note(diag=self.on_rem_string)
            elif self.on_pass is not None:
                data.add_note(diag=self.on_pass, position=0)

    def __contains__(self, item):
        if item in self.ruleset:
            return True
        if item in self.charsets:
            return True
        return False




class ParserRule(object):
    rule_type = ''
    parses_data = False
    single_op = True
    returns_info = True
    allow_repeat = True
    repr_format = '{opt_pre}{pre_rule}{type}({pre_ops}{ops}{post_ops}){post_rule}{opt_post}'
    # parser = ParserOps
    # parser_ops = EMAIL_PARSER_OPS

    def __init__(self,
                 optional=False,
                 return_string=True,
                 on_fail=None,
                 on_pass=None,
                 element_name=None,
                 min_repeat=None,
                 max_repeat=None,
                 inner_optional=False,
                 ):
        self.optional = optional
        self.return_string = return_string
        self.on_fail = on_fail
        self.on_pass = on_pass
        self.element_name = element_name
        self.before_self = []
        self.after_self = []
        self.before_ops = []
        self.after_ops = []
        self.operations = []
        if self.allow_repeat:
            self.min_repeat = min_repeat or ISEMAIL_MIN_REPEAT
            self.max_repeat = max_repeat or ISEMAIL_MAX_REPEAT
            self.inner_optional = inner_optional
        else:
            self.min_repeat = 1
            self.max_repeat = 1
            self.inner_optional = False

    def _operation_strs(self):
        if self.parses_data:
            return self.parse_str
        elif self.single_op:
            return 'r' % self.operation
        else:
            tmp_ret = []
            for r in self.operations:
                tmp_ret.append('%r' % r)
            return ', '.join(tmp_ret)

    def _add_repr_flag(self,
                       before_self=None,
                       after_self=None,
                       before_ops=None,
                       after_ops=None):
        if before_self:
            self.before_self.insert(0, before_self)
        if after_self:
            self.after_self.append(after_self)
        if before_ops:
            self.before_ops.insert(0, before_ops)
        if after_ops:
            self.after_ops.append(after_ops)

    def _set_repr_flags(self):

        if self.return_string:
            self._add_repr_flag(before_self='x')

        if self.on_pass is not None or self.on_fail is not None:
            if self.on_pass is None:
                self._add_repr_flag(after_ops='{F}')
            elif self.on_fail is None:
                self._add_repr_flag(after_ops='{P}')
            else:
                self._add_repr_flag(after_ops='{PF}')

        if self.element_name is not None:
            self._add_repr_flag(after_ops='<%s>' % self.element_name)

    def __repr__(self):
        """
        repr_format = '{opt_pre}{pre_rule}{type}({pre_ops}{ops}{post_ops}){post_rule}{opt_post}'

        pre_flags:
            [type(ops)] = optional
            (x:type(ops)) = do not return string
        post_flags:
            type(ops, {PF}) = pass / fail
            type(ops, <name>)
        """
        if self.optional:
            opt_pre = '['
            opt_post = ']'
        else:
            opt_pre = ''
            opt_post = ''

        if self.before_self or self.after_self:
            pre_rule = '(%s:' % ''.join(self.before_self)
            post_rule = ', %s)' % ''.join(self.after_self)
        else:
            pre_rule = ''
            post_rule = ''

        if self.before_ops or self.after_ops:
            pre_ops = '%s, ' % ''.join(self.before_ops)
            post_ops = ', %s' % ''.join(self.after_ops)
        else:
            pre_ops = ''
            post_ops = ''

        """
        (5*3:type(ops))
        """
        if hasattr(self, 'min_repeat'):
            if self.min_repeat == ISEMAIL_MIN_REPEAT:
                tmp_min = ''
            else:
                tmp_min = str(self.min_repeat)

            if self.max_repeat == ISEMAIL_MAX_REPEAT:
                tmp_max = ''
            else:
                tmp_max = str(self.max_repeat)

            self._add_repr_flag(after_ops='%s*%s:' % (tmp_min, tmp_max))


        tmp_ret = self.repr_format.format(
            type=self.rule_type,
            opt_pre=opt_pre,
            opt_post=opt_post,
            pre_rule=pre_rule,
            post_rule=post_rule,
            pre_ops=pre_ops,
            post_ops=post_ops)

        return tmp_ret

    '''
    def _can_consolidate(self, other_type, **kwargs):
        tmp_my_methods = _EMAIL_PARSER_CONSOLIDATABLE[self.rule_type]

        tmp_consolidate = True
        if other_type == 'repeat' and 'optional' in self.kwargs and self.kwargs['optional']:
            tmp_consolidate = False
        else:
            for m in kwargs:
                if m not in tmp_my_methods:
                    tmp_consolidate = False
                    break

        if tmp_consolidate:
            self.kwargs.update(kwargs)
            # log_ddebug('     consolidating %s(%r) into %s', other_type, kwargs, self.rule_type)
            return True
        return False
    '''

    def __call__(self, parser, data):
        log_ddebug('%s %r on data: %r', space_text, self, ''.join(data.rem_string))
        # method = getattr(parser, '_get_%s' % self.rule_type)
        tmp = space_text.push
        tmp_pos = data.position

        tmp_ret_list = []

        try:
            for i in range(len(data.rem_string)):
                if i > self.max_repeat-1:
                    break
                try:
                    tmp_ret = self.run(self, parser, data)
                except NoElementError:
                    if i < self.min_repeat-1:
                        if self.inner_optional:
                            break
                        else:
                            raise NoElementError(data, popped_text=tmp_ret_list)
                else:
                    if tmp_ret is not None:
                        tmp_ret_list.extend(tmp_ret)
        except NoElementError:
            tmp = space_text.pop
            log_ddebug('%s FAIL->"%r" failed!', space_text, self)
            if not self.optional:
                raise NoElementError(data, fail_flag=self.on_fail, position=tmp_pos)
        else:
            tmp = space_text.pop
            log_ddebug('%s PASS-> "%r" passed', space_text, self)

            if self.on_pass or self.element_name:
                data.add_note(diag=self.on_pass, element_name=self.element_name, element=tmp_ret_list, position=tmp_pos)
            if self.return_string:
                return tmp_ret_list
            else:
                return []

    def run(self, parser, data):
        try:
            return parser.ruleset[self.operation](parser, data)
        except KeyError:
            raise AttributeError('Rule %s not found in rule dictionary' % self.operation)



class QString(ParserRule):
    rule_type = 'qstring'

    def __init__(self, parse_str, min_repeat=1, max_repeat=1, **kwargs):
        self.parse_str = parse_str
        self.min_repeat = min_repeat
        self.max_repeat = max_repeat
        super().__init__(**kwargs)

    def run_quoted_string(self, parser, data):
        # log_ddebug('%s checking for chars in %r', space_text, char_set)
        tmp_ret_list = []
        if len(data.rem_string) < (self.min_repeat * len(self.parse_str)):
            log_ddebug('%s Not enough chars to meet min repeat', space_text)
            raise NoElementError()
        for i in range(len(data.rem_string)):
            if self.max_repeat is not None and i > self.max_repeat-1:
                log_ddebug('%s found, max_repeat (%s) met!', space_text, self.max_repeat)
                break

            log_ddebug('%s checking for: %r in %r', space_text, self.parse_str, data.rem_string)

            try:
                tmp_ret = []
                for c in self.parse_str:
                    tmp_next_char = data.rem_string[0]
                    if tmp_next_char == c:
                        tmp_ret.append(data.rem_string.popleft())
                    else:
                        raise NoElementError(data, popped_text=tmp_ret)
                if tmp_ret:
                    tmp_ret_list.extend(tmp_ret)
                else:
                    log_ddebug('%s missed', space_text)

            except NoElementError:
                if i < self.min_repeat-1:
                    log_ddebug('%s missed, min_repeat (%s) not met!', space_text, self.min_repeat)
                    raise NoElementError(data, popped_text=tmp_ret_list)
        if tmp_ret_list:
            return tmp_ret_list
        else:
            raise NoElementError()

    def run_char(self, parser, data):
        # log_ddebug('%s checking for chars in %r', space_text, char_set)
        tmp_ret = []
        if len(data.rem_string) < self.min_repeat:
            log_ddebug('%s Not enough chars to meet min repeat', space_text)
            raise NoElementError()
        for i in range(len(data.rem_string)):
            tmp_next_char = data.rem_string[0]
            if self.max_repeat is not None and i > self.max_repeat-1:
                log_ddebug('%s found, max_repeat (%s) met!', space_text, self.max_repeat)
                break
            log_ddebug('%s checking for: %r in %r', space_text, tmp_next_char, self.char_set)
            if tmp_next_char in self.char_set:
                tmp_ret.append(data.rem_string.popleft())
                log_ddebug('%s found', space_text)
            elif i < self.min_repeat-1:
                log_ddebug('%s missed, min_repeat (%s) not met!', space_text, self.min_repeat)
                raise NoElementError(data, popped_text=tmp_ret)
            else:
                log_ddebug('%s missed', space_text)
                break
        if tmp_ret:
            if len(tmp_ret) < self.min_repeat:
                log_ddebug('%s missed, min_repeat (%s) not met!', space_text, self.min_repeat)
                raise NoElementError(data, popped_text=tmp_ret)
            return tmp_ret
        else:
            raise NoElementError(data)


'''
class RuleParser(ParserRule):
    rule_type = 'rule'

    def __init__(self, rule, **kwargs):
        self.rule = rule
        super().__init__(**kwargs)

    def run(self, data):
        try:
            return self.parser.ruleset[self.rule](self, data)
        except KeyError:
            raise AttributeError('Rule %s not found in rule dictionary' % self.rule)

    def _operation_strs(self):
        return self.rule
'''

class AndParser(ParserRule):
    rule_type = 'and'
    single_op = False

    def __init__(self, *operations, min_repeat=1, max_repeat=1, **kwargs):
        self.operations = operations
        self.min_repeat = min_repeat
        self.max_repeat = max_repeat
        super().__init__(**kwargs)

    def run(self, parser, data):
        tmp_ret_list = []
        log_debug('all must match---')
        for i in range(len(data.rem_string)):
            if self.max_repeat is not None and i > self.max_repeat-1 or not data.rem_string:
                break

            for op in self.operations:
                try:
                    # tmp_ret = op['method'](data, *op['args'], **op['kwargs'])
                    tmp_ret = op(self, parser, data)
                except NoElementError:
                    raise NoElementError(data, popped_text=tmp_ret_list)
                else:
                    if tmp_ret is not None:
                        tmp_ret_list.extend(tmp_ret)

            if i < self.min_repeat-1:
                raise NoElementError(data, popped_text=tmp_ret_list)

        if not tmp_ret_list:
            raise NoElementError()

        return tmp_ret_list


class OrParser(ParserRule):
    rule_type = 'or'
    single_op = False

    def __init__(self, *operations, **kwargs):
        self.operations = operations
        super().__init__(**kwargs)

    def run(self, parser, data):
        tmp_ret = []
        for op in self.operations:
            try:
                # tmp_ret = op['method'](data, *op['args'], **op['kwargs'])
                tmp_ret = op(parser, data)
                break
            except NoElementError:
                pass
        if tmp_ret:
            return tmp_ret
        else:
            raise NoElementError()


class OptParser(ParserRule):
    rule_type = 'opt'
    repr_format = '{opt_pre}{ops}{opt_post}'

    def __init__(self, operation, **kwargs):
        self.operation = operation
        kwargs['optional'] = True
        super().__init__(**kwargs)

    def run(self, parser, data):
        return self.operation(self, parser, data)


class RepeatParser(ParserRule):
    rule_type = 'repeat'
    repr_format = '{opt_pre}{pre_rule}({pre_ops}{ops}{post_ops}){post_rule}{opt_post}'

    def __init__(self, operation,
                 min_repeat=ISEMAIL_MIN_REPEAT,
                 max_repeat=ISEMAIL_MAX_REPEAT,**kwargs):
        self.min_repeat = min_repeat
        self.max_repeat = max_repeat
        self.operation = operation
        super().__init__(**kwargs)

    def run(self, parser, data):
        tmp_ret_list = []
        for i in range(len(data.rem_string)):
            if i > self.max_repeat-1:
                break
            try:
                tmp_ret = self.operation(self, parser, data)
                # tmp_ret = op['method'](data, *op['args'], **op['kwargs'])

                # tmp_ret = self._get(op, data)
            except NoElementError:
                if i < self.min_repeat-1:
                    raise NoElementError(data, popped_text=tmp_ret_list)
            else:
                if tmp_ret is not None:
                    tmp_ret_list.extend(tmp_ret)

        return tmp_ret_list


class MarkParser(ParserRule):
    rule_type = 'mark'

    def __init__(self, operation, **kwargs):
        self.operation = operation
        super().__init__(**kwargs)

    def run(self, parser, data):
        return self.operation(self, parser, data)


class LookParser(ParserRule):
    rule_type = 'look'

    def __init__(self, operations, *fors,
                 only_on_pass=False, only_on_fail=False, **kwargs):
        self.fors = fors
        self.operation = operations
        self.only_on_fail = only_on_fail
        self.only_on_pass = only_on_pass
        kwargs = {'return_string': False}
        super().__init__(**kwargs)

    def run(self, parser, data):
        passed = True
        get_look = False
        tmp_ret = []
        try:
            tmp_ret = self.operation(parser, data)
        except NoElementError:
            passed = False

        if self.only_on_fail or self.only_on_pass:
            if passed and self.only_on_pass:
                get_look = True
            elif not passed and self.only_on_fail:
                get_look = True
        else:
            get_look = True

        if get_look:
            for lookfor in self.fors:
                lookfor(parser, data, passed)

        return tmp_ret


class LookForParser(ParserRule):
    rule_type = 'for'

    def __init__(self, char_set,
                 only_on_pass=False, only_on_fail=False,
                 on_pass=None, on_fail=None, **kwargs):
        self.char_set = char_set
        self.only_on_fail = only_on_fail
        self.only_on_pass = only_on_pass
        kwargs = {'return_string': False}
        super().__init__(**kwargs)
        self.on_fail = on_fail
        self.on_pass = on_pass

    def run(self, parser, data, passed):
        tmp_pos = data.position
        get_look = False

        if self.only_on_fail or self.only_on_pass:
            if passed and self.only_on_pass:
                get_look = True
            elif not passed and self.only_on_fail:
                get_look = True
        else:
            get_look = True

        if get_look:
            if data.rem_string[0] == self.char_set:
                if self.on_pass is not None:
                    data.add_note(diag=self.on_pass, position=tmp_pos)
            else:
                if self.on_fail is not None:
                    data.add_note(diag=self.on_fail, position=tmp_pos)

    def _operation_strs(self):
        return self.char_set


class CountParser(ParserRule):
    rule_type = 'count'

    def __init__(self, operation,
                 char_set,
                 min_count=0,
                 max_count=ISEMAIL_MAX_REPEAT,
                 only_on_pass=False,
                 only_on_fail=False,
                 on_below_min=None,
                 on_above_max=None,
                 on_within_min_max=None,
                 count_optional=False,
                 **kwargs):
        super().__init__(**kwargs)
        self.operation = operation
        self.char_set = char_set
        self.min_count = min_count
        self.max_count = max_count
        self.only_on_pass = only_on_pass
        self.only_on_fail = only_on_fail
        self.on_below_min = on_below_min
        self.on_above_max = on_above_max
        self.on_within_min_max = on_within_min_max
        self.count_optional = count_optional

    def run(self, parser, data):
        passed = True
        get_count = False
        tmp_ret = []
        tmp_pos = data.position
        count_pass = True
        try:
            tmp_ret = self.operation(parser, data)
        except NoElementError:
            passed = False

        if self.only_on_fail or self.only_on_pass:
            if passed and self.only_on_pass:
                get_count = True
            elif not passed and self.only_on_fail:
                get_count = True
        else:
            get_count = True

        if get_count:
            count = data.rem_string.count(self.char_set)

            if count < self.min_count:
                if self.on_below_min is not None:
                    data.add_note(diag=self.on_below_min, position=tmp_pos)
                    count_pass=False
            elif count > self.max_count:
                if self.on_above_max is not None:
                    data.add_note(diag=self.on_above_max, position=tmp_pos)
                    count_pass=False
            else:
                if self.on_within_min_max is not None:
                    data.add_note(diag=self.on_within_min_max, position=tmp_pos)
            if not self.count_optional and not count_pass:
                raise NoElementError(data, popped_text=tmp_ret)
        return tmp_ret

'''
def _make_meth(method, **kwargs):
    #  log_ddebug('          making method object for -->%r<--', method)
    tmp_ret = None
    if isinstance(method, str):
        if method[0] == '"' and method[-1] == '"':
            # if it is a quoted string:  "do this"
            tmp_and_set = []
            for c in method[1:-1]:
                tmp_and_set.append(_r(1, _char(c)))
            #  log_ddebug('               "QSTRING" method')
            tmp_ret = _and(*tmp_and_set)

        elif method[0] == '[' and method[-1] == ']':
            # if it is in square brackets:  [blah]
            tmp_opp = _make_meth(method[1:-1])
            #  log_ddebug('               "OPT" method')
            tmp_ret = _opt(tmp_opp, **kwargs)

        else:
            # this is a string set
            try:
                #  log_ddebug('               trying "CONST(CHAR)" method')
                tmp_ret = _char(_PARSER_CONST[method])
            except KeyError:
                if method[0] == '_':
                    # log_ddebug('               trying "METH" method')
                    tmp_ret = _meth(method)
                else:
                    #  log_ddebug('               trying "RULE" method')
                    tmp_ret = _rule(method)
    else:
        #  log_ddebug('               falling through, is already a method')
        tmp_ret = method

    # log_ddebug('             was %r, returning %r', method, tmp_ret)
    return tmp_ret
'''


def _make_op_obj(operation, *args, **kwargs):
    #  log_ddebug('          making method object for -->%r<--', method)
    if isinstance(operation, str):
        return StringParser(operation)
    else:
        return operation
'''
def _meth(meth_name, **kwargs):
    return ParserRule(meth=meth_name)
'''

def _rule(rule_name):
    return ParserRule(
        rule_name,
        meth='rule')

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

def _r(*args):

    if len(args) == 1:
        min_repeat = ISEMAIL_MIN_REPEAT
        max_repeat = ISEMAIL_MAX_REPEAT
        op = args[0]
    else:
        op = args[1]
        first_arg = args[0]
        if isinstance(first_arg, int) or first_arg.isdigit():
            min_repeat = first_arg
            max_repeat = first_arg
        else:
            if '*' in first_arg:
                min_repeat, max_repeat = first_arg.split('*')
                if min_repeat == '':
                    min_repeat = ISEMAIL_MIN_REPEAT
                if max_repeat == '':
                    max_repeat = ISEMAIL_MAX_REPEAT
            else:
                raise AttributeError('"*" not in %s' % first_arg)

        min_repeat = int(min_repeat)
        max_repeat = int(max_repeat)

    op = _make_meth(op)

    if op._can_consolidate('repeat', min_repeat=min_repeat, max_repeat=max_repeat):
        return op
    else:
        return ParserRule(op, meth='repeat', min_repeat=min_repeat, max_repeat=max_repeat)


def _m(op, on_fail=None, on_pass=None, element_name=None, return_string=True):
    op = _make_meth(op)

    if op._can_consolidate('mark', on_fail=on_fail, on_pass=on_pass, element_name=element_name, return_string=return_string):
        tmp_ret = op
    else:
        tmp_ret = ParserRule(op, meth='mark', on_fail=on_fail, on_pass=on_pass,
                          element_name=element_name, return_string=return_string)
    return tmp_ret

def _look(op, *fors):
    op = _make_meth(op)
    return ParserRule(op, meth='look', fors=fors)


def _for(op, repeat=1, on_fail=None, on_pass=None, only_on_fail=False, only_on_pass=False):
    return ParserRule(op, meth='for', on_fail=on_fail, on_pass=on_pass,
                      only_on_pass=only_on_pass, only_on_fail=only_on_fail, repeat=repeat)


parser_ops = ParserOps()
