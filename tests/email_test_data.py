TESTS = [{
    'diag': 'VALID',
    'comment': '',
    'addr': 'test@iana.org',
    'id_num': '1',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'ERR_EMPTY_ADDRESS',
    'comment': '',
    'addr': '',
    'id_num': '2',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_NO_DOMAIN_SEP',
    'comment': '',
    'addr': 'test',
    'id_num': '3',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_NO_LOCAL_PART',
    'comment': '',
    'addr': '@',
    'id_num': '4',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_NO_DOMAIN_PART',
    'comment': '',
    'addr': 'test@',
    'id_num': '5',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'VALID',
    'comment': "io. currently has an MX-record (Feb 2011). Some DNS setups seem to find it, some don't. If you don't see the MX for io. then try setting your DNS server to 8.8.8.8 (the Google DNS server)",
    'addr': 'test@io',
    'id_num': '6',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'ERR_NO_LOCAL_PART',
    'comment': 'io. currently has an MX-record (Feb 2011)',
    'addr': '@io',
    'id_num': '7',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_NO_LOCAL_PART',
    'comment': '',
    'addr': '@iana.org',
    'id_num': '8',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'VALID',
    'comment': '',
    'addr': 'test@nominet.org.uk',
    'id_num': '9',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'VALID',
    'comment': '',
    'addr': 'test@about.museum',
    'id_num': '10',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'VALID',
    'comment': '',
    'addr': 'a@iana.org',
    'id_num': '11',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'DNSWARN_NO_RECORD',
    'comment': '',
    'addr': 'test@e.com',
    'id_num': '12',
    'codes': [],
    'cat': 'ISEMAIL_DNSWARN'
}, {
    'diag': 'DNSWARN_NO_RECORD',
    'comment': '',
    'addr': 'test@iana.a',
    'id_num': '13',
    'codes': [],
    'cat': 'ISEMAIL_DNSWARN'
}, {
    'diag': 'VALID',
    'comment': '',
    'addr': 'test.test@iana.org',
    'id_num': '14',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'ERR_DOT_START',
    'comment': '',
    'addr': '.test@iana.org',
    'id_num': '15',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_DOT_END',
    'comment': '',
    'addr': 'test.@iana.org',
    'id_num': '16',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_CONSECUTIVE_DOTS',
    'comment': '',
    'addr': 'test..iana.org',
    'id_num': '17',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_NO_DOMAIN_PART',
    'comment': '',
    'addr': 'test_exa-mple.com',
    'id_num': '18',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'VALID',
    'comment': '',
    'addr': '!#$%&`{{42}}+/=?^`{{123}}|{{125}}~@iana.org',
    'id_num': '19',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': 'test{{92}}@test@iana.org',
    'id_num': '20',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'VALID',
    'comment': '',
    'addr': '123@iana.org',
    'id_num': '21',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'VALID',
    'comment': '',
    'addr': 'test@123.com',
    'id_num': '22',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'RFC5321_TLD_NUMERIC',
    'comment': '',
    'addr': 'test@iana.123',
    'id_num': '23',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'RFC5321_TLD_NUMERIC',
    'comment': '',
    'addr': 'test@255.255.255.255',
    'id_num': '24',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'VALID',
    'comment': '',
    'addr': 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklm@iana.org',
    'id_num': '25',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'RFC5322_LOCAL_TOO_LONG',
    'comment': '',
    'addr': 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklmn@iana.org',
    'id_num': '26',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'DNSWARN_NO_RECORD',
    'comment': '',
    'addr': 'test@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.com',
    'id_num': '27',
    'codes': [],
    'cat': 'ISEMAIL_DNSWARN'
}, {
    'diag': 'RFC5322_LABEL_TOO_LONG',
    'comment': '',
    'addr': 'test@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklm.com',
    'id_num': '28',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'VALID',
    'comment': '',
    'addr': 'test@mason-dixon.com',
    'id_num': '29',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'ERR_DOMAIN_HYPHEN_START',
    'comment': '',
    'addr': 'test@-iana.org',
    'id_num': '30',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_DOMAIN_HYPHEN_END',
    'comment': '',
    'addr': 'test@iana-.com',
    'id_num': '31',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'VALID',
    'comment': 'c--n.com currently has an MX-record (May 2011)',
    'addr': 'test@c--n.com',
    'id_num': '32',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'DNSWARN_NO_RECORD',
    'comment': '',
    'addr': 'test@iana.co-uk',
    'id_num': '33',
    'codes': [],
    'cat': 'ISEMAIL_DNSWARN'
}, {
    'diag': 'ERR_DOT_START',
    'comment': '',
    'addr': 'test@.iana.org',
    'id_num': '34',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_DOT_END',
    'comment': '',
    'addr': 'test@iana.org.',
    'id_num': '35',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_CONSECUTIVE_DOTS',
    'comment': '',
    'addr': 'test@iana..com',
    'id_num': '36',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'DNSWARN_NO_RECORD',
    'comment': '',
    'addr': 'a@a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z.a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z.a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z.a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z.a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v',
    'id_num': '37',
    'codes': [],
    'cat': 'ISEMAIL_DNSWARN'
}, {
    'diag': 'DNSWARN_NO_RECORD',
    'comment': '',
    'addr': 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklm@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghi',
    'id_num': '38',
    'codes': [],
    'cat': 'ISEMAIL_DNSWARN'
}, {
    'diag': 'RFC5322_TOO_LONG',
    'comment': '',
    'addr': 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklm@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghij',
    'id_num': '39',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_TOO_LONG',
    'comment': '',
    'addr': 'a@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefg.hij',
    'id_num': '40',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_DOMAIN_TOO_LONG',
    'comment': '',
    'addr': 'a@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefg.hijk',
    'id_num': '41',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5321_QUOTED_STRING',
    'comment': '',
    'addr': '"test"@iana.org',
    'id_num': '42',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'RFC5321_QUOTED_STRING',
    'comment': '',
    'addr': '""@iana.org',
    'id_num': '43',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': '"""@iana.org',
    'id_num': '44',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'RFC5321_QUOTED_STRING',
    'comment': '',
    'addr': '"{{92}}a"@iana.org',
    'id_num': '45',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'RFC5321_QUOTED_STRING',
    'comment': '',
    'addr': '"{{92}}""@iana.org',
    'id_num': '46',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'ERR_UNCLOSED_QUOTED_STR',
    'comment': '',
    'addr': '"{{92}}"@iana.org',
    'id_num': '47',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'RFC5321_QUOTED_STRING',
    'comment': '',
    'addr': '"{{92}}{{92}}"@iana.org',
    'id_num': '48',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': 'test"@iana.org',
    'id_num': '49',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_UNCLOSED_QUOTED_STR',
    'comment': '',
    'addr': '"test@iana.org',
    'id_num': '50',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_ATEXT_AFTER_QS',
    'comment': '',
    'addr': '"test"test@iana.org',
    'id_num': '51',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': 'test"text"@iana.org',
    'id_num': '52',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': '"test""test"@iana.org',
    'id_num': '53',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'DEPREC_LOCAL_PART',
    'comment': '',
    'addr': '"test"."test"@iana.org',
    'id_num': '54',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'RFC5321_QUOTED_STRING',
    'comment': '',
    'addr': '"test{{92}}{{32}}test"@iana.org',
    'id_num': '55',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'DEPREC_LOCAL_PART',
    'comment': '',
    'addr': '"test".test@iana.org',
    'id_num': '56',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'ERR_EXPECTING_QTEXT',
    'comment': '',
    'addr': '"test{{9216}}"@iana.org',
    'id_num': '57',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'DEPREC_QP',
    'comment': '',
    'addr': '"test{{92}}{{9216}}"@iana.org',
    'id_num': '58',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'RFC5322_LOCAL_TOO_LONG',
    'comment': 'Quotes are still part of the length restriction',
    'addr': '"abcdefghijklmnopqrstuvwxyz{{32}}abcdefghijklmnopqrstuvwxyz{{32}}abcdefghj"@iana.org',
    'id_num': '59',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_LOCAL_TOO_LONG',
    'comment': 'Quoted pair is still part of the length restriction',
    'addr': '"abcdefghijklmnopqrstuvwxyz{{32}}abcdefghijklmnopqrstuvwxyz{{32}}abcdefg{{92}}h"@iana.org',
    'id_num': '60',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5321_ADDRESS_LITERAL',
    'comment': '',
    'addr': 'test@[255.255.255.255]',
    'id_num': '61',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': 'test@a[255.255.255.255]',
    'id_num': '62',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'RFC5322_DOMAIN_LITERAL',
    'comment': '',
    'addr': 'test@[255.255.255]',
    'id_num': '63',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_DOMAIN_LITERAL',
    'comment': '',
    'addr': 'test@[255.255.255.255.255]',
    'id_num': '64',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_DOMAIN_LITERAL',
    'comment': '',
    'addr': 'test@[255.255.255.256]',
    'id_num': '65',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_DOMAIN_LITERAL',
    'comment': '',
    'addr': 'test@[1111:2222:3333:4444:5555:6666:7777:8888]',
    'id_num': '66',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_IPV6_GRP_COUNT',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555:6666:7777]',
    'id_num': '67',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5321_ADDRESS_LITERAL',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555:6666:7777:8888]',
    'id_num': '68',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'RFC5322_IPV6_GRP_COUNT',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555:6666:7777:8888:9999]',
    'id_num': '69',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_IPV6_BAD_CHAR',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555:6666:7777:888G]',
    'id_num': '70',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5321_IPV6_DEPRECATED',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555:6666::8888]',
    'id_num': '71',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'RFC5321_ADDRESS_LITERAL',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555::8888]',
    'id_num': '72',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'RFC5322_IPV6_MAX_GRPS',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555:6666::7777:8888]',
    'id_num': '73',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_IPV6_COLON_STRT',
    'comment': '',
    'addr': 'test@[IPv6::3333:4444:5555:6666:7777:8888]',
    'id_num': '74',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5321_ADDRESS_LITERAL',
    'comment': '',
    'addr': 'test@[IPv6:::3333:4444:5555:6666:7777:8888]',
    'id_num': '75',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'RFC5322_IPV6_2X2X_COLON',
    'comment': '',
    'addr': 'test@[IPv6:1111::4444:5555::8888]',
    'id_num': '76',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5321_ADDRESS_LITERAL',
    'comment': '',
    'addr': 'test@[IPv6:::]',
    'id_num': '77',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'RFC5322_IPV6_GRP_COUNT',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555:255.255.255.255]',
    'id_num': '78',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5321_ADDRESS_LITERAL',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555:6666:255.255.255.255]',
    'id_num': '79',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'RFC5322_IPV6_GRP_COUNT',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555:6666:7777:255.255.255.255]',
    'id_num': '80',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5321_ADDRESS_LITERAL',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444::255.255.255.255]',
    'id_num': '81',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'RFC5322_IPV6_MAX_GRPS',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:5555:6666::255.255.255.255]',
    'id_num': '82',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_IPV6_2X2X_COLON',
    'comment': '',
    'addr': 'test@[IPv6:1111:2222:3333:4444:::255.255.255.255]',
    'id_num': '83',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_IPV6_COLON_STRT',
    'comment': '',
    'addr': 'test@[IPv6::255.255.255.255]',
    'id_num': '84',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'DEPREC_CFWS_NEAR_AT',
    'comment': '',
    'addr': '{{32}}test{{32}}@iana.org',
    'id_num': '85',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'DEPREC_CFWS_NEAR_AT',
    'comment': '',
    'addr': 'test@{{32}}iana{{32}}.com',
    'id_num': '86',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'DEPREC_FWS',
    'comment': '',
    'addr': 'test{{32}}.{{32}}test@iana.org',
    'id_num': '87',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'CFWS_FWS',
    'comment': 'FWS',
    'addr': '{{9229}}{{9226}}{{32}}test@iana.org',
    'id_num': '88',
    'codes': [],
    'cat': 'ISEMAIL_CFWS'
}, {
    'diag': 'DEPREC_FWS',
    'comment': 'FWS with one line composed entirely of WSP -- only allowed as obsolete FWS (someone might allow only non-obsolete FWS)',
    'addr': '{{9229}}{{9226}}{{32}}{{9229}}{{9226}}{{32}}test@iana.org',
    'id_num': '89',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'CFWS_COMMENT',
    'comment': '',
    'addr': '(comment)test@iana.org',
    'id_num': '90',
    'codes': [],
    'cat': 'ISEMAIL_CFWS'
}, {
    'diag': 'ERR_UNCLOSED_COMMENT',
    'comment': '',
    'addr': '((comment)test@iana.org',
    'id_num': '91',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'CFWS_COMMENT',
    'comment': '',
    'addr': '(comment(comment))test@iana.org',
    'id_num': '92',
    'codes': [],
    'cat': 'ISEMAIL_CFWS'
}, {
    'diag': 'DEPREC_CFWS_NEAR_AT',
    'comment': '',
    'addr': 'test@(comment)iana.org',
    'id_num': '93',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'ERR_ATEXT_AFTER_CFWS',
    'comment': '',
    'addr': 'test(comment)test@iana.org',
    'id_num': '94',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'DEPREC_CFWS_NEAR_AT',
    'comment': '',
    'addr': 'test@(comment)[255.255.255.255]',
    'id_num': '95',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'CFWS_COMMENT',
    'comment': '',
    'addr': '(comment)abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklm@iana.org',
    'id_num': '96',
    'codes': [],
    'cat': 'ISEMAIL_CFWS'
}, {
    'diag': 'DEPREC_CFWS_NEAR_AT',
    'comment': '',
    'addr': 'test@(comment)abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.com',
    'id_num': '97',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'CFWS_COMMENT',
    'comment': '',
    'addr': '(comment)test@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghik.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghik.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijk.abcdefghijklmnopqrstuvwxyzabcdefghijk.abcdefghijklmnopqrstu',
    'id_num': '98',
    'codes': [],
    'cat': 'ISEMAIL_CFWS'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': 'test@iana.org{{9226}}',
    'id_num': '99',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'VALID',
    'comment': "A valid IDN from ICANN's ",
    'addr': 'test@xn--hxajbheg2az3al.xn--jxalpdlp',
    'id_num': '100',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'VALID',
    'comment': 'RFC 3490: "unless the\n   email standards are revised to invite the use of IDNA for local\n   parts, a domain label that holds the local part of an email address\n   SHOULD NOT begin with the ACE prefix, and even if it does, it is to\n   be interpreted literally as a local part that happens to begin with\n   the ACE prefix"',
    'addr': 'xn--test@iana.org',
    'id_num': '101',
    'codes': [],
    'cat': 'ISEMAIL_VALID_CATEGORY'
}, {
    'diag': 'ERR_DOMAIN_HYPHEN_END',
    'comment': '',
    'addr': 'test@iana.org-',
    'id_num': '102',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_UNCLOSED_QUOTED_STR',
    'comment': '',
    'addr': '"test@iana.org',
    'id_num': '103',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_UNCLOSED_COMMENT',
    'comment': '',
    'addr': '(test@iana.org',
    'id_num': '104',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_UNCLOSED_COMMENT',
    'comment': '',
    'addr': 'test@(iana.org',
    'id_num': '105',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_UNCLOSED_DOM_LIT',
    'comment': '',
    'addr': 'test@[1.2.3.4',
    'id_num': '106',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_UNCLOSED_QUOTED_STR',
    'comment': '',
    'addr': '"test{{92}}"@iana.org',
    'id_num': '107',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_UNCLOSED_COMMENT',
    'comment': '',
    'addr': '(comment{{92}})test@iana.org',
    'id_num': '108',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_UNCLOSED_COMMENT',
    'comment': '',
    'addr': 'test@iana.org(comment{{92}})',
    'id_num': '109',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_BACKSLASH_END',
    'comment': '',
    'addr': 'test@iana.org(comment{{92}}',
    'id_num': '110',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'RFC5322_DOMAIN_LITERAL',
    'comment': '',
    'addr': 'test@[RFC-5322-domain-literal]',
    'id_num': '112',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'ERR_ATEXT_AFTER_DOMLIT',
    'comment': '',
    'addr': 'test@[RFC-5322]-domain-literal]',
    'id_num': '113',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_EXPECTING_DTEXT',
    'comment': '',
    'addr': 'test@[RFC-5322-[domain-literal]',
    'id_num': '114',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'RFC5322_DOM_LIT_OBS_DTEXT',
    'comment': 'obs-dtext ',
    'addr': 'test@[RFC-5322-{{92}}{{9223}}-domain-literal]',
    'id_num': '115',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_DOM_LIT_OBS_DTEXT',
    'comment': '',
    'addr': 'test@[RFC-5322-{{92}}{{9225}}-domain-literal]',
    'id_num': '116',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_DOM_LIT_OBS_DTEXT',
    'comment': '',
    'addr': 'test@[RFC-5322-{{92}}]-domain-literal]',
    'id_num': '117',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'ERR_UNCLOSED_DOM_LIT',
    'comment': '',
    'addr': 'test@[RFC-5322-domain-literal{{92}}]',
    'id_num': '118',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_BACKSLASH_END',
    'comment': '',
    'addr': 'test@[RFC-5322-domain-literal{{92}}',
    'id_num': '119',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'RFC5322_DOMAIN_LITERAL',
    'comment': 'Spaces are FWS in a domain literal',
    'addr': 'test@[RFC{{32}}5322{{32}}domain{{32}}literal]',
    'id_num': '120',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'RFC5322_DOMAIN_LITERAL',
    'comment': '',
    'addr': 'test@[RFC-5322-domain-literal]{{32}}(comment)',
    'id_num': '121',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': '{{127}}@iana.org',
    'id_num': '122',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': 'test@{{127}}.org',
    'id_num': '123',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'DEPREC_QTEXT',
    'comment': '',
    'addr': '"{{127}}"@iana.org',
    'id_num': '124',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'DEPREC_QP',
    'comment': '',
    'addr': '"{{92}}{{127}}"@iana.org',
    'id_num': '125',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'DEPREC_CTEXT',
    'comment': '',
    'addr': '({{127}})test@iana.org',
    'id_num': '126',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'ERR_CR_NO_LF',
    'comment': 'No LF after the CR',
    'addr': 'test@iana.org{{9229}}',
    'id_num': '127',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_CR_NO_LF',
    'comment': 'No LF after the CR',
    'addr': '{{9229}}test@iana.org',
    'id_num': '128',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_CR_NO_LF',
    'comment': 'No LF after the CR',
    'addr': '"{{9229}}test"@iana.org',
    'id_num': '129',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_CR_NO_LF',
    'comment': 'No LF after the CR',
    'addr': '({{9229}})test@iana.org',
    'id_num': '130',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_CR_NO_LF',
    'comment': 'No LF after the CR',
    'addr': 'test@iana.org({{9229}})',
    'id_num': '131',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': '{{9226}}test@iana.org',
    'id_num': '132',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_EXPECTING_QTEXT',
    'comment': '',
    'addr': '"{{9226}}"@iana.org',
    'id_num': '133',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'DEPREC_QP',
    'comment': '',
    'addr': '"{{92}}{{9226}}"@iana.org',
    'id_num': '134',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'ERR_EXPECTING_CTEXT',
    'comment': '',
    'addr': '({{9226}})test@iana.org',
    'id_num': '135',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': '{{9223}}@iana.org',
    'id_num': '136',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_EXPECTING_ATEXT',
    'comment': '',
    'addr': 'test@{{9223}}.org',
    'id_num': '137',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'DEPREC_QTEXT',
    'comment': '',
    'addr': '"{{9223}}"@iana.org',
    'id_num': '138',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'DEPREC_QP',
    'comment': '',
    'addr': '"{{92}}{{9223}}"@iana.org',
    'id_num': '139',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'DEPREC_CTEXT',
    'comment': '',
    'addr': '({{9223}})test@iana.org',
    'id_num': '140',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'ERR_FWS_CRLF_END',
    'comment': 'Not FWS because no actual white space',
    'addr': '{{9229}}{{9226}}test@iana.org',
    'id_num': '141',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_FWS_CRLF_END',
    'comment': 'Not obs-FWS because there must be white space on each "fold"',
    'addr': '{{9229}}{{9226}}{{32}}{{9229}}{{9226}}test@iana.org',
    'id_num': '142',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_FWS_CRLF_END',
    'comment': 'Not FWS because no white space after the fold',
    'addr': '{{32}}{{9229}}{{9226}}test@iana.org',
    'id_num': '143',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'CFWS_FWS',
    'comment': 'FWS',
    'addr': '{{32}}{{9229}}{{9226}}{{32}}test@iana.org',
    'id_num': '144',
    'codes': [],
    'cat': 'ISEMAIL_CFWS'
}, {
    'diag': 'ERR_FWS_CRLF_END',
    'comment': 'Not FWS because no white space after the second fold',
    'addr': '{{32}}{{9229}}{{9226}}{{32}}{{9229}}{{9226}}test@iana.org',
    'id_num': '145',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_FWS_CRLF_X2',
    'comment': 'Not FWS because no white space after either fold',
    'addr': '{{32}}{{9229}}{{9226}}{{9229}}{{9226}}test@iana.org',
    'id_num': '146',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_FWS_CRLF_X2',
    'comment': 'Not FWS because no white space after the first fold',
    'addr': '{{32}}{{9229}}{{9226}}{{9229}}{{9226}}{{32}}test@iana.org',
    'id_num': '147',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'CFWS_FWS',
    'comment': 'FWS',
    'addr': 'test@iana.org{{9229}}{{9226}}{{32}}',
    'id_num': '148',
    'codes': [],
    'cat': 'ISEMAIL_CFWS'
}, {
    'diag': 'DEPREC_FWS',
    'comment': 'FWS with one line composed entirely of WSP -- only allowed as obsolete FWS (someone might allow only non-obsolete FWS)',
    'addr': 'test@iana.org{{9229}}{{9226}}{{32}}{{9229}}{{9226}}{{32}}',
    'id_num': '149',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'ERR_FWS_CRLF_END',
    'comment': 'Not FWS because no actual white space',
    'addr': 'test@iana.org{{9229}}{{9226}}',
    'id_num': '150',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_FWS_CRLF_END',
    'comment': 'Not obs-FWS because there must be white space on each "fold"',
    'addr': 'test@iana.org{{9229}}{{9226}}{{32}}{{9229}}{{9226}}',
    'id_num': '151',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_FWS_CRLF_END',
    'comment': 'Not FWS because no white space after the fold',
    'addr': 'test@iana.org{{32}}{{9229}}{{9226}}',
    'id_num': '152',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'CFWS_FWS',
    'comment': 'FWS',
    'addr': 'test@iana.org{{32}}{{9229}}{{9226}}{{32}}',
    'id_num': '153',
    'codes': [],
    'cat': 'ISEMAIL_CFWS'
}, {
    'diag': 'ERR_FWS_CRLF_END',
    'comment': 'Not FWS because no white space after the second fold',
    'addr': 'test@iana.org{{32}}{{9229}}{{9226}}{{32}}{{9229}}{{9226}}',
    'id_num': '154',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_FWS_CRLF_X2',
    'comment': 'Not FWS because no white space after either fold',
    'addr': 'test@iana.org{{32}}{{9229}}{{9226}}{{9229}}{{9226}}',
    'id_num': '155',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'ERR_FWS_CRLF_X2',
    'comment': 'Not FWS because no white space after the first fold',
    'addr': 'test@iana.org{{32}}{{9229}}{{9226}}{{9229}}{{9226}}{{32}}',
    'id_num': '156',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'CFWS_FWS',
    'comment': '',
    'addr': '{{32}}test@iana.org',
    'id_num': '157',
    'codes': [],
    'cat': 'ISEMAIL_CFWS'
}, {
    'diag': 'CFWS_FWS',
    'comment': '',
    'addr': 'test@iana.org{{32}}',
    'id_num': '158',
    'codes': [],
    'cat': 'ISEMAIL_CFWS'
}, {
    'diag': 'RFC5322_IPV6_COLON_END',
    'comment': '',
    'addr': 'test@[IPv6:1::2:]',
    'id_num': '159',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'ERR_EXPECTING_QPAIR',
    'comment': '',
    'addr': '"test{{92}}{{169}}"@iana.org',
    'id_num': '160',
    'codes': [],
    'cat': 'ISEMAIL_ERR'
}, {
    'diag': 'RFC5322_DOMAIN',
    'comment': '',
    'addr': 'test@iana/icann.org',
    'id_num': '161',
    'codes': [],
    'cat': 'ISEMAIL_RFC5322'
}, {
    'diag': 'DEPREC_COMMENT',
    'comment': '',
    'addr': 'test.(comment)test@iana.org',
    'id_num': '165',
    'codes': [],
    'cat': 'ISEMAIL_DEPREC'
}, {
    'diag': 'RFC5321_TLD',
    'comment': '',
    'addr': 'test@org',
    'id_num': '166',
    'codes': [],
    'cat': 'ISEMAIL_RFC5321'
}, {
    'diag': 'DNSWARN_NO_MX_RECORD',
    'comment': 'test.com has an A-record but not an MX-record',
    'addr': 'test@test.com',
    'id_num': '167',
    'codes': [],
    'cat': 'ISEMAIL_DNSWARN'
}, {
    'diag': 'DNSWARN_NO_RECORD',
    'comment': 'nic.no currently has no MX-records or A-records (Feb 2011). If you are seeing an A-record for nic.io then try setting your DNS server to 8.8.8.8 (the Google DNS server) - your DNS server may be faking an A-record (OpenDNS does this, for instance).',
    'addr': 'test@nic.no',
    'id_num': '168',
    'codes': [],
    'cat': 'ISEMAIL_DNSWARN'
}]


# ***********************************************************************
#  CODE TO CREATE LIST
# ***********************************************************************

"""

import unittest
import xml.etree.ElementTree as ET
from parse_objects import make_char_str, EmailParser

TEST_DATA = ET.parse('tests.xml').getroot()
# TEST_DATA2 = ET.parse('tests-original.xml').getroot()

DIGIT = '1234567890'
ALPHA = make_char_str((65, 90), (97, 122))
DQUOTE = '"'
TTEXT = make_char_str(ALPHA, DIGIT, DQUOTE, "!#$%&'+-/=?^_`|~.@[]():")

class TestMakeTestDict(unittest.TestCase):

    def test_make_data_dict(self):
        tmp_info = ET.parse('tests.xml').getroot()
        tmp_items = []

        for item in tmp_info.findall('test'):
            id_num = item.get('id')

            tmp_addr = []
            addr_in = item.find('address').text

            if addr_in is None:
                addr = ''
            else:
                for c in addr_in:
                    if c in TTEXT:
                        tmp_addr.append(c)
                    else:
                        tmp_addr.append('{{%s}}' % ord(c))
                addr = ''.join(tmp_addr)

            category = item.find('category').text
            diag = item.find('diagnosis').text
            comment = item.find('comment')
            if comment is None:
                comment = ''
            else:
                comment = comment.text

            tmp_dict = dict(
                id_num=id_num,
                addr=addr,
                cat=category,
                diag=diag,
                codes=[],
                comment=comment)

            tmp_items.append(tmp_dict)

        print(repr(tmp_items))

            # print('id: [%r] : %r   | cat=%r, diag=%r, comment=%s' % (id_num, addr, category, diag, comment))

            # print(tmp_key, ' : ', tmp_value)

"""