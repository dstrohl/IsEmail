
def make_char_str(*chars_in):
    tmp_ret = []
    for char in chars_in:
        if isinstance(char, str):
            tmp_ret.append(char)
        elif isinstance(char, int):
            tmp_ret.append(chr(char))
        elif isinstance(char, tuple):
            for c in range(char[0], char[1] + 1):
                tmp_ret.append(chr(c))
    return ''.join(tmp_ret)


def make_list(obj_in):
    if obj_in is None:
        return []
    if isinstance(obj_in, str):
        return [obj_in]
    if isinstance(obj_in, (list, tuple)):
        return obj_in
    if hasattr(obj_in, '__iter__'):
        return obj_in
    return [obj_in]


class UnSet(object):
    """
    Used in places to indicated an unset condition where None may be a valid option

    .. note:: *I borrowed the concept from* :py:mod:`configparser` *module*

    Example:
        For an example of this, see :py:class:`MultiLevelDictManager.get`

    """
    UnSetValidationString = '_*_This is the Unset Object_*_'

    def __repr__(self):
        return 'Empty Value'

    def __str__(self):
        return 'Empty Value'

    def __eq__(self, other):
        return isinstance(other, UnSet)


_UNSET = UnSet()