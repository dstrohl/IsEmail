import unittest
from helpers.general.general import make_char_str, adv_getattr, RangeList, ListFormatter, ListFormatSpec, \
    DEFAULT_LINE_FORMAT, InterruptedRange


class TF2(object):
    test = 'tf2_test'
    tl = ['tf2_1', 'tf2_2', 'tf2_3']

    def __eq__(self, other):
        return self.test == other.test

class TF1(object):
    test = 'tf1_test'
    t2 = TF2()
    tl = ['tf1_1', 'tf1_2', TF2()]

    def __eq__(self, other):
        return self.test == other.test

tf1 = TF1()


class TestAdvGetAttr(unittest.TestCase):

    def test_adv_get_attr(self):
        TESTS = [
            (1, 'string', '[2]', 'r'),
            (2, tf1, 'test', 'tf1_test'),
            (3, tf1, 't2', TF2),
            (4, tf1, 't2.test', 'tf2_test'),
            (5, tf1, 'test[2]', '1'),
            (6, tf1, 'tl[2].test', 'tf2_test'),
            (7, tf1, 't2.tl[0]', 'tf2_1'),
        ]

        for test in TESTS:
            with self.subTest(str(test[0])):
                self.assertEqual(adv_getattr(test[1], test[2]), test[3])


class TestMakeParseString(unittest.TestCase):

    def test_make_string(self):
        tmp_res = make_char_str('foobar')
        self.assertEqual('foobar', tmp_res)

    def test_from_int(self):
        tmp_res = make_char_str(65, 66, 67)
        self.assertEqual('ABC', tmp_res)

    def test_from_string(self):
        tmp_res = make_char_str('ABC', '123')
        self.assertEqual('ABC123', tmp_res)

    def test_from_int_range(self):
        tmp_res = make_char_str((65, 67), (97, 99))
        self.assertEqual('ABCabc', tmp_res)


class TestRangeList(unittest.TestCase):

    def test_range_list(self):
        rl = RangeList()
        self.assertIsNone(rl.get(0))
        self.assertIsNone(rl.get(10))
        self.assertIsNone(rl.get(100))

        rl.add('test1')
        self.assertEqual('test1', rl.get(0))
        self.assertEqual('test1', rl.get(1))
        self.assertEqual('test1', rl.get(10))
        self.assertEqual('test1', rl.get(100))

        rl.add('test2', 1)
        self.assertEqual('test1', rl.get(0), repr(rl))
        self.assertEqual('test2', rl.get(1))
        self.assertEqual('test2', rl.get(10))
        self.assertEqual('test2', rl.get(100))

        rl.add('test3', 10)
        self.assertEqual('test1', rl.get(0))
        self.assertEqual('test2', rl.get(1))
        self.assertEqual('test3', rl.get(10))
        self.assertEqual('test3', rl.get(100))

class TestListFormatSpec(unittest.TestCase):

    def test_def_format_spec(self):
        lfs = ListFormatSpec()

        self.assertEqual(len(lfs), len(DEFAULT_LINE_FORMAT))
        for k, i in lfs.items():
            with self.subTest(k):
                self.assertEqual(DEFAULT_LINE_FORMAT[k], i)

    def test_changed_format_spec(self):

        test_dict = {'item_join': 'foobar', 'indent': 1}
        lfs = ListFormatSpec(line_join=', ', **test_dict)

        self.assertEqual(len(lfs), len(DEFAULT_LINE_FORMAT))
        self.assertEqual('foobar', lfs['item_join'])
        self.assertEqual(', ', lfs['line_join'])
        self.assertEqual(None, lfs['max_line_len'])
        self.assertEqual(1, lfs['indent'])

        self.assertEqual(test_dict, lfs.unique)

    def test_error_on_invalid_field(self):
        with self.assertRaises(AttributeError):
            lfs = ListFormatSpec({'item_join': 'foobar', 'foobar': 1})


class TestListFormatter(unittest.TestCase):

    def test_base(self):
        lf = ListFormatter()
        self.assertEqual('No Items', str(lf))
        lf('line1', 'line2')
        self.assertEqual('line1, line2', str(lf))

    def test_format(self):
        lf = ListFormatter('{foo}-{bar}')
        self.assertEqual('No Items', str(lf))
        d1 = {'foo': 'l1.1', 'bar': 'l1.2'}
        d2 = {'foo': 'l2.1', 'bar': 'l2.2'}

        self.assertEqual('l1.1-l1.2, l2.1-l2.2', lf(d1, d2).as_str())

    def test_indent(self):
        lf = ListFormatter('{foo}-{bar}', specs={'indent': 2})
        self.assertEqual('  No Items', str(lf))
        d1 = {'foo': 'l1.1', 'bar': 'l1.2'}
        d2 = {'foo': 'l2.1', 'bar': 'l2.2'}

        self.assertEqual('  l1.1-l1.2, l2.1-l2.2', lf(d1, d2).as_str())

    def test_join_items(self):
        lf = ListFormatter('{foo}-{bar}', specs={'indent': 2, 'item_join': '\n'})
        self.assertEqual('  No Items', str(lf))
        d1 = {'foo': 'l1.1', 'bar': 'l1.2'}
        d2 = {'foo': 'l2.1', 'bar': 'l2.2'}

        self.assertEqual('  l1.1-l1.2\n  l2.1-l2.2', lf(d1, d2).as_str())

    def test_max_line_len(self):
        lf = ListFormatter(specs={'max_line_len': 15, 'line_join': '\n'}, do_not_cache=True)
        lf('test1', 'test2', 'test3', 'test4', 'test5')
        exp_ret = 'test1, test2\ntest3, test4\ntest5'
        self.assertEqual(exp_ret, str(lf))

    def test_max_line_count(self):
        lf = ListFormatter(specs={'max_line_count': 3, 'line_join': '\n'})
        lf('test1', 'test2', 'test3', 'test4', 'test5')
        exp_ret = 'test1, test2, test3\ntest4, test5'
        self.assertEqual(exp_ret, str(lf))

    def test_prefix(self):
        lf = ListFormatter(specs={'max_line_count': 3, 'line_join': '\n', 'prefix': 'test_prefix\n'})
        lf('test1', 'test2', 'test3', 'test4', 'test5')
        exp_ret = 'test_prefix\ntest1, test2, test3\ntest4, test5'
        self.assertEqual(exp_ret, str(lf))

    def test_postfix(self):
        lf = ListFormatter(specs={'max_line_count': 3, 'line_join': '\n',
                                  'prefix': 'test_prefix\n', 'postfix': '\ntest_postfix',
                                  'indent': 2})
        lf('test1', 'test2', 'test3', 'test4', 'test5')
        exp_ret = 'test_prefix\n  test1, test2, test3\n  test4, test5\ntest_postfix'
        self.assertEqual(exp_ret, str(lf))

    def test_indent_prefix(self):
        lf = ListFormatter(specs={'max_line_count': 3, 'line_join': '\n',
                                  'prefix': 'test_prefix\n', 'postfix': '\n{indent}test_postfix',
                                  'indent': 4, 'prefix_indent': 2, 'postfix_indent': 2})
        self.assertEqual('  test_prefix\n    No Items\n  test_postfix', str(lf))

        lf('test1', 'test2', 'test3', 'test4', 'test5')
        exp_ret = '  test_prefix\n    test1, test2, test3\n    test4, test5\n  test_postfix'
        self.assertEqual(exp_ret, str(lf))

    def test_2_specs(self):
        spec_0 = {}
        spec_1 = {'prefix': 'Item: '}
        spec_2 = {'prefix': 'Items:\n{indent}(', 'postfix': ')', 'prefix_indent': 3}

        lf = ListFormatter(specs=[spec_0, spec_2])

        exp_0 = 'No Items'
        exp_1 = 'Items:\n   (test1)'
        exp_2 = 'Items:\n   (test1, test2)'
        exp_3 = 'Items:\n   (test1, test2, test3)'

        self.assertEqual(exp_0, str(lf))
        lf('test1')
        self.assertEqual(exp_1, str(lf))
        lf('test2')
        self.assertEqual(exp_2, str(lf))
        lf('test3')
        self.assertEqual(exp_3, str(lf))


    def test_3_specs(self):
        spec_0 = {}
        spec_1 = {'prefix': 'Item: '}
        spec_2 = {'prefix': 'Items:\n{indent}(', 'postfix': ')', 'prefix_indent': 3}

        lf = ListFormatter(specs=[spec_0, spec_1, spec_2])

        exp_0 = 'No Items'
        exp_1 = 'Item: test1'
        exp_2 = 'Items:\n   (test1, test2)'
        exp_3 = 'Items:\n   (test1, test2, test3)'

        self.assertEqual(exp_0, str(lf))
        lf('test1')
        self.assertEqual(exp_1, str(lf))
        lf('test2')
        self.assertEqual(exp_2, str(lf))
        lf('test3')
        self.assertEqual(exp_3, str(lf))


class TestInterruptedRange(unittest.TestCase):

    def setUp(self):
        self.ir = InterruptedRange()
        self.ir.extend((0, 5), (10, 15), (20, 25))

    def is_in(self, *args):


    def is_not_in(self, *args):


    def test_base(self):


    def test_add_overlap(self):
        raise unittest.SkipTest('not started')

    def test_add_length(self):
        raise unittest.SkipTest('not started')

    def test_at(self):
        raise unittest.SkipTest('not started')

    def test_get(self):
        raise unittest.SkipTest('not started')

    def test_remove(self):
        raise unittest.SkipTest('not started')

    def test_copy(self):
        raise unittest.SkipTest('not started')

    def test_iter(self):
        raise unittest.SkipTest('not started')

    def test_bool(self):
        raise unittest.SkipTest('not started')

    def test_str(self):
        raise unittest.SkipTest('not started')

    def test_len(self):
        raise unittest.SkipTest('not started')

    def test_mm_add(self):
        raise unittest.SkipTest('not started')

    def test_iadd(self):
        raise unittest.SkipTest('not started')
