from collections import deque

from helpers.meta_data.meta_data import *


# import logging

# log = logging.getLogger(__name__)


# <editor-fold desc="***** Diag Manager *******************************">
class DiagItem(object):
    def __init__(self, key, value, name=None, description=None, category=None, **kwargs):
        self.key = key
        self.value = value
        self.name = name or ''
        self.description = description or name
        self.category = category
        for key, value in kwargs.items():
            if key not in self.__dir__():
                setattr(self, key, value)

    def __int__(self):
        return self.value

    def __str__(self):
        return self.name

class DiagsList(object):
    def __init__(self, *items):
        self._by_value = {}
        self._by_key = {}

        if len(items) == 1 and isinstance(items[0], dict):
            for key, item in items[0].items():
                if isinstance(item, dict):
                    item['key'] = key
                elif isinstance(item, int):
                    item = {'key': key, 'value': item}
                elif isinstance(key, int) and isinstance(item, str):
                    item = {'key': key, 'value': item}
                else:
                    raise AttributeError('could not determine diags from: %r' % item)
                self.add_diag(DiagItem(**item))
        else:
            for item in items:
                self.add_diag(item)

    def add_diag(self, item):
        self._by_key[item.key] = item
        self._by_value[item.value] = item

    def code(self, item):
        tmp_diag = self[item]
        return {"key": tmp_diag.key, 'value': tmp_diag.value}

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._by_key[item]
        else:
            return self._by_value[item]



BASE_DIAGS = DiagsList(dict(PASS=0, REM=1, FAIL=2))
# </editor-fold>


class ElementHelper(object):
    name = 'element'

    def __init__(self, lookup=None):
        self.items = {}
        self.count = 0
        self.lookup = lookup
        self._max = None

    def name_value(self, code):
        return code, code

    def set_max(self, value):
        pass

    def add(self, code, **kwargs):
        self.count += 1
        name, value =  self.name_value(code)
        tmp_item = kwargs
        tmp_item['name'] = name
        tmp_item['value'] = value
        self.set_max(value)
        if name in self:
            self[name]['instances'].append(tmp_item)
        else:
            self[name] = dict(
                name=name,
                value=value,
                instances=[tmp_item]
            )
            if self.lookup is not None:
                self[code]['info'] = self.lookup[code]

        log_ddebug('adding %s: %s (%r)', self.name, code, tmp_item)

    def get(self, name=None, max_value=None, min_value=None, field=None):
        min_value = min_value or -1
        max_value = max_value or sys.maxsize

        if name is None:
            tmp_ret = {}
            for diag, items in self.items.items():
                if min_value < items['value'] < max_value:
                    if field is None:
                        tmp_ret[diag] = items['instances']
                    else:
                        tmp_ret[diag] = []
                        for i in items['instances']:
                            tmp_ret[diag].append(i[field])
            return tmp_ret
        else:
            if field is None:
                return self.items[name]
            else:
                tmp_ret = []
                for i in self.items[name]['instances']:
                    tmp_ret.append(i[field])
                return tmp_ret


    def __contains__(self, item):
        return item in self.items

    def __getitem__(self, item):
        return self.items[item]

    def __setitem__(self, key, value):
        self.items[key] = value

    def __iter__(self):
        for item in self.items.values():
            yield item


class DiagHelper(ElementHelper):

    def name_value(self, code):
        if self.lookup is not None:
            try:
                return self.lookup[code].key, self.lookup[code].value
            except KeyError:
                pass
        return code, code

    def set_max(self, value):
        if isinstance(value, int):
            if self._max is None:
                self._max = 0
            self._max = max(self._max, value)
        else:
            self._max = value

class WorkQueue(object):
    def __init__(self):
        self.queue = []
        self.done = []
        self.name_queue = []

    def push(self, name, **kwargs):
        self.name_queue.append(name)
        kwargs['name'] = '.'.join(self.name_queue)
        self.queue.append(kwargs)

    def pop(self, **kwargs):
        tmp_item = self.queue.pop()
        tmp_item.update(kwargs)
        self.done.append(tmp_item)
        return tmp_item

    def last(self):
        return self.done[-1]


class ParsedResp(object):
    def __init__(self,
                 raw_string,
                 charsets=None,
                 rules=None,
                 diag_lookup=None,
                 element_lookup=None,

                 on_fail=None,
                 on_rem_string=None,
                 on_pass=None):

        self.ruleset = rules

        self.charsets = _PARSER_CONST.copy()
        self.charsets.update(charsets or {})

        self.on_fail = on_fail
        self.on_rem_string = on_rem_string
        self.on_pass = on_pass

        self._diag_lookup = diag_lookup
        self.raw_string = raw_string
        self.raw_length = len(raw_string)
        self.diags = DiagHelper(lookup=diag_lookup)
        self.elements = ElementHelper(lookup=element_lookup)

        self.work_queue = WorkQueue()
        self.working_text = ''
        self.working_pos = 0
        self.rem_string = deque(raw_string)

    def remaining(self):
        return ''.join(self.rem_string)

    @property
    def position(self):
        return self.raw_length - len(self.rem_string)

    def add_note(self, diag=None, position=None, element_name=None, element=None, element_pos=None):
        position = position or self.position

        if diag is not None:
            self.diags.add(diag, position=position)

        if element_name is not None:
            element_pos = element_pos or position-len(element)
            if isinstance(element, list):
                element = ''.join(element)
            self.elements.add(element_name, element=element, position=element_pos)

    '''
    def __call__(self, parse_str, rule=None):
        tmp_data = ParsedItem(parse_str)
        self.parse_str(tmp_data, rule)
        return tmp_data
    '''

    '''
    def __int__(self):
        return self._max_diag


    def __getitem__(self, item):
        return self.elements(element_name=item)

    def __call__(self, email_in):
        self.parse(email_in)
        return self._max_diag
    '''


"""
class ParsedItem(object):

    def __init__(self, raw_string):
        '''
                 parser=None,
                 parser_start_rule=None,
                 diag_codes=None):
        '''
        # self.parser = parser or parser_ops.parse_email
        # self.parser_start_rule = parser_start_rule or 'start'

        self.rem_string = deque(raw_string)
        self.raw_string = raw_string
        self.raw_length = len(raw_string)
        self._diag_count = 0
        self._elements = {}
        self._diags = {}
        # self.work = WorkQueue()
        self._max_diag = 0

        # if raw_string is not None:
        #    self.parse(raw_string)

    '''
    def reset(self):
        self.rem_string.clear()
        self._elements.clear()
        self._diags.clear()
        self.work.clear()
        self._max_diag = 0
    '''
    '''
    def parse(self, raw_email):
        log_debug('Parse: %s', raw_email)
        self.reset()
        self.rem_string.extend(raw_email)
        self.raw_length = len(raw_email)
        self.parser(self, rule=self.parser_start_rule)
    '''

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

    '''
    def __call__(self, email_in):
        self.parse(email_in)
        return self._max_diag
    '''

"""
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
            # print('adding %r back to %r ' % (popped_text, is_email_obj.rem_string))
            popped_text.reverse()
            is_email_obj.rem_string.extendleft(popped_text)
        if fail_flag is not None:
            is_email_obj.add_note(diag=fail_flag, pos=position)

class RuleError(Exception):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return self.msg

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


# <editor-fold desc="************ Rule Builder Helpers *******************************">
class RuleBuilderItem(object):
    def __init__(self, builder, rule_str):
        self.init_rule_str = rule_str
        self.builder = builder
        if isinstance(rule_str, list):
            if len(rule_str) == 1:
                self._rule = Opt(rule_str[0])
            else:
                raise RuleError('Rule Builder Error: no more than one item allows in optionals (through lists), %r passed' % rule_str)
        elif issubclass(rule_str.__class__, BaseRule):
            self._rule = rule_str

        elif isinstance(rule_str, str):
            self._kwargs = {}
            self.rule_type = None
            self.is_repeated = False
            self.is_charset = False
            self.is_quoted_string = False
            self.is_optional = False
            self.is_case_sensitive = True
            self.return_string = True
            self._rule = None
            self.rule_str = None
            self._parse_rule_str()
        else:
            raise RuleError('Rule Builder Error: unknown rule object: %r' % rule_str)

    def kwargs(self, kwargs=None):
        if kwargs is None:
            return self.kwargs
        else:
            kwargs.update(self._kwargs)
            return kwargs

    def rule(self, rule_type=None, data=None, **kwargs):
        if rule_type is not None or \
                self._rule is None or \
                (self._rule is LookupRule and data is not None):

            self.set_type(rule_type=rule_type, data=data)
            self._rule = self.rule_type(self.rule_str, **self.kwargs(kwargs))

        return self._rule

    def set_type(self, rule_type=None, data=None):
        if rule_type is not None:
            self.rule_type = rule_type
        elif self.is_charset:
            if self.is_repeated:
                self.rule_type = Word
            else:
                self.rule_type = Char
        elif self.is_quoted_string:
            if len(self.rule_str) > 1:
                self.rule_type = Word
            else:
                self.rule_type = Char
        else:
            if data is not None:
                if self.rule_str in data.ruleset:
                    self.rule_type = Rule
                elif self.rule_str in data.charsets:
                    self.rule_str = data.charsets[self.rule_str]
                    if self.is_repeated:
                        self.rule_type = Word
                    else:
                        self.rule_type = Char
                else:
                    raise RuleError('Rule %s not found in lookups' % self.operations)
            else:
                self.rule_type = LookupRule
        return self.rule_type

    def _parse_rule_str(self):
        """
        string formatting options:
        'abcde' Rule('abcde')
        '/abcde' = Char('abcde')
        '"foo"' = QString('foo', case=True)
        '^"Foo"' = QString('foo', case=False)
        '2*34abcde' = Rule(abcde, min=2, max=34)
        '2*3/abcde' = Word('abcde', min=3, max=34)
        '[abcde]' = Rule(abcde, optional=True)
        '-abcde' = Rule(abcde, return_string=False)
        """
        key_chars = '1234567890*[/"^'
        repeat_chars = '1234567890*'

        rule_str_in = self.init_rule_str

        if rule_str_in[0] == '[' and rule_str_in[-1] == ']':
            self.is_optional = True
            rule_str_in = rule_str_in[1:-1]
            self._kwargs['optional'] = True

        while rule_str_in and rule_str_in[0] in key_chars:
            if rule_str_in[0] == '"' and rule_str_in[-1] == '"':
                self.is_quoted_string = True
                rule_str_in = rule_str_in[1:-1]
                self._kwargs['quoted_str'] = True
                break   # since this means that everything else is a quoted string

            elif rule_str_in[0] == '-':
                rule_str_in = rule_str_in[1:]
                self.return_string = False
                self._kwargs['return_string'] = False

            elif rule_str_in[0] == '^' and rule_str_in[1] == '"' and rule_str_in[-1] == '"':
                self.is_quoted_string = True
                self.is_case_sensitive = False
                rule_str_in = rule_str_in[2:-1]
                self._kwargs['case_sensitive'] = False
                break   # since this means that everything else is a quoted string

            elif rule_str_in[0] == '/':
                self.is_charset = True
                rule_str_in = rule_str_in[1:]
                break # since means everything else is a char_set

            elif rule_str_in[0] in repeat_chars:
                self.is_repeated = True
                tmp_repeat_str = []

                for c in rule_str_in:
                    if c in repeat_chars:
                        tmp_repeat_str.append(c)
                    else:
                        break

                rule_str_in = rule_str_in[len(tmp_repeat_str):]

                tmp_repeat_str = ''.join(tmp_repeat_str)

                if '*' in tmp_repeat_str:
                    min_repeat, max_repeat = tmp_repeat_str.split('*')
                    if min_repeat == '':
                        min_repeat = ISEMAIL_MIN_REPEAT
                    if max_repeat == '':
                        max_repeat = ISEMAIL_MAX_REPEAT
                else:
                    min_repeat = tmp_repeat_str
                    max_repeat = tmp_repeat_str

                self._kwargs['min_repeat'] = int(min_repeat)
                self._kwargs['max_repeat'] = int(max_repeat)

            else:
                raise RuleError('Invalid rule string: %s' % rule_str_in)

        self.rule_str = rule_str_in

    def run(self, data, **kwargs):
        return self.rule(data=data, **kwargs)(data)


class RuleBuilder(object):
    """
    Returns Rule Objects from strings
    RuleBuilder["rulestring"] returns the rule builder object
    RuleBuilder("rulestring") returns the a rule object
    RuleBuilder["rulestring"](*args, **kwargs) wil run the rule object

    """

    def __init__(self):
        self.rules = {}

    def parsed(self, rule_str):
        if isinstance(rule_str, list):
            if len(rule_str) == 1:
                rule_str = '[%s]' % rule_str[0]
            else:
                raise TypeError('invalid argument: %r, if a list is passed it must only have one object' % rule_str)
        if not isinstance(rule_str, str):
            raise TypeError('%r is not a string rule' % rule_str)
        if rule_str not in self.rules:
            tmp_item = RuleBuilderItem(self, rule_str)
            self.rules[rule_str] = tmp_item
        return self.rules[rule_str]

    def rule(self, rule_str, rule_type=None, data=None, **kwargs):
        if isinstance(rule_str, str):
            return self.parsed(rule_str).rule(rule_type=rule_type, data=data, **kwargs)
        else:
            return rule_str

    def run(self, rule_str, data, **kwargs):
        return self.parsed(rule_str).run(data, **kwargs)

    def __call__(self, rule_str, **kwargs):
        return self[rule_str].rule(**kwargs)

make_rule = RuleBuilder()


def parse_string(self, rule, raw_string, **kwargs):
    data = ParsedResp(raw_string=raw_string, **kwargs)

    try:
        self(data)

    except NoElementError:
        if data.on_fail is not None:
            data.add_note(diag=data.on_fail, position=0)
    else:
        if data.rem_string and data.on_rem_string is not None:
            data.add_note(diag=data.on_rem_string)
        elif data.on_pass is not None:
            data.add_note(diag=data.on_pass, position=0)



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

# </editor-fold>

"""
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
        self.charsets = _PARSER_CONST.copy()
        self.charsets.update(char_sets or {})
        self.on_fail = on_fail
        self.on_rem_string = on_rem_string
        self.on_pass = on_pass

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
    '''
    def __contains__(self, item):
        if item in self.ruleset:
            return True
        if item in self.charsets:
            return True
        return False
    '''
    def __call__(self, parse_str, rule=None):
        tmp_data = ParsedItem(parse_str)
        self.parse_str(tmp_data, rule)
        return tmp_data

"""

class ParserAction(object):

    def __init__(self, pass_diag=None, fail_diag=None, name=None):
        self.pass_diag = pass_diag
        self.fail_diag = fail_diag
        self.name = name

    def __call__(self, data, passed, element, position):
        if passed:
            diag = self.pass_diag
        else:
            diag = self.fail_diag
        data.add_note(diag=diag, element_name=self.name, element=element, position=position)

    def __repr__(self):
        tmp_ret_list = []
        if self.name is not None:
            tmp_ret_list.append('(%s)' % self.name)

        if self.pass_diag is not None or self.fail_diag is not None:
            pf_diag_list = []
            if self.pass_diag is not None:
                pf_diag_list.append('P:%s' % self.pass_diag)
            if self.fail_diag is not None:
                pf_diag_list.append('F:%s' % self.fail_diag)
            tmp_ret_list.append('[%s]' % '/'.join(pf_diag_list))
        if tmp_ret_list:
            return 'Action: %s' % ' '.join(tmp_ret_list)
        else:
            return 'Action: Empty'




# <editor-fold desc="************** Rules *****************************************">
class BaseRule(object):
    rule_type = 'BaseRule'
    parses_chars = False
    single_op = True
    returns_info = True
    allow_repeat = True
    should_repeat = False
    repr_format = '{opt_pre}{pre_rule}{type}({pre_ops}{ops}{post_ops}){post_rule}{opt_post}'

    if should_repeat:
        def_min_repeat = ISEMAIL_MIN_REPEAT
        def_max_repeat = ISEMAIL_MAX_REPEAT
    else:
        def_min_repeat = 1
        def_max_repeat = 1


    def __init__(self, *operations, **kwargs):
        """
        optional=False
        return_string=True
        min_repeat=None
        max_repeat=None
        inner_optional=False
        actions=None
        next=None
        not_next=None

        old -----
        on_fail=None
        on_pass=None
        element_name=None

        """
        log_ddebug('starting to load rule type: "%s" / operations=%r / kwargs=%r)', self.rule_type, operations, kwargs)
        if self.parses_chars:
            tmp_arg = make_rule.parsed(operations[0])
            kwargs = tmp_arg.kwargs(kwargs)
            self.operations = tmp_arg.rule_str
            self.is_quoted_string = kwargs.get('quoted_str', False)
        else:
            if self.single_op:
                self.operations = make_rule.rule(operations[0])
            else:
                self.operations = []
                for o in operations:
                    self.operations.append(make_rule.rule(o))

        self.optional = kwargs.get('optional', False)
        self.return_string = kwargs.get('return_string', True)
        self.case_sensitive = kwargs.get('case_sensitive', True)
        '''
        self.on_fail = None
        self.on_pass = None
        self.element_name = None

        self.before_self = []
        self.after_self = []
        self.before_ops = []
        self.after_ops = []
        '''
        if 'next' in kwargs:
            self._next = make_rule.rule(kwargs['next'])
        else:
            self._next = None
        '''
        if 'not_next' in kwargs:
            self._not_next = make_rule.rule(kwargs['not_next'])
        '''
        self._actions = kwargs.get('actions', [])
        if not isinstance(self._actions, (list, tuple)):
            self._actions = [self._actions]
        if self.allow_repeat:
            self.min_repeat = kwargs.get('min_repeat', self.def_min_repeat)
            self.max_repeat = kwargs.get('max_repeat', self.def_max_repeat)
        else:
            self.min_repeat = 1
            self.max_repeat = 1
        log_ddebug('loaded rule type: %r', self)

    def _run_actions(self, data, passed, element, position):
        for a in self._actions:
            a(data, passed, element, position)

    def _run_next(self, data):
        if self._next is not None:
            try:
                try:
                    tmp_ret = self._next(data)
                except NoElementError:
                    op_passed = False
                    raise
                else:
                    op_passed = True
                    raise NoElementError(data, popped_text=tmp_ret)
            except NoElementError:
                if not op_passed:
                    raise NoElementError()

    def parse_string(self, raw_string, **kwargs):
        data = ParsedResp(raw_string=raw_string, **kwargs)

        try:
            self(data)

        except NoElementError:
            if data.on_fail is not None:
                data.add_note(diag=data.on_fail, position=0)
        else:
            if data.rem_string and data.on_rem_string is not None:
                data.add_note(diag=data.on_rem_string)
            elif data.on_pass is not None:
                data.add_note(diag=data.on_pass, position=0)

    def _operation_strs(self):
        if self.single_op:
            return '%r' % self.operations
        else:
            tmp_ret = []
            for r in self.operations:
                tmp_ret.append('%r' % r)
            return ', '.join(tmp_ret)
    '''
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
    '''
    '''
    def _set_repr_flags(self):

        if self.return_string:
            self._add_repr_flag(before_self='-')
    '''
    def __repr__(self):
        """
        format:
            Char{2*2,A,N,-}([operations])
        """
        tmp_flags = []
        if hasattr(self, 'min_repeat'):
            if self.min_repeat == ISEMAIL_MIN_REPEAT:
                tmp_min = ''
            else:
                tmp_min = str(self.min_repeat)

            if self.max_repeat == ISEMAIL_MAX_REPEAT:
                tmp_max = ''
            else:
                tmp_max = str(self.max_repeat)

            if tmp_min == tmp_max:
                if tmp_min != '1' and tmp_max != '1':
                    tmp_flags.append(tmp_min)

            else:
                tmp_flags.append('%s*%s' % (tmp_min, tmp_max))

        if self._actions:
            tmp_flags.append('A')
        if self._next:
            tmp_flags.append('N')
        if not self.return_string:
            tmp_flags.append('-')

        if tmp_flags:
            tmp_flags = '{%s}' % ','.join(tmp_flags)
        else:
            tmp_flags = ''
        if tmp_flags == '{}':
            tmp_flags = ''

        if self.optional:
            opt_pre = '['
            opt_post = ']'
        else:
            opt_pre = ''
            opt_post = ''

        tmp_ret = '{type}{flags}({opt_pre}{ops}{opt_post})'.format(
            type=self.rule_type,
            opt_pre=opt_pre,
            opt_post=opt_post,
            flags=tmp_flags,
            ops=self._operation_strs())

        return tmp_ret

    def __call__(self, data):
        log_ddebug('%s %r on data: %r', space_text, self, ''.join(data.rem_string))
        tmp = space_text.push
        tmp_pos = data.position

        tmp_ret_list = []

        try:
            if self.allow_repeat:
                for i in range(len(data.rem_string)):
                    if i > self.max_repeat - 1:
                        break
                    try:
                        tmp_ret = self.run(data)
                    except NoElementError:
                        if i < self.min_repeat - 1:
                            raise NoElementError(data, popped_text=tmp_ret_list)
                    else:
                        if tmp_ret is not None:
                            tmp_ret_list.extend(tmp_ret)
            else:
                tmp_ret_list.extend(self.run(data))

            try:
                self._run_next(data)
            except NoElementError:
                raise NoElementError(data, popped_text=tmp_ret_list)

        except NoElementError:
            tmp = space_text.pop
            log_ddebug('%s FAIL->"%r" failed!', space_text, self)
            self._run_actions(data, False, [], tmp_pos)
            if not self.optional:
                raise NoElementError()
        else:
            tmp = space_text.pop
            log_ddebug('%s PASS-> "%r" passed', space_text, self)
            self._run_actions(data, True, [], tmp_pos)

            if self.return_string:
                return tmp_ret_list
            else:
                return []

    def run(self, data):
        raise NotImplementedError()


class Rule(BaseRule):
    rule_type = 'Rule'

    def run(self, data):
        try:
            return data.ruleset[self.operations](data)
        except KeyError:
            raise AttributeError('Rule %s not found in rule dictionary' % self.operations)


class LookupRule(BaseRule):
    rule_type = 'Lookup'

    def __init__(self, parsed_rule_str, **kwargs):
        self.kwargs = kwargs
        self.operations = parsed_rule_str
        # super().__init__(*args, **kwargs)

    def __call__(self, data):
        return make_rule.run(self.operations, data, **self.kwargs)

    def run(self, data):
        pass


class Word(BaseRule):
    rule_type = 'Word'
    parses_chars = True
    allow_repeat = True
    should_repeat = True

    def run(self, data):
        '''
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

        log_ddebug('%s checking for: %r in %r', space_text, data.rem_string[0], self.operations)

        if data.rem_string[0] in self.operations:
            log_ddebug('%s found', space_text)
            return data.rem_string.popleft()
        else:
            log_ddebug('%s missed', space_text)
            raise NoElementError(data)


class Char(Word):
    rule_type = 'Char'
    parses_chars = True
    should_repeat = False


class QString(BaseRule):
    rule_type = 'QString'
    parses_chars = True
    quoted_string = True
    should_repeat = False

    def run(self, data):
        log_ddebug('%s checking for quoted string: "%s" in %r', space_text, self.operations, data.rem_string)

        tmp_ret = []
        for c in self.operations:
            tmp_next_char = data.rem_string[0]
            if tmp_next_char == c:
                tmp_ret.append(data.rem_string.popleft())
            else:
                raise NoElementError(data, popped_text=tmp_ret)
        return tmp_ret


class And(BaseRule):
    rule_type = 'And'
    single_op = False
    allow_repeat = True
    should_repeat = False

    def __init__(self, *operations, min_repeat=1, max_repeat=1, **kwargs):
        self.operations = operations
        self.min_repeat = min_repeat
        self.max_repeat = max_repeat
        super().__init__(**kwargs)

    def run(self, data):
        tmp_ret_list = []
        log_debug('all must match---')
        for op in self.operations:
            try:
                tmp_ret = op(self, data)
            except NoElementError:
                raise NoElementError(data, popped_text=tmp_ret_list)
            else:
                if tmp_ret is not None:
                    tmp_ret_list.extend(tmp_ret)

        if not tmp_ret_list:
            raise NoElementError()

        return tmp_ret_list


class Or(BaseRule):
    rule_type = 'Or'
    single_op = False
    allow_repeat = True
    should_repeat = False

    def __init__(self, *operations, **kwargs):
        self.operations = operations
        super().__init__(**kwargs)

    def run(self, data):
        tmp_ret = []
        for op in self.operations:
            try:
                tmp_ret = op(self, data)
                break
            except NoElementError:
                pass
        if tmp_ret:
            return tmp_ret
        else:
            raise NoElementError()


class Opt(BaseRule):
    rule_type = 'Opt'
    repr_format = '{opt_pre}{ops}{opt_post}'
    allow_repeat = False
    should_repeat = False

    def __init__(self, *args, **kwargs):
        kwargs['optional'] = True
        super().__init__(*args, **kwargs)

    def run(self, data):
        return self.operations(self, data)


class Repeat(BaseRule):
    rule_type = 'Repeat'
    repr_format = '{opt_pre}{pre_rule}({pre_ops}{ops}{post_ops}){post_rule}{opt_post}'
    single_op = True
    allow_repeat = True
    should_repeat = True

    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            super().__init__(args[0], **kwargs)
        elif len(args) == 2:
            if isinstance(args[0], str):
                tmp_opt = make_rule.parsed(args[0])
                super().__init__(args[1], **tmp_opt.kwargs(kwargs))
            elif isinstance(args[0], int):
                kwargs['min_repeat'] = args[0]
                kwargs['max_repeat'] = args[0]
                super().__init__(args[1], **kwargs)
            else:
                raise RuleError('Error processing repeat rule arg: %r' % args[0])
        else:
            raise RuleError('invalid number of args for repeat rule: %r' % args)

    def run(self, data):
        return self.operations(self, data)

'''
class MarkParser(ParserRule):
    rule_type = 'mark'

    def __init__(self, operation, **kwargs):
        self.operation = operation
        super().__init__(**kwargs)

    def run(self, parser, data):
        return self.operation(self, parser, data)
'''
'''
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
'''


class MeasureBaseRule(BaseRule):
    rule_type = 'MeasureBase'
    single_op = True
    allow_repeat = False
    parses_chars = False

    def __init__(self, measure_string, operation, **kwargs):
        tmp_args = make_rule.parsed(measure_string)
        self.measure_str = tmp_args.rule_str
        super().__init__(operation, **tmp_args.kwargs(kwargs))

    def __call__(self, data):
        log_ddebug('%s %r on data: %r', space_text, self, ''.join(data.rem_string))
        tmp = space_text.push
        tmp_pos = data.position

        tmp_ret = self.operations(data)

        try:
            self.run(tmp_ret)

        except NoElementError:
            tmp = space_text.pop
            self._run_actions(data, False, [], tmp_pos)
            if not self.optional:
                raise NoElementError(popped_text=tmp_ret)
        else:
            tmp = space_text.pop
            log_ddebug('%s PASS-> "%r" passed', space_text, self)
            self._run_actions(data, True, [], tmp_pos)
            '''
            if self.on_pass or self.element_name:
                data.add_note(diag=self.on_pass, element_name=self.element_name, element=tmp_ret, position=tmp_pos)
            '''
            if self.return_string:
                return tmp_ret
            else:
                return []

    def run(self, op_data):
        raise NotImplementedError()


class Count(MeasureBaseRule):
    rule_type = 'Count'

    def run(self, op_data):

        if self.is_quoted_string:
            tmp_str = ''.join(op_data)
        else:
            tmp_str = op_data

        tmp_count = tmp_str.count(self.measure_str)

        if not self.min_repeat < tmp_count < self.max_repeat:
            raise NoElementError()


class Len(BaseRule):
    rule_type = 'Len'

    def run(self, op_data):

        tmp_count = len(op_data)

        if not self.min_repeat < tmp_count < self.max_repeat:
            raise NoElementError()
# </editor-fold>

