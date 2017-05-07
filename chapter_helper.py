
def number_to_alpha(num, uppper_case=True, start_at=1):

    if num < start_at:
        raise AttributeError('number passed (%s) is lower than the start_at point (%s)' % (num, start_at))
    tmp_col_let = ''
    if uppper_case:
        start_char = 65
    else:
        start_char = 97
    num = num - start_at + 1

    while num > 0:
        mod = int((num - 1) % 26)
        tmp_col_let = chr(start_char + mod) + tmp_col_let
        num = int((num - mod) / 26)
    return tmp_col_let


def alpha_to_number(alpha, start_at=1):
    alpha = alpha.upper()
    tmp_ret = 0
    for c in alpha:
        tmp_ret *= 26
        tmp_ret += ord(c) - ord('A') + 1
    tmp_ret = tmp_ret - 1 + start_at
    return tmp_ret

class ChapterHelper(object):
    def __init__(self, pattern=None):
        """
        pattern = 'A1a'
        :param patterm:
        """
        self._pattern = pattern
        self._base_pattern = pattern
        self._curr_level = -1
        self._outline = []
        self._outline_output = []

    def add(self):
        try:
            self._outline[-1] += 1
            self._fix_last()
            return '.'.join(self._outline_output)
        except IndexError:
            return self.add_level()

    def add_level(self):
        self._outline.append(1)
        self._curr_level += 1
        self._outline_output.append('')
        self._fix_last()
        return '.'.join(self._outline_output)

    def rem_level(self):
        if self._curr_level == 0:
            raise IndexError('Trying to remove last level')
        self._outline.pop()
        self._outline_output.pop()
        self._curr_level -= 1
        self.add()
        self._fix_last()
        return '.'.join(self._outline_output)

    def _fix_last(self):
        try:
            tmp_fmt = self._pattern[self._curr_level]
        except IndexError:
            self._pattern += self._base_pattern
            tmp_fmt = self._pattern[self._curr_level]

        if tmp_fmt == '1':
            self._outline_output[self._curr_level] = str(self._outline[self._curr_level])
        elif tmp_fmt == 'A':
            self._outline_output[self._curr_level] = number_to_alpha(self._outline[self._curr_level])
        elif tmp_fmt == 'a':
            self._outline_output[self._curr_level] = number_to_alpha(self._outline[self._curr_level], uppper_case=False)

    def _output(self):
        return '.'.join(self._outline_output)
    __str__ = _output

    def __repr__(self):
        return 'ChapterHelper(%s, pattern=%s)' % (self._outline, self._base_pattern)



class TestChapterHelper(unittest.TestCase):

    def test_chapter_helper(self):

        TESTS = [
            # (index, command, '1', 'a', 'A', '1Aa', '1a')
            (1, 'add', '1', 'a', 'A', '1', '1'),
            (2, 'add', '2', 'b', 'B', '2', '2'),
            (3, 'add_level', '2.1', 'b.a', 'B.A', '2.A', '2.a'),
            (4, 'add', '2.2', 'b.b', 'B.B', '2.B', '2.b'),
            (5, 'add', '2.3', 'b.c', 'B.C', '2.C', '2.c'),
            (6, 'add', '2.4', 'b.d', 'B.D', '2.D', '2.d'),
            (7, 'add_level', '2.4.1', 'b.d.a', 'B.D.A', '2.D.a', '2.d.1'),
            (8, 'add', '2.4.2', 'b.d.b', 'B.D.B', '2.D.b', '2.d.2'),
            (9, 'rem_level', '2.5', 'b.e', 'B.E', '2.E', '2.e'),
            (10, 'add_level', '2.5.1', 'b.e.a', 'B.E.A', '2.E.a', '2.e.1'),
            (11, 'add', '2.5.2', 'b.e.b', 'B.E.B', '2.E.b', '2.e.2'),
            (12, 'rem_level', '2.6', 'b.f', 'B.F', '2.F', '2.f'),
            (13, 'rem_level', '3', 'c', 'C', '3', '3'),
            (14, 'add', '4', 'd', 'D', '4', '4'),
            (15, 'add_level', '4.1', 'd.a', 'D.A', '4.A', '4.a'),
            (16, 'add_level', '4.1.1', 'd.a.a', 'D.A.A', '4.A.a', '4.a.1'),
            (17, 'add_level', '4.1.1.1', 'd.a.a.a', 'D.A.A.A', '4.A.a.1', '4.a.1.a'),
            (18, 'add_level', '4.1.1.1.1', 'd.a.a.a.a', 'D.A.A.A.A', '4.A.a.1.A', '4.a.1.a.1'),
            (19, 'add_level', '4.1.1.1.1.1', 'd.a.a.a.a.a', 'D.A.A.A.A.A', '4.A.a.1.A.a', '4.a.1.a.1.a'),
            (20, 'add_level', '4.1.1.1.1.1.1', 'd.a.a.a.a.a.a', 'D.A.A.A.A.A.A', '4.A.a.1.A.a.1', '4.a.1.a.1.a.1'),
        ]

        TEST_FORMATS = ['1', 'a', 'A', '1Aa', '1a']

        LIMIT_TO = None

        # if LIMIT_TO is not None:
        #     with self.subTest('Limited Test Run'):
        #         self.fail()

        for exp_index, fmt in enumerate(TEST_FORMATS, 2):
            ch = ChapterHelper(pattern=fmt)
            for test in TESTS:
                test_name = '%s-%s' % (test[0], fmt)
                # with self.subTest(test_name):
                # print(test_name)
                if LIMIT_TO is not None and LIMIT_TO == test_name:
                    print('test_point')

                if test[1] == 'add':
                    tmp_ret = ch.add()
                elif test[1] == 'add_level':
                    tmp_ret = ch.add_level()
                else:
                    tmp_ret = ch.rem_level()

                # print('\nexpected: %s\nreturned: %s\n' % (test[exp_index], tmp_ret))

                self.assertEqual(tmp_ret, test[exp_index], msg=repr(ch))


class TestNumToAlpha(unittest.TestCase):

    def test_num_to_alpha(self):
        for i in range(1, 1000):
            tmp_char = number_to_alpha(i)
            tmp_num = alpha_to_number(tmp_char)
            # print('%s = %s' % (tmp_char, tmp_num))
            self.assertEqual(tmp_num, i, msg='Character = ' + tmp_char)

    def test_num_to_alpha_lowercase(self):
        for i in range(1, 1000):
            tmp_char = number_to_alpha(i, uppper_case=False)
            tmp_num = alpha_to_number(tmp_char)
            # print('%s = %s' % (tmp_char, tmp_num))
            self.assertEqual(tmp_num, i, msg='Character = %r' % tmp_char)

    def test_num_to_alpha_zero_offset(self):
        for i in range(1, 1000):
            tmp_char = number_to_alpha(i, start_at=0)
            tmp_num = alpha_to_number(tmp_char, start_at=0)
            # print('num_2_alpha(%s) = %r' % (i, tmp_char))
            # print('alpha_2_num(%r) = %s' % (tmp_char, tmp_num))
            # print('')
            # print('%s = %s' % (tmp_char, tmp_num))
            self.assertEqual(tmp_num, i, msg='Character = %r' % tmp_char)

    def test_num_to_alpha_5_offset(self):
        for i in range(10, 1000):
            tmp_char = number_to_alpha(i, start_at=10)
            tmp_num = alpha_to_number(tmp_char, start_at=10)
            # print('num_2_alpha(%s) = %r' % (i, tmp_char))
            # print('alpha_2_num(%r) = %s' % (tmp_char, tmp_num))
            # print('')
            self.assertEqual(tmp_num, i, msg='Character = %r' % tmp_char)

    def test_num_too_low_raises(self):
        with self.assertRaises(AttributeError):
            tmp_char = number_to_alpha(1, start_at=10)

