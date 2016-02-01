import unittest
# from .old_test_data import TESTS
# from CompIntel.helpers.IsEmail.meta import META_DICT
from py_is_email import ParseEmail
from meta_data import *
import xml.etree.ElementTree as ET
from collections import OrderedDict
from meta import IsEmailMetaData

# IS_EMAIL_META = IsEmailMetaData()

# TEST_DATA = ET.parse('tests.xml').getroot()
# TEST_DATA2 = ET.parse('tests-original.xml').getroot()
import logging
import sys
'''
logger = logging.getLogger()
logger.setLevel(0)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)
'''

# from testfixtures import LogCapture

def set_find(elem):

    def my_find(find_str, default=''):
        tmp_ret = elem.find(find_str)
        if tmp_ret is None:
            return default
        else:
            return tmp_ret.text
    return my_find

'''
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
'''

class TestSets(object):
    def __init__(self, xml_file):
        self.data = ET.parse(xml_file).getroot().findall('test')

    def __iter__(self):
        for i in self.data:
            yield GetTest(i)

elements_title_list = (
    ISEMAIL_ELEMENT_LOCALPART,
    ISEMAIL_ELEMENT_COMMENT,
    ISEMAIL_ELEMENT_QUOTEDSTRING,
    ISEMAIL_ELEMENT_DOMAINPART,
    ISEMAIL_ELEMENT_DOMAIN_LIT_IPV4,
    ISEMAIL_ELEMENT_DOMAIN_LIT_IPV6,
    ISEMAIL_ELEMENT_DOMAIN_LIT_GEN,
)

class GetTest(object):

    def __init__(self, test_rec):
        self._test_rec = test_rec

        self.id = int(self._test_rec.get('id'))
        self.address = self.find_str('address')
        self.cat = self.find_str('category')
        self.source = self.find_str('source')
        self.source_link = self.find_str('sourcelink')
        self.max_diag = None

        diag_list = self.find_list('diagnosis')
        self.diags = OrderedDict()
        for diag in diag_list:
            tmp_pos = int(diag.get('pos') or '-1')
            tmp_diag = diag.text
            tmp_key = '%s: [pos: %s]' % (tmp_diag, tmp_pos)
            self.diags[tmp_key] = dict(
                position=tmp_pos,
                diag=META_LOOKUP.diags[tmp_diag])

            if self.max_diag is None:
                self.max_diag = tmp_diag

        self.elements = {}
        element_list = self._test_rec.find('elements')
        if element_list is not None:
            for name in elements_title_list:
                tmp_element_strings = []
                for item in element_list.findall(name):
                    tmp_element_strings.append(item.text)
                if tmp_element_strings:
                    self.elements[name] = tmp_element_strings

    def name(self, test_type=''):
        if test_type:
            test_type = '-%s' % test_type
        return '%s%s [%s]:  %s' % (self.id, test_type, self.max_diag, self.address)

    def find_str(self, find_str, default=''):
        tmp_ret = self._test_rec.find(find_str)
        if tmp_ret is None:
            return default
        else:
            return tmp_ret.text

    def find_list(self, find_list):
        tmp_ret = self._test_rec.findall(find_list)
        for i in tmp_ret:
            yield i

pe = ParseEmail()

def val_max_diag(ret, exp):
    assert ret == exp

def val_parse_run(test):
    tmp_res = pe(test.address)
    val_max_diag.description = test.name('max_diag')
    yield val_max_diag, tmp_res['key'], test.max_diag


"""
def test_is_email():
    tests = TestSets('tests.xml')
    for test in tests:



        print(test.name())
        # with self.subTest(test.name('Run')):
        tmp_res = None
        val_parse_run.description = test.name()
        yield val_parse_run, test

        # with self.subTest(test.name('MaxDiag')):
        # yield val_max_diag, tmp_res['key'], test.max_diag
            # self.assertEqual(test.max_diag, tmp_res['key'])
        '''
        if test.elements:
            with self.subTest(test.name('elements')):
                for name, elements in test.elements.items():
                    tmp_element_list = pe.elements(element_name=name)
                    self.assertEqual(tmp_element_list, elements)

        if len(test.diags) > 1:
            with self.subTest(test.name('diags')):
                self.assertEqual(test.diags, pe.diags())
        '''
"""


class TestIsEmail(unittest.TestCase):
    def test_is_email(self):
        tests = TestSets('tests.xml')
        for test in tests:

            logger = logging.getLogger()
            logger.setLevel(0)
            stream_handler = logging.StreamHandler(sys.stdout)
            logger.addHandler(stream_handler)

            '''
            tmp_my_find = set_find(test)
            test_address = tmp_my_find('address') or ''
            test_id = int(test.get('id'))
            test_cat = tmp_my_find('category')
            test_diag = tmp_my_find('diagnosis')
            test_source = tmp_my_find('source')
            test_source_link = tmp_my_find('sourcelink')
            local_part = tmp_my_find('localpart')
            domain_part = tmp_my_find('domainpart')
            tmp_parse = {}
            tmp_name = 'id: %s [%s]:  %s' % (test_id, test_diag, test_address)
            '''

            # l = LogCapture()

            print(test.name())
            with self.subTest(test.name('Run')):

                tmp_res = pe(test.address)

                # print(tmp_res)

                # tmp_res_text = META_LOOKUP[int(tmp_res)]['key']
                '''
                msg = ['\n%s  =>  local: %s  /  domain:  %s\n' % (test.address, tmp_res[ISEMAIL_ELEMENT_LOCALPART], tmp_res[ISEMAIL_ELEMENT_DOMAINPART])]
                msg.append('Diags returned: %s' % tmp_res.responses(response_type='key_list'))
                msg.append('Should be : %s\nReturned  : %s\n' % (test.max_diag, tmp_res_text))
                msg.append('----------------------------------------------------')
                msg.append(IS_EMAIL_META[test.max_diag].short_string())
                msg.append('----------------------------------------------------')
                msg.append(IS_EMAIL_META[tmp_res_text].short_string())
                msg.append('=====================================================\n')
                msg = '\n'.join(msg)
                '''

                with self.subTest(test.name('MaxDiag')):
                    # yield val_max_diag, tmp_res['key'], test.max_diag
                    self.assertEqual(test.max_diag, tmp_res['key'])

                if test.elements:
                    with self.subTest(test.name('elements')):
                        for name, elements in test.elements.items():
                            tmp_element_list = pe.elements(element_name=name)
                            self.assertEqual(tmp_element_list, elements)

                if len(test.diags) > 1:
                    with self.subTest(test.name('diags')):
                        self.assertEqual(test.diags, pe.diags())

            # print(l)

            # l.uninstall()