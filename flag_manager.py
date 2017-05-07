
class FlagManager(object):
    _data = None
    """
    Manager to handle easier setting of boolean type flags.

    locked:

        FM = FlagManager()

        FM = FlagManager()

        FM = FlagManager('+flag_1_name', '-flag_2_name', 'flag_3_name')

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
        FlagManager(flag1=False, flag2=True, flag3=false)

    open

        FM = FlagManager()

        FM = FlagManager(
            add_on_plus=True,
            allow_us_start=False,
            case_sensitive=False,
            fix_names=False)

        FM = FlagManager('+flag_1_name', '-flag_2_name', 'flag_3_name')

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
        FlagManager(flag1, flag2, flag3)


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

        elif isinstance(data_in, (FlagManager, LockedFlagManager)):
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

        elif isinstance(data_in, (FlagManager, LockedFlagManager)):
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

        if not isinstance(other, (FlagManager, LockedFlagManager)):
            other = FlagManager(other)

        for key, value in self._data.items():
            if value and key in other._data and other._data[key]:
                tmp_ret += key

        return tmp_ret

    def _or(self, other):
        tmp_ret = self._copy(set_to=False)
        if not isinstance(other, (FlagManager, LockedFlagManager)):
            other = FlagManager(other)

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
        if '_FlagManager__initialised' not in self.__dict__:
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
        return 'FlagManager(%s)' % self.__str__()

    def __eq__(self, other):
        if not isinstance(other, (FlagManager, LockedFlagManager)):
            other = FlagManager(other)

        for key, item in self._data.items():
            try:
                if item != other[key]:
                    return False
            except KeyError:
                return False
        return True

    def __ne__(self, other):
        return not self == other


class LockedFlagManager(FlagManager):
    def __init__(self, *args, **kwargs):
        super(LockedFlagManager, self).__init__(*args, **kwargs)
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
        if '_LockedFlagManager__initialised' not in self.__dict__:
            object.__setattr__(self, key, value)
        elif key in self.__dict__:
            super(LockedFlagManager).__setattr__(key, value)
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
        return 'LockedFlagManager(%s)' % self.__str__()
