

from helpers.flag_manager import FlagHelper
from helpers.general import CompareFieldMixin, make_list
# from helpers.meta_data import ISEMAIL_RESULT_CODES, META_LOOKUP, ISEMAIL_DNS_LOOKUP_LEVELS
from helpers.hisatory import HistoryHelper
from ValidationParser.exceptions import *
from ValidationParser.trace_helper import TraceHelper, TraceFormatManager
from ValidationParser.parser_messages import get_message_lookup, FullMessageHelper, STATUS_CODES, \
    SinpleMessageHelper


class ParsingTracerFormatter(TraceFormatManager):

    def begin(self, stage_name, position, **kwargs):
        if self:
            self.tracer._begin_stage(
                stage_name=stage_name,
                position=position,
                parser=self._begin_parse,
                remaining=self.tracer.parse_obj.mid(position),
                **kwargs)
        return self.tracer

    def note(self, note, position=0, **kwargs):
        if self:
            self.tracer._add_trace(
                position=position,
                parser=self._note_parse,
                note=note,
                **kwargs)
        return self.tracer

    def end(self, results, raise_error=False, **kwargs):
        if self:
            self.tracer._end_stage(
                parser=self._end_parse,
                results=results,
                stage_text=str(results),
                raise_error=raise_error,
                **kwargs)
        return self.tracer

        # *** Trace parsers ***********************************

    def _begin_parse(self, *args, format_str='Begin: {stage}', **kwargs):
        format_str = 'Begin {stage}: scanning from {position}: ->{remaining!r}<-'
        return format_str.format(*args, **kwargs)
    _begin_parse.name = 'Begin'

    def _end_parse(self, *args, format_str='End: {stage}', **kwargs):
        if 'results' in kwargs:
            if isinstance(kwargs['results'], (str, list, tuple)):
                kwargs['results'] = kwargs['parsing_obj'].fb(kwargs['begin'], *make_list(kwargs['results']))
            elif isinstance(kwargs['results'], int):
                kwargs['results'] = kwargs['parsing_obj'].fb(kwargs['begin'], kwargs['results'])

        if kwargs.get('raise_error', False):
            tmp_raised = ' -RAISED - '
        else:
            tmp_raised = ''

        results = kwargs['results']

        if not results:
            format_str = 'End {stage}%s: UN-MATCHED : {results!r}' % tmp_raised
        else:
            format_str = 'End {stage}%s: Found {results.l} "{stage_text}" : {results!r}' % tmp_raised

        return format_str.format(*args, **kwargs)

    _end_parse.name = 'End'

    def _note_parse(self, *args, note, **kwargs):

        if kwargs.get('position', 0) == 0:
            format_str = 'Note : %s' % note
        else:
            format_str = 'Note (position): %s' % note
        return format_str.format(*args, **kwargs)

    _note_parse.name = 'Note'


class ParsingTracer(TraceHelper):
    _trace_name = 'Parsing Trace'
    _trace_format_manager = ParsingTracerFormatter

    def __init__(self, parse_helper, trace_level=None, logger=None, max_traces=None, immediate_parse=False,
                 name=None, tz='utc', formats=None, **kwargs):
        self.parse_obj = parse_helper
        if name is None:
            name = self.parse_obj.parse_str_len
        super().__init__(trace_level, logger, max_traces, immediate_parse, name, tz, formats, **kwargs)


class ParseResultFootball(CompareFieldMixin):
    """
    Sort order from 0 = worst to high = better.
    """

    _compare_fields = ('max_status', '_max_length', '_length', '_len_')

    def __init__(self, parse_obj, segment, begin, is_history=False):
        """
        :param parse_obj:
        :param stage:
        :param begin:
        """
        self.parse_obj = parse_obj
        # self.results = []
        self.begin = begin
        self._max_length = 0
        self._length = 0
        self.segment = segment
        if is_history:
            self._history = HistoryHelper(segment, begin=begin, from_string=parse_obj.parse_str)
        else:
            self._history = None
        if parse_obj.verbose >1:
            self._messages = ParseMessageHelper(parse_obj.message_lookup, parse_obj.parse_str, segment, parse_obj.local_msg_overrides)
        else:
            self._messages = ParseSimpleMessageHelper(parse_obj.message_lookup, parse_obj.parse_str, segment, parse_obj.local_msg_overrides)
        self._raise_on_error = self.parse_obj.raise_on_error
        self.error = False
        self.data = {}

    def set_length(self, length):
        self._max_length = max(length, self._max_length)
        self._length = length

    def copy(self):
        tmp_ret = self.__class__(self.parse_obj, self.segment, self.begin)
        tmp_ret._length = self._length
        tmp_ret._max_length = self._max_length
        tmp_ret._messages = self._messages.copy()
        if self._history is not None:
            tmp_ret._history = self._history.copy()
        else:
            tmp_ret._history = None
        tmp_ret.error = self.error
        # tmp_ret._history = self._history.clean(str(self.email_obj))
        return tmp_ret
    __copy__ = copy

    # def set_as_element(self):
    #     self._history.name = self.stage

    def set_done(self, set_history=False, pass_msg=None, fail_msg=None):
        if set_history:
            if self._history is None:
                self._history = HistoryHelper(self.segment, begin=self.begin, from_string=self.parse_obj.parse_str)

            self._history.name = self.segment
            self._history.begin = self.begin
            self._history.length = self.length
        if pass_msg and self:
            self(pass_msg)
        if fail_msg and not self:
            self(fail_msg)

    def get_history(self, depth=-1):
        return self._history.as_string(depth=depth)

    @property
    def history(self):
        if self._history is not None:
            return str(self._history)
        else:
            return 'No History'

    @property
    def l(self):
        return self._length

    @property
    def length(self):
        return self._length

    @property
    def max_length(self):
        return self._max_length

    @property
    def max_status(self):
        if self._messages.max_status == STATUS_CODES.UNKNOWN:
            if self._length == 0:
                return STATUS_CODES.ERROR
            return STATUS_CODES.OK
        return self._messages.max_status

    # @property
    # def diags(self):
    #     tmp_ret = []
    #     for r in self.results:
    #         if r[0] not in tmp_ret:
    #             tmp_ret.append(r[0])
    #     return tmp_ret
    #
    # @property
    # def max_diag(self):
    #     tmp_diag = self.diags
    #     if not tmp_diag:
    #         return None
    #     return self.parse_obj.meta_data.max_obj(*self.diags)
    #
    # @property
    # def max_diag_value(self):
    #     tmp_diag = self.max_diag
    #     if tmp_diag is None:
    #         return -1
    #     return tmp_diag.value

    def remove(self, msg, position=None):
        self._messages.remove(msg, position=position)

    def __iadd__(self, other):
        return self(other)

    def __add__(self, other):
        return self.length + int(other)
    __radd__ = __add__

    def __isub__(self, other):
        self.set_length(self.length - int(other))
        return self

    def __sub__(self, other):
        return self.length - int(other)
    __rsub__ = __sub__

    # def _set_error(self, new_error):
    #     if not self.error:
    #         if new_error:
    #             self.error = True

    def merge(self, other):
        if other is None:
            return
        if isinstance(other, ParseResultFootball):
            self.set_length(self.length + other.length)
            self._messages(other._messages)
            if self._history is None and other._history is not None:
                    self._history = HistoryHelper('', begin=self.begin, from_string=self.parse_obj.parse_str)
                    self._history.append(other._history)
            elif other._history is not None:
                self._history.append(other._history)
            self.error = not bool(self._messages)
            self.data.update(other.data)
        else:
            raise AttributeError('Cannot Merge, Not Football instance: %r' % other)

    def add_message(self, msg, begin=None, length=None, raise_on_error=None):
        if raise_on_error is None:
            raise_on_error = self._raise_on_error
        if begin is None:
            begin = self.begin
        if length is None:
            length = self.length
        # self.is_finished = False
        tmp_msg = self._messages(msg, begin=begin, length=length)
        if self.max_status == STATUS_CODES.ERROR:
            self.set_length(0)

        if not tmp_msg:
            self.error = True
            if raise_on_error:
                raise ParsingError(results=self)

        return self

    def __call__(self, *args,
                 msg_begin=None,
                 msg_length=None,
                 set_length=None,
                 raise_on_error=None):
        """
        for *args
            if string, this will be a diag str if we can look it up in diags, a segment name if not.
            if int, this will add at number to the length
            if football, this will add the football to the object
        if begin / length used, this is passed along with the message (but does not change the football settings)
        if set_length used, this will override the length and set it to this number.
        raise on error is passed to the message
        """

        for arg in args:
            if arg is None:
                return self
            elif isinstance(arg, bool):
                return self
            elif isinstance(arg, ParseResultFootball):
                self.merge(arg)
            elif isinstance(arg, int):
                self.set_length(self.length + arg)
            elif isinstance(arg, (dict, str)):
                self.add_message(arg, begin=msg_begin, length=msg_length, raise_on_error=raise_on_error)
            elif isinstance(arg, (tuple, list)):
                for i in arg:
                    self.add(i, msg_begin=msg_begin, msg_length=msg_length, raise_on_error=raise_on_error)
            else:
                raise AttributeError('Error parsing item to add to football: %r' % arg)

        if set_length is not None:
            self.set_length(set_length)

        return self
    add = __call__

    def _compare_(self, other, compare_fields=None):
        if isinstance(other, int):
            return super()._compare_(other, ('_max_length',))
        else:
            return super()._compare_(other)

    def max(self, other):
        if self >= other:
            return self
        else:
            return other

    def __contains__(self, item):
        return item in self._messages

    def __repr__(self):
        tmp_str = '[ %s / %s(%s) ' % (
            self.segment or '<unk>',
            self.max_status.name,
            self.length or '(not found)')

        if len(self._messages) > 0:
            tmp_str += '/ %s' % self._messages

        tmp_str += ' ]'

        return tmp_str

    def __str__(self):
        return self.parse_obj.mid(self.begin, self.length)

    def __bool__(self):
        return not self.error and self.length > 0

    def __int__(self):
        return self.length

    def __len__(self):
        return len(self._messages)

    @property
    def _len_(self):
        return len(self._messages)


class ParsingObj(object):

    def __init__(self,
                 parse_str=None,
                 verbose=0,
                 trace_level=None,
                 raise_on_error=False,
                 message_lookup=None,
                 local_msg_overrides=None):
        """
        :param email_in:  the email to parse
        :param verbose:
            * 0 = only return true/false
            * 1 = return t/f + major reason
            * 2 = return all

        """
        self.raise_on_error = raise_on_error
        self.verbose = verbose

        if self.verbose < 2 and trace_level is None:
            self.trace_level = 0
        else:
            self.trace_level = trace_level or -1

        self.message_lookup = get_message_lookup(message_lookup)
        self.local_msg_overrides = fix_local_overrides(local_msg_overrides)
        self.flags = FlagHelper()

        self.results = None

        self.parse_str = None
        self._parse_str_len = None
        self.trace = None
        self.full_stage = None
        self.stage_queue = []
        self.stage_id = 0
        self.limit_length = 0

        if parse_str is not None:
            self.setup(parse_str)

    def setup(self, parse_str):
        self._parse_str_len = len(parse_str)
        self.parse_str = parse_str
        self.trace = ParsingTracer(self, self.trace_level)
        self.full_stage = self.trace.get_full_stage

    @property
    def parse_str_len(self):
        if self.limit_length:
            return self.limit_length
        return self._parse_str_len

    @property
    def stage(self):
        return self.trace.get_stage

    def __getitem__(self, item):
        return self.parse_str[item]

    @property
    def trace_str(self):
        return str(self.trace)

    def begin_stage(self, stage_name, position, **kwargs):
        self.trace.add.begin(stage_name=stage_name, position=position, **kwargs)
        self.stage_id += 1
        self.stage_queue.append((self.stage_id, position))
        # print('begin stage: ', self.stage_id, ' - ', stage_name)
        return self.stage_id

    def end_stage(self, results, raise_error=False, stage_id=None, **kwargs):
        # print('end stage: ', stage_id)
        if stage_id is None:
            stage_id, begin = self.stage_queue.pop()
            self.trace.add.end(results=results, raise_error=raise_error, parsing_obj=self, begin=begin, **kwargs)
        else:
            tmp_stage_id = -1
            while self.stage_queue and tmp_stage_id != stage_id:
                tmp_stage_id, begin = self.stage_queue.pop()
                self.trace.add.end(results=results, raise_error=raise_error, parsing_obj=self, begin=begin, **kwargs)

    def note(self, note, position=0, **kwargs):
        self.trace.add.note(note=note, position=position, **kwargs)

    def at_end(self, position):
        return int(position) >= self.parse_str_len

    def is_last(self, position):
        return int(position) == self.parse_str_len

    def set_limit_len(self, length=0):
        if length < 0:
            self.limit_length = max(0, (self._parse_str_len-length))
        else:
            self.limit_length = min(length, self._parse_str_len)

    def is_ok(self, check_obj):
        if isinstance(check_obj, str):
            return self.message_lookup.get_status(self.stage, check_obj, local_overrides=self.local_msg_overrides) != STATUS_CODES.ERROR
        return bool(check_obj)

    def fb(self, position, *msgs, is_history=False):
        tmp_ret = ParseResultFootball(self, str(self.stage), int(position), is_history=is_history)
        if msgs:
            tmp_ret(*msgs)
        return tmp_ret

    def __len__(self):
        return self.parse_str_len

    def __str__(self):
        return self.parse_str

    def __repr__(self):
        return 'Parse: "%s", at stage %s' % (self.parse_str, self.stage)

    def mid(self, begin=0, length=None):
        try:
            begin = int(begin)
        except TypeError:
            begin = 0

        if length is None:
            return self.parse_str[begin:]
        else:
            return self.parse_str[begin:min(begin + length, self.parse_str_len)]

    def slice(self, begin=0, end=None):
        try:
            begin = int(begin)
        except TypeError:
            begin = 0
        try:
            end = int(end)
        except TypeError:
            end = self.parse_str_len
        return self.parse_str[begin:end]

    def remaining(self, begin, end=None, count=None, **kwargs):
        if not kwargs:
            if count is None:
                for c in self.slice(begin, end):
                    yield c
            else:
                for c in self.mid(begin, count):
                    yield c
        else:
            for c in self.remaining_complex(begin, end, count, **kwargs):
                yield c

    def remaining_complex(self, begin, end=None, count=None, until_char=None, skip_quoted=False, ret_offset=False):
        in_qs = False
        try:
            count = int(count)
        except TypeError:
            count = -1

        if until_char is None:
            until_char = ''

        for i, c in enumerate(self.slice(begin, end)):
            if count != -1 and i == count:
                break
            if until_char is not None:
                if skip_quoted and c == '\\' and not in_qs:
                    in_qs = True
                    continue
                if in_qs:
                    in_qs = False
                    continue
                if c in until_char:
                    break
            if ret_offset:
                yield i + begin, c
            else:
                yield c

    def count(self, begin, search_for, end=None, **kwargs):
        if len(search_for) > 1:
            tmp_str = list(self.remaining(begin, end, **kwargs))
            tmp_str = ''.join(tmp_str)
            return tmp_str.count(search_for)
        else:
            tmp_ret = 0
            for c in self.remaining(begin, end, **kwargs):
                if c == search_for:
                    tmp_ret += 1
            return tmp_ret

    def find(self, begin, search_for, end=None, **kwargs):
        for i, c in self.remaining_complex(begin, end, **kwargs, ret_offset=True):
            if c == search_for:
                return i
        return -1

    def next_char_in(self, begin, look_for, min_count=None, max_count=None, caps_sensitive=True, min_error_msg=None, **kwargs):
        try:
            min_count = int(min_count)
        except TypeError:
            min_count = 0

        try:
            max_count = int(max_count)
        except TypeError:
            max_count = self.parse_str_len

        if kwargs:
            looper = self.remaining(begin, **kwargs)
            if not caps_sensitive:
                looper = '.'.join(list(looper))
        else:
            looper = self.slice(begin)

        if not caps_sensitive:
            looper = looper.lower()
            look_for = look_for.lower()

        loop_count = 0
        for ch in looper:
            if loop_count == max_count:
                break
            if ch not in look_for:
                break
            loop_count += 1

        if min_count > loop_count:
            return min_error_msg or 0

        return loop_count

    def next_string_in(self, begin, look_for, min_count=None, max_count=None, caps_sensitive=True, min_error_msg=None, **kwargs):
        lf_len = len(look_for)
        if lf_len > 2 and look_for[0] == '"' and look_for[-1] == '"':
            look_for = look_for[1:-1]
            lf_len -= 2

        try:
            min_count = int(min_count)
        except TypeError:
            min_count = 0

        try:
            max_count = int(max_count)
        except TypeError:
            max_count = self.parse_str_len / lf_len

        if kwargs:
            looper = self.remaining(begin, **kwargs)
            looper = '.'.join(list(looper))
        else:
            looper = self.slice(begin)

        if not caps_sensitive:
            looper = looper.lower()
            look_for = look_for.lower()

        loop_count = 0
        ret_count = 0

        while len(looper) >= lf_len:
            if loop_count == max_count:
                break
            if looper[:lf_len] != look_for:
                break
            loop_count += 1
            ret_count += lf_len
            looper = looper[lf_len:]

        if min_count > loop_count:
            return min_error_msg or 0

        return ret_count

    def next_1_char_in(self, begin, look_for, caps_sensitive=True):
        if self.at_end(begin):
            return 0
        if caps_sensitive:
            if self[begin] in look_for:
                return 1
        else:
            look_for = look_for.upper()
            if self[begin].upper() in look_for:
                return 1

    def next(self, begin, look_for, min_count=None, max_count=None, caps_sensitive=True, min_error_msg=None, **kwargs):
        lf_len = len(look_for)
        if lf_len > 2 and look_for[0] == '"' and look_for[-1] == '"':
            return self.next_string_in(begin,
                                       look_for,
                                       min_count=min_count,
                                       max_count=max_count,
                                       caps_sensitive=caps_sensitive,
                                       min_error_msg=min_error_msg,
                                       **kwargs)
        elif min_count is not None and min_count == 1 and max_count is not None and max_count == 1 and not kwargs:
            return self.next_1_char_in(begin, look_for, caps_sensitive=caps_sensitive)

        else:
            return self.next_char_in(begin,
                                     look_for,
                                     min_count=min_count,
                                     max_count=max_count,
                                     caps_sensitive=caps_sensitive,
                                     min_error_msg=min_error_msg,
                                     **kwargs)

    __call__ = next

    def next_char(self, begin, look_for, caps_sensitive=False):
        tmp_ret = self.fb(begin)
        if caps_sensitive:
            if self[begin] == look_for:
                return tmp_ret(1)
            else:
                return tmp_ret
        else:
            if self[begin].lower() == look_for.lower():
                return tmp_ret(1)
            else:
                return tmp_ret

    #
    #
    # def in_chars(self, begin, look_for, min_count=None, max_count=None, **kwargs):
    #     tmp_ret = self.fb(begin)
    #     tmp_count = 0
    #     try:
    #         min_count = int(min_count)
    #     except TypeError:
    #         min_count = 0
    #
    #     for i in self.remaining(begin=begin, count=max_count, **kwargs):
    #         if i in look_for:
    #             tmp_count += 1
    #         else:
    #             if tmp_count > min_count:
    #                 return tmp_ret(tmp_count)
    #             else:
    #                 return tmp_ret
    #
    #     if tmp_count > min_count:
    #         return tmp_ret(tmp_count)
    #     return tmp_ret
    #
    # def is_chars(self, begin, look_for, caps_sensitive=True):
    #     tmp_ret = self.fb(begin)
    #     tmp_len = len(look_for)
    #
    #     if tmp_len > 1:
    #
    #         tmp_check = self.mid(begin, tmp_len)
    #
    #         if not caps_sensitive:
    #             tmp_check = tmp_check.lower()
    #             look_for = look_for.lower()
    #
    #         if tmp_check == look_for:
    #             tmp_ret += tmp_len
    #
    #     else:
    #
    #         if self[begin] == look_for:
    #             return tmp_ret(1)
    #
    #     return tmp_ret
    #

    def __enter__(self, length_limit):
        self.set_limit_len(length_limit)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.set_limit_len()

