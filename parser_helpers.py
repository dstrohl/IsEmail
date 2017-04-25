
__all__ = ['make_char_str', 'ParsingError', 'ParseShortResult', 'ParseResultFootball',
           'ParseFullResult', 'UnfinishedParsing', 'EmailInfo']

from meta_data import ISEMAIL_RESULT_CODES, META_LOOKUP, ISEMAIL_DOMAIN_TYPE, ISEMAIL_DNS_LOOKUP_LEVELS
from dns_functions import dns_lookup

# def _make_list(obj_in):
#     if isinstance(obj_in, (str, int)):
#         return [obj_in]
#     elif isinstance(obj_in, (list, tuple)):
#         return obj_in


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


# <editor-fold desc="Exceptions">

class ParsingError(Exception):

    def __init__(self, results, *args, **kwargs):
        self.results = results
        super().__init__(*args, **kwargs)

    def __str__(self):
        return 'ERROR: Parsing Error: %r' % self.results

    def __repr__(self):
        return str(self)


class UnfinishedParsing(Exception):
    def __str__(self):
        return 'ERROR: Not finished parsing yet, data is not available'

# </editor-fold>


class ParseHistoryData(object):
    def __init__(self, name, begin=0, length=0, from_string=''):
        self.name = name
        self.children = []
        self.begin = begin
        self.length = length
        self._base_str = from_string
        self.cleaned = False

    @property
    def is_leaf(self):
        self.clean()
        if self.children:
            return False
        return True

    def append(self, child):
        self.cleaned = False
        self.children.append(child)

    def extend(self, children):
        self.cleaned = False
        self.children.extend(children)

    def __repr__(self):
        if self.name:
            return 'History(%s)[%s, %s]' % (self.name, self.begin, self.length)
        else:
            return 'History(<unk>)[%s, %s]' % (self.begin, self.length)

    def __iter__(self):
        self.clean()
        yield self
        for i in self.children:
            for y in i:
                yield y

    def __getitem__(self, item):
        return self.children[item]

    def __contains__(self, item):
        if self.name == item:
            return True
        else:
            for c in self.children:
                if item in c:
                    return True
        return False

    def clear(self):
        self.children.clear()
        self.name = ''
        self.cleaned = False

    def clean(self, from_string=None):
        if not self.cleaned:
            self._clean(from_string=from_string)
        return self

    def _clean(self, from_string=None):
        tmp_kids = []
        for c in self.children:
            tmp_kid = c._clean(from_string=from_string)
            if tmp_kid is not None:
                if isinstance(tmp_kid, list):
                    tmp_kids.extend(tmp_kid)
                else:
                    tmp_kids.append(tmp_kid)
        self.children = tmp_kids

        if from_string is not None:
            self._base_str = from_string

        if self.name == '':
            if self.children:
                return self.children
            else:
                return None
        else:
            return self

    def __len__(self):
        self.clean()
        tmp_ret = 1
        for c in self.children:
            tmp_ret += len(c)
        return tmp_ret

    def set_str(self, from_string):
        self._base_str = from_string

    def as_string(self, depth=9999, from_string=None, with_string=False):
        self.clean()

        from_string = from_string or self._base_str

        if depth == 0:
            return ''

        if self.name:
            depth -= 1

        if self.children:
            if depth == 0:
                kids = '(...)'
            else:
                tmp_ret_list = []
                for c in self.children:
                    tmp_child = c.as_string(depth=depth, from_string=from_string, with_string=with_string)
                    if tmp_child:
                        tmp_ret_list.append(tmp_child)

                kids = '(%s)' % ', '.join(tmp_ret_list)
        else:
            kids = ''

        if with_string and self.name:
            tmp_str = '[%r]' % from_string[self.begin:self.begin + self.length]
        else:
            tmp_str = ''

        tmp_ret = '%s%s%s' % (self.name, tmp_str, kids)

        tmp_ret = tmp_ret.strip()
        if tmp_ret and tmp_ret[0] == '(':
            tmp_ret = tmp_ret[1:-1]
        return tmp_ret
    __call__ = as_string

    def __str__(self):
        return self.as_string()


class ParseFlags(object):
    def __init__(self):
        self.data = {}

    def add(self, *flags, **kwargs):
        for flag in flags:
            if isinstance(flag, dict):
                self.data.update(flag)
            elif isinstance(flag, ParseFlags):
                self.data.update(flag.data)
            else:
                self.data[flag] = None
        if kwargs:
            self.data.update(kwargs)
        return self
    __iadd__ = add
    __call__ = add

    def rem(self, *flags):
        for f in flags:
            try:
                del self.data[f]
            except KeyError:
                pass
        return self
    __del__ = rem
    __isub__ = rem

    def clear(self):
        self.data.clear()

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, item):
        return self.data[item]

    def __bool__(self):
        return bool(self.data)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        tmp_ret = []
        for d in self.data:
            if self.data[d] is None:
                tmp_ret.append(d)
            else:
                tmp_ret.append('%s(%s)' % (d, self.data[d]))

        return ', '.join(tmp_ret)

    def __repr__(self):
        return 'Flags(%s)' % str(self)


class ParseResultFootball(object):

    def __init__(self, email_obj, segment, begin):
        self.email_obj = email_obj
        self._max_length = 0
        self.results = []
        self._history = ParseHistoryData()
        # self.children = []
        self.begin = begin
        self._length = 0
        self.segment = segment
        # self.depth = 0
        # self.hist_cache = None
        self.error = False
        # self.flags = ParseFlags()
        # self.domain_type = None

    def set_length(self, length):
        self._max_length = max(length, self._max_length)
        self._length = length

    def copy(self):
        tmp_ret = self.__class__(self.email_obj, self.segment, self.begin)
        tmp_ret._length = self._length
        tmp_ret._max_length = self._max_length
        tmp_ret.results = self.results.copy()
        tmp_ret.error = self.error
        tmp_ret._history = self._history.clean(str(self.email_obj))
        return tmp_ret
    __copy__ = copy

    def set_as_element(self):
        self._history.name = self.segment

    @property
    def l(self):
        return self._length

    @property
    def length(self):
        return self._length

    def diags(self):
        tmp_ret = []
        for r in self.results:
            if r[0] not in tmp_ret:
                tmp_ret.append(r[0])
        return tmp_ret

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
            if self.email_obj.meta_data.is_error(i[0]):
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
            tmp_error = self.email_obj.meta_data.is_error(diag)
        except KeyError:
            raise AttributeError('Invalid Diagnosis: ' + diag)
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
        if self.segment:
            tmp_str = '<%s>' % self.segment
        else:
            tmp_str = '<unk>'

        if self.error:
            tmp_str += ' ERROR '

        if self.length == 0:
            tmp_str += '(not found)'
        else:
            tmp_str += '(%s)' % self.length

        if self.results:
            tmp_str += ' [%s]' % ','.join(self.diags())

        return tmp_str

    def __str__(self):
        return repr(self)

    def __bool__(self):
        if not self.error and self.length > 0:
            return True
        return False

    def __int__(self):
        return self.length

    def __len__(self):
        return len(self.results)

# <editor-fold desc="Result Objects">

class ParseShortResult(object):
    def __init__(self, email_in, parts, results):
        self.full_address = email_in
        self._full_addr_len = len(email_in)
        self._major_diag = None
        self.status = None

        if results is not None:
            tmp_res_keys = []
            for r in results:
                tmp_res_keys.append(r[0])
                self._xtra_parse_result(r)
            self._major_diag, self.status = META_LOOKUP.max_status(*tmp_res_keys)
        else:
            self.status = None
            self._major_diag = None

        if parts is None:
            self.clean_address = email_in
            self.domain = '*** PARSING ERROR ***'
            self.local = '*** PARSING ERROR ***'
            self.full_domain = '*** PARSING ERROR ***'
            self.full_local = '*** PARSING ERROR ***'
            self.clean_domain = '*** PARSING ERROR ***'
            self.clean_local = '*** PARSING ERROR ***'

        else:
            self.clean_address = '%s@%s' % (parts['clean_local_part'], parts['clean_domain_part'])
            self.domain = parts['domain_part']
            self.local = parts['local_part']
            self.full_domain = parts['full_domain_part']
            self.full_local = parts['full_local_part']
            self.clean_domain = parts['clean_domain_part']
            self.clean_local = parts['clean_local_part']

        self.error = self.status == ISEMAIL_RESULT_CODES.ERROR
        self.ok = self.status == ISEMAIL_RESULT_CODES.OK
        self.warning = self.status == ISEMAIL_RESULT_CODES.WARNING

    def _xtra_parse_result(self, result):
        pass

    def diag(self, filter=None, show_all=False, inc_cat=False, inc_diag=True, return_obj=False, return_as_list=False):
        if inc_cat:
            return META_LOOKUP[self._major_diag].category.key
        elif inc_diag:
            return self._major_diag
        else:
            return ''

    def __contains__(self, item):
        return item in self._major_diag.key

    def __repr__(self):
        if self.error:
            return 'ERROR: [%s] %s' % (self._major_diag.key, self.clean_address)
        elif self.warning:
            return 'WARN: [%s] %s' % (self._major_diag.key, self.clean_address)
        else:
            return '[%s] %s' % (self._major_diag.key, self.clean_address)

    def __str__(self):
        return self.clean_address

    def __bool__(self):
        return not self.error

    def __len__(self):
        return len(self.clean_address)

    def description(self, as_list=True, show_all=False):
        return str(META_LOOKUP[self._major_diag])

    def __getitem__(self, item):
        if item in self:
            return self._major_diag
        else:
            raise KeyError(item)


class ParseFullResult(ParseShortResult):
    def __init__(self, email_in, parts, results, history, local_comments, domain_comments, domain_type, email_info):
        self._diag_recs = {}
        self._diag_keys = []
        # self._cat_recs = MetaList()

        super().__init__(email_in, parts, results)

        self._history = history
        self._local_comments = local_comments
        self._domain_comments = domain_comments
        self.domain_type = domain_type
        self.email_info = email_info
        self._at_index = []

    def trace(self):
        return str(self.email_info.traces)

    def _xtra_parse_result(self, result):
        # tmp_result = META_LOOKUP[result[0]]
        if result[0] in self._diag_recs:
            self._diag_recs[result[0]].append(result[1:])
            self._diag_keys.append(result[0])
        else:
            self._diag_recs[result[0]] = [result[1:]]

        # if result.diag.category.key in self._cat_recs:
        #     self._cat_recs[result.diag.category.key].append(result)
        # else:
        #    self._cat_recs[result.diag.category.key] = [result]

    def _load_item_positions(self, obj):

        if isinstance(obj, ParseHistoryData):
            begin = obj.begin
            length = obj.length
            save_obj = {'obj': obj, 'key': obj.name, 'rec_type': 'Element'}
        else:
            begin = obj[1]
            length = obj[2]
            save_obj = {'obj': META_LOOKUP[obj[0]], 'key': obj[0], 'rec_type': 'Diagnostic'}

        if length == 0:
            length = 1

        end = begin + length
        if end > self._full_addr_len:
            end = self._full_addr_len

        for p in range(begin, end):
            self._at_index[p].append(save_obj)

    def _load_positional_data(self):
        self._at_index.clear()

        for i in range(self._full_addr_len):
            self._at_index.append([])

        for h in self._history:
            self._load_item_positions(h)

        for d, pos in self._diag_recs.items():
            for p in pos:
                self._load_item_positions((d, p[0], p[1]))

    def at(self, pos, ret_history=True, ret_diags=True, ret_obj=False, template=None):
        template = template or '{rec_type}: {key}'
        tmp_ret = []

        if not self._at_index:
            self._load_positional_data()

        if not self._at_index[pos]:
            return tmp_ret

        for i in self._at_index[pos]:
            if not ret_history and i['rec_type'] == 'Element':
                continue
            if not ret_diags and i['rec_type'] == 'Diagnostic':
                continue

            if ret_obj:
                tmp_ret.append(i['obj'])
            else:
                tmp_ret.append(template.format(**i))
        return tmp_ret

    def history(self, depth=999, inc_email=False):
        return self._history(depth=depth, with_string=inc_email)

    @property
    def local_comments(self):
        return list(self._local_comments.values())

    @property
    def domain_comments(self):
        return list(self._domain_comments.values())

    def diag(self, filter=None, show_all=False, inc_cat=False, inc_diag=True, return_obj=False, return_as_list=False):
        if return_obj and return_as_list:
            tmp_report = 'object_list'
        elif return_obj:
            tmp_report = 'object_dict'
        elif return_as_list:
            tmp_report = 'key_list'
        else:
            tmp_report = 'key_dict'

        return META_LOOKUP(tmp_report, self._diag_recs.keys(), filter=filter, show_all=show_all, inc_cat=inc_cat, inc_diag=inc_diag)

    def __contains__(self, item):
        # if isinstance(item, str):
        #    try:
        #        item = META_LOOKUP[item]
        #    except KeyError:
        #        return False
        return item in self._diag_recs

    def __repr__(self):
        tmp_str = super().__repr__
        tmp_str += '[%s]' % ','.join(self.diag(show_all=True))
        return tmp_str

    def report(self, report_name='formatted_string', filter=None, **kwargs):
        return META_LOOKUP(report_name, diags=self._diag_recs.keys(), filter=filter, **kwargs)

    def __getitem__(self, item):
        # if isinstance(item, str):
        #    item = META_LOOKUP[item]
        #if item in self:
        #    return item
        #else:
        #    raise KeyError('%s is not in this return object' % item.key)
        if item in self:
            return META_LOOKUP[item]
        else:
            raise KeyError('%s is not in this return object' % item.key)

    def description(self, as_list=True, show_all=True):
        if as_list:
            tmp_rep = 'desc_list'
        else:
            tmp_rep = 'formatted_string'
        return self.report(tmp_rep, show_all=show_all, inc_diag=True, inc_cat=False)
# </editor-fold>


# <editor-fold desc="Trace Objects">
class TraceObjBase(object):
    def __init__(self, tracer, stage, full_stage, indent_level, position=0, length=0):
        self.tracer = tracer
        self.stage_name = stage
        self.full_stage_name = full_stage
        self.indent = ''.rjust(indent_level * 4)
        self.position = position
        self.length = length


class TraceObjBegin(TraceObjBase):
    def __init__(self, *args, **kwargs):
        super(TraceObjBegin, self).__init__(*args, **kwargs)

    def __str__(self):
        return '%sbegin (%s): %s  scanning: ->%r<-' % (self.indent, self.position, self.stage_name, self.tracer.mid(self.position))


class TraceObjEnd(TraceObjBase):
    def __init__(self, *args, results, raise_error=False, **kwargs):
        super(TraceObjEnd, self).__init__(*args, **kwargs)
        self.results = results
        self.raise_error = raise_error
        if self.length == 0:
            self.length = results.l

    def __str__(self):
        if self.raise_error:
            tmp_raised = ' -RAISED - '
        else:
            tmp_raised = ''

        if self.results.l == 0 or self.results.error:
            return '%send      %s : %s  -- %r ' % (self.indent, tmp_raised, self.stage_name, self.results)
        else:
            return '%send       (%r) %s : %s  -- %r ' % (self.indent,
                                                         self.tracer.mid(self.position, self.results.length),
                                                         tmp_raised,
                                                         self.stage_name,
                                                         self.results)


class TraceObjNote(TraceObjBase):
    def __init__(self, *args, note, **kwargs):
        super(TraceObjNote, self).__init__(*args, **kwargs)
        self.note = note

    def __str__(self):
        if self.position == 0:
            return '%sNote : %s' % (self.indent, self.note)
        else:
            return '%sNote (%s): %s' % (self.indent, self.position, self.note)


class StageHelper(object):
    def __init__(self):
        self._stage = []

    def pop(self, count=1):
        for i in range(count):
            self._stage.pop()

    def add(self, stage):
        self._stage.append(stage)
    __call__ = add

    def __str__(self):
        return self._stage[-1]

    def __repr__(self):
        return '.'.join(self._stage)

    def __len__(self):
        return len(self._stage)

    def __getitem__(self, item):
        item *= -1
        return self._stage[item]


class ParseTracer(object):
    def __init__(self, email_in, trace_level=-1):
        self._email_in = email_in
        self._email_len = len(email_in)
        self._traces = []
        self._indent_level = 0
        self._trace_level = trace_level
        self.stage = StageHelper()

    def indent(self, count=1):
        self._indent_level += count
        return self
    i = indent
    __iadd__ = indent

    def outdent(self, count=1):
        self._indent_level -= count
        return self
    o = outdent
    __isub__ = outdent

    def can_trace(self):
        if self._trace_level == -1 or self._trace_level >= self._indent_level:
            return True
        return False
    __bool__ = can_trace

    def mid(self, begin: int = 0, length: int = 0):
        if length > 0:
            tmp_end = min(begin + length, self._email_len)
        else:
            tmp_end = self._email_len
        return self._email_in[begin:tmp_end]

    def trace_str(self):
        tmp_list = []
        for t in self._traces:
            tmp_list.append(str(t))
        tmp_ret = '\nTRACE (%s records, string: %s): \n%s\n-----------------' % (
            len(self._traces), repr(self._email_in), '\n'.join(tmp_list))
        return tmp_ret
    __str__ = trace_str

    def _trace_obj_dict(self, **kwargs):
        kwargs.update(dict(
            tracer=self,
            stage=self.stage.__str__(),
            full_stage=self.stage.__repr__(),
            indent_level=self._indent_level))
        return kwargs

    def begin(self, position):
        if self:
            tmp_trace = TraceObjBegin(**self._trace_obj_dict(position=position))
            self._traces.append(tmp_trace)
        return self

    def end(self, position, results, raise_error=False):
        if self:
            tmp_trace = TraceObjEnd(**self._trace_obj_dict(
                position=position,
                results=results,
                raise_error=raise_error))
            self._traces.append(tmp_trace)
        return self

    def note(self, note, position=0):
        if self:
            tmp_trace = TraceObjNote(**self._trace_obj_dict(position=position, note=note))
            self._traces.append(tmp_trace)
        return self

    def __call__(self, *args):
        if self:
            tmp_position = 0
            tmp_results = None
            tmp_note = None
            for a in args:
                if isinstance(a, int):
                    tmp_position = a
                elif isinstance(a, str):
                    tmp_note = a
                elif isinstance(a, ParseResultFootball):
                    tmp_results = a
            if tmp_results is not None:
                self.end(position=tmp_position, results=tmp_results)
            elif tmp_note is None and tmp_position:
                self.begin(position=tmp_position)
            if tmp_note is not None:
                self.note(note=tmp_note, position=tmp_position)
        return self

    def __len__(self):
        return len(self._traces)

    def __repr__(self):
        return 'ParseTracer: (%s recs) %r' % (len(self._traces), self._email_in)
# </editor-fold>


class EmailInfo(object):

    def __init__(self,
                 email_in=None,
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
        self.verbose = verbose
        self.raise_on_error = raise_on_error
        self.trace_level = trace_level
        self.meta_data = meta_data or META_LOOKUP

        # self._in_local_part = False
        # self._in_domain_part = False
        # self._in_crlf = False
        # self._at_in_cfws = False
        # self._near_at_flag = False

        self.at_loc = None
        self.local_comments = {}
        self.domain_comments = {}
        self.domain_type = None
        self.results = None

        self.flags = ParseFlags()

        self.email_in = None
        self.email_len = None
        self.trace = None
        self.stage = None

        if email_in is not None:
            self.setup(email_in)

    def setup(self, email_in):
        self.email_len = len(email_in)
        self.email_in = email_in
        self.trace = ParseTracer(email_in, self.trace_level)
        self.stage = self.trace.stage

        # self._in_local_part = False
        # self._in_domain_part = False
        # self._in_crlf = False
        # self._at_in_cfws = False
        # self._near_at_flag = False

    def __getitem__(self, item):
        return self.email_in[item]

    def at_end(self, position):
        return int(position) >= self.email_len

    def fb(self, position):
        return ParseResultFootball(self, str(self.stage), position)

    def __len__(self):
        return self.email_len

    def __str__(self):
        return self.email_in

    def __repr__(self):
        return 'Parse: "%s", at stage %s' % (self.email_in, self.stage)

    def mid(self, begin: int = 0, length: int = -1):
        if length >= 0:
            return self.email_in[begin:min(int(begin) + length, self.email_len)]
        else:
            return self.email_in[int(begin):]

    def remaining(self, begin, end=-1):
        for c in self.mid(begin, end):
            yield c
    __call__ = remaining

    def remaining_complex(self, begin, end=-1, count=-1, until_char=None, skip_quoted=False):
        in_qs = False
        if until_char is None:
            until_char = ''
        for i, c in enumerate(self.mid(begin, end)):
            if count != -1 and i == count:
                break
            if until_char is not None:
                if skip_quoted and c == '\\' and not in_qs:
                    in_qs = True
                    continue
                if in_qs:
                    in_qs=False
                    continue
                if c in until_char:
                    break

            yield c

    def count(self, begin, search_for, end=-1, count=-1, until_char=None, skip_quoted=False):
        tmp_ret = 0
        for c in self.remaining_complex(begin, end, count, until_char, skip_quoted):
            if c == search_for:
                tmp_ret += 1
        return tmp_ret

    def find(self, begin, search_for, end=-1, count=-1, until_char=None, skip_quoted=False):
        in_qs = False
        for i, c in enumerate(self.mid(begin, end)):
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
            if c == search_for:
                return i
        return -1

    @property
    def in_domain(self):
        return self.at_loc is not None

    @property
    def in_local(self):
        return self.at_loc is None

    def add_comment(self, football):

        if self.in_local:
            self.local_comments[football.begin] = self.mid(football.begin+1, football.length-2)
        else:
            self.domain_comments[football.begin] = self.mid(football.begin+1, football.length-2)
        return self


'''
class OldEmailParser(object):

    # test_text = ''

    def __init__(self,
                 email_in=None,
                 verbose=0,
                 trace_filter=-1,
                 raise_on_error=False,
                 dns_lookup_level=None,
                 dns_servers=None,
                 dns_timeout=None,
                 tld_list=None):
        """
        :param email_in:  the email to parse
        :param verbose:
            * 0 = only return true/false
            * 1 = return t/f + cleaned email + major reason
            * 2 = return all

        :param error_on_warning:
        :param error_on_category:
        :param error_on_diag:
        """
        self._dns_lookup_level = dns_lookup_level or ISEMAIL_DNS_LOOKUP_LEVELS.NO_LOOKUP
        self._dns_servers = dns_servers
        self._dns_timeout = dns_timeout
        self._tld_list = tld_list
        self.email_in = ''
        self.result = None
        self.position = -1
        self.email_len = 0
        # self.parsed = []
        # self.remaining = deque()
        self.email_list = []
        self.cleaned = []
        self.verbose = verbose
        # self.error_on_warning = error_on_warning
        # self.error_on_category = error_on_category
        # self.error_on_diag = error_on_diag
        self._raise_on_error = raise_on_error

        if email_in is not None:
            self.setup(email_in)

        self.stage = []
        self.trace = []
        self.trace_level = 0
        self.trace_filter = trace_filter
        self.in_local_part = False
        self.in_domain_part = False
        self.in_crlf = False

        self.at_in_cfws = False
        self.near_at_flag = False

    def __repr__(self):
        return 'Parse: "%s", at stage %s' % (self.email_in, self.stage)

    @property
    def _empty(self):
        return ParseResultFootball(self)

    def mid(self, begin: int = 0, length: int = 0):
        if length > 0:
            tmp_end = min(begin + length, self.email_len)
        else:
            tmp_end = self.email_len
        tmp_str = ''.join(self.email_list[begin:tmp_end])
        return tmp_str

    def setup(self, email_in):
        # self.result = ParseEmailResult(email_in)
        self.result = None
        self.email_len = len(email_in)
        self.email_in = email_in
        self.position = 0
        self.email_list.clear()
        self.email_list.extend(email_in)

        # self.parsed = []
        # self.remaining = deque()
        self.cleaned = []

        self.stage = []
        self.trace = []
        self.trace_level = 0

        self.in_crlf = False

    def remaining(self, position, until=None):
        position = self.pos(position)
        until = until or self.email_len
        for i in range(position, until):
            yield self.email_list[i]


    @property
    def cur_stage(self):
        return self.stage[-1]

    @property
    def stage_str(self):
        return '.'.join(self.stage)


    def parse(self,
              email_in=None,
              method=None,
              position=0,
              dns_lookup_level=None,
              raise_on_error=False,
              **kwargs):

        return_football = kwargs.pop('return_football', False)

        dns_lookup_level = dns_lookup_level or self._dns_lookup_level
        raise_on_error = raise_on_error or self._raise_on_error

        if email_in == '' or email_in is None:
            tmp_ret = self._empty
            tmp_ret('ERR_EMPTY_ADDRESS', raise_on_error=False)
            if return_football:
                if raise_on_error and tmp_ret.error:
                    raise ParsingError(tmp_ret)
                else:
                    return tmp_ret

            return tmp_ret.finish(dns_lookup_level=dns_lookup_level, raise_on_error=raise_on_error)

        if method is None:
            method = self.address_spec
        elif isinstance(method, str):
            method = getattr(self, method)

        if email_in is not None:
            self.setup(email_in=email_in)

        try:
            tmp_ret = method(position, **kwargs)
        except ParsingError as err:
            tmp_ret = err.results

        if return_football:
            if raise_on_error and tmp_ret.error:
                raise ParsingError(tmp_ret)
            else:
                return tmp_ret

        return tmp_ret.finish(dns_lookup_level=dns_lookup_level, raise_on_error=raise_on_error)

    __call__ = parse

    def this_char(self, position):
        position = self.pos(position)
        try:
            return self.email_list[position]
        except IndexError:
            return ''

    def at_end(self, position):
        position = self.pos(position)
        if position >= self.email_len:
            return True
        return False

    def find(self, position, search_for, stop_at='', skip_quoted_str=False, skip_chars=''):
        position = self.pos(position)
        tmp_ret = 0
        in_qs = False
        for c in self.remaining(position):
            tmp_ret += 1
            if skip_quoted_str and c == self.BACKSLASH and not in_qs:
                in_qs = True
            elif c not in skip_chars:
                if not in_qs:
                    if c in search_for:
                        return tmp_ret
                    if c in stop_at:
                        return -1
                else:
                    in_qs = False
        return -1

    def count(self, position, search_for, stop_for=None, length=None):
        tmp_ret = 0
        tmp_pos = position
        for c in self.remaining(position, length):
            tmp_pos += 1
            if c in search_for:
                tmp_ret += 1
            if stop_for is not None and c in stop_for:
                return tmp_ret
        return tmp_ret

    def simple_char(self,
                    position: int,
                    parse_for: str,
                    min_count: int = -1,
                    max_count: int = 99999,
                    parse_until: str = None) -> ParseResultFootball:

        tmp_ret = ParseResultFootball(self)
        for i in self.remaining(position):
            if parse_until is not None and i in parse_until:
                return tmp_ret
            if i in parse_for:
                tmp_ret += 1
                if tmp_ret == max_count:
                    break
            else:
                if tmp_ret >= min_count:
                    break
                else:
                    return self._empty

        if parse_until is not None:
            return self._empty

        if tmp_ret >= min_count:
            return tmp_ret
        return tmp_ret(set_length=0)

'''