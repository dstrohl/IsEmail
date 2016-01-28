import unittest
# from .old_test_data import TESTS
# from CompIntel.helpers.IsEmail.meta import META_DICT
from py_is_email import is_email
from meta_data import *
import xml.etree.ElementTree as ET

from meta import IsEmailMetaData

IS_EMAIL_META = IsEmailMetaData()

TEST_DATA = ET.parse('tests.xml').getroot()
TEST_DATA2 = ET.parse('tests-original.xml').getroot()


def set_find(elem):

    def my_find(find_str, default=''):
        tmp_ret = elem.find(find_str)
        if tmp_ret is None:
            return default
        else:
            return tmp_ret.text
    return my_find


def make_meta_dict():
    tmp_info = ET.parse('meta.xml').getroot()
    tmp_dict = {}

    for item in tmp_info[3]:
        tmp_value = item.get('id')
        tmp_key = int(item.find('value').text)
        tmp_dict[tmp_key] = tmp_value

        # print(tmp_key, ' : ', tmp_value)

    return tmp_dict

TEST_META = make_meta_dict()

class TestIsEmail(unittest.TestCase):
    def test_is_email(self):
        for test in TEST_DATA.findall('test'):
            tmp_my_find = set_find(test)
            test_address = tmp_my_find('address') or ''
            test_id = int(test.get('id'))
            test_cat = tmp_my_find('category')
            test_diag = tmp_my_find('diagnosis')
            test_source = tmp_my_find('source')
            test_source_link = tmp_my_find('sourcelink')
            local_part = tmp_my_find('local_part')
            domain_part = tmp_my_find('local_part')
            tmp_parse = {}

            tmp_name = 'id: %s [%s]:  %s' % (test_id, test_diag, test_address)

            with self.subTest(tmp_name):
                tmp_res = is_email(test_address)
                # print(tmp_res)
                tmp_res_text = TEST_META[int(tmp_res)]


                if tmp_res != tmp_res_text:

                    msg = ['\n%s  =>  local: %s  /  domain:  %s\n' % (test_address, tmp_res[ISEMAIL_COMPONENT_LOCALPART], tmp_res[ISEMAIL_COMPONENT_DOMAIN])]
                    msg.append('Diags returned: %s' % tmp_res.responses(response_type='key_list'))
                    msg.append('Should be : %s\nReturned  : %s\n' % (test_diag, tmp_res_text))
                    msg.append('----------------------------------------------------')
                    msg.append(IS_EMAIL_META[test_diag].short_string())
                    msg.append('----------------------------------------------------')
                    msg.append(IS_EMAIL_META[tmp_res_text].short_string())
                    msg.append('=====================================================\n')
                    msg = '\n'.join(msg)
                else:
                    msg = ''

                self.assertEqual(test_diag, tmp_res_text, msg=msg)

