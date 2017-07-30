import unittest

from ValidationParser.exceptions import ParsingError, MessageListLocked
from ValidationParser.footballs import ParseResultFootball, ParsingObj
from ValidationParser.parser_messages import MESSAGE_LOOKUP
from helpers.general.test_helpers import TestCaseCompare


class TestParsingObj(unittest.TestCase):

    def make_ei(self, parse_str='abcde"fghi"jk(lm)nop', **kwargs):
        return ParsingObj(parse_str=parse_str, **kwargs)

    def test_init(self):
        ei = self.make_ei()
        self.assertEqual(str(ei), 'abcde"fghi"jk(lm)nop')

    def test_get_item(self):
        ei = self.make_ei()
        self.assertEqual(ei[:3], 'abc')

    def test_at_end(self):
        ei = self.make_ei()
        self.assertFalse(ei.at_end(19))
        self.assertTrue(ei.at_end(20))
        self.assertTrue(ei.at_end(21))
        self.assertTrue(ei.at_end(40))

    def test_is_last(self):
        ei = self.make_ei()
        self.assertFalse(ei.is_last(19))
        self.assertTrue(ei.is_last(20))
        self.assertFalse(ei.is_last(21))
        self.assertFalse(ei.is_last(40))

    def test_len(self):
        ei = self.make_ei()
        self.assertEqual(len(ei), 20)

    def test_mid(self):
        ei = self.make_ei()
        self.assertEqual(ei.mid(0, 2), 'ab')
        self.assertEqual(ei.mid(length=10), 'abcde"fghi')
        self.assertEqual(ei.mid(19), 'p')
        self.assertEqual(ei.mid(7, 4), 'ghi"')

    def test_slice(self):
        ei = self.make_ei()
        self.assertEqual(ei.slice(0, 2), 'ab')
        self.assertEqual(ei.slice(0, 10), 'abcde"fghi')
        self.assertEqual(ei.slice(19), 'p')
        self.assertEqual(ei.slice(13, -2), '(lm)n')

    def test_remaining(self):
        ei = self.make_ei()
        test_exp = list('"fghi"jk(lm)nop')
        test_ret = list(ei.remaining(5))
        self.assertEqual(test_exp, test_ret)

    def test_remaining_complex(self):
        ei = self.make_ei('abcde\\"fghi\\"jk(lm)nop')
        test_exp = list('\\"fghi\\"jk(lm)n')
        test_ret = list(ei.remaining_complex(5, end=-2))
        self.assertEqual(test_exp, test_ret)

        test_exp = list('\\"fghi\\"jk(l')
        test_ret = list(ei.remaining_complex(5, end=-2, until_char='m'))
        self.assertEqual(test_exp, test_ret)

        test_exp = list('fghijk(l')
        test_ret = list(ei.remaining_complex(5, end=-2, until_char='m', skip_quoted=True))
        self.assertEqual(test_exp, test_ret)

    def test_count(self):
        ei = self.make_ei('abcde\\"fghi\\"jk(lm)nop')
        self.assertEqual(ei.count(5, '"'), 2)
        self.assertEqual(ei.count(18, '"'), 0)
        self.assertEqual(ei.count(5, 'f'), 1)
        self.assertEqual(ei.count(5, '"', skip_quoted=True), 0)
        self.assertEqual(ei.count(5, '"', until_char='g'), 1)

    def test_find(self):
        ei = self.make_ei('abcde\\"fghi\\"jk(lm)nop')
        self.assertEqual(ei.find(0, 'c'), 2)
        self.assertEqual(ei.find(5, 'c'), -1)
        self.assertEqual(ei.find(5, '"', skip_quoted=True), -1)
        self.assertEqual(ei.find(5, '"', until_char='g'), 6)

    def test_flags(self):
        ei = self.make_ei()
        self.assertFalse(ei.flags.in_crlf)
        self.assertFalse(ei.flags.at_in_cfws)
        self.assertFalse(ei.flags.near_at_flag)

        ei.flags.in_crlf = True
        ei.flags.at_in_cfws = False
        ei.flags.near_at_flag = False

        self.assertTrue(ei.flags.in_crlf)
        self.assertFalse(ei.flags.at_in_cfws)
        self.assertFalse(ei.flags.near_at_flag)

    def test_next(self):

        TESTS = [
            ('ex_1-max-good', 'abcddd', {'begin': 3, 'look_for': '"d"', 'max_count': 3}, 3),
            ('ex_1-min-good', 'abcddd', {'begin': 3, 'look_for': '"d"', 'min_count': 2}, 3),
            ('ex_1-min-under', 'abddefghi', {'begin': 3, 'look_for': '"d"', 'min_count': 3}, 0),
            ('ex_1-mm-bad_caps', 'abcddd', {'begin': 3, 'look_for': '"D"', 'min_count': 2, 'max_count': 5}, 0),
            ('ex_1-mm-good', 'abcddd', {'begin': 3, 'look_for': '"d"', 'min_count': 2, 'max_count': 3}, 3),
            ('ex_1-mm-nocaps-good', 'ABCDDD', {'begin': 3, 'look_for': '"d"', 'min_count': 1, 'max_count': 3, 'caps_sensitive': False}, 3),
            ('ex_1-mm-under', 'abcdefghi', {'begin': 3, 'look_for': '"d"', 'min_count': 2, 'max_count': 5}, 0),
            ('ex_1-x-bad', 'abcefghij', {'begin': 3, 'look_for': '"d"'}, 0),
            ('ex_1-x-good', 'abcddd', {'begin': 3, 'look_for': '"d"'}, 3),
            ('ex_m-max-good', 'abcdefdefdef', {'begin': 3, 'look_for': '"def"', 'max_count': 2}, 6),
            ('ex_m-min-good', 'abcdefdefdef', {'begin': 3, 'look_for': '"def"', 'min_count': 2}, 9),
            ('ex_m-min-under', 'abcdefdefghi', {'begin': 3, 'look_for': '"def"', 'min_count': 3}, 0),
            ('ex_m-mm-good', 'abcdefdefdef', {'begin': 3, 'look_for': '"def"', 'min_count': 2, 'max_count': 3}, 9),
            ('ex_m-mm-under', 'abcdeffed', {'begin': 3, 'look_for': '"def"', 'min_count': 2, 'max_count': 5}, 0),
            ('ex_m-x-bad', 'abcfeddfghu', {'begin': 3, 'look_for': '"def"'}, 0),
            ('ex_m-x-bad_caps', 'abddefghi', {'begin': 3, 'look_for': '"DEF"', 'caps_sensitive': True}, 0),
            ('ex_m-x-good', 'abcdefdefdef', {'begin': 3, 'look_for': '"def"'}, 9),
            ('ex_m-x-nocaps-good', 'ABCDEFDEFDEFGHI', {'begin': 3, 'look_for': '"def"', 'caps_sensitive': False}, 9),
            ('in_1-max-good', 'abcdddefghi', {'begin': 3, 'look_for': 'd', 'max_count': 2}, 2),
            ('in_1-min-bad_caps', 'abcdefghi', {'begin': 3, 'look_for': 'D', 'min_count': 1}, 0),
            ('in_1-min-good', 'abcdddefghi', {'begin': 3, 'look_for': 'd', 'min_count': 2}, 3),
            ('in_1-min-nocaps-good', 'abcDdDefghi', {'begin': 3, 'look_for': 'd', 'min_count': 2, 'caps_sensitive': False}, 3),
            ('in_1-min-under', 'abcdefdd', {'begin': 3, 'look_for': 'd', 'min_count': 2}, 0),
            ('in_1-mm-good', 'abcdddefghi', {'begin': 3, 'look_for': 'd', 'min_count': 2, 'max_count': 3}, 3),
            ('in_1-mm-under', 'abcdefghi', {'begin': 3, 'look_for': 'd', 'min_count': 2, 'max_count': 4}, 0),
            ('in_1-x-bad', 'abcghi', {'begin': 3, 'look_for': 'd'}, 0),
            ('in_1-x-good', 'abcdddefghi', {'begin': 3, 'look_for': 'd'}, 3),
            ('in_m-max-good', 'abcdddefghi', {'begin': 3, 'look_for': 'def', 'max_count': 2}, 2),
            ('in_m-max-nocaps-good', 'abcDDeDfghi', {'begin': 3, 'look_for': 'def', 'max_count': 2, 'caps_sensitive': False}, 2),
            ('in_m-min-good', 'abcdddefghi', {'begin': 3, 'look_for': 'def', 'min_count': 2}, 5),
            ('in_m-min-under', 'abdfeghi', {'begin': 3, 'look_for': 'def', 'min_count': 3}, 0),
            ('in_m-mm-good', 'abcdddefghi', {'begin': 3, 'look_for': 'def', 'min_count': 2, 'max_count': 3}, 3),
            ('in_m-mm-under', 'abcdefdghi', {'begin': 3, 'look_for': 'def', 'min_count': 5, 'max_count': 10}, 0),
            ('in_m-x-bad', 'abdghijkl', {'begin': 3, 'look_for': 'def'}, 0),
            ('in_m-x-good', 'abcdddefghi', {'begin': 3, 'look_for': 'def'}, 5),
        ]

        LIMIT_TO = None
        # LIMIT_TO = 'ex_1-min-good'

        if LIMIT_TO is not None:
            with self.subTest('LIMITED TEST'):
                self.fail()
        for test in TESTS:
            with self.subTest(test[0]):
                if LIMIT_TO is not None and test[0] != LIMIT_TO:
                    continue
                ei = self.make_ei(test[1])
                tmp_fb = ei(**test[2])
                self.assertEqual(tmp_fb.l, test[3], repr(tmp_fb))


    # Manual check this one
    # def test_trace(self):
    #     ei = self.make_ei()
    #     fb = ParseResultFootball(ei, 'test', 0)
    #     ei.begin_stage('s1', 0)
    #     ei.begin_stage('s1.1', 0)
    #     ei.end_stage(fb)
    #     ei.end_stage(fb)
    #
    #     tmp_ret = str(ei.trace)
    #     exp_ret = 'TRACE 20: (4/4 records, 0.0 seconds)\n(*** Including lines 1 to 4 ***)\n' \
    #               '----------------------------------------------\nBegin s1: scanning from 0: ' \
    #               '->\'abcde"fghi"jk(lm)nop\'<-\n    Begin s1.1: scanning from 0: ->' \
    #               '\'abcde"fghi"jk(lm)nop\'<-\n    End s1.1: UN-MATCHED : <test>(not found)\n' \
    #               'End s1: UN-MATCHED : <test>(not found)\n----------------------------------------------'
    #
    #     self.assertEqual(tmp_ret, exp_ret, msg=repr(tmp_ret))


class TestParseFootball(TestCaseCompare):

    @staticmethod
    def fb(*msgs, parse_str='abcdefghijklmnop', po=None, segment='test', begin=0, length=0, max_length=0):
        if po is None:
            po = ParsingObj(parse_str)
        fb = ParseResultFootball(po, segment, begin)
        if max_length:
            fb._max_length = max_length
        if msgs:
            fb(*msgs)
        if length:
            fb.set_length(length)
        return fb

    @staticmethod
    def po(parse_str='abcdefghijklmnop', **kwargs):
        return ParsingObj(parse_str, **kwargs)

    def setUp(self):
        MESSAGE_LOOKUP.clear_overrides()

    def test_init_options(self):
        f = self.fb()
        self.assertEqual(f.length, 0)

        f += 10
        self.assertEqual(f.length, 10)

        f -= 5
        self.assertEqual(f.length, 5)

    def test_math(self):
        f = self.fb()
        f2 = self.fb()

        self.assertEqual(f.length, 0)

        f += 10
        self.assertEqual(f.length, 10)

        f2 += 10
        f2 += f
        self.assertEqual(f2.length, 20)

    def test_math_2(self):
        f = self.fb()

        self.assertEqual(f + 2, 2)
        self.assertEqual(2 + f, 2)

        f += 10
        self.assertEqual(f + 2, 12)
        self.assertEqual(2 + f, 12)

        f2 = self.fb()
        f2 += 5

        self.assertEqual(f + f2, 15)
        self.assertEqual(f2 + f, 15)

    def test_init_length(self):
        f = self.fb(length=10)

        self.assertEqual(f.length, 10)

    def test_init_length_full(self):

        f = self.fb(length=13, begin=20, segment='hello')

        self.assertEqual(f.length, 13)

    def test_compare(self):

        TESTS = [
            # (key, item, value),
            ('B-0-0-0', self.fb(length=0), 0),
            ('B-5-5-0', self.fb(length=5), 305050),
            ('B-10-10-0', self.fb(length=10), 310100),
            ('B-15-15-0', self.fb(length=15), 315150),
            ('B-20-20-0', self.fb(length=20), 320200),
            ('E-0-0-2', self.fb('ERROR', 'TOO_LONG'), 2),
            ('E-0-0-3', self.fb('ERROR', 'VALID', 'WARNING'), 3),
            ('E-5-5-1', self.fb('ERROR', length=5), 5051),
            ('E-10-10-1', self.fb('ERROR', length=10), 10101),
            ('E-10-10-2', self.fb('ERROR', 'TOO_LONG', length=10), 10102),
            ('E-10-10-3', self.fb('ERROR', 'VALID', 'WARNING', length=10), 10103),
            ('E-15-5-1', self.fb('ERROR', length=5, max_length=15), 15051),
            ('E-15-5-2', self.fb('ERROR', 'TOO_LONG', length=5, max_length=15), 15052),
            ('E-15-5-3', self.fb('ERROR', 'VALID', 'WARNING', length=5, max_length=15), 15053),
            ('E-15-10-1', self.fb('ERROR', length=10, max_length=15), 15101),
            ('E-15-10-2', self.fb('ERROR', 'TOO_LONG', length=10, max_length=15), 15102),
            ('E-15-10-3', self.fb('ERROR', 'VALID', 'WARNING', length=10, max_length=15), 15103),
            ('E-20-5-1', self.fb('ERROR', length=5, max_length=20), 20051),
            ('E-20-5-2', self.fb('ERROR', 'TOO_LONG', length=5, max_length=20), 20052),
            ('E-20-5-2', self.fb('ERROR', 'TOO_LONG', length=5, max_length=20), 20052),
            ('E-20-5-3', self.fb('ERROR', 'VALID', 'WARNING', length=5, max_length=20), 20053),
            ('E-20-5-3', self.fb('ERROR', 'VALID', 'WARNING', length=5, max_length=20), 20053),
            ('E-20-10-1', self.fb('ERROR', length=10, max_length=20), 20101),
            ('E-20-10-2', self.fb('ERROR', 'TOO_LONG', length=10, max_length=20), 20102),
            ('E-20-10-3', self.fb('ERROR', 'VALID', 'WARNING', length=10, max_length=20), 20103),
            ('W-0-0-1', self.fb('DEPRECATED'), 200001),
            ('W-0-0-2', self.fb('WARNING', 'DEPRECATED'), 200002),
            ('W-0-0-3', self.fb('WARNING', 'VALID', 'DEPRECATED'), 200003),
            ('W-5-5-1', self.fb('WARNING', length=5), 205051),
            ('W-10-10-1', self.fb('WARNING', length=10), 210101),
            ('W-10-10-2', self.fb('WARNING', 'DEPRECATED', length=10), 210102),
            ('W-10-10-3', self.fb('WARNING', 'VALID', 'DEPRECATED', length=10), 210103),
            ('W-15-5-1', self.fb('WARNING', length=5, max_length=15), 215051),
            ('W-15-5-2', self.fb('WARNING', 'DEPRECATED', length=5, max_length=15), 215052),
            ('W-15-5-3', self.fb('WARNING', 'VALID', 'DEPRECATED', length=5, max_length=15), 215053),
            ('W-15-10-1', self.fb('WARNING', length=10, max_length=15), 215101),
            ('W-15-10-2', self.fb('WARNING', 'DEPRECATED', length=10, max_length=15), 215102),
            ('W-15-10-3', self.fb('WARNING', 'VALID', 'DEPRECATED', length=10, max_length=15), 215103),
            ('W-20-5-1', self.fb('WARNING', length=5, max_length=20), 220051),
            ('W-20-5-2', self.fb('WARNING', 'DEPRECATED', length=5, max_length=20), 220052),
            ('W-20-5-2', self.fb('WARNING', 'DEPRECATED', length=5, max_length=20), 220052),
            ('W-20-5-3', self.fb('WARNING', 'VALID', 'DEPRECATED', length=5, max_length=20), 220053),
            ('W-20-5-3', self.fb('WARNING', 'VALID', 'DEPRECATED', length=5, max_length=20), 220053),
            ('W-20-10-1', self.fb('WARNING', length=10, max_length=20), 220101),
            ('W-20-10-2', self.fb('WARNING', 'DEPRECATED', length=10, max_length=20), 220102),
            ('W-20-10-3', self.fb('WARNING', 'VALID', 'DEPRECATED', length=10, max_length=20), 220103),
            ('O-0-0-1', self.fb('VALID'), 300001),
            ('O-5-5-1', self.fb('VALID', length=5), 305051),
            ('O-10-10-1', self.fb('VALID', length=10), 310101),
            ('O-15-5-1', self.fb('VALID', length=5, max_length=15), 315051),
            ('O-15-10-1', self.fb('VALID', length=10, max_length=15), 315101),
            ('O-20-5-1', self.fb('VALID', length=5, max_length=20), 320051),
            ('O-20-10-1', self.fb('VALID', length=10, max_length=20), 320101),
        ]

        self.assertComparisons(TESTS)  # , limit='E-0-0-0 > E-0-0-2')

    def test_comp_with_int(self):
        f = self.fb(length=10)

        self.assertTrue(f > 5)
        self.assertTrue(f >= 10)
        self.assertTrue(f == 10)
        self.assertTrue(f != 20)
        self.assertTrue(f < 21)
        self.assertTrue(f <= 10)

    def test_comp_with_fb(self):
        f = self.fb(length=10)
        f10 = self.fb(length=10)
        f5 = self.fb(length=5)
        f20 = self.fb(length=20)

        self.assertTrue(f > f5)
        self.assertTrue(f >= f10)
        self.assertTrue(f == f10)
        self.assertTrue(f != f20)
        self.assertTrue(f < f20)
        self.assertTrue(f <= f10)

    def test_add_msg_str(self):
        per = self.fb()
        per.add('VALID')

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_bad_msg(self):
        po = self.po(locked=True)
        per = self.fb(po=po)
        with self.assertRaises(MessageListLocked):
            per.add('FOOBAR')

    # def test_add_msg_tuple(self):
    #     per = self.fb()
    #     per.add(('VALID',1))
    # 
    #     tmp_ret = 'VALID' in per
    #     self.assertTrue(tmp_ret)

    def test_add_msg_dict(self):
        per = self.fb()
        per.add({'key': 'VALID', 'description': 'this is blah'}, 1, msg_length=1)
        per += 1
        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_length_set(self):
        per = self.fb()
        per += 3
        self.assertEqual(per.l, 3)
        per.add('VALID').set_length(1)

        self.assertEqual(per.l, 1)

    def test_add_football(self):
        per = self.fb()
        per += 1

        per2 = self.fb()
        per += 3

        per.add(per2)

        self.assertEqual(per.l, 4)

    def test_add_length_add(self):
        per = self.fb()
        per += 1
        self.assertEqual(per.l, 1)
        per.add('VALID', 1, msg_length=1)

        self.assertEqual(per.l, 2)

    def test_add_ok_result(self):
        per = self.fb(parse_str='test_email_in', begin=1)

        per.add('VALID')

        self.assertFalse(per.error)

    def test_add_error_result(self):
        per = self.fb(parse_str='test_email_in')

        with self.assertRaises(ParsingError):
            per.add('ERROR', raise_on_error=True)

        per.add('ERROR')
        self.assertTrue(per.error)
        self.assertFalse(per)

    def test_add_warn_result(self):
        per = self.fb(parse_str='test_email_in')

        per.add('WARNING', msg_begin=1, msg_length=1)
        self.assertFalse(per.error)

    def test_add_mult_result(self):
        per = self.fb(parse_str='test_email_in')

        # self.assertTrue(per)
        # self.assertEqual(len(per), 0)

        per.add('VALID', 1, msg_begin=1, msg_length=1)
        self.assertEqual(len(per), 1)
        self.assertFalse(per.error)

        per.add('WARNING', msg_begin=1, msg_length=1)
        # self.assertTrue(per)
        self.assertEqual(len(per), 2)
        self.assertFalse(per.error)

        per.add('ERROR', msg_begin=1, msg_length=1)
        self.assertTrue(per.error)

        per.add('WARNING', msg_begin=1, msg_length=1)
        self.assertTrue(per.error)

    def test_error_on_warn(self):
        po = self.po(error_on_warning=True, raise_on_error=True)
        per = self.fb(parse_str='test_email_in', po=po)

        per.add('VALID', msg_begin=1, msg_length=1)
        self.assertFalse(per.error)

        with self.assertRaises(ParsingError):
            per.add('WARNING', msg_begin=1, msg_length=1)
        self.assertTrue(per.error)

        per.add('VALID', msg_begin=1, msg_length=1)
        self.assertTrue(per.error)

    def test_error_on_value(self):
        po = self.po(error_on_message=['DEPRECATED'])
        per = self.fb(parse_str='test_email_in', po=po)
        per('WARNING')
        with self.assertRaises(ParsingError):
            per('DEPRECATED', raise_on_error=True)
        self.assertTrue(per.error)

    def test_contains(self):
        per = self.fb('test_email_in')

        per(('VALID', 1, 1))
        per({'key': 'SNAFU', 'description': 'This is a test'}, msg_begin=1, msg_length=1)
        per('DEPRECATED')
        per('TOO_LONG')

        self.assertIn('DEPRECATED', per)

        self.assertNotIn('foobar', per)

    # def test_clear(self):
    #     per = self.fb('test_email_in')
    #
    #     self.assertEqual(len(per), 0)
    #     per += 10
    #
    #     per.add(msg=('VALID', 1, 1))
    #     per.add(msg={'msg':'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
    #     per.add(msg='DEPREC_QTEXT', raise_on_error=False)
    #     per.add(msg='DNSWARN_NO_MX_RECORD')
    #
    #     self.assertEqual(len(per), 4)
    #     self.assertEqual(per.l, 10)
    #     per.clear()
    #
    #     self.assertEqual(len(per), 0)
    #     self.assertEqual(per.l, 0)

    def test_remove(self):
        per = self.fb()

        per += 10

        per.add('VALID', msg_begin=1, msg_length=1)
        per.add({'key': 'WARNING', 'begin': 1, 'length': 1})
        per.add('DEPRECATED', raise_on_error=False)
        per.add('WARNING')

        self.assertEqual(len(per), 4, repr(per))
        self.assertEqual(per.l, 10)

        per.remove('VALID')
        self.assertEqual(len(per), 3)

        per.remove('*.WARNING')
        self.assertEqual(len(per), 1)

        per.add('VALID', msg_begin=1, msg_length=1)
        per.add({'key': 'WARNING'}, msg_begin=1, msg_length=1)
        per.add('DEPRECATED', raise_on_error=False)
        per.add('TOO_LONG')

        self.assertEqual(len(per), 5, repr(per))

        per.remove('WARNING')
        self.assertEqual(len(per), 4)

    def test_max(self):
        per_ok = self.fb('VALID', length=10)
        per_warn = self.fb('WARNING', length=10)
        per_error = self.fb('ERROR', length=10)

        with self.subTest('1'):
            self.assertEqual(per_ok, per_ok.max(per_ok))
        with self.subTest('2'):
            self.assertEqual(per_ok, per_ok.max(per_warn))
        with self.subTest('3'):
            self.assertEqual(per_ok, per_ok.max(per_error))

        with self.subTest('4'):
            self.assertEqual(per_ok, per_warn.max(per_ok))
        with self.subTest('5'):
            self.assertEqual(per_warn, per_warn.max(per_warn))
        with self.subTest('6'):
            self.assertEqual(per_warn, per_warn.max(per_error))

        with self.subTest('7'):
            self.assertEqual(per_ok, per_error.max(per_ok))
        with self.subTest('8'):
            self.assertEqual(per_warn, per_error.max(per_warn))
        with self.subTest('9'):
            self.assertEqual(per_error, per_error.max(per_error))
