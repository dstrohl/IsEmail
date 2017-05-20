
from collections import deque
from datetime import datetime, timezone


class TraceFormatManager(object):

    def __init__(self, tracer):
        # self._parsers = []
        self.tracer = tracer

    def __call__(self, *args, **kwargs):
        args = list(args)
        note = args.pop()
        self.note(*args, note=note, **kwargs)
        return self.tracer

    def __bool__(self):
        return self.tracer._ok_to_add()

    def begin(self, stage_name, *args, **kwargs):
        if self:
            self.tracer._begin_stage(stage_name=stage_name, *args, parser=self._begin_parse, **kwargs)
        return self.tracer

    def note(self, note, *args, **kwargs):
        if self:
            self.tracer._add_trace(*args, parser=self._note_parse, note=note, **kwargs)
        return self.tracer

    def end(self, *args, **kwargs):
        if self:
            self.tracer._end_stage(*args, parser=self._end_parse, **kwargs)
        return self.tracer

    def indent(self, count=1):
        self.tracer.add_indent(count=count)
        return self.tracer

    # *** Trace parsers ***********************************

    def _begin_parse(self, *args, format_str='Begin: {stage}', **kwargs):
        return format_str.format(*args, **kwargs)
    _begin_parse.name = 'Begin'

    def _end_parse(self, *args, format_str='End: {stage}', **kwargs):
        return format_str.format(*args, **kwargs)
    _end_parse.name = 'End'

    def _note_parse(self, *args, note, **kwargs):
        return note.format(*args, **kwargs)
    _note_parse.name = 'Note'


class TimerHelper(object):

    def __init__(self, tz='utc', start_time=None, end_time=None):
        if tz == 'utc':
            self.tz = timezone.utc
        else:
            self.tz = tz

        self.end_time = end_time
        self.start_time = None
        self.start(start_time)

    def start(self, start_time=None):
        if start_time is None:
            self.start_time = datetime.now(tz=self.tz)
        else:
            self.start_time = start_time
        return self

    def end(self, end_time=None):
        if end_time is None:
            self.end_time = datetime.now(tz=self.tz)
        else:
            self.end_time = end_time
        return self

    def delta(self, end_time=None):
        end_time = end_time or self.end_time or datetime.now(self.tz)
        return end_time - self.start_time

    def delta_sec(self, end_time=None):
        tmp_delta = self.delta(end_time)
        return tmp_delta.seconds

    def delta_msec(self, end_time=None):
        tmp_delta = self.delta(end_time)
        return tmp_delta.microseconds

    def delta_tsec(self, end_time=None):
        tmp_delta = self.delta(end_time)
        return tmp_delta.total_seconds()


class QueueCounterHelper(object):

    def __init__(self, start=0, max_count=None):
        self.queue_count = 0
        self.overflow_count = 0
        self.max_count = max_count
        self.overflowed = False
        self += start

    def __iadd__(self, other):
        if self.overflowed:
            self.overflow_count += other
        else:
            self.queue_count += other
            if self.max_count is not None and self.queue_count > self.max_count:
                self.overflow_count += (self.queue_count - self.max_count)
                self.queue_count = self.max_count
                self.overflowed = True
        return self

    @property
    def total_count(self):
        return self.queue_count + self.overflow_count

    @property
    def first_queue_counter(self):
        return self.overflow_count

    def __eq__(self, other):
        return self.queue_count == other

    def __gt__(self, other):
        return self.queue_count > other

    def __lt__(self, other):
        return self.queue_count < other

    def __ge__(self, other):
        return self.queue_count >= other

    def __le__(self, other):
        return self.queue_count <= other

    def __int__(self):
        return self.queue_count

    def __add__(self, other):
        return self.queue_count + other

    def __sub__(self, other):
        return self.queue_count - other

    def get_dict(self, start_line=0, end_line=999999, **kwargs):
        if start_line < 0:
            start_line += self.queue_count
        if end_line < 0:
            end_line = self.queue_count + end_line - 1
        end_line = min(end_line + 1, self.queue_count)

        kwargs.update(
            total_count=self.total_count,
            page_count=end_line - start_line,
            queue_count=self.queue_count,
            overflow_count=self.overflow_count,
            start_line=start_line + self.overflow_count + 1,
            end_line=end_line + self.overflow_count,
            line_range=range(start_line, end_line)
        )
        return kwargs


class CounterHelper(QueueCounterHelper):

    def __iadd__(self, other):
        self.queue_count += other
        return self


class TraceHelper(object):
    """
    Message fields include:
        in Header / footer:
            {total_count}
            *{start_time:%Y-%m-%d %H:%M:%S}
            *{end_time:%Y-%m-%d %H:%M:%S}
            *{end_delta:%m}
            {trace_name}
            {start_line}
            {end_line}
            {page_count}
            {overflow_count}
        Also in traces:
            {count}
            {indent}
            {indent_level}
            {parser_type}
            {stage}
            {full_stage)
            {parser_name}
            *{stage_delta}
            *{trace_delta}
            *{start_delta}
            *{time:%Y-%m-%d %H:%M:%S}



    """
    _prefix = '{indent}'
    _log_prefix = ''
    _header_message = '' \
                      'TRACE {trace_name}: ({page_count}/{total_count} records, {end_delta.seconds}.' \
                      '{end_delta.microseconds} seconds)\n' \
                      '{overflow_message}{slice_message}----------------------------------------------'
    _footer_message = '----------------------------------------------'
    _overflow_message = '(^^^ {overflow_count} lines overflowed ^^^)\n'
    _slice_message = '(*** Including lines {start_line} to {end_line} ***)\n'
    _indent_size = 4
    _indent_start = ''
    _indent_pad = ' '
    _track_time = True
    _trace_level = 0

    _format_fields = ['prefix', 'log_prefix', 'header_message', 'footer_message', 'parsers', 'default_parser',
                      'indent_size', 'indent_start', 'indent_pad', 'overflow_message', 'header_sep', 'footer_sep']

    _trace_name = 'Tracer'
    _traces = None
    _trace_format_manager = TraceFormatManager

    def __init__(self,
                 trace_level=None,
                 logger=None,
                 max_traces=None,
                 immediate_parse=False,
                 name=None,
                 tz='utc',
                 formats=None,
                 **kwargs):

        if trace_level is not None:
            self._trace_level = trace_level

        if name is not None:
            self._trace_name = name

        self.data = kwargs

        self._indents = []
        self._start_time = None
        self._named_indents = {}
        self._indent_level = 0
        self._immediate_parse = immediate_parse
        self._max_traces = max_traces
        if max_traces:
            self._traces = deque(maxlen=max_traces)
            self._counter = QueueCounterHelper(max_count=max_traces)
        else:
            self._traces = []
            self._counter = CounterHelper()

        if formats is not None:
            for key, item in formats.items():
                if key in self._format_fields:
                    setattr(self, '_' + key, item)

        self._parser_names = {}
        self._logger = logger
        self.add = self._trace_format_manager(self)
        self._indent_str = self._indent_start.ljust(self._indent_size, self._indent_pad)
        self._stage = []
        self._stage_data = []
        self._full_stage_cache = ''
        self._max_stage_length = 0
        self._max_full_length = 0
        if tz == 'utc':
            self._tz = timezone.utc
        else:
            self._tz = tz

        self._start_time = TimerHelper(tz=self._tz)
        self._last_trace_time = TimerHelper(tz=self._tz)

        self._begin_stage('----', indent=0, supress_trace=True)

    # **** Add Trace methods *********************************

    def __call__(self, *args, **kwargs):
        self.add(*args, **kwargs)
        return self

    def _ok_to_add(self):
        if self._trace_level == -1 or self._trace_level > self._indent_level:
            return True
        return False

    def _add_trace(self, *args, add_count=True, time_now=None, **kwargs):
        if add_count:
            self._counter += 1
        tmp_timehelper = TimerHelper(tz=self._tz, start_time=time_now)
        if self._immediate_parse:
            tmp_kwargs = dict(
                args=args,
                count=int(self._counter),
                indent_level=self._indent_level,
                stage=self.get_stage,
                full_stage=self.get_full_stage,
                stage_delta=self.get_stage_tsec(end_time=time_now),
                trace_delta=self._last_trace_time.delta_tsec(end_time=time_now),
                start_delta=self._start_time.delta_tsec(end_time=time_now),
                start_time=tmp_timehelper,
                time=tmp_timehelper.start_time,
                parser_name=kwargs['parser'].name,
                data=self.data)
            kwargs.update(tmp_kwargs)
            tmp_kwargs['trace_str'] = self._make_trace_str(kwargs)

            kwargs = tmp_kwargs

        else:
            kwargs.update(
                args=args,
                count=int(self._counter),
                indent_level=self._indent_level,
                stage=self.get_stage,
                full_stage=self.get_full_stage,
                stage_delta=self.get_stage_tsec(end_time=time_now),
                trace_delta=self._last_trace_time.delta_tsec(end_time=time_now),
                start_delta=self._start_time.delta_tsec(end_time=time_now),
                start_time=tmp_timehelper,
                time=tmp_timehelper.start_time,
                parser_name=kwargs['parser'].name,
                data=self.data)

        self._last_trace_time = tmp_timehelper
        self._traces.append(kwargs)

    @staticmethod
    def _make_trace_str(trace_rec):
        return trace_rec['parser'](*trace_rec['args'], **trace_rec)

    # **** Indent methods *********************************

    def set_indent(self, count=1):
        self._indent_level = count
    i = set_indent

    def add_indent(self, count=1):
        self._indent_level += count
        return self
    a = add_indent

    def sub_indent(self, count=1):
        self._indent_level -= count
        return self
    s = sub_indent

    def push(self, indent=None):
        if indent is not None:
            self._named_indents[indent] = self._indent_level
        else:
            self._indents.append(self._indent_level)
        return self

    def pop(self, indent=None, clear=False):
        if indent is not None:
            try:
                self._indent_level = self._named_indents[indent]
            except KeyError:
                raise KeyError('named indent %s does not exist' % indent)
            if clear:
                del self._named_indents[indent]
        else:
            self._indent_level = self._indents.pop()
        return self

    def _make_indent(self, indent_level):
        return self._indent_str * indent_level

    # **** Stage methods *********************************

    def _begin_stage(self, stage_name, *args, indent=1, supress_trace=False, **kwargs):
        self._stage.append(stage_name)
        self._full_stage_cache = ''
        self.push(self.get_full_stage)

        tmp_stage = dict(
            stage_name=stage_name,
            stage_counter=self._counter,
            stage_full_name=self.get_full_stage)

        if self._track_time:
            tmp_stage['stage_time'] = TimerHelper(tz=self._tz, start_time=kwargs.get('now_time', None))

        self._stage_data.append(tmp_stage)
        if not supress_trace:
            self._add_trace(*args, stage_name=stage_name, **kwargs)
        self.add_indent(indent)

    def _end_stage(self, *args, **kwargs):
        if self._stage:
            self.pop(self.get_full_stage)
            self._add_trace(*args, **kwargs)
            self._stage.pop()
            self._stage_data.pop()
            self._full_stage_cache = ''
        else:
            raise IndexError('Trying to end stage when none exist')

    @property
    def get_stage(self):
        if self._stage:
            return self._stage[-1]
        return None

    @property
    def get_full_stage(self):
        if self._full_stage_cache == '':
            self._full_stage_cache = '.'.join(self._stage[1:])
        return self._full_stage_cache

    @property
    def get_stage_data(self):
        return self._stage_data[-1]

    def get_stage_tsec(self, end_time=None):
        return self._stage_data[-1]['stage_time'].delta_tsec(end_time=end_time)

    # **** General methods *********************************

    def __bool__(self):
        return bool(self._traces)

    def __len__(self):
        if self:
            return len(self._traces)
        return 0

    def __repr__(self):
        return 'ParseTracer: (%s recs) %r' % (len(self._traces), self._trace_name)

    def output(self,
               as_string=True,
               exc_flags=None,
               start_line=0,
               end_line=999999,
               to_level=-1,
               **parser_kwargs):

        if to_level == -1:
            to_level = 9999

        exc_flags = exc_flags or []

        self._start_time.end()

        tmp_hdr_kwargs = self._counter.get_dict(
            start_line=start_line,
            end_line=end_line,
            trace_name=self._trace_name,
            data=self.data,
            start_time=self._start_time.start_time,
            end_time=self._start_time.end_time,
            end_delta=self._start_time.delta(),
            **parser_kwargs
        )

        if 'header' not in exc_flags and self._header_message:
            overflow_message = ''
            slice_message = ''

            if self._counter.overflowed:
                if 'overflow_header' not in exc_flags and self._overflow_message:
                    overflow_message = self._overflow_message.format(**tmp_hdr_kwargs)

            if start_line is not None or end_line is not None:
                if 'slice_header' not in exc_flags and self._slice_message:
                    slice_message = self._slice_message.format(**tmp_hdr_kwargs)

            tmp_ret = [self._header_message.format(
                overflow_message=overflow_message,
                slice_message=slice_message,
                **tmp_hdr_kwargs)]

        else:
            tmp_ret = []

        for index in tmp_hdr_kwargs['line_range']:
            trace = self._traces[index]
            trace['indent'] = self._make_indent(trace['indent_level'])
            if trace['indent_level'] < to_level:
                if 'trace_str' not in trace:
                    trace.update(tmp_hdr_kwargs)
                    trace['trace_str'] = self._make_trace_str(trace)
                    # self._traces[index] = tmp_dict
                    # trace = self._traces[index]
                if 'empty_lines' not in exc_flags or trace['trace_str']:
                    if 'prefix' not in exc_flags:
                        prefix = self._prefix.format(**trace)
                        tmp_ret.append(prefix + trace['trace_str'])
                    else:
                        tmp_ret.append(trace['trace_str'])

        if 'footer' not in exc_flags and self._footer_message:
            tmp_ret.append(self._footer_message.format(**tmp_hdr_kwargs))

        if as_string:
            return '\n'.join(tmp_ret)
        else:
            return tmp_ret

