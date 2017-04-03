import unittest
from IsEmail.dns_functions import dns_lookup, ISEMAIL_DNS_LOOKUP_LEVELS, DNSTimeoutError, DNSCommError

LL = ISEMAIL_DNS_LOOKUP_LEVELS

class TestDNSFuncs(unittest.TestCase):
    # 'DNSWARN_INVALID_TLD', 'DNSWARN_NO_MX_RECORD', 'DNSWARN_NO_RECORD'

    def test_lookup(self):
        test_data = [
            # (num, domain_name, lookup_type, expected_return, raised_error, kwargs_dict)
            (1, 'example.com', LL.NO_LOOKUP, ''),

            (100, 'example.com', LL.TLD_MATCH, ''),
            (101, 'example.foobar', LL.TLD_MATCH, 'DNSWARN_INVALID_TLD'),

            (201, 'example.com', LL.ANY_RECORD, ''),
            (202, 'example.foobar', LL.ANY_RECORD, 'DNSWARN_INVALID_TLD'),
            (203, 'no_domain.example.com', LL.ANY_RECORD, 'DNSWARN_NO_RECORD'),

            (301, 'iana.org', LL.MX_RECORD, ''),
            (302, 'example.foobar', LL.MX_RECORD, 'DNSWARN_INVALID_TLD'),
            (303, 'no_domain.example.com', LL.MX_RECORD, 'DNSWARN_NO_RECORD'),
            (304, 'example.com', LL.MX_RECORD, 'DNSWARN_NO_MX_RECORD'),

            # Force Sockets
            (401, 'example.com', LL.ANY_RECORD, '', None, {'force_sockets': True}),
            (401, 'no_domain.example.com', LL.ANY_RECORD, 'DNSWARN_NO_RECORD', None, {'force_sockets': True}),

            # sockets with MX
            (501, 'example.com', LL.MX_RECORD, '', ImportError, {'force_sockets': True}),

            # comm error
            (601, 'example.com', LL.ANY_RECORD, 'DNSWARN_COMM_ERROR', None, {'servers': '127.0.0.1', 'timeout': 1, 'raise_on_comm_error': False}),
            (602, 'example.com', LL.ANY_RECORD, '', DNSTimeoutError, {'servers': '127.0.0.1', 'timeout': 1}),

            # no tld list
            (701, 'example.com', LL.TLD_MATCH, '', AttributeError, {'tld_list': []}),
            (702, 'example.com', LL.ANY_RECORD, '', None, {'tld_list': []}),

            # manual TLD list
            (801, 'example.foobar', LL.TLD_MATCH, '', None, {'tld_list': ['BLAH', 'FOOBAR']}),
            (802, 'example.com', LL.TLD_MATCH, 'DNSWARN_INVALID_TLD', None, {'tld_list': ['BLAH', 'FOOBAR']}),

            # force server
            (901, 'example.com', LL.ANY_RECORD, '', None, {'servers': '8.8.8.8'}),
        ]

        LIMIT_TO = -1

        if LIMIT_TO != -1:
            with self.subTest('LIMITING TEST TO %s' % LIMIT_TO):
                self.fail('ALERT, this test is limited.')

        for test in test_data:
            test_name = '#%s - %s' % (test[0], test[1])
            with self.subTest(test_name):
                if LIMIT_TO == -1 or LIMIT_TO == test[0]:
                    tmp_kwargs = {'domain_name': test[1], 'lookup_level': test[2]}
                    if len(test) > 5:
                        tmp_kwargs.update(test[5])
                    if len(test) > 4 and test[4] is not None:
                        with self.subTest(test_name + ' - Exception'):
                            with self.assertRaises(test[4]):
                                tmp_ret = dns_lookup(**tmp_kwargs)
                    else:
                        tmp_ret = dns_lookup(**tmp_kwargs)
                        with self.subTest(test_name + ' - response'):
                            self.assertEquals(tmp_ret, test[3])
