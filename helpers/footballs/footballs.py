

from helpers.flag_manager import FlagHelper
from helpers.meta_data import ISEMAIL_RESULT_CODES, META_LOOKUP, ISEMAIL_DNS_LOOKUP_LEVELS
from helpers.hisatory import HistoryHelper
from helpers.exceptions import *
from helpers.tracer import TraceHelper, TraceFormatManager


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
        if kwargs.get('raise_error', False):
            tmp_raised = ' -RAISED - '
        else:
            tmp_raised = ''

        results = kwargs['results']

        if results.l == 0 or results.error:
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


class ParseResultFootball(object):

    def __init__(self, parse_obj, stage, begin):
        self.parse_obj = parse_obj
        self.results = []
        # self.children = []
        self.begin = begin
        self._max_length = 0
        self._length = 0
        self.stage = stage
        self._history = HistoryHelper(stage, begin=begin)
        # self.depth = 0
        # self.hist_cache = None
        self.error = False
        # self.flags = ParseFlags()
        # self.domain_type = None

    def set_length(self, length):
        self._max_length = max(length, self._max_length)
        self._length = length

    def copy(self):
        tmp_ret = self.__class__(self.parse_obj, self.stage, self.begin)
        tmp_ret._length = self._length
        tmp_ret._max_length = self._max_length
        tmp_ret.results = self.results.copy()
        tmp_ret.error = self.error
        # tmp_ret._history = self._history.clean(str(self.email_obj))
        return tmp_ret
    __copy__ = copy

    # def set_as_element(self):
    #     self._history.name = self.stage

    def set_history(self, stage=None, begin=None, length=None):
        if stage is not None:
            self._history.name = stage or self.stage
        if begin is not None:
            self._history.begin = begin
        if length is not None:
            self._history.length = length

    def get_history(self, depth=-1):
        return self._history.as_string(depth=depth)

    @property
    def history(self):
        return str(self._history)

    @property
    def l(self):
        return self._length

    @property
    def length(self):
        return self._length

    @property
    def diags(self):
        tmp_ret = []
        for r in self.results:
            if r[0] not in tmp_ret:
                tmp_ret.append(r[0])
        return tmp_ret

    @property
    def max_diag(self):
        tmp_diag = self.diags
        if not tmp_diag:
            return None
        return self.parse_obj.meta_data.max_obj(*self.diags)

    @property
    def max_diag_value(self):
        tmp_diag = self.max_diag
        if tmp_diag is None:
            return -1
        return tmp_diag.value

    def remove(self, diag, position=None, length=None, rem_all=False):
        rem_list = []
        tmp_range = reversed(range(len(self.results)))

        for i in tmp_range:
            if self.results[i][0] == diag:
                if rem_all:
                    rem_list.append(i)

                elif position is None:
                    rem_list.append(i)
                    break

                else:
                    if length is None and position == self.results[i][1]:
                        rem_list.append(i)
                    elif length == self.results[i][2] and position == self.results[i][1]:
                        rem_list.append(i)

        if rem_list:
            for i in rem_list:
                del self.results[i]
            self.is_finished = False
            self._refresh()
        return len(rem_list)

    def _refresh(self):
        for i in self.results:
            if self.parse_obj.meta_data.is_error(i[0]):
                self.status = ISEMAIL_RESULT_CODES.ERROR

    def __iadd__(self, other):
        if isinstance(other, int):
            self.set_length(self.length + other)
        else:
            self.merge(other)

        return self

    def __add__(self, other):
        return self.length + int(other)
    __radd__ = __add__

    def __isub__(self, other):
        self.set_length(self.length - int(other))
        return self

    def __sub__(self, other):
        return self.length - int(other)
    __rsub__ = __sub__

    def _set_error(self, new_error):
        if not self.error:
            if new_error:
                self.error = True

    def merge(self, other):
        if isinstance(other, ParseResultFootball):
            self.is_finished = False
            self.set_length(self.length + other.length)
            self._max_length = max(self._max_length, other._max_length)
            # self.status = max(self.status, other.status)
            self.results.extend(other.results)
            self._set_error(other.error)
            # if other.segment_name is not None and other.segment_name != '':
            self._history.append(other._history)

            # self._local_comments.update(other._local_comments)
            # self._domain_comments.update(other._domain_comments)

            # self.domain_type = self.domain_type or other.domain_type
            # self._parts = other._parts

            # self.at_loc = self.at_loc or other.at_loc

            # self.flags += other.flags
        else:
            raise AttributeError('Cannot Merge, Not Football instance')

    def add_diag(self, diag, begin=None, length=None, raise_on_error=False):
        if begin is None:
            begin = self.begin
        if length is None:
            length = self.length
        # self.is_finished = False
        self.results.append((diag, begin, length))

        try:
            tmp_error = self.parse_obj.meta_data.is_error(diag)
        except KeyError:
            raise AttributeError('Invalid Diagnosis: %r' % diag)
        self._set_error(tmp_error)

        if tmp_error:
            self.set_length(0)
            if raise_on_error:
                raise ParsingError(self)
        return self

    def add(self, *args,
            diag=None,
            begin=None,
            position=None,
            length=None,
            set_length=None,
            raise_on_error=False):
        """
        for *args
            if string, this will be a diag str if we can look it up in diags, a segment name if not.
            if int, this will add at number to the length
            if football, this will add the football to the object
        """
        if begin is not None:
            self.begin = begin

        if position is not None:
            self.begin = position

        if length is not None:
            self.set_length(self.length + length)

        if set_length is not None:
            self.set_length(set_length)

        if diag is not None:
            if isinstance(diag, dict):
                self.add_diag(raise_on_error=raise_on_error, **diag)
            elif isinstance(diag, (tuple, list)):
                self.add_diag(*diag, raise_on_error=raise_on_error)
            elif isinstance(diag, str):
                self.add_diag(diag, raise_on_error=raise_on_error)

        for arg in args:
            if isinstance(arg, ParseResultFootball):
                self.merge(arg)
            elif isinstance(arg, int):
                self.set_length(self.length + arg)
            elif isinstance(arg, dict):
                self.add_diag(raise_on_error=raise_on_error, **arg)
            elif isinstance(arg, (tuple, list)):
                self.add_diag(*arg, raise_on_error=raise_on_error)
            elif isinstance(arg, str):
                self.add_diag(arg, raise_on_error=raise_on_error)

        return self
    __call__ = add

    def max(self, other):
        if self and not other:
            return self

        elif other and not self:
            return other

        elif self and other:
            if self > other:
                return self
            elif other > self:
                return other
            else:
                if self.max_diag_value >= other.max_diag_value:
                    return self
                else:
                    return other

        else:  # neither self nor other
            if self._max_length > other._max_length:
                return self
            elif other._max_length > self._max_length:
                return other
            else:
                if self.max_diag_value >= other.max_diag_value:
                    return self
                else:
                    return other

    def __lt__(self, other):
        return self.length < int(other)

    def __le__(self, other):
        return self.length <= int(other)

    def __eq__(self, other):
        return self.length == int(other)

    def __ne__(self, other):
        return self.length != int(other)

    def __gt__(self, other):
        return self.length > int(other)

    def __ge__(self, other):
        return self.length >= int(other)

    def __contains__(self, item):
        for r in self.results:
            if r[0] == item:
                return True
        return False

    def __repr__(self):
        if self.stage:
            tmp_str = '<%s>' % self.stage
        else:
            tmp_str = '<unk>'

        if self.error:
            tmp_str += ' ERROR '

        if self.length == 0:
            tmp_str += '(not found)'
        else:
            tmp_str += '(%s)' % self.length

        if self.results:
            tmp_str += ' [%s]' % ','.join(self.diags)

        return tmp_str

    def __str__(self):
        return self.parse_obj.mid(self.begin, self.length)

    def __bool__(self):
        if not self.error and self.length > 0:
            return True
        return False

    def __int__(self):
        return self.length

    def __len__(self):
        return len(self.results)


class ParsingObj(object):

    def __init__(self,
                 str_in=None,
                 verbose=0,
                 trace_level=-1,
                 raise_on_error=False,
                 meta_data=None):
        """
        :param email_in:  the email to parse
        :param verbose:
            * 0 = only return true/false
            * 1 = return t/f + cleaned email + major reason
            * 2 = return all

        """
        self.verbose = verbose
        self.raise_on_error = raise_on_error
        self.trace_level = trace_level
        self.meta_data = meta_data or META_LOOKUP
        self.flags = FlagHelper()

        self.results = None

        self.parse_str = None
        self.parse_str_len = None
        self.trace = None
        self.stage = None
        self.full_stage = None

        if str_in is not None:
            self.setup(str_in)

    def setup(self, str_in):
        self.parse_str_len = len(str_in)
        self.parse_str = str_in
        self.trace = ParsingTracer(self, self.trace_level)
        self.stage = self.trace.get_stage
        self.full_stage = self.trace.get_full_stage

    def __getitem__(self, item):
        return self.parse_str[item]

    def begin_stage(self, stage_name, position, **kwargs):
        self.trace.add.begin(stage_name=stage_name, position=position, **kwargs)

    def end_stage(self, results, raise_error=False, **kwargs):
        self.trace.add.end(results=results, raise_error=raise_error, **kwargs)

    def note(self, note, position=0, **kwargs):
        self.trace.add.note(note=note, position=position, **kwargs)

    def at_end(self, position):
        return int(position) >= self.parse_str_len

    def is_last(self, position):
        return int(position) == self.parse_str_len

    def fb(self, position):
        return ParseResultFootball(self, str(self.stage), int(position))

    def __len__(self):
        return self.parse_str_len

    def __str__(self):
        return self.parse_str

    def __repr__(self):
        return 'Parse: "%s", at stage %s' % (self.parse_str, self.stage)

    def mid(self, begin: int = 0, length: int = -1):
        length = int(length)
        if length >= 0:
            return self.parse_str[begin:min(int(begin) + length, self.parse_str_len)]
        else:
            return self.parse_str[int(begin):]

    def slice(self, begin=0, end=999):
        return self.parse_str[int(begin):int(end)]

    def remaining(self, begin, end=999, count=-1, **kwargs):
        if not kwargs:
            if count == -1:
                for c in self.slice(begin, end):
                    yield c
            else:
                for c in self.mid(begin, count):
                    yield c
        else:
            for c in self.remaining_complex(begin, end, count, **kwargs):
                yield c

    __call__ = remaining

    def remaining_complex(self, begin, end=999, count=-1, until_char=None, skip_quoted=False, ret_offset=False):
        in_qs = False
        count = int(count)
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

    def count(self, begin, search_for, end=999, count=-1, until_char=None, skip_quoted=False):
        if len(search_for) > 1:
            tmp_str = list(self.remaining_complex(begin, end, count, until_char, skip_quoted))
            tmp_str = ''.join(tmp_str)
            return tmp_str.count(search_for)
        else:
            tmp_ret = 0
            for c in self.remaining_complex(begin, end, count, until_char, skip_quoted):
                if c == search_for:
                    tmp_ret += 1
            return tmp_ret

    def find(self, begin, search_for, end=999, count=-1, until_char=None, skip_quoted=False):
        for i, c in self.remaining_complex(begin, end, count, until_char, skip_quoted, ret_offset=True):
            if c == search_for:
                return i
        return -1


class EmailParsingObj(ParsingObj):

    def __init__(self,
                 str_in=None,
                 verbose=0,
                 trace_level=-1,
                 raise_on_error=False,
                 dns_lookup_level=None,
                 dns_servers=None,
                 dns_timeout=None,
                 tld_list=None,
                 meta_data=None):
        """
        :param email_in:  the email to parse
        :param verbose:
            * 0 = only return true/false
            * 1 = return t/f + cleaned email + major reason
            * 2 = return all

        """
        self.dns_lookup_level = dns_lookup_level or ISEMAIL_DNS_LOOKUP_LEVELS.NO_LOOKUP
        self.dns_servers = dns_servers
        self.dns_timeout = dns_timeout
        self.tld_list = tld_list

        self.at_loc = None
        self.local_comments = {}
        self.domain_comments = {}
        self.domain_type = None
        self.results = None

        super().__init__(str_in=str_in, verbose=verbose, trace_level=trace_level,
                         raise_on_error=raise_on_error, meta_data=meta_data)

        self.flags = FlagHelper('in_crlf', 'at_in_cfws', 'near_at_flag')

    @property
    def in_domain(self):
        return self.at_loc is not None

    @property
    def in_local(self):
        return self.at_loc is None

    def add_comment(self, football):

        if self.in_local:
            self.local_comments[football.begin] = (football.begin, football.length, self.mid(football.begin+1, football.length-2))
        else:
            self.domain_comments[football.begin] = (football.betin, football.length, self.mid(football.begin+1, football.length-2))
        return self

