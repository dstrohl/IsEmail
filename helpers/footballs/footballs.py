
from helpers.flag_manager import FlagHelper
from helpers.meta_data import ISEMAIL_RESULT_CODES, META_LOOKUP, ISEMAIL_DNS_LOOKUP_LEVELS
from helpers.hisatory import HistoryHelper
from helpers.exceptions import *
from helpers.tracer import TraceHelper

class ParseResultFootball(object):

    def __init__(self, email_obj, segment, begin):
        self.email_obj = email_obj
        self._max_length = 0
        self.results = []
        self._history = HistoryHelper()
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

        self.flags = FlagHelper()

        self.email_in = None
        self.email_len = None
        self.trace = None
        self.stage = None

        if email_in is not None:
            self.setup(email_in)

    def setup(self, email_in):
        self.email_len = len(email_in)
        self.email_in = email_in
        self.trace = TraceHelper(email_in, self.trace_level)
        self.stage = self.trace.stage
        self.flags._set_all(False)
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

