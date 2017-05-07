RETURN_OBJ_TESTS = {
    'diag': {
        'return_as_string': {
            'kwargs': {
                'return_as': 'string'
            },
            'no_cat': {
                'kwargs': {
                    'inc_cat': False,
                    'inc_diag': True
                },
                'exp_full_ret': 'DNSWARN_INVALID_TLD, RFC5321_TLD_NUMERIC, RFC5321_QUOTED_STRING, RFC5321_ADDRESS_LITERAL, ERR_UNCLOSED_COMMENT',
                'filter': 'RFC5321_TLD_NUMERIC',
                'exp_filtered_ret': 'RFC5321_TLD_NUMERIC',
                'single_full_ret': 'ERR_UNCLOSED_COMMENT',
                'single_filtered_ret': 'RFC5321_TLD_NUMERIC'
            },
            'w_cat': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': True
                },
                'exp_full_ret': 'ISEMAIL_DNSWARN(DNSWARN_INVALID_TLD), ISEMAIL_RFC5321(RFC5321_TLD_NUMERIC, RFC5321_QUOTED_STRING, RFC5321_ADDRESS_LITERAL), ISEMAIL_ERR(ERR_UNCLOSED_COMMENT)',
                'filter': 'RFC5321_TLD_NUMERIC',
                'exp_filtered_ret': 'ISEMAIL_RFC5321(RFC5321_TLD_NUMERIC)',
                'single_full_ret': 'ISEMAIL_ERR(ERR_UNCLOSED_COMMENT)',
                'single_filtered_ret': 'ISEMAIL_RFC5321(RFC5321_TLD_NUMERIC)'
            },
            'cat_only': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': False
                },
                'exp_full_ret': 'ISEMAIL_RFC5321, ISEMAIL_DNSWARN, ISEMAIL_ERR',
                'filter': 'RFC5321_TLD_NUMERIC',
                'exp_filtered_ret': 'ISEMAIL_RFC5321',
                'single_full_ret': 'ISEMAIL_ERR',
                'single_filtered_ret': 'ISEMAIL_RFC5321'
            }
        },
        'return_as_list': {
            'kwargs': {
                'return_as': 'list'
            },
            'no_cat': {
                'kwargs': {
                    'inc_cat': False,
                    'inc_diag': True
                },
                'exp_full_ret': [
                    'DNSWARN_INVALID_TLD', 'RFC5321_TLD_NUMERIC', 'RFC5321_QUOTED_STRING',
                    'RFC5321_ADDRESS_LITERAL',
                    'ERR_UNCLOSED_COMMENT'
                ],
                'filter': 'RFC5321_TLD_NUMERIC',
                'exp_filtered_ret': [
                    'RFC5321_TLD_NUMERIC'
                ],
                'single_full_ret': [
                    'ERR_UNCLOSED_COMMENT'
                ],
                'single_filtered_ret': [
                    'RFC5321_TLD_NUMERIC'
                ]
            },
            'w_cat': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': True
                },
                'exp_full_ret': [
                    ('ISEMAIL_DNSWARN', ['DNSWARN_INVALID_TLD']), ('ISEMAIL_RFC5321', ['RFC5321_TLD_NUMERIC', 'RFC5321_QUOTED_STRING', 'RFC5321_ADDRESS_LITERAL']), ('ISEMAIL_ERR', ['ERR_UNCLOSED_COMMENT'])
                ],
                'filter': 'RFC5321_TLD_NUMERIC',
                'exp_filtered_ret': [('ISEMAIL_RFC5321', ['RFC5321_TLD_NUMERIC'])],
                'single_full_ret': [('ISEMAIL_ERR', ['ERR_UNCLOSED_COMMENT'])],
                'single_filtered_ret': [('ISEMAIL_RFC5321', ['RFC5321_TLD_NUMERIC'])]
            },
            'cat_only': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': False
                },
                'exp_full_ret': ['ISEMAIL_RFC5321', 'ISEMAIL_DNSWARN', 'ISEMAIL_ERR'],
                'filter': 'RFC5321_TLD_NUMERIC',
                'exp_filtered_ret': ['ISEMAIL_RFC5321', 'ISEMAIL_DNSWARN', 'ISEMAIL_ERR'],
                'single_full_ret': ['ISEMAIL_ERR'],
                'single_filtered_ret': ['ISEMAIL_RFC5321']
            }
        },

        'return_as_dict': {
            'kwargs': {
                'return_as': 'dict'
            },
            'no_cat': {
                'kwargs': {
                    'inc_cat': False,
                    'inc_diag': True
                },
                'exp_full_ret': {
                    'ISEMAIL_DNSWARN': [
                        'DNSWARN_INVALID_TLD'
                    ],
                    'ISEMAIL_RFC5321': [
                        'RFC5321_TLD_NUMERIC',
                        'RFC5321_QUOTED_STRING',
                        'RFC5321_ADDRESS_LITERAL'
                    ],
                    'ISEMAIL_ERR': [
                        'ERR_UNCLOSED_COMMENT'
                    ]
                },
                'filter': 'RFC5321_TLD_NUMERIC',
                'exp_filtered_ret': {
                    'ISEMAIL_RFC5321': [
                        'RFC5321_TLD_NUMERIC'
                    ]
                },
                'single_full_ret': {
                    'ISEMAIL_ERR': 'ERR_UNCLOSED_COMMENT'
                },
                'single_filtered_ret': {
                    'ISEMAIL_RFC5321': 'RFC5321_TLD_NUMERIC'
                }
            },
            'w_cat': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': True
                },
                'exp_full_ret': {
                    'ISEMAIL_DNSWARN': [
                        'DNSWARN_INVALID_TLD'
                    ],
                    'ISEMAIL_RFC5321': [
                        'RFC5321_TLD_NUMERIC',
                        'RFC5321_QUOTED_STRING',
                        'RFC5321_ADDRESS_LITERAL'
                    ],
                    'ISEMAIL_ERR': [
                        'ERR_UNCLOSED_COMMENT'
                    ]
                },
                'filter': 'RFC5321_TLD_NUMERIC',
                'exp_filtered_ret': {
                    'ISEMAIL_RFC5321': [
                        'RFC5321_TLD_NUMERIC'
                    ]
                },
                'single_full_ret': {
                    'ISEMAIL_ERR': 'ERR_UNCLOSED_COMMENT'
                },
                'single_filtered_ret': {
                    'ISEMAIL_RFC5321': 'RFC5321_TLD_NUMERIC'
                }
            },
            'cat_only': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': False
                },
                'exp_full_ret': {
                    'ISEMAIL_DNSWARN': ['DNSWARN_INVALID_TLD'],
                    'ISEMAIL_RFC5321': ['RFC5321_TLD_NUMERIC', 'RFC5321_QUOTED_STRING', 'RFC5321_ADDRESS_LITERAL'],
                    'ISEMAIL_ERR': ['ERR_UNCLOSED_COMMENT']
                },
                'filter': 'RFC5321_TLD_NUMERIC',
                'exp_filtered_ret': {
                    'ISEMAIL_RFC5321': ['RFC5321_TLD_NUMERIC']
                },
                'single_full_ret': {
                    'ISEMAIL_ERR': 'ERR_UNCLOSED_COMMENT'
                },
                'single_filtered_ret': {
                    'ISEMAIL_RFC5321': 'RFC5321_TLD_NUMERIC'
                }
            }
        },
    },

    'desc': {
        'return_as_string': {
            'kwargs': {
                'return_as': 'string'
            },
            'no_cat': {
                'kwargs': {
                    'inc_cat': False,
                    'inc_diag': True
                },
                'exp_full_ret': ''\
                '[ERROR] Unclosed comment\n'\
                '[WARNING] Address is valid but the Top Level Domain begins with a number\n'\
                '[WARNING] Address is valid but contains a quoted string\n'\
                '[WARNING] Address is valid but at a literal address not a domain\n'\
                '[WARNING] Top Level Domain is not in the list of available TLDs',
                'filter': ('ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
                'exp_filtered_ret': ''\
                '[WARNING] Address is valid but the Top Level Domain begins with a number\n'\
                '[WARNING] Address is valid but contains a quoted string\n'\
                '[WARNING] Address is valid but at a literal address not a domain\n'\
                '[WARNING] Top Level Domain is not in the list of available TLDs\n',
                'single_full_ret': '[ERROR] Unclosed comment',
                'single_filtered_ret': '[ERROR] Unclosed comment'
            },
            'w_cat': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': True
                },
                'exp_full_ret': ''\
                'Invalid Address: (ERROR)\n'\
                '(Address is invalid for any purpose)\n'\
                '    - description="Unclosed comment\n'\
                '\n'\
                'Valid Address (unusual): [WARNING]\n'\
                '(Address is valid for SMTP but has unusual elements)\n'\
                '    - Address is valid but the Top Level Domain begins with a number\n'\
                '    - Address is valid but contains a quoted string\n'\
                '    - Address is valid but at a literal address not a domain\n'\
                '\n'\
                'Valid Address (DNS Warning): [WARNINNG]\n'\
                '(Address is valid but a DNS check was not successful)\n'\
                '    - Top Level Domain is not in the list of available TLDs\n',
                'filter': ('ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
                'exp_filtered_ret': ''\
                'Valid Address (unusual): [WARNING]\n'\
                '(Address is valid for SMTP but has unusual elements)\n'\
                '    - Address is valid but the Top Level Domain begins with a number\n'\
                '    - Address is valid but contains a quoted string\n'\
                '    - Address is valid but at a literal address not a domain\n'\
                '\n'\
                'Valid Address (DNS Warning): [WARNINNG]\n'\
                '(Address is valid but a DNS check was not successful)\n'\
                '    - Top Level Domain is not in the list of available TLDs',
                'single_full_ret': ''\
                'Invalid Address: (ERROR)\n'\
                '(Address is invalid for any purpose)\n'\
                '    - description="Unclosed comment',
                'single_filtered_ret': ''\
                'Invalid Address: (ERROR)\n'\
                '(Address is invalid for any purpose)\n'\
                '    - description="Unclosed comment'
            },
            'cat_only': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': False
                },
                'exp_full_ret': ''\
                '[ERROR] - Invalid Address: (Address is invalid for any purpose)\n'\
                '[WARNING] - Valid Address (unusual): (Address is valid for SMTP but has unusual elements)\n'\
                '[WARNING] - Valid Address (DNS Warning): (Address is valid but a DNS check was not successful)',
                'filter': (
                    'ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
                'exp_filtered_ret': ''\
                '[WARNING] - Valid Address (unusual): (Address is valid for SMTP but has unusual elements)\n'\
                '[WARNING] - Valid Address (DNS Warning): (Address is valid but a DNS check was not successful)',
                'single_full_ret': '[ERROR] - Invalid Address: (Address is invalid for any purpose)',
                'single_filtered_ret': '[ERROR] - Invalid Address: (Address is invalid for any purpose)'
            }
        },
        'return_as_list': {
            'kwargs': {
                'return_as': 'list'
            },
            'no_cat': {
                'kwargs': {
                    'inc_cat': False,
                    'inc_diag': True
                },
                'exp_full_ret': [
                    '[ERROR] Unclosed comment',
                    '[WARNING] Address is valid but the Top Level Domain begins with a number',
                    '[WARNING] Address is valid but contains a quoted string',
                    '[WARNING] Address is valid but at a literal address not a domain',
                    '[WARNING] Top Level Domain is not in the list of available TLDs'
                ],
                'filter': (
                    'ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
                'exp_filtered_ret': [
                    '[WARNING] Address is valid but the Top Level Domain begins with a number',
                    '[WARNING] Address is valid but contains a quoted string',
                    '[WARNING] Address is valid but at a literal address not a domain',
                    '[WARNING] Top Level Domain is not in the list of available TLDs'
                ],
                'single_full_ret': [
                    '[ERROR] Unclosed comment'
                ],
                'single_filtered_ret': [
                    '[ERROR] Unclosed comment'
                ]
            },
            'w_cat': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': True
                },
                'exp_full_ret': [
                    ['[ERROR] - Invalid Address: (Address is invalid for any purpose)', [
                        '[ERROR] Unclosed comment'
                    ]],
                    ['[WARNING] - Valid Address (unusual): (Address is valid for SMTP but has unusual elements)', [
                        '[WARNING] Address is valid but the Top Level Domain begins with a number',
                        '[WARNING] Address is valid but contains a quoted string',
                        '[WARNING] Address is valid but at a literal address not a domain'
                    ]],
                    ['[WARNING] - Valid Address (DNS Warning): (Address is valid but a DNS check was not successful)', [
                        '[WARNING] Top Level Domain is not in the list of available TLDs'
                    ]]
                ],
                'filter': (
                    'ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
                'exp_filtered_ret': [
                    ['[WARNING] - Valid Address (unusual): (Address is valid for SMTP but has unusual elements)', [
                        '[WARNING] Address is valid but the Top Level Domain begins with a number',
                        '[WARNING] Address is valid but contains a quoted string',
                        '[WARNING] Address is valid but at a literal address not a domain'
                    ]],
                    ['[WARNING] - Valid Address (DNS Warning): (Address is valid but a DNS check was not successful)', [
                        '[WARNING] Top Level Domain is not in the list of available TLDs'
                    ]]
                ],
                'single_full_ret': [
                    ['[ERROR] - Invalid Address: (Address is invalid for any purpose)', [
                        '[ERROR] Unclosed comment'
                    ]]
                ],
                'single_filtered_ret': [
                    ['[ERROR] - Invalid Address: (Address is invalid for any purpose)', [
                        '[ERROR] Unclosed comment'
                    ]]
                ]
            },
            'cat_only': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': False
                },
                'exp_full_ret': [
                    '[ERROR] - Invalid Address: (Address is invalid for any purpose)',
                    '[WARNING] - Valid Address (unusual): (Address is valid for SMTP but has unusual elements)',
                    '[WARNING] - Valid Address (DNS Warning): (Address is valid but a DNS check was not successful)'
                ],
                'filter': ('ISEMAIL_RFC5321', 'ERR_UNCLOSED_COMMENT'),
                'exp_filtered_ret': [
                    '[WARNING] - Valid Address (unusual): (Address is valid for SMTP but has unusual elements)',
                    '[WARNING] - Valid Address (DNS Warning): (Address is valid but a DNS check was not successful)'
                ],
                'single_full_ret': ['[ERROR] - Invalid Address: (Address is invalid for any purpose)'],
                'single_filtered_ret': ['[ERROR] - Invalid Address: (Address is invalid for any purpose)']
            }
        },
        'return_as_dict': {
            'kwargs': {
                'return_as': 'dict'
            },
            'no_cat': {
                'kwargs': {
                    'inc_cat': False,
                    'inc_diag': True
                },
                'exp_full_ret': {
                    'RFC5321_TLD_NUMERIC': {
                        'value': 1010,
                        'description': "Address is valid but the Top Level Domain begins with a number",
                        'cat': 'ISEMAIL_RFC5321',
                        'type': 'WARNING'
                    },
                    'RFC5321_QUOTED_STRING': {
                        'value': 1011,
                        'description': "Address is valid but contains a quoted string",
                        'cat': 'ISEMAIL_RFC5321',
                        'type': 'WARNING'
                    },
                    'RFC5321_ADDRESS_LITERAL': {
                        'value': 1012,
                        'description': "Address is valid but at a literal address not a domain",
                        'cat': 'ISEMAIL_RFC5321',
                        'type': 'WARNING'
                    },
                    'DNSWARN_INVALID_TLD': {
                        'value': 1004,
                        'description': "Top Level Domain is not in the list of available TLDs",
                        'cat': 'ISEMAIL_DNSWARN',
                        'type': 'WARNING'
                    },
                    'ERR_UNCLOSED_COMMENT': {
                        'value': 1146,
                        'description': "Unclosed comment",
                        'cat': 'ISEMAIL_ERR',
                        'type': 'ERROR'
                    }
                },
                'filter': 'WARNING',
                'exp_filtered_ret': {
                    'RFC5321_TLD_NUMERIC': {
                        'value': 1010,
                        'description': "Address is valid but the Top Level Domain begins with a number",
                        'cat': 'ISEMAIL_RFC5321',
                        'type': 'WARNING'
                    },
                    'RFC5321_QUOTED_STRING': {
                        'value': 1011,
                        'description': "Address is valid but contains a quoted string",
                        'cat': 'ISEMAIL_RFC5321',
                        'type': 'WARNING'
                    },
                    'RFC5321_ADDRESS_LITERAL': {
                        'value': 1012,
                        'description': "Address is valid but at a literal address not a domain",
                        'cat': 'ISEMAIL_RFC5321',
                        'type': 'WARNING'
                    },
                    'DNSWARN_INVALID_TLD': {
                        'value': 1004,
                        'description': "Top Level Domain is not in the list of available TLDs",
                        'cat': 'ISEMAIL_DNSWARN',
                        'type': 'WARNING'
                    }
                },
                'single_full_ret': {
                    'ERR_UNCLOSED_COMMENT': {
                        'value': 1146,
                        'description': "Unclosed comment",
                        'cat': 'ISEMAIL_ERR',
                        'type': 'ERROR'
                    }
                },
                'single_filtered_ret': {
                    'RFC5321_ADDRESS_LITERAL': {
                        'value': 1012,
                        'description': "Address is valid but at a literal address not a domain",
                        'cat': 'ISEMAIL_RFC5321',
                        'type': 'WARNING'
                    }
                }
            },
            'w_cat': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': True
                },
                'exp_full_ret': {
                    'ISEMAIL_RFC5321': {
                        'value': 115,
                        'name': 'Valid Address (unusual)',
                        'description': "Address is valid for SMTP but has unusual elements",
                        'type': 'WARNING',
                        'diags': {
                            'RFC5321_TLD_NUMERIC': {
                                'value': 1010,
                                'description': "Address is valid but the Top Level Domain begins with a number",
                                'cat': 'ISEMAIL_RFC5321',
                                'type': 'WARNING'
                            },
                            'RFC5321_QUOTED_STRING': {
                                'value': 1011,
                                'description': "Address is valid but contains a quoted string",
                                'cat': 'ISEMAIL_RFC5321',
                                'type': 'WARNING'
                            },
                            'RFC5321_ADDRESS_LITERAL': {
                                'value': 1012,
                                'description': "Address is valid but at a literal address not a domain",
                                'cat': 'ISEMAIL_RFC5321',
                                'type': 'WARNING'
                            }
                        }
                    },
                    'ISEMAIL_DNSWARN': {
                        'value': 107,
                        'name': 'Valid Address (DNS Warning)',
                        'description': "Address is valid but a DNS check was not successful",
                        'type': 'WARNING',
                        'diags': {
                            'DNSWARN_INVALID_TLD': {
                                'value': 1004,
                                'description': "Top Level Domain is not in the list of available TLDs",
                                'cat': 'ISEMAIL_DNSWARN',
                                'type': 'WARNING'
                            }
                        }
                    },
                    'ISEMAIL_ERR': {
                        'value': 999,
                        'name': 'Invalid Address',
                        'description': "Address is invalid for any purpose",
                        'type': 'ERROR',
                        'diags': {
                            'ERR_UNCLOSED_COMMENT': {
                                'value': 1146,
                                'description': "Unclosed comment",
                                'cat': 'ISEMAIL_ERR',
                                'type': 'ERROR'
                            }
                        }
                    }
                },
                'filter': 'WARNING',
                'exp_filtered_ret': {
                    'ISEMAIL_RFC5321': {
                        'value': 115,
                        'name': 'Valid Address (unusual)',
                        'description': "Address is valid for SMTP but has unusual elements",
                        'type': 'WARNING',
                        'diags': {
                            'RFC5321_TLD_NUMERIC': {
                                'value': 1010,
                                'description': "Address is valid but the Top Level Domain begins with a number",
                                'cat': 'ISEMAIL_RFC5321',
                                'type': 'WARNING'
                            },
                            'RFC5321_QUOTED_STRING': {
                                'value': 1011,
                                'description': "Address is valid but contains a quoted string",
                                'cat': 'ISEMAIL_RFC5321',
                                'type': 'WARNING'
                            },
                            'RFC5321_ADDRESS_LITERAL': {
                                'value': 1012,
                                'description': "Address is valid but at a literal address not a domain",
                                'cat': 'ISEMAIL_RFC5321',
                                'type': 'WARNING'
                            }
                        }
                    },
                    'ISEMAIL_DNSWARN': {
                        'value': 107,
                        'name': 'Valid Address (DNS Warning)',
                        'description': "Address is valid but a DNS check was not successful",
                        'type': 'WARNING',
                        'diags': {
                            'DNSWARN_INVALID_TLD': {
                                'value': 1004,
                                'description': "Top Level Domain is not in the list of available TLDs",
                                'cat': 'ISEMAIL_DNSWARN',
                                'type': 'WARNING'
                            }
                        }
                    }
                },
                'single_full_ret': {
                    'ISEMAIL_ERR': {
                        'value': 999,
                        'name': 'Invalid Address',
                        'description': "Address is invalid for any purpose",
                        'type': 'ERROR',
                        'diags': {
                            'ERR_UNCLOSED_COMMENT': {
                                'value': 1146,
                                'description': "Unclosed comment",
                                'cat': 'ISEMAIL_ERR',
                                'type': 'ERROR'
                            }
                        }
                    }
                },
                'single_filtered_ret': {
                    'ISEMAIL_RFC5321': {
                        'value': 115,
                        'name': 'Valid Address (unusual)',
                        'description': "Address is valid for SMTP but has unusual elements",
                        'type': 'WARNING',
                        'diags': {
                            'RFC5321_ADDRESS_LITERAL': {
                                'value': 1012,
                                'description': "Address is valid but at a literal address not a domain",
                                'cat': 'ISEMAIL_RFC5321',
                                'type': 'WARNING'
                            }
                        }
                    }
                }
            },
            'cat_only': {
                'kwargs': {
                    'inc_cat': True,
                    'inc_diag': False
                },
                'exp_full_ret': {
                    'ISEMAIL_RFC5321': {
                        'value': 115,
                        'name': 'Valid Address (unusual)',
                        'description': "Address is valid for SMTP but has unusual elements",
                        'type': 'WARNING'
                    },
                    'ISEMAIL_DNSWARN': {
                        'value': 107,
                        'name': 'Valid Address (DNS Warning)',
                        'description': "Address is valid but a DNS check was not successful",
                        'type': 'WARNING'
                    },
                    'ISEMAIL_ERR': {
                        'value': 999,
                        'name': 'Invalid Address',
                        'description': "Address is invalid for any purpose",
                        'type': 'ERROR'
                    }
                },
                'filter': 'WARNING',
                'exp_filtered_ret': {
                    'ISEMAIL_RFC5321': {
                        'value': 115,
                        'name': 'Valid Address (unusual)',
                        'description': "Address is valid for SMTP but has unusual elements",
                        'type': 'WARNING'
                    },
                    'ISEMAIL_DNSWARN': {
                        'value': 107,
                        'name': 'Valid Address (DNS Warning)',
                        'description': "Address is valid but a DNS check was not successful",
                        'type': 'WARNING'
                    }
                },
                'single_full_ret': {
                    'ISEMAIL_ERR': {
                        'value': 999,
                        'name': 'Invalid Address',
                        'description': "Address is invalid for any purpose",
                        'type': 'ERROR'
                    }
                },
                'single_filtered_ret': {
                    'ISEMAIL_RFC5321': {
                        'value': 115,
                        'name': 'Valid Address (unusual)',
                        'description': "Address is valid for SMTP but has unusual elements",
                        'type': 'WARNING'
                    }
                }
            }
        },
    },

}