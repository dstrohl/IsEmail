
class HistoryHelper(object):
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
