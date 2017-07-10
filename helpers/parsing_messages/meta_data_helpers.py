from helpers.meta_data.meta_data import ISEMAIL_DIAG_RESPONSES, ISEMAIL_RESULT_CODES, ISEMAIL_RESP_CATEGORIES
from helpers.general import make_list

class MetaBase(object):
    type_name = 'Base'
    is_cat = False
    is_diag = False

    def __init__(self, key, dict_in, lookup):
        self.lookup = lookup
        self.name = dict_in.get('name', None)
        self.key = key
        self._value = dict_in['value']
        self.description = dict_in['description']
        self._override_status = None
        self._result = dict_in.get('result', None)
        self._single_desc = None
        self._both_desc = None

        self._diags = MetaList()

    def format(self, format_str=None, **kwargs):
        format_str = format_str or self.lookup.default_format
        return format_str.format(**self._fmt_dict(kwargs))

    def _fmt_dict(self, kwargs):
        raise NotImplementedError()

    def __repr__(self):
        return '%s(%s) [%s]' % (self.type_name, self.key, self.status.name)

    def __str__(self):
        return self.format()

    @property
    def _base_status(self):
        return self._result

    @property
    def value(self):
        if self.status == ISEMAIL_RESULT_CODES.ERROR:
            return self._value * 10000
        elif self.status == ISEMAIL_RESULT_CODES.WARNING:
            return self._value * 100
        else:
            return self._value

    @property
    def status(self):
        return self._override_status or self._base_status

    def set_override_status(self, new_status):
        self._override_status = new_status
        # self._single_desc = None
        # self._both_desc = None

    def reset_status(self):
        self._override_status = None
        # self._single_desc = None
        # self._both_desc = None

    def _get_other(self, other):
        if isinstance(other, str):
            return self.lookup[other].value
        elif isinstance(other, int):
            return other
        else:
            return other.value

    def __eq__(self, other):
        return self.value == self._get_other(other)

    def __ne__(self, other):
        return self.value != self._get_other(other)

    def __lt__(self, other):
        return self.value < self._get_other(other)

    def __le__(self, other):
        return self.value <= self._get_other(other)

    def __gt__(self, other):
        return self.value > self._get_other(other)

    def __ge__(self, other):
        return self.value >= self._get_other(other)

    def __hash__(self):
        return hash(self.key)

    def _in_flt_cat(self, filter_set=None, exact=False):
        return self.key in filter_set

    def _in_flt_diag(self, filter_set=None, exact=False):
        return self.key in filter_set

    def _in_flt_status(self, filter_set=None):
        return self.status.name in filter_set

    def in_filter(self, filter, exact=False):
        if filter is None:
            return True
        if isinstance(filter, dict):
            tmp_cat = self._in_flt_cat(make_list(filter.get('cats', None)), exact)
            tmp_diag = self._in_flt_diag(make_list(filter.get('diags', None)), exact)
            tmp_status = self._in_flt_status(make_list(filter.get('status', None)))
            return any((tmp_cat, tmp_diag, tmp_status))
        else:
            return self.key in make_list(filter)


class MetaCat(MetaBase):
    type_name = 'Categ'
    is_cat = False
    is_diag = True

    def add_diag(self, key, dict_in):
        tmp_diag = MetaDiag(key, dict_in, self, self.lookup)
        self._diags[key] = tmp_diag
        return tmp_diag

    def _fmt_dict(self, kwargs):
        tmp_dict = dict(
            name=self.name,
            description=self.description,
            key=self.key,
            value=self.value,
            status=self.status.name)
        tmp_dict.update(kwargs)
        return tmp_dict

    def _in_flt_diag(self, filter_set=None, exact=False):
        if exact:
            return False
        else:
            for d in self._diags.keys():
                if d.key in filter_set:
                    return True
            return False


class MetaDiag(MetaBase):
    type_name = 'Diag'
    is_cat = False
    is_diag = True

    def __init__(self, key, dict_in, cat_rec, lookup):
        super().__init__(key, dict_in, lookup)

        self.category = cat_rec
        self.smtp = dict_in['smtp']['description']
        self.reference = []
        if 'reference' in dict_in:
            tmp_refs = dict_in['reference']
            if isinstance(tmp_refs, (list, tuple)):
                for ref in dict_in['reference']:
                    self.reference.append(ref)
            else:
                self.reference.append(tmp_refs)

    def __repr__(self):
        return '%s(%s) [%s] -> %s' % (self.type_name, self.key, self.status.name, self.category.key)

    @property
    def _dif_status(self):
        if self._override_status is None:
            return ''
        else:
            return '[%s] ' % self.status.name

    def _fmt_dict(self, kwargs):
        tmp_dict = dict(
            description=self.description,
            key=self.key,
            value=self.value,
            status=self.status.name,
            cat_key=self.category.key,
            cat_name=self.category.name,
            dif_status=self._dif_status)
        tmp_dict.update(kwargs)
        return tmp_dict

    def _in_flt_cat(self, filter_set=None, exact=False):
        if exact:
            return False
        else:
            return self.category.key in filter_set

    @property
    def _base_status(self):
        return self.category.status


class MetaList(object):
    def __init__(self, data=None):
        self._keys = {}
        self._ordered = []

        if data is not None:
            self.update(data)

        self._sorted = None

    def clear(self):
        self._keys.clear()
        self._ordered.clear()
        self._sorted = None

    def sort(self, reverse=True):
        if self._sorted != repr(reverse):
            self._ordered.sort(reverse=reverse)
            self._sorted = repr(reverse)

    def update(self, dict_in):
        self._sorted = False
        for key, item in dict_in:
            self[key] = item

    def keys(self, reverse=True, show_all=True, ordered=False, filter=None, within=None):
        if isinstance(within, str):
            within = [within]
        if not show_all:
            ordered = True
        if ordered or filter is not None:
            tmp_ret = []
            for i in self.values(reverse=reverse, show_all=show_all):
                if filter is None or i.in_filter(filter):
                    if within is None or i.key in within:
                        tmp_ret.append(i.key)
            return tmp_ret
        else:
            return self._keys.keys()

    def values(self, reverse=True, show_all=True, filter=None, ordered=True, within=None):
        if isinstance(filter, str):
            filter = [filter]
        if isinstance(within, str):
            within = [within]

        if ordered or not show_all:
            self.sort(reverse=reverse)

        if filter is not None or within is not None:
            tmp_ret = []
            for i in self._ordered:
                if i.in_filter(filter):
                    if within is None or i.key in within:
                        tmp_ret.append(i)
        else:
            tmp_ret = self._ordered.copy()
        if show_all or len(tmp_ret) < 2:
            return tmp_ret
        else:
            return [tmp_ret[0]]

    def __getitem__(self, item):
        return self._keys[item]

    def __setitem__(self, key, value):
        self._sorted = None
        self._keys[key] = value
        self._ordered.append(value)

    def __iter__(self):
        self.sort(reverse=True)
        for item in self._ordered:
            yield item

    def __contains__(self, item):
        return item in self._keys

    def __bool__(self):
        return bool(self._keys)

    def __len__(self):
        return len(self._ordered)


class MetaOutoutBase(object):
    report_name = ''
    only_single = False
    only_both = False

    def __init__(self, parent):
        self.parent = parent
        self.items = MetaList()
        self.sub_items = {}

    def add_item(self, diag):
        if self.inc_both:
            tmp_cat = diag.category
            if tmp_cat.key not in self.items:
                self.items[tmp_cat.key] = tmp_cat
                self.sub_items[tmp_cat.key] = MetaList()
            self.sub_items[tmp_cat.key][diag.key] = diag
        elif self.inc_cat:
            diag = diag.category
            if diag.key not in self.items:
                self.items[diag.key] = diag
        else:
            self.items[diag.key] = diag

    def _generate(self, **kwargs):
        raise NotImplementedError('_generate must be implemented in sub classes')

    def out(self, diags, **kwargs):
        self.sub_items.clear()
        self.items.clear()
        if self.only_both:
            self.inc_cat = kwargs.pop('inc_cat', True)
            self.inc_diag = kwargs.pop('inc_diag', True)
            if not self.inc_cat or not self.inc_diag:
                raise AttributeError('%s report does not support inc_cat or inc_diag' % self.report_name)
            self.inc_both = True

        elif self.only_single:
            self.inc_cat = kwargs.pop('inc_cat', False)
            self.inc_diag = kwargs.pop('inc_diag', True)
            if self.inc_cat and self.inc_diag:
                raise AttributeError('%s report does not support inc_cat or inc_diag' % self.report_name)
            self.inc_both = False
        else:
            self.inc_cat = kwargs.pop('inc_cat', False)
            self.inc_diag = kwargs.pop('inc_diag', True)
            self.inc_both = self.inc_cat and self.inc_diag

        if diags is not None:
            for item in diags:
                self.add_item(item)

        return self._generate(**kwargs)


class MR_KeyDict(MetaOutoutBase):
    report_name = 'key_dict'
    only_single = False
    only_both = True

    def _generate(self, **kwargs):
        tmp_ret = {}
        for item in self.items:
            tmp_sub_item = []
            for diag in self.sub_items[item.key]:
                tmp_sub_item.append(diag.key)
            tmp_ret[item.key] = tmp_sub_item
        return tmp_ret


class MR_ObjDict(MetaOutoutBase):
    report_name = 'obj_dict'
    only_single = True
    only_both = False

    def _generate(self, **kwargs):
        tmp_ret = {}
        for item in self.items:
            tmp_ret[item.key] = item
        return tmp_ret


class MR_ObjList(MetaOutoutBase):
    report_name = 'object_list'
    only_single = True
    only_both = False
    # object_list (either cat or diag)

    def _generate(self, **kwargs):
        tmp_ret = []
        for item in self.items:
            tmp_ret.append(item)
        return tmp_ret


class MR_KeyList(MetaOutoutBase):
    report_name = 'key_list'
    only_single = True
    only_both = False
    # key_list (either cat or diat)

    def _generate(self, **kwargs):
        tmp_ret = []
        for item in self.items:
            tmp_ret.append(item.key)
        return tmp_ret


class MR_FormattedList(MetaOutoutBase):
    report_name = 'formatted_list'
    only_single = False
    only_both = False
    # formatted_string (any)
    single_cat_format = '[{status}] - {name}: ({description})'
    single_diag_format = '[{status}] {description}'
    both_cat_format = '{name}: [{status}]((SPLIT))({description})'
    both_diag_format = '{indent}- {description}'

    def _generate(self, **kwargs):
        indent = kwargs.get('indent', 4)
        indent_str = ''.rjust(indent, ' ')
        tmp_ret = []
        if self.inc_both:
            for item in self.items:
                tmp_add = item.format(self.both_cat_format)
                tmp_ret.extend(tmp_add.split('((SPLIT))'))
                for diag in self.sub_items[item.key]:
                    tmp_add = diag.format(self.both_diag_format, indent=indent_str)
                    tmp_ret.extend(tmp_add.split('((SPLIT))'))
        else:
            if self.inc_diag:
                tmp_fmt = self.single_diag_format
            else:
                tmp_fmt = self.single_cat_format
            for item in self.items:
                tmp_ret.append(item.format(tmp_fmt, indent=indent_str))

        return tmp_ret


class MR_FormattedString(MetaOutoutBase):
    report_name = 'formatted_string'
    only_single = False
    only_both = False

    # formatting strings

    single_wrapper_format = '{items}'
    single_cat_format = '[{status}] - {name}: ({description})'
    single_diag_format = '[{status}] {description}'
    single_item_separetor = '\n'

    both_wrapper_format = '{cats}'
    both_cat_format = '{name}: [{status}]\n({description})\n{diags}'
    both_diag_format = '{indent}- {description}'
    both_diag_separetor = '\n'
    both_cat_separetor = '\n\n'

    def _generate(self, **kwargs):
        indent = kwargs.get('indent', 4)
        indent_str = ''.ljust(indent, ' ')
        if self.inc_both:
            tmp_lst = []
            for item in self.items:
                tmp_diags_list = []
                for diag in self.sub_items[item.key]:
                    tmp_diags_list.append(diag.format(self.both_diag_format, indent=indent_str))
                tmp_diags = self.both_diag_separetor.join(tmp_diags_list)
                tmp_cat = item.format(self.both_cat_format, indent=indent_str, diags=tmp_diags)
                tmp_lst.append(tmp_cat)
            tmp_ret = self.both_cat_separetor.join(tmp_lst)
            tmp_ret = self.both_wrapper_format.format(cats=tmp_ret, indent=indent_str)
            return tmp_ret
        else:
            tmp_lst = []
            if self.inc_diag:
                tmp_fmt = self.single_diag_format
            else:
                tmp_fmt = self.single_cat_format

            for item in self.items:
                tmp_lst.append(item.format(tmp_fmt))
            tmp_ret = self.single_item_separetor.join(tmp_lst)
            tmp_ret = self.single_wrapper_format.format(items=tmp_ret, indent=indent_str)
            return tmp_ret


class MR_DescList(MR_FormattedList):
    report_name = 'desc_list'
    single_cat_format = '[{status}] - {name}: ({description})'
    single_diag_format = '[{status}] {description}'
    both_cat_format = '{name}: [{status}]((SPLIT))({description})'
    both_diag_format = '{indent}- {description}'
    return_as_list = True


class MR_DocumentString(MR_FormattedString):
    report_name = 'document_string'
    only_both = True

    single_cat_format = '{key} [{status}]: {name}\n{diags}'
    single_diag_format = '{key} [{status}]: {description}'

    both_cat_format = '{key} [{status}]: {name}\n{diags}'
    both_diag_format = '{indent}{key}: {dif_status}{description}'


_meta_formatters = [MetaOutoutBase, MR_KeyDict, MR_ObjDict, MR_ObjList,
    MR_KeyList, MR_FormattedString, MR_DescList, MR_DocumentString]


class MetaLookup(object):
    default_key_format = '[{status}] {key}'
    default_desc_format = '[{status}] {description}'

    def __init__(self, error_on_warning=False, *error_on_code):
        # self.by_value = {}
        # self.by_key = {}
        self.results = ISEMAIL_RESULT_CODES
        self.categories = MetaList()
        self.diags = MetaList()
        self.lookup = MetaList()
        self.statuses = {
            'WARNING': [],
            'ERROR': [],
            'OK': []}

        self.default_format = self.default_desc_format

        # self.categories = MetaList(MetaCat, self, ISEMAIL_RESP_CATEGORIES)
        # self.diags = MetaList(MetaDiag, self, ISEMAIL_DIAG_RESPONSES)

        for key, item in ISEMAIL_RESP_CATEGORIES.items():
            tmp_cat = MetaCat(key, item, self)
            if key in self.lookup:
                raise AttributeError('%s already exists!' % key)
            self.categories[key] = tmp_cat
            self.lookup[key] = tmp_cat

        for key, item in ISEMAIL_DIAG_RESPONSES.items():
            tmp_diag = self.lookup[item['category']].add_diag(key, item)
            if key in self.lookup:
                raise AttributeError('%s already exists!' % key)
            self.diags[key] = tmp_diag
            self.lookup[key] = tmp_diag

        self.error_codes = {}

        if error_on_warning:
            self.set_error_on_warning(reload=False)
        if error_on_code:
            self.set_error_on(*error_on_code, reload=False)

        self._load_codes()

        self._formatters = {}
        for f in _meta_formatters:
            self._formatters[f.report_name] = f(self)

    def set_default_format(self, format_str=None, to_desc=False, to_key=False):
        if format_str is not None:
            self.default_format = format_str
        elif to_desc:
            self.default_format = self.default_desc_format
        elif to_key:
            self.default_format = self.default_key_format

    def __getitem__(self, item):
        return self.lookup[item]

    def __contains__(self, item):
        return item in self.lookup

    def _load_codes(self):
        self.error_codes.clear()
        for c in self.diags.values():
            if c.status == ISEMAIL_RESULT_CODES.ERROR:
                self.error_codes[c.key] = c

    def clear_overrides(self):
        self.error_codes.clear()
        for c in self.categories.values(ordered=False):
            c.reset_status()
        for c in self.diags.values():
            c.reset_status()
            if c.status == ISEMAIL_RESULT_CODES.ERROR:
                self.error_codes[c.key] = c

    def set_error_on_warning(self, set_to=True, reload=True):
        for c in self.categories.values():
            if set_to and c._base_status == ISEMAIL_RESULT_CODES.WARNING:
                c.set_override_status(ISEMAIL_RESULT_CODES.ERROR)
            else:
                c.reset_status()

        if reload:
            self._load_codes()

    def set_error_on(self, *codes_to_error, reload=True):
        for code in codes_to_error:
            self._add_eo(code)
        if reload:
            self._load_codes()

    def _add_eo(self, obj_in):
        if isinstance(obj_in, (list, tuple)):
            self.set_error_on(*obj_in)
        else:
            self[obj_in].set_override_status(ISEMAIL_RESULT_CODES.ERROR)

    def status(self, diag):
        return self[diag].status

    def is_error(self, diag):
        if diag in self:
            return diag in self.error_codes
        else:
            raise KeyError('Diag %s not in system' % diag)

    def filter(self, diags=None, filter=None, show_all=True, ordered=False, return_key=False):

        if filter is not None:
            if isinstance(filter, str):
                filter = [filter]

            filter_dict = {'diags': [], 'cats': [], 'status': []}

            for f in filter:
                f = f.upper()
                if f in self.diags:
                    filter_dict['diags'].append(f)
                elif f in self.categories:
                    filter_dict['cats'].append(f)
                elif f in ('WARNING', 'ERROR', 'OK'):
                    filter_dict['status'].append(f)
                else:
                    raise AttributeError('Invalid filter string: %s' % f)
            filter = filter_dict

        if return_key:
            return self.diags.keys(show_all=show_all, filter=filter, ordered=ordered, within=diags)

        else:
            return self.diags.values(show_all=show_all, filter=filter, ordered=ordered, within=diags)

    def get_report(self, report_name, diags=None, show_all=True, filter=None, **kwargs):
        try:
            tmp_report = self._formatters[report_name]
        except KeyError:
            raise AttributeError('Report "%s" does not exist, valid reports = %r' % (report_name, self._formatters.keys()))

        tmp_diags = self.filter(diags=diags, filter=filter, show_all=show_all, ordered=True)

        return tmp_report.out(diags=tmp_diags, **kwargs)
    __call__ = get_report

    def max(self, *args):
        return self.max_obj(*args).key

    def max_obj(self, *args):
        tmp_list = []
        for a in args:
            tmp_list.append(self[a])
        return max(tmp_list)

    def max_value(self, *args):
        return self.max_obj(*args).value

    def max_status(self, *args):
        tmp_max = self.max_obj(*args)
        return tmp_max.key, tmp_max.status


META_LOOKUP = MetaLookup()

