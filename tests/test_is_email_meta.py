import unittest

from CompIntel.helpers.IsEmail.meta import IsEmailMetaData

IS_EMAIL_META = IsEmailMetaData()

class TestIsEmailMeta(unittest.TestCase):

    maxDiff = None

    def test_valid(self):
        iem = IS_EMAIL_META['ISEMAIL_VALID']

        short_str_check = 'VALID_CATEGORY / VALID:\n' \
                          '    - Address is valid\n' \
                          '    - Address is valid. Please note that this does not mean the address actually\n' \
                          '      exists, nor even that the domain actually exists. This address could be\n' \
                          '      issued by the domain owner without breaking the rules of any RFCs.\n'

        self.assertEqual('VALID', iem.id)
        self.assertEqual('VALID_CATEGORY', iem.cat_id)
        self.assertEqual('VALID_CATEGORY / VALID', iem.name)

        self.assertEqual(short_str_check, iem.short_string())

    def test_valid_int(self):
        iem = IS_EMAIL_META[0]

        short_str_check = 'VALID_CATEGORY / VALID:\n' \
                          '    - Address is valid\n' \
                          '    - Address is valid. Please note that this does not mean the address actually\n' \
                          '      exists, nor even that the domain actually exists. This address could be\n' \
                          '      issued by the domain owner without breaking the rules of any RFCs.\n'

        self.assertEqual('VALID', iem.id)
        self.assertEqual('VALID_CATEGORY', iem.cat_id)
        self.assertEqual('VALID_CATEGORY / VALID', iem.name)

        self.assertEqual(short_str_check, iem.short_string())
