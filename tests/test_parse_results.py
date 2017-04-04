import unittest
from parse_results import ParseResultFootball, ParsingError
from meta_data import META_LOOKUP, ISEMAIL_RESULT_CODES, ISEMAIL_DNS_LOOKUP_LEVELS


class ParserFixture(object):
    def __init__(self, email_in='', **kwargs):
        self.email_in = email_in
        self.verbose = 3
        self.email_len = len(email_in)
        self.email_list = list(email_in)

        self.trace_str = ''
        self.history_str = ''

        for key, item in kwargs.items():
            setattr(self, key, item)



    def mid(self, begin: int = 0, length: int = 0):
        if length > 0:
            tmp_end = min(begin + length, self.email_len)
        else:
            tmp_end = self.email_len
        tmp_str = ''.join(self.email_list[begin:tmp_end])
        return tmp_str


PF = ParserFixture()


class TestParseFootball(unittest.TestCase):

    def setUp(self):
        META_LOOKUP.clear_overrides()

    def test_init_options(self):
        f = ParseResultFootball(PF)
        self.assertEquals(f.length, 0)

        f += 10
        self.assertEquals(f.length, 10)

        f -= 5
        self.assertEquals(f.length, 5)

    def test_math(self):
        f = ParseResultFootball(PF)
        f2 = ParseResultFootball(PF)

        self.assertEquals(f.length, 0)

        f += 10
        self.assertEquals(f.length, 10)

        f2 += 10
        f2 += f
        self.assertEquals(f2.length, 20)

    def test_math_2(self):
        f = ParseResultFootball(PF)

        self.assertEquals(f + 2, 2)
        self.assertEquals(2 + f, 2)

        f += 10
        self.assertEquals(f + 2, 12)
        self.assertEquals(2 + f, 12)

        f2 = ParseResultFootball(PF)
        f2 += 5

        self.assertEquals(f + f2, 15)
        self.assertEquals(f2 + f, 15)

    def test_init_length(self):
        f = ParseResultFootball(PF, length=10)

        self.assertEquals(f.length, 10)

    def test_init_length_full(self):

        f = ParseResultFootball(PF, length=13, position=20, segment='hello')

        self.assertEquals(f.length, 13)

    def test_comp_with_int(self):
        f = ParseResultFootball(PF, length=10)

        self.assertTrue(f > 5)
        self.assertTrue(f >= 10)
        self.assertTrue(f == 10)
        self.assertTrue(f != 20)
        self.assertTrue(f < 21)
        self.assertTrue(f <= 10)

    def test_comp_with_fb(self):
        f = ParseResultFootball(PF, length=10)
        f10 = ParseResultFootball(PF, length=10)
        f5 = ParseResultFootball(PF, length=5)
        f20 = ParseResultFootball(PF, length=20)

        self.assertTrue(f > f5)
        self.assertTrue(f >= f10)
        self.assertTrue(f == f10)
        self.assertTrue(f != f20)
        self.assertTrue(f < f20)
        self.assertTrue(f <= f10)

    def test_add_diag_str(self):
        per = ParseResultFootball(PF)
        per.add('VALID')

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_bad_diag(self):
        per = ParseResultFootball(PF)
        with self.assertRaises(AttributeError):
            per.add('FOOBAR')

    def test_add_diag_tuple(self):
        per = ParseResultFootball(PF)
        per.add(('VALID',1))

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_diag_dict(self):
        per = ParseResultFootball(PF)
        per.add({'diag': 'VALID', 'length': 1})

        tmp_ret = 'VALID' in per
        self.assertTrue(tmp_ret)

    def test_add_length_set(self):
        per = ParseResultFootball(PF)
        per += 3
        self.assertEquals(per.l, 3)
        per.add('VALID', set_length=1)

        self.assertEquals(per.l, 1)

    def test_add_football(self):
        per = ParseResultFootball(PF)
        per += 1

        per2 = ParseResultFootball(PF)
        per += 3

        per.add(per2)

        self.assertEquals(per.l, 4)

    def test_add_length_add(self):
        per = ParseResultFootball(PF)
        per += 1
        self.assertEquals(per.l, 1)
        per.add('VALID', length=1)

        self.assertEquals(per.l, 2)

    def test_add_ok_result(self):
        per = ParseResultFootball(PF, 'test_email_in', position=1)

        per.add(diag='VALID')

        self.assertFalse(per.error)

    def test_add_error_result(self):
        per = ParseResultFootball(PF, 'test_email_in')

        with self.assertRaises(ParsingError):
            per.add(diag='ERR_FWS_CRLF_X2')

        self.assertTrue(per.error)

    def test_add_warn_result(self):
        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertFalse(per.error)

    def test_add_mult_result(self):
        per = ParseResultFootball(PF, 'test_email_in')

        # self.assertTrue(per)
        # self.assertEquals(len(per), 0)

        per.add(diag='VALID', begin=1, length=1)
        # self.assertTrue(per)
        self.assertEquals(len(per), 1)
        self.assertFalse(per.error)

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        # self.assertTrue(per)
        self.assertEquals(len(per), 2)
        self.assertFalse(per.error)

        with self.assertRaises(ParsingError):
            per.add(diag='ERR_FWS_CRLF_X2', begin=1, length=1)
        self.assertTrue(per.error)

        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertTrue(per.error)

    def test_error_on_warn(self):

        META_LOOKUP.set_error_on_warning(True)
        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag='VALID', begin=1, length=1)
        self.assertFalse(per.error)

        with self.assertRaises(ParsingError):
            per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertTrue(per.error)

        per.add(diag='VALID', begin=1, length=1)
        self.assertTrue(per.error)

    def test_error_on_value(self):
        per = ParseResultFootball(PF, 'test_email_in')

        META_LOOKUP.set_error_on('VALID')
        per('DNSWARN_NO_MX_RECORD')
        with self.assertRaises(ParsingError):
            per.add('VALID')
        self.assertTrue(per.error)

    def test_contains(self):
        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag':'DNSWARN_NO_MX_RECORD', 'begin':1, 'length':1})
        per.add(diag='DEPREC_QTEXT')
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertIn('DNSWARN_NO_MX_RECORD', per)

        self.assertNotIn('foobar', per)

    def test_clear(self):
        per = ParseResultFootball(PF, 'test_email_in')

        self.assertEquals(len(per), 0)
        per += 10

        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag':'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
        per.add(diag='DEPREC_QTEXT', raise_on_error=False)
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertEquals(len(per), 4)
        self.assertEquals(per.l, 10)
        per.clear()

        self.assertEquals(len(per), 0)
        self.assertEquals(per.l, 0)

    def test_remove(self):
        per = ParseResultFootball(PF, 'test_email_in')

        per += 10

        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag': 'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
        per.add(diag='DEPREC_QTEXT', raise_on_error=False)
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertEquals(len(per), 4)
        self.assertEquals(per.l, 10)

        per.remove(diag='VALID')
        self.assertEquals(len(per), 3)

        per.remove('DNSWARN_NO_MX_RECORD', rem_all=True)
        self.assertEquals(len(per), 1)


        per.add(diag=('VALID', 1, 1))
        per.add(diag={'diag': 'DNSWARN_NO_MX_RECORD', 'begin': 1, 'length': 1})
        per.add(diag='DEPREC_QTEXT', raise_on_error=False)
        per.add(diag='DNSWARN_NO_MX_RECORD')

        self.assertEquals(len(per), 5)

        per.remove('DNSWARN_NO_MX_RECORD')
        self.assertEquals(len(per), 4)


class TestFullResults(unittest.TestCase):

    TEST_EMAILS = dict(
        complex=dict(
            email_in='(comment1)"foobar"(comment2)@(comment2)[example.com](comment4)',
            at_loc=28,
            local_comments=((0, 10), (19, 10)),
            domain_comments=((29, 10), (52, 10)),
        ),
        local_qs_comments=dict(
            email_in='(comment1)"foobar"(comment2)@example.com',
            at_loc=28,
            local_comments=((0, 10), (19, 10)),
        ),
        domain_lit_comments=dict(
            email_in='foobar@(comment2)[example.com](comment4)',
            at_loc=6,
            domain_comments=((7, 10), (30, 10)),
        ),
        local_qs=dict(
            email_in='"foobar"@example.com',
            at_loc=28,
            local_comments=((0, 10), (19, 10)),
        ),
        domain_lit=dict(
            email_in='foobar@[example.com]',
            at_loc=6,
            domain_comments=((7, 10), (30, 10)),
        ),
        normal=dict(
            email_in='foobar@example.com',
            at_loc=6,
        ),
    )

    TEST_DIAG_SETS = dict(
        VALID=['VALID'],
        MULT_WARN=['RFC5322_DOMAIN', 'DEPREC_COMMENT'],
        WARN=['RFC5322_DOMAIN', 'DEPREC_COMMENT'],
        MULT_WARN_ERR=['RFC5322_DOMAIN', 'DEPREC_COMMENT', 'ERR_DOT_END'],
        ERR=['ERR_DOT_END'],
    )

    def make_parser(self, **kwargs):
        kwargs['email_in'] = kwargs.get('email_in', 'foobar@example.com')
        kwargs['verbose'] = kwargs.get('verbose', 3)
        kwargs['trace_filter'] = kwargs.get('trace_filter', 999)
        kwargs['raise_on_error'] = kwargs.get('raise_on_error', False)
        kwargs['at_loc'] = kwargs.get('at_loc', 6)
        kwargs['dns_lookup_level'] = kwargs.get('dns_lookup_level', ISEMAIL_DNS_LOOKUP_LEVELS.NO_LOOKUP)

        tmp_ret = ParserFixture(**kwargs)

        return tmp_ret

    def make_football(self, *args, parser=None, diags=None, length=6, position=0, raise_on_error=False, **kwargs):
        if parser is None:
            parser = self.make_parser()
        if isinstance(parser, dict):
            parser = self.make_parser(**parser)
        if isinstance(parser, str):
            parser = self.make_parser(email_in=parser)

        tmp_fb = ParseResultFootball(parser)

        if parser.at_loc is not None:
            tmp_fb.at_loc = parser.at_loc

        tmp_fb += length
        tmp_fb.begin = position

        if 'local_comments' in kwargs:
            tmp_fb._local_comments = kwargs.pop('local_comments')

        if 'domain_comments' in kwargs:
            tmp_fb._local_comments = kwargs.pop('domain_comments')

        if kwargs or args:
            tmp_fb(*args, raise_on_error=raise_on_error, **kwargs)

        if diags is not None:
            if isinstance(diags, str):
                tmp_fb(diags, raise_on_error=raise_on_error)
            else:
                tmp_fb(*diags, raise_on_error=raise_on_error)

        else:
            tmp_fb('VALID')
        return tmp_fb

    def make_result(self, *args, parser=None, diags=None, dns_lookup_level=None, raise_on_error=False, length=6, position=0, **kwargs):
        tmp_fb = self.make_football(*args, parser=parser, diags=diags, length=length, position=position, raise_on_error=raise_on_error, **kwargs)
        tmp_ret = tmp_fb.finish(dns_lookup_level=dns_lookup_level, raise_on_error=raise_on_error)
        return tmp_ret

    def test_init(self):
        tmp_resp = self.make_result()

    def test_bool(self):
        tmp_resp = self.make_result()
        self.assertTrue(tmp_resp)

        tmp_resp = self.make_result(diags='ERR_EMPTY_ADDRESS', raise_on_error=False)
        self.assertFalse(tmp_resp)

    def test_str(self):
        tmp_resp = self.make_result()
        self.assertEqual(str(tmp_resp), 'foobar@example.com')

    def test_len(self):
        tmp_resp = self.make_result()
        self.assertEqual(len(tmp_resp), 18)

    def test_status(self):
        tmp_resp = self.make_result(diags=['ERR_EMPTY_ADDRESS', 'RFC5322_LOCAL_TOO_LONG'])
        self.assertEqual(tmp_resp.status, ISEMAIL_RESULT_CODES.ERROR)
        self.assertFalse(tmp_resp)

        tmp_resp = self.make_result(diags=['RFC5322_TOO_LONG', 'RFC5322_LOCAL_TOO_LONG'])
        self.assertEqual(tmp_resp.status, ISEMAIL_RESULT_CODES.WARNING)
        self.assertTrue(tmp_resp)

    def test_ok(self):
        tmp_resp = self.make_result()
        self.assertTrue(tmp_resp.ok)
        self.assertFalse(tmp_resp.warning)
        self.assertFalse(tmp_resp.error)

    def test_error(self):
        tmp_resp = self.make_result(diag='RFC5322_TOO_LONG')
        self.assertTrue(tmp_resp.ok)
        self.assertFalse(tmp_resp.warning)
        self.assertFalse(tmp_resp.error)

    def test_warning(self):
        tmp_resp = self.make_result(diag='ERR_EMPTY_ADDRESS')
        self.assertTrue(tmp_resp.ok)
        self.assertFalse(tmp_resp.warning)
        self.assertFalse(tmp_resp.error)

    def test_clean_address(self):
        tmp_resp = self.make_result()
        self.assertEqual(tmp_resp.clean_address, 'foobar@example.com')

    def test_local(self):
        tmp_resp = self.make_result()
        self.assertEqual(tmp_resp.local, 'foobar')

    def test_domain(self):
        tmp_resp = self.make_result()
        self.assertEqual(tmp_resp.domain, 'example.com')

    def test_full_local_normal(self):
        tmp_resp = self.make_result(parser='"foobar"#[example.com]')
        self.assertEqual(tmp_resp.full_local, '"foobar"')

    def test_full_local_QS(self):
        tmp_resp = self.make_result(parser='"foobar"#[example.com]')
        self.assertEqual(tmp_resp.full_local, '"foobar"')

    def test_full_local_comments(self):
        tmp_resp = self.make_result(parser='"foobar"#[example.com]')
        self.assertEqual(tmp_resp.full_local, '"foobar"')




    def test_full_domain(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_full_address(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_trace(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_history(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_local_comments(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_domain_comments(self):
        tmp_resp = self.make_result()
        self.fail()
    """
    def test_get_item_diag(self):
        tmp_resp = self.make_result()
        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag='VALID', begin=1, length=1)
        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        per.add(diag='DEPREC_QTEXT', begin=1, length=1)
        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)

        tmp_res = per['DNSWARN_NO_MX_RECORD']

        self.assertEquals(len(tmp_res), 2)
        self.assertEquals(tmp_res[0].diag.key, 'DNSWARN_NO_MX_RECORD')

    def test_get_item_cat(self):
        tmp_resp = self.make_result()

        per = ParseResultFootball(PF, 'test_email_in')

        per.add(diag='VALID', begin=1, length=1)
        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)
        per.add(diag='DEPREC_QTEXT', begin=1, length=1)
        per.add(diag='DNSWARN_NO_MX_RECORD', begin=1, length=1)

        tmp_res = per['ISEMAIL_VALID_CATEGORY']

        self.assertEquals(len(tmp_res), 1)
        self.assertEquals(tmp_res[0].diag.category.key, 'ISEMAIL_VALID_CATEGORY')

    """
    def test_diag_all(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_diag_one(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_diag_cat_all(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_diag_ret_diag_objs(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_diag_ret_diag_sets(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_get_item_filter_for_diag(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_diag_iter(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_diag_cat_one(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_contains(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_repr(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_desc(self):
        tmp_resp = self.make_result()
        self.fail()

    def test_getitem(self):
        tmp_resp = self.make_result()
        self.fail()


class TestHistory(unittest.TestCase):
    PF = ParserFixture('abcdefghijklmnopqrstuvwxyz')

    def test_sinple_history(self):
        per = ParseResultFootball(self.PF, 'test_in', position=0)
        per += 10
        self.assertEquals(str(per.history), 'test_in')

    def test_simple_history_w_str(self):
        per = ParseResultFootball(self.PF, 'test_in', position=2, length=4)
        # per += 10

        self.assertEquals(str(per.history.short_desc(inc_string=True)), "test_in['cdef']")

    def test_simple_history_2(self):
        per = ParseResultFootball(self.PF, 'test_in')
        per += 10

        self.assertEquals(str(per.history.short_desc()), 'test_in')

    def test_long_history_w_str(self):
        per = ParseResultFootball(self.PF, 'test_in')
        per += 4
        self.assertEquals(str(per.history.long_desc()), "test_in   :   'abcd'")

    def test_2_level(self):
        per = ParseResultFootball(self.PF, 'lvl_1')
        per += 2
        per_2 = ParseResultFootball(self.PF, 'lvl_2')
        per_2 += 3
        per += per_2
        self.assertEquals(per.history.short_desc(), 'lvl_1(lvl_2)')

    def test_complex_history_w_str(self):
        per = ParseResultFootball(self.PF, 'lvl_1', position=0)

        per_2 = ParseResultFootball(self.PF, 'lvl_2', position=0)
        per_2 += 2
        per += per_2

        per_3 = ParseResultFootball(self.PF, 'lvl_3', position=2)
        per_3 += 2
        per += per_3

        self.assertEquals(per.history.short_desc(), 'lvl_1(lvl_2, lvl_3)')

        self.assertEquals(per.history.short_desc(inc_string=True), "lvl_1['abcd'](lvl_2['ab'], lvl_3['cd'])")

        self.assertEquals(per.history.long_desc(), "lvl_1   :   'abcd'\n    lvl_2   :   'ab'\n    lvl_3   :   'cd'")


class TestMetaLookup(unittest.TestCase):

    def test_lenths(self):
        self.assertEquals(len(META_LOOKUP.categories), 7)
        self.assertEquals(len(META_LOOKUP.diags), 67)

    def test_get_by_value_cat(self):
        tmp_item = META_LOOKUP[115]
        self.assertEquals(tmp_item.name, 'Valid Address (unusual)')
        self.assertEquals(tmp_item.description, "Address is valid for SMTP but has unusual elements")
        self.assertEquals(tmp_item.result, ISEMAIL_RESULT_CODES.WARNING)

    def test_get_by_value_diag(self):
        tmp_item = META_LOOKUP['ISEMAIL_RFC5322']
        self.assertEquals(tmp_item.name, 'Valid Address (unusable)')
        self.assertEquals(tmp_item.description, "The address is only valid according to the broad definition of RFC 5322. It is otherwise invalid.",)
        self.assertEquals(tmp_item.result, ISEMAIL_RESULT_CODES.WARNING)

    def test_get_by_key_cat(self):
        tmp_item = META_LOOKUP[1010]
        self.assertEquals(tmp_item.key, 'RFC5321_TLD_NUMERIC')
        self.assertEquals(tmp_item.category.value, 115)
        self.assertEquals(tmp_item.description, "Address is valid but the Top Level Domain begins with a number")
        self.assertEquals(tmp_item.category.result, ISEMAIL_RESULT_CODES.WARNING)
        self.assertEquals(tmp_item.smtp, "250 2.1.5 ok")
        self.assertEquals(tmp_item.reference[0].key, 'TLD-format')

    def test_get_by_key_diag(self):
        tmp_item = META_LOOKUP['DEPREC_QTEXT']
        self.assertEquals(tmp_item.value, 1035)
        self.assertEquals(tmp_item.category.value, 500)
        self.assertEquals(tmp_item.description, "A quoted string contains a deprecated character")
        self.assertEquals(tmp_item.category.result, ISEMAIL_RESULT_CODES.WARNING)
        self.assertEquals(tmp_item.smtp, "553 5.1.3 Bad destination mailbox address syntax")
        self.assertEquals(tmp_item.reference[0].key, 'obs-qtext')

    def test_print_help_text(self):

        """

        [9123] FOOBAR    this is the description
                            (CAT code/name)
        [9123] FOOBAR    this is the description
                            (CAT code/name)
        [9123] FOOBAR    this is the description
                            (CAT code/name)
        """

        tmp_longest_diag_key = 0
        tmp_longest_cat_key = 0

        for diag in META_LOOKUP.diags._by_key:
            tmp_longest_diag_key = max(len(diag), tmp_longest_diag_key)

        for cat in META_LOOKUP.categories._by_key:
            tmp_longest_cat_key = max(len(cat), tmp_longest_cat_key)

        diag_cat_indent = 11 + tmp_longest_diag_key

        print('Categories')
        print('**********')
        tmp_ret = []
        for key, cat in META_LOOKUP.categories._by_key.items():
            tmp_ret.append('[%s] %s  %s' %
                  (
                      str(cat.value).rjust(3, ' '),
                      cat.key.rjust(tmp_longest_cat_key, ' '),
                      cat.description)
                  )
        tmp_ret.sort()
        print('\n'.join(tmp_ret))


        print('\n\nDiags')
        print('*********')
        tmp_ret = []
        for key, diag in META_LOOKUP.diags._by_key.items():
            tmp_ret.append('[%s] %s  %s (%s)' %
                  (
                      str(diag.value).rjust(3, ' '),
                      diag.key.rjust(tmp_longest_diag_key, ' '),
                      diag.description,
                      diag.category.key
                  )
                  )
        tmp_ret.sort()
        print('\n'.join(tmp_ret))


        print('\n\n\n')
        print(repr(list(META_LOOKUP.diags._by_key.items())))

    def test_ia_error(self):
        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertFalse(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertFalse(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.set_error_on('VALID')
        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertFalse(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertTrue(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.set_error_on('DNSWARN_COMM_ERROR')
        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertTrue(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertTrue(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.clear_overrides()

        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertFalse(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertFalse(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.set_error_on('ISEMAIL_DNSWARN')
        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertTrue(META_LOOKUP.is_error('DNSWARN_NO_RECORD'))
        self.assertTrue(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertFalse(META_LOOKUP.is_error('DEPREC_COMMENT'))
        self.assertFalse(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.clear_overrides()

        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertFalse(META_LOOKUP.is_error('DNSWARN_NO_RECORD'))
        self.assertFalse(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertFalse(META_LOOKUP.is_error('DEPREC_COMMENT'))
        self.assertFalse(META_LOOKUP.is_error('VALID'))

        META_LOOKUP.set_error_on_warning()
        self.assertTrue(META_LOOKUP.is_error('ERR_UNCLOSED_DOM_LIT'))
        self.assertTrue(META_LOOKUP.is_error('DNSWARN_NO_RECORD'))
        self.assertTrue(META_LOOKUP.is_error('DNSWARN_COMM_ERROR'))
        self.assertTrue(META_LOOKUP.is_error('DEPREC_COMMENT'))
        self.assertFalse(META_LOOKUP.is_error('VALID'))


