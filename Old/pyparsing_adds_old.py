from pyparsing import *

ParserElement.setDefaultWhitespaceChars('')

class MeasureParsers(ParseElementEnhance):
    """
    Subclass for measurement parsers
    """
    def __init__(self, expr, min=1, max=None, exact=None, savelist=True):
        super(MeasureParsers, self).__init__(expr, savelist=savelist)
        self.mayReturnEmpty = True
        self.minCount = min
        self.maxCount = max
        self.exactCount = exact

    def _measure_results(self, loc, tokens):
        raise NotImplementedError()

    def parseImpl( self, instring, loc, doActions=True ):
        loc, tokens = super(MeasureParsers, self).parseImpl(instring=instring, loc=loc, doActions=doActions)
        measure = self._measure_results(loc, tokens)
        if self.exactCount is not None:
            if measure != self.exactCount:
                raise ParseException( instring, len(instring), self.errmsg, self )

        if self.maxCount is not None:
            if measure > self.maxCount:
                raise ParseException( instring, len(instring), self.errmsg, self )

        if self.minCount > 0:
            if measure < self.minCount:
                raise ParseException( instring, len(instring), self.errmsg, self )

        return loc, tokens


class CountIn(MeasureParsers):
    """
    Counts the occurrences of another parser while passing the results of the
    enclosing parser through unchanged, or will raise a ParserException if the min,
    max, or exact parameters are not met.
    Usage:
        CountIn(<expr>, <count_expr>, min=1, max=0, exact=0, overlap=False)

        expr = the initial expression that returns a tokenlist
        count_expr = an expression that will be used against the returned tokens
        min = if the count of count_expr is less than min, raise ParserException
        max = if the count of count_expr is more than max, raise ParserException
            (0 will validate that an expression is NOT in the tokens)
        exact = if the count of count_expr is not exactly exact, raise ParserException
            (0 will validate that an expression is NOT in the tokens)
        overlap = will count overlapping strings.

    Notes:
        This is uses the following approach:

            tokens = <expr>.parseString(instring)
            tmp_string = ''.join(tokens)
            tmp_tokens = <count_expr>.scanString(tmp_string, overlap=self.overlap)

            measure = len(list(tmp_tokens))
    """
    def __init__(self, expr, count_expr, *args, overlap=False, **kwargs):
        super(CountIn, self).__init__(expr, *args, **kwargs)
        self.count_expr = count_expr
        self.overlap = overlap

    def _measure_results(self, loc, tokens):
        tmp_string = ''.join(tokens)
        tmp_tokens = self.count_expr.scanString(tmp_string, overlap=self.overlap)
        return len(list(tmp_tokens))


class CountTokens(MeasureParsers):
    """
    Counts the number of tokens returned after passing the results of the
    enclosing parser, which is passed through unchanged, or will raise a
    ParserException if the min, max, or exact parameters are not met.
    Usage:
        CountTokens(<expr>, min=1, max=0, exact=0)

        expr = the initial expression that returns a tokenlist
        min = if the number of tokens returned is less than min, raise ParserException
        max = if the number of tokens returned is more than max, raise ParserException
            (0 will validate that an expression is NOT in the tokens)
        exact = if the  number of tokens returned is not exactly exact, raise ParserException
            (0 will validate that an expression is NOT in the tokens)

    Notes:
        This is uses the following approach:
            tokens = <expr>.parseString(instring)

            measure = len(list(tmp_tokens))
    """
    def _measure_results(self, loc, tokens):
        return len(tokens)


class Len(MeasureParsers):
    """
    Measures the length of the string of tokens returned after passing the
    results of the enclosing parser, which is passed through unchanged, or
    will raise a ParserException if the min, max, or exact parameters are not met.
    Usage:
        Len(<expr>, min=1, max=0, exact=0)

        expr = the initial expression that returns a tokenlist
        min = if the length of the combined strings of the tokens returned is less than min, raise ParserException
        max = if the length of the combined strings of the tokens is more than max, raise ParserException
            (0 will validate that an expression is NOT in the tokens)
        exact = if the length of the combined strings of the tokens returned is not exactly exact, raise ParserException
            (0 will validate that an expression is NOT in the tokens)

    Notes:
        This is uses the following approach:

            tokens = <expr>.parseString(instring)
            tmp_string = ''.join(tokens)

            measure = len(tmp_string)
    """
    def _measure_results(self, loc, tokens):
        tmp_string = ''.join(tokens)
        return len(tmp_string)

