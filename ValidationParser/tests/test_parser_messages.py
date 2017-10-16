from unittest import TestCase, skip, SkipTest
from ValidationParser.parser_messages import *
from helpers.general import show_compared_items
from helpers.general.test_helpers import TestCaseCompare, make_msg
from ValidationParser.exceptions import MessageListLocked
from copy import deepcopy, copy



ref_1 = 'ref_1'
ref_2 = {'key': 'ref_2', 'name': 'reference_2', 'description': 'blah blah', 'details': 'foobar'}
ref_3 = {'key': 'ref_3', 'description': 'blah blah 3', 'details': 'foobar 3'}
ref_4 = '[rfc1234]'
ref_5 = '[4567]'
ref_6 = '[7890#4.3.2]'

ref_1_resp = {'key': 'ref_1', 'name': 'Ref 1'}
ref_2_resp = {'key': 'ref_2', 'name': 'reference_2', 'description': 'blah blah', 'details': 'foobar'}
ref_3_resp = {'key': 'ref_3', 'name': 'Ref 3', 'description': 'blah blah 3', 'details': 'foobar 3'}
ref_4_resp = {'key': 'RFC1234', 'name': 'RFC 1234', 'description': 'RFC 1234', 'url': 'https://tools.ietf.org/html/rfc1234'}
ref_5_resp = {'key': 'RFC4567', 'name': 'RFC 4567', 'description': 'RFC 4567', 'url': 'https://tools.ietf.org/html/rfc4567'}
ref_6_resp = {'key': 'RFC7890#4.3.2', 'name': 'RFC 7890', 'description': 'RFC 7890 Section 4.3.2', 'url': 'https://tools.ietf.org/html/rfc7890#section-4.3.2'}

ref_list = [ref_1, ref_2, ref_3, ref_4, ref_5, ref_6]

s1_m1_key = KeyObj('s1.m1')
s1_m2_key = KeyObj('s1.m2')
s2_m1_key = KeyObj('s2.m1')
s2_m2_key = KeyObj('s2.m2')

s1_m1_msg = {'key': s1_m1_key}

s1_message = {'key': 's1.*', 'name': 'Segment 1', 'description': 'Segment 1 desc', 'references': [ref_1]}
s1_warning_message = {'key': 's1.WARNING', 'name': 'new warn', 'description': 'Segment 1 warn', 'references': [ref_3, ref_4]}

mod_1 = {'key': s1_m1_key, 'begin': 1, 'length': 5}
mod_2 = {'key': s1_m2_key, 'begin': 2, 'length': 2}
mod_3 = {'key': s2_m1_key, 'begin': 10, 'length': 5}


class ParserFixture(object):
    name = 'blah'
    messages = ['s3.m1', {'key': 's3.m2', 'description': 's3 m2', 'references': ['ref_2']}]
    references = ref_list


class TestReferences(TestCase):

    def test_add_dict(self):
        tr = References(ref_2)
        self.assertEqual(len(tr), 1)
        self.assertEqual(tr['ref_2'], ref_2_resp)

    def test_add_list(self):
        tr = References()
        test_ret = tr.add(ref_2, ref_3)
        self.assertEqual(len(tr), 2)
        self.assertEqual(tr['ref_2'], ref_2_resp)
        self.assertEqual(tr['ref_3'], ref_3_resp)
        self.assertEqual(test_ret, ['ref_2', 'ref_3'])

    def test_add_str(self):
        tr = References(ref_3)
        test_ret = tr.add(ref_1, ref_2)
        self.assertEqual(len(tr), 3)
        self.assertEqual(tr['ref_1'], ref_1_resp)
        self.assertEqual(tr['ref_2'], ref_2_resp)
        self.assertEqual(tr['ref_3'], ref_3_resp)
        self.assertEqual(test_ret, ['ref_1', 'ref_2'])

    def test_get_1_refs(self):
        tr = References(ref_1, ref_3, ref_2)
        tmp_ret = list(tr.get_refs('ref_2'))
        self.assertCountEqual(tmp_ret, [ref_2])

    def test_get_2_refs(self):
        tr = References(ref_1, ref_3, ref_2)
        tmp_ret = list(tr.get_refs('ref_1', 'ref_2'))
        self.assertCountEqual(tmp_ret, [ref_1_resp, ref_2_resp])

    def test_rfc_full(self):
        tr = References(ref_1, ref_3, ref_2, ref_4)
        self.assertCountEqual(tr['RFC1234'], ref_4_resp)

    def test_rfc_no_text(self):
        tr = References(ref_1, ref_3, ref_2, ref_5)
        self.assertCountEqual(tr['RFC4567'], ref_5_resp)

    def test_rfc_section(self):
        tr = References(ref_1, ref_3, ref_2, ref_6)
        self.assertCountEqual(tr['RFC7890#4.3.2'], ref_6_resp)


class TestPositionObj(TestCaseCompare):

    def test_base(self):
        po = PositionObject(3, 5)
        self.assertTrue(po.at(5))
        self.assertFalse(po.at(2))
        self.assertFalse(po.at(10))
        self.assertEqual(po.get_slice, slice(3, 8))
        self.assertEqual(po.get_range, range(3, 8))
        self.assertEqual(po.get_set, {3, 4, 5, 6, 7})
        self.assertEqual(list(po), [3, 4, 5, 6, 7])
        self.assertEqual(po.items, (3, 5))
        self.assertEqual(str(po), '3 / 5')

    def test_order(self):

        tests = (
            (60, PositionObject(6, 0), 60),
            (35, PositionObject(3, 5), 35),
            (45, (4, 5), 45),
            (44, PositionObject(4, 4), 44),
            (1, (0, 1), 1),
        )

        self.assertComparisons(tests)


class TestMessageLookup(TestCase):

    def setUp(self):
        MESSAGE_LOOKUP.clear()

    def tearDown(self):
        MESSAGE_LOOKUP.clear()

    def test_add_references(self):
        ml = get_message_lookup({'name': 'snafu', 'references': ref_list})
        self.assertEqual(len(ml.references), 6)

    def test_get_references(self):
        ml_1 = MessageLookup('foobar', references=ref_list)
        ml = get_message_lookup(ml_1)
        self.assertEqual(len(ml.references), 6)
        self.assertEqual(list(ml.get_references('ref_1')), [ref_1_resp])

    def test_add_parser(self):
        ml = get_message_lookup()
        pf = ParserFixture()
        ml.add_parser(pf)
        test_resp = ml['s3.m2']
        self.assertEqual('s3 m2', test_resp['description'])

    def test_add_msg(self):
        ml = get_message_lookup()
        ml['s1.*'] = s1_message
        ml.update(s1_warning_message)

        self.assertTrue('s1.*' in ml._data)
        self.assertTrue('s1.WARNING' in ml._data)

    def test_mult_desc(self):
        ml = get_message_lookup()
        ml['s1.*'] = s1_message
        ml.update(s1_warning_message)

        tmp_resp = ml['s1.WARNING']
        self.assertEqual('Segment 1 desc\nSegment 1 warn', tmp_resp['description'])

    def test_mult_name(self):
        ml = get_message_lookup()
        ml['s1.*'] = s1_message
        ml.update(s1_warning_message)

        tmp_resp = ml['s1.VALID']
        self.assertEqual('Segment 1 - Valid Segment', tmp_resp['name'])
        tmp_resp = ml['s2.VALID']
        self.assertEqual('Valid Segment', tmp_resp['name'])


    def test_mult_ref(self):
        ml = get_message_lookup()
        ml['s1.*'] = s1_message
        ml.update(s1_warning_message)

        tmp_resp = ml['s1.WARNING']
        self.assertCountEqual(['ref_1', 'ref_3', 'RFC1234'], tmp_resp['references'])

        tmp_resp = ml['s1.VALID']
        self.assertEqual({'ref_1'}, tmp_resp['references'])

        tmp_resp = ml['s2.VALID']
        self.assertEqual(set(), tmp_resp['references'])


class TestMessageObj(TestCaseCompare):

    @classmethod
    def setUpClass(cls):
        MESSAGE_LOOKUP.clear()
        MESSAGE_LOOKUP.add_references(ref_list)
        MESSAGE_LOOKUP.update(s1_message, s1_warning_message)
        cls.ml = get_message_lookup()

    @classmethod
    def tearDownClass(cls):
        MESSAGE_LOOKUP.clear()

    def test_base(self):
        ml = get_message_lookup()

        tmp_resp = ml('s1.WARNING')
        self.assertCountEqual(['ref_1', 'ref_3', 'RFC1234'], tmp_resp._references)
        self.assertEqual('Segment 1 - new warn', tmp_resp.name)
        self.assertEqual('Segment 1 desc\nSegment 1 warn', tmp_resp.description)
        self.assertEqual(STATUS_CODES.WARNING, tmp_resp.status)
        self.assertEqual('s1.WARNING', str(tmp_resp.key))
        self.assertTrue(tmp_resp)

        tmp_resp = ml('s1.VALID')
        self.assertEqual({'ref_1'}, tmp_resp._references)
        self.assertEqual('Segment 1 - Valid Segment', tmp_resp.name)
        self.assertEqual('Segment 1 desc', tmp_resp.description)
        self.assertEqual(STATUS_CODES.OK, tmp_resp.status)
        self.assertEqual('s1.VALID', str(tmp_resp.key))
        self.assertTrue(tmp_resp)

        tmp_resp = ml('s2.VALID')
        self.assertEqual(set(), tmp_resp._references)
        self.assertEqual('Valid Segment', tmp_resp.name)
        self.assertEqual('', tmp_resp.description)
        self.assertEqual(STATUS_CODES.OK, tmp_resp.status)
        self.assertEqual('s2.VALID', str(tmp_resp.key))
        self.assertTrue(tmp_resp)

        tmp_resp = ml('s2.ERROR')
        self.assertEqual(set(), tmp_resp._references)
        self.assertEqual('s2 - ERROR', tmp_resp.name)
        self.assertEqual('', tmp_resp.description)
        self.assertEqual(STATUS_CODES.ERROR, tmp_resp.status)
        self.assertEqual('s2.ERROR', str(tmp_resp.key))
        self.assertFalse(tmp_resp)

    def test_add_pos(self):
        tmp_resp = self.ml('s1.VALID', 10, 5)
        self.assertEqual({'ref_1'}, tmp_resp._references)
        self.assertEqual('Segment 1 - Valid Segment', tmp_resp.name)
        self.assertEqual('Segment 1 desc', tmp_resp.description)
        self.assertEqual(STATUS_CODES.OK, tmp_resp.status)
        self.assertEqual('s1.VALID', str(tmp_resp.key))

        self.assertTrue(tmp_resp.at(11))
        self.assertFalse(tmp_resp.at(16))

        self.assertEqual(1, len(tmp_resp))
        tmp_resp.add_pos(12, 7)

        self.assertTrue(16 in tmp_resp)
        self.assertEqual(2, len(tmp_resp))

    def test_copy(self):
        tmp_resp = self.ml('s1.VALID', 5, 5)
        self.assertEqual('s1.VALID', str(tmp_resp.key))

        self.assertEqual(1, len(tmp_resp))
        tmp_resp.add_pos(12, 7)

        self.assertTrue(tmp_resp.at(16))
        self.assertEqual(2, len(tmp_resp))

        tmp_resp_2 = tmp_resp.copy(clear=False)
        self.assertEqual(2, len(tmp_resp_2))

        tmp_resp_3 = tmp_resp.copy(clear=True)
        self.assertEqual(1, len(tmp_resp_3))
        self.assertEqual([(0, 0)], tmp_resp_3._position_list)

    def test_remove(self):
        tmp_resp = self.ml('s1.VALID', 5, 5)
        self.assertEqual('s1.VALID', str(tmp_resp.key))

        self.assertEqual(1, len(tmp_resp))
        tmp_resp.add_pos(12, 7)

        self.assertTrue(tmp_resp.at(16))
        self.assertEqual(2, len(tmp_resp))

        self.assertTrue(6 in tmp_resp)
        
        tmp_resp.remove(5)
        self.assertEqual(1, len(tmp_resp))
        
        self.assertFalse(6 in tmp_resp)
        self.assertTrue(13 in tmp_resp)
        
        tmp_resp.add_pos(15, 10)
        self.assertEqual(2, len(tmp_resp))

        self.assertFalse(6 in tmp_resp)
        self.assertTrue(13 in tmp_resp)
        self.assertTrue(20 in tmp_resp)

        tmp_resp.remove()
        self.assertEqual(1, len(tmp_resp))

        self.assertFalse(6 in tmp_resp)
        self.assertTrue(13 in tmp_resp)
        self.assertFalse(20 in tmp_resp)

        with self.assertRaises(ValueError):
            tmp_resp.remove(15)

        self.assertEqual(1, len(tmp_resp))

        self.assertFalse(6 in tmp_resp)
        self.assertTrue(13 in tmp_resp)
        self.assertFalse(20 in tmp_resp)

        tmp_resp.remove()

        self.assertEqual(1, len(tmp_resp))

        self.assertTrue(0 in tmp_resp, repr(tmp_resp))
        self.assertFalse(6 in tmp_resp)
        self.assertFalse(13 in tmp_resp)
        self.assertFalse(20 in tmp_resp)

    def test_key_match(self):
        tmp_resp = self.ml('s1.VALID', 5, 5)
        self.assertEqual('s1.VALID', str(tmp_resp.key))

        self.assertEqual(1, len(tmp_resp))
        tmp_resp.add_pos(12, 7)

        self.assertTrue(tmp_resp.at(16))
        self.assertEqual(2, len(tmp_resp))

        self.assertTrue(6 in tmp_resp)

        self.assertTrue(tmp_resp.key_match('*.VALID'))
        self.assertTrue(tmp_resp.key_match('s1.VALID'))
        self.assertTrue(tmp_resp.key_match('s1.*'))
        self.assertTrue(tmp_resp.key_match('*.*'))
        self.assertTrue(tmp_resp.key_match('*.*', 12))
        self.assertTrue(tmp_resp.key_match('*.*', 5))

        self.assertFalse(tmp_resp.key_match('*.ERROR'))
        self.assertFalse(tmp_resp.key_match('s2.VALID'))
        self.assertFalse(tmp_resp.key_match('s2.*'))
        self.assertFalse(tmp_resp.key_match('*.*', 10))
        self.assertFalse(tmp_resp.key_match('*.*', 1))

    def test_str(self):
        tmp_resp = self.ml('s1.VALID', 5, 5)
        self.assertEqual('s1.VALID', str(tmp_resp))

        self.assertEqual(1, len(tmp_resp))
        tmp_resp.add_pos(12, 7)

        self.assertTrue(tmp_resp.at(16))
        self.assertEqual(2, len(tmp_resp))

        self.assertTrue(6 in tmp_resp)

        self.assertEqual('s1.VALID [(5, 5), (12, 7)]', repr(tmp_resp))

    def test_max(self):
        tmp_resp = self.ml('s1.VALID', 5, 5)
        self.assertEqual('s1.VALID', str(tmp_resp))

        self.assertEqual(1, len(tmp_resp))
        tmp_resp.add_pos(12, 3)

        self.assertEqual(2, len(tmp_resp))

        self.assertEqual(12, tmp_resp.max_position)

    def test_compare(self):

        TESTS = [
            (1, self.ml('s1.ERROR', 5, 5), 1),
            (2, self.ml('s1.SEGMENT_TOO_LONG', 10, 5), 2),
            (3, self.ml('s2.ERROR', 5, 5), 3),
            (4, self.ml('s23.SEGMENT_TOO_LONG', 5, 5), 4),

            (5, self.ml('s1.WARNING', 10, 5), 6),
            (6, self.ml('s1.DEPRECATED', 5, 5), 5),

            (7, self.ml('s1.VALID', 5, 5), 8),
            (8, self.ml('s1.VALID', 1, 2), 7),
        ]

        self.assertComparisons(TESTS)




"""
class TestPycharm(TestCase):
    def test_pycharm(self):
        with self.subTest('test'):
            self.assertEqual(True, False)

    def test_pycharm_works(self):
        self.assertEqual(True, False)
"""

class TestSimpleMessageHelper(TestCase):

    def make_mh(self, message_lookup=None,
                msg_defs=None,
                init_messages=None,
                def_seg='s1',
                parse_string='abcdefghijklmnop',
                override_defs=None,
                **lookup_kwargs):
        ml = message_lookup or get_message_lookup(**lookup_kwargs)
        mh = SinpleMessageHelper(ml, parse_string=parse_string, default_segment=def_seg, override_definitions=override_defs)
        init_defs_len = len(ml)
        init_len = 0

        if msg_defs:
            msg_defs = make_list(msg_defs)
            mh.define(*msg_defs)
            init_defs_len += len(msg_defs)

        if init_messages:
            init_messages = make_list(init_messages)
            for m in init_messages:
                mh(*make_list(m))
            init_len = 1

        self.assertEqual(init_len, len(mh), repr(mh))
        self.assertEqual(init_defs_len, len(ml))

        return mh

    def test_empty(self):
        mh = self.make_mh()
        self.assertEqual(0, len(mh))
        self.assertFalse(mh)

    def test_call_key_undefined(self):
        with self.assertRaises(KeyError):
            mh = self.make_mh(init_messages='foobar')

    def test_call_def(self):
        mh = self.make_mh(init_messages='VALID')
        self.assertTrue('s1.VALID' in mh)
        self.assertTrue('VALID' in mh)

        mh({'key': 's3.FOOBAR'})
        self.assertTrue('s3.FOOBAR' in mh)
        self.assertFalse('FOOBAR' in mh)
        mh({'key': 'SNAFU'})
        self.assertTrue('s1.SNAFU' in mh)
        self.assertTrue('SNAFU' in mh)
        self.assertFalse('s1.VALID' in mh)
        self.assertFalse('VALID' in mh)
        self.assertFalse('s1.VALID' in mh)

    def test_check_max(self):

        mh = self.make_mh(init_messages='WARNING')
        self.assertTrue('s1.WARNING' in mh)
        self.assertTrue('WARNING' in mh)

        mh('VALID')
        self.assertTrue('s1.WARNING' in mh)
        self.assertTrue('WARNING' in mh)

        mh('ERROR')
        self.assertTrue('s1.ERROR' in mh)
        self.assertTrue('ERROR' in mh)

    def test_call_mh(self):
        mh_e = self.make_mh(init_messages='ERROR')
        self.assertTrue('ERROR' in mh_e)
        self.assertTrue(mh_e)

        mh_v = self.make_mh(init_messages='VALID')
        self.assertTrue('VALID' in mh_v)
        self.assertTrue(mh_v)

        mh_w = self.make_mh(init_messages='WARNING')
        self.assertTrue('WARNING' in mh_w)
        self.assertTrue(mh_v)

        mh_w(mh_v)
        self.assertTrue('s1.WARNING' in mh_w)
        self.assertTrue('WARNING' in mh_w)

        mh_w(mh_e)
        self.assertTrue('s1.ERROR' in mh_w, repr(mh_w))
        self.assertTrue('ERROR' in mh_w)

    def test_define(self):
        mh = self.make_mh()

        with self.assertRaises(KeyError):
            mh('FOOBAR')

        mh.define({'key': 'foobar'})
        self.assertFalse('FOOBAR' in mh)
        mh('FOOBAR')
        self.assertTrue('FOOBAR' in mh)

    def test_at(self):
        mh = self.make_mh()
        mh('VALID', begin=5, length=10, note='my note')
        self.assertTrue(mh.at('VALID'))
        self.assertTrue(mh.at('VALID', 7))
        self.assertFalse(mh.at('VALID', 21))

        mh('ERROR', begin=12, length=10, note='my note')
        self.assertFalse(mh.at('VALID'))
        self.assertFalse(mh.at('VALID', 7))
        self.assertFalse(mh.at('VALID', 11))
        self.assertTrue(mh.at('ERROR'))
        self.assertTrue(mh.at('ERROR', 16))
        self.assertFalse(mh.at('ERROR', 7))

        mh('ERROR', begin=0, length=5, note='my note2')
        self.assertFalse(mh.at('VALID'))
        self.assertFalse(mh.at('VALID', 7))
        self.assertFalse(mh.at('VALID', 11))
        self.assertTrue(mh.at('ERROR'))
        self.assertTrue(mh.at('ERROR', 16))
        self.assertFalse(mh.at('ERROR', 7))
        self.assertTrue(mh.at('ERROR', 2))

        self.assertEqual(2, len(mh.get('ERROR')))

    def test_copy(self):
        mh = self.make_mh(init_messages='VALID')
        mh_2 = copy(mh)
        mh_3 = mh.copy()

        self.assertTrue('VALID' in mh_2)
        self.assertTrue('VALID' in mh_3)

        mh('ERROR')

        self.assertFalse('VALID' in mh)
        self.assertTrue('VALID' in mh_2)
        self.assertTrue('VALID' in mh_3)
        self.assertFalse('ERROR' in mh_2)
        self.assertFalse('ERROR' in mh_3)

    def test_iadd(self):
        mh_e = self.make_mh(init_messages='ERROR')
        self.assertTrue('ERROR' in mh_e)

        mh_v = self.make_mh(init_messages='VALID')
        self.assertTrue('VALID' in mh_v)

        mh_w = self.make_mh(init_messages='WARNING')
        self.assertTrue('WARNING' in mh_w)

        mh_w += mh_v
        self.assertTrue('s1.WARNING' in mh_w)
        self.assertTrue('WARNING' in mh_w)

        mh_w += mh_e
        self.assertTrue('s1.ERROR' in mh_w)
        self.assertTrue('ERROR' in mh_w)

    def test_add(self):
        mh_e = self.make_mh(init_messages='ERROR')
        self.assertTrue('ERROR' in mh_e)

        mh_v = self.make_mh(init_messages='VALID')
        self.assertTrue('VALID' in mh_v)

        mh_w = self.make_mh(init_messages='WARNING')
        self.assertTrue('WARNING' in mh_w)

        mh_2 = mh_w + mh_v
        self.assertTrue('s1.WARNING' in mh_2)
        self.assertTrue('WARNING' in mh_2)

        mh_3 = mh_w + mh_e
        self.assertTrue('s1.ERROR' in mh_3)
        self.assertTrue('ERROR' in mh_3)

    def test_items(self):
        mh = self.make_mh()
        mh('ERROR', begin=10, length=5)
        self.assertTrue('ERROR' in mh)

        tmp_ret = list(mh.items())

        self.assertEqual(1, len(tmp_ret))
        self.assertEqual('s1.ERROR', str(tmp_ret[0]))

        tmp_ret = list(mh.items('ERROR'))

        self.assertEqual(1, len(tmp_ret))
        self.assertEqual('s1.ERROR', str(tmp_ret[0]))

        tmp_ret = list(mh.items(position=13))

        self.assertEqual(1, len(tmp_ret), repr(tmp_ret))
        self.assertEqual('s1.ERROR', str(tmp_ret[0]))

        tmp_ret = list(mh.items('ERROR', position=13))

        self.assertEqual(1, len(tmp_ret))
        self.assertEqual('s1.ERROR', str(tmp_ret[0]))

        # no return
        tmp_ret = list(mh.items('VALID'))
        self.assertEqual(0, len(tmp_ret))

        tmp_ret = list(mh.items(position=6))
        self.assertEqual(0, len(tmp_ret))

        tmp_ret = list(mh.items('ERROR', position=2))
        self.assertEqual(0, len(tmp_ret))

        tmp_ret = list(mh.items('VALID', position=12))
        self.assertEqual(0, len(tmp_ret))

    def test_remove(self):
        mh = self.make_mh()
        mh('ERROR', begin=12, length=10, note='my note')
        self.assertTrue(mh.at('ERROR', 16))
        mh('ERROR', begin=0, length=5, note='my note2')
        self.assertTrue(mh.at('ERROR', 16))
        self.assertTrue(mh.at('ERROR', 2))

        self.assertEqual(2, len(mh.get('ERROR')))

        mh.remove()
        self.assertEqual(0, len(mh))
        self.assertFalse(mh)

    def test_remove_key(self):
        mh = self.make_mh()
        mh('ERROR', begin=12, length=10, note='my note')
        self.assertTrue(mh.at('ERROR', 16))
        mh('ERROR', begin=0, length=5, note='my note2')
        self.assertTrue(mh.at('ERROR', 16))
        self.assertTrue(mh.at('ERROR', 2))

        self.assertEqual(2, len(mh.get('ERROR')))

        with self.assertRaises(KeyError):
            mh.remove(key='VALID')

        mh.remove(key='ERROR')
        self.assertEqual(0, len(mh))
        self.assertFalse(mh)

    def test_remove_pos(self):
        mh = self.make_mh()
        mh('ERROR', begin=12, length=10, note='my note')
        self.assertTrue(mh.at('ERROR', 16))
        mh('ERROR', begin=0, length=5, note='my note2')
        self.assertTrue(mh.at('ERROR', 16))
        self.assertTrue(mh.at('ERROR', 2))

        self.assertEqual(2, len(mh.get('ERROR')))

        with self.assertRaises(IndexError):
            mh.remove(position=99)

        mh.remove(position=14)
        self.assertEqual(1, len(mh))
        self.assertTrue(mh)

        mh.remove(position=4)
        self.assertEqual(0, len(mh))
        self.assertFalse(mh)

    def test_remove_key_pos(self):
        mh = self.make_mh()
        mh('ERROR', begin=12, length=10, note='my note')
        self.assertTrue(mh.at('ERROR', 16))
        mh('ERROR', begin=0, length=5, note='my note2')
        self.assertTrue(mh.at('ERROR', 16))
        self.assertTrue(mh.at('ERROR', 2))

        self.assertEqual(2, len(mh.get('ERROR')))

        with self.assertRaises(IndexError):
            mh.remove(key='ERROR', position=99)

        mh.remove(key='ERROR', position=14)
        self.assertEqual(1, len(mh))
        self.assertTrue(mh)

        mh.remove(key='ERROR', position=4)
        self.assertEqual(0, len(mh))
        self.assertFalse(mh)

    def test_keys(self):
        mh = self.make_mh()
        mh('ERROR', begin=10, length=5)
        self.assertTrue('ERROR' in mh)

        tmp_ret = list(mh.keys())
        self.assertTrue(isinstance(tmp_ret[0], KeyObj))
        self.assertEqual('s1.ERROR', str(tmp_ret[0]))

        tmp_ret = list(mh.keys(as_string=True))
        self.assertTrue(isinstance(tmp_ret[0], str))
        self.assertEqual('s1.ERROR', tmp_ret[0])

    def test_get(self):
        mh = self.make_mh()
        mh('ERROR', begin=10, length=5)
        self.assertTrue('ERROR' in mh)

        tmp_ret = mh.get()
        self.assertEqual('s1.ERROR', str(tmp_ret))

        tmp_ret = mh.get('ERROR')

        self.assertEqual('s1.ERROR', str(tmp_ret))

        tmp_ret = mh.get(position=13)

        self.assertEqual('s1.ERROR', str(tmp_ret))

        tmp_ret = mh.get('ERROR', position=13)

        self.assertEqual('s1.ERROR', str(tmp_ret))

        # no return
        tmp_ret = mh.get('VALID')
        self.assertIsNone(tmp_ret)

        tmp_ret = mh.get(position=6)
        self.assertIsNone(tmp_ret)

        tmp_ret = mh.get('ERROR', position=2)
        self.assertIsNone(tmp_ret)

        tmp_ret = mh.get('VALID', position=12)
        self.assertIsNone(tmp_ret)

    def test_str(self):
        mh = self.make_mh()
        mh('ERROR', begin=12, length=10, note='my note')
        self.assertTrue(mh.at('ERROR', 16))
        mh('ERROR', begin=0, length=5, note='my note2')
        self.assertTrue(mh.at('ERROR', 16))
        self.assertTrue(mh.at('ERROR', 2))

        self.assertEqual(2, len(mh.get('ERROR')))

        self.assertEqual('s1 (ERROR)', str(mh))

    def test_repr(self):
        mh = self.make_mh()
        mh('ERROR', begin=12, length=10, note='my note')
        self.assertTrue(mh.at('ERROR', 16))
        mh('ERROR', begin=0, length=5, note='my note2')
        self.assertTrue(mh.at('ERROR', 16))
        self.assertTrue(mh.at('ERROR', 2))

        self.assertEqual(2, len(mh.get('ERROR')))

        self.assertEqual('s1 [ERROR (12, 10), (0, 5)]', repr(mh))


'''

test_msg_2 = {'key': 'test_msg_2', 'description': 'This is test msg 2', 'status': STATUS_CODES.WARNING, 'references': ['test_ref']}
test_msg_3 = {'key': 'test_segment.test_msg_3', 'description': 'tm3_desc', 'status': STATUS_CODES.OK, 'references': 'test_ref_2'}

TEST_MESSAGES = ['s6.TEST_MSG_1', test_msg_2, test_msg_3]

TEST_SEGMENTS = [
    's6',
    {'key': 'test_segment', 'status_override': STATUS_CODES.OK, 'description': 'segment description'},
    {'key': 'test_segment2', 'name': 'Test Segment Two'



TEST_SEG = ParseSegmentRec(MESSAGE_LOOKUP, 'test_seg')

class TestMessageLookup(TestCase):

    def setUp(self):
        MESSAGE_LOOKUP.clear()
        MESSAGE_LOOKUP.add(messages=TEST_MESSAGES, references=TEST_REFERENCES, segments=TEST_SEGMENTS)
        # print(MESSAGE_LOOKUP.dump())

    def tearDown(self):
        MESSAGE_LOOKUP.clear()


    def test_get_len(self):
        self.assertEqual(MESSAGE_LOOKUP.len(), 25, MESSAGE_LOOKUP.dump())

    def test_get_msg(self):
        tmp_msg = MESSAGE_LOOKUP.get_message('test_segment.VALID')
        self.assertEqual(tmp_msg.key, 'VALID')
        self.assertEqual(tmp_msg.status, STATUS_CODES.OK)

    # def test_get_new_msg(self):
    #     tmp_msg = MESSAGE_LOOKUP.get_message('test_segment', 'test_new_message')
    #     self.assertEqual(tmp_msg.key, 'test_new_message')
    #     self.assertEqual(tmp_msg.status, RESULT_CODES.ERROR)
    #     self.assertEqual(tmp_msg.name, 'Test New Message')

    def test_get_new_msg_locked_raise(self):
        MESSAGE_LOOKUP.locked = True
        with self.assertRaises(MessageNotFoundError):
            tmp_msg = MESSAGE_LOOKUP.get_message('test_segment', 'test_new_message')
        MESSAGE_LOOKUP.locked = False

    # def test_get_new_msg_with_kwargs(self):
    #     tmp_msg = MESSAGE_LOOKUP.get_message('test_segment', 'test_new_message', status=RESULT_CODES.OK, name='test_name')
    #     self.assertEqual(tmp_msg.key, 'test_new_message')
    #     self.assertEqual(tmp_msg.status, RESULT_CODES.OK)
    #     self.assertEqual(tmp_msg.name, 'test_name')

    def test_get_segment(self):
        MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        tmp_seg = MESSAGE_LOOKUP.get_segment('test_segment')
        self.assertEqual(tmp_seg.key, 'test_segment')
        # self.assertEqual(tmp_seg['status_override'], RESULT_CODES.OK)
        self.assertEqual(tmp_seg.name, 'Test Segment')
        self.assertEqual(tmp_seg.description, 'segment description')

    def test_get_new_segment(self):
        tmp_seg = MESSAGE_LOOKUP.get_segment('test_segment')
        self.assertEqual(tmp_seg.key, 'test_segment')
        # self.assertEqual(tmp_seg['status_override'], None)
        self.assertEqual(tmp_seg.name, 'Test Segment')
        self.assertEqual(tmp_seg.description, 'segment description')

    # def test_get_new_segment_locked_raise(self):
    #     with self.assertRaises(MessageListLocked):
    #         tmp_seg = MESSAGE_LOOKUP.set_message('*', 'test_segment')

    # def test_get_new_segment_with_kwargs(self):
    #     MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
    #     tmp_seg = MESSAGE_LOOKUP.get_segment('test_segment_4')
    #     self.assertEqual(tmp_seg.key, 'test_segment_4')
    #     # self.assertEqual(tmp_seg['status_override'], RESULT_CODES.WARNING)
    #     self.assertEqual(tmp_seg.name, 'Test Segment 4')
    #     self.assertEqual(tmp_seg.description, 'segment description')

    def test_get_reference(self):
        # MESSAGE_LOOKUP.add(references=TEST_REFERENCES)
        tmp_ref = MESSAGE_LOOKUP.get_reference('test_ref_2')
        self.assertEqual(tmp_ref.key, 'test_ref_2')
        self.assertEqual(tmp_ref.name, 'Test Ref 2')
        self.assertEqual(tmp_ref.url, 'ref_2_url')
        self.assertEqual(tmp_ref.text, 'ref_2_text')

    def test_get_rfc_reference(self):
        tmp_ref = MESSAGE_LOOKUP.add_reference('[12345]')
        self.assertEqual(tmp_ref.key, 'rfc12345')
        self.assertEqual(tmp_ref.name, 'Rfc12345')
        self.assertEqual(tmp_ref.url, 'https://tools.ietf.org/html/rfc12345')
        self.assertEqual(tmp_ref.description, 'See rfc12345 for more information')

    def test_get_rfc_reference_2(self):
        tmp_ref = MESSAGE_LOOKUP.add_reference('[rfc12345]')
        self.assertEqual(tmp_ref.key, 'rfc12345')
        self.assertEqual(tmp_ref.name, 'Rfc12345')
        self.assertEqual(tmp_ref.url, 'https://tools.ietf.org/html/rfc12345')
        self.assertEqual(tmp_ref.description, 'See rfc12345 for more information')

    def test_get_rfc_reference_section(self):
        tmp_ref = MESSAGE_LOOKUP.add_reference('[12345#1.2.3]')
        self.assertEqual(tmp_ref.key, 'rfc12345#1.2.3')
        self.assertEqual(tmp_ref.name, 'Rfc12345#1.2.3')
        self.assertEqual(tmp_ref.url, 'https://tools.ietf.org/html/rfc12345#section-1.2.3')
        self.assertEqual(tmp_ref.description, 'See rfc12345#1.2.3 for more information')

    def test_get_rfc_reference_section_2(self):
        tmp_ref = MESSAGE_LOOKUP.add_reference('[rfc12345#section-1.2.3]')
        self.assertEqual(tmp_ref.key, 'rfc12345#1.2.3')
        self.assertEqual(tmp_ref.name, 'Rfc12345#1.2.3')
        self.assertEqual(tmp_ref.url, 'https://tools.ietf.org/html/rfc12345#section-1.2.3')
        self.assertEqual(tmp_ref.description, 'See rfc12345#1.2.3 for more information')

    def test_get_new_reference_error(self):
        # MESSAGE_LOOKUP.add(references=TEST_REFERENCES)
        with self.assertRaises(ReferenceNotFoundError):
            tmp_ref = MESSAGE_LOOKUP.get_reference('test_ref_foobar')
        # self.assertEqual(tmp_ref.key, 'test_ref_foobar')
        # self.assertEqual(tmp_ref.name, 'Test Ref Foobar')
        # self.assertEqual(tmp_ref.url, '')
        # self.assertEqual(tmp_ref.text, '')

    def test_get_msg_object(self):
        # MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        tmp_msg = MESSAGE_LOOKUP('test_segment3', 'DEPRECATED')
        self.assertEqual(tmp_msg.long_key, 'test_segment3.DEPRECATED')
        self.assertEqual(tmp_msg.status, STATUS_CODES.WARNING)

    # def test_get_new_msg_object(self):
    #     MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
    #     tmp_msg = MESSAGE_LOOKUP('test_segment3', 'foobar')
    #     self.assertEqual(tmp_msg.long_key, 'test_segment3.foobar')
    #     self.assertEqual(tmp_msg.status, RESULT_CODES.ERROR)

    # def test_get_dict_msg_object(self):
    #     MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS, references=TEST_REFERENCES)
    #     tmp_msg = MESSAGE_LOOKUP('test_segment3', {'key': 'blah', 'status': RESULT_CODES.OK})
    #     self.assertEqual(tmp_msg.long_key, 'test_segment3.blah')
    #     self.assertEqual(tmp_msg.status, RESULT_CODES.OK)

    def test_set_error_on_warning(self):
        # MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        MESSAGE_LOOKUP.set_overrides({STATUS_CODES.WARNING: STATUS_CODES.ERROR})
        tmp_msg = MESSAGE_LOOKUP('test_segment3', 'DEPRECATED')
        self.assertEqual(tmp_msg.key, 'DEPRECATED')
        self.assertEqual(tmp_msg.status, STATUS_CODES.ERROR)

        tmp_msg = MESSAGE_LOOKUP('test_segment3', 'VALID')
        self.assertEqual(tmp_msg.long_key, 'test_segment3.VALID')
        self.assertEqual(tmp_msg.status, STATUS_CODES.OK)

    def test_override_status(self):
        # MESSAGE_LOOKUP.add(segments=TEST_SEGMENTS)
        MESSAGE_LOOKUP.set_overrides('test_segment3.DEPRECATED', '*.ERROR', default=STATUS_CODES.OK)
        tmp_msg_1 = MESSAGE_LOOKUP('test_segment3', 'DEPRECATED')
        self.assertEqual(tmp_msg_1.long_key, 'test_segment3.DEPRECATED')
        self.assertEqual(tmp_msg_1.status, STATUS_CODES.OK)

        tmp_msg_2 = MESSAGE_LOOKUP('test_segment3', 'WARNING')
        self.assertEqual(tmp_msg_2.long_key, 'test_segment3.WARNING')
        self.assertEqual(tmp_msg_2.status, STATUS_CODES.WARNING)

        tmp_msg_3 = MESSAGE_LOOKUP('test_segment2', 'ERROR')
        self.assertEqual(tmp_msg_3.long_key, 'test_segment2.ERROR')
        self.assertEqual(tmp_msg_3.status, STATUS_CODES.OK)

        tmp_msg_4 = MESSAGE_LOOKUP('test_segment3', 'ERROR')
        self.assertEqual(tmp_msg_4.long_key, 'test_segment3.ERROR')
        self.assertEqual(tmp_msg_4.status, STATUS_CODES.OK)

        MESSAGE_LOOKUP.clear_overrides()

        self.assertEqual(tmp_msg_1.long_key, 'test_segment3.DEPRECATED')
        self.assertEqual(tmp_msg_1.status, STATUS_CODES.OK)

        self.assertEqual(tmp_msg_2.long_key, 'test_segment3.WARNING')
        self.assertEqual(tmp_msg_2.status, STATUS_CODES.WARNING)

        self.assertEqual(tmp_msg_3.long_key, 'test_segment2.ERROR')
        self.assertEqual(tmp_msg_3.status, STATUS_CODES.OK)

        self.assertEqual(tmp_msg_4.long_key, 'test_segment3.ERROR')
        self.assertEqual(tmp_msg_4.status, STATUS_CODES.OK)

        tmp_msg_5 = MESSAGE_LOOKUP('test_segment3', 'DEPRECATED')
        self.assertEqual(tmp_msg_5.long_key, 'test_segment3.DEPRECATED')
        self.assertEqual(tmp_msg_5.status, STATUS_CODES.WARNING)

        tmp_msg_6 = MESSAGE_LOOKUP('test_segment3', 'WARNING')
        self.assertEqual(tmp_msg_6.long_key, 'test_segment3.WARNING')
        self.assertEqual(tmp_msg_6.status, STATUS_CODES.WARNING)

        tmp_msg_7 = MESSAGE_LOOKUP('test_segment2', 'ERROR')
        self.assertEqual(tmp_msg_7.long_key, 'test_segment2.ERROR')
        self.assertEqual(tmp_msg_7.status, STATUS_CODES.ERROR)

        tmp_msg_8 = MESSAGE_LOOKUP('test_segment4', 'ERROR')
        self.assertEqual(tmp_msg_8.long_key, 'test_segment4.ERROR')
        self.assertEqual(tmp_msg_8.status, STATUS_CODES.ERROR)


class TestMesageRecs(TestCase):
    def setUp(self):
        MESSAGE_LOOKUP.clear()
        MESSAGE_LOOKUP.add(messages=TEST_MESSAGES, references=TEST_REFERENCES, segments=TEST_SEGMENTS)
        # print(MESSAGE_LOOKUP.dump())

    def tearDown(self):
        MESSAGE_LOOKUP.clear()

    def test_basic_message_rec(self):
        pmr = ParseMessageRec('test_key', segment=TEST_SEG)
        self.assertEqual(pmr.key, 'test_key')
        self.assertEqual(pmr.name, 'Test Key')

    def test_add_field(self):
        pmr = ParseMessageRec('test_key', segment=TEST_SEG)
        pmr.update(name='New Test')
        pmr.update(description='test desc')
        self.assertEqual(pmr.key, 'test_key')
        self.assertEqual(pmr.name, 'New Test')
        self.assertEqual(pmr.description, 'test desc')
        # self.assertEqual(pmr.status_override, None)

    def test_add_existing_field(self):
        pmr = ParseMessageRec('test_key', segment=TEST_SEG)
        pmr.name = 'New Test'
        pmr.update(name='Another Test')
        pmr.description='test desc'
        pmr.update(description = 'foobar')
        self.assertEqual(pmr.key, 'test_key')
        self.assertEqual(pmr.name, 'Another Test')
        self.assertEqual(pmr.description, 'test desc')
        # self.assertEqual(pmr.status_override, None)

    def test_add_bad_field(self):
        pmr = ParseMessageRec('test_key', segment=TEST_SEG)
        with self.assertRaises(AttributeError):
            test = pmr.name_2
            self.assertEqual(test, 'foobar')

    def test_update_list(self):
        pmr = ParseMessageRec('test_key', segment=TEST_SEG)
        pmr.references.update('[test]')
        pmr.references.update('[test2]')
        self.assertEqual(list(pmr.references.keys()), ['rfctest', 'rfctest2'])

    def test_update_dict(self):
        pmr = ParseMessageRec('test_key', segment=TEST_SEG)
        pmr.name = 'New Test'
        pmr.update({'name': 'foobar', 'description': 'new desc'})
        self.assertEqual(pmr.name, 'foobar')
        self.assertEqual(pmr.description, 'new desc')

    # def test_update_obj(self):
    #     pmr = ParseMessageRec('test_key')
    #     pmr.name = 'New Test'
    #     pmr2 = ParseMessageRec('t2', name='foobar2', description='another desc')
    #     pmr.update(pmr2)
    #     self.assertEqual(pmr.name, 'New Test')
    #     self.assertEqual(pmr.description, 'another desc')

    def test_copy(self):
        tmp_seg = ParseSegmentRec(MESSAGE_LOOKUP, 'test_seg')
        pmr = ParseMessageRec('test_key', segment=tmp_seg, description='test_desc',
                              name='New Test', references=[{'key': 'test', 'description': 'test'},
                                                           {'key': 'test2', 'description': 'test2'}])
        # pmr.name = 'New Test'
        # pmr.description = 'test desc'
        # pmr.references.append('test')
        # pmr.references.append('test2')

        pmr2 = pmr.copy()

        self.assertEqual(pmr2.key, 'test_key')
        self.assertEqual(pmr2.name, 'New Test')
        self.assertEqual(list(pmr2.references.keys()), ['test', 'test2'])

        pmr.update(references={'key': 'test3', 'description': 'test3'})

        pmr2.status = STATUS_CODES.OK

        self.assertEqual(list(pmr2.references.keys()), ['test', 'test2'])
        self.assertEqual(list(pmr.references.keys()), ['test', 'test2', 'test3'])

        self.assertEqual(pmr.status, STATUS_CODES.ERROR)
        self.assertEqual(pmr2.status, STATUS_CODES.OK)


class TestMessageObject(TestCaseCompare):
    maxDiff = None
    def setUp(self):
        MESSAGE_LOOKUP.clear()
        MESSAGE_LOOKUP.add(messages=TEST_MESSAGES, references=TEST_REFERENCES, segments=TEST_SEGMENTS)
        # print(MESSAGE_LOOKUP.dump())

    def tearDown(self):
        MESSAGE_LOOKUP.clear()

    ML = MessageLookup('test', messages=TEST_MESSAGES, references=TEST_REFERENCES, segments=TEST_SEGMENTS)
    ML.add(messages=BASE_PARSING_MESSAGES)

    def test_strings(self):
        tm = self.ML('test_segment', 'test_msg_3')
        self.assertEqual(str(tm), 'test_segment.test_msg_3')
        self.assertEqual(tm.name, 'Test Msg 3')
        self.assertEqual(tm.key, 'test_msg_3')
        self.assertEqual(tm.description, 'tm3_desc')
        self.assertEqual(tm.segment_name, 'Test Segment')
        self.assertEqual(tm.segment_key, 'test_segment')
        self.assertEqual(tm.segment_description, 'segment description')
        self.assertEqual(tm.long_name, 'Test Segment / Test Msg 3')
        self.assertEqual(tm.long_key, 'test_segment.test_msg_3')
        self.assertEqual(tm.long_description, 'segment description\ntm3_desc')
        # self.assertEqual(tm.full_name, 'Test Seg 5 / Test Msg 3 (test_note)')
        # self.assertEqual(tm.full_description, 'test_desc_5\ntm3_desc\ntest_note')

    def test_references(self):
        tm = self.ML('test_seg_5', 'test_msg_3')
        self.assertEqual(len(tm.references), 2, '%r' % tm.references)

    def test_detailed_reference_string(self):
        tm = self.ML('test_seg_5', 'test_msg_3')
        test_exp = 'Test Ref 2 (ref_2_desc)\nURL: ref_2_url\nref_2_text\n\ntest reference 3 (ref_3_desc)\nURL: ref_3_url\nref_3_text'
        test_ret = tm.reference_str(detailed=True)
        self.assertEqual(test_exp, test_ret, show_compared_items(test_exp, test_ret))

    def test_not_detailed_reference_string(self):
        tm = self.ML('test_seg_5', 'test_msg_3')
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
        tm = self.ML('test_segment', 'test_msg_3')
        self.assertTrue(tm)

    def test_compare(self):

        TESTS = [
            ('tm_1', self.ML('test', 'TEST_MSG_1'), 1),  # ERROR     4a
            ('tm_3', self.ML('test2', 'TEST_MSG_1'), 2),  # ERROR    5a
            ('tm_4', self.ML('test', 'test_msg_2'), 3),  # WARNING   3a
            ('tm_5', self.ML('test', {'key': 'test_msg_3', 'status': STATUS_CODES.OK}), 4),  # OK        1a
            ('tm_6', self.ML('test', 'VALID'), 5),  # OK             2a
        ]

        self.assertComparisons(TESTS)

    def test_sort(self):
        tm_1 = self.ML('test', 'TEST_MSG_1')  # ERROR
        tm_2 = self.ML('test', 'TEST_MSG_1')  # ERROR
        tm_3 = self.ML('test2', 'TEST_MSG_1')  # ERROR
        tm_4 = self.ML('test', 'test_msg_2')  # WARNING
        tm_5 = self.ML('test', 'test_msg_3')  # OK
        tm_6 = self.ML('test', 'VALID')  # OK

        tmp_list = [tm_2, tm_6, tm_1, tm_3, tm_5, tm_4]
        tmp_list.sort()

        tmp_exp = [tm_1, tm_2, tm_3, tm_4, tm_5, tm_6]

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


class TestMessageHandler(TestCaseCompare):

    def setUp(self):
        MESSAGE_LOOKUP.clear()
        MESSAGE_LOOKUP.add(messages=TEST_MESSAGES, references=TEST_REFERENCES, segments=TEST_SEGMENTS)
        # print(MESSAGE_LOOKUP.dump())

    def tearDown(self):
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

        pmh = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh('test_msg_1', 1, 2)
        pmh('test_msg_1', 10, 2)
        pmh('test_seg_2.test_msg_1', 4, 2)
        pmh('test_seg_2.test_msg_2', 10, 2)
        self.assertEqual(len(pmh), 4)

        exp_ret = 'test_seg_1.test_msg_1\ntest_seg_2.test_msg_1\ntest_seg_1.test_msg_1\ntest_seg_2.test_msg_2'
        tmp_ret = pmh.get_output('long_key', combine_same=False)
        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

        exp_ret = 'test_msg_1\ntest_msg_2'
        tmp_ret = pmh.get_output('key', combine_same=True)
        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

        exp_ret = 'test_seg_1(test_msg_1(2)), test_seg_2(test_msg_1, test_msg_2)'
        tmp_ret = pmh.get_output('seg_keys', join=', ')
        self.assertEqual(len(pmh), 4)
        self.assertEqual(exp_ret, tmp_ret, make_msg(exp_ret, tmp_ret))

    def test_copy(self):
        pmh_1 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')

        pmh_1('WARNING')

        self.assertEqual(len(pmh_1), 1)

        pmh_2 = pmh_1.copy()

        self.assertTrue(pmh_1)
        self.assertTrue(pmh_2)

        self.assertEqual(len(pmh_1), 1)
        self.assertEqual(len(pmh_2), 1)

        pmh_1('VALID')

        self.assertTrue(pmh_1)
        self.assertTrue(pmh_2)

        self.assertEqual(len(pmh_1), 2)
        self.assertEqual(len(pmh_2), 1)

        pmh_2('ERROR')

        self.assertTrue(pmh_1)
        self.assertFalse(pmh_2)

        self.assertEqual(len(pmh_1), 2)
        self.assertEqual(len(pmh_2), 2, repr(pmh_2))

    def test_compare(self):
        pmh_valid = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
        pmh_warn = pmh_valid.copy()
        pmh_depre = pmh_valid.copy()
        pmh_too = pmh_valid.copy()
        pmh_error = pmh_valid.copy()

        pmh_valid('VALID')
        pmh_warn('WARNING')
        pmh_depre('DEPRECATED')
        pmh_too('TOO_LONG')
        pmh_error('ERROR')

        TESTS = [
            ('valid', pmh_valid, 99),
            ('warning', pmh_warn, 50),
            ('deprecated', pmh_depre, 50),
            ('too_long', pmh_too, 25),
            ('error', pmh_error, 25),
        ]

        self.assertComparisons(TESTS)

    # def test_compare_eq(self):
    #     pmh_1 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
    #     pmh_2 = pmh_1.copy()
    #     pmh_3 = pmh_1.copy()
    #
    #     pmh_1('VALID')
    #     pmh_2('WARNING')
    #     pmh_3('DEPRECATED')
    #     pmh_4('TOO_LONG')
    #     pmh_5('ERROR')
    #
    #     self.assertTrue(pmh_2 == pmh_3)
    #
    #     self.assertFalse(pmh_1 == pmh_2, msg='%r == %r' % (pmh_2, pmh_3))
    #     self.assertFalse(pmh_1 == pmh_5)
    #
    #
    # def test_compare_ne(self):
    #     pmh_1 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
    #     pmh_2 = pmh_1.copy()
    #     pmh_3 = pmh_1.copy()
    #
    #     pmh_1('VALID')
    #     pmh_2('WARNING')
    #     pmh_3('ERROR')
    #
    #     self.assertFalse(pmh_1 != pmh_2)
    #
    #     self.assertTrue(pmh_2 != pmh_3)
    #     self.assertTrue(pmh_1 != pmh_3)
    #
    # def test_compare_lt(self):
    #     pmh_1 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
    #     pmh_2 = pmh_1.copy()
    #     pmh_3 = pmh_1.copy()
    #
    #     pmh_1('VALID')
    #     pmh_2('WARNING')
    #     pmh_3('ERROR')
    #
    #     self.assertFalse(pmh_1 < pmh_2)
    #
    #     self.assertTrue(pmh_2 < pmh_3)
    #     self.assertTrue(pmh_1 < pmh_3)
    #
    #     self.assertFalse(pmh_3 < pmh_2)
    #     self.assertFalse(pmh_3 < pmh_1)
    #
    # def test_compare_le(self):
    #     pmh_1 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
    #     pmh_2 = pmh_1.copy()
    #     pmh_3 = pmh_1.copy()
    #
    #     pmh_1('VALID')
    #     pmh_2('WARNING')
    #     pmh_3('ERROR')
    #
    #     self.assertTrue(pmh_1 <= pmh_2)
    #
    #     self.assertTrue(pmh_2 <= pmh_3)
    #     self.assertTrue(pmh_1 <= pmh_3)
    #
    #     self.assertFalse(pmh_3 <= pmh_2)
    #     self.assertFalse(pmh_3 <= pmh_1)
    #
    # def test_compare_gt(self):
    #     pmh_1 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
    #     pmh_2 = pmh_1.copy()
    #     pmh_3 = pmh_1.copy()
    #
    #     pmh_1('VALID')
    #     pmh_2('WARNING')
    #     pmh_3('ERROR')
    #
    #     self.assertFalse(pmh_1 > pmh_2)
    #
    #     self.assertFalse(pmh_2 > pmh_3)
    #     self.assertFalse(pmh_1 > pmh_3)
    #
    #     self.assertTrue(pmh_3 > pmh_2)
    #     self.assertTrue(pmh_3 > pmh_1)
    #
    # def test_compare_ge(self):
    #     pmh_1 = ParseMessageHelper(MESSAGE_LOOKUP, 'this_is_a_test', 'test_seg_1')
    #     pmh_2 = pmh_1.copy()
    #     pmh_3 = pmh_1.copy()
    #
    #     pmh_1('VALID')
    #     pmh_2('WARNING')
    #     pmh_3('ERROR')
    #
    #     self.assertTrue(pmh_1 >= pmh_2)
    #
    #     self.assertFalse(pmh_2 >= pmh_3, msg='%r == %r  (%s)' % (pmh_2, pmh_3, str(pmh_2._compare_(pmh_3))))
    #     self.assertFalse(pmh_1 >= pmh_3)
    #
    #     self.assertTrue(pmh_3 >= pmh_2)
    #     self.assertTrue(pmh_3 >= pmh_1)

KEY_ARGS_OBJ_KWARGS = {
    'other': {'default_segment': None, 'other_ret': '*'},
    'normal': {'default_segment': None, 'other_ret': None},
    'default_other': {'default_segment': 'default', 'other_ret': '*'},
    'default': {'default_segment': 'default', 'other_ret': None}}


class TestKeyArgsObj(TestCaseCompare):
    def setUp(self):
        MESSAGE_LOOKUP.clear()
        MESSAGE_LOOKUP.add(messages=TEST_MESSAGES, references=TEST_REFERENCES, segments=TEST_SEGMENTS)
        # print(MESSAGE_LOOKUP.dump())

    def tearDown(self):
        MESSAGE_LOOKUP.clear()

    def check_return(self, expected_rec, returned_ret, test_name, kwargs):
        error_list = []
        passed = True
        if returned_ret.seg_key != expected_rec.ret_seg:
            passed = False
            error_list.append('seg')

        if returned_ret.msg_key != expected_rec.ret_msg:
            passed = False
            error_list.append('msg')

        if returned_ret.seg_kwargs != (expected_rec.ret_seg_kwargs or {}):
            passed = False
            error_list.append('seg kwargs')

        if returned_ret.msg_kwargs != (expected_rec.ret_msg_kwargs or {}):
            passed = False
            error_list.append('msg kwargs')

        tmp_msg = None
        if not passed:
            tmp_msg = self._make_msg_text(
                test_name=test_name,
                expected=expected_rec,
                returned=returned_ret,
                error_list=error_list,
                kwargs=kwargs)

        return passed, tmp_msg

    def _make_msg_text(self, test_name, expected, returned, error_list=None, kwargs=None):
        tmp_msg = ['', test_name]
        if error_list is not None:
            tmp_msg.append('Errors: %s\n' % ', '.join(error_list))
        tmp_msg.append('    Sent:')
        tmp_msg.append('        Args       : %r' % repr(expected.args))
        tmp_msg.append('        seg kwrags : %r' % expected.seg_kwargs)
        tmp_msg.append('        msg kwrags : %r' % expected.msg_kwargs)
        tmp_msg.append('        is_segment : %r' % expected.as_segment)
        tmp_msg.append('        kwargs     : %r' % kwargs or {})
        if error_list and 'raise' not in error_list:
            tmp_msg.append('    Expected')
            tmp_msg.append('        segment    : %r / %r' % (expected.ret_seg, expected.ret_seg_kwargs))
            tmp_msg.append('        message    : %r / %r' % (expected.ret_msg, expected.ret_msg_kwargs))
        tmp_msg.append('    Returned')
        tmp_msg.append('        segment    : %r / %r' % (returned.seg_key, returned.seg_kwargs))
        tmp_msg.append('        message    : %r / %r' % (returned.msg_key, returned.msg_kwargs))
        return '\n'.join(tmp_msg)

    def test_key_args_obj(self):
        seg = 'seg'
        msg = 'msg'
        NA = 'NA'
        msg_dict = {'a': 'msg_dict'}
        msg_dict_key = {'key': 'msg', 'a': 'msg_dict'}
        msg_kwarg_key2 = {'key': 'msg2', 'a': 'msg_dict'}
        msg_dict_sm_key = {'key': 'seg.msg', 'a': 'msg_dict'}
        msg_kwarg = {'b': 'msg_dict_b'}
        msg_kwarg_seg_dict = {'b': 'msg_dict_b', 's': 'seg_dict'}
        msg_kwarg_dict = {'a': 'msg_dict', 'b': 'msg_dict_b'}
        seg_dict = {'s': 'seg_dict'}
        seg_dict_key = {'key': 'seg', 's': 'seg_dict'}
        seg_kwarg = {'t': 'seg_dict_t'}
        seg_kwarg_dict = {'t': 'seg_dict_t', 's': 'seg_dict'}
        seg_kwarg_msg_dict = {'t': 'seg_dict_t', 'a': 'msg_dict'}
        seg_kwarg_key2 = {'key': 'seg2', 's': 'seg_dict'}
        seg_dict_sm_key = {'key': 'seg.msg', 's': 'seg_dict'}

        key_obj = KeyObj(seg, msg)
        key_args_obj = KeyObj(seg, msg, msg_kwargs=msg_kwarg)

        ArgsTestObj = namedtuple('ArgsTestObj', ('index', 'args', 'seg_kwargs', 'msg_kwargs', 'should_raise',
                                                 'as_segment', 'ret_seg', 'ret_msg', 'ret_seg_kwargs', 'ret_msg_kwargs'))


        TESTS = [
            ArgsTestObj(1, (seg, msg), None, None, False, NA, seg, msg, None, None),
            ArgsTestObj(2, (seg, msg_dict_key), None, None, False, NA, seg, msg, None, msg_dict),
            ArgsTestObj(3, (seg_dict_key, msg), None, None, False, NA, seg, msg, seg_dict, None),
            ArgsTestObj(4, (seg_dict_key, msg_dict_key), None, None, False, NA, seg, msg, seg_dict, msg_dict),
            ArgsTestObj(5, (seg, msg_dict_sm_key), None, None, False, NA, seg, msg, None, msg_dict),
            ArgsTestObj(6, (seg_dict_sm_key, msg), None, None, False, NA, seg, msg, seg_dict, None),
            ArgsTestObj(7, (seg, ), None, None, False, True, seg, None, None, None),
            ArgsTestObj(8, (msg,), None, None, False, False, None, msg, None, None),
            ArgsTestObj(9, (msg_dict_key,), None, None, False, False, None, msg, None, msg_dict),
            ArgsTestObj(10, (msg,), None, None, False, True, msg, None, None, None),
            ArgsTestObj(11, (msg_dict_key,), None, None, False, False, None, msg, None, msg_dict),
            ArgsTestObj(12, (seg_dict_key,), None, None, False, True, seg, None, seg_dict, None),
            ArgsTestObj('13a', (msg_dict_sm_key,), None, None, False, True, seg, msg, msg_dict, None),
            ArgsTestObj('13b', (msg_dict_sm_key,), None, None, False, False, seg, msg, None, msg_dict),
            ArgsTestObj(14, (seg, msg), seg_kwarg, msg_kwarg, False, NA, seg, msg, seg_kwarg, msg_kwarg),
            ArgsTestObj(15, (seg, msg_dict_key), seg_kwarg, msg_kwarg, False, NA, seg, msg, seg_kwarg, msg_kwarg_dict),
            ArgsTestObj(16, (seg_dict_key, msg), seg_kwarg, msg_kwarg, False, NA, seg, msg, seg_kwarg_dict, msg_kwarg),
            ArgsTestObj(17, (seg_dict_key, msg_dict_key), seg_kwarg, msg_kwarg, False, NA, seg, msg, seg_kwarg_dict, msg_kwarg_dict),
            ArgsTestObj(18, (seg, msg_dict_sm_key), seg_kwarg, msg_kwarg, False, NA, seg, msg, seg_kwarg, msg_kwarg_dict),
            ArgsTestObj(19, (msg_dict_sm_key, msg), seg_kwarg, msg_kwarg, False, NA, seg, msg, seg_kwarg_msg_dict, msg_kwarg),
            ArgsTestObj(20, (seg, msg_dict_sm_key), seg_kwarg_key2, msg_kwarg, True, NA, None, None, None, None),
            ArgsTestObj(21, (msg_dict_sm_key, msg), seg_kwarg, msg_kwarg_key2, True, NA, None, None, None, None),
            ArgsTestObj('22a', (seg,), seg_kwarg, msg_kwarg, False, True, seg, None, seg_kwarg, msg_kwarg),
            ArgsTestObj('22b', (seg,), seg_kwarg, msg_kwarg, False, False, None, seg, seg_kwarg, msg_kwarg),
            ArgsTestObj(23, (msg,), seg_kwarg, msg_kwarg, False, False, None, msg, seg_kwarg, msg_kwarg),
            ArgsTestObj('24a', (msg_dict_key,), seg_kwarg, msg_kwarg, False, True, msg, None, seg_kwarg_msg_dict, msg_kwarg),
            ArgsTestObj('24b', (msg_dict_key,), seg_kwarg, msg_kwarg, False, False, None, msg, seg_kwarg, msg_kwarg_dict),
            ArgsTestObj('25a', (msg,), seg_kwarg, msg_kwarg, False, True, msg, None, seg_kwarg, msg_kwarg),
            ArgsTestObj('25b', (msg,), seg_kwarg, msg_kwarg, False, False, None, msg, seg_kwarg, msg_kwarg),
            ArgsTestObj('26a', (msg_dict_key,), seg_kwarg, msg_kwarg, False, True, msg, None, seg_kwarg_msg_dict, msg_kwarg),
            ArgsTestObj('26b', (msg_dict_key,), seg_kwarg, msg_kwarg, False, False, None, msg, seg_kwarg, msg_kwarg_dict),
            ArgsTestObj('27a', (seg_dict_key,), seg_kwarg, msg_kwarg, False, True, seg, None, seg_kwarg_dict, msg_kwarg),
            ArgsTestObj('27b', (seg_dict_key,), seg_kwarg, msg_kwarg, False, False, None, seg, seg_kwarg, msg_kwarg_seg_dict),
            ArgsTestObj('28a', (msg_dict_sm_key,), seg_kwarg, msg_kwarg, False, True, seg, msg, seg_kwarg_msg_dict, msg_kwarg),
            ArgsTestObj('28b', (msg_dict_sm_key,), seg_kwarg, msg_kwarg, False, False, seg, msg, seg_kwarg, msg_kwarg_dict),
            ArgsTestObj(29, (seg, msg), seg_kwarg, None, False, NA, seg, msg, seg_kwarg, None),
            ArgsTestObj(30, (seg, msg_dict_key), seg_kwarg, None, False, NA, seg, msg, seg_kwarg, msg_dict),
            ArgsTestObj(31, (seg_dict_key, msg), seg_kwarg, None, False, NA, seg, msg, seg_kwarg_dict, None),
            ArgsTestObj(32, (seg_dict_key, msg_dict_key), seg_kwarg, None, False, NA, seg, msg, seg_kwarg_dict, msg_dict),
            ArgsTestObj(33, (seg, msg_dict_sm_key), seg_kwarg, None, False, NA, seg, msg, seg_kwarg, msg_dict),
            ArgsTestObj(34, (msg_dict_sm_key, msg), seg_kwarg, None, False, NA, seg, msg, seg_kwarg_msg_dict, None),

            ArgsTestObj('35a', (seg,), seg_kwarg, None, False, True, seg, None, seg_kwarg, None),
            ArgsTestObj('35b', (seg,), seg_kwarg, None, False, False, None, seg, seg_kwarg, None),
            ArgsTestObj('36a', (msg,), seg_kwarg, None, False, True, msg, None, seg_kwarg, None),
            ArgsTestObj('36b', (msg,), seg_kwarg, None, False, False, None, msg, seg_kwarg, None),
            ArgsTestObj('37a', (msg_dict_key,), seg_kwarg, None, False, True, msg, None, seg_kwarg_msg_dict, None),
            ArgsTestObj('37b', (msg_dict_key,), seg_kwarg, None, False, False, None, msg, seg_kwarg, msg_dict),
            ArgsTestObj('38a', (msg,), seg_kwarg, None, False, True, msg, None, seg_kwarg, None),
            ArgsTestObj('38b', (msg,), seg_kwarg, None, False, False, None, msg, seg_kwarg, None),
            ArgsTestObj('39a', (msg_dict_key,), seg_kwarg, None, False, True, msg, None, seg_kwarg_msg_dict, None),
            ArgsTestObj('39b', (msg_dict_key,), seg_kwarg, None, False, False, None, msg, seg_kwarg, msg_dict),
            ArgsTestObj('40a', (seg_dict_key,), seg_kwarg, None, False, True, seg, None, seg_kwarg_dict, None),
            ArgsTestObj('40b', (seg_dict_key,), seg_kwarg, None, False, False, None, seg, seg_kwarg, seg_dict),
            ArgsTestObj('41a', (msg_dict_sm_key,), seg_kwarg, None, False, True, seg, msg, seg_kwarg_msg_dict, None),
            ArgsTestObj('41b', (msg_dict_sm_key,), seg_kwarg, None, False, False, seg, msg, seg_kwarg, msg_dict),

            ArgsTestObj(42, (seg, msg), None, msg_kwarg, False, NA, seg, msg, None, msg_kwarg),
            ArgsTestObj(43, (seg, msg_dict_key), None, msg_kwarg, False, NA, seg, msg, None, msg_kwarg_dict),
            ArgsTestObj(44, (seg_dict_key, msg), None, msg_kwarg, False, NA, seg, msg, seg_dict, msg_kwarg),
            ArgsTestObj(45, (seg_dict_key, msg_dict_key), None, msg_kwarg, False, NA, seg, msg, seg_dict, msg_kwarg_dict),
            ArgsTestObj(46, (seg, msg_dict_sm_key), None, msg_kwarg, False, NA, seg, msg, None, msg_kwarg_dict),
            ArgsTestObj(47, (msg_dict_sm_key, msg), None, msg_kwarg, False, NA, seg, msg, msg_dict, msg_kwarg),


            ArgsTestObj('48a', (seg,), None, msg_kwarg, False, True, seg, None, None, msg_kwarg),
            ArgsTestObj('48b', (seg,), None, msg_kwarg, False, False, None, seg, None, msg_kwarg),
            ArgsTestObj('49a', (msg,), None, msg_kwarg, False, True, msg, None, None, msg_kwarg),
            ArgsTestObj('49b', (msg,), None, msg_kwarg, False, False, None, msg, None, msg_kwarg),
            ArgsTestObj('50a', (msg_dict_key,), None, msg_kwarg, False, True, msg, None, msg_dict, msg_kwarg),
            ArgsTestObj('50b', (msg_dict_key,), None, msg_kwarg, False, False, None, msg, None, msg_kwarg_dict),
            ArgsTestObj('51a', (msg,), None, msg_kwarg, False, True, msg, None, None, msg_kwarg),
            ArgsTestObj('51b', (msg,), None, msg_kwarg, False, False, None, msg, None, msg_kwarg),
            ArgsTestObj('52a', (msg_dict_key,), None, msg_kwarg, False, True, msg, None, msg_dict, msg_kwarg),
            ArgsTestObj('52b', (msg_dict_key,), None, msg_kwarg, False, False, None, msg, None, msg_kwarg_dict),
            ArgsTestObj('53a', (seg_dict_key,), None, msg_kwarg, False, True, seg, None, seg_dict, msg_kwarg),
            ArgsTestObj('53b', (seg_dict_key,), None, msg_kwarg, False, False, None, seg, None, msg_kwarg_seg_dict),
            ArgsTestObj('54a', (msg_dict_sm_key,), None, msg_kwarg, False, True, seg, msg, msg_dict, msg_kwarg),
            ArgsTestObj('54b', (msg_dict_sm_key,), None, msg_kwarg, False, False, seg, msg, None, msg_kwarg_dict),

            ArgsTestObj(55, [], seg_kwarg, None, False, NA, None, None, seg_kwarg, None),
            ArgsTestObj(56, [], seg_dict_key, None, False, NA, seg, None, seg_dict, None),
            ArgsTestObj(57, [], msg_dict_sm_key, None, False, NA, seg, msg, msg_dict, None),
            ArgsTestObj(58, [], None, msg_kwarg, False, NA, None, None, None, msg_kwarg),
            ArgsTestObj(59, [], None, msg_dict_key, False, NA, None, msg, None, msg_dict),
            ArgsTestObj(60, [], None, msg_dict_sm_key, False, NA, seg, msg, None, msg_dict),
            ArgsTestObj(61, [], seg_kwarg, msg_kwarg, False, NA, None, None, seg_kwarg, msg_kwarg),
            ArgsTestObj(62, [], seg_dict, msg_kwarg, False, NA, None, None, seg_dict, msg_kwarg),
            ArgsTestObj(63, [], seg_kwarg, msg_dict_key, False, NA, None, msg, seg_kwarg, msg_dict),
            ArgsTestObj(64, [], seg_kwarg, msg_dict_sm_key, False, NA, seg, msg, seg_kwarg, msg_dict),
            ArgsTestObj(65, [], seg_dict_sm_key, msg_kwarg, False, NA, seg, msg, seg_dict, msg_kwarg),
            ArgsTestObj(66, [], seg_dict_sm_key, msg_dict_sm_key, False, NA, seg, msg, seg_dict, msg_dict),

            ArgsTestObj(70, ('.msg',), None, None, False, NA, None, msg, None, None),
            ArgsTestObj(71, ('*.msg',), None, None, False, NA, '*', msg, None, None),
            ArgsTestObj(72, ('seg.',), None, None, False, NA, seg, None, None, None),
            ArgsTestObj(73, ('seg.*',), None, None, False, NA, seg, '*', None, None),

            ArgsTestObj(80, (key_obj,), None, None, False, NA, seg, msg, None, None),

            ArgsTestObj(81, (key_args_obj,), None, None, False, NA, seg, msg, None, msg_kwarg),

        ]

        LIMIT_TO = None
        # LIMIT_TO = '19_other_as_seg'

        if LIMIT_TO is not None:
            with self.subTest('LIMITED_TEST'):
                self.fail('LIMITED_TEST')

        for tmp_test in TESTS:
            for key, kwargs in KEY_ARGS_OBJ_KWARGS.items():
                for seg_type in [True, False]:
                    test = tmp_test

                    tmp_seg = test.ret_seg or kwargs.get('default_segment', None) or kwargs.get('other_ret', None)
                    tmp_msg = test.ret_msg or kwargs.get('other_ret', None)
                    tmp_seg_kwargs = test.ret_seg_kwargs or {}
                    tmp_msg_kwargs = test.ret_msg_kwargs or {}

                    test = test._replace(
                        ret_seg=tmp_seg,
                        ret_msg=tmp_msg,
                        ret_seg_kwargs=tmp_seg_kwargs,
                        ret_msg_kwargs=tmp_msg_kwargs,
                        as_segment=seg_type)

                    if tmp_test.as_segment == 'NA' or tmp_test.as_segment == seg_type:
                        if test.should_raise:
                            test_name = '%s_%s_RAISE' % (test.index, key)
                        elif seg_type:
                            test_name = '%s_%s_as_seg' % (test.index, key)
                        else:
                            test_name = '%s_%s_no_as_seg' % (test.index, key)

                        if LIMIT_TO is None or LIMIT_TO == test_name:
                            with self.subTest(test_name):

                                args = deepcopy(test.args)
                                msg_kwargs = deepcopy(test.msg_kwargs)
                                seg_kwargs = deepcopy(test.seg_kwargs)

                                if test.should_raise:

                                    # with self.assertRaises(AttributeError, msg=test_name):
                                    try:
                                        tmp_ret = make_message_key(*args, seg_kwargs=seg_kwargs, msg_kwargs=msg_kwargs,
                                                             as_segment=seg_type, **kwargs)
                                        self.fail(self._make_msg_text(test_name=test_name,
                                                                      expected=test,
                                                                      returned=tmp_ret,
                                                                      error_list=['raise'],
                                                                      kwargs=kwargs))
                                    except AttributeError:
                                        pass
                                else:
                                    tmp_ret = make_message_key(*args, seg_kwargs=seg_kwargs, msg_kwargs=msg_kwargs,
                                                         as_segment=seg_type, **kwargs)

                                    self.assertTrue(*self.check_return(test, tmp_ret, test_name, kwargs))

                                # with self.subTest(test_name + '-seg_kw'):
                                #     self.assertEqual(test.ret_seg_kwargs or {}, tmp_ret.seg_kwargs, '\n\n'+test_name)
                                # with self.subTest(test_name + '-msg_kw'):
                                #     self.assertEqual(test.ret_msg_kwargs or {}, tmp_ret.msg_kwargs, '\n\n'+test_name)
                                #
                                # tmp_exp_msg = test.ret_msg
                                # if tmp_exp_msg is None and kwargs.get('other_ret', None):
                                #     tmp_exp_msg = kwargs['other_ret']
                                #
                                # tmp_exp_seg = test.ret_seg
                                # if tmp_exp_seg is None:
                                #     if kwargs.get('other_ret', None):
                                #         tmp_exp_seg = kwargs['other_ret']
                                #
                                #     if kwargs.get('default_segment', None):
                                #         tmp_exp_seg = kwargs['default_segment']
                                #
                                # with self.subTest(test_name + '-msg_key'):
                                #     self.assertEqual(tmp_exp_msg, tmp_ret.msg, '\n\n'+test_name)
                                # with self.subTest(test_name + '-seg_key'):
                                #     self.assertEqual(tmp_exp_seg, tmp_ret.seg, '\n\n'+test_name)

    # def test_key_args_obj_raise(self):
    #     TESTS = [
    #         # (test_id, args, result_type),
    #
    #         # extra kwargs
    #         (1, ('seg_key', 'foo_key', {'foo': 'seg_bar'}, 'msg_key', {'foo': 'msg_bar'})),
    #
    #         # three strings
    #         (2, ('seg_key', 'msg_key', 'test_junk', {'foo': 'msg_bar'})),
    #
    #         # three dicts
    #         (3, ('seg_key.msg_key', {'foo': 'seg_bar'}, {'foo': 'msg_bar'}, {'blah': 'msg_blah'})),
    #
    #         # str and dict_key
    #         (4, ('msg', {'key': 'seg_key', 'foo': 'seg_bar'}, 'msg_key', {'key': 'test', 'foo': 'msg_bar'})),
    #
    #         # dict (no_key) first
    #         (5, ({'foo': 'seg_bar'}, {'foo': 'msg_bar'}, {'blah': 'msg_blah'})),
    #
    #         # one key, two dicts (no key)
    #         (6, ('msg_key', {'foo': 'seg_bar'}, {'foo': 'msg_bar'})),
    #
    #         # key.key and string
    #         (7, ('seg', 'seg_key.msg_key', {'foo': 'seg_bar'}, {'foo': 'msg_bar'})),
    #
    #         # (key, key) and string
    #         (8, ('seg', ('seg_key', 'msg_key'), {'foo': 'seg_bar'}, {'foo': 'msg_bar'})),
    #     ]
    #
    #     for test in TESTS:
    #         for key, kwargs in KEY_ARGS_OBJ_KWARGS.items():
    #             test_name = '%s-%s' % (str(test[0]), key)
    #             tmp_kwargs = kwargs.copy()
    #             test_args = deepcopy(test[1])
    #             with self.subTest(test_name + '-no_segment'):
    #                 with self.assertRaises(AttributeError):
    #                     tmp_ret = KeyArgsObj(*test_args, **tmp_kwargs)
    #
    #             test_args = deepcopy(test[1])
    #             tmp_kwargs['as_segment'] = True
    #             with self.subTest(test_name+'-segment'):
    #                 with self.assertRaises(AttributeError):
    #                     tmp_ret = KeyArgsObj(*test_args, **tmp_kwargs)



class TestStatusHelper(TestCase):

    def setUp(self):
        MESSAGE_LOOKUP.clear()
        MESSAGE_LOOKUP.add(messages=TEST_MESSAGES, references=TEST_REFERENCES, segments=TEST_SEGMENTS)
        self.MV = MESSAGE_LOOKUP('test_segment3', 'VALID')
        self.ME = MESSAGE_LOOKUP('test_segment3', 'ERROR')
        self.MW = MESSAGE_LOOKUP('test_segment3', 'WARNING')
        # print(MESSAGE_LOOKUP.dump())

    def tearDown(self):
        MESSAGE_LOOKUP.clear()

    def test_no_overrides(self):
        sh = StatusHelper()

        with self.subTest('msg_obj'):
            self.assertEqual(sh(self.MV), STATUS_CODES.OK)
        with self.subTest('msg_key'):
            self.assertEqual(sh('test_segment.WARNING'), STATUS_CODES.ERROR)
        with self.subTest('msg_key obj'):
            self.assertEqual(sh(KeyObj('test_segment', 'WARNING')), STATUS_CODES.ERROR)


    def test_override_by_specific_item(self):
        sh = StatusHelper({STATUS_CODES.WARNING: 'test_segment.foobar', STATUS_CODES.OK: ('test_segment3.WARNING', 'test.ok')})

        with self.subTest('msg_obj'):
            self.assertEqual(sh(self.MW), STATUS_CODES.OK)
        with self.subTest('msg_key'):
            self.assertEqual(sh('test.ok'), STATUS_CODES.OK)
        with self.subTest('msg_key obj'):
            self.assertEqual(sh(KeyObj('test_segment', 'foobar')), STATUS_CODES.WARNING)

    def test_override_by_segment(self):
        sh = StatusHelper({STATUS_CODES.WARNING: 'test_segment.*'})
        sh.update('test_segment.blah', default=STATUS_CODES.OK)
        with self.subTest('msg_obj'):
            self.assertEqual(sh(self.MW), STATUS_CODES.WARNING)
        with self.subTest('msg_key'):
            self.assertEqual(sh('test_segment.foobar'), STATUS_CODES.WARNING)
        with self.subTest('msg_key obj'):
            self.assertEqual(sh(KeyObj('test_segment', 'blah')), STATUS_CODES.OK)

    def test_override_by_default_segment(self):
        sh = StatusHelper({STATUS_CODES.WARNING: '*.foobar'})
        sh.update({'*.blah': STATUS_CODES.OK, '*.WARNING': STATUS_CODES.OK}, default=STATUS_CODES.OK)
        with self.subTest('msg_obj'):
            self.assertEqual(sh(self.MW), STATUS_CODES.OK)
        with self.subTest('msg_key'):
            self.assertEqual(sh('test_segment.foobar'), STATUS_CODES.WARNING)
        with self.subTest('msg_key obj'):
            self.assertEqual(sh(KeyObj('test', 'foobar')), STATUS_CODES.WARNING)
        with self.subTest('msg_key obj2'):
            self.assertEqual(sh(KeyObj('test', 'blah')), STATUS_CODES.OK)

    def test_override_by_status_code(self):
        sh = StatusHelper()
        sh.update({'*.blah': STATUS_CODES.WARNING})
        with self.subTest('msg_obj'):
            self.assertEqual(sh(self.MW), STATUS_CODES.WARNING)
        with self.subTest('msg_key'):
            self.assertEqual(sh('test_segment.blah'), STATUS_CODES.WARNING)
        with self.subTest('msg_key obj'):
            self.assertEqual(sh(KeyObj('test', 'foobar')), STATUS_CODES.ERROR)
        with self.subTest('msg_key obj2'):
            self.assertEqual(sh(KeyObj('test', 'blah')), STATUS_CODES.WARNING)

    def test_local_overrides_by_specific_item(self):
        sh = StatusHelper({STATUS_CODES.WARNING: 'test_segment.foobar',
                           STATUS_CODES.OK: ('test_segment3.WARNING', 'test.ok')})
        override_dict = fix_local_overrides({'test_segment.blah': STATUS_CODES.WARNING})

        with self.subTest('msg_obj'):
            self.assertEqual(sh(self.MW, override_dict), STATUS_CODES.OK)
        with self.subTest('msg_key'):
            self.assertEqual(sh('test_segment.blah', override_dict), STATUS_CODES.WARNING)
        with self.subTest('msg_key obj'):
            self.assertEqual(sh(KeyObj('test', 'foobar'), override_dict), STATUS_CODES.ERROR)
        with self.subTest('msg_key obj2'):
            self.assertEqual(sh(KeyObj('test', 'blah'), override_dict), STATUS_CODES.ERROR)

    def test_local_override_by_segment(self):
        sh = StatusHelper({STATUS_CODES.WARNING: 'test_segment.blah',
                           STATUS_CODES.OK: ('test_segment3.WARNING', 'test.blah')})
        override_dict = fix_local_overrides({'*.blah': STATUS_CODES.WARNING})

        with self.subTest('msg_obj'):
            self.assertEqual(sh(self.MW, override_dict), STATUS_CODES.OK)
        with self.subTest('msg_key'):
            self.assertEqual(sh('test.blah', override_dict), STATUS_CODES.WARNING)
        with self.subTest('msg_key obj'):
            self.assertEqual(sh(KeyObj('test', 'foobar'), override_dict), STATUS_CODES.ERROR)
        with self.subTest('msg_key obj2'):
            self.assertEqual(sh(KeyObj('test_segment', 'blah'), override_dict), STATUS_CODES.WARNING)

    def test_local_override_by_status_code(self):
        sh = StatusHelper({STATUS_CODES.WARNING: 'test_segment.blah',
                           STATUS_CODES.OK: ('test_segment3.WARNING', 'test.blah')})
        override_dict = fix_local_overrides({STATUS_CODES.OK: STATUS_CODES.WARNING})

        with self.subTest('msg_obj'):
            self.assertEqual(sh(self.MW, override_dict), STATUS_CODES.OK)
        with self.subTest('msg_key'):
            self.assertEqual(sh('test.blah', override_dict), STATUS_CODES.OK)
        with self.subTest('msg_key obj'):
            self.assertEqual(sh(KeyObj('test', 'foobar'), override_dict), STATUS_CODES.ERROR)
        with self.subTest('msg_key obj2'):
            self.assertEqual(sh(KeyObj('test_segment', 'blah'), override_dict), STATUS_CODES.WARNING)



'''