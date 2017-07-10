from copy import copy, deepcopy
from collections import UserDict
from string import _string


def adv_getattr(obj, attr):
    first, rest = _string.formatter_field_name_split(attr)

    # loop through the rest of the field_name, doing
    #  getattr or getitem as needed
    if first:
        obj = getattr(obj, first)

    for is_attr, i in rest:
        if is_attr:
            obj = getattr(obj, i)
        else:
            obj = obj[i]

    return obj


class CompareFieldMixin(object):
    _compare_fields = None
    _compare_caps_sensitive = True
    _compare_convert_to = None

    def _compare_(self, other):
        if self._compare_convert_to is not None:
            other = self._compare_convert_to(other)

        if not isinstance(other, self.__class__):
            raise AttributeError('Cannot compare ParsingMessages with %r' % other)

        for field in self._compare_fields:
            self_field = adv_getattr(self, field)
            if isinstance(self_field, str) and not self._compare_caps_sensitive:
                self_field = self_field.lower()

            other_field = adv_getattr(other, field)
            if isinstance(other_field, str) and not self._compare_caps_sensitive:
                other_field = other_field.lower()

            if self_field > other_field:
                return 1
            elif self_field < other_field:
                return -1
        return 0

    def __eq__(self, other):
        return self._compare_(other) == 0

    def __ne__(self, other):
        return self._compare_(other) != 0

    def __lt__(self, other):
        return self._compare_(other) == -1

    def __le__(self, other):
        return self._compare_(other) < 1

    def __gt__(self, other):
        return self._compare_(other) == 1

    def __ge__(self, other):
        return self._compare_(other) > -1




class AutoAddDict(UserDict):
    def __init__(self, sub_type, *args, **kwargs):
        self._sub_type = sub_type
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            self.data[item] = self._sub_type()
            return super().__getitem__(item)


def show_compared_items(expected, returned):
    tmp_ret = ['', '',
               'Expected: %r\nReturned: %r' % (expected, returned),
               '\n\n',
               '*****************************',
               '\nExpected:\n%s\n\nReturned:\n%s\n\n' % (expected, returned)]

    return '\n'.join(tmp_ret)


def make_char_str(*chars_in):
    tmp_ret = []
    for char in chars_in:
        if isinstance(char, str):
            tmp_ret.append(char)
        elif isinstance(char, int):
            tmp_ret.append(chr(char))
        elif isinstance(char, tuple):
            for c in range(char[0], char[1] + 1):
                tmp_ret.append(chr(c))
    return ''.join(tmp_ret)


def make_list(obj_in, copy_first=False, deepcopy_first=False):
    if obj_in is None:
        return []
    if isinstance(obj_in, str):
        return [obj_in]

    if copy_first:
        obj_in = copy(obj_in)
    elif deepcopy_first:
        obj_in = deepcopy(obj_in)

    if isinstance(obj_in, (list, tuple)):
        return obj_in
    if hasattr(obj_in, '__iter__'):
        return obj_in
    return [obj_in]


class UnSet(object):
    """
    Used in places to indicated an unset condition where None may be a valid option

    .. note:: *I borrowed the concept from* :py:mod:`configparser` *module*

    Example:
        For an example of this, see :py:class:`MultiLevelDictManager.get`

    """
    UnSetValidationString = '_*_This is the Unset Object_*_'

    def __repr__(self):
        return 'Empty Value'

    def __str__(self):
        return 'Empty Value'

    def __eq__(self, other):
        return isinstance(other, UnSet)

    def __ne__(self, other):
        return not isinstance(other, UnSet)

    def __bool__(self):
        return False


_UNSET = UnSet()

