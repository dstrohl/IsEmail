import unittest
import json
from parse_results import ParseResultFootball, ParsingError, ParseHistoryData
from meta_data import META_LOOKUP, ISEMAIL_RESULT_CODES, ISEMAIL_DNS_LOOKUP_LEVELS, ISEMAIL_DOMAIN_TYPE


def _test_name(l1, l2=None, l3=None, suffix=None):
    tmp_ret = l1
    if l2 is not None:
        tmp_ret += '-'
        tmp_ret += RETURN_OBJ_L2[l2][0]
    if l3 is not None:
        tmp_ret += '-'
        tmp_ret += RETURN_OBJ_L3[l3][0]
    if suffix is not None:
        tmp_ret += '-'
        tmp_ret += suffix
    return tmp_ret


class TestFullResults(unittest.TestCase):
    COMPLEX_PARSER = dict(
        email_in='(comment1)"foobar"(comment2)@(comment3)[example.com](comment4)',
        at_loc=28,
        local_comments={0: 'comment1', 18: 'comment2'},
        domain_comments={29: 'comment3', 52: 'comment4'},
        domain_type=ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT,
    )
    LOCAL_QS_COM_PARSER = dict(
        email_in='(comment1)"foobar"(comment2)@example.com',
        at_loc=28,
        local_comments={0: 'comment1', 18: 'comment2'},
        domain_type=ISEMAIL_DOMAIN_TYPE.DNS,
    )
    DOMAIN_LIT_COM_PARSER = dict(
        email_in='foobar@(comment3)[example.com](comment4)',
        at_loc=6,
        domain_comments={7: 'comment3', 30: 'comment4'},
        domain_type=ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT,
    )
    LOCAL_QS_PARSER = dict(
        email_in='"foobar"@example.com',
        at_loc=8,
        domain_type=ISEMAIL_DOMAIN_TYPE.DNS,
    )
    DOMAIN_LIT_PARSER = dict(
        email_in='foobar@[example.com]',
        at_loc=6,
        domain_type=ISEMAIL_DOMAIN_TYPE.DOMAIN_LIT,
    )
    NORMAL_PARSER = dict(
        email_in='foobar@example.com',
        at_loc=6,
        domain_type=ISEMAIL_DOMAIN_TYPE.DNS,
    )
    IPV4_PARSER = dict(
        email_in='"foobar"@[1.2.3.4]',
        at_loc=8,
        domain_type=ISEMAIL_DOMAIN_TYPE.IPv4,
    )
    IPV6_PARSER = dict(
        email_in='foobar@[IPV6:1::6:7:8]',
        at_loc=6,
        domain_type=ISEMAIL_DOMAIN_TYPE.IPv6,
    )
    GENERAL_LIT_PARSER = dict(
        email_in='foobar@[http:example.com]',
        at_loc=6,
        domain_type=ISEMAIL_DOMAIN_TYPE.GENERAL_LIT,
    )

    VALID = ['VALID']
    MULT_WARN = ['RFC5322_DOMAIN', 'DEPREC_COMMENT']
    WARN = ['RFC5322_DOMAIN', 'DEPREC_COMMENT']
    MULT_WARN_ERR = ['RFC5322_DOMAIN', 'DEPREC_COMMENT', 'ERR_DOT_END']
    MULT_WARN_ERR_POS = [('RFC5322_DOMAIN', 8, 6), ('DEPREC_COMMENT', 0, 3), ('ERR_DOT_END', 10, 0)]
    ERR = ['ERR_DOT_END']
    COMPLEX_DIAGS = ['DNSWARN_INVALID_TLD', 'RFC5321_TLD_NUMERIC', 'RFC5321_QUOTED_STRING',
                     'RFC5321_ADDRESS_LITERAL', 'ERR_UNCLOSED_COMMENT']

    # 'foobar@example.com'
    _dot_atom = ParseHistoryData('dot_atom', begin=0, length=6)
    _local_part = ParseHistoryData('local_part', begin=0, length=6)
    _local_part.append(_dot_atom)

    _cfws1 = ParseHistoryData('cfws1', begin=7, length=2)
    _domain_lit = ParseHistoryData('domain_lit', begin=9, length=7)
    _cfws2 = ParseHistoryData('cfws2', begin=16, length=2)

    _domain_part = ParseHistoryData('domain_part', begin=7, length=11)
    _domain_part.extend((_cfws1, _domain_lit, _cfws2))

    TEST_HISTORY = ParseHistoryData('address_spec', begin=0, length=18)
    TEST_HISTORY.extend((_local_part, _domain_part))

    _address_spec = TEST_HISTORY

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
        at_loc = None
        domain_type = None
        local_comments = None
        domain_comments = None
        history = None

        if parser is None:
            parser = self.make_parser()
        if isinstance(parser, dict):
            at_loc = parser.pop('at_loc', None)
            domain_type = parser.pop('domain_type', None)
            local_comments = parser.pop('local_comments', None)
            domain_comments = parser.pop('domain_comments', None)
            history = parser.pop('_history', None)
            parser = self.make_parser(**parser)

        if isinstance(parser, str):
            parser = self.make_parser(email_in=parser)

        tmp_fb = ParseResultFootball(parser)

        tmp_fb += length
        tmp_fb.begin = position

        if at_loc is not None:
            tmp_fb.at_loc = at_loc
        if domain_type is not None:
            tmp_fb.domain_type = domain_type
        if local_comments is not None:
            tmp_fb._local_comments = local_comments
        if domain_comments is not None:
            tmp_fb._domain_comments = domain_comments
        if history is not None:
            tmp_fb._history = history

        if kwargs or args:
            tmp_fb(*args, raise_on_error=raise_on_error, **kwargs)

        if diags is not None:
            if isinstance(diags, str):
                tmp_fb(diags, raise_on_error=raise_on_error)
            else:
                if isinstance(diags[0], str):
                    tmp_fb(*diags, raise_on_error=raise_on_error)
                else:
                    for d in diags:
                        tmp_fb.add_diag(diag=d[0], begin=d[1], length=d[2], raise_on_error=raise_on_error)

        else:
            tmp_fb('VALID')
        return tmp_fb

    def make_result(self, *args, parser=None, diags=None, dns_lookup_level=None, raise_on_error=False, length=6,
                    position=0, **kwargs):
        tmp_fb = self.make_football(*args, parser=parser, diags=diags, length=length, position=position,
                                    raise_on_error=raise_on_error, **kwargs)
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

    def test_warning(self):
        tmp_resp = self.make_result(diag='RFC5322_TOO_LONG')
        self.assertFalse(tmp_resp.ok)
        self.assertTrue(tmp_resp.warning)
        self.assertFalse(tmp_resp.error)

    def test_error(self):
        tmp_resp = self.make_result(diag='ERR_EMPTY_ADDRESS')
        self.assertFalse(tmp_resp.ok)
        self.assertFalse(tmp_resp.warning)
        self.assertTrue(tmp_resp.error)

    def test_parsing_complex(self):
        """
        COMPLEX_PARSER = dict(
            email_in='(comment1)"foobar"(comment2)@(comment3)[example.com](comment4)',
            at_loc=28,
            local_comments={0: 'comment1', 18: 'comment2'},
            domain_comments={29: 'comment3', 52: 'comment4'},
        )
        """
        tmp_resp = self.make_result(parser=self.COMPLEX_PARSER)
        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, '(comment1)"foobar"(comment2)')

        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '(comment3)[example.com](comment4)')

        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, '"foobar"')

        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[example.com]')

        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')

        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')

        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, '"foobar"@[example.com]')

        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, '(comment1)"foobar"(comment2)@(comment3)[example.com](comment4)')

        with self.subTest('local_comments'):
            self.assertCountEqual(tmp_resp.local_comments, ['comment1', 'comment2'])

        with self.subTest('domain_comments'):
            self.assertCountEqual(tmp_resp.domain_comments, ['comment3', 'comment4'])

    def test_parsing_qs_com(self):
        """
        LOCAL_QS_COM_PARSER = dict(
            email_in='(comment1)"foobar"(comment2)@example.com',
            at_loc=28,
            local_comments={0: 'comment1', 18: 'comment2'},
        )
        """
        tmp_resp = self.make_result(parser=self.LOCAL_QS_COM_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, '(comment1)"foobar"(comment2)')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, 'example.com')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, '"foobar"')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, 'example.com')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, '"foobar"@example.com')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, '(comment1)"foobar"(comment2)@example.com')
        with self.subTest('local_comments'):
            self.assertCountEqual(tmp_resp.local_comments, ['comment1', 'comment2'])
        with self.subTest('domain_comments'):
            self.assertCountEqual(tmp_resp.domain_comments, [])

    def test_parsing_dom_lit_com(self):
        """
        DOMAIN_LIT_COM_PARSER = dict(
            email_in='foobar@(comment2)[example.com](comment4)',
            at_loc=6,
            domain_comments={7: 'comment3', 30: 'comment4'},
        )
        """
        tmp_resp = self.make_result(parser=self.DOMAIN_LIT_COM_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, 'foobar')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '(comment3)[example.com](comment4)')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, 'foobar')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[example.com]')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, 'foobar@[example.com]')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, 'foobar@(comment3)[example.com](comment4)')
        with self.subTest('local_comments'):
            self.assertCountEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertCountEqual(tmp_resp.domain_comments, ['comment3', 'comment4'])

    def test_parsing_qs(self):
        """
        LOCAL_QS_PARSER = dict(
            email_in='"foobar"@example.com',
            at_loc=8,
        )
        """
        tmp_resp = self.make_result(parser=self.LOCAL_QS_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, '"foobar"')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, 'example.com')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, '"foobar"')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, 'example.com')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, '"foobar"@example.com')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, '"foobar"@example.com')
        with self.subTest('local_comments'):
            self.assertCountEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertCountEqual(tmp_resp.domain_comments, [])

    def test_parsing_dom_lit(self):
        """
        DOMAIN_LIT_PARSER = dict(
            email_in='foobar@[example.com]',
            at_loc=6,
        )
        """
        tmp_resp = self.make_result(parser=self.DOMAIN_LIT_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, 'foobar')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '[example.com]')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, 'foobar')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[example.com]')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, 'foobar@[example.com]')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, 'foobar@[example.com]')
        with self.subTest('local_comments'):
            self.assertEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertEqual(tmp_resp.domain_comments, [])

    def test_parsing_normal(self):
        """
        NORMAL_PARSER = dict(
            email_in='foobar@example.com',
            at_loc=6,
        )
        """
        tmp_resp = self.make_result(parser=self.NORMAL_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, 'foobar')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, 'example.com')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, 'foobar')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, 'example.com')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, 'example.com')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, 'foobar@example.com')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, 'foobar@example.com')
        with self.subTest('local_comments'):
            self.assertEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertEqual(tmp_resp.domain_comments, [])

    def test_parsing_ipv4(self):
        """
        IPV4_PARSER = dict(
            email_in='"foobar"@[1.2.3.4]',
            at_loc=8,
        )
        """

        tmp_resp = self.make_result(parser=self.IPV4_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, '"foobar"')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '[1.2.3.4]')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, '"foobar"')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[1.2.3.4]')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, '1.2.3.4')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, '"foobar"@[1.2.3.4]')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, '"foobar"@[1.2.3.4]')
        with self.subTest('local_comments'):
            self.assertEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertEqual(tmp_resp.domain_comments, [])

    def test_parsing_ipv6(self):
        """
        IPV6_PARSER = dict(
            email_in='foobar@[IPV6:1::6:7:8',
            at_loc=6,
        )
        """
        tmp_resp = self.make_result(parser=self.IPV6_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, 'foobar')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '[IPv6:1::6:7:8]')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, 'foobar')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[IPv6:1::6:7:8]')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, '1::6:7:8')
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, 'foobar@[IPv6:1::6:7:8]')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, 'foobar@[IPV6:1::6:7:8]')
        with self.subTest('local_comments'):
            self.assertEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertEqual(tmp_resp.domain_comments, [])

    def test_parsing_gen_lit(self):
        """
        GENERAL_LIT_PARSER = dict(
            email_in='foobar@[http:example.com]',
            at_loc=6,
        )
        """
        tmp_resp = self.make_result(parser=self.GENERAL_LIT_PARSER)

        with self.subTest('full_local'):
            self.assertEqual(tmp_resp.full_local, 'foobar')
        with self.subTest('full_domain'):
            self.assertEqual(tmp_resp.full_domain, '[http:example.com]')
        with self.subTest('clean_local'):
            self.assertEqual(tmp_resp.clean_local, 'foobar')
        with self.subTest('clean_domain'):
            self.assertEqual(tmp_resp.clean_domain, '[http:example.com]')
        with self.subTest('local'):
            self.assertEqual(tmp_resp.local, 'foobar')
        with self.subTest('domain'):
            self.assertEqual(tmp_resp.domain, ['http', 'example.com'])
        with self.subTest('clean_address'):
            self.assertEqual(tmp_resp.clean_address, 'foobar@[http:example.com]')
        with self.subTest('full_address'):
            self.assertEqual(tmp_resp.full_address, 'foobar@[http:example.com]')
        with self.subTest('local_comments'):
            self.assertEqual(tmp_resp.local_comments, [])
        with self.subTest('domain_comments'):
            self.assertEqual(tmp_resp.domain_comments, [])

    # def test_trace(self):
    #     tmp_resp = self.make_result()
    #     self.assertEqual(tmp_resp.trace, 'This is a trace string')

    def test_history(self):
        tmp_resp = self.make_result(parser={'_history': self.TEST_HISTORY})

        self.assertEqual(tmp_resp.history(depth=1), 'address_spec(...)')
        self.assertEqual(tmp_resp.history(depth=2), 'address_spec(local_part(...), domain_part(...))')
        self.assertEqual(tmp_resp.history(),
                         'address_spec(local_part(dot_atom), domain_part(cfws1, domain_lit, cfws2))')

    def test_at(self):

        """
        MULT_WARN_ERR_POS = [
            ('RFC5322_DOMAIN', 8, 6),
            ('DEPREC_COMMENT', 0, 3),
            ('ERR_DOT_END', 10, 0)]

        'foobar@example.com'

        _dot_atom = ParseHistoryData('dot_atom', begin=0, length=6)
        _local_part = ParseHistoryData('local_part', begin=0, length=6)
        _local_part.append(_dot_atom)

        _cfws1 = ParseHistoryData('cfws', begin=7, length=2)
        _domain_lit = ParseHistoryData('domain_lit', begin=9, length=7)
        _cfws2 = ParseHistoryData('cfws', begin=16, length=2)

        _domain_part = ParseHistoryData('domain_part', begin=0, length=11)
        _domain_part.extend((_cfws1, _domain_lit, _cfws2))

        TEST_HISTORY = ParseHistoryData('address_spec', begin=0, length=18)
        TEST_HISTORY.extend((_local_part, _domain_part))

        """

        TESTS = [
            # (index, letter, diag_codes, hist_codes),
            (0, 'f', ['DEPREC_COMMENT'], ['address_spec', 'local_part', 'dot_atom']),
            (1, 'o', ['DEPREC_COMMENT'], ['address_spec', 'local_part', 'dot_atom']),
            (2, 'o', ['DEPREC_COMMENT'], ['address_spec', 'local_part', 'dot_atom']),
            (3, 'b', [], ['address_spec', 'local_part', 'dot_atom']),
            (4, 'a', [], ['address_spec', 'local_part', 'dot_atom']),
            (5, 'r', [], ['address_spec', 'local_part', 'dot_atom']),
            (6, '@', [], ['address_spec', ]),
            (7, 'e', [], ['address_spec', 'domain_part', 'cfws1']),
            (8, 'x', ['RFC5322_DOMAIN'], ['address_spec', 'domain_part', 'cfws1']),
            (9, 'a', ['RFC5322_DOMAIN'], ['address_spec', 'domain_part', 'domain_lit']),
            (10, 'm', ['RFC5322_DOMAIN', 'ERR_DOT_END'], ['address_spec', 'domain_part', 'domain_lit']),
            (11, 'p', ['RFC5322_DOMAIN'], ['address_spec', 'domain_part', 'domain_lit']),
            (12, 'l', ['RFC5322_DOMAIN'], ['address_spec', 'domain_part', 'domain_lit']),
            (13, 'e', ['RFC5322_DOMAIN'], ['address_spec', 'domain_part', 'domain_lit']),
            (14, '.', [], ['address_spec', 'domain_part', 'domain_lit']),
            (15, 'c', [], ['address_spec', 'domain_part', 'domain_lit']),
            (16, 'o', [], ['address_spec', 'domain_part', 'cfws2']),
            (17, 'm', [], ['address_spec', 'domain_part', 'cfws2']),
        ]

        LIMIT_TO = -1

        tmp_resp = self.make_result(
            diags=self.MULT_WARN_ERR_POS,
            parser={'_history': self.TEST_HISTORY})

        if LIMIT_TO != -1:
            with self.subTest('LIMITED TEST'):
                self.fail()

        for test in TESTS:
            if LIMIT_TO == -1 or LIMIT_TO == test[0]:
                with self.subTest('#' + str(test[0])):
                    hist_ret = test[3]
                    hist_obj_ret = []
                    for h in hist_ret:
                        hist_obj_ret.append(getattr(self, '_' + h))

                    diag_ret = test[2]
                    diag_obj_ret = []
                    for d in diag_ret:
                        diag_obj_ret.append(META_LOOKUP[d])

                    both_ret = hist_ret + diag_ret
                    both_obj_ret = hist_obj_ret + diag_obj_ret

                    with self.subTest('#' + str(test[0]) + '-hist'):
                        tmp_ret = tmp_resp.at(test[0], ret_history=True, ret_diags=False, ret_obj=False,
                                              template='{key}')
                        tmp_msg = '\n\nExpected: %r\nReturned: %r\n' % (hist_ret, tmp_ret)
                        self.assertCountEqual(tmp_ret, hist_ret, msg=tmp_msg)

                    with self.subTest('#' + str(test[0]) + '-hist_obj'):
                        tmp_ret = tmp_resp.at(test[0], ret_history=True, ret_diags=False, ret_obj=True,
                                              template='{key}')
                        tmp_msg = '\n\nExpected: %r\nReturned: %r\n' % (hist_obj_ret, tmp_ret)
                        self.assertCountEqual(tmp_ret, hist_obj_ret, msg=tmp_msg)

                    with self.subTest('#' + str(test[0]) + '-diag'):
                        tmp_ret = tmp_resp.at(test[0], ret_history=False, ret_diags=True, ret_obj=False,
                                              template='{key}')
                        tmp_msg = '\n\nExpected: %r\nReturned: %r\n' % (diag_ret, tmp_ret)
                        self.assertCountEqual(tmp_ret, diag_ret, msg=tmp_msg)

                    with self.subTest('#' + str(test[0]) + '-diag_obj'):
                        tmp_ret = tmp_resp.at(test[0], ret_history=False, ret_diags=True, ret_obj=True,
                                              template='{key}')
                        tmp_msg = '\n\nExpected: %r\nReturned: %r\n' % (diag_obj_ret, tmp_ret)
                        self.assertCountEqual(tmp_ret, diag_obj_ret, msg=tmp_msg)

                    with self.subTest('#' + str(test[0]) + '-both'):
                        tmp_ret = tmp_resp.at(test[0], ret_history=True, ret_diags=True, ret_obj=False,
                                              template='{key}')
                        tmp_msg = '\n\nExpected: %r\nReturned: %r\n' % (both_ret, tmp_ret)
                        self.assertCountEqual(tmp_ret, both_ret, msg=tmp_msg)

                    with self.subTest('#' + str(test[0]) + '-both_obj'):
                        tmp_ret = tmp_resp.at(test[0], ret_history=True, ret_diags=True, ret_obj=True, template='{key}')
                        tmp_msg = '\n\nExpected: %r\nReturned: %r\n' % (both_obj_ret, tmp_ret)
                        self.assertCountEqual(tmp_ret, both_obj_ret, msg=tmp_msg)

    def test_contains(self):
        tmp_resp = self.make_result(diags=self.COMPLEX_DIAGS)
        tmp_answ = 'RFC5321_ADDRESS_LITERAL' in tmp_resp
        self.assertTrue(tmp_answ)

        tmp_answ = 'foobar' in tmp_resp
        self.assertFalse(tmp_answ)

    def test_getitem(self):
        tmp_resp = self.make_result(diags=self.COMPLEX_DIAGS)
        tmp_answ = tmp_resp['RFC5321_ADDRESS_LITERAL']
        self.assertEqual(tmp_answ, ML['RFC5321_ADDRESS_LITERAL'])

    def run_ret_obj_test(self, l1, l2, l3, call_diag=False):
        tmp_res = self.make_result(diags=self.COMPLEX_DIAGS)

        kwargs = {}
        kwargs.update(RETURN_OBJ_L2[l2][1])
        kwargs.update(RETURN_OBJ_L3[l3][1])
        if 'filter' in kwargs:
            kwargs['filter'] = RETURN_OBJ_TESTS[l1][l2]['filter']

        if call_diag:
            if l1 == 'object_list':
                kwargs['return_obj'] = True
                kwargs['return_as_list'] = True

            elif l1 == 'object_dict':
                kwargs['return_obj'] = True
                kwargs['return_as_list'] = False

            elif l1 == 'key_list':
                kwargs['return_obj'] = False
                kwargs['return_as_list'] = True

            elif l1 == 'key_dict':
                kwargs['return_obj'] = False
                kwargs['return_as_list'] = False

            tmp_ret = tmp_res.diag(**kwargs)
        else:
            tmp_ret = tmp_res.report(l1, **kwargs)

        tmp_exp = RETURN_OBJ_TESTS[l1][l2][l3]

        if l1 in ['key_dict', 'key_list', 'desc_list']:
            tmp_ret_str = json.dumps(tmp_ret, indent=4)
            tmp_exp_str = json.dumps(tmp_exp, indent=4)
        elif l1 in ['document_string', 'formatted_string']:
            tmp_ret_str = tmp_ret
            tmp_exp_str = tmp_exp
        else:
            tmp_ret_str = repr(tmp_ret)
            tmp_exp_str = repr(tmp_exp)

        tmp_msg = '\n\n\nItems do not compare\n\n'
        tmp_msg += 'L1: %s\n' % l1
        tmp_msg += 'L2: %s\n' % l2
        tmp_msg += 'L3: %s\n' % l3
        tmp_msg += 'Test Name: %s\n\n' % _test_name(l1, l2, l3)

        tmp_msg += 'kwargs:\n%s\n\n' % json.dumps(kwargs, indent=4)
        tmp_msg += 'Expected:\n************************\n' \
                   '%s\n\nReturned\n************************\n%s\n\n' % (tmp_exp_str, tmp_ret_str)

        tmp_msg += '\n\n\n'
        tmp_msg += 'Expected: %r\nReturned: %r\n\n' % (tmp_exp_str, tmp_ret_str)

        self.assertEqual(tmp_ret, tmp_exp, msg=tmp_msg)

    def test_return_objects(self):
        """
        {
        L1    'report_name':
        L2        'inc_whatever':
                       'raises'
                      'filter':
        L3            'show_all':
                        'show_all_filtered'
                        'show_one'
                        'show_one_filtered'
        """
        # META_LOOKUP.set_error_on('RFC5321_QUOTED_STRING')
        LIMIT_TO = ['', '', '']
        # LIMIT_TO = ['desc_list', 'both', 'all-flt']

        if LIMIT_TO != ['', '', '']:
            with self.subTest('NOTE: Test Limited to: %r' % LIMIT_TO):
                self.fail()

        for l1 in RETURN_OBJ_TESTS.keys():
            if LIMIT_TO[0] == '' or LIMIT_TO[0] == l1:
                for l2 in RETURN_OBJ_L2.keys():
                    if LIMIT_TO[1] == '' or LIMIT_TO[1] == RETURN_OBJ_L2[l2][0]:
                        if not 'raises' in RETURN_OBJ_TESTS[l1][l2]:
                            for l3 in RETURN_OBJ_L3.keys():
                                if LIMIT_TO[2] == '' or LIMIT_TO[2] == RETURN_OBJ_L3[l3][0]:
                                    for i in RETURN_OBJ_MD_CHANGE:
                                        META_LOOKUP.clear_overrides()
                                        if _test_name(l1, l2, l3).startswith(i):
                                            META_LOOKUP.set_error_on(RETURN_OBJ_MD_CHANGE[i])
                                    with self.subTest(_test_name(l1, l2, l3)):
                                        self.run_ret_obj_test(l1, l2, l3)
                                    with self.subTest(_test_name(l1, l2, l3) + '-DIAG'):
                                        if l1 in ['object_list', 'object_dict', 'key_list', 'key_dict']:
                                            self.run_ret_obj_test(l1, l2, l3, call_diag=True)


