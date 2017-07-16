import unittest
from datetime import datetime, timezone, timedelta
from time import sleep

from ValidationParser.trace_helper import TraceHelper, QueueCounterHelper, CounterHelper

_named_times = {}


def now(name=None, add_sec=None):
    if add_sec is None:
        tmp_date = datetime.now(tz=timezone.utc)
    else:
        td = timedelta(seconds=add_sec)
        tmp_date = datetime.now(tz=timezone.utc) + td
    if name is not None:
        _named_times[name] = tmp_date
    return tmp_date


class TestCounterHelper(unittest.TestCase):

    def test_init(self):
        tch = CounterHelper()
        tch = QueueCounterHelper()

    def test_normal_counter(self):
        TESTS = [
            # (total, queue, overflow, first_queue),
            (0, 0, 0, 0),
            (1, 1, 0, 0),
            (2, 2, 0, 0),
            (3, 3, 0, 0),
            (4, 4, 0, 0),
            (5, 5, 0, 0),
            (6, 6, 0, 0),
            (7, 7, 0, 0),
            (8, 8, 0, 0),
            (9, 9, 0, 0),
            (10, 10, 0, 0),
            (11, 11, 0, 0),
            (12, 12, 0, 0),
            (13, 13, 0, 0),
        ]
        tch = CounterHelper()
        for t in TESTS:
            with self.subTest('%r - Total' % t[0]):
                self.assertEqual(t[0], tch.total_count)
            with self.subTest('%s - Queue' % t[1]):
                self.assertEqual(t[1], tch.queue_count)
            with self.subTest('%s - Overflow' % t[2]):
                self.assertEqual(t[2], tch.overflow_count)
            with self.subTest('%s - First Queue' % t[3]):
                self.assertEqual(t[3], tch.first_queue_counter)
            tch += 1

    def test_queued_counter(self):
        TESTS = [
            # (total, queue, overflow, first_queue),
            (0, 0, 0, 0),
            (1, 1, 0, 0),
            (2, 2, 0, 0),
            (3, 3, 0, 0),
            (4, 4, 0, 0),
            (5, 5, 0, 0),
            (6, 5, 1, 1),
            (7, 5, 2, 2),
            (8, 5, 3, 3),
            (9, 5, 4, 4),
            (10, 5, 5, 5),
            (11, 5, 6, 6),
            (12, 5, 7, 7),
            (13, 5, 8, 8),
        ]
        tch = QueueCounterHelper(max_count=5)
        for t in TESTS:
            with self.subTest('%s - Total' % t[0]):
                self.assertEqual(t[0], tch.total_count)
            with self.subTest('%s - Queue' % t[0]):
                self.assertEqual(t[1], tch.queue_count)
            with self.subTest('%s - Overflow' % t[0]):
                self.assertEqual(t[2], tch.overflow_count)
            with self.subTest('%s - First Queue' % t[0]):
                self.assertEqual(t[3], tch.first_queue_counter)
            tch += 1

    def test_start_at(self):
        tch = QueueCounterHelper(max_count=5, start=13)
        with self.subTest('Total'):
            self.assertEqual(13, tch.total_count)
        with self.subTest('Queue'):
            self.assertEqual(5, tch.queue_count)
        with self.subTest('Overflow'):
            self.assertEqual(8, tch.overflow_count)
        with self.subTest('First Queue'):
            self.assertEqual(8, tch.first_queue_counter)

    def test_comp(self):
        tch = QueueCounterHelper(max_count=5, start=13)

        self.assertGreater(tch, 3)
        self.assertEqual(tch, 5)
        self.assertGreaterEqual(tch, 5)
        self.assertGreaterEqual(tch, 4)
        self.assertLess(tch, 10)
        self.assertLessEqual(tch, 5)
        self.assertLessEqual(tch, 9)

    def test_math(self):
        tch = QueueCounterHelper(max_count=5, start=13)
        self.assertEqual(tch + 5, 10)
        self.assertEqual(tch - 2, 3)

    def test_get_dict(self):
        tch = QueueCounterHelper(max_count=5, start=13)
        ret = tch.get_dict(start_line=2, test_data='foobar')
        exp = dict(
            test_data='foobar',
            total_count=13,
            page_count=3,
            queue_count=5,
            overflow_count=8,
            start_line=11,
            end_line=13,
            line_range=range(2, 5)
        )
        self.assertEqual(ret, exp)


    def test_get_dict_1(self):
        tch = QueueCounterHelper(max_count=5, start=13)
        ret = tch.get_dict(start_line=-2, test_data='foobar')
        exp = dict(
            test_data='foobar',
            total_count=13,
            page_count=2,
            queue_count=5,
            overflow_count=8,
            start_line=12,
            end_line=13,
            line_range=range(3, 5)
        )
        self.assertEqual(ret, exp)


    def test_get_dict_2(self):
        tch = QueueCounterHelper(max_count=5, start=13)
        ret = tch.get_dict(test_data='foobar')
        exp = dict(
            test_data='foobar',
            total_count=13,
            page_count=5,
            queue_count=5,
            overflow_count=8,
            start_line=9,
            end_line=13,
            line_range=range(0, 5)
        )
        self.assertEqual(ret, exp)

    def test_get_dict_3(self):
        tch = QueueCounterHelper(max_count=5, start=13)
        ret = tch.get_dict(end_line=2, test_data='foobar')
        exp = dict(
            test_data='foobar',
            total_count=13,
            page_count=3,
            queue_count=5,
            overflow_count=8,
            start_line=9,
            end_line=11,
            line_range=range(0, 3)
        )
        self.assertEqual(ret, exp)


class TraceHelperFixture(TraceHelper):
    _header_message = None
    _footer_message = None
    _indent_start = '|'
    _indent_pad = '.'
    _trace_level = -1


class TestParseTracer(unittest.TestCase):

    def test_init(self):
        th = TraceHelper()

    def test_basic_op(self):
        th = TraceHelper(trace_level=-1)
        th._header_message = 'header'
        th._footer_message = 'footer'
        th('t1')
        th.a()
        th('t2')
        th('')
        th.s()
        th('t3')

        self.assertEqual(len(th), 4)

        with self.subTest('normal'):
            tmp_exp = 'header\nt1\n    t2\n    \nt3\nfooter'
            tmp_ret = th.output()
            self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

        with self.subTest('no_header'):
            tmp_exp = 't1\n    t2\n    \nt3\nfooter'
            tmp_ret = th.output(exc_flags=['header'])
            self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

        with self.subTest('no_footer'):
            tmp_exp = 'header\nt1\n    t2\n    \nt3'
            tmp_ret = th.output(exc_flags=['footer'])
            self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

        with self.subTest('no_prefix'):
            tmp_exp = 'header\nt1\nt2\n\nt3\nfooter'
            tmp_ret = th.output(exc_flags=['prefix'])
            self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

        with self.subTest('no_keep_empty'):
            tmp_exp = 'header\nt1\n    t2\nt3\nfooter'
            tmp_ret = th.output(exc_flags=['empty_lines'])
            self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_basic_no_hdr(self):
        th = TraceHelperFixture(trace_level=None)
        th('t1')
        tmp_exp = 't1'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_indent_add(self):
        th = TraceHelperFixture(trace_level=2)
        th('t1')
        th.a()
        th('t2')
        th.s()
        th('t3')
        tmp_exp = 't1\n|...t2\nt3'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_indent_add_indent_size_2(self):
        th = TraceHelperFixture(formats={'indent_size': 2})
        th('t1')
        th.a()
        th('t2')
        th.s()
        th('t3')
        tmp_exp = 't1\n|.t2\nt3'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_indent_add_indent_start_pad(self):
        th = TraceHelperFixture()
        th('t1')
        th.a()
        th('t2')
        th.a()
        th('t3')
        th.s()
        th('t4')
        th.s()
        th('t5')

        tmp_exp = 't1\n|...t2\n|...|...t3\n|...t4\nt5'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))


    def test_push_indent(self):
        th = TraceHelperFixture(trace_level=None)
        th('t1')
        th.a().push()
        th('t2')
        th.a(3)
        th('t3')
        th.s()
        th('t4')
        th.pop()('t5')

        tmp_exp = 't1\n|...t2\n|...|...|...|...t3\n|...|...|...t4\n|...t5'
        tmp_ret = th.output()

        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_named_indent(self):
        th = TraceHelperFixture(trace_level=None)
        th('t1')
        th.a().push('test')
        th('t2')
        th.a(3)
        th('t3')
        th.s()
        th('t4')
        th.pop('test')('t5')

        tmp_exp = 't1\n|...t2\n|...|...|...|...t3\n|...|...|...t4\n|...t5'
        tmp_ret = th.output()

        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_len(self):
        th = TraceHelperFixture(trace_level=None)
        th('t1')('t2')('t3')('t4')
        tmp_exp = 4
        tmp_ret = len(th)

        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_level_all(self):
        th = TraceHelperFixture(trace_level=None)
        th('t1').a()('t2').a()('t3').s()('t4').s()('t5')
        tmp_exp = 't1\n|...t2\n|...|...t3\n|...t4\nt5'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 5)


    def test_level_1(self):
        th = TraceHelperFixture(trace_level=1)
        th('t1').a()('t2').a()('t3').s()('t4').s()('t5')
        tmp_exp = 't1\nt5'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 2)

    def test_level_2(self):
        th = TraceHelperFixture(trace_level=2)
        th('t1').a()('t2').a()('t3').s()('t4').s()('t5')
        tmp_exp = 't1\n|...t2\n|...t4\nt5'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 4)


    def test_level_none(self):
        th = TraceHelperFixture(trace_level=0)
        th('t1').a()('t2').a()('t3').s()('t4').s()('t5')
        tmp_exp = ''
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 0)

    def test_level_all_return_1(self):
        th = TraceHelperFixture()
        th('t1').a()('t2').a()('t3').s()('t4').s()('t5')
        tmp_exp = 't1\n|...t2\n|...|...t3\n|...t4\nt5'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 5)

        tmp_exp = 't1\nt5'
        tmp_ret = th.output(to_level=1)

        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_max_trace(self):
        th = TraceHelperFixture(trace_level=None, max_traces=2, formats={'header_message': '{overflow_message}'})

        th('t1').a()('t2').a()('t3').s()('t4').s()('t5')

        tmp_exp = '(^^^ 3 lines overflowed ^^^)\n\n|...t4\nt5'
        tmp_ret = th.output()

        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 2)

    def test_level_with_start(self):
        th = TraceHelperFixture(trace_level=None, formats={'header_message': '{slice_message}'})
        th('t1')('t2')('t3')('t4')('t5')
        tmp_exp = '(*** Including lines 3 to 5 ***)\n\nt3\nt4\nt5'
        tmp_ret = th.output(start_line=2)
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 5)

    def test_level_with_neg_start(self):
        th = TraceHelperFixture(trace_level=None, formats={'header_message': '{slice_message}'})
        th('t1')('t2')('t3')('t4')('t5')
        tmp_exp = '(*** Including lines 4 to 5 ***)\n\nt4\nt5'
        tmp_ret = th.output(start_line=-2)
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 5)

    def test_level_all_with_end(self):
        th = TraceHelperFixture(trace_level=None, formats={'header_message': '{slice_message}'})
        th('t1')('t2')('t3')('t4')('t5')
        tmp_exp = '(*** Including lines 1 to 4 ***)\n\nt1\nt2\nt3\nt4'
        tmp_ret = th.output(end_line=3)
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 5)

    def test_level_all_with_neg_end(self):
        th = TraceHelperFixture(trace_level=None, formats={'header_message': '{slice_message}'})
        th('t1')('t2')('t3')('t4')('t5')
        tmp_exp = '(*** Including lines 1 to 3 ***)\n\nt1\nt2\nt3'
        tmp_ret = th.output(end_line=-2)
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 5)

    def test_level_all_with_start_end(self):
        th = TraceHelperFixture(trace_level=None, formats={'header_message': '{slice_message}'})
        th('t1')('t2')('t3')('t4')('t5')
        tmp_exp = '(*** Including lines 3 to 4 ***)\n\nt3\nt4'
        tmp_ret = th.output(start_line=2, end_line=3)
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 5)

    def test_level_all_with_limit_and_start_end(self):
        th = TraceHelperFixture(max_traces=6, formats={'header_message': '{slice_message}'})
        th('t1')('t2')('t3')('t4')('t5')('t6')('t7')('t8')('t9')('t10')
        tmp_exp = '(*** Including lines 7 to 8 ***)\n\nt7\nt8'
        tmp_ret = th.output(start_line=2, end_line=3)
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 6)


class TestParseTracerVars(unittest.TestCase):

    counter = 0

    @property
    def n(self):
        self.counter += 10
        return self.counter

    def test_level_all_with_limit_and_start_end(self):
        th = TraceHelperFixture(max_traces=6, formats={'header_message': '{slice_message}'})
        th('t1')('t2')('t3')('t4')('t5')('t6')('t7')('t8')('t9')('t10')
        tmp_exp = '(*** Including lines 7 to 8 ***)\n\nt7\nt8'
        tmp_ret = th.output(start_line=2, end_line=3)
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))
        self.assertEqual(len(th), 6)


    def test_total_count(self):
        th = TraceHelperFixture(max_traces=6, formats={'header_message': '{total_count}'})
        th('t1')('t2')('t3')('t4')('t5')('t6')('t7')('t8')('t9')('t10')
        tmp_exp = '10\nt5\nt6\nt7\nt8\nt9\nt10'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_start_time_1(self):
        th = TraceHelperFixture(max_traces=6, formats={'header_message': '->{start_time:%H:%M:%S}<-'})
        nowtime = now()
        # time_str = nowtime.strftime('%Y-%m-%d %H:%M:%S')
        th('t1')('t2')('t3')('t4')
        sleep(3)
        th('t5')('t6')('t7')('t8')('t9')('t10')
        tmp_exp = '->%s<-\nt5\nt6\nt7\nt8\nt9\nt10' % nowtime.strftime('%H:%M:%S')
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_end_time(self):
        th = TraceHelperFixture(max_traces=6, formats={'header_message': '->{end_time:%H:%M:%S}<-'})
        th('t1')('t2')('t3')('t4')
        sleep(3)
        th('t5')('t6')('t7')('t8')('t9')('t10')
        nowtime = now()
        time_str = nowtime.strftime('%H:%M:%S')
        tmp_exp = '->%s<-\nt5\nt6\nt7\nt8\nt9\nt10' % time_str
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_end_delta(self):
        th = TraceHelperFixture(max_traces=6, formats={'header_message': '->{end_delta.seconds}<-'})
        stime = now()
        th('t1')('t2')('t3')('t4')
        sleep(3)
        th('t5')('t6')('t7')
        sleep(0.25)
        th('t8')('t9')('t10')

        nowtime = now() - stime
        # time_str = nowtime.seconds

        tmp_exp = '->%s<-\nt5\nt6\nt7\nt8\nt9\nt10' % nowtime.seconds
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_trace_name(self):
        th = TraceHelperFixture(max_traces=6, name='test1', formats={'header_message': '{trace_name}'})
        th('t1')('t2')('t3')('t4')('t5')('t6')('t7')('t8')('t9')('t10')
        tmp_exp = 'test1\nt5\nt6\nt7\nt8\nt9\nt10'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_page_count(self):
        hdr_format = '{total_count} / {page_count} / {overflow_count}'
        th = TraceHelperFixture(max_traces=6, name='test1', formats={'header_message': hdr_format})
        th('t1')('t2')('t3')('t4')('t5')('t6')('t7')('t8')('t9')('t10')
        tmp_exp = '10 / 6 / 4\nt5\nt6\nt7\nt8\nt9\nt10'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    # Also in traces:

    def test_count(self):
        th = TraceHelperFixture(formats={'prefix': '{count}{indent}'})
        th.a()('t1')('t2')('t3')('t4')
        tmp_exp = '1|...t1\n2|...t2\n3|...t3\n4|...t4'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_indent_level(self):
        th = TraceHelperFixture(formats={'prefix': '{indent_level}{indent}'})
        th('t1').a()('t2').a()('t3').s()('t4')
        tmp_exp = '0t1\n1|...t2\n2|...|...t3\n1|...t4'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_parser_type(self):
        th = TraceHelperFixture(formats={'prefix': '{parser_name}{indent}'})
        th.a()('t1')('t2')('t3')('t4')
        tmp_exp = 'Note|...t1\nNote|...t2\nNote|...t3\nNote|...t4'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_delta(self):
        th = TraceHelperFixture(formats={'prefix': '{trace_delta:.0f}{indent}'})
        th.a()
        th('t1')
        sleep(1)
        th('t2')
        sleep(2)
        th('t3')
        sleep(1)
        th('t4')
        tmp_exp = '0|...t1\n1|...t2\n2|...t3\n1|...t4'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_time(self):
        th = TraceHelperFixture(formats={'prefix': '{time:%H:%M:%S}{indent}'})
        t1 = now()
        th.a()('t1')
        sleep(1)
        t2 = now()
        th('t2')
        sleep(2)
        t3 = now()
        th('t3')
        sleep(1)
        t4 = now()
        th('t4')

        tmp_exp = '%s|...t1\n%s|...t2\n%s|...t3\n%s|...t4' % (
            t1.strftime('%H:%M:%S'),
            t2.strftime('%H:%M:%S'),
            t3.strftime('%H:%M:%S'),
            t4.strftime('%H:%M:%S'),
        )
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    # testing Data:

    def test_data_dict(self):
        th = TraceHelperFixture(
            formats={'header_message': '{data[n].n}', 'prefix': '{data[n].n}{indent}'},
            n=self)
        th.a()('t1')('t2')('t3')('t4')
        tmp_exp = '10\n20|...t1\n30|...t2\n40|...t3\n50|...t4'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))

    def test_data_str(self):
        th = TraceHelperFixture(
            formats={'header_message': '{data[foo]}', 'prefix': '{data[snafu]}{indent}'},
            foo='foobar', snafu='*')
        th.a()('t1', bar='s1')('t2', bar='s1')('t3', bar='s1')('t4', bar='s1')
        tmp_exp = 'foobar\n*|...t1\n*|...t2\n*|...t3\n*|...t4'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg='\n\nRETURNED: %r\nEXPECTED: %r\n' % (tmp_ret, tmp_exp))


class TestStagedTraceHelper(unittest.TestCase):
    maxDiff = None
    """
    sh.begin_stage('test')
    sh.end_stage()

    sh.stage_name
    sh.stage_full_name
    sh.stage_time
    sh.stage_delta
    
    # new header and trace vars
    {stage_name}
    {stage_full_name}
    {stage_time}
    {stage_deta}
    {stage_trace_count}
    
    # output:
    
    {indent}BEGIN {stage_name}

    
    """
    def format_results(self, expected, returned):
        tmp_ret = '\n\nEXPECTED: %r\nRETURNED: %r\n\n' % (expected, returned)
        tmp_ret += 'EXPECTED:\n--------\n%s\n\n' % expected
        tmp_ret += 'RETURNED:\n--------\n%s\n\n' % returned
        return tmp_ret

    def test_one_stage(self):
        th = TraceHelperFixture(trace_level=None)
        th.add.begin('stage1')
        th('t1')
        th('t2')
        th.add.end()
        tmp_exp = 'Begin: stage1\n|...t1\n|...t2\nEnd: stage1'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg=self.format_results(tmp_exp, tmp_ret))
        self.assertEqual(len(th), 4)

    def test_two_stage(self):
        format_str = 'Begin: {full_stage}'
        th = TraceHelperFixture(trace_level=None)
        th('t0')
        self.assertEqual(th.get_stage, '')
        self.assertEqual(th.get_full_stage, '')
        th.add.begin('stage1', format_str=format_str)
        th('t1')
        self.assertEqual(th.get_stage, 'stage1')
        self.assertEqual(th.get_full_stage, 'stage1')
        th.add.begin('stage2', format_str=format_str)
        th('t2')
        self.assertEqual(th.get_stage, 'stage2')
        self.assertEqual(th.get_full_stage, 'stage1.stage2')
        th.add.begin('stage3', format_str=format_str)
        th('t3')
        self.assertEqual(th.get_stage, 'stage3')
        self.assertEqual(th.get_full_stage, 'stage1.stage2.stage3')
        th.add.end()
        th('t4')
        self.assertEqual(th.get_stage, 'stage2')
        self.assertEqual(th.get_full_stage, 'stage1.stage2')
        th.add.end()
        th('t5')
        self.assertEqual(th.get_stage, 'stage1')
        self.assertEqual(th.get_full_stage, 'stage1')
        th.add.end()
        th('t6')
        self.assertEqual(th.get_stage, '')
        self.assertEqual(th.get_full_stage, '')
        tmp_exp = 't0\nBegin: stage1\n|...t1\n|...Begin: stage1.stage2\n|...|...t2\n|...|...Begin: stage1.stage2.stage3\n|...|...|...t3\n|...|...End: stage3\n|...|...t4\n|...End: stage2\n|...t5\nEnd: stage1\nt6'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg=self.format_results(tmp_exp, tmp_ret))
        self.assertEqual(len(th), 13)

    def test_stage_with_extra_ind(self):
        format_str = 'Begin: {full_stage}'
        th = TraceHelperFixture(trace_level=None)
        th.add.begin('stage1', format_str=format_str)
        th('t1').a()
        th.add.begin('stage2', format_str=format_str)
        th('t2').a(3)
        th.add.begin('stage3', format_str=format_str)
        th('t3').a(2)
        th.add.end()
        th('t4').a(1)
        th.add.end()
        th('t5').a(2)
        th.add.end()
        tmp_exp = 'Begin: stage1\n|...t1\n|...|...Begin: stage1.stage2\n|...|...|...t2\n|...|...|...|...|...|...Begin: stage1.stage2.stage3\n|...|...|...|...|...|...|...t3\n|...|...|...|...|...|...End: stage3\n|...|...|...|...|...|...t4\n|...|...End: stage2\n|...|...t5\nEnd: stage1'
        tmp_ret = th.output()
        self.assertEqual(tmp_exp, tmp_ret, msg=self.format_results(tmp_exp, tmp_ret))
        self.assertEqual(len(th), 11)


