from helpers.general import make_list, _UNSET
from copy import copy, deepcopy

__all__ = ['KeyObj', 'WildCardMergeDict']


'''
class MsgKeyObj(KeyObj):
    """
    extra kwargs:
        seg_kwargs
        msg_kwargs,
        default_segment,

    """
    @property
    def msg_key(self):
        return self.key2

    @property
    def seg_key(self):
        return self.key1

    @property
    def has_msg_key(self):
        return self.has_key1

    @property
    def has_seg_key(self):
        return self.has_key2

    @property
    def full_msg_kwargs(self):
        tmp_ret = {'key': self.msg_key}
        tmp_ret.update(self.msg_kwargs)
        return tmp_ret

    @property
    def full_seg_kwargs(self):
        tmp_ret = {'key': self.seg_key}
        tmp_ret.update(self.seg_kwargs)
        return tmp_ret
'''

class KeyObj(object):
    _key1_default = '*'
    _key2_default = '*'
    _key_field = 'key'
    _key1_function = 'lower'
    _key2_function = 'upper'

    def __init__(self, *keys, **kwargs):
        self.key_data = {}
        if kwargs:
            for attr, value in kwargs.items():
                if hasattr(self, attr):
                    setattr(self, attr, value)
        self.key1 = self._key1_default
        self.key2 = self._key2_default
        if self._key1_function is not None:
            self._key1_function = getattr(str, self._key1_function)
        if self._key2_function is not None:
            self._key2_function = getattr(str, self._key2_function)
        self.update(*keys)

    def _set_key1(self, key1):
        if self._iskey(key1):
            key1 = self._key1_function(key1)
            if not self.has_key1:
                if self._key1_function:
                    self.key1 = key1
                else:
                    self.key1 = key1
            elif self.key1 != key1:
                raise AttributeError('Unable to update, mis-matched keys: %s -> %s' % (self.key1, key1))
        elif not self.has_key1 and self._key1_default:
            self.key1 = self._key1_function(self._key1_default)

    def _set_key2(self, key2):
        if self._iskey(key2):
            key2 = self._key2_function(key2)
            if not self.has_key2:
                if self._key2_function:
                    self.key2 = key2
                else:
                    self.key2 = key2
            elif self.key2 != key2:
                raise AttributeError('Unable to update, mis-matched keys: %s -> %s' % (self.key2, key2))
        elif not self.has_key2 and self._key2_default:
            self.key2 = self._key2_function(self._key2_default)

    @staticmethod
    def _iskey(key):
        return key and key != '*'

    def update(self, *keys):
        if keys:
            found_key = False
            for key in keys:
                try:
                    key1, key2 = key.split('.')
                except ValueError:
                    raise AttributeError('Unable to parse key: %r (no "." found)' % key)
                except AttributeError:
                    if key is None:
                        continue
                    elif isinstance(key, self.__class__):
                        self._set_key1(key.key1)
                        self._set_key2(key.key2)
                        self.key_data.update(key.key_data)
                        found_key = True
                    elif isinstance(key, dict):
                        key = deepcopy(key)
                        tmp_key = key.pop(self._key_field, None)
                        if tmp_key:
                            found_key = True
                            self.update(tmp_key)
                        self.key_data.update(key)
                    elif isinstance(key, (list, tuple)):
                        self.update(*key)
                        found_key = True
                    else:
                        raise AttributeError('Unable to parse key: ' + repr(key))
                else:
                    self._set_key1(key1)
                    self._set_key2(key2)
                    found_key = True

            if not found_key:
                raise AttributeError('Unable to find key')

    @classmethod
    def make_key(cls, *keys, **kwargs):
        if keys and isinstance(keys[0], cls):
            return keys[0]
        return cls(*keys, **kwargs)

    @property
    def has_key1(self):
        return self.key1 != '*'

    @property
    def has_key2(self):
        return self.key2 != '*'

    @property
    def is_exact(self):
        return self.has_key1 and self.has_key2

    @property
    def is_any(self):
        return self.key1 == '*' and self.key2 == '*'

    @property
    def dot_star(self):
        return self.key1 + '.*'

    @property
    def star_dot(self):
        return '*.' + self.key2

    @property
    def as_dict(self):
        tmp_dict = dict(**self.key_data)
        tmp_dict[self._key_field] = str(self)
        return tmp_dict

    def keys(self, inc_all=True, inc_star=True):
        if inc_all:
            yield '*.*'
        if inc_star and self.has_key1:
            yield self.key1 + '.*'
        if inc_star and self.has_key2:
            yield '*.' + self.key2
        if self.is_exact:
            yield '%s.%s' % (self.key1, self.key2)

    def copy(self):
        return self.__class__(self.as_dict)
    __copy__ = copy

    def __bool__(self):
        return not self.is_any

    def __iadd__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('Cannot combine object, is not KeyObj class: %r' % other)
        self.update(other)
        return self

    def __add__(self, other):
        tmp_item = self.__copy__()
        tmp_item.update(other)
        return tmp_item

    def _compare_eq_(self, other):
        other = self.make_key(other)
        for field in ['key1', 'key2']:
            self_field = getattr(self, field).lower()
            other_field = getattr(other, field).lower()
            if self_field == '*' or other_field == '*':
                continue
            if self_field > other_field:
                return 1
            elif self_field < other_field:
                return -1
        return 0

    def _compare_(self, other):
        other = self.make_key(other)
        for field in ['key1', 'key2']:
            self_field = getattr(self, field).lower()
            other_field = getattr(other, field).lower()
            if self_field == '*' and other_field == '*':
                continue
            if self_field > other_field or other_field == '*':
                return 1
            elif self_field < other_field or self_field == '*':
                return -1
        return 0

    def __eq__(self, other):
        return self._compare_eq_(other) == 0

    def __ne__(self, other):
        return self._compare_eq_(other) != 0

    def __lt__(self, other):
        return self._compare_(other) == -1

    def __le__(self, other):
        return self._compare_(other) < 1

    def __gt__(self, other):
        return self._compare_(other) == 1

    def __ge__(self, other):
        return self._compare_(other) > -1

    def __str__(self):
        return '%s.%s' % (self.key1, self.key2)

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return 'KeyObj(' + self.__str__() + ')'


# def make_key(*args, key_field='key'):
#     if args and isinstance(args[0], KeyObj):
#         return args[0]
#     return KeyObj(*args, key_field=key_field)


class WildMergeDictFieldHandler(object):
    copy_flag = False
    deepcopy_flag = False
    locked_flag = False
    key_flag = False

    def __init__(self, field_name, add_function, merge_function, *flags, **kwargs):
        self.kwargs = kwargs
        self.name = field_name
        self._add = add_function
        self._merge = merge_function
        for flag in flags:
            flag = flag + "_flag"
            if hasattr(self, flag):
                setattr(self, flag, True)

    def add(self, key, to_dict, value):
        if self.copy_flag:
            value = copy(value)
        if self.deepcopy_flag:
            value = deepcopy(value)

        self._add(key=key, to_dict=to_dict, field_name=self.name, value=value, **self.kwargs)

    def merge(self, key, from_dict, to_dict, tmp_dict):
        if self.name in to_dict and self.locked_flag:
            raise AttributeError('field %s already exists in dict %r' % (self.name, to_dict))
        self._merge(key=key, from_dict=from_dict, field_name=self.name, to_dict=to_dict, tmp_dict=tmp_dict, **self.kwargs)

    def __repr__(self):
        return 'Field Definition: ' + self.name


class WildCardMergeDict(object):
    COPY_FLAG = 'copy'
    DEEPCOPY_FLAG = 'deepcopy'
    LOCKED_FLAG = 'locked'
    KEY_FLAG = 'key'
    UPPER_FLAG = 'upper'
    LOWER_FLAG = 'lower'

    """
    fields = (
        ('field_name', dict(
            add=add_function,  (function reference or string name of function)
            merge=merge_function,   (function reference or string name of function)
            default=default_value,   (if no default value, this will not return anything unless filled in.)
            flags=[*flags],
            kwargs={})), 
        ('field_name', default_value),  (no flags and uses default string handlers)
        'field_name',            
        ...),        
        
        if only one item (after the field name) is present, and it is empty if dict, it is assumed to be the default)
        
        
    flags:
        'copy'    # will copy content before adding to record
        'deepcopy'  # will deepcopy content before adding to record
        'locked'    # will raise error if a field is updated in a merge
        'upper'
        'lower'

    if default is list or dict, default functions will update/append data.    

    add_function(key, record_dict, field_name, value, **kwargs)
        updates record dict

    merge_function(key, new_record_dict, field_name, old_rec_dict, **kwargs)
        updates new record dict       
    """

    fields = None
    fields_locked = True
    return_on = 'partial'    # 'full'|'partial'|'any'

    def __init__(self, *args):
        if self.fields is None:
            raise NotImplementedError('Fields property must not be None')
        self._key_field = 'key'
        self._data = {}
        self._cache = {}
        self._field_order = []
        self._update_handlers()
        self.update(*args)
        if '*.*' in self._data:
            args = args + (self._data['*.*'],)
        self._defaults = args

    def _key_handler(self, *args, **kwargs):
        return KeyObj.make_key(*args, key_field=self._key_field, **kwargs)

    def _update_handlers(self):
        tmp_fields = {}
        tmp_default = {}
        added_key = False
        for field in self.fields:
            if isinstance(field, str):
                tmp_def = WildMergeDictFieldHandler(field, self._add_default, self._merge_default)
                tmp_fields[field] = tmp_def
                self._field_order.append(field)

            elif isinstance(field, (list, tuple)):
                field_name = field[0]
                field_value = field[1]
                self._field_order.append(field_name)
                tmp_add = None
                tmp_mer = None
                tmp_flags = []
                tmp_kwargs = {}
                if isinstance(field_value, dict) and field_value:
                    tmp_add = field_value.get('add', None)
                    tmp_mer = field_value.get('merge', None)
                    tmp_flags = field_value.get('flags', [])
                    tmp_def = field_value.get('default', _UNSET)
                    tmp_kwargs = field_value.get('kwargs', {})
                else:
                    tmp_def = field_value

                if tmp_def is not _UNSET:
                    tmp_default[field_name] = deepcopy(tmp_def)

                if 'key' in tmp_flags:
                    added_key = True
                    self._key_field = field_name
                    if tmp_add is None:
                        tmp_add = self._add_key
                    if tmp_mer is None:
                        tmp_mer = self._merge_key

                if tmp_add is None:
                    if tmp_def is not _UNSET:
                        if isinstance(tmp_def, (list, tuple)):
                            tmp_add = self._add_default
                        elif isinstance(tmp_def, dict):
                            tmp_add = self._add_dict
                        else:
                            tmp_add = self._add_default
                    else:
                        tmp_add = self._add_default
                elif isinstance(tmp_add, str):
                    tmp_add = getattr(self, tmp_add)

                if tmp_mer is None:
                    if tmp_def is not _UNSET:
                        if isinstance(tmp_def, (list, tuple)):
                            tmp_mer = self._merge_list
                        elif isinstance(tmp_def, dict):
                            tmp_mer = self._merge_dict
                        else:
                            tmp_mer = self._merge_default
                    else:
                        tmp_mer = self._merge_default
                elif isinstance(tmp_mer, str):
                    tmp_mer = getattr(self, tmp_mer)

                tmp_item = WildMergeDictFieldHandler(field_name, tmp_add, tmp_mer, *tmp_flags, **tmp_kwargs)
                tmp_fields[field_name] = tmp_item

            else:
                raise AttributeError('Invalid Field Definition: %r' % field)

        if not added_key:
            self._field_order.append(self._key_field)
            tmp_item = WildMergeDictFieldHandler(self._key_field, self._add_key, self._merge_key, 'key')
            tmp_fields[self._key_field] = tmp_item

        self._fields = tmp_fields

        tmp_default[self._key_field] = self._key_handler('*.*')
        self._data['*.*'] = tmp_default

    def _add_default(self, key, to_dict, field_name, value, **kwargs):
        to_dict[field_name] = value

    def _merge_default(self, key, from_dict, field_name, to_dict, **kwargs):
        to_dict[field_name] = from_dict[field_name]

    def _add_list(self, key, to_dict, field_name, value, **kwargs):
        if field_name not in to_dict:
            to_dict[field_name] = []
        to_dict[field_name].extend(make_list(value))

    def _merge_list(self, key, from_dict, field_name, to_dict, **kwargs):
        if field_name not in to_dict:
            to_dict[field_name] = []
        to_dict[field_name].extend(from_dict[field_name])

    def _merge_set_unique(self, key, from_dict, field_name, to_dict, **kwargs):
        if to_dict.get(field_name, None) and from_dict.get(field_name, None):
            to_dict[field_name] = set().union(to_dict[field_name], from_dict[field_name])

        elif field_name in from_dict:
            to_dict[field_name] = from_dict[field_name]

    def _add_dict(self, key, to_dict, field_name, value, **kwargs):
        if field_name not in to_dict:
            to_dict[field_name] = value
        else:
            to_dict[field_name].update(value)

    def _merge_dict(self, key, from_dict, field_name, to_dict, **kwargs):
        if field_name not in to_dict:
            to_dict[field_name] = from_dict[field_name]
        else:
            to_dict[field_name].update(from_dict[field_name])

    def _merge_combine_string(self, key, from_dict, field_name, to_dict, sep='\n', rev_order=False, **kwargs):
        if to_dict.get(field_name, None) and from_dict.get(field_name, None):
            if rev_order:
                to_dict[field_name] = to_dict[field_name] + sep + from_dict[field_name]
            else:
                to_dict[field_name] = from_dict[field_name] + sep + to_dict[field_name]
        elif field_name in from_dict:
            to_dict[field_name] = from_dict[field_name]

    def _merge_combine_string_by_key(self, key, from_dict, field_name, to_dict, tmp_dict, sep=' - ', **kwargs):
        if tmp_dict is None:
            to_dict[field_name] = from_dict[field_name]
        else:
            try:
                tmp_data = tmp_dict['_comb_key_str_'][field_name]
            except KeyError:
                if '_comb_key_str_' not in tmp_dict:
                    tmp_dict['_comb_key_str_'] = {}
                if field_name not in tmp_dict['_comb_key_str_']:
                    tmp_dict['_comb_key_str_'][field_name] = dict(
                        tmp_part_1='',
                        tmp_part_2='',
                        tmp_part_3='',
                    )
                tmp_data = tmp_dict['_comb_key_str_'][field_name]

            tmp_key = from_dict[self._key_field]
            if tmp_key.is_any:
                tmp_data['tmp_part_1'] = from_dict.get(field_name, '')

            elif tmp_key.has_key2:
                if tmp_key.is_exact or not tmp_data['tmp_part_3']:
                    tmp_data['tmp_part_3'] = from_dict.get(field_name, '')

            elif tmp_key.has_key1:
                tmp_data['tmp_part_2'] = from_dict.get(field_name, '')

            if tmp_data['tmp_part_2'] and tmp_data['tmp_part_3']:
                tmp_ret = tmp_data['tmp_part_2'] + sep + tmp_data['tmp_part_3']
            else:
                tmp_ret = tmp_data['tmp_part_3'] or tmp_data['tmp_part_2']

            if tmp_data['tmp_part_1'] and tmp_ret:
                tmp_ret = tmp_data['tmp_part_1'] + ': ' + tmp_ret

            to_dict[field_name] = tmp_ret

    def _add_key(self, key, to_dict, field_name, value, key1=None, key2=None, **kwargs):
        tmp_key = self._key_handler(value)
        if key1 is not None:
            key.key1 = key1(tmp_key.key1)
        if key2 is not None:
            key.key2 = key2(tmp_key.key2)
        to_dict[field_name] = tmp_key

    def _merge_key(self, key, from_dict, field_name, to_dict, tmp_dict, **kwargs):
        if field_name not in to_dict:
            to_dict[field_name] = from_dict[field_name]
        else:
            to_dict[field_name] = from_dict[field_name] + to_dict[field_name]

    def _get_rec_handler(self, field_name):
        try:
            return self._fields[field_name]
        except KeyError:
            raise AttributeError('field %s not defined' % field_name)

    def _merge_rec(self, key, from_rec, to_rec, tmp_dict):
        if from_rec is not None:
            for field, value in from_rec.items():
                self._get_rec_handler(field).merge(key, from_dict=from_rec, to_dict=to_rec, tmp_dict=tmp_dict)

    def get(self, key, overrides=None):
        key = self._key_handler(key)
        if not key.is_exact:
            raise AttributeError('Can only "GET" exact keys.  (%s passed)' % key)
        tmp_ret = self[key]
        tmp_ret['key'] = key
        self._merge_rec(key, from_rec=overrides, to_rec=tmp_ret, tmp_dict=None)
        return tmp_ret
    __call__ = get

    def __getitem__(self, key):
        key = self._key_handler(key)
        try:
            return self._cache[key]
        except KeyError:
            tmp_def = self._data.get('*.*', None)
            tmp_sd = self._data.get(key.star_dot, None)
            tmp_ds = self._data.get(key.dot_star, None)
            tmp_ex = self._data.get(str(key), None)

            if key.is_exact:
                if self.return_on == 'full' and tmp_ex is None:
                    raise KeyError('no exact matches found for %s in lookup: %r' % (key, self))
                elif self.return_on == 'partial' and tmp_ex is None and tmp_ds is None and tmp_sd is None:
                    raise KeyError('no partial matches found for %s in lookup: %r' % (key, self))
            elif key.has_key1 or key.has_key2:
                if not self.return_on == 'any':
                    if (key.has_key1 and tmp_ds is None) or (key.has_key2 and tmp_sd is None):
                        raise KeyError('no partial matches found for %s in lookup: %r' % (key, self))
            tmp_ret = {}
            tmp_dict = {}
            self._merge_rec(key, tmp_def, tmp_ret, tmp_dict)
            self._merge_rec(key, tmp_sd, tmp_ret, tmp_dict)
            self._merge_rec(key, tmp_ds, tmp_ret, tmp_dict)
            self._merge_rec(key, tmp_ex, tmp_ret, tmp_dict)

            if not tmp_ret:
                raise KeyError('%s not in lookup: %r' % (key, self))

            self._cache[key] = tmp_ret
            return tmp_ret

    def __setitem__(self, key, value):
        key = self._key_handler(key)
        tmp_rec = {}
        for field, field_value in value.items():
            self._get_rec_handler(field).add(key, to_dict=tmp_rec, value=field_value)
        tmp_rec[self._key_field] = key
        self._data[key] = tmp_rec
        self._cache.clear()

    def __contains__(self, key):
        if key in self._cache:
            return True

        key = self._key_handler(key)
        if key.is_exact:
            if self.return_on == 'full' and key not in self._data:
                return False
            elif self.return_on == 'partial' and \
                            key not in self._data and \
                            key.star_dot not in self._data and \
                            key.dot_star not in self._data:
                return False
        elif key.has_key1 or key.has_key2:
            if not self.return_on == 'any':
                if (key.has_key1 and key.dot_star not in self._data) or \
                        (key.has_key2 and key.star_dot not in self._data):
                    return False
        return True

    def clear(self):
        self._cache.clear()
        self._data.clear()
        self.update(self._defaults)

    def update(self, *args):
        for arg in args:
            if isinstance(arg, (list, tuple)):
                self.update(*arg)
            elif isinstance(arg, dict):
                arg = deepcopy(arg)
                try:
                    key = arg.pop(self._key_field)
                except KeyError:
                    raise KeyError('Key %r is not in dict %r' % (self._key_field, arg))
                self[key] = arg
            elif isinstance(arg, str):
                self[arg] = {}
            else:
                raise TypeError('item cannot be updated: %r' % arg)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(list(self._data.keys()))

    def __iter__(self):
        for i in self._data.keys():
            yield i
