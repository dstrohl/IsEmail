from helpers.general import _UNSET
from copy import deepcopy, copy
from collections import namedtuple


"""
    flag types
    <default_state><field_name><current_state>

    x/x/x|<field_name>

    (<allow none flag>/<default>/<current>)
    (<allow none flag>/default-current)
    (default/current)
    (default-current)

    or

    <allow_none_flag><default-current>field_name


    States:
        + = True
        - = False (or no flag)
        * = None

    T/F flag default false= 'string_name' or '-|string_name'
    T/F flag default true = '+|string_name'
    T/F/N flag initial none = '*|string_name'

    T/F flag default false, current True = '-+|string_name'
    T/F flag default true, default false = '+-|string_name'
    T/F/N flag initial none, current_ none = '*|string_name'
    T/F/N flag initial none, default_false, current_none = '*-*|string_name'


    TF flag set default all-false = ('flag_1', 'flag_2', 'flag_3')
    TF flag set default flag = ('-|flag_1', '+|flag_2', '-|flag_3')
    TF flag set initial None = ('*', 'flag_1', 'flag_2', 'flag_3')
    TF flag set initial None current marked = ('*', '--|flag_1', '++|flag_2', '--|flag_3')

    named flag set default None = ('flag_set_name', ('flag_1', 'flag_2', 'flag_3'))
    named flag set default flag = ('flag_set_name', ('-|flag_1', '-|flag_2', '+|flag_3'))


    Set Rules:
        - Initial None:
            - clear resets to None
            - reset resets to defaults
        - normal
            - clear + reset resets to defaults
            - if no default marked, default = last field
        - allow all False
            - clear resets to all False
            - reset resets to defaults
            - if no default marked, all false
        - allow all false + initial none
            - clear resets to None
            - reset resets to defaults
            - if no default marked, default = all False

    item rules
        - with initial None
            - clear resets to None
            - reset resets to default
        - normal
            - clear Sets to False
            - reset resets to default
            - default = false if not marked

"""
PREFIX_LOOKUP = {'+': True, '-': False, '*': None, '^': _UNSET}
PREFIX_STRING = {True: '+', False: '-', None: '*'}

"""
class FlagDefs(object):
    name = ''
    value = _UNSET
    default = _UNSET    

    def __init__(self, *args, **kwargs):
"""


def make_icon(initial_none, default, value, pretty=False):
    if initial_none:
        tmp_ret = ['*']
    else:
        tmp_ret = []

    tmp_ret.append(PREFIX_STRING[default])
    tmp_ret.append(PREFIX_STRING[value])

    if pretty:
        tmp_ret = '/'.join(tmp_ret)
    else:
        tmp_ret = ''.join(tmp_ret)

    return tmp_ret

'''
def strip_flag(flag_str):
    return flag_str.strip('+-*^')
'''

'''
def strip_value(name, current=_UNSET):
    return name.strip('+-*^'), PREFIX_LOOKUP.get(name[-1], current)

'''

'''
def parse_flag(name, return_as_obj=True, initial_none=False, **kwargs):
    
    name = str(name)
    if name.strip('+-*|') == '':
        raise AttributeError('Flag object must have a name, field passed = %r' % name)

    initial_none = initial_none or name[0] == '*'
    initial_name = name

    if initial_none:
        default = None
        value = None
    else:
        default = False
        value = False

    if '|' in name:
        state_flags, name = name.split('|', 1)

    elif name[0] in '*-+':
        state_flags = ''
        for i in name:
            if i in '*-+':
                state_flags += i
        name = name.strip('*-+')
    else:
        state_flags = []

    if state_flags:
        if '/' in state_flags:
            state_flags = state_flags.split('/')

        if len(state_flags) == 3:
            if state_flags[0] != '*':
                raise AttributeError('Invalud Flag Set for flag: %s' % initial_name)
            default = PREFIX_LOOKUP[state_flags[1]]
            value = PREFIX_LOOKUP[state_flags[2]]
        elif len(state_flags) == 2:
            default = PREFIX_LOOKUP[state_flags[0]]
            value = PREFIX_LOOKUP[state_flags[1]]

        elif len(state_flags) == 1:
            default = PREFIX_LOOKUP[state_flags[0]]
            value = default

    value = kwargs.pop('value', value)
    default = kwargs.pop('value', default)

    if value is None and not initial_none:
        raise AttributeError('Value cannot be None if initial_none is not set')

    if not name.isidentifier() or name[0] == '_':
        raise AttributeError('Flag name %r is invalid' % name)
    
    if return_as_obj:
        kwargs.update(dict(name=name, default=default, value=value, initial_none=initial_none))
        return FlagObj(**kwargs)

    else:
        return dict(name=name, default=default, value=value, initial_none=initial_none)


def parse_flagset(name, *flags, **kwargs):
    initial_all_none = False
    allow_all_false = False
    tmp_flags = []
    current_flag = _UNSET

    if not flags:
        raise AttributeError('Flags must be specified')

    if name is not None and (not name.isidentifier or name[0] == '_'):
        raise AttributeError('FlagSet name %r is invalid' % name)

    if len(flags) == 1:
        if ' ' in flags:
            flags = flags[0].split(' ')
        else:
            raise AttributeError('More than 1 flag must be specified')

    if flags[0].strip('*-') == '':
        if '*' in flags[0]:
            initial_all_none = True
        if '-' in flags[0]:
            allow_all_false = True
        flags = flags[1:]

    has_default = False
    has_default_true = False
    has_value = False
    has_true = False

    for flag in flags:
        if initial_all_none:
            flag = "*" + flag
        tmp_flag = parse_flag(flag, clean=False, return_as_obj=False)
        tmp_flags.append(tmp_flag)

        if tmp_flag['default'] is not _UNSET:
            has_default = True
            if tmp_flag['default']:
                if has_default_true:
                    raise AttributeError('Cannot have more than one default flag marked as True')
                else:
                    has_default_true = True

        if tmp_flag['value'] is not _UNSET:
            has_value = True

            if tmp_flag['value']:
                if has_true:
                    raise AttributeError('Cannot have more than one flag marked as True')
                else:
                    has_true = True
    
    if initial_all_none and not has_default:
        default_as = 'none'
    else:
        if allow_all_false and not has_default_true:
            default_as = 'ff'
        else:
            default_as = 'tf'
            
    if initial_all_none and not has_value:
        value_as = 'none'
        current_flag = _UNSET
    else:
        if allow_all_false and not has_true:
            value_as = 'ff'
            current_flag = None
        else:
            value_as = 'tf'

    if default_as == 'tf' and not has_default_true:
        tmp_flags[-1]['default'] = True
        
    for flag in tmp_flags:
        if default_as == 'none':
            flag['default'] = None
        elif default_as == 'ff':
            flag['default'] = False
        else:
            if not flag['default']:
                flag['default'] = False
        
        if value_as == 'none':
            flag['value'] = None
        elif value_as == 'ff':
            flag['value'] = False
        else:
            if flag['value'] == _UNSET:
                if has_true:
                    flag['value'] = False
                else:
                    flag['value'] = flag['default']
            if not flag['value']:
                flag['value'] = False
            else:
                current_flag = flag['name']
    
    """
    default     value

    None        None        = not has_defaults, initial_none, not has_value
    None        TF          = not has_defaults, initial_none, has_value, has_true or Not allow_all_false
    None        FF          = not has_defaults, initial_none, has_value, allow_all_false
    TF          TF          = has_defaults, has_true_default, or not allow_all_false, has_true or not allow_all_false
    FF          FF          = has_defaults, allow_all_false,
    TF          FF          = has_defaults, allow_all_false, has_default_true.

    Default:

    None        = not has_defaults, initial_none

    TF          = has_defaults, has_true_default, or not allow_all_false,
    
    FF          = has_defaults, allow_all_false,

    Value:

    None        = not has_defaults, initial_none, not has_value

    TF          = has_value, has_true or Not allow_all_false

    FF          = has_value and not has_true, or not has_value, allow_all_false





    """
    
    kwargs.update(dict(
        name=name,
        flags=tmp_flags,
        allow_all_false=allow_all_false,
        initial_all_none=initial_all_none,
        current_flag=current_flag))
    return FlagSetObj(**kwargs)
'''

class FlagObj(object):
    flag_set = False

    def __init__(self, name, initial_none=False, locked=True, **kwargs):
        # self.name = name
        # self.default = default
        # self.value = value
        # self.initial_none = initial_none
        self.locked = locked

        name = str(name)
        if name.strip('+-*|') == '':
            raise AttributeError('Flag object must have a name, field passed = %r' % name)

        self.initial_none = initial_none or name[0] == '*'
        initial_name = name

        if self.initial_none:
            self.default = None
            self.value = None
        else:
            self.default = False
            self.value = False

        if '|' in name:
            state_flags, self.name = name.split('|', 1)

        elif name[0] in '*-+':
            state_flags = ''
            for i in name:
                if i in '*-+':
                    state_flags += i
            self.name = name.strip('*-+')
        else:
            state_flags = []
            self.name = name

        if state_flags:
            if '/' in state_flags:
                state_flags = state_flags.split('/')

            if len(state_flags) == 3:
                if state_flags[0] != '*':
                    raise AttributeError('Invalud Flag Set for flag: %s' % initial_name)
                self.default = PREFIX_LOOKUP[state_flags[1]]
                self.value = PREFIX_LOOKUP[state_flags[2]]
            elif len(state_flags) == 2:
                self.default = PREFIX_LOOKUP[state_flags[0]]
                self.value = PREFIX_LOOKUP[state_flags[1]]

            elif len(state_flags) == 1:
                self.default = PREFIX_LOOKUP[state_flags[0]]
                self.value = self.default

        self.value = kwargs.pop('value', self.value)
        self.default = kwargs.pop('value', self.default)

        if self.value is None and not self.initial_none:
            raise AttributeError('Value cannot be None if initial_none is not set')

        if not self.name.isidentifier() or self.name[0] == '_':
            raise AttributeError('Flag name %r is invalid' % name)

    def copy(self):
        return self.__class__(self.build_args, locked=self.locked)
    __copy__ = copy

    def __deepcopy__(self, memo):
        result = self.copy()
        memo[id(self)] = result
        return result

    def set(self, flag=None, value=True):
        self.value = bool(value)

    def update(self, other):
        if isinstance(other, self.__class__):
            self.value = other.value
            self.default = other.default
            self.initial_none = other.initial_none
            self.locked = other.locked
        else:
            self.set(other)

    def get(self, flag=None):
        return self.value

    def reset(self):
        self.value = self.default

    def clear(self):
        """
        - with initial None
            - clear resets to None
        - normal
            - clear Sets to False

        """
        if self.initial_none:
            self.value = None
        else:
            self.value = False

    @property
    def is_set(self):
        return self.value is not None

    @property
    def has_default(self):
        return self.default is not _UNSET

    @property
    def is_default(self):
        return self.value == self.default

    def __bool__(self):
        return bool(self.value)

    def _get_dict(self, *flags_filter, inc_sets=True, flat=False, filter_for=_UNSET):
        tmp_dict = {}
        if not flags_filter or self.name in flags_filter:
            if filter_for is _UNSET or self.value in filter_for:
                tmp_dict[self.name] = self.value
        return tmp_dict

    def _str(self, *fields_filter, show_state=True, show_default=True, pretty=True, filter_for=_UNSET, **kwargs):
        tmp_ret = ''
        if not fields_filter or self.name in fields_filter:
            if filter_for is _UNSET or self.value in filter_for:
                if show_state:
                    if show_default:
                        tmp_ret = '%s|%s' % (
                            make_icon(initial_none=self.initial_none, default=self.default,
                                      value=self.value, pretty=pretty),
                            self.name)
                    else:
                        tmp_ret = '%s|%s' % (PREFIX_STRING[self.value], self.name)
                else:
                    tmp_ret = self.name

        return tmp_ret

    @property
    def build_args(self):
        return self._str(show_state=True, show_default=True, pretty=False)

    def __str__(self):
        return self._str(pretty=True)

    def __repr__(self):
        tmp_ret = 'SingleFlagObject(%s)' % self.build_args
        return tmp_ret

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, self.__class__):
            return self.name == other.name and self.value == other.value
        elif isinstance(other, bool):
            return self.value == other
        elif other is None:
            return self.value is None

    def __ne__(self, other):
        return not self == other


class FlagSetObj(object):
    flag_set = True

    def __init__(self, name, *flags, allow_all_false=False, initial_all_none=False, locked=False, **kwargs):
        self.name = name
        self.locked = locked
        self.initial_all_none = initial_all_none
        self.allow_all_false = allow_all_false
        self.flags = {}
        self.flag_order = []

        default_true_flag = None

        if flags[0].strip('*-') == '':
            if '*' in flags[0]:
                self.initial_all_none = True
            if '-' in flags[0]:
                self.allow_all_false = True
            flags = flags[1:]

        if self.initial_all_none:
            self.current_flag = _UNSET
        else:
            self.current_flag = None

        for flag in flags:
            tmp_flag = FlagObj(flag, initial_none=self.initial_all_none, locked=True)
            self.flags[tmp_flag.name] = tmp_flag
            self.flag_order.append(tmp_flag)
            if tmp_flag:
                if self.current_flag:
                    raise AttributeError('Error, cannot set flag %s to True as existing flag %s is already True' % (tmp_flag.name, self.current_flag.name))
                self.current_flag = tmp_flag
            if tmp_flag.default:
                if default_true_flag:
                    raise AttributeError('Error, cannot set default flag %s to True as existing default flag %s is already True' % (tmp_flag.name, default_true_flag.name))
                default_true_flag = tmp_flag

        if not self.current_flag and not self.initial_all_none and not self.allow_all_false:
            self.set(self.flag_order[-1].name, True)
        if ((default_true_flag and not default_true_flag.default) or default_true_flag is None) and not self.initial_all_none and not self.allow_all_false:
            self.flag_order[-1].default = True

    def copy(self):
        name, tmp_bl = self.build_args
        return self.__class__(name, *tmp_bl)
    __copy__ = copy

    def __deepcopy__(self, memo):
        result = self.copy()
        memo[id(self)] = result
        return result

    def set(self, flag, value):
        print('Setting %r to %r on %r' % (flag, value, self))
        if bool(value):
            if self.current_flag is _UNSET:
                for set_flag in self.flag_order:
                    if set_flag.name == flag:
                        set_flag.set(value=True)
                        self.current_flag = set_flag
                    else:
                        set_flag.set(value=False)
            else:
                if self.current_flag is not None:
                    self.current_flag.set(value=False)
                self.current_flag = self.flags[flag]
                self.current_flag.set(value=True)
        else:
            if self.allow_all_false:
                if self.current_flag is _UNSET:
                    for set_flag in self.flag_order:
                        set_flag.set(value=False)
                    self.current_flag = None
                else:
                    if self.current_flag is not None and self.current_flag == flag:
                        self.current_flag.set(value=False)
                        self.current_flag = None
            else:
                raise AttributeError('Cannot set item to false unless "allow_all_false" set')
        print('Returning: %r\n\n' % self)

    def get(self, flag):
        return self.flags[flag].get()

    def update(self, other):
        if isinstance(other, self.__class__):
            for flag in other.flag_order:
                self.update(flag)

        elif isinstance(other, FlagObj):
            self.flags[other.name].update(other)
            if other.name == self.current_flag.name and other is False:
                if not self.allow_all_false:
                    raise AttributeError('Cannot set item to false unless "allow_all_false" set')
                self.current_flag = None

            elif other.value is None:
                raise AttributeError('Cannot set item to None directly')

            elif other and other.name != self.current_flag.name:
                self.current_flag = self.flags[other.name]

        else:
            other = FlagObj(other)
            self.update(other)

    def reset(self):
        """
        Set Rules:
        - Initial None:
            - reset resets to defaults
        - normal
            - clear + reset resets to defaults
            - if no default marked, default = last flag
        - allow all False
            - reset resets to defaults
            - if no default marked, all false
        - allow all false + initial none
            - reset resets to defaults
            - if no default marked, default = all False

        :return:
        """
        if self.initial_all_none:
            self.current_flag = _UNSET
        else:
            self.current_flag = None

        for flag in self.flag_order:
            flag.reset()
            if flag:
                self.current_flag = flag

    def clear(self):
        """
        Set Rules:
        - Initial None:
            - clear resets to None
        - normal
            - clear + reset resets to defaults
        - allow all False
            - clear resets to all False
        - allow all false + initial none
            - clear resets to None

        :return:
        """
        if self.initial_all_none:
            for f in self.flag_order:
                f.clear()
            self.current_flag = _UNSET
        elif self.allow_all_false:
            for f in self.flag_order:
                f.set(value=False)
            self.current_flag = None
        else:
            self.current_flag = None
            for f in self.flag_order:
                f.reset()
                if f.value:
                    self.current_flag = f
            if self.current_flag is None:
                self.set(self.flag_order[-1].name, True)

    @property
    def is_set(self):
        return self.current_flag is not _UNSET

    def __bool__(self):
        return self.current_flag is not None and self.current_flag is not _UNSET

    def _flags_str(self, *flags_filter, show_state=True, show_default=True, pretty=True, filter_for=_UNSET):
        tmp_ret = []
        for flag in self.flag_order:
            tmp_item = flag._str(*flags_filter, show_state=show_state,
                                  show_default=show_default, pretty=pretty, filter_for=filter_for)
            if tmp_item:
                tmp_ret.append(tmp_item)

        return tmp_ret

    def _get_dict(self, *flags_filter, inc_sets=True, flat=False, filter_for=_UNSET):
        tmp_dict = {}
        if inc_sets:
            if flags_filter and self.name in flags_filter:
                flags_filter = []

            for f in self.flag_order:
                tmp_dict.update(f._get_dict(*flags_filter, filter_for=filter_for))

        if tmp_dict and not flat:
            tmp_dict = {self.name: tmp_dict.copy()}

        return tmp_dict

    def _str(self, *flags, show_state=True, show_default=True, pretty=True, show_name=True,
             filter_for=_UNSET, inc_sets=True, flat=False):
        tmp_ret = []
        if inc_sets:
            if flags and self.name in flags:
                flags = []
            tmp_ret = self._flags_str(
                *flags,
                show_state=show_state,
                show_default=show_default,
                pretty=pretty,
                filter_for=filter_for)

        if tmp_ret:
            tmp_ret = ', '.join(tmp_ret)

            if not flat:
                if show_name:
                    tmp_ret = '%s(%s)' % (self.name, tmp_ret)
                else:
                    tmp_ret = '(%s)' % tmp_ret
        else:
            tmp_ret = ''

        return tmp_ret

    @property
    def build_args(self):
        tmp_ret = []
        tmp_str = ''
        if self.initial_all_none:
            tmp_str += '*'
        if self.allow_all_false:
            tmp_str += '-'
        if tmp_str:
            tmp_ret.append(tmp_str)
        tmp_ret.extend(self._flags_str(show_state=True, show_default=True, pretty=False))

        return self.name, tmp_ret

    def __len__(self):
        return len(self.flags)

    def __str__(self):
        return self._str(pretty=True)

    def __repr__(self):
        name, flags = self.build_args
        if self.current_flag:
            cf = self.current_flag.name
        else:
            cf = str(self.current_flag)
        return 'SingleFlagObject(%s, %r, current=%s)' % (name, ', '.join(flags), cf)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, self.__class__):
            if self.name != other.name or len(self) != len(other):
                return False
            for f in self.flag_order:
                if f != other[f.name]:
                    return False
        else:
            try:
                tmp_other = self.__class__(self.name, other)
                return self == tmp_other
            except AttributeError:
                return False
        return True

    def __ne__(self, other):
        return not self == other


# FlagSetDefs = namedtuple('FlagSetDefs', ('name', 'named', 'fields', 'init_none', 'default', 'all_false'))


class FlagHelper(object):
    """
    flag types
    T/F flag default false= 'string_name' or '-string_name'
    T/F flag default true = '+string_name'
    T/F/N flag initial none = '*string_name'

    TF flag set default all-false = ('flag_1', 'flag_2', 'flag_3')
    TF flag set default flag = ('flag_1', '+flag_2', 'flag_3')
    TF flag set initial None = ('*', 'flag_1', 'flag_2', 'flag_3')

    named flag set default None = ('flag_set_name', ('flag_1', 'flag_2', 'flag_3'))
    named flag set default flag = ('flag_set_name', ('flag_1', 'flag_2', '+flag_3'))

    via kwargs:

    T/F flag default false= flag_name=False
    T/F flag default true = flag_name=True
    T/F/N flag starts at None = flag_name=None

    T/F flags with default = flag_set_name = ('flag1', 'flag2', '+flag3')
    T/F flags with allow_all_neg = flag_set_name = ('flag1', 'flag2', 'flag3')
    T/F flags with is_initial_none = flag_set_name = ('*', 'flag1', 'flag2', 'flag3')


    arg
    T/F flag flag default False = flag_name
    t/F/N flag initial none = *flag_name

    named flag set default None = ('flag_set_name', ('flag_1', 'flag_2', 'flag_3'))
    named flag set default flag = ('flag_set_name', ('flag_1', 'flag_2', '+flag_3'))


    LockedFlagHelper((flag_set_name, (

    Manager to handle easier setting of boolean type flags.

    locked:

        FM = FlagHelper()

        FM = FlagHelper()

        FM = FlagHelper('+flag_1_name', '-flag_2_name', 'flag_3_name')

        FM.flag1 = True
        FM.flag1
        >> True

        FM.no_flag
        >> False

        FM += 'flag'
        FM.flag
        >> False

        FM += ['flag1', '-flag2', 'flag3']
        FM.flag
        >> False

        FM -= ['existing flag', 'flag2']
        FM.existing_flag
        >> False

        for f in FM:
        >> <True flag names>, ...

        FM[<flag_name>]
        >> True/False

        FM._clear()

        FM._get(filter_for=True)

        FM._get_dict()

        len(FM)

        bool()
         - when unlocked = has any flags

        copy()

        call()
            will return all true flags
            can pass list of flags to set

        str()
        flag1, flag2, flag3

        repr()
        FlagHelper(flag1=False, flag2=True, flag3=false)

    open

        FM = FlagHelper()

        FM = FlagHelper(
            add_on_plus=True,
            allow_us_start=False,
            case_sensitive=False,
            fix_names=False)

        FM = FlagHelper('+flag_1_name', '-flag_2_name', 'flag_3_name')

        FM.flag1 = True
        FM.flag1
        >> True

        FM.no_flag
        >> False

        FM += 'flag'
        FM.flag
        >> False

        FM += ['flag1', '-flag2', 'flag3']
        FM.flag
        >> False

        FM -= ['existing flag', 'flag2']
        FM.existing_flag
        >> False

        for f in FM:
        >> <True flag names>, ...

        FM[<flag_name>]
        >> True/False

        FM._clear()

        FM._get()

        FM._get_dict()

        len(FM)

        bool() has any flags
         - when locked = and all flags

        copy()

        call()
            will return all true flags
            can pass list of flags to set

        str()
        flag1, flag2, flag3

        repr()
        FlagHelper(flag1, flag2, flag3)


    """

    # _data = None

    def __init__(self, *flags, lock_flags=False, **flag_kwargs):

        self._init_flags = False

        # self._flag_data = {}
        # self._flag_set_data = {}

        # self._flag_sets = {}
        # self._flag_single_names = []
        # self._flag_set_flags = {}

        self._flag_data = {}
        self._flags = {}
        self._flag_sets = {}
        self._flag_singles = {}
        self._flag_order = []

        self._next_counter = 0
        self._max_counter = 999
        self._locked = False

        if flags or flag_kwargs:
            self._update(*flags, **flag_kwargs, locked=True)

        # self._default = dict(
        #     _flag_data=self._flag_data.copy(),
        #     _flag_set_data=self._flag_set_data.copy())

        self._locked = lock_flags

        self._init_flags = True
        self.__initialised = True

    def _rem(self, flag, raise_on_error=True):
        if self._locked:
            # print(repr(flag))
            raise AttributeError('flag %s cannot be deleted from locked helper' % repr(flag))

        if isinstance(flag, str):
            flag = str(flag).strip('*-+|')
            if flag not in self:
                if raise_on_error:
                    raise AttributeError('flag %r does not exist' % flag)
                else:
                    return
            else:
                flag = self._get_obj(flag)
                if flag.flag_set:
                    for f in flag:
                        del self._flags[f]
                    del self._flag_sets[flag.name]

                else:
                    del self._flag_singles[flag.name]
                    del self._flags[flag.name]

                del self._flag_data[flag.name]
                self._flag_order.remove(flag)

        elif isinstance(flag, (list, tuple)):
            for f in flag:
                self._rem(f)
        elif isinstance(flag, dict):
            for f, in flag:
                self._rem(f)
        elif isinstance(flag, self.__class__):
            for f in flag._flag_order:
                self._rem(f.name)
        elif isinstance(flag, (FlagObj, FlagSetObj)):
            self._rem(flag.name)
        else:
            self._rem(str(flag))
    __delitem__ = _rem

    # @staticmethod
    # def _validate_addr(flag):
    #     if flag.isidentifier() and flag[0] != '_':
    #         return True
    #     raise AttributeError('Flag name %r is invalid' % flag)
    #
    # def _validate_add_addr(self, flag):
    #     if flag in self._flag_data:
    #         return True
    #     elif flag.isidentifier() and flag[0] != '_':
    #         if self._locked:
    #             raise AttributeError('Flag not present and flags locked')
    #         return True
    #     raise AttributeError('Flag name %r is invalid' % flag)
    #
    # @staticmethod
    # def _flag_split(flag_str, value=_UNSET):
    #     tmp_flag = flag_str[0]
    #     if tmp_flag not in '+-*':
    #         if value is _UNSET:
    #             return flag_str, False
    #         else:
    #             return flag_str, bool(value)
    #     else:
    #         if value is _UNSET:
    #             return flag_str[1:], PREFIX_LOOKUP[tmp_flag]
    #         else:
    #             return flag_str[1:], bool(value)

    def _update(self, *flags, locked=False, overwrite_flag=False, **flag_kwargs):
        for a in flags:
            self._add(a, locked=locked, overwrite_flag=overwrite_flag)
        for flag, value in flag_kwargs.items():
            self._add(flag, value, locked=locked, overwrite_flag=overwrite_flag)

    def _add(self, flag_name, *values, locked=False, overwrite_flag=False):
        if isinstance(flag_name, str):
            if len(values) == 0:
                flag = FlagObj(flag_name, locked=locked)
            elif len(values) == 1:
                if isinstance(values[0], str):
                    values = values[0].split(' ')
                    flag = FlagSetObj(flag_name, *values, locked=locked)
                elif isinstance(values[0], (list, tuple)):
                    flag = FlagSetObj(flag_name, *values[0], locked=locked)
                else:
                    flag = FlagObj(flag_name, value=bool(values[0]), locked=locked)
            else:
                flag = FlagSetObj(flag_name, *values, locked=locked)

        elif isinstance(flag_name, (list, tuple)):
            if len(flag_name) == 2 and isinstance(flag_name[1], (list, tuple)):
                flag = FlagSetObj(flag_name[0], *flag_name[1], locked=locked)
            else:
                for f in flag_name:
                    self._add(f, locked=locked, overwrite_flag=overwrite_flag)
                return

        elif isinstance(flag_name, dict):
            self._update(**flag_name)
            return

        elif isinstance(flag_name, self.__class__):
            for f in flag_name._flag_order:
                self._add(f, locked=locked, overwrite_flag=overwrite_flag)
            return

        elif isinstance(flag_name, (FlagSetObj, FlagObj)):
            flag = flag_name.copy()
            flag.locked = locked
        else:

            raise AttributeError('Unable to determine flag and value from %r and %r' % (flag_name, values))

        if flag.name in self:
            if not overwrite_flag:
                raise AttributeError('flag %s already exists in %r' % (flag.name, self))
            self._flag_data[flag.name].update(flag)

        else:
            if self._locked:
                raise AttributeError('Unable to add flag "%s", flag manager locked' % flag.name)

            self._flag_data[flag.name] = flag
            self._flag_order.append(flag)

            if flag.flag_set:
                self._flag_sets[flag.name] = flag
                for f in flag.flag_order:
                    self._flags[f.name] = flag
            else:
                self._flag_singles[flag.name] = flag
                self._flags[flag.name] = flag

    # @property
    # def _make_new_set_name(self):
    #     self._next_counter += 1
    #     tmp_ret = '__unnamed_set_%s__' % str(self._next_counter)
    #     while tmp_ret in self:
    #         tmp_ret = self._make_new_set_name
    #     return tmp_ret

    def _reset(self, rem_new=False):
        for f in self._flag_order:
            if not f.locked and rem_new:
                self._del(f.name)
            else:
                f.reset()

    def _clear(self, rem_new=False):
        for f in self._flag_order:
            if not f.locked and rem_new:
                self._del(f.name)
            else:
                f.clear()

    def _copy(self):
        tmp_ret = self.__class__(*self._build_args)
        tmp_ret._locked = self._locked
        return tmp_ret
    __copy__ = _copy

    def __deepcopy__(self, memo):
        result = self._copy()
        memo[id(self)] = result
        return result

    def _copy_default(self):
        tmp_ret = self._copy()
        tmp_ret._reset()
        return tmp_ret

    # def _get_set(self, set_name):
    #     return self._flag_sets[set_name]

    def _get_dict(self, *flags, inc_sets=True, flat=False, filter_for=_UNSET):
        tmp_ret = {}

        if filter_for is _UNSET:
            filter_for = (True, False, None)
        elif not isinstance(filter_for, (tuple, list)):
            filter_for = [filter_for]

        for flag in self._flag_order:
            tmp_ret.update(flag._get_dict(*flags, inc_sets=inc_sets, flat=flat, filter_for=filter_for))

        return tmp_ret

    def _get_values(self, *flags, inc_sets=True):
        tmp_ret = []
        if not flags:
            if inc_sets:
                for f in self._flag_order:
                    tmp_ret.append(bool(f))
            else:
                for f in self._flag_singles.values():
                    tmp_ret.append(bool(f))
        else:
            for f in flags:
                tmp_ret.append(bool(self._get(f)))
        return tmp_ret

    def _str(self, *flags, inc_sets=True, flat=False, show_state=True, show_default=True,
             pretty=True, as_string=True, filter_for=_UNSET, show_name=True):
        tmp_ret = []

        if filter_for is _UNSET:
            filter_for = (True, False, None)
        elif not isinstance(filter_for, (tuple, list)):
            filter_for = [filter_for]

        for flag in self._flag_order:
            tmp_item = flag._str(
                *flags,
                inc_sets=inc_sets,
                flat=flat,
                show_state=show_state,
                show_default=show_default,
                pretty=pretty,
                # as_string=False,
                show_name=show_name,
                filter_for=filter_for)
            if tmp_item:
                tmp_ret.append(tmp_item)
        if as_string:
            return ', '.join(tmp_ret)
        else:
            return tmp_ret

    def _all(self, *flags, inc_sets=True):
        return all(self._get_values(*flags, inc_sets=inc_sets))

    def _any(self, *flags, inc_sets=True):
        return any(self._get_values(*flags, inc_sets=inc_sets))

    def _set(self, flag, value=_UNSET):
        if flag in self:
            value = PREFIX_LOOKUP.get(flag[-1], value)
            flag = flag.strip('+-*^')
            self._flags[flag].set(flag=flag, value=value)
        elif not self._locked:
            self._add(flag, value)
        else:
            raise AttributeError('%s does not exist in %r' % (flag, self))

    def _get(self, flag):
        if flag in self:
            try:
                return self._flags[flag].get(flag)
            except KeyError:
                return bool(self._flag_sets[flag])
        elif not self._locked:
            self._add(flag, False)
            return False
        else:
            raise AttributeError('%s does not exist in %r' % (flag, self))

    def _get_obj(self, flag):
        return self._flag_data[flag]

    @property
    def _build_args(self):
        tmp_args = []
        for f in self._flag_order:
            tmp_args.append(f.build_args)
        return tmp_args

    def __iter__(self):
        for k in self._flags:
            yield k

    def __contains__(self, flag):
        if flag in self._flags:
            return True
        else:
            return flag in self._flag_sets

    def __getattr__(self, flag):
        return self._get(flag)

    def __setattr__(self, key, value):
        if '_FlagHelper__initialised' not in self.__dict__:
            object.__setattr__(self, key, value)
        elif key in self.__dict__:
            super().__setattr__(key, value)
        else:
            self._set(key, value)

    def __getitem__(self, flag):
        return self._get(flag)

    def __setitem__(self, key, value):
        self._set(key, value)

    def __call__(self, *args, **kwargs):
        self._update(*args, **kwargs, locked=False, overwrite_flag=True)

    def __len__(self):
        return len(self._flags)

    def __bool__(self):
        return self._all()

    def __str__(self):
        return self._str(pretty=True)

    def __repr__(self):
        tmp_flags = []
        for f in self._flag_order:
            tmp_flags.append(repr(f))
        tmp_flags = ', '.join(tmp_flags)

        return 'FlagHelper(%s)' % tmp_flags

    def _make_other(self, other):
        if isinstance(other, (list, tuple)):
            return self.__class__(*other)
        elif isinstance(other, dict):
            return self.__class__(**other)
        elif isinstance(other, str):
            return self.__class__(other)
        elif isinstance(other, self.__class__):
            return other
        else:
            raise AttributeError('Could not determine other type ( %r )' % other)

    def __eq__(self, other):
        other = self._make_other(other)

        for item in self._flag_order:
            try:
                if item != other._flag_data[item.name]:
                    return False
            except KeyError:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    """
    def _merge_flags(self, from_object, *flags):
        if not flags:
            flags = from_object._flag_single_names
        for flag in flags:
            if flag in self or not self._locked:
                self._add_flag(flag, from_object[flag])
                try:
                    self._default['_flag_data'][flag] = from_object._default['_flag_data'][flag]
                except KeyError:
                    pass
            else:
                raise AttributeError('Cannot add %s flag, helper locked' % flag)

    def _merge_sets(self, from_object, *set_names):
        if not set_names:
            set_names = from_object._flag_sets.keys()
        for set_name in set_names:
            set_record = from_object._flag_sets[set_name]
            if set_record.named:
                if set_record.name in self._flag_sets:
                    existing_set = self._flag_sets[set_record.named]
                else:
                    existing_set = None
            else:
                if set_record.flags[0] in self._flag_set_flags:
                    existing_set = self._flag_sets[self._flag_set_flags[set_record.flags[0]]]
                else:
                    existing_set = None

            if existing_set is not None:
                if len(set_record.flags) != len(existing_set.flags):
                    raise AttributeError('flag set flags count mismatch')

                for flag in set_record.flags:
                    if flag not in existing_set.flags:
                        raise AttributeError('flag set flag mismatch')

                del self[existing_set.name]
            elif self._locked:
                raise AttributeError('Cannot add flag set %s, manager locked' % set_name)

            if not set_record.named:
                new_set_record = set_record._replace(name=self._get_next_name())
            else:
                new_set_record = copy(set_record)

            self._flag_sets[new_set_record.name] = new_set_record

            fs = new_set_record.name

            for flag in new_set_record.flags:
                if flag in self._flag_single_names:
                    raise AttributeError('flag %s exists outside of set' % flag)

                self._flag_data[flag] = from_object[flag]
                self._flag_set_flags[flag] = fs

                try:
                    self._default['_flag_data'][flag] = from_object._default['_flag_data'][flag]
                except KeyError:
                    pass

            self._flag_set_data[fs] = from_object[fs]
            try:
                self._default['_flag_set_data'][fs] = from_object._default['_flag_set_data'][fs]
            except KeyError:
                pass


    def _merge_objects(self, from_obj, to_obj=None):
        if to_obj is None:
            to_obj = self

        to_obj._merge_flags(from_obj)
        to_obj._merge_sets(from_obj)

    def _move_flag(self, flag, from_obj, to_obj):
        if flag in to_obj._flag_set_flags:
            raise AttributeError('Cannot move to object, flag name in flag set.')
        else:
            to_obj._flag_data[flag] = from_obj._flag_data[flag]
            try:
                to_obj._default['_flag_data'][flag] = from_obj._default['_flag_data'][flag]
            except KeyError:
                pass

    def _move_set(self, flag, from_obj, to_obj):
        if flag in from_obj._flag_sets:
            if flag in to_obj._flag_data:
                raise AttributeError('Merged flag set must not exist as flag in target')
            elif flag in to_obj._flag_sets:
                raise AttributeError('Cannot merge existing flag sets')
            else:
                from_fs = from_obj._flag_sets[flag]
                if from_fs.named:
                    to_obj._flag_sets[from_fs.name] = from_fs
                    to_fs = from_fs
                else:
                    tmp_name = to_obj._get_next_name()
                    to_fs = from_fs._replace(name=tmp_name)
                    to_obj._flag_sets[tmp_name] = to_fs

                for f in to_fs.flags:
                    if f in to_obj._flag_data:
                        raise AttributeError('Merged flag set flag must not exist in target')
                    to_obj._flag_data[f] = from_obj._flag_data[f]
                    to_obj._default['_flag_data'][f] = from_obj._flag_data[f]
                    to_obj._flag_set_flags[f] = to_fs.name

                to_obj._flag_set_data[to_fs.name] = from_obj._flag_set_data[from_fs.name]
                to_obj._default['_flag_set_data'][to_fs.name] = from_obj._flag_set_data[from_fs.name]

        elif flag in from_obj._flag_set_flags:
            raise AttributeError('Cannot move individual flag set flags')

        elif flag in to_obj._flag_set_flags:
            raise AttributeError('Cannot move to object, flag name in flag set.')

        else:
            to_obj._flag_data[flag] = from_obj._flag_data[flag]
            try:
                to_obj._default['_flag_data'][flag] = from_obj._default['_flag_data'][flag]
            except KeyError:
                pass

    """

    def __and__(self, other):
        other = self._make_other(other)
        tmp_ret = self.__class__()
        for flag in self._flag_order:
            if flag.name in other and flag and other[flag.name]:
                tmp_ret._add(other._get_obj(flag.name))
        tmp_ret._locked = self._locked
        return tmp_ret

    def __or__(self, other):
        other = self._make_other(other)
        tmp_ret = self.__class__()

        for flag in self._flag_order:
            if flag:
                tmp_ret._add(self._get_obj(flag.name))

        for flag in other._flag_order:
            if flag.name not in tmp_ret:
                if flag:
                    tmp_ret._add(other._get_obj(flag.name))


        tmp_ret._locked = self._locked
        return tmp_ret

    # def _add_obj(self, from_obj, to_obj):
    #     if isinstance(from_obj, (list, tuple)):
    #         for o in from_obj:
    #             to_obj._set(o)
    #     elif isinstance(from_obj, dict):
    #         for flag, value in from_obj.items():
    #             to_obj._set(flag, value)
    #     elif isinstance(from_obj, to_obj.__class__):
    #         to_obj._merge_sets(from_obj)
    #         to_obj._merge_flags(from_obj)
    #     else:
    #         to_obj._set(from_obj)
    #     return to_obj

    def __add__(self, other):
        tmp_ret = self._copy()
        tmp_ret._add(other, overwrite_flag=True)
        return tmp_ret

    def __iadd__(self, other):
        self._add(other, overwrite_flag=True)
        return self

    # def _sub_obj(self, from_obj, to_obj):
    #     if to_obj._locked:
    #         raise AttributeError('flags cannot be deleted from locked helpers')
    #     if isinstance(from_obj, (list, tuple)):
    #         for o in from_obj:
    #             del to_obj[o]
    #     elif isinstance(from_obj, dict):
    #         for flag, value in from_obj.items():
    #             del to_obj[flag]
    #     elif isinstance(from_obj, to_obj.__class__):
    #         for flag in to_obj._flag_single_names.copy():
    #             del to_obj[flag]
    #         for flag in list(to_obj._flag_sets):
    #             del to_obj[flag]
    #     else:
    #         del to_obj[from_obj]
    #
    #     return to_obj

    def __sub__(self, other):
        tmp_ret = self._copy()
        tmp_ret._locked = False
        tmp_ret._rem(other, raise_on_error=False)
        tmp_ret._locked = self._locked
        return tmp_ret

    def __isub__(self, other):
        self._rem(other)
        return self
