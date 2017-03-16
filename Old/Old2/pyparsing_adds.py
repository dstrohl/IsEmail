import pyparsing as pp
from pyparsing import *
import sys

pp.ParserElement.setDefaultWhitespaceChars('')

PP_DEBUG = False

# ==================================================================
# Common Literals
# ==================================================================

'''
def _consolidate_parsed_results(token, combine=True, root=None, join_str=''):
    token = token.copy()
    tmp_ret_list = []
    tmp_keys = list(token)
    tmp_root = root or token

    if isinstance(token, dict):
        tmp_keys.sort()

    for key in tmp_keys:
        item = token[key]
        if isinstance(item, (pp.ParseResults, dict)):
            tmp_sub_item = _consolidate_parsed_results(item, combine, root=tmp_root, join_str=join_str)
            if combine:
                tmp_root[key] = tmp_sub_item
                tmp_ret_list.append(tmp_sub_item)
            else:
                del token[key]
        else:
            if root is not None:
                root[key] = item
                if combine:
                    tmp_ret_list.append(item)

    if root is not None:
        return join_str.join(tmp_ret_list)
    else:
        return token
'''
def flatten_results(results):
    tmp_ret = {}
    for key, item in results.items():
        if isinstance(item, (list, str)):
            tmp_ret[key] = item
        else:
            tmp_flat = flatten_results(item)
            tmp_item = ''.join(tmp_flat.values())
            tmp_ret[key] = tmp_item
            tmp_ret.update(flatten_results(item))
    return tmp_ret


def make_char_str(*chars_in, skip=None):
    tmp_ret = []
    for char in chars_in:
        if isinstance(char, str):
            tmp_ret.append(char)
        elif isinstance(char, int):
            tmp_ret.append(chr(char))
        elif isinstance(char, tuple):
            for c in range(char[0], char[1]+1):
                tmp_ret.append(chr(c))

    tmp_ret = ''.join(tmp_ret)

    if skip is not None:
        tmp_skip = make_char_str(*skip)
        for char in tmp_skip:
            tmp_ret = tmp_ret.replace(char, '')

    return tmp_ret


def mme_match(measure, min=1, max=None, exact=None):
    if exact is not None:
        return measure == exact
    max = max or sys.maxsize
    return (min - 1) < measure < (max + 1)


def mme_string(min=1, max=None, exact=None):
    if exact is not None:
        return 'exactly %s' % exact
    if max is None:
        return 'more than %s' % min
    else:
        return 'between %s and %s' % (min, max)


def count_in(tokens, match_expr, min=1, max=None, exact=None, overlap=False):
    tmp_string = ''.join(list(tokens))
    if issubclass(match_expr.__class__, pp.ParserElement):
        tmp_tokens = match_expr.scanString(tmp_string, overlap=overlap)
        measure = len(list(tmp_tokens))
    else:
        measure = tmp_string.count(match_expr)

    return mme_match(measure=measure, min=min, max=max, exact=exact)


def count_token(tokens, min=1, max=None, exact=None):
    return mme_match(len(tokens), min=min, max=max, exact=exact)


def len_tokens(tokens, min=1, max=None, exact=None):
    tmp_string = ''.join(list(tokens))
    return mme_match(len(tmp_string), min=min, max=max, exact=exact)


def CountIn(expr, match_expr, min=1, max=None, exact=None, overlap=False):
    msg = 'count of %r is not %s' % (match_expr, mme_string(min, max, exact))
    return expr.copy().addCondition(lambda t: count_in(t, match_expr, min, max, exact, overlap), message=msg)


def Count(expr, min=1, max=None, exact=None):
    msg = 'token count is not %s' % (mme_string(min, max, exact))
    return expr.copy().addCondition(lambda t: count_token(t, min, max, exact), message=msg)


def Len(expr, min=1, max=None, exact=None):
    msg = 'length of the tokens is not %s' % (mme_string(min, max, exact))
    return expr.copy().addCondition(lambda t: len_tokens(t, min, max, exact), message=msg)


def _add_debug(cls, *args, **kwargs):
    return cls(*args, **kwargs).setDebug(PP_DEBUG)


def Word(*args, **kwargs):
    return _add_debug(pp.Word, *args, **kwargs)

def Literal(*args, **kwargs):
    return _add_debug(pp.Literal, *args, **kwargs)

def CaselessLiteral(*args, **kwargs):
    return _add_debug(pp.CaselessLiteral, *args, **kwargs)

def Combine(*args, **kwargs):
    return _add_debug(pp.Combine, *args, **kwargs)

def And(*args, **kwargs):
    return _add_debug(pp.And, *args, **kwargs)

def Or(*args, **kwargs):
    return _add_debug(pp.Or, *args, **kwargs)

def MatchFirst(*args, **kwargs):
    return _add_debug(pp.MatchFirst, *args, **kwargs)

def Optional(*args, **kwargs):
    return _add_debug(pp.Optional, *args, **kwargs)

def OneOrMore(*args, **kwargs):
    return _add_debug(pp.OneOrMore, *args, **kwargs)

def White(*args, **kwargs):
    return _add_debug(pp.White, *args, **kwargs)

def ZeroOrMore(*args, **kwargs):
    return _add_debug(pp.ZeroOrMore, *args, **kwargs)

def Forward(*args, **kwargs):
    return _add_debug(pp.Forward, *args, **kwargs)
