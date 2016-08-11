import json

TEST_DATA = """
{
  "tests": {
    "-version": "3.05",
    "description": {
      "p": [
        { "strong": "New test set" },
        "This test set is designed to replace and extend the coverage of the original set but with fewer tests.",
        "Thanks to Michael Rushton (michael@squiloople.com) for starting this work and contributing tests 1-100"
      ]
    },
    "test": [
      {
        "-id": "1",
        "address": "",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_NODOMAIN",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "2",
        "address": "test",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_NODOMAIN",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "3",
        "address": "@",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_NOLOCALPART",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "4",
        "address": "test@",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_NODOMAIN",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "5",
        "address": "test@io",
        "comment": "io. currently has an MX-record (Feb 2011). Some DNS setups seem to find it, some don't. If you don't see the MX for io. then try setting your DNS server to 8.8.8.8 (the Google DNS server)",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "6",
        "address": "@io",
        "comment": "io. currently has an MX-record (Feb 2011)",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_NOLOCALPART",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "7",
        "address": "@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_NOLOCALPART",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "8",
        "address": "test@iana.org",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "9",
        "address": "test@nominet.org.uk",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "10",
        "address": "test@about.museum",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "11",
        "address": "a@iana.org",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "12",
        "address": "test@e.com",
        "category": "ISEMAIL_DNSWARN",
        "diagnosis": "ISEMAIL_DNSWARN_NO_RECORD",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "13",
        "address": "test@iana.a",
        "category": "ISEMAIL_DNSWARN",
        "diagnosis": "ISEMAIL_DNSWARN_NO_RECORD",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "14",
        "address": "test.test@iana.org",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "15",
        "address": ".test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_DOT_START",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "16",
        "address": "test.@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_DOT_END",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "17",
        "address": "test..iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_CONSECUTIVEDOTS",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "18",
        "address": "test_exa-mple.com",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_NODOMAIN",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "19",
        "address": "!#$%&`*+/=?^`{|}~@iana.org",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "20",
        "address": "test\\@test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "21",
        "address": "123@iana.org",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "22",
        "address": "test@123.com",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "23",
        "address": "test@iana.123",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_TLDNUMERIC",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "24",
        "address": "test@255.255.255.255",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_TLDNUMERIC",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "25",
        "address": "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklm@iana.org",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "26",
        "address": "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklmn@iana.org",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_LOCAL_TOOLONG",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "27",
        "address": "test@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.com",
        "category": "ISEMAIL_DNSWARN",
        "diagnosis": "ISEMAIL_DNSWARN_NO_RECORD",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "28",
        "address": "test@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklm.com",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_LABEL_TOOLONG",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "29",
        "address": "test@mason-dixon.com",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "30",
        "address": "test@-iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_DOMAINHYPHENSTART",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "31",
        "address": "test@iana-.com",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_DOMAINHYPHENEND",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "32",
        "address": "test@c--n.com",
        "comment": "c--n.com currently has an MX-record (May 2011)",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "33",
        "address": "test@iana.co-uk",
        "category": "ISEMAIL_DNSWARN",
        "diagnosis": "ISEMAIL_DNSWARN_NO_RECORD",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "34",
        "address": "test@.iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_DOT_START",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "35",
        "address": "test@iana.org.",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_DOT_END",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "36",
        "address": "test@iana..com",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_CONSECUTIVEDOTS",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "37",
        "address": "a@a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z.a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z.a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z.a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z.a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v",
        "category": "ISEMAIL_DNSWARN",
        "diagnosis": "ISEMAIL_DNSWARN_NO_RECORD",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "38",
        "address": "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklm@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghi",
        "category": "ISEMAIL_DNSWARN",
        "diagnosis": "ISEMAIL_DNSWARN_NO_RECORD",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "39",
        "address": "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklm@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghij",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_TOOLONG",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "40",
        "address": "a@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefg.hij",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_TOOLONG",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "41",
        "address": "a@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefg.hijk",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMAIN_TOOLONG",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "42",
        "address": "\"test\"@iana.org",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_QUOTEDSTRING",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "43",
        "address": "\"\"@iana.org",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_QUOTEDSTRING",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "44",
        "address": "\"\"\"@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "45",
        "address": "\"\\a\"@iana.org",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_QUOTEDSTRING",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "46",
        "address": "\"\\\"\"@iana.org",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_QUOTEDSTRING",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "47",
        "address": "\"\\\"@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDQUOTEDSTR",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "48",
        "address": "\"\\\\\"@iana.org",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_QUOTEDSTRING",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "49",
        "address": "test\"@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "50",
        "address": "\"test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDQUOTEDSTR",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "51",
        "address": "\"test\"test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_ATEXT_AFTER_QS",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "52",
        "address": "test\"text\"@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "53",
        "address": "\"test\"\"test\"@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "54",
        "address": "\"test\".\"test\"@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_LOCALPART",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "55",
        "address": "\"test\\ test\"@iana.org",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_QUOTEDSTRING",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "56",
        "address": "\"test\".test@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_LOCALPART",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "57",
        "address": "\"test␀\"@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_QTEXT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "58",
        "address": "\"test\\␀\"@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_QP",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "59",
        "address": "\"abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefghj\"@iana.org",
        "comment": "Quotes are still part of the length restriction",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_LOCAL_TOOLONG",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "60",
        "address": "\"abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz abcdefg\\h\"@iana.org",
        "comment": "Quoted pair is still part of the length restriction",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_LOCAL_TOOLONG",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "61",
        "address": "test@[255.255.255.255]",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_ADDRESSLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "62",
        "address": "test@a[255.255.255.255]",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "63",
        "address": "test@[255.255.255]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMAINLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "64",
        "address": "test@[255.255.255.255.255]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMAINLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "65",
        "address": "test@[255.255.255.256]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMAINLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "66",
        "address": "test@[1111:2222:3333:4444:5555:6666:7777:8888]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMAINLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "67",
        "address": "test@[IPv6:1111:2222:3333:4444:5555:6666:7777]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_GRPCOUNT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "68",
        "address": "test@[IPv6:1111:2222:3333:4444:5555:6666:7777:8888]",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_ADDRESSLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "69",
        "address": "test@[IPv6:1111:2222:3333:4444:5555:6666:7777:8888:9999]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_GRPCOUNT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "70",
        "address": "test@[IPv6:1111:2222:3333:4444:5555:6666:7777:888G]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_BADCHAR",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "71",
        "address": "test@[IPv6:1111:2222:3333:4444:5555:6666::8888]",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_RFC5321_IPV6DEPRECATED",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "72",
        "address": "test@[IPv6:1111:2222:3333:4444:5555::8888]",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_ADDRESSLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "73",
        "address": "test@[IPv6:1111:2222:3333:4444:5555:6666::7777:8888]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_MAXGRPS",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "74",
        "address": "test@[IPv6::3333:4444:5555:6666:7777:8888]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_COLONSTRT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "75",
        "address": "test@[IPv6:::3333:4444:5555:6666:7777:8888]",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_ADDRESSLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "76",
        "address": "test@[IPv6:1111::4444:5555::8888]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_2X2XCOLON",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "77",
        "address": "test@[IPv6:::]",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_ADDRESSLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "78",
        "address": "test@[IPv6:1111:2222:3333:4444:5555:255.255.255.255]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_GRPCOUNT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "79",
        "address": "test@[IPv6:1111:2222:3333:4444:5555:6666:255.255.255.255]",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_ADDRESSLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "80",
        "address": "test@[IPv6:1111:2222:3333:4444:5555:6666:7777:255.255.255.255]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_GRPCOUNT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "81",
        "address": "test@[IPv6:1111:2222:3333:4444::255.255.255.255]",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_ADDRESSLITERAL",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "82",
        "address": "test@[IPv6:1111:2222:3333:4444:5555:6666::255.255.255.255]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_MAXGRPS",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "83",
        "address": "test@[IPv6:1111:2222:3333:4444:::255.255.255.255]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_2X2XCOLON",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "84",
        "address": "test@[IPv6::255.255.255.255]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_COLONSTRT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "85",
        "address": " test @iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_CFWS_NEAR_AT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "86",
        "address": "test@ iana .com",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_CFWS_NEAR_AT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "87",
        "address": "test . test@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_FWS",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "88",
        "address": "␍␊ test@iana.org",
        "comment": "FWS",
        "category": "ISEMAIL_CFWS",
        "diagnosis": "ISEMAIL_CFWS_FWS",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "89",
        "address": "␍␊ ␍␊ test@iana.org",
        "comment": "FWS with one line composed entirely of WSP -- only allowed as obsolete FWS (someone might allow only non-obsolete FWS)",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_FWS",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "90",
        "address": "(comment)test@iana.org",
        "category": "ISEMAIL_CFWS",
        "diagnosis": "ISEMAIL_CFWS_COMMENT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "91",
        "address": "((comment)test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDCOMMENT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "92",
        "address": "(comment(comment))test@iana.org",
        "category": "ISEMAIL_CFWS",
        "diagnosis": "ISEMAIL_CFWS_COMMENT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "93",
        "address": "test@(comment)iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_CFWS_NEAR_AT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "94",
        "address": "test(comment)test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_ATEXT_AFTER_CFWS",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "95",
        "address": "test@(comment)[255.255.255.255]",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_CFWS_NEAR_AT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "96",
        "address": "(comment)abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghiklm@iana.org",
        "category": "ISEMAIL_CFWS",
        "diagnosis": "ISEMAIL_CFWS_COMMENT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "97",
        "address": "test@(comment)abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghikl.com",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_CFWS_NEAR_AT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "98",
        "address": "(comment)test@abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghik.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghik.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijk.abcdefghijklmnopqrstuvwxyzabcdefghijk.abcdefghijklmnopqrstu",
        "category": "ISEMAIL_CFWS",
        "diagnosis": "ISEMAIL_CFWS_COMMENT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "99",
        "address": "test@iana.org␊",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "100",
        "address": "test@xn--hxajbheg2az3al.xn--jxalpdlp",
        "comment": {
          "#text": "A valid IDN from ICANN's ",
          "a": {
            "-href": "http://idn.icann.org/#The_example.test_names",
            "#text": "IDN TLD evaluation gateway"
          }
        },
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "101",
        "address": "xn--test@iana.org",
        "comment": "RFC 3490: \"unless the
   email standards are revised to invite the use of IDNA for local
   parts, a domain label that holds the local part of an email address
   SHOULD NOT begin with the ACE prefix, and even if it does, it is to
   be interpreted literally as a local part that happens to begin with
   the ACE prefix\"",
        "category": "ISEMAIL_VALID_CATEGORY",
        "diagnosis": "ISEMAIL_VALID",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "102",
        "address": "test@iana.org-",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_DOMAINHYPHENEND",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "103",
        "address": "\"test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDQUOTEDSTR",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "104",
        "address": "(test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDCOMMENT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "105",
        "address": "test@(iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDCOMMENT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "106",
        "address": "test@[1.2.3.4",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDDOMLIT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "107",
        "address": "\"test\\\"@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDQUOTEDSTR",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "108",
        "address": "(comment\\)test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDCOMMENT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "109",
        "address": "test@iana.org(comment\\)",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDCOMMENT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "110",
        "address": "test@iana.org(comment\\",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_BACKSLASHEND",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "112",
        "address": "test@[RFC-5322-domain-literal]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMAINLITERAL",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "113",
        "address": "test@[RFC-5322]-domain-literal]",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_ATEXT_AFTER_DOMLIT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "114",
        "address": "test@[RFC-5322-[domain-literal]",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_DTEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "115",
        "address": "test@[RFC-5322-\\␇-domain-literal]",
        "comment": {
          "#text": [
            "obs-dtext ",
            " obs-qp"
          ],
          "strong": "and"
        },
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMLIT_OBSDTEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "116",
        "address": "test@[RFC-5322-\\␉-domain-literal]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMLIT_OBSDTEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "117",
        "address": "test@[RFC-5322-\\]-domain-literal]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMLIT_OBSDTEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "118",
        "address": "test@[RFC-5322-domain-literal\\]",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_UNCLOSEDDOMLIT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "119",
        "address": "test@[RFC-5322-domain-literal\\",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_BACKSLASHEND",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "120",
        "address": "test@[RFC 5322 domain literal]",
        "comment": "Spaces are FWS in a domain literal",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMAINLITERAL",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "121",
        "address": "test@[RFC-5322-domain-literal] (comment)",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMAINLITERAL",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "122",
        "address": "@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "123",
        "address": "test@.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "124",
        "address": "\"\"@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_QTEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "125",
        "address": "\"\\\"@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_QP",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "126",
        "address": "()test@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_CTEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "127",
        "address": "test@iana.org␍",
        "comment": "No LF after the CR",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_CR_NO_LF",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "128",
        "address": "␍test@iana.org",
        "comment": "No LF after the CR",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_CR_NO_LF",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "129",
        "address": "\"␍test\"@iana.org",
        "comment": "No LF after the CR",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_CR_NO_LF",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "130",
        "address": "(␍)test@iana.org",
        "comment": "No LF after the CR",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_CR_NO_LF",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "131",
        "address": "test@iana.org(␍)",
        "comment": "No LF after the CR",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_CR_NO_LF",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "132",
        "address": "␊test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Michael Rushton",
        "sourcelink": "http://squiloople.com/tag/email/"
      },
      {
        "-id": "133",
        "address": "\"␊\"@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_QTEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "134",
        "address": "\"\\␊\"@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_QP",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "135",
        "address": "(␊)test@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_CTEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "136",
        "address": "␇@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "137",
        "address": "test@␇.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_ATEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "138",
        "address": "\"␇\"@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_QTEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "139",
        "address": "\"\\␇\"@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_QP",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "140",
        "address": "(␇)test@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_CTEXT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "141",
        "address": "␍␊test@iana.org",
        "comment": "Not FWS because no actual white space",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_END",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "142",
        "address": "␍␊ ␍␊test@iana.org",
        "comment": "Not obs-FWS because there must be white space on each \"fold\"",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_END",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "143",
        "address": " ␍␊test@iana.org",
        "comment": "Not FWS because no white space after the fold",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_END",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "144",
        "address": " ␍␊ test@iana.org",
        "comment": "FWS",
        "category": "ISEMAIL_CFWS",
        "diagnosis": "ISEMAIL_CFWS_FWS",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "145",
        "address": " ␍␊ ␍␊test@iana.org",
        "comment": "Not FWS because no white space after the second fold",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_END",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "146",
        "address": " ␍␊␍␊test@iana.org",
        "comment": "Not FWS because no white space after either fold",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_X2",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "147",
        "address": " ␍␊␍␊ test@iana.org",
        "comment": "Not FWS because no white space after the first fold",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_X2",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "148",
        "address": "test@iana.org␍␊ ",
        "comment": "FWS",
        "category": "ISEMAIL_CFWS",
        "diagnosis": "ISEMAIL_CFWS_FWS",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "149",
        "address": "test@iana.org␍␊ ␍␊ ",
        "comment": "FWS with one line composed entirely of WSP -- only allowed as obsolete FWS (someone might allow only non-obsolete FWS)",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_FWS",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "150",
        "address": "test@iana.org␍␊",
        "comment": "Not FWS because no actual white space",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_END",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "151",
        "address": "test@iana.org␍␊ ␍␊",
        "comment": "Not obs-FWS because there must be white space on each \"fold\"",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_END",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "152",
        "address": "test@iana.org ␍␊",
        "comment": "Not FWS because no white space after the fold",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_END",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "153",
        "address": "test@iana.org ␍␊ ",
        "comment": "FWS",
        "category": "ISEMAIL_CFWS",
        "diagnosis": "ISEMAIL_CFWS_FWS",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "154",
        "address": "test@iana.org ␍␊ ␍␊",
        "comment": "Not FWS because no white space after the second fold",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_END",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "155",
        "address": "test@iana.org ␍␊␍␊",
        "comment": "Not FWS because no white space after either fold",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_X2",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "156",
        "address": "test@iana.org ␍␊␍␊ ",
        "comment": "Not FWS because no white space after the first fold",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_FWS_CRLF_X2",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "157",
        "address": " test@iana.org",
        "category": "ISEMAIL_CFWS",
        "diagnosis": "ISEMAIL_CFWS_FWS",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "158",
        "address": "test@iana.org ",
        "category": "ISEMAIL_CFWS",
        "diagnosis": "ISEMAIL_CFWS_FWS",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "159",
        "address": "test@[IPv6:1::2:]",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_IPV6_COLONEND",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "160",
        "address": "\"test\\©\"@iana.org",
        "category": "ISEMAIL_ERR",
        "diagnosis": "ISEMAIL_ERR_EXPECTING_QPAIR",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "161",
        "address": "test@iana/icann.org",
        "category": "ISEMAIL_RFC5322",
        "diagnosis": "ISEMAIL_RFC5322_DOMAIN",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "165",
        "address": "test.(comment)test@iana.org",
        "category": "ISEMAIL_DEPREC",
        "diagnosis": "ISEMAIL_DEPREC_COMMENT",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "166",
        "address": "test@org",
        "category": "ISEMAIL_RFC5321",
        "diagnosis": "ISEMAIL_RFC5321_TLD",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "167",
        "address": "test@test.com",
        "comment": "test.com has an A-record but not an MX-record",
        "category": "ISEMAIL_DNSWARN",
        "diagnosis": "ISEMAIL_DNSWARN_NO_MX_RECORD",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      },
      {
        "-id": "168",
        "address": "test@nic.no",
        "comment": "nic.no currently has no MX-records or A-records (Feb 2011). If you are seeing an A-record for nic.io then try setting your DNS server to 8.8.8.8 (the Google DNS server) - your DNS server may be faking an A-record (OpenDNS does this, for instance).",
        "category": "ISEMAIL_DNSWARN",
        "diagnosis": "ISEMAIL_DNSWARN_NO_RECORD",
        "source": "Dominic Sayers",
        "sourcelink": "http://isemail.info"
      }
    ]
  }
}"""

TESTS = json.dumps(TEST_DATA)