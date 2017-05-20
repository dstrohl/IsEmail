
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