import unittest
from dns_functions import has_dns_entry, has_mx_from_ip, has_mx_rec, tld_match

class TestDNSFuncs(unittest.TestCase):
    def test_base_lookup(self):
        has_dns_entry('danstrohl.com')

    def test_mx_lookup(self):

        has_mx_rec('com')

    def test_ip_lookup(self):

        has_mx_from_ip('0.0.0.0')

    def test_tld_lookup(self):

        print(tld_match('com'))
        print(tld_match('me.com'))
        print(tld_match('blah'))