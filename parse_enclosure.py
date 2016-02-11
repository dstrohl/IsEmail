
class StringParseTree(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.items = []

    def child(self):
        tmp_child = StringParseTree(self)
        self.items.append(tmp_child)
        return tmp_child

    def __iadd__(self, other):
        if not self.items or not isinstance(self.items[-1], str):
            self.items.append('')
        self.items[-1] += other
        return self

    def list(self):
        tmp_ret = []
        for i in self.items:
            if isinstance(i, str):
                tmp_ret.append(i)
            else:
                tmp_ret.append(i.list())
        return tmp_ret

def parse_enclosed_string(string_in, start, end, escape_char=None):
    cur_item = StringParseTree()
    if escape_char is None:
        escapable = False
    else:
        escapable = True
    escaped = False

    for c in string_in:
        if escapable and c == escape_char:
            escaped = True

        elif c == start and not escaped:
            cur_item = cur_item.child()

            # tmp_parent = tmp_working_item
            # tmp_working_item.append([''])
            # tmp_working_item = tmp_working_item[-1]
            #tmp_item_stack.append(''.join(tmp_working_item))
            # tmp_item_stack.append([])

        elif c == end and not escaped:
            cur_item = cur_item.parent
            if cur_item is None:
                raise AttributeError('more closing objects than opening ones.')

            # tmp_parent =
            # tmp_item_stack.append(''.join(tmp_working_item))
            # try:
            #     tmp_ret_list.append(tmp_item_stack.pop())
            # except IndexError:

        else:
            if escaped and (c != start and c != end):
                cur_item += escape_char
            cur_item += c
            escaped = False

    if cur_item.parent is not None:
        raise AttributeError('more closing chars than opening ones.')
    else:
        return cur_item.list()

