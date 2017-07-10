from helpers.parser_helpers.parser_messages import *
from unittest import TestCase
from helpers.general import show_compared_items

test_msg_2 = {'key': 'test_msg_2', 'description': 'This is test msg 2', 'status': RESULT_CODES.WARNING, 'references': ['test_ref']}
test_msg_3 = {'key': 'test_msg_3', 'description': 'tm3_desc', 'status': RESULT_CODES.OK, 'references': 'test_ref_2'}

TEST_MESSAGES = ['TEST_MSG_1', test_msg_2, test_msg_3]

TEST_SEGMENTS = [
    {'key': 'test_segment', 'status_override': RESULT_CODES.OK, 'description': 'segment description'},
    {'key': 'test_segment2', 'name': 'Test Segment Two', 'status_override': RESULT_CODES.OK, 'description': 'segment description'},
    {'key': 'test_segment3', 'name': 'Test Segment Three', 'description': 'segment_desc'},
    {'key': 'test_seg_5', 'description': 'test_desc_5', 'references': ['test_ref_2', 'test_ref_3']}
]

TEST_REFERENCES = [
    'test_ref_1',
    {'key': 'test_ref_2', 'description': 'ref_2_desc', 'url': 'ref_2_url', 'text': 'ref_2_text'},
    {'key': 'test_ref_3', 'name': 'test reference 3', 'description': 'ref_3_desc', 'url': 'ref_3_url', 'text': 'ref_3_text'}
]


def make_msg(expected, returned):
    tmp_ret = ['','']
    tmp_ret.append('Expected: %r' % expected)
    tmp_ret.append('Returned: %r' % returned)

    if isinstance(expected, str) and isinstance(returned, str):
        tmp_ret.append('')
        tmp_ret.append('Strings:')
        tmp_ret.append('Expected:\n%s' % expected)
        tmp_ret.append('Returned:\n%s' % returned)

    return '\n'.join(tmp_ret)

class TestMessageLookup(TestCase):

    def setUp(self):
        MESSAGE_LOOKUP.clear()
        # print(MESSAGE_LOOKUP.dump())

    def test_get_len(self):
        self.assertEqual(MESSAGE_LOOKUP.len(), 19, MESSAGE_LOOKUP.dump())

    def test_get_msg(self):
        tmp_msg = MESSAGE_LOOKUP.message('test_segment.VALID')
        self.assertEqual(tmp_msg.key, 'VALID')
        self.assertEqual(tmp_msg.status, RESULT_CODES.OK)

    def test_get_new_msg(self):
        tmp_msg = MESSAGE_LOOKUP.message('test_segment', 'test_new_message')
        self.assertEqual(tmp_msg.key, 'test_new_message')
        self.assertEqual(tmp_msg.status, RESULT_CODES.ERROR)
        self.assertEqual(tmp_msg.name, 'Test New Message')

    def test_get_new_msg_with_kwargs(self):
        tmp_msg = MESSAGE_LOOKUP.message('test_segment', 'test_new_message', status=RESULT_CODES.OK, name='test_name')
        self.assertEqual(tmp_msg.key, 'test_new_message')
        self.assertEqual(tmp_msg['status'], RESULT_CODES.OK)
        self.assertEqual(tmp_msg.name, 'test_name')

    def test_get_segment(self):
        MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        tmp_seg = MESSAGE_LOOKUP.segment('test_segment')
        self.assertEqual(tmp_seg.key, 'test_segment')
        # self.assertEqual(tmp_seg['status_override'], RESULT_CODES.OK)
        self.assertEqual(tmp_seg.name, 'Test Segment')
        self.assertEqual(tmp_seg.description, 'segment description')

    def test_get_new_segment(self):
        tmp_seg = MESSAGE_LOOKUP.segment('test_segment')
        self.assertEqual(tmp_seg.key, 'test_segment')
        # self.assertEqual(tmp_seg['status_override'], None)
        self.assertEqual(tmp_seg.name, 'Test Segment')
        self.assertEqual(tmp_seg.description, None)

    def test_get_new_segment_with_kwargs(self):
        MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        tmp_seg = MESSAGE_LOOKUP.segment('test_segment_4', description='segment description')
        self.assertEqual(tmp_seg.key, 'test_segment_4')
        # self.assertEqual(tmp_seg['status_override'], RESULT_CODES.WARNING)
        self.assertEqual(tmp_seg.name, 'Test Segment 4')
        self.assertEqual(tmp_seg.description, 'segment description')

    def test_get_reference(self):
        MESSAGE_LOOKUP.add(references=TEST_REFERENCES)
        tmp_ref = MESSAGE_LOOKUP.get_reference('test_ref_2')
        self.assertEqual(tmp_ref.key, 'test_ref_2')
        self.assertEqual(tmp_ref.name, 'Test Ref 2')
        self.assertEqual(tmp_ref.url, 'ref_2_url')
        self.assertEqual(tmp_ref.text, 'ref_2_text')

        tmp_ref = MESSAGE_LOOKUP.get_reference('test_ref_1')
        self.assertEqual(tmp_ref.key, 'test_ref_1')
        self.assertEqual(tmp_ref.name, 'Test Ref 1')
        self.assertEqual(tmp_ref.url, '')
        self.assertEqual(tmp_ref.text, '')

    def test_get_new_reference(self):
        MESSAGE_LOOKUP.add(references=TEST_REFERENCES)
        tmp_ref = MESSAGE_LOOKUP.get_reference('test_ref_foobar')
        self.assertEqual(tmp_ref.key, 'test_ref_foobar')
        self.assertEqual(tmp_ref.name, 'Test Ref Foobar')
        self.assertEqual(tmp_ref.url, '')
        self.assertEqual(tmp_ref.text, '')

    def test_get_msg_object(self):
        MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        tmp_msg = MESSAGE_LOOKUP('test_segment3', 'DEPRECATED')
        self.assertEqual(tmp_msg.long_key, 'test_segment3.DEPRECATED')
        self.assertEqual(tmp_msg.status, RESULT_CODES.WARNING)

    def test_get_new_msg_object(self):
        MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        tmp_msg = MESSAGE_LOOKUP('test_segment3', 'foobar')
        self.assertEqual(tmp_msg.long_key, 'test_segment3.foobar')
        self.assertEqual(tmp_msg.status, RESULT_CODES.ERROR)

    def test_get_dict_msg_object(self):
        MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        tmp_msg = MESSAGE_LOOKUP('test_segment3', {'key': 'blah', 'status': RESULT_CODES.OK})
        self.assertEqual(tmp_msg.long_key, 'test_segment3.blah')
        self.assertEqual(tmp_msg.status, RESULT_CODES.OK)

    def test_set_error_on_warning(self):
        MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        MESSAGE_LOOKUP.set_error_on_warning()
        tmp_msg = MESSAGE_LOOKUP('test_segment3', 'DEPRECATED')
        self.assertEqual(tmp_msg.key, 'DEPRECATED')
        self.assertEqual(tmp_msg.status, RESULT_CODES.ERROR)

        tmp_msg = MESSAGE_LOOKUP('test_segment3', 'VALID')
        self.assertEqual(tmp_msg.long_key, 'test_segment3.VALID')
        self.assertEqual(tmp_msg.status, RESULT_CODES.OK)

    def test_override_status(self):
        MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        MESSAGE_LOOKUP.add_error_on_message('test_segment3.DEPRECATED', 'ERROR', set_to=RESULT_CODES.OK)
        tmp_msg_1 = MESSAGE_LOOKUP('test_segment3', 'DEPRECATED')
        self.assertEqual(tmp_msg_1.long_key, 'test_segment3.DEPRECATED')
        self.assertEqual(tmp_msg_1.status, RESULT_CODES.OK)

        tmp_msg_2 = MESSAGE_LOOKUP('test_segment3', 'WARNING')
        self.assertEqual(tmp_msg_2.long_key, 'test_segment3.WARNING')
        self.assertEqual(tmp_msg_2.status, RESULT_CODES.WARNING)

        tmp_msg_3 = MESSAGE_LOOKUP('test_segment2', 'ERROR')
        self.assertEqual(tmp_msg_3.long_key, 'test_segment2.ERROR')
        self.assertEqual(tmp_msg_3.status, RESULT_CODES.OK)

        tmp_msg_4 = MESSAGE_LOOKUP('test_segment4', 'ERROR')
        self.assertEqual(tmp_msg_4.long_key, 'test_segment4.ERROR')
        self.assertEqual(tmp_msg_4.status, RESULT_CODES.OK)

        MESSAGE_LOOKUP.clear_overrides()

        self.assertEqual(tmp_msg_1.long_key, 'test_segment3.DEPRECATED')
        self.assertEqual(tmp_msg_1.status, RESULT_CODES.OK)

        self.assertEqual(tmp_msg_2.long_key, 'test_segment3.WARNING')
        self.assertEqual(tmp_msg_2.status, RESULT_CODES.WARNING)

        self.assertEqual(tmp_msg_3.long_key, 'test_segment2.ERROR')
        self.assertEqual(tmp_msg_3.status, RESULT_CODES.OK)

        self.assertEqual(tmp_msg_4.long_key, 'test_segment4.ERROR')
        self.assertEqual(tmp_msg_4.status, RESULT_CODES.OK)

        tmp_msg_5 = MESSAGE_LOOKUP('test_segment3', 'DEPRECATED')
        self.assertEqual(tmp_msg_5.long_key, 'test_segment3.DEPRECATED')
        self.assertEqual(tmp_msg_5.status, RESULT_CODES.WARNING)

        tmp_msg_6 = MESSAGE_LOOKUP('test_segment3', 'WARNING')
        self.assertEqual(tmp_msg_6.long_key, 'test_segment3.WARNING')
        self.assertEqual(tmp_msg_6.status, RESULT_CODES.WARNING)

        tmp_msg_7 = MESSAGE_LOOKUP('test_segment2', 'ERROR')
        self.assertEqual(tmp_msg_7.long_key, 'test_segment2.ERROR')
        self.assertEqual(tmp_msg_7.status, RESULT_CODES.ERROR)

        tmp_msg_8 = MESSAGE_LOOKUP('test_segment4', 'ERROR')
        self.assertEqual(tmp_msg_8.long_key, 'test_segment4.ERROR')
        self.assertEqual(tmp_msg_8.status, RESULT_CODES.ERROR)


class TestMesageRecs(TestCase):

    def test_basic_message_rec(self):
        pmr = ParseMessageRec('test_key')
        self.assertEqual(pmr.key, 'test_key')
        self.assertEqual(pmr.name, 'Test Key')

    def test_add_field(self):
        pmr = ParseMessageRec('test_key')
        pmr['name'] = 'New Test'
        pmr.description = 'test desc'
        self.assertEqual(pmr.key, 'test_key')
        self.assertEqual(pmr.name, 'New Test')
        self.assertEqual(pmr.description, 'test desc')
        # self.assertEqual(pmr.status_override, None)

    def test_add_existing_field(self):
        pmr = ParseMessageRec('test_key')
        pmr['name'] = 'New Test'
        pmr['name'] = 'Another Test'
        pmr.description = 'test desc'
        pmr.description = 'foobar'
        self.assertEqual(pmr.key, 'test_key')
        self.assertEqual(pmr.name, 'New Test')
        self.assertEqual(pmr.description, 'test desc')
        # self.assertEqual(pmr.status_override, None)

    def test_add_bad_field(self):
        pmr = ParseMessageRec('test_key')
        pmr['name_2'] = 'New Test'
        with self.assertRaises(AttributeError):
            test = pmr.name_2
            self.assertEqual(test, 'foobar')

    def test_update_list(self):
        pmr = ParseMessageRec('test_key')
        pmr.references.append('test')
        pmr.references.append('test2')
        self.assertEqual(pmr.references, ['test', 'test2'])

    def test_update_dict(self):
        pmr = ParseMessageRec('test_key')
        pmr['name'] = 'New Test'
        pmr.update({'name': 'foobar', 'description': 'new desc', 'snafu': 12})
        self.assertEqual(pmr.name, 'New Test')
        self.assertEqual(pmr.description, 'new desc')

    def test_update_obj(self):
        pmr = ParseMessageRec('test_key')
        pmr['name'] = 'New Test'
        pmr2 = ParseMessageRec('t2', name='foobar2', description='another desc')
        pmr.update(pmr2)
        self.assertEqual(pmr.name, 'New Test')
        self.assertEqual(pmr.description, 'another desc')

    def test_copy(self):
        pmr = ParseMessageRec('test_key')
        pmr['name'] = 'New Test'
        pmr.description = 'test desc'
        pmr.references.append('test')
        pmr.references.append('test2')

        pmr2 = pmr.copy()

        self.assertEqual(pmr2.key, 'test_key')
        self.assertEqual(pmr2.name, 'New Test')
        self.assertEqual(pmr2.references, ['test', 'test2'])

        pmr.references.append('test3')

        pmr2.status = RESULT_CODES.OK

        self.assertEqual(pmr2.references, ['test', 'test2'])
        self.assertEqual(pmr.references, ['test', 'test2', 'test3'])

        self.assertEqual(pmr.status, RESULT_CODES.ERROR)
        self.assertEqual(pmr2.status, RESULT_CODES.OK)


class TestMessageObject(TestCase):
    maxDiff = None

    ML = MessageLookup(messages=TEST_MESSAGES, references=TEST_REFERENCES, segments=TEST_SEGMENTS)
    ML.add(messages=BASE_PARSING_MESSAGES)

    def test_strings(self):
        tm = self.ML('test_seg_5', 'test_msg_3', note='test_note')
        self.assertEqual(str(tm), 'test_seg_5.test_msg_3')
        self.assertEqual(tm.name, 'Test Msg 3')
        self.assertEqual(tm.key, 'test_msg_3')
        self.assertEqual(tm.description, 'tm3_desc')
        self.assertEqual(tm.segment_name, 'Test Seg 5')
        self.assertEqual(tm.segment_key, 'test_seg_5')
        self.assertEqual(tm.segment_description, 'test_desc_5')
        self.assertEqual(tm.long_name, 'Test Seg 5 / Test Msg 3')
        self.assertEqual(tm.long_key, 'test_seg_5.test_msg_3')
        self.assertEqual(tm.long_description, 'test_desc_5\ntm3_desc')
        # self.assertEqual(tm.full_name, 'Test Seg 5 / Test Msg 3 (test_note)')
        # self.assertEqual(tm.full_description, 'test_desc_5\ntm3_desc\ntest_note')

    def test_references(self):
        tm = self.ML('test_seg_5', 'test_msg_3', note='test_note')
        self.assertEqual(len(tm.references), 2, '%r' % tm.references)

    def test_detailed_reference_string(self):
        tm = self.ML('test_seg_5', 'test_msg_3', note='test_note')
        test_exp = 'Test Ref 2 (ref_2_desc)\nURL: ref_2_url\nref_2_text\n\ntest reference 3 (ref_3_desc)\nURL: ref_3_url\nref_3_text'
        test_ret = tm.reference_str(detailed=True)
        self.assertEqual(test_exp, test_ret, show_compared_items(test_exp, test_ret))

    def test_not_detailed_reference_string(self):
        tm = self.ML('test_seg_5', 'test_msg_3', note='test_note')
        test_exp = 'Test Ref 2 (ref_2_desc)\ntest reference 3 (ref_3_desc)'
        test_ret = tm.reference_str(detailed=False)
        self.assertEqual(test_exp, test_ret, show_compared_items(test_exp, test_ret))

    def test_bool_error(self):
        tm = self.ML('test', 'TEST_MSG_1')
        self.assertFalse(tm)

    def test_bool_warning(self):
        tm = self.ML('test', 'test_msg_2')
        self.assertTrue(tm)

    def test_bool_ok(self):
        tm = self.ML('test', 'test_msg_3')
        self.assertTrue(tm)

    def test_compare(self):

        LIMIT_TEST = None

        # LIMIT_TEST = 'tm_1.tm_6'

        TEST_DICT = dict(
            tm_1=(self.ML('test', 'TEST_MSG_1'), '4a'),  # ERROR     4a
            tm_2=(self.ML('test', 'TEST_MSG_1'), '4a'),  # ERROR     4b
            tm_3=(self.ML('test2', 'TEST_MSG_1'), '5a'),  # ERROR    5a
            tm_4=(self.ML('test', 'test_msg_2'), '3a'),  # WARNING   3a
            tm_5=(self.ML('test', 'test_msg_3'), '1a'),  # OK        1a
            tm_6=(self.ML('test', 'VALID'), '2a'),  # OK             2a
        )

        if LIMIT_TEST is not None:
            with self.subTest('LIMITED TEST'):
                self.fail()

        for l_key, l_item in TEST_DICT.items():
            l_test_obj, l_value = l_item
            for r_key, r_item in TEST_DICT.items():
                if LIMIT_TEST is not None and LIMIT_TEST != '%s.%s' % (l_key, r_key):
                    continue
                r_test_obj, r_value = r_item
                with self.subTest('%s == %s' % (l_key, r_key)):
                    self.assertEqual(l_value == r_value, l_test_obj == r_test_obj, '\n\n%r == %r\nreturns: %r' % (l_test_obj, r_test_obj, str(l_test_obj._compare_(r_test_obj))))

                with self.subTest('%s != %s' % (l_key, r_key)):
                    self.assertEqual(l_value != r_value, l_test_obj != r_test_obj, '\n\n%r != %r\nreturns: %r' % (l_test_obj, r_test_obj, str(l_test_obj._compare_(r_test_obj))))

                with self.subTest('%s > %s' % (l_key, r_key)):
                    self.assertEqual(l_value > r_value, l_test_obj > r_test_obj, '\n\n%r > %r\nreturns: %r' % (l_test_obj, r_test_obj, str(l_test_obj._compare_(r_test_obj))))

                with self.subTest('%s >= %s' % (l_key, r_key)):
                    self.assertEqual(l_value >= r_value, l_test_obj >= r_test_obj, '\n\n%r >= %r\nreturns: %r' % (l_test_obj, r_test_obj, str(l_test_obj._compare_(r_test_obj))))

                with self.subTest('%s < %s' % (l_key, r_key)):
                    self.assertEqual(l_value < r_value, l_test_obj < r_test_obj, '\n\n%r < %r\nreturns: %r' % (l_test_obj, r_test_obj, str(l_test_obj._compare_(r_test_obj))))

                with self.subTest('%s <= %s' % (l_key, r_key)):
                    self.assertEqual(l_value <= r_value, l_test_obj <= r_test_obj, '\n\n%r <= %r\nreturns: %r' % (l_test_obj, r_test_obj, str(l_test_obj._compare_(r_test_obj))))

    def test_sort(self):
        tm_1 = self.ML('test', 'TEST_MSG_1')  # ERROR
        tm_2 = self.ML('test', 'TEST_MSG_1')  # ERROR
        tm_3 = self.ML('test2', 'TEST_MSG_1')  # ERROR
        tm_4 = self.ML('test', 'test_msg_2')  # WARNING
        tm_5 = self.ML('test', 'test_msg_3')  # OK
        tm_6 = self.ML('test', 'VALID')  # OK

        tmp_list = [tm_2, tm_6, tm_1, tm_3, tm_5, tm_4]
        tmp_list.sort()

        tmp_exp = [tm_5, tm_6, tm_4, tm_1, tm_2, tm_3]

        tmp_msg = '\n\nReturned: %r\nExpected: %r' % (tmp_list, tmp_exp)

        self.assertEqual(tmp_list, tmp_exp, tmp_msg)


TEST_MH_MSG_1_1_0 = dict(key='test_msg_1', begin=0, length=0, segment__key='test_seg_1', text='')
TEST_MH_MSG_1_1_9 = dict(key='test_msg_1', begin=9, length=4, segment__key='test_seg_1', text='_tes')
TEST_MH_MSG_1_1_10 = dict(key='test_msg_1', begin=10, length=2, segment__key='test_seg_1', text='te')

TEST_MH_MSG_1_2_0 = dict(key='test_msg_2', begin=0, length=0, segment__key='test_seg_1', text='')
TEST_MH_MSG_1_2_9 = dict(key='test_msg_2', begin=9, length=4, segment__key='test_seg_1', text='_tes')
TEST_MH_MSG_1_2_10 = dict(key='test_msg_2', begin=10, length=2, segment__key='test_seg_1', text='te')

TEST_MH_MSG_2_1_0 = dict(key='test_msg_1', begin=0, length=0, segment__key='test_seg_2', text='')
TEST_MH_MSG_2_1_9 = dict(key='test_msg_1', begin=9, length=4, segment__key='test_seg_2', text='_tes')
TEST_MH_MSG_2_1_10 = dict(key='test_msg_1', begin=10, length=2, segment__key='test_seg_2', text='te')

TEST_MH_MSG_2_2_0 = dict(key='test_msg_2', begin=0, length=0, segment__key='test_seg_2', text='')
TEST_MH_MSG_2_2_9 = dict(key='test_msg_2', begin=9, length=4, segment__key='test_seg_2', text='_tes')
TEST_MH_MSG_2_2_10 = dict(key='test_msg_2', begin=10, length=2, segment__key='test_seg_2', text='te')


class TestMessageHandler(TestCase):

    def setUp(self):
        MESSAGE_LOOKUP.clear()

    @staticmethod
    def _validate_msg(msg_rec, answer_dict=None, **kwargs):

        tmp_missed = []
        if answer_dict is None:
            answer_dict = {}
        else:
            answer_dict = deepcopy(answer_dict)
        answer_dict.update(kwargs)

        if 'bool' in kwargs:
            check_bool = answer_dict.pop('bool')
            if bool(msg_rec) != check_bool:
                tmp_missed.append(('bool', bool(msg_rec), check_bool))

        for key, item in answer_dict.items():
            if '__' in key:
                meth, attr = key.split('__', 1)
                tmp_meth = getattr(msg_rec, meth)
                tmp_check = getattr(tmp_meth, attr)
            else:
                tmp_check = getattr(msg_rec, key)
            if tmp_check != item:
                tmp_missed.append((key, tmp_check, item))
        if tmp_missed:
            tmp_ret = []
            for key, check, item in tmp_missed:
                tmp_ret.append('\n%s:\n    Expected: %r\n    Returned: %r\n' % (key, item, check))
            return False, '\n'.join(tmp_ret)
        else:
            return True, ''

    def test_load(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        self.assertEqual(len(pmh), 0)

    def test_add_message_via_key(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1')

        tmp_ret = pmh.get_instance('test_msg_1')

        passed, msg = self._validate_msg(tmp_ret, TEST_MH_MSG_1_1_0)
        self.assertTrue(passed, msg)

    def test_get_message_via_none(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 10, 2)
        pmh('test_msg_2', 1, 3)
        pmh('test_seg_2.test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_2', 3, 1)

        tmp_ret = pmh.get_instance()
        passed, msg = self._validate_msg(tmp_ret, long_key='test_seg_2.test_msg_1')
        self.assertTrue(passed, msg)

    def test_get_message_via_key(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 10, 2)
        pmh('test_msg_2', 1, 3)
        pmh('test_seg_2.test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_2', 3, 1)

        tmp_ret = pmh.get_instance('test_msg_1')
        passed, msg = self._validate_msg(tmp_ret, long_key='test_seg_1.test_msg_1')
        self.assertTrue(passed, msg)

    def test_get_message_via_seg_and_key(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 10, 2)
        pmh('test_msg_2', 1, 3)
        pmh('test_seg_2.test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_2', 3, 1)

        tmp_ret = pmh.get_instance('test_seg_1.test_msg_2')
        passed, msg = self._validate_msg(tmp_ret, long_key='test_seg_1.test_msg_2')
        self.assertTrue(passed, msg)

    def test_get_message_via_key_and_pos(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 10, 2)
        pmh('test_msg_2', 1, 3)
        pmh('test_seg_2.test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_2', 3, 1)

        tmp_ret = pmh.get_instance('*.test_msg_2', 3)
        passed, msg = self._validate_msg(tmp_ret, long_key='test_seg_2.test_msg_2')
        self.assertTrue(passed, msg)

    def test_get_message_via_seg(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 10, 2)
        pmh('test_msg_2', 1, 3)
        pmh('test_seg_2.test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_2', 3, 1)

        tmp_ret = pmh.get_instance('test_seg_2.*')
        passed, msg = self._validate_msg(tmp_ret, long_key='test_seg_2.test_msg_1')
        self.assertTrue(passed, msg)

    def test_get_message_via_star_msg(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 10, 2)
        pmh('test_msg_2', 1, 3)
        pmh('test_seg_2.test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_2', 3, 1)

        tmp_ret = pmh.get_instance('*.test_msg_2')
        passed, msg = self._validate_msg(tmp_ret, long_key='test_seg_2.test_msg_2')
        self.assertTrue(passed, msg)

    def test_add_message_via_key_w_pos(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 10)

        tmp_ret = pmh.get_instance('test_msg_1')
        passed, msg = self._validate_msg(tmp_ret, TEST_MH_MSG_1_1_10, length=0, text='')
        self.assertTrue(passed, msg)

    def test_add_message_via_key_w_pos_len(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 10, 2)

        self.assertEqual(len(pmh), 1)

        tmp_ret = pmh.get_instance('test_msg_1')

        passed, msg = self._validate_msg(tmp_ret, TEST_MH_MSG_1_1_10)
        self.assertTrue(passed, msg)

    def test_add_message_via_key_w_pos_len_pos_raise(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        with self.assertRaises(IndexError):
            pmh('test_msg_1', 30, 2)

    def test_add_message_via_key_w_pos_len_len_raise(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        with self.assertRaises(IndexError):
            pmh('test_msg_1', 10, 20)

    def test_add_msg_dict(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh(test_msg_2, 9, 4)

        tmp_ret = pmh.get_instance('test_msg_2')
        passed, msg = self._validate_msg(tmp_ret, TEST_MH_MSG_1_2_9, description='This is test msg 2', bool=True)
        self.assertTrue(passed, msg)

    def test_add_msg_dict_seg_2(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_seg_2.test_msg_1', 10, 2)

        with self.assertRaises(KeyError):
            tmp_ret = pmh.get_instance('test_msg_1')

        tmp_ret = pmh.get_instance('test_seg_2.test_msg_1')
        passed, msg = self._validate_msg(tmp_ret, TEST_MH_MSG_2_1_10)
        self.assertTrue(passed, msg)

    def test_add_msg_dict_w_lookup(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_2', 9, 4)

        tmp_ret = pmh.get_instance('test_msg_2')

        passed, msg = self._validate_msg(tmp_ret, TEST_MH_MSG_1_2_9, description='', bool=False)
        self.assertTrue(passed, msg)

        MESSAGE_LOOKUP.clear()
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh.define(test_msg_2)
        pmh('test_msg_2', 9, 4)

        tmp_ret = pmh.get_instance('test_msg_2')
        passed, msg = self._validate_msg(tmp_ret, TEST_MH_MSG_1_2_9, description='This is test msg 2', bool=True)
        self.assertTrue(passed, msg)

    def test_in(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_2', 9, 4)
        pmh('test_seg_2.test_msg_1', 10, 2)

        with self.subTest():
            self.assertEqual(len(pmh), 2)

        with self.subTest():
            self.assertTrue('test_msg_2' in pmh)
        with self.subTest():
            self.assertFalse('test_msg_1' in pmh)
        with self.subTest():
            self.assertTrue('*.test_msg_2' in pmh)
        with self.subTest():
            self.assertTrue('*.test_msg_1' in pmh)
        with self.subTest():
            self.assertFalse('*.test_msg_3' in pmh)
        with self.subTest():
            self.assertTrue('test_seg_1.*' in pmh)
        with self.subTest():
            self.assertTrue('test_seg_2.*' in pmh)
        with self.subTest():
            self.assertFalse('test_msg_3.*' in pmh)
        with self.subTest():
            self.assertTrue('test_seg_1.test_msg_2' in pmh)
        with self.subTest():
            self.assertTrue('test_seg_2.test_msg_1' in pmh)
        with self.subTest():
            self.assertFalse('test_seg_1.test_msg_3' in pmh)
        with self.subTest():
            self.assertFalse('test_seg_2.test_msg_2' in pmh)
        with self.subTest():
            self.assertFalse('test_seg_1.test_msg_1' in pmh)

    def test_at_pos(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_2', 9, 4)
        pmh('test_msg_1', 10, 2)

        with self.subTest():
            self.assertEqual(len(pmh), 2)

        with self.subTest():
            self.assertTrue(pmh.at('test_msg_2', 9))
        with self.subTest():
            self.assertTrue(pmh.at('test_msg_2', 10))
        with self.subTest():
            self.assertTrue(pmh.at('test_msg_2', 11))
        with self.subTest():
            self.assertTrue(pmh.at('test_msg_2', 12))
        with self.subTest():
            self.assertFalse(pmh.at('test_msg_2', 8))

        with self.subTest():
            self.assertFalse(pmh.at('test_msg_1', 9))
        with self.subTest():
            self.assertTrue(pmh.at('test_msg_1', 10))
        with self.subTest():
            self.assertTrue(pmh.at('test_msg_1', 11))
        with self.subTest():
            self.assertTrue(pmh.at('test_msg_1', 12))
        with self.subTest():
            self.assertFalse(pmh.at('test_msg_1', 8))

        with self.subTest():
            with self.assertRaises(IndexError):
                self.assertFalse(pmh.at('test_msg_2', 24))

        with self.subTest():
            with self.assertRaises(IndexError):
                self.assertFalse(pmh.at('test_msg_1', 15))

        with self.subTest():
            with self.assertRaises(KeyError):
                self.assertFalse(pmh.at('test_msg_3', 13))

    def test_at_pos_same_key(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_2', 9, 2)
        pmh('test_msg_2', 10, 2)

        with self.subTest():
            self.assertEqual(len(pmh), 2)

        with self.subTest():
            self.assertTrue(pmh.at('test_msg_2', 9))
        with self.subTest():
            self.assertTrue(pmh.at('test_msg_2', 10))
        with self.subTest():
            self.assertTrue(pmh.at('test_msg_2', 11))
        with self.subTest():
            self.assertTrue(pmh.at('test_msg_2', 12))
        with self.subTest():
            self.assertFalse(pmh.at('test_msg_2', 8))


    def test_combine_helpers(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 9, 2)
        pmh('test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 2)

        pmh_2 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_2')
        pmh_2('test_msg_1', 9, 2)
        pmh_2('test_msg_2', 10, 2)
        self.assertEqual(len(pmh_2), 2)


        pmh += pmh_2
        self.assertEqual(len(pmh), 4)

        exp_ret = ['test_seg_1.test_msg_1', 'test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()

        self.assertEqual(exp_ret, tmp_ret)

    def test_add_helpers(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 9, 2)
        pmh('test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 2)

        pmh_2 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_2')
        pmh_2('test_msg_1', 9, 2)
        pmh_2('test_msg_2', 10, 2)
        self.assertEqual(len(pmh_2), 2)

        pmh_3 = pmh + pmh_2
        self.assertEqual(len(pmh_3), 4)
        self.assertEqual(len(pmh), 2)
        self.assertEqual(len(pmh_2), 2)

        exp_ret = ['test_seg_1.test_msg_1', 'test_seg_1.test_msg_2']
        tmp_ret = pmh.keys()
        self.assertEqual(exp_ret, tmp_ret)

        exp_ret = ['test_seg_2.test_msg_1', 'test_seg_2.test_msg_2']
        tmp_ret = pmh_2.keys()
        self.assertEqual(exp_ret, tmp_ret)

        exp_ret = ['test_seg_1.test_msg_1', 'test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh_3.keys()
        self.assertEqual(exp_ret, tmp_ret)


    def test_remove_by_long_key(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 9, 2)
        pmh('test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 2)

        pmh_2 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_2')
        pmh_2('test_msg_1', 9, 2)
        pmh_2('test_msg_2', 10, 2)
        self.assertEqual(len(pmh_2), 2)

        pmh += pmh_2
        self.assertEqual(len(pmh), 4)
        exp_ret = ['test_seg_1.test_msg_1', 'test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()
        self.assertEqual(exp_ret, tmp_ret)

        pmh.remove('test_seg_1.test_msg_1')
        exp_ret = ['test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()

        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))


    def test_remove_by_short_key(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 9, 2)
        pmh('test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 2)

        pmh_2 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_2')
        pmh_2('test_msg_1', 9, 2)
        pmh_2('test_msg_2', 10, 2)
        self.assertEqual(len(pmh_2), 2)

        pmh += pmh_2
        self.assertEqual(len(pmh), 4)
        exp_ret = ['test_seg_1.test_msg_1', 'test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()
        self.assertEqual(exp_ret, tmp_ret)

        pmh.remove('test_msg_1')
        exp_ret = ['test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()

        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))


    def test_remove_by_star_msg(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 9, 2)
        pmh('test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 2)

        pmh_2 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_2')
        pmh_2('test_msg_1', 9, 2)
        pmh_2('test_msg_2', 10, 2)
        self.assertEqual(len(pmh_2), 2)

        pmh += pmh_2
        self.assertEqual(len(pmh), 4)
        exp_ret = ['test_seg_1.test_msg_1', 'test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()
        self.assertEqual(exp_ret, tmp_ret)

        pmh.remove('*.test_msg_1')
        exp_ret = ['test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()

        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))


    def test_remove_by_seg_star(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 9, 2)
        pmh('test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 2)

        pmh_2 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_2')
        pmh_2('test_msg_1', 9, 2)
        pmh_2('test_msg_2', 10, 2)
        self.assertEqual(len(pmh_2), 2)

        pmh += pmh_2
        self.assertEqual(len(pmh), 4)
        exp_ret = ['test_seg_1.test_msg_1', 'test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()
        self.assertEqual(exp_ret, tmp_ret)

        pmh.remove('test_seg_2.*')
        exp_ret = ['test_seg_1.test_msg_1', 'test_seg_1.test_msg_2']
        tmp_ret = pmh.keys()

        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

        with self.assertRaises(KeyError):
            pmh.remove('test_seg_2.*')


    def test_remove_by_msg_pos(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 1, 2)
        pmh('test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 2)

        pmh_2 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_2')
        pmh_2('test_msg_1', 4, 2)
        pmh_2('test_msg_2', 10, 2)
        self.assertEqual(len(pmh_2), 2)

        pmh += pmh_2
        self.assertEqual(len(pmh), 4)
        exp_ret = ['test_seg_1.test_msg_1', 'test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()
        self.assertEqual(exp_ret, tmp_ret)

        pmh.remove('*.test_msg_1', 1)
        exp_ret = ['test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()

        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

    def test_show_keys(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 1, 2)
        pmh('test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 2)

        pmh_2 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_2')
        pmh_2('test_msg_1', 4, 2)
        pmh_2('test_msg_2', 10, 2)
        self.assertEqual(len(pmh_2), 2)

        pmh += pmh_2
        self.assertEqual(len(pmh), 4)
        exp_ret = ['test_seg_1.test_msg_1', 'test_seg_2.test_msg_1', 'test_seg_1.test_msg_2', 'test_seg_2.test_msg_2']
        tmp_ret = pmh.keys()
        self.assertEqual(exp_ret, tmp_ret)

        exp_ret = ['test_seg_1', 'test_seg_2']
        tmp_ret = pmh.keys(inc_message_key=False)
        self.assertEqual(exp_ret, tmp_ret)

        exp_ret = ['test_msg_1', 'test_msg_2']
        tmp_ret = pmh.keys(inc_segment_key=False)
        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))


    def test_show_info_normal(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 1, 2)
        pmh('test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_1', 4, 2)
        pmh('test_seg_2.test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 4)

        exp_ret = [
            ('test_seg_1.test_msg_1', 1, 2),
            ('test_seg_2.test_msg_1', 4, 2),
            ('test_seg_1.test_msg_1', 10, 2),
            ('test_seg_2.test_msg_2', 10, 2),
        ]

        tmp_ret = pmh.info()
        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

    def test_show_info_only_len(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 1, 2)
        pmh('test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_1', 4, 2)
        pmh('test_seg_2.test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 4)

        exp_ret = [
            ('test_seg_1.test_msg_1', 2),
            ('test_seg_2.test_msg_1', 2),
            ('test_seg_1.test_msg_1', 2),
            ('test_seg_2.test_msg_2', 2),
        ]

        tmp_ret = pmh.info(inc_position=False)
        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

    def test_show_info_only_pos(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 1, 2)
        pmh('test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_1', 4, 2)
        pmh('test_seg_2.test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 4)

        exp_ret = [
            ('test_seg_1.test_msg_1', 1),
            ('test_seg_2.test_msg_1', 4),
            ('test_seg_1.test_msg_1', 10),
            ('test_seg_2.test_msg_2', 10),
        ]

        tmp_ret = pmh.info(inc_length=False)
        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

    def test_show_info_combined(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 1, 2)
        pmh('test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_1', 4, 2)
        pmh('test_seg_2.test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 4)

        exp_ret = [
            ('test_seg_1.test_msg_1', [(1, 2), (10, 2)]),
            ('test_seg_2.test_msg_1', [(4, 2)]),
            ('test_seg_2.test_msg_2', [(10, 2)]),
        ]

        tmp_ret = pmh.info(combine_like=True)
        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

    def test_show_info_combine_like_only_msg(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 1, 2)
        pmh('test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_1', 4, 2)
        pmh('test_seg_2.test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 4)

        exp_ret = [
            ('test_msg_1', [(1, 2), (4, 2), (10, 2)]),
            ('test_msg_2', [(10, 2)]),
        ]

        tmp_ret = pmh.info(combine_like=True, inc_segment_key=False)
        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

    def test_show_info_combine_like_only_msg_only_pos(self):
        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 1, 2)
        pmh('test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_1', 4, 2)
        pmh('test_seg_2.test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 4)

        exp_ret = [
            ('test_msg_1', [(1, ), (4, ), (10, )]),
            ('test_msg_2', [(10, )]),
        ]

        tmp_ret = pmh.info(combine_like=True, inc_segment_key=False, inc_length=False)
        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

    def test_list_objects(self):
        """

        list_objects:
            for item in PMH
        """
        self.fail()


    def test_printed_output(self):
        """

        printed output:
            PMH.get_output('template_or_key', join='join_string', header='', footer='')
                * ordered by:
                    position (lowest to highest)
                    returned code (worst to best)
                    length (shortest to longest)
                    alpha (segment_key / msg_key)
        """
        self.fail()

