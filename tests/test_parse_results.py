import unittest
from parse_results import ParseEmailResult, ParseResultFootball
from meta_data import META_LOOKUP, ISEMAIL_RESULT_CODES


class TestParseFootball(unittest.TestCase):

    def test_init(self):
        f = ParseResultFootball()
        self.assertEquals(f.length, 0)

        f += 10
        self.assertEquals(f.length, 10)

        f -= 5
        self.assertEquals(f.length, 5)

    def test_math(self):
        f = ParseResultFootball()
        f2 = ParseResultFootball()

        self.assertEquals(f.length, 0)

        f += 10
        self.assertEquals(f.length, 10)

        f2 += 10
        f2 += f
        self.assertEquals(f2.length, 20)


    def test_init_length(self):
        f = ParseResultFootball(10)

        self.assertEquals(f.length, 10)

    def test_init_length_full(self):

        f = ParseResultFootball(13, diag="VALID", begin=20)

        self.assertEquals(f.length, 13)

    def test_comp_with_int(self):
        f = ParseResultFootball(10)

        self.assertTrue(f > 5)
        self.assertTrue(f >= 10)
        self.assertTrue(f == 10)
        self.assertTrue(f != 20)
        self.assertTrue(f < 21)
        self.assertTrue(f <= 10)

    def test_comp_with_fb(self):
        f = ParseResultFootball(10)
        f10 = ParseResultFootball(10)
        f5 = ParseResultFootball(5)
        f20 = ParseResultFootball(20)

        self.assertTrue(f > f5)
        self.assertTrue(f >= f10)
        self.assertTrue(f == f10)
        self.assertTrue(f != f20)
        self.assertTrue(f < f20)
        self.assertTrue(f <= f10)


class TestMetaLookup(unittest.TestCase):

    def test_lenths(self):
        self.assertEquals(len(META_LOOKUP.categories), 7)
        self.assertEquals(len(META_LOOKUP.diags), 54)

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


class TestParseEmailResults(unittest.TestCase):
    def test_add_ok_result(self):
        per = ParseEmailResult('test_email_in')

        self.assertTrue(per)
        self.assertEquals(len(per), 0)

        per.add_result('VALID', begin=1, length=1)
        self.assertTrue(per)
        self.assertEquals(len(per), 1)
        self.assertTrue(per.ok)
        self.assertFalse(per.error)
        self.assertFalse(per.warning)


    def test_add_error_result(self):
        per = ParseEmailResult('test_email_in')

        per.add_result('ERR_FWS_CRLF_X2', begin=1, length=1)
        self.assertFalse(per)
        self.assertEquals(len(per), 1)
        self.assertFalse(per.ok)
        self.assertTrue(per.error)
        self.assertFalse(per.warning)


    def test_add_warn_result(self):
        per = ParseEmailResult('test_email_in')

        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertTrue(per)
        self.assertEquals(len(per), 1)
        self.assertFalse(per.ok)
        self.assertFalse(per.error)
        self.assertTrue(per.warning)

    def test_add_mult_result(self):
        per = ParseEmailResult('test_email_in')

        self.assertTrue(per)
        self.assertEquals(len(per), 0)

        per.add_result('VALID', begin=1, length=1)
        self.assertTrue(per)
        self.assertEquals(len(per), 1)
        self.assertTrue(per.ok)
        self.assertFalse(per.error)
        self.assertFalse(per.warning)

        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertTrue(per)
        self.assertEquals(len(per), 2)
        self.assertFalse(per.ok)
        self.assertFalse(per.error)
        self.assertTrue(per.warning)

        per.add_result('ERR_FWS_CRLF_X2', begin=1, length=1)
        self.assertFalse(per)
        self.assertEquals(len(per), 3)
        self.assertFalse(per.ok)
        self.assertTrue(per.error)
        self.assertFalse(per.warning)

        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertFalse(per)
        self.assertEquals(len(per), 4)
        self.assertFalse(per.ok)
        self.assertTrue(per.error)
        self.assertFalse(per.warning)


    def test_error_on_warn(self):
        per = ParseEmailResult('test_email_in', error_on_warning=True)

        per.add_result('VALID', begin=1, length=1)
        self.assertTrue(per)
        self.assertEquals(len(per), 1)
        self.assertTrue(per.ok)
        self.assertFalse(per.error)
        self.assertFalse(per.warning)

        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertFalse(per)
        self.assertEquals(len(per), 2)
        self.assertFalse(per.ok)
        self.assertTrue(per.error)
        self.assertFalse(per.warning)

        per.add_result('VALID', begin=1, length=1)
        self.assertFalse(per)
        self.assertEquals(len(per), 3)
        self.assertFalse(per.ok)
        self.assertTrue(per.error)
        self.assertFalse(per.warning)


    def test_error_on_value(self):
        per = ParseEmailResult('test_email_in', error_on_warning=True)

        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertFalse(per)
        self.assertEquals(len(per), 1)
        self.assertFalse(per.ok)
        self.assertTrue(per.error)
        self.assertFalse(per.warning)

    def test_verbose_false(self):
        per = ParseEmailResult('test_email_in', verbose=False)

        self.assertTrue(per)
        self.assertEquals(len(per), 0)

        per.add_result('VALID', begin=1, length=1)
        self.assertTrue(per)
        self.assertEquals(len(per), 0)
        self.assertTrue(per.ok)
        self.assertFalse(per.error)
        self.assertFalse(per.warning)

        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertTrue(per)
        self.assertEquals(len(per), 0)
        self.assertFalse(per.ok)
        self.assertFalse(per.error)
        self.assertTrue(per.warning)

        per.add_result('ERR_FWS_CRLF_X2', begin=1, length=1)
        self.assertFalse(per)
        self.assertEquals(len(per), 0)
        self.assertFalse(per.ok)
        self.assertTrue(per.error)
        self.assertFalse(per.warning)

        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)
        self.assertFalse(per)
        self.assertEquals(len(per), 0)
        self.assertFalse(per.ok)
        self.assertTrue(per.error)
        self.assertFalse(per.warning)

    def test_contains(self):
        per = ParseEmailResult('test_email_in')

        self.assertTrue(per)
        self.assertEquals(len(per), 0)

        per.add_result('VALID', begin=1, length=1)
        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)
        per.add_result('ERR_FWS_CRLF_X2', begin=1, length=1)
        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)

        self.assertIn('DNSWARN_NO_MX_RECORD', per)
        self.assertIn('ISEMAIL_VALID_CATEGORY', per)

        self.assertNotIn('foobar', per)


    def test_get_item_diag(self):
        per = ParseEmailResult('test_email_in')

        self.assertTrue(per)
        self.assertEquals(len(per), 0)

        per.add_result('VALID', begin=1, length=1)
        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)
        per.add_result('ERR_FWS_CRLF_X2', begin=1, length=1)
        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)

        tmp_res = per['DNSWARN_NO_MX_RECORD']

        self.assertEquals(len(tmp_res), 2)
        self.assertEquals(tmp_res[0].diag.key, 'DNSWARN_NO_MX_RECORD')

    def test_get_item_cat(self):

        per = ParseEmailResult('test_email_in')

        self.assertTrue(per)
        self.assertEquals(len(per), 0)

        per.add_result('VALID', begin=1, length=1)
        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)
        per.add_result('ERR_FWS_CRLF_X2', begin=1, length=1)
        per.add_result('DNSWARN_NO_MX_RECORD', begin=1, length=1)

        tmp_res = per['ISEMAIL_VALID_CATEGORY']

        self.assertEquals(len(tmp_res), 1)
        self.assertEquals(tmp_res[0].diag.category.key, 'ISEMAIL_VALID_CATEGORY')

