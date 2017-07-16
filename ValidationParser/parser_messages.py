from enum import IntEnum, Enum
from helpers.general import make_list, adv_format, AutoAddDict, CompareFieldMixin
from collections import UserDict, namedtuple, UserList
from copy import deepcopy
from ValidationParser.exceptions import MessageListLocked


class OverrideDict(UserDict):
    all_items = None

    def clear(self):
        self.all_items = None
        super().clear()

    def __setitem__(self, key, value):
        if key == '*':
            self.all_items = value
            return
        super().__setitem__(key, value)

    def __getitem__(self, item):
        if self.all_items is not None:
            return self.all_items
        return super().__getitem__(item)


class RESULT_CODES(IntEnum):
    OK = 3
    WARNING = 2
    ERROR = 1
    UNKNOWN = 99

class TEXT_TYPE(Enum):
    SHORT = 'short'
    LONG = 'long'
    FULL = 'full'
    DETAILED = 'detailed'


BASE_PARSING_MESSAGES = [
    {'key': 'INVALID_CHAR', 'name': 'Invalid Character'},
    'SEGMENT_TOO_LONG',
    'SEGMENT_TOO_SHORT',
    'TOO_MANY_SEGMENTS',
    'TOO_FEW_SEGMENTS',
    'UNCLOSED_STRING',
    'INVALID_LOCATION',
    'INVALID_NEXT_CHAR',
    {'key': 'MISSING_CHAR', 'name': 'Missing Character'},
    'INVALID_END',
    'INVALID_START',
    'MISSING_SEGMENT',
    'ABOVE_RANGE',
    'BELOW_RANGE',
    'ERROR',
    {'key': 'DEPRECATED', 'name': 'Deprecated Content', 'status': RESULT_CODES.WARNING},
    {'key': 'POTENTIAL_PROBLEM', 'status': RESULT_CODES.WARNING},
    {'key': 'WARNING', 'status': RESULT_CODES.WARNING},
    {'key': 'VALID', 'name': 'Valid Segment', 'status': RESULT_CODES.OK}
]


'''
DEFAULT_REFERENCE = {
    'name': '',
    'description': None,
    'url': None,
    'text': None,
}
'''

MsKwargs = namedtuple('MsKwargs', ('msg_key', 'msg_kwargs', 'seg_key', 'seg_kwargs'))


def _get_key(item):
    if isinstance(item, dict):
        return item['key']
    else:
        return item


def _make_kwargs(item):
    if isinstance(item, str):
        return {'key': item}
    else:
        return item


def _split_sm(item, def_as_msg=True, other_ret='*'):
    if isinstance(item, (list, tuple)):
        tmp_seg, tmp_msg = item
    elif isinstance(item, str):
        if '.' in item:
            tmp_seg, tmp_msg = item.split('.', 1)
        else:
            if def_as_msg:
                tmp_msg = item
                tmp_seg = other_ret
            else:
                tmp_msg = other_ret
                tmp_seg = item
    else:
        raise AttributeError('Cannot split segment/message from %r' % item)
    return tmp_seg, tmp_msg


def _make_ms_kwargs(segment, message=None, *, msg_kwargs=None, seg_kwargs=None,
                    other_ret='*', as_segment=False, default_segment=None):

    def _split_key(item, kwargs=None):
        if isinstance(item, dict):
            item = deepcopy(item)
            try:
                key = item.pop('key')
            except KeyError:
                raise KeyError('Error, no "key" in %r' % item)
            if kwargs is not None:
                item.update(kwargs)
            return key, item
        else:
            return item, kwargs or {}

    if isinstance(segment, MsKwargs):
        return segment

    seg_kwargs = deepcopy(seg_kwargs) or {}
    msg_kwargs = deepcopy(msg_kwargs) or {}

    if as_segment:
        seg_key, seg_kwargs = _split_key(segment, seg_kwargs)
        msg_key = None

    else:
        if message is None:
            msg_key, msg_kwargs = _split_key(segment, msg_kwargs)
            seg_key, msg_key = _split_sm(msg_key, other_ret=other_ret)
            seg_key = msg_kwargs.get('segment', seg_key)
            seg_kwargs = seg_kwargs
        else:
            msg_key, msg_kwargs = _split_key(message, msg_kwargs)
            seg_key, seg_kwargs = _split_key(segment, seg_kwargs)

    if default_segment is not None and seg_key in (None, '*'):
        seg_key = default_segment

    tmp_ret = MsKwargs(
        msg_key=msg_key,
        msg_kwargs=msg_kwargs,
        seg_key=seg_key,
        seg_kwargs=seg_kwargs,
    )

    return tmp_ret


class ParseMessageHelper(CompareFieldMixin):
    """
    PMH = ParseMessageHelper(message_lookup, parse_string, segment_definition or key)

    add via string:
        PMH('msg_key')                           #  position = 0, length = 0
        PMH('msg_key', 'msg_key', position, length)
        PMH('msg_key', position, length, note)   # adds a note to the msg
        PMH('msg_key', position)                 # length = 0

        PMH('segment_key.msg_key', position)      # allows entering for a different segment

    add via dict:
        PMH({'key': 'msg_key', ...}, position, length)

    add definition:
        PMH.define({'key': 'msg_key',...}, 'msg_key', ...}

    check if contains:
        'msg_key' in PMH
        'segment_key.* in PMH  == [True/False]

    check if contains at position:
        PMH.at('*.msg_key', position) == [True/False]
        PMH.at('segment_key.msg_key', position) == [True/False]
        PMH.at('segment_key.*', position) == [True/False]

    combine:
        PMH += PMH_2

    combine into new:
        PMH_3 = PMH + PMH_2

    remove key:
        PMH.remove('segment_key.msg_key', position)  # if no position, removes last key
        PMH.remove('msg_key', position)  # if no position and no segment separater, removes last key
        PMH.remove('segment_key.*')  # if msg = * and no position removes all messages in that segment
        PMH.remove('*.msg_key')  # if segment = *, and no position, removes all messages of that key in all segments

    list keys:
        PMH.keys(show_segment_key, show_msg_key, show_position, show_length)
            [('segment_key.msg_key', position, length), (segment_key.msg_key, position, length), ...]

        PMH.keys(show_segment_key, show_msg_key, show_position, combine_like=True, show_length)
            [('segment_key.msg_key', [(position, length), (position, length)]),
             ('segment_key.msg_key', [(position, length)]), ...]


    list_objects:
        PMH.items() == [msg_obj, msg_pbj, ...]
        for item in PMH

    get_object:
        PMH.get_message(msg_key, position)
            * if no position, gets last message
            * if msg_key == "segment_key.*", gets last msg for that segment
            * if msg_key == "*,msg_key", gets last message of that type (any segment)
            * if no args, gets worst msg

    printed output:
        PMH.get_output('template_or_key', join='join_string', header='', footer='')
            * ordered by:
                position (lowest to highest)
                returned code (worst to best)
                length (shortest to longest)
                alpha (segment_key / msg_key)

    bool:
        if PMH:   # returns true if worst code == OK or WARNING

    len:
        len(PMH)   #  counts messages


    Sort Order =

    """
    _compare_fields = ('max_status',)

    def __init__(self, message_lookup, parse_str, segment):
        self.message_lookup = message_lookup
        self.parse_str = parse_str
        self.segments = AutoAddDict(dict)
        # self.message_keys = {}
        self._caches = {}
        # self.messages = []
        self.current_segment = segment
        # self.parent = None

        self.max_status = RESULT_CODES.UNKNOWN
        self.max_length = 0

    def copy(self):
        tmp_ret = self.__class__(self.message_lookup, self.parse_str, self.current_segment)
        tmp_ret.segments = deepcopy(self.segments)
        tmp_ret.max_status = self.max_status
        tmp_ret.max_length = self.max_length
        return tmp_ret

    def _mid(self, begin, length=None, end=None):
        if length is None and end is None:
            return self.parse_str[begin:]
        if length is None:
            return self.parse_str[begin:end]
        else:
            return self.parse_str[begin:begin+length]

    def extend(self, *messages, begin=0, length=0, note=None, **kwargs):
        self._caches.clear()

        self._check_pos(begin)
        self._check_pos(length+begin)

        self.max_length = max(self.max_length, length)

        last_item = None
        for m in messages:
            if isinstance(m, self.__class__):
                self._merge(m)
                last_item = m
            else:
                last_item = self.add(m, begin=begin, length=length, note=note, **kwargs)

        return last_item

    def add(self, message, begin=0, length=0, note=None, **kwargs):
        self._caches.clear()
        self._check_pos(begin)
        self._check_pos(length+begin)
        self.max_length = max(self.max_length, length)

        if isinstance(message, (str, dict)):
            ms_args = _make_ms_kwargs(message, msg_kwargs=kwargs, default_segment=self.current_segment)
            try:
                tmp_msg = self.segments[ms_args.seg_key][ms_args.msg_key]
            except KeyError:
                tmp_msg = self.message_lookup(ms_args.seg_key, ms_args.msg_key, **ms_args.msg_kwargs)
                tmp_msg.message_helper = self
                self.segments[ms_args.seg_key][ms_args.msg_key] = tmp_msg
                # self.messages.append(tmp_msg)
            tmp_msg.instances.add(begin=begin, length=length, note=note)
            self.max_status = min(self.max_status, tmp_msg.status)
            return tmp_msg

        elif isinstance(message, self.__class__):
            return self.extend(message)

        elif isinstance(message, ParseMessage):
            if message.key not in self.segments[message.segment_key]:
                message.message_helper = self
                self.segments[message.segment_key][message.key] = message

            for i in message:
                i.message = message
            self.max_status = min(self.max_status, message.status)
            return message
        else:
            raise AttributeError('Unable to determine type of object to add: %r' % message)


    __call__ = add

    def __bool__(self):
        return self.max_status != RESULT_CODES.ERROR

    def __len__(self):
        return len(self.instances)

    def __iter__(self):
        for i in self.instances:
            yield i

    @property
    def messages(self):
        for s in self.segments.values():
            for m in s.values():
                yield m

    @property
    def instances(self):
        if 'instances' not in self._caches:
            tmp_instances = []
            for m in self.messages:
                for i in m:
                    tmp_instances.append(i)
            tmp_instances.sort()
            self._caches['instances'] = tmp_instances
        return self._caches['instances']

    def _check_pos(self, position):
        if position is not None and position > len(self.parse_str):
            raise IndexError('Position is beyond the parsed string')
        return position

    def define(self, *args, **kwargs):
        for a in args:
            ms_args = _make_ms_kwargs(a, msg_kwargs=kwargs)
            self.message_lookup.message(ms_args)

    def items(self, key=None, position=None):
        position = self._check_pos(position)
        matched = False
        indexed = False
        for i in self.instances:
            if key is None or i.key_match(key):
                matched = True
                if position is None:
                    indexed = True
                    yield i
                elif i.begin == position:
                    indexed = True
                    yield i
        if not matched:
            raise KeyError('Message %r not found' % key)

        if not indexed:
            raise IndexError('Message %r not found at position %s' % (key, str(position)))

    def get_instance(self, message_key=None, position=None):
        tmp_items = list(self.items(message_key, self._check_pos(position)))
        return tmp_items[-1]

    def get_message(self, segment, message=None):
        ms_kwargs = _make_ms_kwargs(segment, message, default_segment=self.current_segment)
        return self.segments[ms_kwargs.seg_key][ms_kwargs.msg_key]

    def at(self, key, position):
        for i in self.items(key):
            if self._check_pos(position) in i:
                return True
        return False

    def remove(self, message_key, position=None):
        self._caches.clear()
        position = self._check_pos(position)
        found_key = False
        kill_segs = []
        for seg_key, segment in self.segments.items():
            kill_msgs = []
            for msg_key, message in segment.items():
                if message.key_match(message_key):
                    found_key = True
                    if position is None:
                        kill_msgs.append(msg_key)
                    else:
                        message.remove(position)
                        if len(message) == 0:
                            kill_msgs.append(msg_key)
            for m in kill_msgs:
                del self.segments[seg_key][m]
            if not self.segments[seg_key]:
                kill_segs.append(seg_key)
        for s in kill_segs:
            del self.segments[s]
        if not found_key:
            raise KeyError('Key %r not present in %r' % (message_key, self))

    def keys(self, key=None, inc_message_key=True, inc_segment_key=True):
        if inc_message_key and inc_segment_key:
            tmp_key = 'long_key'
        elif inc_segment_key:
            tmp_key = 'segment_key'
        else:
            tmp_key = 'key'
        tmp_ret = {}
        for i in self.items(key):
            tmp_ret[i.get_str(tmp_key)] = None
        return list(tmp_ret)

    def info(self, key=None, inc_message_key=True, inc_segment_key=True,
             inc_position=True, inc_length=True, combine_like=False):
        if combine_like:
            tmp_dict = {}
            for i in self.items(key):
                tmp_key, tmp_info = i.info(inc_message_key=inc_message_key,
                                           inc_segment_key=inc_segment_key,
                                           inc_position=inc_position,
                                           inc_length=inc_length,
                                           combine_like=combine_like)
                if tmp_key in tmp_dict:
                    tmp_dict[tmp_key].append(tmp_info)
                else:
                    tmp_dict[tmp_key] = [tmp_info]

            tmp_ret = []
            for key, item in tmp_dict.items():
                tmp_ret.append((key, item))
            return tmp_ret
        else:
            tmp_ret = []
            for i in self.items(key):
                tmp_info = i.info(inc_message_key=inc_message_key,
                                  inc_segment_key=inc_segment_key,
                                  inc_position=inc_position,
                                  inc_length=inc_length,
                                  combine_like=combine_like)
                tmp_ret.append(tmp_info)
            return tmp_ret

    def get_output(self, template_or_key=None, join='\n', header=None, footer=None, combine_same=True):
        tmp_ret = []
        if header is not None:
            tmp_ret.append(header)

        if template_or_key == 'seg_keys':
            for seg_key, msgs in self.segments.items():
                tmp_msgs = list(msgs.values())
                tmp_msgs.sort()
                tmp_keys = []
                for msg in tmp_msgs:
                    if len(msg) != 1:
                        tmp_keys.append('%s(%s)' % (msg.key, len(msg)))
                    else:
                        tmp_keys.append(msg.key)

                tmp_str = '%s(%s)' % (seg_key, ', '.join(tmp_keys))
                tmp_ret.append(tmp_str)
        else:
            for i in self:
                tmp_str = i.get_str(template_or_key)
                if not combine_same or tmp_str not in tmp_ret:
                    tmp_ret.append(tmp_str)

        if footer is not None:
            tmp_ret.append(footer)

        if join is not None:
            tmp_ret = join.join(tmp_ret)

        return tmp_ret

    def _merge(self, other):
        for msg in other.messages:
            self.add(msg)

    def __add__(self, other):
        tmp_ret = self.copy()
        tmp_ret._merge(other)
        return tmp_ret

    def __iadd__(self, other):
        self._merge(other)
        return self

    def __contains__(self, item):
        for m in self.messages:
            if m.key_match(item):
                return True
        return False

    def __str__(self):
        return self.get_output('seg_keys', join=', ')

    def __repr__(self):
        return 'ParseMessageHelper [%s] --> %s' % (self, self.max_status.name)

    """
    def get_str(self, recurse=True, single=True, as_str=True, join_str=',', flat=False, text_typ='short'):
        if flat:
            if single:
                tmp_ret = {}
                for m in self.messages:
                    tmp_ret[m.get_str(text_type=text_typ)] = None
                if recurse:
                    for c in self.children:
                        tmp_ret.update(c.get_str(recurse=True, single=True, as_str=False, text_typ=text_typ))
                if not as_str:
                    return tmp_ret
                tmp_ret = list(tmp_ret.keys())
            else:
                tmp_ret = []
                for m in self.messages:
                    tmp_ret.append(m.get_str(text_type=text_typ))
                if recurse:
                    for c in self.children:
                        tmp_ret.extend(c.get_str(recurse=True, single=False, as_str=False, text_typ=text_typ))
                if not as_str:
                    return tmp_ret
            return join_str.join(tmp_ret)
        else:
            tmp_ret = []
            for m in self.messages:
                tmp_ret[m.get_str(text_type=text_typ)] = None
            if recurse:
                for c in self.children:
                    tmp_ret.append(c.get_str(recurse=True, flat=False, text_typ=text_typ))
            return '%s(%s)' % (self.segment, ', '.join(tmp_ret))
    """


class InstanceList(UserList):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.at = {}
        self.starts = AutoAddDict(list)

    def add(self, begin=0, length=0, note=None):
        if isinstance(begin, ParseInstance):
            tmp_inst = begin
        else:
            tmp_inst = ParseInstance(self.message, begin=begin, length=length, note=note)
        self.append(tmp_inst)
        return tmp_inst

    def append(self, item):
        self.data.append(item)
        self.starts[item.begin].append(item)
        self.at.clear()

    # def at(self, position):
    #     if not self.at:
    #         for i in self.data:
    #             for p in range(i.begin, i.end):
    #                 self.at[p] = None
    #     return position in self.at

    def copy(self, new_message=None):
        if new_message is None:
            new_message = self.message

        tmp_ret = self.__class__(new_message)
        for item in self:
            tmp_ret.append(item.copy(new_message))
        return tmp_ret

    # def clear(self):
    #     self.data.clear()
    #     self.at.clear()
    #     self.starts.clear()

    def remove(self, position):
        tmp_kill = []
        for index, i in enumerate(self.data):
            if i.begin == position:
                tmp_kill.append(index)
        tmp_kill.reverse()
        for index in tmp_kill:
            self.data.pop(index)

    # def __contains__(self, item):
    #     return self.at(item)

    def __iter__(self):
        self.sort()
        for i in self.data:
            yield i


class ParseMessage(CompareFieldMixin):
    """
    DEFAULT_MESSAGE = {
        'key': '',
        'name': '',
        'description': None,
        'status': None,
        'status_override': None,
        'references': [],
    }

    DEFAULT_SEGMENT = {
        'key': '',
        'name': '',
        'description': None,  # will default to name.title()
        'references': [],  # item or list of strings
        'messages': {},
        'status_override': None
    }

    """
    _string_formats = {
        'name': '{message.name}',
        'key': '{message.key}',
        'description': '{message.description}',
        'segment_name': '{segment.name}',
        'segment_description': '{segment.description}',
        'segment_key': '{segment.key}',
        'long_key': '{segment.key}.{message.key}',
        'long_name': '{segment.name} / {message.name}',
        'long_description': '{segment.description}\n{message.description}',
        # 'full_name': '{segment.name} / {message.name}',
        # 'full_description': '{segment.description}\n{message.description}{?\n<note>?}',
    }
    _compare_fields = ('status', 'segment_key', 'key')
    _compare_caps_sensitive = False

    def __init__(self, message_lookup, message, **kwargs):
        self.message_lookup = message_lookup
        self.message_helper = None
        self.segment = message.segment
        self.message = message
        self.status = None
        self.instances = InstanceList(self)
        for k, i in kwargs.items():
            setattr(self, k, i)

        self._field_cache = {}

        # tmp_status = self.status

    def get_str(self, format_str):
        try:
            return self._field_cache[format_str]
        except KeyError:
            try:
                format_str = self._string_formats[format_str]
            except KeyError:
                pass
            tmp_dict = dict(
                segment=self.segment,
                message=self.message,
                # note=self.note,
                # begin=str(self.begin),
                # length=str(self.length),
                status=self.status.name
            )
            if 'references' in format_str:
                tmp_dict['references'] = self.reference_str(detailed=False)
            if 'detailed_references' in format_str:
                tmp_dict['references'] = self.reference_str(detailed=True)

            tmp_str = adv_format(format_str, **tmp_dict)
            self._field_cache[format_str] = tmp_str
        return tmp_str

    def remove(self, position):
        self.instances.remove(position)

    def __getattr__(self, item):
        if item in self._string_formats:
            return self.get_str(item)
        raise AttributeError('%r is not a valid Attribute for %r' % (item, self))

    def key_match(self, key):
        if '.' not in key:
            segment = self.message_helper.current_segment
        else:
            segment, key = key.split('.', 1)
        seg_match = False
        key_match = False
        if segment == '*' or segment == self.segment_key:
            seg_match = True
        if key == '*' or key == self.key:
            key_match = True
        return key_match and seg_match

    @property
    def references(self):
        try:
            return self._field_cache['references']
        except KeyError:
            tmp_ret = {}

            for r in self.segment.references:
                tmp_ret[r] = self.message_lookup.get_reference(r)
            for r in self.message.references:
                tmp_ret[r] = self.message_lookup.get_reference(r)

            self._field_cache['references'] = tmp_ret
            return tmp_ret

    def reference_str(self, detailed=False):
        tmp_ret = []
        tmp_dict = self.references
        tmp_keys = list(self.references)
        tmp_keys.sort()

        if detailed:
            joiner = '\n\n'
        else:
            joiner = '\n'

        for rk in tmp_keys:
            r = tmp_dict[rk]
            tmp_ret.append(r.reference_str(detailed=detailed))
        return joiner.join(tmp_ret)

    def update(self, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def copy(self, **kwargs):
        tmp_ret = self.__class__(self.message_lookup, self.message)
        tmp_ret.status = self.status
        tmp_ret._field_cache = deepcopy(self._field_cache)
        tmp_ret.instances = self.instances.copy(tmp_ret)
        for k, i in kwargs.items():
            try:
                setattr(tmp_ret, k, i)
            except AttributeError:
                raise AttributeError('Cant set attribute %s to %r' % (k, i))
        return tmp_ret

    def __deepcopy__(self, memodict):
        tmp_ret = self.copy()
        memodict[id(self)] = tmp_ret
        return tmp_ret

    # def _compare_(self, other):
    #     if not isinstance(other, self.__class__):
    #         raise AttributeError('Cannot compare ParsingMessages with %r' % other)
    #
    #     for field in ['status', 'segment_key', 'key']:
    #         self_field = getattr(self, field)
    #         other_field = getattr(other, field)
    #         if self_field > other_field:
    #             return 1
    #         elif self_field < other_field:
    #             return -1
    #     return 0
    #
    # def __eq__(self, other):
    #     return self._compare_(other) == 0
    #
    # def __ne__(self, other):
    #     return self._compare_(other) != 0
    #
    # def __lt__(self, other):
    #     return self._compare_(other) == -1
    #
    # def __le__(self, other):
    #     return self._compare_(other) < 1
    #
    # def __gt__(self, other):
    #     return self._compare_(other) == 1
    #
    # def __ge__(self, other):
    #     return self._compare_(other) > -1

    def __str__(self):
        return self.get_str('long_key')

    def __repr__(self):
        return 'MessageObject(%s) -> %s' % (self.__str__(), self.status.name)

    def __bool__(self):
        return self.status != RESULT_CODES.ERROR

    def __len__(self):
        return len(self.instances)

    def __iter__(self):
        for i in self.instances:
            yield i


class ParseInstance(CompareFieldMixin):
    _string_formats = {
        'name': '{message.name}',
        'key': '{message.key}',
        'description': '{message.description!S}',
        'segment_name': '{segment.name}',
        'segment_description': '{segment.description!S}',
        'segment_key': '{segment.key}',
        'long_key': '{segment.key}.{message.key}',
        'long_name': '{segment.name} / {message.name}',
        'long_description': '{segment.description!S}{?\n<message.description!S>?}',
        'full_name': '{segment.name} / {message.name}',
        'full_description': '{segment.description!S}{?\n<message.description!S>?}{?\n<note>?}',
    }
    _compare_fields = ('status', 'begin', 'length', 'segment_key', 'key')
    _compare_caps_sensitive = False

    def __init__(self, message, begin=0, length=0, note=None):
        self.message = message
        self.begin = begin
        self.length = length
        self.note = note
        self._field_cache = {}

    def copy(self, new_message=None):
        if new_message is None:
            new_message = self.message
        return self.__class__(new_message, begin=self.begin, length=self.length, note=self.note)
    __copy__ = copy

    def key_match(self, key, position=None):
        if not self.message.key_match(key):
            return False
        if position is None:
            return True
        return position == self.begin

    @property
    def end(self):
        return self.begin + self.length

    @property
    def text(self):
        return self.message.message_helper._mid(self.begin, length=self.length)

    def info(self, inc_message_key=True, inc_segment_key=True, inc_position=True, inc_length=True, combine_like=True):
        if inc_message_key and inc_segment_key:
            tmp_ret = (self.get_str('long_key'),)
        elif inc_segment_key:
            tmp_ret = (self.get_str('segment_key'),)
        else:
            tmp_ret = (self.get_str('key'),)

        tmp_nums = ()
        if inc_position:
            tmp_nums += (self.begin,)
        if inc_length:
            tmp_nums += (self.length,)

        if combine_like:
            tmp_ret += (tmp_nums,)
        else:
            tmp_ret += tmp_nums

        return tmp_ret

    def get_str(self, format_str):
        try:
            return self._field_cache[format_str]
        except KeyError:
            try:
                format_str = self._string_formats[format_str]
            except KeyError:
                pass
            tmp_dict = dict(
                segment=self.message.segment,
                message=self.message.message,
                note=self.note,
                begin=str(self.begin),
                length=str(self.length),
                status=self.message.status.name
            )
            if 'references' in format_str:
                tmp_dict['references'] = self.message.reference_str(detailed=False)
            if 'detailed_references' in format_str:
                tmp_dict['references'] = self.message.reference_str(detailed=True)

            tmp_str = adv_format(format_str, **tmp_dict)
            self._field_cache[format_str] = tmp_str
        return tmp_str

    def __getattr__(self, item):
        if item in self._string_formats:
            return self.get_str(item)
        else:
            return getattr(self.message, item)

    def __contains__(self, item):
        return self.begin <= item <= self.end

    def __str__(self):
        return self.text

    def __repr__(self):
        return '%s --> %r [%s/%s]' % (self.message.__repr__(), self.text, self.begin, self.end)

    def __bool__(self):
        return self.message.status != RESULT_CODES.ERROR


class ParseBaseRec(object):
    # rw_fields = ()
    _default_data = {}

    def __init__(self, key, **kwargs):
        self._data = {'key': key}
        self.update(kwargs)
        self.__initialised = True

    def update(self, *items, force=False, **kwargs):
        for item in items:
            if isinstance(item, dict):
                for k, i in item.items():
                    self._set(k, i, force=force)
            elif isinstance(item, self.__class__):
                for k, i in item._data.items():
                    self._set(k, i, force=force)

        for k, i in kwargs.items():
            self._set(k, i, force=force)

    @property
    def name(self):
        try:
            return self._data['name']
        except KeyError:
            tmp_ret = self._data['key'].replace('-', ' ').replace('_', ' ').title()
            self._data['name'] = tmp_ret
            return tmp_ret

    def _set(self, key, value, force=False):
        if key not in self._default_data or (key in self._data and not force):
            return

        if key == 'references':
            value = make_list(value, deepcopy_first=True)

        elif key == 'messages':
            value = deepcopy(value)

        self._data[key] = value

    def __setattr__(self, key, value):
        if '_ParseBaseRec__initialised' not in self.__dict__:
            object.__setattr__(self, key, value)
        elif key in self.__dict__:
            super().__setattr__(key, value)
        elif key in self._default_data:
            self._set(key, value)
        else:
            raise AttributeError('%s is not a valid property of %r' % (key, self))

    def __setitem__(self, key, value):
        self._set(key, value)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError('%s is not a valid property of %r' % (item, self))

    def __getitem__(self, item):
        try:
            return self._data[item]
        except KeyError:
            return self._default_data[item]

    def copy(self):
        tmp_kwargs = self._data.copy()
        if 'segment' in tmp_kwargs:
            del tmp_kwargs['segment']
        return self.__class__(**tmp_kwargs)

    def __deepcopy__(self, memodict=None):
        return self.copy()

    def __repr__(self):
        return self.key


class ParseMessageRec(ParseBaseRec):
    # rw_fields = ('status',)
    _default_data = {
        'segment': None,
        'key': None,
        'name': None,
        'description': None,
        'status': RESULT_CODES.ERROR,
        'references': None,
    }

    def __init__(self, key, **kwargs):
        if isinstance(key, MsKwargs):
            kwargs = kwargs or key.msg_kwargs
            key = key.msg_key
        super().__init__(key, **kwargs)
        if 'references' not in self._data:
            self._data['references'] = []

    def _set(self, key, value, force=False):
        if key == 'segment':
            self._data['segment'] = value
            value.messages[self._data['key']] = self
        else:
            super(ParseMessageRec, self)._set(key, value, force=force)


class ParseSegmentRec(ParseBaseRec):
    # rw_fields = ('status', )
    _default_data = {
        'key': None,
        'name': None,
        'description': None,  # will default to name.title()
        'references': None,  # item or list of strings
        'messages': None}

    def __init__(self, lookup, key, **kwargs):
        if isinstance(key, MsKwargs):
            kwargs = kwargs or key.seg_kwargs
            key = key.seg_key

        self.lookup = lookup
        super().__init__(key, **kwargs)
        if 'references' not in self._data:
            self._data['references'] = []

        if 'messages' not in self._data:
            self._data['messages'] = {}

    def copy(self):
        tmp_kwargs = self._data.copy()
        if 'segment' in tmp_kwargs:
            del tmp_kwargs['segment']
        return self.__class__(self.lookup, **tmp_kwargs)

    def message(self, msg_key, msg_data=None):
        if isinstance(msg_key, MsKwargs):
            msg_data = msg_key.msg_kwargs
            msg_key = msg_key.msg_key

        try:
            tmp_msg = self._data['messages'][msg_key]
        except KeyError:
            pass
        else:
            if msg_data:
                tmp_msg.update(msg_data)
                self.lookup.message_cache.clear()
            return tmp_msg

        if msg_key in self.lookup.segments['*'].messages:
            tmp_msg = self.lookup.segments['*'].messages[msg_key].copy()

        else:
            if self.lookup.locked:
                raise MessageListLocked(msg_key)
            tmp_msg = ParseMessageRec(msg_key, segment=self)

        tmp_msg.update(msg_data, segment=self)
        self._data['messages'][msg_key] = tmp_msg
        return tmp_msg


class ParseRefRec(object):
    def __init__(self, key, **kwargs):
        self.key = key
        self.name = kwargs.get('name', key.replace('-', ' ').replace('_', ' ').title())
        self.description = kwargs.get('description', '')
        self.url = kwargs.get('url', '')
        self.text = kwargs.get('text', '')

    def __repr__(self):
        return self.name

    def reference_str(self, detailed=False):
        if detailed:
            return adv_format('{name}{? (<description>)?}{?\nURL&coln; <url>?}{?\n<text>?}',
                              name=self.name,
                              description=self.description,
                              url=self.url,
                              text=self.text,
                              colon=':')
        else:
            return adv_format('{name}{? (<description>)?}',
                              name=self.name,
                              description=self.description)


class MessageLookup(object):
    ms_kwargs = namedtuple('ms_kwargs', ('msg_key', 'msg_kwargs', 'seg_key', 'seg_kwargs'))

    def __init__(self,
                 messages=None,
                 references=None,
                 segments=None,
                 error_on_warning=False,
                 error_on_message=None,
                 locked=False):

        self.locked = False
        self._defaults = dict(
            error_on_warning=error_on_warning,
            error_on_message=error_on_message or [],
            messages=messages or BASE_PARSING_MESSAGES,
            segments=segments or [],
            references=references or [],
        )
        self.message_cache = {}
        self.error_on_warning = error_on_warning
        self.override_status = {}
        self.references = {}
        self.segments = {}
        # self.segment('*')

        # self.message_keys = {}
        # self.sm_cache = {}
        # self.ok_messages = []

        self.clear()

        self.locked = locked

    def clear_overrides(self):
        self.set_error_on_warning(self._defaults['error_on_warning'])
        self.override_status = {'*': OverrideDict()}
        self.add_error_on_message(*self._defaults['error_on_message'])
        self.message_cache.clear()

    def clear(self):
        # self.message_keys.clear()
        # self.sm_cache.clear()
        tmp_locked = self.locked
        self.locked = False
        self.references.clear()
        self.segments.clear()
        self.segment('*')
        self.add(
            references=deepcopy(self._defaults['references']),
            messages=deepcopy(self._defaults['messages']),
            segments=deepcopy(self._defaults['segments']))
        self.clear_overrides()
        self.locked = tmp_locked

    def add(self, messages=None, segments=None, references=None):
        tmp_lock = self.locked
        self.locked = False
        if segments is not None:
            for item in make_list(segments, deepcopy_first=True):
                self.segment(item)

        if messages is not None:
            for item in make_list(messages, deepcopy_first=True):
                self.message(item)

        if references is not None:
            for item in make_list(references, deepcopy_first=True):
                self.add_reference(**_make_kwargs(item))
        
        self.message_cache.clear()

        self.locked = tmp_lock

    def message(self, segment, message=None, seg_kwargs=None, **msg_kwargs):
        if isinstance(segment, self.ms_kwargs):
            ms_args = segment
        else:
            ms_args = _make_ms_kwargs(segment, message, seg_kwargs=seg_kwargs, msg_kwargs=msg_kwargs)

        tmp_ret = self.segment(ms_args).message(ms_args)
        return tmp_ret

    def segment(self, segment, **kwargs):
        if not isinstance(segment, MsKwargs):
            ms_kwargs = _make_ms_kwargs(segment, message='*', seg_kwargs=kwargs)
        else:
            ms_kwargs = segment

        try:
            tmp_ret = self.segments[ms_kwargs.seg_key]
        except KeyError:
            if self.locked:
                raise MessageListLocked(ms_kwargs.seg_key)
            tmp_seg = ParseSegmentRec(self, ms_kwargs)
            self.segments[ms_kwargs.seg_key] = tmp_seg
            return tmp_seg
        else:
            if ms_kwargs.seg_kwargs:
                tmp_ret.update(ms_kwargs.seg_kwargs)
                self.message_cache.clear()
            return tmp_ret

    def add_reference(self, key, **kwargs):
        tmp_ret = ParseRefRec(key, **kwargs)
        self.references[key] = tmp_ret
        return tmp_ret

    def add_error_on_message(self, *overrides, set_to=RESULT_CODES.ERROR):
        for item in overrides:
            if item in ['VALID', '*.VALID']:
                continue

            segment, message = _split_sm(item)

            if segment == '*' and message == '*':
                raise AttributeError('Error, cannot global override')

            if segment not in self.override_status:
                self.override_status[segment] = OverrideDict()
            self.override_status[segment][message] = set_to

        self.message_cache.clear()

    def set_error_on_warning(self, set_to=True):
        self.error_on_warning = set_to
        self.message_cache.clear()

    def _get_status(self, seg_key, msg_key, msg_status):
        try:
            tmp_ret = self.override_status[seg_key][msg_key]
        except KeyError:
            try:
                tmp_ret = self.override_status['*'][msg_key]
            except KeyError:
                tmp_ret = msg_status
        if self.error_on_warning and tmp_ret == RESULT_CODES.WARNING:
            return RESULT_CODES.ERROR

        return tmp_ret

    def __call__(self, segment, message=None, **kwargs):
        ms_data = _make_ms_kwargs(segment, message, msg_kwargs=kwargs)
        try:
            tmp_ret = self.message_cache[ms_data.seg_key][ms_data.msg_key]
        except KeyError:
            tmp_msg = self.message(ms_data)
            tmp_ret = ParseMessage(self, tmp_msg,
                                   status=self._get_status(ms_data.seg_key, ms_data.msg_key, tmp_msg.status))

            if ms_data.seg_key not in self.message_cache:
                self.message_cache[ms_data.seg_key] = {}
            self.message_cache[ms_data.seg_key][ms_data.msg_key] = tmp_ret

        # if kwargs:
        #     tmp_ret = tmp_ret.copy(**kwargs)

        return tmp_ret.copy()

    def get_reference(self, ref_key):
        try:
            return self.references[ref_key]
        except KeyError:
            return self.add_reference(ref_key)

    def iter_messages(self):
        for i in self.segments.values():
            for m in i['messages'].values():
                yield m

    @staticmethod
    def _get_max_key_len(iter_in):
        max_len = 0
        for i in iter_in:
            max_len = max(max_len, len(i))
        return max_len

    def dump(self):
        tmp_ret = ['', '']
        max_seg = self._get_max_key_len(self.segments)
        seg_header = '{!s:>%s} : {!r}' % max_seg
        for key, seg in self.segments.items():
            tmp_ret.append(seg_header.format(key, seg))
            max_item = self._get_max_key_len(seg['messages'])
            msg_header = '    {!s:>%s} : {!r}' % max_item
            for msg_key, msg in seg['messages'].items():
                tmp_ret.append(msg_header.format(msg_key, msg))
        return '\n'.join(tmp_ret)

    def len(self):
        return len(list(self.iter_messages()))
    __len__ = len

MESSAGE_LOOKUP = MessageLookup(messages=BASE_PARSING_MESSAGES)
