from helpers.general import _UNSET
from copy import deepcopy, copy
from collections import namedtuple


"""
    flag types
    <default_state><field_name><current_state>

    States:
        + = True
        - = False (or no flag)
        * = None
        ^ = No default

    T/F flag default false= 'string_name' or '-string_name'
    T/F flag default true = '+string_name'
    T/F/N flag initial none = '*string_name'

    T/F flag default false, current True = 'string_name+' or '-string_name+'
    T/F flag default true, default false = '+string_name-'
    T/F/N flag initial none, current_ none = '*string_name*'


    TF flag set default all-false = ('flag_1', 'flag_2', 'flag_3')
    TF flag set default flag = ('flag_1', '+flag_2', 'flag_3')
    TF flag set initial None = ('*', 'flag_1', 'flag_2', 'flag_3')
    TF flag set initial None current marked = ('*', 'flag_1', 'flag_2+', 'flag_3')

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
    T/F flag field default False = flag_name
    t/F/N flag initial none = *flag_name

    named flag set default None = ('flag_set_name', ('flag_1', 'flag_2', 'flag_3'))
    named flag set default flag = ('flag_set_name', ('flag_1', 'flag_2', '+flag_3'))

"""
PREFIX_LOOKUP = {'+': True, '-': False, '*': None, '^': _UNSET}


def make_icon(field_data, inc=True, clean=True):
    if not inc:
        return ''
    if clean:
        tmp_tmplate = '(%s)'
    else:
        tmp_tmplate = '%s'

    if field_data is None:
        return tmp_tmplate % '*'
    elif field_data is _UNSET:
        return tmp_tmplate % '^'
    elif field_data:
        return tmp_tmplate % '+'
    else:
        return tmp_tmplate % '-'


def strip_flag(flag_str):
    return flag_str.strip('+-*^')


def strip_value(name, current=_UNSET):
    return name.strip('+-*^'), PREFIX_LOOKUP.get(name[-1], current)


def parse_field(name, current=_UNSET, default=_UNSET):
    name = name.strip('+-*^')
    default = PREFIX_LOOKUP.get(name[0], default)
    value = PREFIX_LOOKUP.get(name[-1], current)
    value = value or default or False
    return dict(name=name.strip('+-*^'), default=default, value=value)


class FlagObj(object):
    flag_set = False

    def __init__(self, name, default=_UNSET, current=_UNSET, new_field=False):

        self.name = name.strip('+-*^')
        self.new_field = new_field
        self.default = PREFIX_LOOKUP.get(name[0], default)
        self.value = PREFIX_LOOKUP.get(name[-1], current)
        self.value = self.value or self.default or False

        if not self.name.isidentifier() or self.name[0] == '_':
            raise AttributeError('Flag name %r is invalid' % self.name)

    def copy(self):
        return self.__class__(self.build_args)
    __copy__ = copy

    def __deepcopy__(self, memo):
        result = self.copy()
        memo[id(self)] = result
        return result

    def set(self, field=None, value=True):
        self.value = bool(value)

    def get(self, field=None):
        return self.value

    def reset(self):
        self.value = self.default

    @property
    def is_set(self):
        return self.value is not None

    @property
    def has_default(self):
        return self.default is not _UNSET

    def __bool__(self):
        return bool(self.value)

    def _str(self, show_current=True, show_default=True,
             pretty=True, filter_for=_UNSET, fields_filter=None):

        tmp_ret = ''
        if fields_filter is None or self.name in fields_filter:
            if filter_for is not _UNSET and self.value in filter_for:
                tmp_ret = '%s%s%s' % (
                    make_icon(self.default, inc=show_default, clean=pretty),
                    self.name,
                    make_icon(self.value, inc=show_current, clean=pretty))

        return tmp_ret

    @property
    def build_args(self):
        return self._str(show_current=True, show_default=True, pretty=False)

    def __str__(self):
        return self._str(pretty=True)

    def __repr__(self):
        tmp_ret = 'SingleFlagObject(%s)' % self.build_args
        return tmp_ret


class FlagSetObj(object):
    flag_set = True

    def __init__(self, *fields, name=None, new_field=False, **kwargs):

        self.new_field = new_field
        self.initial_all_none = False
        self.allow_all_false = True
        self.fields = {}
        self.field_order = []
        self.current_field = _UNSET

        if not fields:
            raise AttributeError('Fields must be specified')

        if name is not None:
            if not name.isidentifier or name[0] == '_':
                raise AttributeError('FlagSet name %r is invalid' % name)
        self.name = name

        if len(fields) == 1:
            if ' ' in fields:
                fields = fields[0].split(' ')
            else:
                raise AttributeError('More than 1 field must be specified')

        if fields[0].strip('*-') == '':
            if '*' in fields[0]:
                self.initial_all_none = True
            if '-' in fields[0]:
                self.allow_all_false = True
            fields = fields[1:]

        self._add_fields(*fields, **kwargs)

    def _add_fields(self, *fields, **field_kwargs):
        for field in fields:
            self._add_field(field)

        for field, value in field_kwargs:
            self._add_fields(field, value)

        if self.current_field is _UNSET and not self.initial_all_none:
            if self.allow_all_false:
                self.current_field = None
            else:
                self.current_field = self.field_order[0]

    def _add_field(self, field, value=_UNSET):
        if self.initial_all_none:
            field = field.rstrip('+-*^')
            field += '*'
        tmp_field = FlagObj(field, current=value)

        self.fields[tmp_field.name] = tmp_field
        self.field_order.append(tmp_field)
        if tmp_field:
            self.current_field = tmp_field
        if tmp_field.default:
            self.default_field = tmp_field

    def copy(self):
        name, tmp_bl = self.build_args
        return self.__class__(*tmp_bl, name=name)
    __copy__ = copy

    def __deepcopy__(self, memo):
        result = self.copy()
        memo[id(self)] = result
        return result

    def set(self, field, value):
        if bool(value):
            if self.current_field is _UNSET:
                for set_field in self.field_order:
                    if set_field.name == field:
                        set_field.set(True)
                        self.current_field = set_field
                    else:
                        set_field.set(False)
            else:
                if self.current_field is not None:
                    self.current_field.set(False)
                self.current_field = self.fields[field]
                self.current_field.set(True)
        else:
            if self.allow_all_false:
                if self.current_field is _UNSET:
                    for set_field in self.field_order:
                        set_field.set(False)
                    self.current_field = None
                else:
                    if self.current_field is not None:
                        self.current_field.set(False)
                        self.current_field = None
            else:
                raise AttributeError('Cannot set item to false unless "allow_all_false" set')

    def get(self, field):
        return self.fields[field].get()

    def reset(self):
        for field in self.field_order:
            field.reset()

    @property
    def is_set(self):
        return self.current_field is not _UNSET

    @property
    def has_default(self):
        return self.default_field is not _UNSET

    def __bool__(self):
        return self.default_field is True

    def _fields_str(self, show_current=True, show_default=True, pretty=True,
                    as_string=True, fields_filter=None, filter_for=_UNSET):

        tmp_ret = []
        for field in self.field_order:
            tmp_item = field._str(fields_filter=fields_filter, show_current=show_current,
                                  show_default=show_default, pretty=pretty, filter_for=filter_for)
            if tmp_item:
                tmp_ret.append(tmp_item)

        if as_string:
            tmp_ret = ', '.join(tmp_ret)

        return tmp_ret

    def _str(self, *fields, show_current=True, show_default=True, pretty=True, show_name=True,
             filter_for=_UNSET, inc_sets=True):
        tmp_ret = []
        if inc_sets:
            if fields and self.name in fields:
                fields = []
            tmp_ret = self._fields_str(
                fields_filter = fields,
                show_current=show_current,
                show_default=show_default,
                pretty=pretty,
                filter_for=filter_for)

        if tmp_ret:
            tmp_ret = ', '.join(tmp_ret)
            if show_name:
                if self.name is not None:
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
        tmp_ret.extend(self._fields_str(show_current=True, show_default=True, pretty=False, as_string=False))

        return self.name, tmp_ret

    def __str__(self):
        return self._str(pretty=True)

    def __repr__(self):
        return 'SingleFlagObject(%r)' % self.build_args

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
    T/F flag field default False = flag_name
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

    def __init__(self, *fields, lock_fields=False, **field_kwargs):

        self._init_fields = False

        # self._field_data = {}
        # self._field_set_data = {}

        # self._field_sets = {}
        # self._field_single_names = []
        # self._field_set_fields = {}

        self._field_data = {}
        self._fields = {}
        self._field_sets = {}
        self._field_singles = {}
        self._field_order = []

        # self._next_counter = 0
        # self._max_counter = 999
        self._locked = False

        if fields or field_kwargs:
            self._update(*fields, **field_kwargs, new_field=True)

        # self._default = dict(
        #     _field_data=self._field_data.copy(),
        #     _field_set_data=self._field_set_data.copy())

        self._locked = lock_fields

        self._init_fields = True
        self.__initialised = True

    def _rem(self, field, raise_on_error=True):
        if self.locked:
            raise AttributeError('Field %s cannot be deleted from locked helper' % field)

        if isinstance(field, str):
            if field not in self:
                if raise_on_error:
                    raise AttributeError('Field %r does not exist' % field)
            else:
                field = self._get_obj(field)
                if field.flag_set:
                    for f in field:
                        del self._fields[f]
                    del self._field_sets[field.name]

                else:
                    del self._field_singles[field.name]
                    del self._fields[field.name]

                del self._field_data[field.name]
                self._field_order.remove(field)

        elif isinstance(field, (list, tuple)):
            for f in field:
                self._rem(f)
        elif isinstance(field, dict):
            for f, in field:
                self._rem(f)
        elif isinstance(field, self.__class__):
            for f in field._field_order:
                self._rem(f.name)
        elif isinstance(field, (FlagObj, FlagSetObj)):
            self._rem(field.name)
        else:
            self._rem(str(field))
    __delitem__ = _rem

    # @staticmethod
    # def _validate_addr(flag):
    #     if flag.isidentifier() and flag[0] != '_':
    #         return True
    #     raise AttributeError('Flag name %r is invalid' % flag)
    #
    # def _validate_add_addr(self, flag):
    #     if flag in self._field_data:
    #         return True
    #     elif flag.isidentifier() and flag[0] != '_':
    #         if self._locked:
    #             raise AttributeError('Flag not present and fields locked')
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

    def _update(self, *fields, new_field=False, **field_kwargs):
        for a in fields:
            self._add(a, new_field=new_field)
        for field, value in field_kwargs.items():
            self._add(field, value, new_field=new_field)

    def _add(self, field_name, *values, new_field=True, overwrite_field=False):
        if isinstance(field_name, str):
            if len(values) == 0:
                field = FlagObj(field_name, new_field=new_field)
            elif len(values) == 1 and isinstance(values[0], str):
                values = values[0].split(' ')
                field = FlagSetObj(field_name, *values, new_field=new_field)
            elif len(values) > 1:
                field = FlagSetObj(field_name, *values, new_field=new_field)
            else:
                field = FlagObj(field_name, current=bool(values), new_field=new_field)
        elif isinstance(field_name, (list, tuple)):
            if len(field_name) == 2 and isinstance(field_name[1], (list, tuple)):
                field = FlagSetObj(field_name[0], *field_name[1], new_field=new_field)
            else:
                field = FlagSetObj(None, *field_name, new_field=new_field)
        elif isinstance(field_name, self.__class__):
            for f in field_name._field_order:
                self._add(f, new_field=new_field, overwrite_field=overwrite_field)
                return
        elif isinstance(field_name, (FlagSetObj, FlagObj)):
            field = field_name
            field.new_field = new_field
        else:
            raise AttributeError('Unable to determine field and value from %r and %r' % (field_name, values))

        if field.name in self:
            if not overwrite_field:
                raise AttributeError('Field %s already exists in %r' % (field.name, self))
            self._field_data[field.name].update(field)

        else:
            if field.name is not None:
                self._field_data[field.name] = field

            self._field_order.append(field)

            if field.flag_set:
                self._field_sets[field.name] = field
                for f in field.fields:
                    self._fields[f.name] = field
            else:
                self._field_singles[field.name] = field
                self._fields[field.name] = field

    def _reset(self, rem_new=False):
        for f in self._field_order:
            if f.new_field and rem_new:
                self._del(f.name)
            else:
                f.reset()

    def _copy(self):
        tmp_ret = self.__class__(*self._build_args)
        return tmp_ret
    __copy__ = _copy

    def _copy_default(self):
        tmp_ret = self._copy()
        tmp_ret._reset()
        return tmp_ret

    # def _get_set(self, set_name):
    #     return self._field_sets[set_name]

    def _get_dict(self, *fields, inc_sets=True, flat=False, filter_for=_UNSET):
        tmp_ret = {}

        for field in self._field_order:
            tmp_ret.update(field.get_dict(*fields, inc_sets=inc_sets, flat=flat, filter_for=filter_for))

        return tmp_ret

    def _get_values(self, *fields, inc_sets=True):
        tmp_ret = []
        if not fields:
            if inc_sets:
                for f in self._field_data:
                    tmp_ret.append(bool(f))
            else:
                for f in self._field_singles:
                    tmp_ret.append(bool(f))
        else:
            for f in fields:
                tmp_ret.append(bool(self._get(f)))
        return tmp_ret

    # def _get_field_str(self, field, with_icon=False):
    #     if with_icon:
    #         if self._field_data[field] is None:
    #             return '(*)%s' % field
    #         elif self._field_data[field]:
    #             return '(+)%s' % field
    #         else:
    #             return '(-)%s' % field
    #     else:
    #         return field

    def _get_str(self, *fields, inc_sets=True, flat=False, inc_current=True, inc_default=True,
                 pretty=False, as_str=True, filter_for=_UNSET):
        tmp_ret = []
        for field in self._field_order:
            tmp_item = field._str(
                *fields,
                inc_sets=inc_sets,
                flat=flat,
                inc_current=inc_current,
                inc_default=inc_default,
                pretty=pretty,
                as_str=False,
                filter_for=filter_for)
            if tmp_item:
                tmp_ret.append(tmp_item)
        if as_str:
            return ', '.join(tmp_ret)
        else:
            return tmp_ret

    def _all(self, *fields, inc_sets=True):
        return all(self._get_values(*fields, inc_sets=inc_sets))

    def _any(self, *fields, inc_sets=True):
        return any(self._get_values(*fields, inc_sets=inc_sets))

    def _set(self, field, value=_UNSET):
        if field in self:
            value = PREFIX_LOOKUP.get(field[-1], value)
            field = field.strip('+-*^')
            self._fields[field].set(field=field, value=value)
        elif not self._locked:
            self._add(field, value)
        else:
            raise AttributeError('%s does not exist in %r' % (field, self))

    def _get(self, field):
        if field in self:
            return self._fields[field].get(field)
        elif not self._locked:
            self._add(field, False)
            return False
        else:
            raise AttributeError('%s does not exist in %r' % (field, self))

    def _get_obj(self, field):
        return self._field_data[field]

    @property
    def _build_args(self):
        tmp_args = []
        for f in self._field_order:
            tmp_args.append(f.build_args)
        return tmp_args

    def __iter__(self):
        for k in self._fields:
            yield k

    def __contains__(self, field):
        return field in self._fields

    def __getattr__(self, field):
        return self._get(field)

    def __setattr__(self, key, value):
        if '_FlagHelper__initialised' not in self.__dict__:
            object.__setattr__(self, key, value)
        elif key in self.__dict__:
            super().__setattr__(key, value)
        else:
            self._set(key, value)

    def __getitem__(self, field):
        return self._get(field)

    def __setitem__(self, key, value):
        self._set(key, value)

    def __call__(self, *args, **kwargs):
        for arg in args:
            self._set(arg)
        for field, value in kwargs.items():
            self._set(field, value)

    def __len__(self):
        return len(self._fields)

    def __bool__(self):
        return self._all()

    def __str__(self):
        return self._get_str(pretty=True)

    def __repr__(self):
        return 'FlagHelper(%s)' % self.__str__()

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
            raise AttributeError('Cound not determine other type ( %r )' % other)

    def __eq__(self, other):
        other = self._make_other(other)

        for key, item in self._field_data.items():
            try:
                if item != other._field_data[key]:
                    return False
            except KeyError:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    """
    def _merge_fields(self, from_object, *fields):
        if not fields:
            fields = from_object._field_single_names
        for field in fields:
            if field in self or not self._locked:
                self._add_field(field, from_object[field])
                try:
                    self._default['_field_data'][field] = from_object._default['_field_data'][field]
                except KeyError:
                    pass
            else:
                raise AttributeError('Cannot add %s field, helper locked' % field)

    def _merge_sets(self, from_object, *set_names):
        if not set_names:
            set_names = from_object._field_sets.keys()
        for set_name in set_names:
            set_record = from_object._field_sets[set_name]
            if set_record.named:
                if set_record.name in self._field_sets:
                    existing_set = self._field_sets[set_record.named]
                else:
                    existing_set = None
            else:
                if set_record.fields[0] in self._field_set_fields:
                    existing_set = self._field_sets[self._field_set_fields[set_record.fields[0]]]
                else:
                    existing_set = None

            if existing_set is not None:
                if len(set_record.fields) != len(existing_set.fields):
                    raise AttributeError('Field set fields count mismatch')

                for field in set_record.fields:
                    if field not in existing_set.fields:
                        raise AttributeError('Field set field mismatch')

                del self[existing_set.name]
            elif self._locked:
                raise AttributeError('Cannot add field set %s, manager locked' % set_name)

            if not set_record.named:
                new_set_record = set_record._replace(name=self._get_next_name())
            else:
                new_set_record = copy(set_record)

            self._field_sets[new_set_record.name] = new_set_record

            fs = new_set_record.name

            for field in new_set_record.fields:
                if field in self._field_single_names:
                    raise AttributeError('Field %s exists outside of set' % field)

                self._field_data[field] = from_object[field]
                self._field_set_fields[field] = fs

                try:
                    self._default['_field_data'][field] = from_object._default['_field_data'][field]
                except KeyError:
                    pass

            self._field_set_data[fs] = from_object[fs]
            try:
                self._default['_field_set_data'][fs] = from_object._default['_field_set_data'][fs]
            except KeyError:
                pass


    def _merge_objects(self, from_obj, to_obj=None):
        if to_obj is None:
            to_obj = self

        to_obj._merge_fields(from_obj)
        to_obj._merge_sets(from_obj)

    def _move_field(self, field, from_obj, to_obj):
        if field in to_obj._field_set_fields:
            raise AttributeError('Cannot move to object, field name in field set.')
        else:
            to_obj._field_data[field] = from_obj._field_data[field]
            try:
                to_obj._default['_field_data'][field] = from_obj._default['_field_data'][field]
            except KeyError:
                pass

    def _move_set(self, field, from_obj, to_obj):
        if field in from_obj._field_sets:
            if field in to_obj._field_data:
                raise AttributeError('Merged flag set must not exist as field in target')
            elif field in to_obj._field_sets:
                raise AttributeError('Cannot merge existing flag sets')
            else:
                from_fs = from_obj._field_sets[field]
                if from_fs.named:
                    to_obj._field_sets[from_fs.name] = from_fs
                    to_fs = from_fs
                else:
                    tmp_name = to_obj._get_next_name()
                    to_fs = from_fs._replace(name=tmp_name)
                    to_obj._field_sets[tmp_name] = to_fs

                for f in to_fs.fields:
                    if f in to_obj._field_data:
                        raise AttributeError('Merged flag set field must not exist in target')
                    to_obj._field_data[f] = from_obj._field_data[f]
                    to_obj._default['_field_data'][f] = from_obj._field_data[f]
                    to_obj._field_set_fields[f] = to_fs.name

                to_obj._field_set_data[to_fs.name] = from_obj._field_set_data[from_fs.name]
                to_obj._default['_field_set_data'][to_fs.name] = from_obj._field_set_data[from_fs.name]

        elif field in from_obj._field_set_fields:
            raise AttributeError('Cannot move individual field set fields')

        elif field in to_obj._field_set_fields:
            raise AttributeError('Cannot move to object, field name in field set.')

        else:
            to_obj._field_data[field] = from_obj._field_data[field]
            try:
                to_obj._default['_field_data'][field] = from_obj._default['_field_data'][field]
            except KeyError:
                pass

    """

    def __and__(self, other):
        other = self._make_other(other)
        tmp_ret = self.__class__()
        for field in self._field_order:
            if field and other[field.name]:
                tmp_ret._add(other.get_obj(field.name))
        tmp_ret._locked = self._locked
        return tmp_ret

    def __or__(self, other):
        other = self._make_other(other)
        tmp_ret = self.__class__()

        for field in self._field_order:
            if field:
                tmp_ret.add(self._get_obj(field.name))
            elif other[field.name]:
                tmp_ret.add(other._get_obj(field.name))

        tmp_ret._locked = self._locked
        return tmp_ret



    # def _add_obj(self, from_obj, to_obj):
    #     if isinstance(from_obj, (list, tuple)):
    #         for o in from_obj:
    #             to_obj._set(o)
    #     elif isinstance(from_obj, dict):
    #         for field, value in from_obj.items():
    #             to_obj._set(field, value)
    #     elif isinstance(from_obj, to_obj.__class__):
    #         to_obj._merge_sets(from_obj)
    #         to_obj._merge_fields(from_obj)
    #     else:
    #         to_obj._set(from_obj)
    #     return to_obj

    def __add__(self, other):
        tmp_ret = self._copy()
        tmp_ret._add(other)
        return tmp_ret

    def __iadd__(self, other):
        self._add(other)
        return self

    # def _sub_obj(self, from_obj, to_obj):
    #     if to_obj._locked:
    #         raise AttributeError('Fields cannot be deleted from locked helpers')
    #     if isinstance(from_obj, (list, tuple)):
    #         for o in from_obj:
    #             del to_obj[o]
    #     elif isinstance(from_obj, dict):
    #         for field, value in from_obj.items():
    #             del to_obj[field]
    #     elif isinstance(from_obj, to_obj.__class__):
    #         for field in to_obj._field_single_names.copy():
    #             del to_obj[field]
    #         for field in list(to_obj._field_sets):
    #             del to_obj[field]
    #     else:
    #         del to_obj[from_obj]
    #
    #     return to_obj

    def __sub__(self, other):
        tmp_ret = self._copy()
        tmp_ret._rem(other)
        return tmp_ret

    def __isub__(self, other):
        self._rem(other)
        return self



'''
class OldFlagHelper(object):
    _data = None
    """
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

    def __init__(self, *args, **kwargs):
        self._data = {}
        self._init_fields = False
        for arg in args:
            self._add(arg)
        if kwargs:
            self._add(kwargs)
        self._default = self._data.copy()
        self._init_fields = True
        self.__initialised = True

    def _clear(self):
        self._data.clear()

    def _str_conv(self, flag_str):
        if flag_str[0] in '+-':
            return flag_str[1:], flag_str[0] == '+'
        else:
            return flag_str, True

    def _add(self, data_in):
        if isinstance(data_in, str):
            tmp_key, tmp_value = self._str_conv(data_in)
            self[tmp_key] = tmp_value

        elif isinstance(data_in, (list, tuple)):
            for d in data_in:
                self._add(d)

        elif isinstance(data_in, dict):
            self._update(data_in)

        elif isinstance(data_in, (FlagHelper, LockedFlagHelper)):
            self._update(data_in._data.copy())

        return self

    def _del(self, data_in):
        tmp_ret = {}
        if isinstance(data_in, str):
            tmp_key, tmp_value = self._str_conv(data_in)
            self._set_false(tmp_key)

        elif isinstance(data_in, (list, tuple)):
            for d in data_in:
                tmp_key, tmp_value = self._str_conv(d)
                self._set_false(tmp_key)

        elif isinstance(data_in, dict):
            for k in data_in.keys():
                self._set_false(k)

        elif isinstance(data_in, (FlagHelper, LockedFlagHelper)):
            for k in data_in:
                self._set_false(k)

        return self

    def _reset(self, set_to=False, set_to_default=False):
        if set_to_default:
            self._data.clear()
            self._data.update(self._default.copy())
        else:
            self._set_all(set_to)

    def _set_all(self, set_to=False):
        tmp_list = list(self._data.keys())
        if set_to:
            self._add(tmp_list)
        else:
            self._del(tmp_list)

    def _set_true(self, field):
        if field == '*':
            self._set_all(True)
        else:
            self._validate_addr(field)
            self._data[field] = True

    def _set_false(self, field):
        if field == '*':
            self._set_all(False)
        else:
            try:
                del self._data[field]
            except KeyError:
                pass

    def _update(self, dict_in):
        for key, value in dict_in.items():
            self[key] = value

    def _validate_addr(self, flag):
        if flag.isidentifier():
            if flag[0] != '_':
                return True
        raise AttributeError('Flag name %r is invalid' % flag)

    def _get(self):
        return list(self._data.keys())

    def _get_dict(self):
        return self._data.copy()

    def _and(self, other):
        tmp_ret = self._copy(set_to=False)

        if not isinstance(other, (FlagHelper, LockedFlagHelper)):
            other = FlagHelper(other)

        for key, value in self._data.items():
            if value and key in other._data and other._data[key]:
                tmp_ret += key

        return tmp_ret

    def _or(self, other):
        tmp_ret = self._copy(set_to=False)
        if not isinstance(other, (FlagHelper, LockedFlagHelper)):
            other = FlagHelper(other)

        for key, value in self._data.items():
            if value or (key in other._data and other._data[key]):
                tmp_ret += key

        for key, value in other._data.items():
            if value or (key in self._data and self._data[key]):
                try:
                    tmp_ret += key
                except KeyError:
                    pass

        return tmp_ret

    def _copy(self, set_to_default=False, set_to=None):
        if set_to_default:
            return self.__class__(**self._default)
        else:
            tmp_ret = self.__class__(**self._default)
            if set_to is None:
                tmp_ret._update(self._data)
            else:
                tmp_ret._set_all(set_to)
            return tmp_ret

    __copy__ = _copy

    def __iter__(self):
        for k, i in self._data.items():
            yield k

    def __contains__(self, item):
        return item in self._data and self._data[item]

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        if '_FlagHelper__initialised' not in self.__dict__:
            object.__setattr__(self, key, value)
        elif key in self.__dict__:
            super(self.__class__).__setattr__(key, value)
        else:
            self[key] = bool(value)

    def __getitem__(self, item):
        try:
            return self._data[item]
        except KeyError:
            return False

    def __setitem__(self, key, value):
        if bool(value):
            self._set_true(key)
        else:
            self._set_false(key)

    def __call__(self, *args, **kwargs):
        self._add(args)
        if kwargs:
            self._add(kwargs)
        return self._get()

    def __len__(self):
        return len(self._data)

    def __bool__(self):
        return bool(self._data)

    def __iadd__(self, other):
        self._add(other)
        return self

    def __isub__(self, other):
        self._del(other)
        return self

    def _str(self, with_icons=False):
        tmp_list = list(self._data.keys())
        tmp_list.sort()

        if with_icons:
            for i in range(len(tmp_list)):
                if self._data[tmp_list[i]]:
                    tmp_list[i] = '(+)' + tmp_list[i]
                else:
                    tmp_list[i] = '(-)' + tmp_list[i]

        return ', '.join(tmp_list)

    def __str__(self):
        return self._str()

    def __repr__(self):
        return 'FlagHelper(%s)' % self.__str__()

    def __eq__(self, other):
        if not isinstance(other, (FlagHelper, LockedFlagHelper)):
            other = FlagHelper(other)

        for key, item in self._data.items():
            try:
                if item != other[key]:
                    return False
            except KeyError:
                return False
        return True

    def __ne__(self, other):
        return not self == other


class OldLockedFlagHelper(FlagHelper):
    """
    flag types
    T/F flag default false= 'string_name'
    T/F flag default true = '+string_name'
    T/F/N flag default none = '*string_name'
    T/F/N flag default true = '*+string_name'
    T/F/N flag default false = '*-string_name'

    flag set default None = ('flag_1', 'flag_2', 'flag_3')
    flag set default flag = ('flag_1', '+flag_2', 'flag_3')

    named flag set default None = ('flag_set_name', ('flag_1', 'flag_2', 'flag_3'))
    named flag set default flag = ('flag_set_name', ('flag_1', 'flag_2', '+flag_3'))

    LockedFlagHelper((flag_set_name, (
    """

    def __init__(self, *args, **kwargs):
        super(LockedFlagHelper, self).__init__(*args, **kwargs)
        self.__initialised = True

    def _clear(self):
        """
        This will return all fields to their default state
        """
        self._data.clear()
        self._data.update(self._default)

    def _set_false(self, field):
        self._validate_addr(field)
        self._data[field] = False

    def _validate_addr(self, flag):
        if self._init_fields:
            if flag in self._data:
                return True
            else:
                raise KeyError('Invalid flag name %r: valid ones are %r' % (flag, self._str(with_icons=False)))
        else:
            if flag.isidentifier():
                if flag[0] != '_':
                    return True
            raise AttributeError('Flag name %r is invalid' % flag)

    def _get(self, filter_for=None):
        if filter_for is not None:
            tmp_ret = []
            for key, value in self._data.items():
                if value == filter_for:
                    tmp_ret.append(key)
            return tmp_ret
        else:
            return list(self._data.keys())

    def _get_dict(self, filter_for=None):
        if filter_for is not None:
            tmp_ret = {}
            for key, value in self._data.items():
                if value == filter_for:
                    tmp_ret[key] = value
            return tmp_ret
        else:
            return self._data.copy()

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError('Invalid flag name %s: valid ones are %s' % (item, str(self)))

    def __setattr__(self, key, value):
        if '_LockedFlagHelper__initialised' not in self.__dict__:
            object.__setattr__(self, key, value)
        elif key in self.__dict__:
            super(LockedFlagHelper).__setattr__(key, value)
        else:
            self[key] = bool(value)

    def __getitem__(self, item):
        return self._data[item]

    def __call__(self, *args, **kwargs):
        self._add(args)
        if kwargs:
            self._add(kwargs)
        return self._get(filter_for=True)

    def __bool__(self):
        return all(self._data.values())

    def __str__(self):
        return self._str(with_icons=True)

    def __repr__(self):
        return 'LockedFlagHelper(%s)' % self.__str__()

'''