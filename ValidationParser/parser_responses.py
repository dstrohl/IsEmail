__all__ = ['ParseFullResult', 'ParseShortResult']

from ValidationParser.parser_messages import STATUS_CODES
from copy import deepcopy


class ParseShortResult(object):
    """
    returns:
        - parse_str
        - max_message
        - max_status
        - history_str
    """
    def __init__(self, football):
        self.parse_str = football.parse_obj.parse_str
        self.parsed_str = str(football)
        self.history_str = football.history
        self.status = football.max_status
        self.max_message = football._messages.max_msg

        self.error = self.status == STATUS_CODES.ERROR
        self.ok = self.status == STATUS_CODES.OK
        self.warning = self.status == STATUS_CODES.WARNING

    def __repr__(self):
        return 'ParseResult: %s: [%s] %s' % (self.status.name, self.max_message.key, self.parsed_str)

    def __str__(self):
        return self.parsed_str

    def __bool__(self):
        return not self.error

    def __len__(self):
        return len(self.parsed_str)


class ParseFullResult(ParseShortResult):
    """
    returns:
        - parse_str
        - messages
        - history_str
        - trace
    """

    def __init__(self, football):
        super().__init__(football)
        self.messages = deepcopy(football._messages)
        self.history = deepcopy(football._history)
        self.trace = deepcopy(football.parse_obj.trace)
        self.data = deepcopy(football.data)

    """
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
    """
    def __repr__(self):
        tmp_str = super().__repr__()
        tmp_str += ' [%s]' % self.messages
        return tmp_str

    def __contains__(self, item):
        return item in self.history

    """
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
    """