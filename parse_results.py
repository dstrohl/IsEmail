
from meta_data import ISEMAIL_RESULT_CODES, META_LOOKUP, ISEMAIL_DOMAIN_TYPE, ISEMAIL_DNS_LOOKUP_LEVELS, MetaList
from dns_functions import dns_lookup

def _make_list(obj_in):
    if isinstance(obj_in, (str, int)):
        return [obj_in]
    elif isinstance(obj_in, (list, tuple)):
        return obj_in


class ParsingError(Exception):

    def __init__(self, results, *args, **kwargs):
        self.results = results
        super().__init__(*args, **kwargs)

    def __str__(self):
        return 'ERROR: Parsing Error: %s' % self.results.major_diag


class UnfinishedParsing(Exception):
    def __str__(self):
        return 'ERROR: Not finished parsing yet, data is not available'


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




class ParseHistoryResultItem(object):
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

    def __str__(self):
        return self.segment_type

    @property
    def parsed_str(self):
        return self.parser.mid(self.begin, self.length)

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


'''
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
        return self.diag.description

    @property
    def smtp(self):
        return self.diag.smtp.description

    @property
    def references(self):
        return self.diag.references

    @property
    def status(self):
        return self.diag.status

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __le__(self, other):
        return self.value <= other.value

    def __ge__(self, other):
        return self.value >= other.value
'''

class ParseResultFootball(object):

    def __init__(self, parser, segment='', position=0, length=0, stage=''):
        self.parser = parser
        self.email_in = parser.email_in
        if length > 0:
            self.length = length
        else:
            self.length = 0

        self.at_loc = None
        self.results = []
        self.stage = stage
        self._local_comments = {}
        self._domain_comments = {}
        self.children = []
        self.begin = position
        self.segment_name = segment
        self.depth = 0
        self.hist_cache = None
        self.error = False

        self.domain_type = None

    def copy(self):
        tmp_ret = self.__class__(self.parser)
        tmp_ret.length = self.length
        tmp_ret.results = self.results.copy()
        tmp_ret.stage = self.stage
        tmp_ret._local_comments = self._local_comments.copy()
        tmp_ret._domain_comments = self._domain_comments.copy()
        tmp_ret.domain_type = self.domain_type
        tmp_ret.at_loc = self.at_loc
        tmp_ret.error = self.error
        return tmp_ret
    __copy__ = copy

    @property
    def l(self):
        return self.length

    def diags(self):
        tmp_ret = []
        for r in self.results:
            if r[0] not in tmp_ret:
                tmp_ret.append(r[0])
        return tmp_ret

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

    def _set_error(self, new_error):
        if not self.error:
            if new_error:
                self.error = True

    def merge(self, other):
        if isinstance(other, ParseResultFootball):
            self.is_finished = False
            self.length += other.length
            # self.status = max(self.status, other.status)
            self.results.extend(other.results)
            self._set_error(other.error)
            # if other.segment_name is not None and other.segment_name != '':
            self.children.append(other)

            self._local_comments.update(other._local_comments)
            self._domain_comments.update(other._domain_comments)

            self.domain_type = self.domain_type or other.domain_type
            # self._parts = other._parts

            self.at_loc = self.at_loc or other.at_loc

    def add_diag(self, diag, begin=None, length=None, raise_on_error=True):
        if begin is None:
            begin = self.begin
        if length is None:
            length = self.length
        self.is_finished = False
        self.results.append((diag, begin, length))

        try:
            tmp_error = META_LOOKUP.is_error(diag)
        except KeyError:
            raise AttributeError('Invalid Diagnosis: ' + diag)
        self._set_error(tmp_error)

        if tmp_error:
            self.length = 0
            if raise_on_error:
                raise ParsingError(self)

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
                self.add_diag(arg, raise_on_error=raise_on_error)

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
        for r in self.results:
            if r[0] == item:
                return True
        return False

    def __repr__(self):
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

    def __str__(self):
        return repr(self)

    def __bool__(self):
        if self.length == 0:
            return False
        return True

    def __int__(self):
        return self.length

    def __len__(self):
        return len(self.results)

    @property
    def trace_str(self):
        return self.parser.trace_str

    def finish(self, dns_lookup_level=None, raise_on_error=False):
        verbose = self.parser.verbose
        # 0 = return T/F
        # 1 = return short object
        # 2 = return full object
        if dns_lookup_level is None:
            dns_lookup_level = ISEMAIL_DNS_LOOKUP_LEVELS.NO_LOOKUP

        if verbose == 0:
            if dns_lookup_level == ISEMAIL_DNS_LOOKUP_LEVELS.NO_LOOKUP or self.domain_type != ISEMAIL_DOMAIN_TYPE.DNS:
                if raise_on_error and self.error:
                    raise ParsingError(self)
                return not self.error

        parts = dict(
                local_part=[],
                domain_part=[],
                clean_local_part=[],
                clean_domain_part=[],
                full_local_part=[],
                full_domain_part=[])

        if not self.error and self.at_loc is not None:
            in_local = True
            in_literal = False
            index = 0

            while index < len(self.email_in):

                tmp_char = self.email_in[index]

                if index == self.at_loc:
                    in_local = False
                elif index in self._local_comments:
                    parts['full_local_part'].append('(%s)' % self._local_comments[index])
                    index += len(self._local_comments[index])+1
                elif index in self._domain_comments:
                    parts['full_domain_part'].append('(%s)' % self._domain_comments[index])
                    index += len(self._domain_comments[index])+1

                elif tmp_char in '"[]':
                    if in_local:
                        parts['clean_local_part'].append(tmp_char)
                        parts['full_local_part'].append(tmp_char)
                    else:
                        parts['clean_domain_part'].append(tmp_char)
                        parts['full_domain_part'].append(tmp_char)
                    if in_literal:
                        in_literal = False
                    else:
                        if self.domain_type == ISEMAIL_DOMAIN_TYPE.IPv6 and tmp_char == '[':
                            parts['clean_domain_part'].extend('IPv6:')
                            parts['full_domain_part'].extend('IPv6:')
                            index += 5
                        in_literal = True

                elif not in_literal and tmp_char in ' \t\r\n':
                    pass
                else:
                    if in_local:
                        parts['local_part'].append(tmp_char)
                        parts['clean_local_part'].append(tmp_char)
                        parts['full_local_part'].append(tmp_char)
                    else:
                        parts['domain_part'].append(tmp_char)
                        parts['clean_domain_part'].append(tmp_char)
                        parts['full_domain_part'].append(tmp_char)
                index += 1

            parts['local_part'] = ''.join(parts['local_part'])
            parts['domain_part'] = ''.join(parts['domain_part'])
            parts['clean_local_part'] = ''.join(parts['clean_local_part'])
            parts['clean_domain_part'] = ''.join(parts['clean_domain_part'])
            parts['full_local_part'] = ''.join(parts['full_local_part'])
            parts['full_domain_part'] = ''.join(parts['full_domain_part'])

            if self.domain_type == ISEMAIL_DOMAIN_TYPE.GENERAL_LIT:
                parts['domain_part'] = parts['domain_part'].split(':', 1)

            if self.domain_type == ISEMAIL_DOMAIN_TYPE.DNS:
                tmp_dns = dns_lookup(
                    parts['clean_domain_part'],
                    dns_lookup_level,
                    servers=self.parser._dns_servers,
                    timeout=self.parser._dns_timeout,
                    raise_on_comm_error=self.parser._raise_on_error,
                    tld_list=self.parser._tld_list,
                )

                if tmp_dns:
                    self(tmp_dns, raise_on_error=False)
                    # self._fix_result(self.results[-1])

        else:
            parts = None

        if raise_on_error and self.error:
            raise ParsingError(self)

        if verbose == 0:
            return not self.error
        elif verbose == 1:
            return ParseShortResult(
                email_in=self.email_in,
                parts=parts,
                results=self.results)
        else:
            return ParseFullResult(
                email_in=self.email_in,
                parts=parts,
                results=self.results,
                history=self.history,
                local_comments=self._local_comments,
                domain_comments=self._domain_comments,
                domain_type=self.domain_type,
                trace=self.trace_str)

    def add_comment(self, begin=None, length=None):
        begin = begin or self.begin
        length = length or self.length

        if self.parser.in_local_part:
            self._local_comments[begin] = self._mid(begin+1, length-2)
        elif self.parser.in_domain_part:
            self._domain_comments[begin] = self._mid(begin+1, length-2)
        return self

    def _mid(self, position, length):
        end = position+length
        return self.email_in[position:end]


class ParseShortResult(object):
    def __init__(self, email_in, parts, results):
        self.full_address = email_in
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

    def diag(self, filter=None, show_all=False, inc_cat=False, inc_diag=True, return_as='string'):
        if filter:
            return self._major_diag.category.key
        else:
            return self._major_diag.key

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
        return self._major_diag.description

    def __getitem__(self, item):
        if item in self:
            return self._major_diag
        else:
            raise KeyError(item)


class ParseFullResult(ParseShortResult):
    def __init__(self, email_in, parts, results, history, local_comments, domain_comments, domain_type, trace):
        self._diag_recs = {}
        self._diag_keys = []
        # self._cat_recs = MetaList()

        super().__init__(email_in, parts, results)

        self.history = history
        self._local_comments = local_comments
        self._domain_comments = domain_comments
        self.domain_type = domain_type
        self.trace = trace

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

    def report(self, report_name, filter=None, **kwargs):
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


