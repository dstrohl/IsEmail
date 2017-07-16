
class ParsingError(Exception):

    def __init__(self, results, *args):
        self.results = results
        super().__init__(*args)

    def __str__(self):
        return 'ERROR: Parsing Error: %r' % self.results

    def __repr__(self):
        return str(self)


class UnfinishedParsing(Exception):
    def __str__(self):
        return 'ERROR: Not finished parsing yet, data is not available'


class MessageListLocked(Exception):
    def __init__(self, msg, *args):
        self.msg = msg
        super().__init__(*args)

    def __str__(self):
        return 'ERROR: unable to add %s, message list locked' % self.msg
