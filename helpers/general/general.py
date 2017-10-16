from copy import copy, deepcopy
from collections import UserDict, UserList
from string import _string
import textwrap
import sys


class InterruptedRange(object):
    def __init__(self, begin=None, end=None, length=None):
        self._ranges = {}
        self._order = []
        self.start = 0
        self.stop = 0
        self._len = 0
        if begin is not None:
            self.add(begin, end, length)

    def add(self, begin, end=None, length=None):
        if isinstance(begin, self.__class__):
            for r in begin._ranges:
                self.add(r)
            return
        elif isinstance(begin, range):
            tmp_rng = range(begin.start, begin.stop)
            begin = tmp_rng.start
        else:
            if end is None:
                if length is None:
                    end = begin
                else:
                    end = begin + length
            else:
                if length is not None:
                    if begin + length != end:
                        raise AttributeError('begin (%s) + length (%s) != end (%s)' % (begin, length, end))
            tmp_rng = range(begin, end)

        while begin not in self._ranges:
            begin = begin+1
        if begin <= tmp_rng.stop:
            self._ranges[begin] = tmp_rng
            self._order.append(begin)
            self._order.sort()
            self._recalc()
            self.start = min(tmp_rng.start, self.start)
            self.stop = max(tmp_rng.stop, self.stop)
            self._len += len(tmp_rng)

    def _has_overlap(self):
        last_range = None
        for s in self._order:
            r = self._ranges[s]
            if last_range is None:
                last_range = r
            else:
                if r.start < last_range.stop:
                    return True
        return False

    def _recalc(self):
        if self._has_overlap():
            last_range = None
            rebuilt_ranges = {}
            rebuilt_starts = []
            self._len = 0
            for s in self._order:
                r = self._ranges[s]
                if last_range is None:
                    last_range = r
                else:
                    if r.start < last_range.stop:
                        tmp_start = min(r.start, last_range.start)
                        tmp_stop = max(r.stop, last_range.stop)
                        tmp_range = range(tmp_start, tmp_stop)
                    else:
                        tmp_range = r
                    rebuilt_ranges[tmp_range.start] = tmp_range
                    rebuilt_starts.append(tmp_range.start)
                    self._len += len(tmp_range)
                    last_range = tmp_range

            self._ranges = rebuilt_ranges
            self._order = rebuilt_starts
            self._order.sort()

    def extend(self, *ranges):
        for r in ranges:
            self.add(*make_list(r))

    def at(self, position, as_begin=False):
        if as_begin:
            return position in self._order
        else:
            for r in self._ranges.values():
                if position in r:
                    return True
            return False

    def get(self, position, default=_UNSET):
        for r in self._ranges.values():
            if position in r:
                return r
        if default is _UNSET:
            raise IndexError('%s not found in range' % position)
        else:
            return default

    def remove(self, begin, end):
        def in_rem(pos):
            return begin < pos < end

        rebuilt_ranges = {}
        rebuilt_starts = []
        self._len = 0
        def set_range(tmp_range):
            rebuilt_ranges[tmp_range.start] = tmp_range
            rebuilt_starts.append(tmp_range.start)
            self.start = min(tmp_range.start, self.start)
            self.stop = max(tmp_range.stop, self.stop)
            self._len += len(tmp_range)

        for s in self._order:
            r = self._ranges[s]

            if in_rem(r.start):
                if in_rem(r.stop):  # remove mid
                    set_range(range(r.start, begin-1))
                    set_range(range(end, r.stop))
                else:  # remove end
                    set_range(range(end, r.stop))
            else:
                if in_rem(r.stop):  # remove start
                    set_range(range(r.start, begin-1))
                else:  # no match
                    set_range(r)

        self._ranges = rebuilt_ranges
        self._order = rebuilt_starts
        self._order.sort()

    def copy(self):
        tmp_ret = self.__class__()
        tmp_ret.extend(*self._ranges)
        return tmp_ret

    def clear(self):
        self._ranges.clear()
        self._order.clear()
        self.start=0
        self.stop=0

    def __iter__(self):
        for r in self._ranges:
            for i in r:
                yield i

    __call__ = add

    def __bool__(self):
        if self._ranges:
            return True
        return False

    def __str__(self):
        tmp_ret = []
        for i in self._ranges:
            if i.start != i.stop:
                tmp_ret.append('%s-%s' % (i.start, i.stop))
            else:
                tmp_ret.append(i.start)
        return '(%s)' % ', '.join(tmp_ret)

    def __len__(self):
        return self._len

    def __add__(self, other):
        tmp_item = self.copy()
        tmp_item(other)
        return tmp_item

    def __iadd__(self, other):
        self(other)
        return self

    __contains__ = at


DEFAULT_LINE_FORMAT = dict(
    item_join=', ',
    line_join=', ',
    max_line_len=None,
    max_line_count=None,
    indent=0,
    prefix='',
    postfix='',
    prefix_indent=0,
    postfix_indent=0)

class ListFormatSpec(UserDict):
    def __init__(self, *args, **kwargs):
        super(ListFormatSpec, self).__init__(*args, **kwargs)
        tmp_data = DEFAULT_LINE_FORMAT.copy()
        tmp_data.update(self.data)
        self.data = tmp_data
        if len(tmp_data) != len(DEFAULT_LINE_FORMAT):
            raise AttributeError('Invalid format spec item passed')

    @property
    def unique(self):
        tmp_ret = {}
        for key, item in self.data.items():
            if item != DEFAULT_LINE_FORMAT[key]:
                tmp_ret[key] = item
        return tmp_ret

'''
class RangeListItem(object):
    def _init__(self, item, start=0, end=None):
        self.item = item
        self.start = start
        self.end = end or sys.maxsize
        self.next = None
        self.prev = None
        
    def add(self, item, start=0):
        tmp_item = self.__class__(item, start)
        if start == self.start:
            raise IndexError('start position %s already in list' % start)
        if start > self.start:
            if start < self.next.start:
'''


def find_keys(line_in):
    tmp_ret = []
    in_key = False
    tmp_key = ''
    for c in line_in:
        if c == '{':
            if in_key:
                raise AttributeError('Error: "{" found after "{" in %s' % line_in)
            in_key = True
        elif c == '}' or (in_key and (c == ':' or c == '!')):
            if not in_key:
                raise AttributeError('Error: "%s" found with no "{" in %s' % (c, line_in))
            in_key = False
            tmp_ret.append(tmp_key)
            tmp_key = ''
        elif in_key:
            tmp_key += c
    return tmp_ret


class RangeList(object):
    def __init__(self):
        self.items = {0: None}
        self.starts = [0]

    def add(self, item, start=0):
        self.items[start] = item
        if start not in self.starts:
            self.starts.append(start)
        self.starts.sort()

    def get(self, pos):
        tmp_start = 0
        for r in self.starts:
            if pos >= r:
                tmp_start = r
            else:
                break
        # if tmp_start is None:
        #     raise AttributeError('Unknown Error, end of range list encountered')
        return self.items[tmp_start]

    def __iter__(self):
        for s in self.starts:
            yield s, self.items[s]

    def __repr__(self):
        tmp_ret = []
        for i in self.starts:
            tmp_ret.append(str(i))
        return 'RangeList ( %s )' % ', '.join(tmp_ret)


class ListFormatter(object):
    _line_format = '{}'
    _empty_text = 'No Items'

    def __init__(self, line_format=None, empty_text=None, specs=None, do_not_cache=False):
        """
        Default Spec dict = dict(
            item_join=', ',
            line_join=', ',
            max_line_len=None,
            max_line_count=None,
            indent=0,
            prefix='',
            postfix='',
            indent_prefix=0,
            indent_postfix=0,
            )

        :return:
        """
        self._do_not_cache = do_not_cache
        self._line_format = line_format or self._line_format
        self._empty_text = empty_text or self._empty_text
        self._spec_count = 0
        self._specs = RangeList()
        self._data = []
        self._output = None
        self.keys = []

        if specs:
            if isinstance(specs, (list, tuple)):
                if len(specs) == 2 and isinstance(specs[0], int):
                    specs = [specs]
            else:
                specs = make_list(specs)

            for s in specs:
                if isinstance(s, (list, tuple)):
                    self._spec_count = None
                    s_item = s[1]
                    s_count = s[0]
                else:
                    if self._spec_count is None:
                        raise AttributeError('Spec Counts must be used once started')
                    s_item = s
                    s_count = self._spec_count
                    self._spec_count += 1

                if not isinstance(s_item, ListFormatSpec):
                    s_item = ListFormatSpec(**s_item)

                self._specs.add(s_item, s_count)
        else:
            self._specs.add(DEFAULT_LINE_FORMAT, 0)

        self.keys = find_keys(self._line_format)

    def append(self, *line_data):
        self._output = None
        for line in line_data:
            if line is None:
                continue
            elif isinstance(line, dict):
                self._data.append(self._line_format.format(**line))
            else:
                self._data.append(self._line_format.format(*make_list(line)))
        return self
    __call__ = append

    def clear(self):
        self._output = None
        self._data.clear()

    def as_str(self):
        if self._output is None or self._do_not_cache:
            specs = self._specs.get(len(self._data))

            if self._data:

                if specs['max_line_len'] is None and specs['max_line_count'] is None:
                    lines_str = specs['item_join'].join(self._data)
                else:
                    lines = []
                    line_len = 0
                    line_items = 0
                    max_line_len = specs['max_line_len'] or sys.maxsize
                    max_line_count = specs['max_line_count'] or sys.maxsize
                    item_join = specs['item_join']
                    item_join_len = len(item_join)
                    line_lengths = []
                    for l in self._data:
                        line_lengths.append(len(l))

                    tmp_line = []
                    for item_num, item_len in enumerate(line_lengths):
                        line_items += 1
                        if line_len+item_len+item_join_len > max_line_len or line_items > max_line_count:
                            lines.append(item_join.join(tmp_line))
                            line_items = 1
                            line_len = 0
                            tmp_line = []
                        line_len += item_len + item_join_len
                        tmp_line.append(self._data[item_num])
                    lines.append(item_join.join(tmp_line))
                    lines_str = specs['line_join'].join(lines)
            else:
                lines_str = self._empty_text

            if specs['indent']:
                indent_str = ''.rjust(specs['indent'])
                lines_str = textwrap.indent(lines_str, indent_str)

            prefix = specs['prefix']
            if prefix:
                if specs['prefix_indent']:
                    indent_str = ''.rjust(specs['prefix_indent'])
                    if '{indent}' in prefix:
                        prefix = prefix.format(indent=indent_str)
                    else:
                        prefix = indent_str + prefix

            postfix = specs['postfix']
            if postfix:
                if specs['postfix_indent']:
                    indent_str = ''.rjust(specs['postfix_indent'])
                    if '{indent}' in postfix:
                        postfix = postfix.format(indent=indent_str)
                    else:
                        postfix = indent_str + postfix

            lines_str = prefix + lines_str + postfix
            self._output = lines_str

        return self._output
    __str__ = as_str

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for l in self._data:
            yield l

    def __bool__(self):
        if self._data:
            return True
        else:
            return False

    def __repr__(self):
        return 'ListFormatter: %s items' % len(self)

    def __contains__(self, item):
        if item[0] == '{' and item[-1] == '}':
            item = item[1:-1]
        return item in self._line_format


def make_list_formatter(config):
    if isinstance(config, dict):
        if 'line_format' in config or 'empty_text' in config or 'specs' in config:
            return ListFormatter(**config)
        else:
            return ListFormatter(specs=config)

    elif isinstance(config, (list, tuple)):
        tmp_line_format = ListFormatter._line_format
        tmp_empty_text = ListFormatter._empty_text
        arg_count = 0
        spec_list = []
        for arg in config:
            if isinstance(arg, str):
                if arg_count == 0:
                    tmp_line_format = arg
                elif arg_count == 1:
                    tmp_empty_text = arg
                arg_count += 1
            else:
                spec_list.append(arg)
        return ListFormatter(line_format=tmp_line_format,
                             empty_text=tmp_empty_text,
                             specs=spec_list)

    elif isinstance(config, str):
        return ListFormatter(line_format=config)

    elif isinstance(config, ListFormatter):
        config.clear()
        return config

    elif config is None:
        return config



def adv_getattr(obj, attr):
    first, rest = _string.formatter_field_name_split(attr)

    # loop through the rest of the field_name, doing
    #  getattr or getitem as needed
    if first:
        obj = getattr(obj, first)
        #if callable(obj):
        #    obj = obj()

    for is_attr, i in rest:
        if is_attr:
            obj = getattr(obj, i)
            # if callable(obj):
            #     obj = obj()
        else:
            obj = obj[i]

    return obj


def none_to_empty_dict(item) -> dict:
    if item is None:
        return {}
    return item


def none_to_emtpy_tuple(item) -> tuple:
    if item is None:
        return tuple()
    return item


class CompareFieldMixin(object):
    _compare_fields = None
    _compare_caps_sensitive = True
    _compare_convert_to = None
    _compare_convert_args = None
    _compare_convert_kwargs = None

    def _compare_(self, other, compare_fields=None):
        if compare_fields is None:
            compare_fields = self._compare_fields

        if self._compare_convert_to is not None:
            if isinstance(self._compare_convert_to, str) and self._compare_convert_to == 'self':
                if not isinstance(other, self.__class__):
                    other = self.__class__(other,
                                           *none_to_emtpy_tuple(self._compare_convert_args),
                                           **none_to_empty_dict(self._compare_convert_kwargs))
                else:
                    other = self._compare_convert_to(other,
                                           *none_to_emtpy_tuple(self._compare_convert_args),
                                           **none_to_empty_dict(self._compare_convert_kwargs))

        for field in compare_fields:
            self_field = adv_getattr(self, field)
            if isinstance(self_field, str) and not self._compare_caps_sensitive:
                self_field = self_field.lower()

            if isinstance(other, self.__class__):
                other_field = adv_getattr(other, field)
            else:
                other_field = other

            if isinstance(other_field, str) and not self._compare_caps_sensitive:
                other_field = other_field.lower()

            try:

                if self_field > other_field:
                    return 1
                elif self_field < other_field:
                    return -1
            except TypeError:
                raise TypeError('Error comparing %r with %r' % (self_field, other_field))
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


def make_list(obj_in, copy_first=False, deepcopy_first=False, force_list=False):
    if obj_in is None:
        return []
    if isinstance(obj_in, str):
        return [obj_in]

    if copy_first:
        obj_in = copy(obj_in)
    elif deepcopy_first:
        obj_in = deepcopy(obj_in)
    if force_list:
        if isinstance(obj_in, list):
            return obj_in
        if isinstance(obj_in, dict):
            return [obj_in]
        if hasattr(obj_in, '__iter__'):
            return list(obj_in)
        return [obj_in]
    else:
        if isinstance(obj_in, (list, tuple)):
            return obj_in
        if isinstance(obj_in, dict):
            return [obj_in]
        if hasattr(obj_in, '__iter__'):
            return obj_in
        return [obj_in]


def make_set(*obj_in, copy_first=False, deepcopy_first=False):
    tmp_ret = []
    for obj in obj_in:
        if obj_in is None:
            continue
        if isinstance(obj_in, str):
            tmp_ret.append(obj)
            continue

        if copy_first:
            obj = copy(obj)
        elif deepcopy_first:
            obj = deepcopy(obj)

        if isinstance(obj, (set, list, tuple)):
            tmp_ret.extend(obj)
        elif hasattr(obj, '__iter__'):
            tmp_ret.extend(obj)
        else:
            tmp_ret.append(obj)

    return set(tmp_ret)


def list_get(list_in, index, default=None):
    try:
        return list_in[index]
    except IndexError:
        return default


def copy_none(obj_in):
    if obj_in is None:
        return obj_in
    return copy(obj_in)


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

