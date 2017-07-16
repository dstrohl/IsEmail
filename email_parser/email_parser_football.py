
class EmailParsingObj(ParsingObj):

    def __init__(self,
                 str_in=None,
                 verbose=0,
                 trace_level=-1,
                 raise_on_error=False,
                 dns_lookup_level=None,
                 dns_servers=None,
                 dns_timeout=None,
                 tld_list=None,
                 meta_data=None):
        """
        :param email_in:  the email to parse
        :param verbose:
            * 0 = only return true/false
            * 1 = return t/f + cleaned email + major reason
            * 2 = return all

        """
        self.dns_lookup_level = dns_lookup_level or ISEMAIL_DNS_LOOKUP_LEVELS.NO_LOOKUP
        self.dns_servers = dns_servers
        self.dns_timeout = dns_timeout
        self.tld_list = tld_list

        self.at_loc = None
        self.local_comments = {}
        self.domain_comments = {}
        self.domain_type = None
        self.results = None

        super().__init__(str_in=str_in, verbose=verbose, trace_level=trace_level,
                         raise_on_error=raise_on_error, meta_data=meta_data)

        self.flags = FlagHelper('in_crlf', 'at_in_cfws', 'near_at_flag')

    @property
    def in_domain(self):
        return self.at_loc is not None

    @property
    def in_local(self):
        return self.at_loc is None

    def add_comment(self, football):

        if self.in_local:
            self.local_comments[football.begin] = (football.begin, football.length, self.mid(football.begin+1, football.length-2))
        else:
            self.domain_comments[football.begin] = (football.betin, football.length, self.mid(football.begin+1, football.length-2))
        return self

