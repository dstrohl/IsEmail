
from meta_data import ISEMAIL_RESULT_CODES, META_LOOKUP


def _make_list(obj_in):
    if isinstance(obj_in, (str, int)):
        return [obj_in]
    elif isinstance(obj_in, (list, tuple)):
        return obj_in


class ParsingError(Exception):

    def __init__(self, results, *args, **kwargs):
        self.results = results
        super().__init__(*args, **kwargs)


class ParseHistory(object):
    def __init__(self, parser, parent, segment_type, begin, length, depth=0):
        self.parent = parent
        self.parser = parser
        self.segment_type = segment_type
        self.begin = begin
        self.length = length
        self.children = []
        self.depth = depth

        if parent is None:
            self.full_name = segment_type
        else:
            self.full_name = '%s.%s' % (parent.full_name, segment_type)

    @property
    def is_root(self):
        return self.parent is None

    def extend(self, children):
        for c in children:
            self.add(c)

    def add(self, child):
        self.children.append(child)

    def __contains__(self, item):
        if item == self.segment_type:
            return True
        else:
            for c in self.children:
                if item in c:
                    return True
        return False

    def __str__(self):
        return self.segment_type

    @property
    def parsed_str(self):
        return self.parser.mid(self.begin, self.length)

    def long_desc(self, indent_size=4, depth=9999):
        if depth == 0:
            return ''

        hdr_with_str = '{indent}{short_name}   :   {parsed_str}'

        tmp_indent = ''.ljust(self.depth * indent_size, ' ')

        tmp_ret_children = [hdr_with_str.format(
            indent=tmp_indent,
            short_name=self.segment_type,
            parsed_str=repr(self.parsed_str))]

        for c in self.children:
            tmp_ret_children.append(c.long_desc(indent_size=indent_size, depth=depth-1))

        return '\n'.join(tmp_ret_children)

    def short_desc(self, depth=9999, inc_string=False):
        if depth == 0:
            return ''

        if not self.segment_type:
            if self.children:
                if depth == 1:
                    return '...'
                tmp_ret_list = []
                for c in self.children:
                    tmp_child = c.short_desc(depth=depth - 1, inc_string=inc_string)
                    if tmp_child:
                        tmp_ret_list.append(tmp_child)

                tmp_ret = ', '.join(tmp_ret_list)
                return tmp_ret
            else:
                return ''
        tmp_ret = self.segment_type
        if inc_string:
            tmp_ret += '[%r]' % self.parsed_str

        if self.children:

            if depth == 1:
                tmp_ret += '(...)'
            else:
                tmp_ret_list = []
                for c in self.children:
                    tmp_child = c.short_desc(depth=depth - 1, inc_string=inc_string)
                    if tmp_child:
                        tmp_ret_list.append(tmp_child)

                if tmp_ret_list:
                    tmp_ret += '('
                    tmp_ret += ', '.join(tmp_ret_list)
                    tmp_ret += ')'

        return tmp_ret

    def __repr__(self):
        return '%s  :  %r' % (self.full_name, self.parsed_str)


class ParseResultItem(object):

    def __init__(self,
                 diag,
                 begin=0,
                 length=0,
                 ):
        self.diag = META_LOOKUP[diag]
        self.begin = begin
        self.length = length

    def __str__(self):
        return self.key

    @property
    def category(self):
        return self.diag.category

    @property
    def key(self):
        return self.diag.key

    @property
    def category_name(self):
        return self.diag.category.name

    @property
    def category_value(self):
        return self.diag.category.value

    @property
    def category_description(self):
        return self.diag.category.description

    @property
    def result(self):
        return self.diag.category.result

    @property
    def value(self):
        return self.diag.value

    @property
    def description(self):
        return self.diag.longdescription

    @property
    def smtp(self):
        return self.diag.smtp.description

    @property
    def references(self):
        return self.diag.references

    @property
    def status(self):
        return self.diag.status


class ParseResultFootball(object):

    def __init__(self, parser, segment='', position=0, length=0, stage=''):
        self.parser = parser
        if length > 0:
            self.length = length
        else:
            self.length = 0

        self.results = []
        self.stage = stage
        self.status = ISEMAIL_RESULT_CODES.OK
        self.comments = []
        self.children = []
        # self.peers = []
        self.begin = position
        self.segment_name = segment
        self.depth = 0
        self.hist_cache = None

        # self._as_peer = False

        # **** Finished vars ****
        self.is_finished = False
        self.cleaned_email = None
        self.local_part = None
        self.domain_part = None
        self.cat_recs = None
        self.diag_recs = None
        self.major_diag = None
        self.major_diag_value = None

    def copy(self):
        tmp_ret = self.__class__(self.parser)
        tmp_ret.length = self.length
        tmp_ret.results = self.results.copy()
        tmp_ret.stage = self.stage
        tmp_ret.status = self.status

        # **** Finished vars ****
        if self.is_finished:
            tmp_ret.comments = self.comments.copy()
            tmp_ret.is_finished = self.is_finished
            tmp_ret.cleaned_email = self.cleaned_email
            tmp_ret.local_part = self.local_part
            tmp_ret.domain_part = self.domain_part
            if self.cat_recs is None:
                tmp_ret.cat_recs = None
            else:
                tmp_ret.cat_recs = self.cat_recs.copy()

            if self.cat_recs is None:
                tmp_ret.diag_recs = None
            else:
                tmp_ret.diag_recs = self.diag_recs.copy()

            tmp_ret.major_diag = self.major_diag
            tmp_ret.major_diag_value = self.major_diag_value
        
        return tmp_ret
    __copy__ = copy

    @property
    def l(self):
        return self.length

    def diags(self):
        if not self.is_finished:
            self.finish()
        return self.diag_recs.keys()

    def _make_history(self, depth=0, parent=None):

        tmp_children = []
        self.depth = depth

        for c in self.children:
            tmp_child = c._make_history(depth=depth+1, parent=None)
            if isinstance(tmp_child, (list, tuple)):
                tmp_children.extend(tmp_child)
            else:
                tmp_children.append(tmp_child)

        if depth == 0 or self.segment_name != 0:
            tmp_hist = ParseHistory(self.parser, parent, self.segment_name, self.begin, self.length, depth=depth)
            tmp_hist.extend(tmp_children)
            return tmp_hist
        return tmp_children

    @property
    def history(self):
        if self.hist_cache is None:
            self.hist_cache = self._make_history()
        return self.hist_cache

    def clear(self, keep_results=False):
        self.length = 0
        if not keep_results:
            self.results.clear()
            self.is_finished = False
            self._refresh()
            self.hist_cache = None
        return self

    def set_sub_segment(self):
        self.segment_name = None

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
            if META_LOOKUP.is_error(i[0]):
                self.status = ISEMAIL_RESULT_CODES.ERROR

    def __iadd__(self, other):
        if isinstance(other, int):
            self.length += other
        else:
            self.merge(other)

        return self

    def __add__(self, other):
        return self.length + int(other)
    __radd__ = __add__

    def __isub__(self, other):
        self.length -= other
        return self

    def __sub__(self, other):
        return self.length - int(other)
    __rsub__ = __sub__

    def merge(self, other):
        if isinstance(other, ParseResultFootball):
            self.is_finished = False
            self.length += other.length
            self.status = max(self.status, other.status)
            self.results.extend(other.results)

            # if other.segment_name is not None and other.segment_name != '':
            self.children.append(other)

    def add_diag(self, diag, begin=None, length=None, raise_on_error=True):
        if begin is None:
            begin = self.begin
        if length is None:
            length = self.length
        self.is_finished = False
        self.results.append((diag, begin, length))

        tmp_status = None

        if self.verbose > 1:
            tmp_status = META_LOOKUP.status(diag)
        elif META_LOOKUP.is_error(diag):
            tmp_status = ISEMAIL_RESULT_CODES.ERROR

        if tmp_status is not None:
            self.status = max(tmp_status, self.status)
            if tmp_status == ISEMAIL_RESULT_CODES.ERROR:
                self.length = 0
                if raise_on_error:
                    raise ParsingError(self)

        return self


    def add_comment(self, begin=None, length=None):
        if begin is None:
            begin = self.begin

        if length is None:
            length = self.length

        self.comments.append((begin, length))
        return self

    def add(self, *args,
            diag=None,
            segment=None,
            begin=None,
            position=None,
            length=None,
            set_length=None,
            raise_on_error=True):
        """

        :param args:
            if string, this will be a diag str if we can look it up in diags, a segment name if not.
            if int, this will add at number to the length
            if football, this will add the football to the object

        :param diag:
        :param segment:
        :param begin:
        :param position:
        :param length:
        :param set_length:
        :param raise_on_error:
        :return:
        """

        self.is_finished = False

        if begin is not None:
            self.begin = begin

        if position is not None:
            self.begin = position

        if length is not None:
            self.length += length

        if set_length is not None:
            self.length = set_length

        if segment is not None:
            self.segment_name = segment

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
                self.length += arg
            elif isinstance(arg, dict):
                self.add_diag(raise_on_error=raise_on_error, **arg)
            elif isinstance(arg, (tuple, list)):
                self.add_diag(*arg, raise_on_error=raise_on_error)
            elif isinstance(arg, str):
                if arg in META_LOOKUP:
                    self.add_diag(arg, raise_on_error=raise_on_error)
                else:
                    self.segment_name = arg

        return self
    __call__ = add

    @staticmethod
    def _make_int(other):
        if isinstance(other, int):
            return other
        else:
            return other.length

    def __lt__(self, other):
        return self.length < self._make_int(other)

    def __le__(self, other):
        return self.length <= self._make_int(other)

    def __eq__(self, other):
        return self.length == self._make_int(other)

    def __ne__(self, other):
        return self.length != self._make_int(other)

    def __gt__(self, other):
        return self.length > self._make_int(other)

    def __ge__(self, other):
        return self.length >= self._make_int(other)

    def __contains__(self, item):
        if not self.is_finished:
            self.finish()
        return item in self.diag_recs

    def __repr__(self):
        return 'Length: %s, Results: %s' % (self.length, len(self.results))

    def __str__(self):
        if not self.is_finished:
            self.finish()
        tmp_str = ''
        if self.error:
            tmp_str = 'ERROR '

        if self.length == 0:
            tmp_str += '(not found)'
        else:
            tmp_str += '(%s)' % self.length

        if self.results:
            tmp_str += ' [%s]' % ','.join(self.diags())

        return tmp_str

    def __bool__(self):
        if self.length == 0:
            return False
        return True

    def __int__(self):
        return self.length

    def __len__(self):
        return len(self.results)

    @property
    def full_string_in(self):
        return self.parser.email_in

    @property
    def verbose(self):
        return self.parser.verbose

    def finish(self):

        self.is_finished = True
        self.cleaned_email = None
        self.local_part = []
        self.domain_part = []
        
        self.cat_recs = {}
        self.diag_recs = {}

        self.major_diag = None
        self.major_diag_value = 0

        for r in self.results:
            self._fix_result(r)

    def _add_comment(self, begin, length):
        self.comments.append((begin, length))

    def _fix_result(self, result_rec):
        result_rec = ParseResultItem(*result_rec)
        self.status = max(result_rec.status, self.status)

        if self.major_diag_value is None:
            self.major_diag_value = result_rec.value
            self.major_diag = result_rec
        else:
            self.major_diag_value = max(result_rec.value, self.major_diag_value)
            self.major_diag = META_LOOKUP[self.major_diag_value]

        if self.verbose:

            if result_rec.diag.key in self.diag_recs:
                self.diag_recs[result_rec.key].append(result_rec)
            else:
                self.diag_recs[result_rec.key] = [result_rec]

            if result_rec.diag.category.key in self.cat_recs:
                self.cat_recs[result_rec.diag.category.key].append(result_rec)
            else:
                self.cat_recs[result_rec.diag.category.key] = [result_rec]

    @property
    def error(self):
        return self.status == ISEMAIL_RESULT_CODES.ERROR

    @property
    def ok(self):
        return self.status == ISEMAIL_RESULT_CODES.OK

    @property
    def warning(self):
        return self.status == ISEMAIL_RESULT_CODES.WARNING

    # TODO: Finish this
    def response_text(self):
        pass

    # TODO: Finish this
    def response_long_text(self):
        pass

    # TODO: Finish this
    def response_details(self):
        pass

    def __getitem__(self, item):
        if not self.is_finished:
            self.finish()
        try:
            return self.diag_recs[item]
        except KeyError:
            return self.cat_recs[item]


class ParseResultEmptyFootball(object):
    def __init__(self, parser, *args, **kwargs):
        self.length = 0
        self.status = ISEMAIL_RESULT_CODES.OK

        self.parser = parser
        """
        if length > 0:
            self.length = length
        else:
            self.length = 0

        self.results = []
        if kwargs:
            self.add(length=length, **kwargs)

        self.stage = stage

        self.status = ISEMAIL_RESULT_CODES.OK

        self.comments = []

        self.children = []
        self.begin = -1
        self.segment_name = ''
        self.depth = 0
        self.hist_cache = None

        # **** Finished vars ****
        self.is_finished = False
        self.cleaned_email = None
        self.local_part = None
        self.domain_part = None
        self.cat_recs = None
        self.diag_recs = None
        self.major_diag = None
        self.major_diag_value = None
        """

    def copy(self):
        tmp_ret = self.__class__(self.parser)
        return tmp_ret

    __copy__ = copy

    @property
    def l(self):
        return 0

    def diags(self):
        return []
    """
    def _make_history(self, depth=0, parent=None):
        tmp_hist = ParseHistory(self.parser, parent, self.segment_name, self.begin, self.length, depth=depth)
        self.depth = depth

        for c in self.children:
            tmp_hist.add(c._make_history(depth=depth + 1, parent=tmp_hist))

        return tmp_hist
    """
    @property
    def history(self):
        return None
    """
    def clear(self, keep_results=False):
        self.length = 0
        if not keep_results:
             self.results.clear()
            self.is_finished = False
            self._refresh()
            self.hist_cache = None
        return self

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
            if META_LOOKUP.is_error(i[0]):
                self.status = ISEMAIL_RESULT_CODES.ERROR
    """
    def __iadd__(self, other):
        if isinstance(other, int):
            tmp_ret = ParseResultFootball(self.parser)
            tmp_ret += other
            return tmp_ret
        else:
            return self.merge(other)
    __add__ = __iadd__
    __radd__ = __iadd__

    def __isub__(self, other):
        tmp_ret = ParseResultFootball(self.parser)
        tmp_ret -= other
        return tmp_ret

    __sub__ = __isub__
    __rsub__ = __isub__

    def merge(self, other):
        if isinstance(other, ParseResultFootball):
            return other
        else:
            return self

    """
    def add(self, *args, **kwargs):
        should_raise = kwargs.get('raise_on_error', True)
        tmp_res_tuple = None
        if args:
            if len(args) == 1:
                if isinstance(args[0], ParseResultFootball):
                    self.merge(args[0])
                elif isinstance(args[0], int):
                    self.length += args[0]
                else:
                    raise AttributeError('Invalid object trying to add: %r' % args[0])
            else:
                tmp_res_tuple = args
        elif kwargs:
            if 'diag' in kwargs:
                try:
                    tmp_res_tuple = (kwargs['diag'], kwargs['begin'], kwargs.get('length', self.length))
                except KeyError:
                    pass
            if 'segment' in kwargs:
                self.segment_name = kwargs['segment']
                self.begin = kwargs['begin']
                self.length = kwargs.get('length', self.length)

            if 'set' in kwargs:
                self.length = kwargs['set']

        if tmp_res_tuple is not None:
            self.is_finished = False
            self.results.append(tmp_res_tuple)

            if META_LOOKUP.is_error(tmp_res_tuple[0]):
                self.length = 0
                self.status = ISEMAIL_RESULT_CODES.ERROR
                if should_raise:
                    raise ParsingError(self)
        return self

    __call__ = add

    @staticmethod
    def _make_int(other):
        if isinstance(other, int):
            return other
        else:
            return other.length

    def __lt__(self, other):
        return self.length < self._make_int(other)

    def __le__(self, other):
        return self.length <= self._make_int(other)

    def __eq__(self, other):
        return self.length == self._make_int(other)

    def __ne__(self, other):
        return self.length != self._make_int(other)

    def __gt__(self, other):
        return self.length > self._make_int(other)

    def __ge__(self, other):
        return self.length >= self._make_int(other)

    def __contains__(self, item):
        if not self.is_finished:
            self.finish()
        return item in self.diag_recs
    """
    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'EMPTY OBJECT'

    def __bool__(self):
        return False

    def __int__(self):
        return 0

    """
    @property
    def full_string_in(self):
        return self.parser.email_in

    @property
    def verbose(self):
        return self.parser.verbose

    def finish(self):

        self.is_finished = True
        self.cleaned_email = None
        self.local_part = []
        self.domain_part = []

        self.cat_recs = {}
        self.diag_recs = {}

        self.major_diag = None
        self.major_diag_value = 0

        for r in self.results:
            self._fix_result(r)

    def _add_comment(self, begin, length):
        self.comments.append((begin, length))

    def _fix_result(self, result_rec):
        result_rec = ParseResultItem(*result_rec)
        self.status = max(result_rec.status, self.status)

        if self.major_diag_value is None:
            self.major_diag_value = result_rec.value
            self.major_diag = result_rec
        else:
            self.major_diag_value = max(result_rec.value, self.major_diag_value)
            self.major_diag = META_LOOKUP[self.major_diag_value]

        if self.verbose:

            if result_rec.diag.key in self.diag_recs:
                self.diag_recs[result_rec.key].append(result_rec)
            else:
                self.diag_recs[result_rec.key] = [result_rec]

            if result_rec.diag.category.key in self.cat_recs:
                self.cat_recs[result_rec.diag.category.key].append(result_rec)
            else:
                self.cat_recs[result_rec.diag.category.key] = [result_rec]
    """
    @property
    def error(self):
        return self.status == ISEMAIL_RESULT_CODES.ERROR

    @property
    def ok(self):
        return self.status == ISEMAIL_RESULT_CODES.OK

    @property
    def warning(self):
        return self.status == ISEMAIL_RESULT_CODES.WARNING
    """
    # TODO: Finish this
    def response_text(self):
        pass

    # TODO: Finish this
    def response_long_text(self):
        pass

    # TODO: Finish this
    def response_details(self):
        pass

    def __getitem__(self, item):
        try:
            return self.diag_recs[item]
        except KeyError:
            return self.cat_recs[item]

    """
'''
class ParseEmailResult(object):
    def __init__(self, full_email_in, verbose=True, error_on_warning=False, error_on_value=None):
        """

        :param full_email_in:
        :param verbose:
            0 = T/F only
            1 = T/F + major only
            2 = All results
        :param error_on_warning:
        :param error_on_value:
        """
        self.full_string_in = full_email_in
        self.result_recs = []
        # self.worst_result = 0
        # self.worst_category_rec = None
        self.verbose = verbose
        self.error_on_warning = error_on_warning

        self.cleaned_email = None
        self.local_part = []
        self.domain_part = []
        self.comments = []

        self.categories = {}
        self.diags = {}

        self.error_on_value = []
        if error_on_value is not None:
            for item in self._make_list(error_on_value):
                if isinstance(item, int):
                    self.error_on_value.append(item)
                else:
                    self.error_on_value.append(META_LOOKUP[item].value)

        self.status = ISEMAIL_RESULT_CODES.OK

        self.major_diag = None
        self.major_diag_value = 0


    @property
    def error(self):
        return self.status == ISEMAIL_RESULT_CODES.ERROR

    @property
    def ok(self):
        return self.status == ISEMAIL_RESULT_CODES.OK

    @property
    def warning(self):
        return self.status == ISEMAIL_RESULT_CODES.WARNING

    @staticmethod
    def _make_list(obj_in):
        if isinstance(obj_in, (str, int)):
            return [obj_in]
        elif isinstance(obj_in, (list, tuple)):
            return obj_in

    def add_comment(self, diag, begin, length):
        self.comments.append(ParseResultItem(diag=diag, begin=begin, length=length, name='comment'))

    def add_result(self, result_rec, **kwargs):

        if isinstance(result_rec, ParseResultFootball):
            for res in result_rec.results:
                self.add_result(res)
        else:
            if isinstance(result_rec, str):
                result_rec = ParseResultItem(result_rec, **kwargs)

            if result_rec.value in self.error_on_value:
                tmp_status = ISEMAIL_RESULT_CODES.ERROR
            else:
                tmp_status = result_rec.result

            if self.error_on_warning and tmp_status == ISEMAIL_RESULT_CODES.WARNING:
                tmp_status = ISEMAIL_RESULT_CODES.ERROR

            self.status = max(tmp_status, self.status)

            if self.major_diag_value is None:
                self.major_diag_value = result_rec.value
                self.major_diag = result_rec
            else:
                self.major_diag_value = max(result_rec.value, self.major_diag_value)
                self.major_diag = META_LOOKUP[self.major_diag_value]

            if self.verbose:

                self.result_recs.append(result_rec)

                if result_rec.diag.key in self.diags:
                    self.diags[result_rec.diag.key].append(result_rec)
                else:
                    self.diags[result_rec.diag.key] = [result_rec]

                if result_rec.diag.category.key in self.categories:
                    self.diags[result_rec.diag.category.key].append(result_rec)
                else:
                    self.diags[result_rec.diag.category.key] = [result_rec]

    def responses(self):
        return self.result_recs

    # TODO: Finish this
    def response_text(self):
        pass

    # TODO: Finish this
    def response_long_text(self):
        pass

    # TODO: Finish this
    def response_details(self):
        pass

    def __bool__(self):
        return not bool(self.error)

    def __len__(self):
        return len(self.result_recs)

    def __contains__(self, item):
        if item in self.diags:
            return True
        elif item in self.categories:
            return True
        else:
            return False

    def __getitem__(self, item):
        try:
            return self.diags[item]
        except KeyError:
            return self.categories[item]

    def __repr__(self):
        return 'Parse Results[%s] = %s' % (self.full_string_in, self.status.name)

'''