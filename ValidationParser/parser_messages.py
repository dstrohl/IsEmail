from enum import IntEnum, Enum
from helpers.general import make_list, adv_format, AutoAddDict, CompareFieldMixin, make_set, list_get, ListFormatter, \
    ListFormatSpec, make_list_formatter, find_keys
from collections import UserDict, namedtuple, UserList
from copy import deepcopy
from ValidationParser.exceptions import MessageListLocked, MessageNotFoundError, SegmentNotFoundError, \
    ReferenceNotFoundError

from helpers.general.wildcard_dict import KeyObj, WildCardMergeDict

# class OverrideDict(UserDict):
#     all_items = None
#
#     def clear(self):
#         self.all_items = None
#         super().clear()
#
#     def __setitem__(self, key, value):
#         if key == '*':
#             self.all_items = value
#             return
#         super().__setitem__(key, value)
#
#     def __getitem__(self, item):
#         if self.all_items is not None:
#             return self.all_items
#         return super().__getitem__(item)
#
#     def __contains__(self, item):
#         if item == '*' or self.all_items is not None:
#             return True
#         return item in self.data


# class DictOfList(UserDict):
#
#     def __getitem__(self, item):
#         if item not in self.data:
#             self.data[item] = []
#         return self.data[item]
#
#     def __setitem__(self, key, value):
#         if isinstance(value, (list, tuple)):
#             self[key].extend(value)
#         else:
#             self[key].append(value)
#
#
# class DictOfDict(UserDict):
#     def __init__(self, *args, dict_type=None, **kwargs):
#         self._dict_type = dict_type or {}
#         super(DictOfDict, self).__init__(*args, **kwargs)
#
#     def __getitem__(self, item):
#         if item not in self.data:
#             self.data[item] = self._dict_type()
#         return self.data[item]
#
#     def set(self, key, value):
#         self.data[key] = value
#
#     def __setitem__(self, key, value):
#         self[key].update(value)
#
#
# class MsgDict(UserDict):
#
#     def __getitem__(self, item):
#         try:
#             return super().__getitem__(item)
#         except KeyError:
#             if '*' in self.data:
#                 return self.data['*']
#
#     def __contains__(self, item):
#         if item == '*' or '*' in self.data:
#             return True
#         return item in self.data
#
#
# class SegmentDict(UserDict):
#
#     def __init__(self, *args, **kwargs):
#         self._dict_type = dict
#         super(SegmentDict, self).__init__(*args, **kwargs)
#
#     def clear(self):
#         self.data.clear()
#
#     def get_seg(self, seg_key):
#         if seg_key not in self.data:
#             self.data[seg_key] = self._dict_type()
#         return self.data[seg_key]
#
#     def __setitem__(self, key, value):
#         if not isinstance(value, RESULT_CODES):
#             raise TypeError('value (%r) is not a result code type' % value)
#         else:
#             key = make_message_key(key)
#             if key.seg_key == '*' and key.msg_key == '*':
#                 raise AttributeError('Cannot set *.* override')
#             self.get_seg(key.seg_key)[key.msg_key] = value
#
#     def __getitem__(self, key):
#         if isinstance(key, RESULT_CODES):
#             return self.data[key]
#         else:
#             # key = make_message_key(key)
#             try:
#                 tmp_ret = self.data[key.seg_key][key.msg_key]
#             except KeyError:
#                 try:
#                     tmp_ret = self.data['*'][key.msg_key]
#                 except KeyError:
#                     tmp_ret = self.data[key.seg_key]['*']
#
#             return self.data.get(tmp_ret, tmp_ret)
#
#     def __contains__(self, key):
#         if isinstance(key, RESULT_CODES):
#             return key in self.data
#         else:
#             key = make_message_key(key)
#             if key.seg_key in self.data and (key.msg_key == '*' or key.msg_key in self.data[key.seg_key] or '*' in self.data[key.seg_key]):
#                 return True
#
#             if '*' in self.data and key.msg_key in self.data['*']:
#                 return True
#
#             return False
#

'''
class STATUS_CODES(IntEnum):
    UNKNOWN = -1
    SKIP = 0
    OK = 1
    WARNING = 50
    ERROR = 99
'''

class STATUS_CODES(IntEnum):
    UNKNOWN = 99
    SKIP = 98
    OK = 90
    WARNING = 50
    ERROR = 1

STATUS_CODE_DICT = dict(
    OK=STATUS_CODES.OK,
    WARNING=STATUS_CODES.WARNING,
    ERROR=STATUS_CODES.ERROR,
    UNKNOWN=STATUS_CODES.UNKNOWN,
    SKIP=STATUS_CODES.SKIP)


class TEXT_TYPE(Enum):
    SHORT = 'short'
    LONG = 'long'
    FULL = 'full'
    DETAILED = 'detailed'


BASE_PARSING_MESSAGES = [
    {'key': '*.INVALID_CHAR', 'name': 'Invalid Character'},
    '*.SEGMENT_TOO_LONG',
    '*.SEGMENT_TOO_SHORT',
    '*.TOO_MANY_SEGMENTS',
    '*.TOO_FEW_SEGMENTS',
    '*.UNOPENED_ENCLOSURE',
    '*.UNCLOSED_ENCLOSURE',
    '*.INVALID_LOCATION',
    '*.INVALID_NEXT_CHAR',
    {'key': '*.MISSING_CHAR', 'name': 'Missing Character'},
    '*.INVALID_END',
    '*.INVALID_START',
    '*.MISSING_SEGMENT',
    '*.ABOVE_RANGE',
    '*.BELOW_RANGE',
    '*.END_OF_STRING',
    '*.ERROR',
    {'key': '*.UNPARSED_CONTENT', 'name': 'Un-parsed content remaining'},
    {'key': '*.DEPRECATED', 'name': 'Deprecated Content', 'status': STATUS_CODES.WARNING},
    {'key': '*.POTENTIAL_PROBLEM', 'status': STATUS_CODES.WARNING},
    {'key': '*.WARNING', 'status': STATUS_CODES.WARNING},
    {'key': '*.VALID', 'name': 'Valid Segment', 'status': STATUS_CODES.OK}
]


'''
DEFAULT_REFERENCE = {
    'name': '',
    'description': None,
    'url': None,
    'text': None,
}

DEFAULT_MESSAGE = {
    'key' : '',
    'name': '',
    'description': None,
    'status': STATUS_CODES.ERROR,
    'references': [],
}
'''

"""
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


def parse_msg_args(*args, seg_kwargs=None, msg_kwargs=None, as_segment=False):

    def _breakup_param(key, as_msg):
        # tmp_seg = None
        tmp_msg = None
        tmp_kwargs = {}
        if isinstance(key, dict):
            tmp_seg = key.pop('key', None)
            tmp_kwargs = key
        else:
            tmp_seg = key

        if tmp_seg is None:
            tmp_msg = None
        elif isinstance(tmp_seg, (list, tuple)):
            tmp_msg = tmp_seg[1]
            tmp_seg = tmp_seg[0]
        elif isinstance(tmp_seg, str) and '.' in tmp_seg:
            tmp_seg, tmp_msg = tmp_seg.split('.', maxsplit=1)

        if as_msg and tmp_msg is None:
            tmp_msg = tmp_seg
            tmp_seg = None
        return tmp_seg, tmp_msg, tmp_kwargs

    def _combine_keys(*keys):
        tmp_ret = None
        for key in keys:
            if key is not None:
                if tmp_ret is None:
                    tmp_ret = key
                else:
                    if tmp_ret == key:
                        continue
                    else:
                        raise AttributeError('Non matching keys fund: %s != %s' % (tmp_ret, key))
                continue
        return tmp_ret

    if len(args) > 2:
        raise AttributeError('Invalid number of arguments')

    args = list(args)

    if len(args) < 2:
        while len(args) < 2:
            args.append(None)

    seg = deepcopy(args[0])
    msg = deepcopy(args[1])
    seg_kwargs = deepcopy(seg_kwargs) or {}
    msg_kwargs = deepcopy(msg_kwargs) or {}

    if not as_segment and msg is None:
        msg = seg
        seg = None

    seg_1, msg_1, seg_kwargs_1 = _breakup_param(seg, as_msg=False)
    seg_2, msg_2, msg_kwargs_1 = _breakup_param(msg, as_msg=True)
    seg_3, msg_3, seg_kwargs = _breakup_param(seg_kwargs, as_msg=False)
    seg_4, msg_4, msg_kwargs = _breakup_param(msg_kwargs, as_msg=True)

    seg_kwargs.update(seg_kwargs)
    msg_kwargs.update(msg_kwargs)
    seg_kwargs.update(seg_kwargs_1)
    msg_kwargs.update(msg_kwargs_1)

    seg = _combine_keys(seg_1, seg_2, seg_3, seg_4)
    msg = _combine_keys(msg_1, msg_2, msg_3, msg_4)

    return seg, msg, seg_kwargs, msg_kwargs


def make_message_key(*args, seg_kwargs=None, msg_kwargs=None, default_segment=None, other_ret='*', as_segment=False):
    if args:
        if isinstance(args[0], KeyObj):
            return args[0]
        elif isinstance(args[0], (ParseMessageRec, ParseSegmentRec, ParseMessage)):
            return args[0].key_obj
    tmp_ret = parse_msg_args(*args, seg_kwargs=seg_kwargs, msg_kwargs=msg_kwargs, as_segment=as_segment)
    return KeyObj(*tmp_ret, default_segment=default_segment, other_ret=other_ret)

"""


'''
class MsgKeyObj(KeyObj):
    """
    extra kwargs:
        seg_kwargs
        msg_kwargs,
        default_segment,

    """
    def __init__(self, *keys, **kwargs):
        self.seg_kwargs = {}
        self.msg_kwargs = {}
        super(MsgKeyObj, self).__init__(*keys, **kwargs)

    def _set_keys(self, keys, kwargs):
        seg_kwargs = kwargs.get('seg_kwargs', {})
        msg_kwargs = kwargs.get('msg_kwargs', {})
        default_segment = kwargs.get('default_segment', None)

        no_kwargs = not seg_kwargs and not msg_kwargs

        if len(keys) == 1 and isinstance(keys[0], str) and no_kwargs:
            keys = keys[0]
            if '.' in keys:
                self.key1, self.key2 = keys.split('.', maxsplit=1)
            elif self._default_key == 1:
                self.key1 = keys
                self.key2 = '*'
            else:
                self.key2 = keys
                self.key1 = default_segment or '*'
        elif not keys and no_kwargs:
            self.key1 = '*'
            self.key2 = default_segment or '*'

        elif len(keys) > 2:
            raise AttributeError('Too many key arguments (no more than 2 can be passed)')
        else:
            key1 = deepcopy(keys[0])
            if len(keys) == 2:
                key2 = deepcopy(keys[1])
            else:
                key2 = None

            seg_kwargs = deepcopy(seg_kwargs) or {}
            msg_kwargs = deepcopy(msg_kwargs) or {}

            if self._default_key == 2 and key2 is None:
                key2 = key1
                key1 = None

            seg_1, msg_1, seg_kwargs_1 = self._breakup_param(key1, as_key2=False)
            seg_2, msg_2, msg_kwargs_1 = self._breakup_param(key2, as_key2=True)
            seg_3, msg_3, seg_kwargs = self._breakup_param(seg_kwargs, as_key2=False)
            seg_4, msg_4, msg_kwargs = self._breakup_param(msg_kwargs, as_key2=True)

            self.seg_kwargs.update(seg_kwargs)
            self.msg_kwargs.update(msg_kwargs)
            self.seg_kwargs.update(seg_kwargs_1)
            self.msg_kwargs.update(msg_kwargs_1)

            self.key1 = self._combine_keys(seg_1, seg_2, seg_3, seg_4)
            self.key2 = self._combine_keys(msg_1, msg_2, msg_3, msg_4)

    def _breakup_param(self, key, as_key2):
        tmp_key2 = None
        tmp_kwargs = {}

        if isinstance(key, dict):
            tmp_key1 = key.pop('key', None)
            tmp_kwargs = key

        elif isinstance(key, KeyObj):
            tmp_key1 = str(key)
        else:
            tmp_key1 = key

        if isinstance(tmp_key1, (list, tuple)):
            tmp_key1, tmp_key2 = tmp_key1[:2]

        elif isinstance(tmp_key1, str) and '.' in tmp_key1:
            tmp_key1, tmp_key2 = tmp_key1.split('.', maxsplit=1)

        if tmp_key1 == '':
            tmp_key1 = None

        if tmp_key2 == '':
            tmp_key2 = None

        if as_key2 and tmp_key2 is None:
            tmp_key2 = tmp_key1
            tmp_key1 = None
        return tmp_key1, tmp_key2, tmp_kwargs

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

    def update(self, *args, **kwargs):
        msg_key_obj = self.make_key(*args, **kwargs)
        super(MsgKeyObj, self).update(msg_key_obj)
        self.msg_kwargs.update(msg_key_obj.msg_kwargs)
        self.seg_kwargs.update(msg_key_obj.seg_kwargs)

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

    @property
    def any_seg(self):
        return '*.%s' % self.msg_key
'''

'''

# Helper object used in football
class ParseSimpleMessageHelper(CompareFieldMixin):
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

    def __init__(self, message_lookup, parse_str, segment, local_overrides=None):
        """
        :param message_lookup:
        :param parse_str:
        :param segment:
        """
        self.message_lookup = message_lookup
        self.parse_str = parse_str
        # self.segments = AutoAddDict(dict)
        # self._caches = {}
        self.current_segment = segment

        self.max_status = STATUS_CODES.UNKNOWN
        self.max_msg = None
        self.max_length = 0
        self.local_overrides = local_overrides

    def copy(self):
        tmp_ret = self.__class__(self.message_lookup, self.parse_str, self.current_segment,
                                 local_overrides=self.local_overrides)
        tmp_ret.max_status = self.max_status
        tmp_ret.max_length = self.max_length
        tmp_ret.max_msg = self.max_msg
        return tmp_ret

    def _mid(self, begin, length=None, end=None):
        if length is None and end is None:
            return self.parse_str[begin:]
        if length is None:
            return self.parse_str[begin:end]
        else:
            return self.parse_str[begin:begin + length]

    def extend(self, *messages, begin=0, length=0, note=None, **kwargs):
        last_item = None
        for m in messages:
            last_item = self.add(m, begin=begin, length=length, note=note, **kwargs)
        return last_item

    def update_max(self, message=None, length=None, status=None):
        if length is not None:
            self.max_length = max(self.max_length, length)
        if message is not None:
            message = make_message_key(message)
            status = status or self.message_lookup.get_status(message, local_overrides=self.local_overrides)
            if self.max_status == STATUS_CODES.UNKNOWN or\
                    self.max_status < status or \
                    (self.max_status == status and self.max_msg > message):
                self.max_status = status
                self.max_msg = message

    def _add_new(self, msg_key_obj, begin=0, length=0, note=None, **kwargs):
        self.update_max(msg_key_obj, length)
        return msg_key_obj

    def _add_msg(self, message, begin=0, length=0):
        self.update_max(message.key_obj, length, message.status)
        return message

    def add(self, message, begin=0, length=0, note=None, **kwargs):
        self._check_pos(begin)
        self._check_pos(length + begin - 2)

        if isinstance(message, (str, dict)):
            msg_key_obj = make_message_key(message, msg_kwargs=kwargs, default_segment=self.current_segment)
            return self._add_new(msg_key_obj)

        if isinstance(message, ParseMessage):
            return self._add_msg(message)

        elif isinstance(message, self.__class__):
            return self._merge(message)

        elif isinstance(message, (list, tuple)):
            return self.extend(message)

    __call__ = add

    def __bool__(self):
        return self.max_status != STATUS_CODES.ERROR

    def __len__(self):
        return len(self.instances)

    def __iter__(self):
        for i in self.instances:
            yield i

    @property
    def messages(self):
        return self.max_msg

    @property
    def instances(self):
        return [self.max_msg]

    def _check_pos(self, position):
        if position is not None and position > len(self.parse_str):
            raise IndexError(
                'Position (%s) is beyond the parsed string length (%s)' % (position, len(self.parse_str)))
        return position

    def define(self, *args, **kwargs):
        for a in args:
            ms_args = make_message_key(a, msg_kwargs=kwargs)
            self.message_lookup.message(ms_args)

    def items(self, key=None, position=None):
        position = self._check_pos(position)
        if key == self.max_msg:
            if position is None or position == self.max_length:
                yield self.max_msg
                return
            else:
                raise IndexError('Message %r not found at position %s' % (key, str(position)))
        else:
            raise KeyError('Message %r not found' % key)

    def get_instance(self, message_key=None, position=None):
        tmp_items = list(self.items(message_key, self._check_pos(position)))
        return tmp_items[-1]

    def get_message(self, segment, message=None):
        return []

    def at(self, key, position):
        if self.items(key, position):
            return True
        return False

    def remove(self, message_key, position=None):
        if self.items(message_key, position):
            self.max_msg = None
            self.max_status = STATUS_CODES.UNKNOWN
        else:
            raise KeyError('Key %r not present in %r' % (message_key, self))

    def keys(self, key=None, inc_message_key=True, inc_segment_key=True):
        if not inc_message_key and not inc_segment_key:
            return [self.max_msg]
        elif inc_message_key and inc_segment_key:
            return [str(self.max_msg)]
        elif inc_segment_key:
            return [self.max_msg.seg_key]
        else:
            return [self.max_msg.msg_key]

    def info(self, key=None, inc_message_key=True, inc_segment_key=True,
             inc_position=True, inc_length=True, combine_like=False):
        # TODO: Do this
        return

    def get_output(self, template_or_key=None, join='\n', header=None, footer=None, combine_same=True):
        # TODO: Do this
        return

    def _merge(self, other):
        tmp_msg = None
        for msg in other.messages:
            tmp_msg = self.add(msg)
        return tmp_msg

    def __add__(self, other):
        tmp_ret = self.copy()
        tmp_ret._merge(other)
        return tmp_ret

    def __iadd__(self, other):
        self._merge(other)
        return self

    def __contains__(self, item):
        if self.max_msg == item:
            return True
        return False

    def __str__(self):
        return str(self.max_msg)

    def __repr__(self):
        return 'ParseMessageHelper [%s] --> %s' % (self, self.max_status.name)


# Helper object used in football
class ParseMessageHelper(ParseSimpleMessageHelper):
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

    def __init__(self, message_lookup, parse_str, segment, local_overrides=None):
        """
        :param message_lookup:
        :param parse_str:
        :param segment:
        """
        self.segments = AutoAddDict(dict)
        self._caches = {}
        super(ParseMessageHelper, self).__init__(message_lookup=message_lookup,
                                                 parse_str=parse_str,
                                                 segment=segment,
                                                 local_overrides=local_overrides)

    def copy(self):
        tmp_ret = self.__class__(self.message_lookup, self.parse_str, self.current_segment, local_overrides=self.local_overrides)
        tmp_ret.segments = deepcopy(self.segments)
        tmp_ret.max_status = self.max_status
        tmp_ret.max_length = self.max_length
        tmp_ret.max_msg = self.max_msg
        return tmp_ret

    def _add_new(self, msg_key_obj, begin=0, length=0, note=None, **kwargs):
        try:
            tmp_msg = self.segments[msg_key_obj.seg_key][msg_key_obj.msg_key]
        except KeyError:
            tmp_msg = self.message_lookup(msg_key_obj, local_overrides=self.local_overrides)
            tmp_msg.message_helper = self
            self.segments[msg_key_obj.seg_key][msg_key_obj.msg_key] = tmp_msg
        tmp_msg.instances.add(begin=begin, length=length, note=note)
        self.update_max(msg_key_obj, length, tmp_msg.status)

        return tmp_msg

    def _add_msg(self, message, begin=0, length=0):
        if message.key not in self.segments[message.segment_key]:
            message.message_helper = self
            self.segments[message.segment_key][message.key] = message

        for i in message:
            i.message = message

        self.update_max(message.key_obj, length, message.status)
        return message

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
        if key is not None and not matched:
            raise KeyError('Message %r not found' % key)

        if position is not None and not indexed:
            raise IndexError('Message %r not found at position %s' % (key, str(position)))

    def get_message(self, segment, message=None):
        ms_kwargs = make_message_key(segment, message, default_segment=self.current_segment)
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
        tmp_ret = {}
        if not inc_message_key and not inc_segment_key:
            for i in self.items(key):
                tmp_ret[i.key_obj] = None
            return list(tmp_ret)
        elif inc_message_key and inc_segment_key:
            tmp_key = 'long_key'
        elif inc_segment_key:
            tmp_key = 'segment_key'
        else:
            tmp_key = 'key'
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

    def __contains__(self, item):
        for m in self.messages:
            if m.key_match(item):
                return True
        return False

    def __str__(self):
        return self.get_output('seg_keys', join=', ')

    def __repr__(self):
        return 'ParseMessageHelper [%s] --> %s' % (self, self.max_status.name)
'''
'''
# List of instance Objects, used by ParseMessage
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


# Message object returned by lookup, passed to MessageHelper
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
    _compare_fields = ('status', 'key_obj')
    _compare_caps_sensitive = False

    def __init__(self, message_lookup, message, **kwargs):
        self.message_lookup = message_lookup
        self.message_helper = None
        self.segment = message.segment
        self.message = message
        self.key_obj = KeyObj(self.segment.key, message.key)
        self.status = None
        self.instances = InstanceList(self)
        for k, i in kwargs.items():
            setattr(self, k, i)

        self._field_cache = {}

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

    def __str__(self):
        return self.get_str('long_key')

    def __repr__(self):
        return 'MessageObject(%s) -> %s' % (self.__str__(), self.status.name)

    def __bool__(self):
        return self.status != STATUS_CODES.ERROR

    def __len__(self):
        return len(self.instances)

    def __iter__(self):
        for i in self.instances:
            yield i
'''
'''
# An instance of a message, used by ParseMessage
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
        return self.message.status != STATUS_CODES.ERROR
'''

'''
# Reference Record used by MessageLookup
class ParseRefRec(object):
    def __init__(self, key, **kwargs):
        self.key = key
        self.name = kwargs.get('name', key.replace('-', ' ').replace('_', ' ').title())
        self.description = kwargs.get('description', '')
        self.url = kwargs.get('url', '')
        self.text = kwargs.get('text', '')

    def __repr__(self):
        return self.name

    def update(self, **kwargs):
        for k, i in kwargs.items():
            setattr(self, k, i)

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
'''


class PositionObject(CompareFieldMixin):

    def __init__(self, begin=0, length=0, note=''):
        self.begin = begin
        self.length = length
        self.end = begin + length
        self.note = note or ''

    def at(self, position):
        return self.begin <= position <= self.end

    __contains__ = at

    def __str__(self):
        return '%s / %s' % (self.begin, self.length)

    @property
    def get_slice(self):
        return slice(self.begin, self.end)

    @property
    def get_range(self):
        return range(self.begin, self.end)

    def __iter__(self):
        for i in self.get_range:
            yield i

    @property
    def get_set(self):
        return set(self.get_range)

    @property
    def items(self):
        return self.begin, self.length

    @staticmethod
    def _compare_eng_(self_items, other_items):
        for a, b in zip(make_list(self_items), make_list(other_items)):
            if a < b:
                return -1
            elif a > b:
                return 1
        return 0

    def _compare_(self, other, compare_fields=None):
        if isinstance(other, int):
            return self._compare_eng_(self.begin, other)
        if isinstance(other, (list, tuple)):
            return self._compare_eng_((self.begin, self.length), other)
        if isinstance(other, self.__class__):
            return self._compare_eng_((self.begin, self.length), (other.begin, other.length))

    def get_dict(self, **kwargs):
        kwargs.update(
            begin=self.begin,
            length=self.length,
            end=self.end,
            note=self.note)
        return kwargs

    def output(self, template='', **msg_template_kwargs):
        """
        printed output:
            instance_template keywords:
                begin
                length
                end
                note
                (+ msg template keywords)
        """
        return template.format(**self.get_dict(**msg_template_kwargs))

    def __repr__(self):
        return '%s, %s' % (self.begin, self.length)


class PositionList(object):

    def __init__(self):
        self.positions = []
        self.begins = {}
        self.position_index = {}
        self.max_position = None
        self.max_begin = None
        self.empty = True
        self.default_pos = PositionObject(0, 0, 'No Records')

    def add(self, begin, length=0, note=None):
        if isinstance(begin, PositionObject):
            tmp_pos = begin
        elif isinstance(begin, (list, tuple, self.__class__)):
            for p in begin:
                self.add(p)
            return
        else:
            tmp_pos = PositionObject(begin, length, note)
        self.positions.append(tmp_pos)
        self._set_pos(tmp_pos)

    def _set_pos(self, position):
        if position == (0, 0):
            self.position_index = self.position_index | {0}
        else:
            self.position_index = self.position_index | position.get_set
        if self.max_position is None:
            self.max_position = position
        else:
            self.max_position = max(self.max_position, position)

    def at(self, position, as_begin=False):
        return position in self.position_index




class MessageObject(CompareFieldMixin):
    _compare_fields = ('status', 'key', 'max_position')

    def __init__(self, key=None, name=None, description='', status=None, references=None, begin=0, length=0, note='',
                 msg_lookup=None, positions=None):
        self.msg_lookup = msg_lookup
        self.positions = []
        self.position_index = set()
        self.max_position = None
        self.key = key
        self.name = name or str(key).replace('_', ' ').replace('.', ' - ')
        self.status = status or STATUS_CODES.ERROR
        self.description = description
        self._references = references or set()
        self._ref_cache = None
        if positions:
            for p in positions:
                self.add_pos(*p)
        else:
            self.add_pos(begin, length, note)

    def references(self):
        if not self._ref_cache:
            self._ref_cache = self.msg_lookup.get_ref(self._references)
        return self._ref_cache

    def add_pos(self, begin, length=0, note=None):
        if isinstance(begin, PositionObject):
            tmp_pos = begin
        elif isinstance(begin, (list, tuple)):
            for p in begin:
                self.add_pos(p)
            return
        else:
            tmp_pos = PositionObject(begin, length, note)
        self.positions.append(tmp_pos)
        self._set_pos(tmp_pos)

    def _set_pos(self, position):
        if position == (0, 0):
            self.position_index = self.position_index | {0}
        else:
            self.position_index = self.position_index | position.get_set
        if self.max_position is None:
            self.max_position = position
        else:
            self.max_position = max(self.max_position, position)

    def at(self, position):
        return position in self.position_index

    @property
    def _position_list(self):
        tmp_ret = []
        for p in self.positions:
            tmp_ret.append(p.items)
        return tmp_ret

    def copy(self, clear=True):
        if clear:
            tmp_pos_list = None
        else:
            tmp_pos_list = self._position_list

        return self.__class__(
            self.key,
            self.name,
            description=self.description,
            references=self._references,
            positions=tmp_pos_list)
    __copy__ = copy

    def remove(self, position=None, use_begin=False):
        if position is None:
            self.positions.clear()
        else:
            remove_indexes = []
            if use_begin:
                for index, item in enumerate(self.positions):
                    if item.begin == position:
                        remove_indexes.append(index)
            else:
                for index, item in enumerate(self.positions):
                    if position in item:
                        remove_indexes.append(index)
            if not remove_indexes:
                raise IndexError('%s not in list' % position)

        if not self.positions:
            self.add_pos(0, 0)
        self.position_index.clear()
        self.max_position = None
        for pos in self.positions:
            self._set_pos(pos)

    def key_match(self, key=None, position=None):
        if key is not None:
            if not key == self.key:
                return False
        if position is None:
            return True
        return position in self.position_index

    def get_dict(self,
                 key=None,
                 position=None,
                 keys=None,
                 reference_format=None,
                 instance_format=None):
        """
         printed output:
             message_template keywords:
                 full_key
                 segment_key
                 message_key
                 name
                 description
                 status
                 references (only if reference template != None)
                 instances (only if instance template != None)

             reference_template keywords:
                 url
                 name
                 description
                 key

             instance_template keywords:
                 begin
                 length
                 end
                 note
                 (+ msg template keywords)

         default templates:
             message_template = '{message_key}
         """
        if not self.key_match(key, position):
            return None

        tmp_ret = dict(
            full_key=str(self.key),
            segment_key=self.key.key1,
            message_key=self.key.key2,
            name=self.name,
            description=self.description,
            status=self.status.name)

        if keys is None or 'references' in keys:
            if reference_format is None:
                raise AttributeError('Reference list cannot be added without reference format')
            reference_format = make_list_formatter(reference_format)
            for r in self.references():
                reference_format(r)
            tmp_ret['references'] = reference_format.as_str()

        if keys is None or 'instances' in keys:
            if instance_format is None:
                raise AttributeError('Instance list cannot be added without instance format')
            instance_format = make_list_formatter(instance_format)
            for p in self.positions:
                instance_format.append(p.get_dict(**tmp_ret))
            tmp_ret['instances'] = instance_format.as_str()

        return tmp_ret

    def output(self,
               message_format='{full_key}',
               key=None,
               position=None,
               reference_format=None,
               instance_format=None):
        """
        printed output:
            message_template keywords:
                full_key
                segment_key
                message_key
                name
                description
                status
                references (only if reference template != None)
                instances (only if instance template != None)

            reference_template keywords:
                url
                name
                description
                key

            instance_template keywords:
                begin
                length
                end
                note
                (+ msg template keywords)

        default templates:
            message_template = '{message_key}
        """

        tmp_msg_keys = find_keys(message_format)

        tmp_msg_kwargs = self.get_dict(
            key,
            position=position,
            keys=tmp_msg_keys,
            reference_format=reference_format,
            instance_format=instance_format)

        return message_format.format(**tmp_msg_kwargs)

    def __repr__(self):
        tmp_msg_temp = '{full_key} [{instances}]'
        tmp_inst_temp = '({begin}, {length})'
        return self.output(tmp_msg_temp, instance_format=tmp_inst_temp)

    def __contains__(self, item):
        return item in self.position_index

    def __str__(self):
        return str(self.key)

    def __bool__(self):
        return self.status != STATUS_CODES.ERROR

    def __len__(self):
        if self.max_position is None:
            return 0
        return len(self.positions)

    

class SinpleMessageHelper(object):
    """
    PMH = SimpleMessageHelper(message_lookup, parse_string, segment_definition or key, override_definitions)

    add via string:
        PMH('key')                           #  position = 0, length = 0
        PMH('key', position)                 # length = 0
        PMH('key', position, length)
        PMH('key', position, length, note)   # adds a note to the msg

    add via dict (with definition):
        PMH({'key': 'key', ...}, position, length)

    add definition:
        PMH.define({'key': 'key',...}, 'key', ...}

    check if contains:
        'key' in PMH

    check if contains at position:
        PMH.at('key', position) == [True/False]

    combine:
        PMH += PMH_2

    combine into new:
        PMH_3 = PMH + PMH_2

    remove key:
        PMH.remove('key')  # if no position, removes all positions
        PMH.remove('key', position)  # if position == -1, removes last key

        PMH.remove('segment_key.*')  # if msg = * and no position removes all messages in that segment
        PMH.remove('*.msg_key')  # if segment = *, and no position, removes all messages of that key in all segments

    list keys:
        PMH.keys(show_position, show_length)
            [('key', position, length), (key, position, length), ...]

        PMH.keys(show_position, combine_like=True, show_length)
            [('segment_key.msg_key', [(position, length), (position, length)]),
             ('segment_key.msg_key', [(position, length)]), ...]


    list_objects:
        PMH.items() == [msg_obj, msg_pbj, ...]
        for item in PMH

    get_object:
        PMH.get(key, position)
            * if no position, gets last message
            * if no args, gets worst msg

    printed output:
        PMH.get_output(key, template='template', join='join_string', header='', footer='')
            * ordered by:
                status (worst to best)
                position (lowest to highest)
                length (shortest to longest)
                alpha (segment_key / msg_key)

    bool:
        if PMH:   # returns true if worst code == OK or WARNING

    len:
        len(PMH)   #  counts messages

    """

    def __init__(self, message_lookup, parse_string, default_segment, override_definitions=None):
        """
        PMH = SimpleMessageHelper(message_lookup, parse_string, segment_definition or key, override_definitions)
        """
        self._message_lookup = message_lookup
        self._parse_string = parse_string
        self._default_segment = default_segment
        self._override_definitions = override_definitions
        self.max_message = None
        self.last_message = None

    def __call__(self, *args, begin=0, length=0, note=None):
        """
        can add:
            'key', 'key', 'key'
            {'key': 'key', **key_definition}
            MessageObject
            MessageHelper
        """
        if not args:
            raise AttributeError('At least one argument (KEY) must be passed')
        for arg in args:
            if isinstance(arg, str):
                arg = self._key_handler(arg)
                tmp_rec = self._message_lookup(arg, begin=begin, length=length, note=note, overrides=self._override_definitions)
                # tmp_rec = MessageObject(begin=begin, length=length, note=note, **tmp_rec)
                self._add_mo(tmp_rec)
                return tmp_rec
            elif isinstance(arg, dict):
                arg['key'] = self._key_handler(arg['key'])
                self.define(arg)
                # tmp_rec = self._message_lookup(arg['key'])
                # tmp_rec = MessageObject(begin=begin, length=length, note=note, **tmp_rec)
                tmp_rec = self._message_lookup(arg['key'], begin=begin, length=length, note=note, overrides=self._override_definitions)
                self._add_mo(tmp_rec)
                return tmp_rec
            elif isinstance(arg, self.__class__):
                for item in arg:
                    self(item)
                return arg.items()
            elif isinstance(arg, MessageObject):
                self._add_mo(arg)
                return arg

    def _add_mo(self, msg_obj):
        if self.max_message is None:
            self.max_message = msg_obj
        else:
            if self.max_message.key == msg_obj.key:
                if len(msg_obj) > 0:
                    self.max_message.add_pos(msg_obj.positions)
            else:
                self.max_message = min(self.max_message, msg_obj)
        self.last_message = self.max_message
        return msg_obj

    def _key_handler(self, key):
        if key is None:
            return key
        if isinstance(key, str) and '.' not in key:
            key = self._default_segment + '.' + key

        return KeyObj.make_key(key, _key1_default=self._default_segment)

    def define(self, *messages):
        """
        add definition:
            PMH.define({'key': 'key',...}, 'key', ...}
        """
        self._message_lookup.update(*messages, default_key1=self._default_segment)

    def __contains__(self, item):
        if self.max_message is None:
            return item is None
        item = self._key_handler(item)
        return self.max_message.key == item

    def at(self, key=None, position=None):
        key = self._key_handler(key)
        if position is None:
            return key in self
        else:
            for item in self:
                if item.key_match(key=key, position=position):
                    return True
        return False

    def copy(self):
        tmp_item = self.__class__(
            message_lookup=self._message_lookup,
            parse_string=self._parse_string,
            default_segment=self._default_segment,
            override_definitions=self._override_definitions)
        tmp_item.max_message = self.max_message
        return tmp_item
    __copy__ = copy

    def __iadd__(self, other):
        self(other)
        return self

    def __add__(self, other):
        tmp_ret = self.copy()
        tmp_ret(other)
        return tmp_ret

    def items(self, key=None, position=None, raises=False):
        """
        list_objects:
            PMH.items() == [msg_obj, msg_pbj, ...]
            for item in PMH

        """
        found_msg = False
        if self.max_message is not None:
            key = self._key_handler(key)
            if self.max_message.key_match(key=key, position=position):
                found_msg = True
                yield self.max_message
            if not found_msg and raises:
                if self.max_message.key == key:
                    raise IndexError('Position %s not found' % position)
                else:
                    raise KeyError('Key %s not found' % key)
        elif raises:
            raise KeyError('No messages')

    __iter__ = items

    def remove(self, key=None, position=None, raises=False):
        """
        remove key:
            PMH.remove('key')  # if no position, removes all positions

            PMH.remove('segment_key.*')  # if msg = * and no position removes all messages in that segment
            PMH.remove('*.msg_key')  # if segment = *, and no position, removes all messages of that key in all segments
        """
        key = self._key_handler(key)
        if self.max_message is not None:
            if self.max_message.key_match(key=key, position=position):
                if position is not None:
                    self.max_message.remove(position)
            elif key is not None:
                raise KeyError('Key %s not found' % key)
            elif position is not None:
                raise IndexError('Position %s not found' % position)

            if position is None or len(self.max_message) == 0:
                self.max_message = None
                self.last_message = None

        elif raises:
            raise KeyError('No messages')


    def keys(self, key=None, position=None, as_string=False):
        """
        list_keys:
            PMH.items() == [key, key, key, ...]
        """
        if as_string:
            for item in self.items(key=key, position=position):
                yield str(item.key)
        else:
            for item in self.items(key=key, position=position):
                yield item.key

    def get(self, key=None, position=None):
        """
        get_object:
            PMH.get(key, position)
                * if no position, gets worst msg
                * if no args, gets worst msg
                * if no key, gets worst at that position
        """
        if self.max_message is None:
            return None
        else:
            key = self._key_handler(key)
            try:
                return min(self.items(key=key, position=position))
            except ValueError:
                return None

    def output(self, key=None, position=None,
               message_format='{message_key}',
               reference_format=None,
               instance_format=None,
               segment_format='{segment_key} ({messages})'):

        """
        printed output:
            PMH.output(key, template='template', join='join_string', header='', footer='')
                * ordered by:
                    status (worst to best)
                    position (lowest to highest)
                    length (shortest to longest)
                    alpha (segment_key / msg_key)

            segment_template keywords:
                segment_key
                message_count
                messages

            message_template keywords:
                full_key
                segment_key
                message_key
                name
                description
                status
                references (only if reference template != None)
                instances (only if instance template != None)

            reference_template keywords:
                url
                name
                description
                key

            instance_template keywords:
                begin
                length
                end
                note
                (+ msg template keywords)

        default templates:
            segment_template = '{segment_key}( {messages} )'
            message_template = '{message_key}
        """
        if segment_format is None and message_format is None:
            raise AttributeError('You must specify a format for either the segment or messages')

        message_format = make_list_formatter(message_format)
        segment_format = make_list_formatter(segment_format)
        reference_format = make_list_formatter(reference_format)
        instance_format = make_list_formatter(instance_format)

        if segment_format is None:
            for i in self.items(key, position=position):
                message_format.append(i.get_dict(keys=message_format.keys,
                                                 reference_format=reference_format,
                                                 instance_format=instance_format))

            return str(message_format)
        else:
            tmp_segs = {}
            for i in self.items(key, position=position):
                if i.key.key1 in tmp_segs:
                    tmp_segs[i.key.key1].append(i)
                else:
                    tmp_segs[i.key.key1] = [i]
            tmp_seg_list = list(tmp_segs.keys())
            tmp_seg_list.sort()
            for s in tmp_seg_list:
                message_format.clear()
                for i in tmp_segs[s]:
                    message_format.append(i.get_dict(keys=message_format.keys,
                                                     reference_format=reference_format,
                                                     instance_format=instance_format))
                segment_format.append(dict(
                    segment_key=s,
                    message_count=len(message_format),
                    messages=message_format.as_str()))

            return segment_format.as_str()

    """
        tmp_ret = []
        if header:
            tmp_ret.append(header)
            tmp_ret.append('\n')

        tmp_messages = []
        if segment_template is None:
            for i in self.items(key, position=position):
                tmp_messages.append(i.output(template=message_template, reference_template=reference_template,
                                             instance_template=instance_template, reference_join=reference_join,
                                             instance_join=instance_join))
            tmp_ret.append(message_join.join(tmp_messages))
        else:
            tmp_segs = {}
            for i in self.items(key, position=position):
                if i.key_obj.key1 in tmp_segs:
                    tmp_segs[i.key_obj.key1].append(i)
                else:
                    tmp_segs[i.key_obj.key1] = [i]
            tmp_seg_list = list(tmp_segs.keys())
            tmp_seg_list.sort()
            for s in tmp_seg_list:
                seg_msgs = []
                for i in tmp_segs[s]:
                    seg_msgs.append(i.output(template=message_template, reference_template=reference_template,
                                             instance_template=instance_template, reference_join=reference_join,
                                             instance_join=instance_join))
                seg_rec = segment_template.format(
                    segment_key=s,
                    message_count=len(seg_msgs),
                    messages=message_join.join(seg_msgs))
                tmp_messages.append(seg_rec)
            tmp_ret.append(segment_join.join(tmp_messages))

        if footer:
            tmp_ret.append('\n')
            tmp_ret.append(footer)

        return ''.join(tmp_ret)
        """
    def __bool__(self):
        """
        if PMH:   # returns true if worst code == OK or WARNING
        """
        return self.max_message is not None

    def __len__(self):
        """
        len(PMH)   #  counts messages
        """
        if self.max_message is None:
            return 0
        return 1

    def __str__(self):
        return self.output()

    def __repr__(self):
        return self.output(
            message_format='{message_key} {instances}',
            instance_format='({begin}, {length})',
            segment_format='{segment_key} [{messages}]')


class FullMessageHelper(SinpleMessageHelper):
    """
    PMH = SimpleMessageHelper(message_lookup, parse_string, segment_definition or key, override_definitions)

    add via string:
        PMH('key')                           #  position = 0, length = 0
        PMH('key', position)                 # length = 0
        PMH('key', position, length)
        PMH('key', position, length, note)   # adds a note to the msg

    add via dict (with definition):
        PMH({'key': 'key', ...}, position, length)

    add definition:
        PMH.define({'key': 'key',...}, 'key', ...}

    check if contains:
        'key' in PMH

    check if contains at position:
        PMH.at('key', position) == [True/False]

    combine:
        PMH += PMH_2

    combine into new:
        PMH_3 = PMH + PMH_2

    remove key:
        PMH.remove('key')  # if no position, removes all positions
        PMH.remove('key', position)  # if position == -1, removes last key

        PMH.remove('segment_key.*')  # if msg = * and no position removes all messages in that segment
        PMH.remove('*.msg_key')  # if segment = *, and no position, removes all messages of that key in all segments

    list keys:
        PMH.keys(show_position, show_length)
            [('key', position, length), (key, position, length), ...]

        PMH.keys(show_position, combine_like=True, show_length)
            [('segment_key.msg_key', [(position, length), (position, length)]),
             ('segment_key.msg_key', [(position, length)]), ...]


    list_objects:
        PMH.items() == [msg_obj, msg_pbj, ...]
        for item in PMH

    get_object:
        PMH.get(key, position)
            * if no position, gets last message
            * if no args, gets worst msg

    printed output:
        PMH.get_output(key, template='template', join='join_string', header='', footer='')
            * ordered by:
                status (worst to best)
                position (lowest to highest)
                length (shortest to longest)
                alpha (segment_key / msg_key)

    bool:
        if PMH:   # returns true if worst code == OK or WARNING

    len:
        len(PMH)   #  counts messages

    """

    def __init__(self, message_lookup, parse_string, default_segment, override_definitions=None):
        super(FullMessageHelper, self).__init__(message_lookup, parse_string, default_segment,
                                                override_definitions=override_definitions)
        self.messages = {}
        self._message_order = []

    def _add_mo(self, msg_obj):
        super(FullMessageHelper, self)._add_mo(msg_obj)
        self.messages[msg_obj.key] = msg_obj
        self._message_order.append(msg_obj.key)

    def __contains__(self, item):
        item = self._key_handler(item)
        return item in self.messages

    def items(self, key=None, position=None):
        """
        list_objects:
            PMH.items() == [msg_obj, msg_pbj, ...]
            for item in PMH

        """
        for item in self.messages:
            if item.key_match(key=key, position=position):
                yield item
    __iter__ = items

    def remove(self, key=None, position=None):
        """
        remove key:
            PMH.remove('key')  # if no position, removes all positions
            PMH.remove('key', position)  # if position == -1, removes last key

            PMH.remove('segment_key.*')  # if msg = * and no position removes all messages in that segment
            PMH.remove('*.msg_key')  # if segment = *, and no position, removes all messages of that key in all segments

        """
        rem_items = []
        fix_max = False
        for item in self.items(key, position=position):
            if position is None:
                rem_items.append(item.key)
                self._message_order.remove(item.key)
                if item.key == self.max_message.key:
                    fix_max = True
            else:
                try:
                    item.remove(position)
                except ValueError:
                    pass
                if len(item) == 0:
                    rem_items.append(item.key)
                    self._message_order.remove(item.key)
                    if item.key == self.max_message.key:
                        fix_max = True

        for i in rem_items:
            del self.messages[i]

        if fix_max:
            self.max_message = None
            for i in self.messages:
                if self.max_message is None:
                    self.max_message = i
                else:
                    self.max_message = max(self.max_message, i)
    __del__ = remove

    def get(self, key=None, position=None):
        """
        get_object:
            PMH.get(key, position)
                * if no position, gets last message
                * if no args, gets worst msg
        """
        if self.last_message.match_key(key, position=position):
            return self.last_message
        else:
            for i in self.items(key, position=position):
                return i
        return None

    def __len__(self):
        return len(self.messages)


'''
    def copy(self):
        tmp_ret = self.__class__(self.message_lookup, self.parse_str, self.current_segment, local_overrides=self.local_overrides)
        tmp_ret.segments = deepcopy(self.segments)
        tmp_ret.max_status = self.max_status
        tmp_ret.max_length = self.max_length
        tmp_ret.max_msg = self.max_msg
        return tmp_ret

    def _add_new(self, msg_key_obj, begin=0, length=0, note=None, **kwargs):
        try:
            tmp_msg = self.segments[msg_key_obj.seg_key][msg_key_obj.msg_key]
        except KeyError:
            tmp_msg = self.message_lookup(msg_key_obj, local_overrides=self.local_overrides)
            tmp_msg.message_helper = self
            self.segments[msg_key_obj.seg_key][msg_key_obj.msg_key] = tmp_msg
        tmp_msg.instances.add(begin=begin, length=length, note=note)
        self.update_max(msg_key_obj, length, tmp_msg.status)

        return tmp_msg

    def _add_msg(self, message, begin=0, length=0):
        if message.key not in self.segments[message.segment_key]:
            message.message_helper = self
            self.segments[message.segment_key][message.key] = message

        for i in message:
            i.message = message

        self.update_max(message.key_obj, length, message.status)
        return message

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
        if key is not None and not matched:
            raise KeyError('Message %r not found' % key)

        if position is not None and not indexed:
            raise IndexError('Message %r not found at position %s' % (key, str(position)))

    def get_message(self, segment, message=None):
        ms_kwargs = make_message_key(segment, message, default_segment=self.current_segment)
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
        tmp_ret = {}
        if not inc_message_key and not inc_segment_key:
            for i in self.items(key):
                tmp_ret[i.key_obj] = None
            return list(tmp_ret)
        elif inc_message_key and inc_segment_key:
            tmp_key = 'long_key'
        elif inc_segment_key:
            tmp_key = 'segment_key'
        else:
            tmp_key = 'key'
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

    def __contains__(self, item):
        for m in self.messages:
            if m.key_match(item):
                return True
        return False

    def __str__(self):
        return self.get_output('seg_keys', join=', ')

    def __repr__(self):
        return 'ParseMessageHelper [%s] --> %s' % (self, self.max_status.name)

'''


# Stores Reference Records message_lookup.
class References(UserDict):
    def __init__(self, *references):
        # self.message_lookup = message_lookup
        self.refs_added = []
        super(References, self).__init__()
        if references:
            self.add(*references)

    def add(self, *references):
        self.refs_added.clear()
        for ref in references:
            if isinstance(ref, dict):
                ref = ref.copy()
                key = ref.pop('key', None)
                if not key:
                    raise AttributeError('Unable to determine reference key reference: %r' % ref)
                self[key] = ref
            elif isinstance(ref, str):
                self[ref] = {}
            elif isinstance(ref, self.__class__):
                self.data.update(ref.data)
            elif isinstance(ref, (list, tuple)):
                self.add(*ref)
        return self.refs_added

    def get_refs(self, *refs):
        tmp_ret = []
        for ref in refs:
            ref = self._make_key(ref)
            tmp_ret.append(self.data[ref])
        return tmp_ret

    def output(self, template='', reference_join=', '):
        """
        printed output:
            reference_template keywords:
                url
                name
                description
                key
        """
        if template == '':
            return template
        tmp_ret = []
        for r in self.data:
            tmp_ret.append(template.format(**r))
        return reference_join.join(tmp_ret)

    def _make_key(self, key, key_only=True):
        tmp_ret = {
            'key': key,
            'rfc': None,
            'section': None
        }
        if key[0] == '[' and key[-1] == ']':
            key = key[1:-1].upper()
            if key[:3] != 'RFC':
                key = 'RFC' + key

            if '#' in key:
                key = key.replace('SECTION-', '')
                tmp_ret['rfc'], tmp_ret['section'] = key.split('#', maxsplit=1)
            else:
                tmp_ret['rfc'] = key
            tmp_ret['key'] = key
        if key_only:
            return tmp_ret['key']
        else:
            return tmp_ret

    def __getitem__(self, item):
        item = self._make_key(item)
        try:
            return super(References, self).__getitem__(item)
        except KeyError:
            raise KeyError('KeyError: %s not in %r' % (item, self))

    def __setitem__(self, key, value):
        if value:
            value = value.copy()
        else:
            value = {}

        tmp_key = self._make_key(key, False)
        key = tmp_key['key']
        value['key'] = key
        self.refs_added.append(key)

        if tmp_key['rfc'] is not None:
            base_template = 'https://tools.ietf.org/html/{rfc}{section}'
            section_template = '#section-{section}'

            if tmp_key['section'] is not None:
                section = section_template.format(**tmp_key)
                value['description'] = value.get('description', 'IETF %s Section %s' % (tmp_key['rfc'], tmp_key['section']))
                value['url'] = value.get('url', base_template.format(rfc=tmp_key['rfc'], section=section))
                value['name'] = value.get('name', key)
            else:
                value['name'] = value.get('name', key)
                value['description'] = value.get('description', 'IETF %s' % key)
                value['url'] = value.get('url', base_template.format(rfc=key, section=''))

        else:
            value['name'] = value.get('name', key.replace('-', ' ').replace('_', ' ').title())

        if key in self:
            self.data[key].update(value)
        else:
            self.data[key] = value


class MessageLookup(WildCardMergeDict):
    fields = (
        ('name', {'default': '', 'merge': '_merge_combine_string_by_key'}),
        ('description', {'default': '', 'merge': '_merge_combine_string', 'kwargs': {'rev_order': True}}),
        ('references', {'default': set(), 'add': '_add_reference_item', 'merge': '_merge_set_unique'}),
        ('status', STATUS_CODES.ERROR))

    def __init__(self, name, messages=None, references=None):
        self.name = name
        self.references = References(self, *make_list(references))
        super(MessageLookup, self).__init__(*make_list(messages))

    def _add_reference_item(self, key, to_dict, field_name, value, **kwargs):
        tmp_set = to_dict.get(field_name, set())
        tmp_set = tmp_set | set((self.references.add(value)))
        to_dict[field_name] = tmp_set

    def add_references(self, *references):
        self.references.add(*references)

    def get_references(self, *args):
        return self.references.get_refs(*args)

    def add_parser(self, parser_class):
        if parser_class.name is not None:
            if parser_class.references:
                self.add_references(*parser_class.references)
            if parser_class.messages:
                self.update(*parser_class.messages)

    def get(self, key, begin=0, length=0, note='', overrides=None, as_dict=False):

        key = self._key_handler(key)
        if not key.is_exact:
            raise AttributeError('Can only "GET" exact keys.  (%s passed)' % key)
        tmp_ret = self[key]
        tmp_ret['key'] = key

        self._merge_rec(key, from_rec=overrides, to_rec=tmp_ret, tmp_dict=None)

        if as_dict:
            return tmp_ret
        else:
            return MessageObject(begin=begin,
                                 length=length,
                                 note=note,
                                 msg_lookup=self,
                                 **tmp_ret)

    __call__ = get

"""
# Message Record used by MessageLookup
class ParseMessageRec(object):

    def __init__(self, key, name=None, segment=None, description=None, status=None, references=None):
        self.lookup = None
        self._ref_cache = []
        self.segment = None

        self.key = key
        self.name = name or key.replace('-', ' ').replace('_', ' ').title()
        self.description = description
        self.status = status or STATUS_CODES.ERROR
        self._set('segment', segment)
        self.references = References(message_lookup=self.segment.lookup)
        self.update(references=references)

    @property
    def key_obj(self):
        return KeyObj(self.segment.key, self.key)

    def update(self, *items, force=False, **kwargs):
        for item in items:
            if isinstance(item, dict):
                for k, i in item.items():
                    self._set(k, i, force=force)

        for k, i in kwargs.items():
            self._set(k, i, force=force)

    def _set(self, key, value, force=False):
        if value is None:
            return

        elif key == 'segment':
            self.segment = value
            self.lookup = value.lookup
            value.messages[self.key] = self
            if self._ref_cache:
                self.lookup.add(references=self._ref_cache)

        elif key == 'references':
            self.references.update(make_list(value))

        elif key == 'status':
            self.status = value

        elif key == 'name':
            self.name = value

        elif key == 'description':
            if force or self.description is None:
                self.description = value
        else:
            raise AttributeError('invalid attribute: %s' % key)

    def copy(self, **kwargs):
        return self.__class__(
            key=self.key,
            name=kwargs.get('name', self.name),
            segment=kwargs.get('segment', self.segment),
            description=kwargs.get('description', self.description),
            status=kwargs.get('status', self.status),
            references=self.references.copy())

    def __deepcopy__(self, memodict=None):
        return self.copy()

    def __repr__(self):
        return '%s (%s)' % (self.key_obj, self.status.name)


# Segment Record used by MessageLookup
class ParseSegmentRec(object):

    def __init__(self, lookup, key, name=None, description=None, references=None, messages=None, status_override=None):
        self.lookup = lookup
        self.messages = {}
        self.references = References(message_lookup=lookup)

        self.key = key
        self.name = name or key.replace('-', ' ').replace('_', ' ').title()
        self.description = description

        self.update(references=references, messages=messages, status_override=status_override)

    def get_message(self, msg_key, msg_data=None):
        msg_key_obj = make_message_key(msg_key, msg_kwargs=msg_data, as_segment=False)
        try:
            return self.messages[msg_key_obj.msg_key]
        except KeyError:
            raise MessageNotFoundError(msg_key=msg_key_obj, message_lookup=self.lookup)

    def add_message(self, msg_key, msg_data=None, force=False):
        if isinstance(msg_key, ParseMessageRec):
            if msg_key.key not in self.messages:
                msg_key.update(segment=self)
                self.messages[msg_key.key] = msg_key
                # self.lookup.msg_status.update(msg_key, force=False)
            return msg_key

        msg_key_obj = make_message_key(msg_key, msg_kwargs=msg_data, as_segment=False)
        try:
            tmp_msg = self.messages[msg_key_obj.msg_key]
        except KeyError:
            pass
        else:
            if msg_key_obj.msg_kwargs:
                tmp_msg.update(msg_key_obj.msg_kwargs)
                self.lookup.message_cache.clear()
                # self.lookup.msg_status.update(tmp_msg, force=False)
            return tmp_msg

        # if msg_key_obj.msg_key in self.lookup.segments['*'].messages:
        #     tmp_msg = self.lookup.segments['*'].messages[msg_key_obj.msg_key].copy(segment=self, **msg_key_obj.msg_kwargs)

        # else:

        if self.lookup.locked and not force:
            raise MessageListLocked(msg_key_obj.msg_key)
        tmp_msg = ParseMessageRec(msg_key_obj.msg_key, segment=self, **msg_key_obj.msg_kwargs)
        self.messages[msg_key_obj.msg_key] = tmp_msg
        # self.lookup.msg_status.update(tmp_msg, force=False)
        return tmp_msg

    @property
    def key_obj(self):
        return KeyObj(self.key)

    def update(self, *items, force=False, **kwargs):
        for item in items:
            if isinstance(item, dict):
                for k, i in item.items():
                    self._set(k, i, force=force)

        for k, i in kwargs.items():
            self._set(k, i, force=force)

    def _set(self, key, value, force=False):
        if value is None or key == 'name':
            return

        elif key == 'references':
            self.references.update(*make_list(value))

        elif key == 'messages':
            for m in make_list(value):
                self.add_message(m)

        elif key == 'status_override':
            self.lookup.set_overrides('%s.*' % self.key, default=value)

        elif key == 'description':
            if force or self.description is None:
                self.description = value
        else:
            raise AttributeError('invalid attribute: %s' % key)

    def copy(self, **kwargs):
        return self.__class__(
            kwargs.get('lookup', self.lookup),
            self.key,
            name=kwargs.get('name', self.name),
            messages=kwargs.get('messages', self.messages.copy()),
            description=kwargs.get('description', self.description),
            references=self.references.copy())

    def __deepcopy__(self, memodict=None):
        return self.copy()

    def __repr__(self):
        return self.key

"""
'''
# Used by message lookup and message helper to manage status's
class StatusHelper(object):
    """
    override_status can take any of:
      {status: (key, key, ...), status_name: key})
      key
      (key, key, key)

      -or-

      {key: status, key: status, ...} (using "as_key_dict=True")

    """

    def __init__(self, *overrides):
        self._overrides = SegmentDict()
        self.update(*overrides)

    def clear(self, *overrides):
        self._overrides.clear()
        self.update(*overrides)

    def update(self, *overrides, default=STATUS_CODES.ERROR, force=True):
        for override in overrides:
            if override is not None:
                if isinstance(override, (list, tuple)):
                    self.update(*override, default=default, force=force)
                elif isinstance(override, dict):
                    for code, items in override.items():
                        self.update(*make_list(items), default=code, force=force)
                else:
                    if force or override not in self:
                        self[override] = default

    def __setitem__(self, key, value):
        if isinstance(key, STATUS_CODES) and isinstance(value, STATUS_CODES):
            self._overrides[key] = value
        elif isinstance(key, STATUS_CODES):
            tmp_key = key
            key = value
            value = tmp_key

        if isinstance(key, ParseMessageRec):
            tmp_key = key.key_obj
            value = key.status
        else:
            tmp_key = make_message_key(key, other_ret='*')

        self._overrides[tmp_key] = value

    def get(self, key, local_overrides=None, default=STATUS_CODES.ERROR):
        local_overrides = local_overrides or {}
        if isinstance(key, (ParseMessageRec, ParseMessage)):
            if key.status is not None:
                default = key.status
            key = key.key_obj
        else:
            key = make_message_key(key)

        try:
            tmp_ret = local_overrides[key]
        except KeyError:
            try:
                tmp_ret = self._overrides[key]
            except KeyError:
                tmp_ret = default

        try:
            return local_overrides[tmp_ret]
        except KeyError:
            try:
                return self._overrides[tmp_ret]
            except KeyError:
                return tmp_ret

    __call__ = get

    def __getitem__(self, key):
        return self._overrides[key]

    def __contains__(self, key):
        return key in self._overrides
'''

'''
# Stores all messages, used for lookups
class MessageLookupOld(object):
    """
    formats:
    messages = [dict()]
    references = [dict()]
    segments = [dict]
    override_status = {status_name: (key, key, ...), status_name: key}) | key | (key, key, key)
    """
    # ms_kwargs = namedtuple('ms_kwargs', ('msg_key', 'msg_kwargs', 'seg_key', 'seg_kwargs'))

    def __init__(self,
                 name,
                 messages=None,
                 references=None,
                 segments=None,
                 error_on_warning=False,
                 override_status=None,
                 locked=True):
        self.name = name
        self.locked = False
        if error_on_warning:
            error_on_warning = {STATUS_CODES.WARNING: STATUS_CODES.ERROR}
        else:
            error_on_warning = {}
        self._defaults = dict(
            error_on_warning=error_on_warning,
            override_status=override_status,
            messages=messages or BASE_PARSING_MESSAGES,
            segments=segments or [],
            references=references or [],
        )
        self.message_cache = {}
        # self.error_on_warning = error_on_warning
        self.msg_status = StatusHelper()
        self.references = {}
        self.segments = {}

        self.clear()

        self.locked = locked

    def clear_overrides(self):
        self.msg_status.clear(self._defaults['error_on_warning'], self._defaults['override_status'])
        # self.set_error_on_warning(self._defaults['error_on_warning'])
        # self.override_status = {'*': OverrideDict()}
        # self.set_status_on_message(self._defaults['override_status'])
        self.message_cache.clear()

    def set_overrides(self, *overrides, default=STATUS_CODES.ERROR):
        self.msg_status.update(*overrides, default=default)

    def clear(self):
        # self.message_keys.clear()
        # self.sm_cache.clear()
        tmp_locked = self.locked
        self.locked = False
        self.clear_overrides()
        self.references.clear()
        self.segments.clear()
        self.add_segment('*')
        self.add(
            references=deepcopy(self._defaults['references']),
            messages=deepcopy(self._defaults['messages']),
            segments=deepcopy(self._defaults['segments']))
        self.locked = tmp_locked

    def add(self, messages=None, segments=None, references=None):
        tmp_lock = self.locked
        self.locked = False
        if references is not None:
            for item in make_list(references, deepcopy_first=True):
                self.add_reference(**_make_kwargs(item))

        if segments is not None:
            for item in make_list(segments, deepcopy_first=True):
                self.add_segment(item)

        if messages is not None:
            for item in make_list(messages, deepcopy_first=True):
                self.add_message(item)

        self.message_cache.clear()

        self.locked = tmp_lock

    def get_message(self, segment, message=None):
        msg_key_obj = make_message_key(segment, message)
        try:
            return self.get_segment(msg_key_obj).get_message(msg_key_obj)
        except MessageNotFoundError:
            tmp_msg = self.get_segment('*').get_message(msg_key_obj)
            tmp_msg = self.get_segment(msg_key_obj).add_message(tmp_msg.copy())
            return tmp_msg

    def get_segment(self, segment):
        msg_key_obj = make_message_key(segment, '*')
        try:
            return self.segments[msg_key_obj.seg_key]
        except KeyError:
            raise SegmentNotFoundError(msg_key_obj.seg_key, self)

    def add_segment(self, segment, **kwargs):
        msg_key_obj = make_message_key(segment, '*', seg_kwargs=kwargs)
        try:
            tmp_ret = self.segments[msg_key_obj.seg_key]
        except KeyError:
            if self.locked:
                raise MessageListLocked(msg_key_obj.seg_key)
            tmp_seg = ParseSegmentRec(self, msg_key_obj.seg_key, **msg_key_obj.seg_kwargs)
            self.segments[msg_key_obj.seg_key] = tmp_seg
            return tmp_seg
        else:
            if msg_key_obj.seg_kwargs:
                tmp_ret.update(msg_key_obj.seg_kwargs)
                self.message_cache.clear()
            return tmp_ret

    def add_message(self, segment, message=None, **kwargs):
        msg_key_obj = make_message_key(segment, message, msg_kwargs=kwargs)
        if self.locked and msg_key_obj.seg_key == '*':
            raise MessageListLocked(msg_key_obj.msg_key)
        tmp_ret = self.get_segment(msg_key_obj).add_message(msg_key_obj)
        return tmp_ret

    def add_reference(self, key, **kwargs):
        if isinstance(key, dict):
            key.update(kwargs)
            kwargs = key
            key = kwargs.pop('key')

        key, url = make_reference_key(key)

        if url:
            if 'url' not in kwargs:
                kwargs['url'] = url
            if 'description' not in kwargs:
                kwargs['description'] = 'See %s for more information' % key

        if key in self.references:
            tmp_ret = self.references[key]
            tmp_ret.update(**kwargs)
        elif kwargs:
            tmp_ret = ParseRefRec(key, **kwargs)
            self.references[key] = tmp_ret
        else:
            raise ReferenceNotFoundError(key, self)
        return tmp_ret

    def fix_references(self, *refs, kwargs=None):
        kwargs = kwargs or {}
        refs = make_list(refs, force_list=True) + kwargs.get('references', [])
        tmp_refs = {}
        for r in refs:
            tmp_item = self.add_reference(r)
            tmp_refs[tmp_item.key] = tmp_item
        kwargs['references'] = tmp_refs
        return kwargs

    def add_parser(self, parser_class):
        if parser_class.name is not None:
            self.add(references=parser_class.references)
            tmp_lock = self.locked
            self.locked = False
            self.add_segment(parser_class.name, description=parser_class.description)
            self.add(messages=parser_class.messages)
            self.locked = tmp_lock
    # def set_status_on_message(self, overrides, set_to=RESULT_CODES.ERROR):
    #     tmp_overrides = DictOfList()
    #     if isinstance(overrides, (list, tuple)):
    #         tmp_overrides[set_to.name].extend(overrides)
    #
    #     elif isinstance(overrides, str):
    #         tmp_overrides[set_to.name].append(overrides)
    #
    #     elif isinstance(overrides, dict):
    #         tmp_overrides.update(overrides)
    #
    #     for code, items in overrides.items():
    #         for item in items:
    #             if item in ['VALID', '*.VALID']:
    #                 continue
    #
    #             segment, message = _split_sm(item)
    #
    #             if segment == '*' and message == '*':
    #                 raise AttributeError('Error, cannot override both segment AND message keys')
    #
    #             if segment not in self.override_status:
    #                 self.override_status[segment] = OverrideDict()
    #             self.override_status[segment][message] = code
    #
    #     self.message_cache.clear()
    #
    # def set_error_on_warning(self, set_to=True):
    #     self.error_on_warning = set_to
    #     self.message_cache.clear()
    #
    # def _get_status(self, key_obj, msg_status):
    #     try:
    #         tmp_ret = self.override_status[key_obj.seg_key][key_obj.msg_key]
    #     except KeyError:
    #         try:
    #             tmp_ret = self.override_status['*'][key_obj.msg_key]
    #         except KeyError:
    #             tmp_ret = msg_status
    #     if self.error_on_warning and tmp_ret == RESULT_CODES.WARNING:
    #         return RESULT_CODES.ERROR
    #
    #     return tmp_ret

    def __call__(self, segment, message=None, local_overrides=None, **kwargs):
        msg_key_obj = make_message_key(segment, message, msg_kwargs=kwargs)
        # try:
        #     tmp_ret = self.message_cache[msg_key_obj]
        # except KeyError:
        tmp_msg = self.get_message(msg_key_obj)
        tmp_ret = ParseMessage(self, tmp_msg)
        #     self.message_cache[msg_key_obj] = tmp_ret

        # tmp_ret.copy()
        tmp_ret.status = self.msg_status.get(tmp_msg, local_overrides=local_overrides or {})

        return tmp_ret

    def get_status(self, segment, message=None, local_overrides=None):
        msg_key_obj = make_message_key(segment, message)
        status = self.msg_status.get(msg_key_obj, local_overrides=local_overrides)
        return status

    def get_reference(self, ref_key):
        try:
            return self.references[ref_key]
        except KeyError:
            return self.add_reference(ref_key)

    def iter_messages(self, segment=None):
        for i in self.segments.values():
            if segment is None or i.key == segment:
                for m in i.messages.values():
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
            max_item = self._get_max_key_len(seg.messages)
            msg_header = '    {!s:>%s} : {!r}' % max_item
            for msg_key, msg in seg.messages.items():
                tmp_ret.append(msg_header.format(msg_key, msg))
        return '\n'.join(tmp_ret)

    def len(self):
        return len(list(self.iter_messages()))
    __len__ = len
'''

MESSAGE_LOOKUP = MessageLookup('base', messages=BASE_PARSING_MESSAGES)


def get_message_lookup(msg_lookup=None):
    if msg_lookup is None:
        return MESSAGE_LOOKUP
    elif isinstance(msg_lookup, MessageLookup):
        return msg_lookup
    elif isinstance(msg_lookup, dict):
        return MessageLookup(**msg_lookup)


'''
def fix_local_overrides(*overrides):
    """
    accepts in the format of:
      - {status: (key, key, ...), status: key})
      - key
      - (key, key, key)
    """
    tmp_ret = {}
    needs_helper = False

    def add_items(add_list, add_status, item_needs_helper):
        for item in make_list(add_list):
            if not isinstance(item, STATUS_CODES):
                item = make_message_key(item)
                if not item.is_exact:
                    item_needs_helper = True
            else:
                item_needs_helper = True
            tmp_ret[item] = add_status
        return item_needs_helper

    for override in overrides:
        if override is None:
            continue

        elif isinstance(override, dict):
            for status, items in override.items():
                needs_helper = add_items(items, status, needs_helper)
        else:
            status = STATUS_CODES.ERROR
            needs_helper = add_items(override, status, needs_helper)

    if needs_helper:
        tmp_ret_obj = StatusHelper()
        tmp_ret_obj.update(tmp_ret)
        return tmp_ret_obj

    return tmp_ret
'''