
class ParsingError(Exception):

    def __init__(self, results, *args, **kwargs):
        self.results = results
        super().__init__(*args, **kwargs)

    def __str__(self):
        return 'ERROR: Parsing Error: %r' % self.results

    def __repr__(self):
        return str(self)


class UnfinishedParsing(Exception):
    def __str__(self):
        return 'ERROR: Not finished parsing yet, data is not available'
