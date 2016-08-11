
class StringParseTree(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.items = []
        self.simple = True

    def child(self):
        tmp_child = StringParseTree(self)
        self.simple = False
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

        elif c == end and not escaped:
            cur_item = cur_item.parent
            if cur_item is None:
                raise AttributeError('more closing objects than opening ones.')

        else:
            if escaped and (c != start and c != end):
                cur_item += escape_char
            cur_item += c
            escaped = False

    if cur_item.parent is not None:
        raise AttributeError('more closing chars than opening ones.')
    else:
        return cur_item.list()




ADV_BETWEENS2 = [
    ('foo',             ['foo']),
    ('foo(bar)',        ['foo', ['bar']]),
    ('(foo)bar',        [['foo'], 'bar']),
    ('fo(ob)ar',        ['fo', ['ob'], 'ar']),
    ('(foo)(bar)',      [['foo'], ['bar']]),

    ('fo/(ob/)ar',        ['fo(ob)ar']),
    ('(foo/)/(bar)',      [['foo)(bar']]),

    ('foo((ba)r)',      ['foo', [['ba'], 'r']]),
    ('(foo(b(a(r))))',  [['foo', ['b', ['a', ['r']]]]]),

    ('01234(678(9012)456)890', ['01234', ['678', ['9012'], '456'], '890']),
    ('foo(bar(snafu))foo(bar)', ['foo', ['bar', ['snafu']], 'foo', ['bar']])]


ERR_BETWEENS = [
    'te)st',
    'te(st',
    'foo(bar(foo)',
    'foo(bar))foo',
]




class TestGetBetweens(unittest.TestCase):
    def test_complex_betweens2(self):

        for test in ADV_BETWEENS2:
            with self.subTest('run_adv [%s]: %s' % (test[1], test[0])):
                tmp_ret = parse_enclosed_string(test[0], '(', ')', '/')
                self.assertEqual(test[1], tmp_ret)

        for test in ERR_BETWEENS:
            with self.subTest('error: %s' % test):
                with self.assertRaises(AttributeError):
                    tmp_ret = parse_enclosed_string(test, '(', ')', '/')