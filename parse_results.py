
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

    def __init__(self, parser, length=0, stage='', **kwargs):
        self.parser = parser
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
            tmp_ret.cleaned_email = self.cleaned_email.copy()
            tmp_ret.local_part = self.local_part.copy()
            tmp_ret.domain_part = self.domain_part.copy()
            tmp_ret.cat_recs = self.cat_recs.copy()
            tmp_ret.diag_recs = self.diag_recs.copy()
            tmp_ret.major_diag = self.major_diag
            tmp_ret.major_diag_value = self.major_diag_value
        
        return tmp_ret
    __copy__ = copy

    @property
    def l(self):
        return self.length

    def diags(self):
        return self.diag_recs.keys()
 
    def clear(self, keep_results=False):
        self.length = 0
        if not keep_results:
            self.results.clear()
        self.error = False
        return self

    def __iadd__(self, other):
        if isinstance(other, int):
            self.length += other
        else:
            self.merge(other)

        return self
    __add__ = __iadd__
    __radd__ = __iadd__

    def __isub__(self, other):
        self.length -= other
        return self
    __sub__ = __isub__
    __rsub__ = __isub__

    def merge(self, other):
        self.length += other.length
        self.status = max(self.status, other.status)
        self.results.extend(other.results)

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
            try:
                tmp_res_tuple = (kwargs['diag'], kwargs['begin'], kwargs['length'])
            except KeyError:
                pass
            if 'set' in kwargs:
                self.length = kwargs['set']

        if tmp_res_tuple is not None:
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
        try:
            return self.diag_recs[item]
        except KeyError:
            return self.cat_recs[item]

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