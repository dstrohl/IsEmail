__all__ = ['BaseParser', 'SingleCharParser', 'CharParser', 'StringParser', 'SubParsersParser',
           'LoopMixin', 'EnclosedWrapper', 'MaxLenWrapper', 'MinLenWrapper', 'InvalidNextWrapper',
           'InvalidStartStopWrapper',
           'FullLengthWrapper', 'MinMaxLenWrapper',
           'CharNoSegment', 'SingleCharNoSegment', 'StringNoSegment'
           ]

from ValidationParser.exceptions import ParsingError, WrapperStop
from helpers.general.general import make_list
import sys

"""
for correct sub-classing...

NewClass(outmost, outer, inner, base_class)

# **********************************************************************************
# INNER PARSERS
# **********************************************************************************

class PHBaseChar(PHBase):
    look_for = None
    char_until_char = None
    min_char_count = None
    max_char_count = None
    min_char_count_msg = 'SEGMENT_TOO_SHORT'
    caps_sensitive = True

class PHBaseSingleChar(PHBaseChar):
    look_for = None
    char_until_char = None
    min_char_count = None
    max_char_count = None
    min_char_count_msg = 'SEGMENT_TOO_SHORT'
    caps_sensitive = True

    min_char_count = 1
    max_char_count = 1


class PHBaseString(PHBaseChar):
    look_for = None
    char_until_char = None
    min_char_count = None
    max_char_count = None
    min_char_count_msg = 'SEGMENT_TOO_SHORT'
    caps_sensitive = True


class PHBaseSubParsers(PHBase):
    operation = 'and'  # ['and'|'or'|'best']
    parsers = None

# **********************************************************************************
# OUTER PARSERS
# **********************************************************************************

class PHSegment(object):
    is_history_item = True
    is_segment_item = True

    name = None
    description = None
    references = None
    messages = None

    on_pass_msg = None  # 'VALID'
    on_fail_msg = None  # 'ERROR'


class PHFullLength(object):
    not_full_length_msg = 'INVALID_CHAR'


class PHLoop(object):
    min_loop = None
    min_loop_fail_msg = 'TOO_FEW_SEGMENTS'
    max_loop = None
    max_loop_fail_msg = 'TOO_MANY_SEGMENTS'
    max_loop_fail = False

class PHInvalidNext(object):
    invalid_next_char = None
    invalid_next_char_msg = 'INVALID_NEXT_CHAR'


class PHEnclosed(object):
    enclosure_start = '"'
    enclosure_end = '"'
    skip_quoted = True
    unclosed_msg = 'UNCLOSED_STRING'


class PHMinLen(object):
    min_length = None
    min_length_msg = 'SEGMENT_TOO_SHORT'


class PHMaxLen(object):
    max_length = None
    max_length_msg = 'SEGMENT_TOO_LONG'


class PHMinMaxLen(object):
    min_length = None
    min_length_msg = 'SEGMENT_TOO_SHORT'
    max_length = None
    max_length_msg = 'SEGMENT_TOO_LONG'


class PHInvalidStartStop(object):
    invalid_start_chars = None
    invlaid_start_chars_msg = 'INVALID_START'
    invalid_end_chars = None
    invlaid_end_chars_msg = 'INVALID_END'


"""


# **********************************************************************************
# <editor-fold desc="  BASE Parsers  ">
# **********************************************************************************


class BaseParser(object):
    wrappers = None
    # inner_parser = None

    is_history = True
    is_segment = True

    name = None
    description = None
    references = None
    messages = None

    on_pass_msg = None  # 'VALID'
    on_fail_msg = None  # 'ERROR'

    def __init__(self, *args, **kwargs):

        self.wrappers = make_list(kwargs.pop('wrappers', self.wrappers), force_list=True)
        self.messages = make_list(kwargs.pop('messages', self.messages))
        # self.inner_parser = kwargs.pop('parser', self.inner_parser)

        if kwargs:
            for key in list(kwargs):
                setattr(self, key, kwargs.pop(key) or getattr(self, key))

        self._load_parsers()

        # if self.inner_parser is None:
        #     raise AttributeError('Parser must be defined')

        self._lookups = {}
        self._parser_segment_defs = {}

        self.name = self.name or self.__class__.__name__
        self.on_pass_msg = make_list(self.on_pass_msg)
        self.on_fail_msg = make_list(self.on_fail_msg)

        if self.description is not None:
            self._parser_segment_defs['description'] = self.description
        if self.references is not None:
            self._parser_segment_defs['references'] = self.references

    def _load_parsers(self):
        for index, wrapper in enumerate(self.wrappers):
            wrapper = wrapper(self)

            if wrapper.messages:
                self.messages.extend(make_list(wrapper.messages))

            self.wrappers[index] = wrapper

    def _update_messages(self, parser_obj):
        if parser_obj.message_lookup.name not in self._lookups:
            if self.is_segment and self.name:
                parser_obj.message_lookup.segment(self.name, **self._parser_segment_defs)
            if self.messages is not None:
                parser_obj.message_lookup.add(messages=self.messages)
            self._lookups[parser_obj.message_lookup.name] = None

    def _parse(self, tmp_ret, parse_obj, position, **kwargs):
        pass

    def _call(self, tmp_ret, parse_obj, position, **kwargs):
        for wrapper in self.wrappers:
            try:
                wrapper.pre_process(tmp_ret, parse_obj, position + tmp_ret, **kwargs)
            except WrapperStop as err:
                return err.results

        try:
            self._parse(tmp_ret, parse_obj, position + tmp_ret, **kwargs)
        except WrapperStop as err:
            return err.results

        for wrapper in reversed(self.wrappers):
            try:
                wrapper.post_process(tmp_ret, parse_obj, position + tmp_ret, **kwargs)
            except WrapperStop as err:
                return err.results
        return tmp_ret

    def __call__(self, parse_obj, position=0, **kwargs):
        self._update_messages(parse_obj)
        tmp_err = None
        position = int(position)
        # init_position = position

        if self.is_segment:
            parse_obj.begin_stage(self.name, position=position)

        tmp_ret = parse_obj.fb(position, is_history=self.is_history)

        raise_error = False
    
        if parse_obj.at_end(position):
            return tmp_ret

        try:
            tmp_ret = self._call(tmp_ret, parse_obj, position, **kwargs)

        except ParsingError as err:
            tmp_err = err
            raise_error = True
            tmp_ret = err.results

        tmp_ret.set_done(set_history=self.is_history, pass_msg=self.on_pass_msg, fail_msg=self.on_fail_msg)

        if self.is_segment:
            parse_obj.end_stage(tmp_ret, raise_error=raise_error)

        if raise_error:
            raise tmp_err

        return tmp_ret

    def __repr__(self):
        return self.name


class LoopMixin(object):
    min_loop = 0
    min_loop_fail_msg = 'TOO_FEW_SEGMENTS'
    max_loop = sys.maxsize
    max_loop_fail_msg = 'TOO_MANY_SEGMENTS'
    max_loop_fail = False

    def _call(self, tmp_ret, parse_obj, position, **kwargs):

        for wrapper in self.wrappers:
            try:
                wrapper.pre_process(tmp_ret, parse_obj, position + tmp_ret, **kwargs)
            except WrapperStop as err:
                return err.results

        loop_count = 0

        while True:
            tmp_loop = parse_obj.fb(position + tmp_ret)

            try:
                self._parse(tmp_loop, parse_obj, position + tmp_ret, **kwargs)
            except WrapperStop as err:
                break

            if not tmp_loop:
                break
            loop_count += 1
            if loop_count > self.max_loop:
                if self.max_loop_fail:
                    tmp_ret(self.max_loop_fail_msg)
                break
            else:
                tmp_ret += tmp_loop

        if loop_count < self.min_loop:
            tmp_ret(self.min_loop_fail_msg)

        tmp_ret.data['loops'] = loop_count

        if tmp_ret:
            for wrapper in reversed(self.wrappers):
                try:
                    wrapper.post_process(tmp_ret, parse_obj, position + tmp_ret, **kwargs)
                except WrapperStop as err:
                    return err.results

        return tmp_ret


class CharParser(BaseParser):
    look_for = None
    char_until_char = None
    min_char_count = None
    max_char_count = None
    min_char_count_msg = 'SEGMENT_TOO_SHORT'
    caps_sensitive = True

    def _parse(self, tmp_ret, parse_obj, position=0, **kwargs):
        if not parse_obj.at_end(position):
            tmp_item = parse_obj(position, self.look_for,
                                 min_count=self.min_char_count,
                                 max_count=self.max_char_count,
                                 caps_sensitive=self.caps_sensitive,
                                 min_error_msg=self.min_char_count_msg)
            if tmp_item:
                tmp_ret += tmp_item
                return

        raise WrapperStop(self, tmp_ret)


class SingleCharParser(CharParser):
    min_char_count = 1
    max_char_count = 1


class StringParser(CharParser):
    def __init__(self, **kwargs):
        super(StringParser, self).__init__(**kwargs)
        if self.look_for[0] != '"':
            self.look_for = '"' + self.look_for
        if self.look_for[-1] != '"':
            self.look_for += '"'


class SubParsersParser(BaseParser):
    operation = 'and'  # ['and'|'or'|'best']
    parsers = None

    def __init__(self, **kwargs):
        super(SubParsersParser, self).__init__(**kwargs)
        self.parsers = make_list(self.parsers)
        self.operation = getattr(self, '_' + self.operation)

    def _and(self, tmp_ret, parse_obj, position, **kwargs):
        tmp_and = parse_obj.fb(position)
        for p in self.parsers:
            tmp_item = p(parse_obj, position + tmp_and, **kwargs)

            if tmp_item:
                tmp_and += tmp_item
            else:
                raise WrapperStop(self, tmp_ret(tmp_and, set_length=0))
        tmp_ret += tmp_and

    def _or(self, tmp_ret, parse_obj, position, **kwargs):
        for p in self.parsers:
            tmp_item = p(parse_obj, position, **kwargs)
            if tmp_item:
                tmp_ret += tmp_item
                return
        raise WrapperStop(self, tmp_ret)

    def _best(self, tmp_ret, parse_obj, position, **kwargs):
        tmp_best = parse_obj.fb(position)
        for p in self.parsers:
            tmp_item = p(parse_obj, position, **kwargs)
            tmp_best = tmp_best.max(tmp_item)
        if tmp_best:
            tmp_ret += tmp_best
        else:
            raise WrapperStop(self, tmp_ret)

    def _parse(self, tmp_ret, parse_obj, position, **kwargs):
        if parse_obj.at_end(position):
            raise WrapperStop(self, tmp_ret)
        self.operation(tmp_ret, parse_obj, position, **kwargs)

# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  OUTER PARSERS  ">
# **********************************************************************************

class BaseWrapper(object):
    messages = None
    _skip_keys = ('messages', 'pre_process', 'post_process')

    def __init__(self, base_parser):
        self.base_parser = base_parser

        for key in dir(self):
            if key[0] != '_' and key not in self._skip_keys and hasattr(base_parser, key):
                setattr(self, key, getattr(base_parser, key))

    def pre_process(self, tmp_ret, parse_obj, position, **kwargs):
        pass

    def post_process(self, tmp_ret, parse_obj, position, **kwargs):
        pass


class FullLengthWrapper(BaseWrapper):
    not_full_length_msg = 'INVALID_CHAR'

    def post_process(self, tmp_ret, parse_obj, position, **kwargs):
        if parse_obj.at_end(position):
            raise WrapperStop(self, tmp_ret(self.not_full_length_msg))

#
# class PHLoop(BaseWrapper):
#     min_loop = None
#     min_loop_fail_msg = 'TOO_FEW_SEGMENTS'
#     max_loop = None
#     max_loop_fail_msg = 'TOO_MANY_SEGMENTS'
#     max_loop_fail = False
#
#     def parse(self, parse_obj, position=0, **kwargs):
#         loop_count = 0
#         tmp_ret = parse_obj.fb(position)
#
#         min_loop = self.min_loop or 0
#         max_loop = self.max_loop or sys.maxsize
#
#         while True:
#             tmp_loop = super().parse(parse_obj, position + tmp_ret, **kwargs)
#             if not tmp_loop:
#                 break
#             loop_count += 1
#             if loop_count > max_loop:
#                 if self.max_loop_fail:
#                     tmp_ret(self.max_loop_fail_msg)
#                 break
#             else:
#                 tmp_ret += tmp_loop
#
#         if loop_count < min_loop:
#             tmp_ret(self.min_loop_fail_msg)
#
#         tmp_ret.data['loops'] = loop_count
#         return tmp_ret
#
#     def __call__(self, *args, **kwargs):
#         return self.parse(*args, **kwargs)


class InvalidNextWrapper(BaseWrapper):
    invalid_next_char = None
    invalid_next_char_msg = 'INVALID_NEXT_CHAR'

    def post_process(self, tmp_ret, parse_obj, position, **kwargs):
        if not parse_obj.at_end(position) and parse_obj[position] in self.invalid_next_char:
            raise WrapperStop(self, tmp_ret(self.invalid_next_char_msg))


class EnclosedWrapper(BaseWrapper):
    enclosure_start = '"'
    enclosure_end = '"'
    skip_quoted = True
    unclosed_msg = 'UNCLOSED_STRING'

    def pre_process(self, tmp_ret, parse_obj, position, **kwargs):
        if parse_obj.at_end(position) or parse_obj[position] != self.enclosure_start:
            raise WrapperStop(self, tmp_ret)
        tmp_ret(1)

    def post_process(self, tmp_ret, parse_obj, position, **kwargs):
        if parse_obj.at_end(position) or parse_obj[position] != self.enclosure_end:
            raise WrapperStop(self, tmp_ret(self.unclosed_msg))
        tmp_ret(1)


class MinLenWrapper(BaseWrapper):
    min_length = None
    min_length_msg = 'SEGMENT_TOO_SHORT'

    def post_process(self, tmp_ret, parse_obj, position, **kwargs):
        if tmp_ret.l < self.min_length:
            raise WrapperStop(self, tmp_ret(self.min_length_msg))


class MaxLenWrapper(BaseWrapper):
    max_length = None
    max_length_msg = 'SEGMENT_TOO_LONG'

    def post_process(self, tmp_ret, parse_obj, position, **kwargs):
        if tmp_ret.l > self.max_length:
            raise WrapperStop(self, tmp_ret(self.max_length_msg))


class MinMaxLenWrapper(BaseWrapper):
    min_length = None
    min_length_msg = 'SEGMENT_TOO_SHORT'
    max_length = None
    max_length_msg = 'SEGMENT_TOO_LONG'

    def post_process(self, tmp_ret, parse_obj, position, **kwargs):
        if tmp_ret.l > self.max_length:
            raise WrapperStop(self, tmp_ret(self.max_length_msg))
        elif tmp_ret.l < self.min_length:
            raise WrapperStop(self, tmp_ret(self.min_length_msg))


class InvalidStartStopWrapper(BaseWrapper):
    invalid_start_chars = None
    invalid_start_chars_msg = 'INVALID_START'
    invalid_end_chars = None
    invalid_end_chars_msg = 'INVALID_END'

    def pre_process(self, tmp_ret, parse_obj, position, **kwargs):
        if not parse_obj.at_end(position) and parse_obj[position] in self.invalid_start_chars:
            raise WrapperStop(self, tmp_ret(self.invalid_start_chars_msg))

    def post_process(self, tmp_ret, parse_obj, position, **kwargs):
        if not parse_obj.at_end(position) and parse_obj[position] in self.invalid_end_chars:
            raise WrapperStop(self, tmp_ret(self.invalid_end_chars_msg))



# **********************************************************************************
# </editor-fold>
# **********************************************************************************

'''

# **********************************************************************************
# <editor-fold desc="  INNER Parsers  ">
# **********************************************************************************


class PHBase(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                valid_args = list(self.__dict__)
                for v in valid_args:
                    if v[0] == '_':
                        valid_args.remove(v)
                raise AttributeError('Invalid keyword arg: %s, valid args = %r' % (key, valid_args))

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)


class PHBaseChar(PHBase):
    look_for = None
    char_until_char = None
    min_char_count = None
    max_char_count = None
    min_char_count_msg = 'SEGMENT_TOO_SHORT'
    caps_sensitive = True

    def __init__(self, look_for=None, **kwargs):
        self.look_for = look_for or self.look_for
        super(PHBaseChar, self).__init__(**kwargs)

    @classmethod
    def parse(cls, parse_obj, position=0, **kwargs):
        if not parse_obj.at_end(position):
            return parse_obj(position, cls.look_for,
                             min_count=cls.min_char_count,
                             max_count=cls.max_char_count,
                             caps_sensitive=cls.caps_sensitive,
                             min_error_msg=cls.min_char_count_msg)
        else:
            return parse_obj.fb(position)


class PHBaseSingleChar(PHBaseChar):
    min_char_count = 1
    max_char_count = 1


class PHBaseString(PHBaseChar):
    __initialized = False

    def __init__(self, look_for=None, **kwargs):
        self.look_for = look_for or self.look_for
        super(PHBaseString, self).__init__(**kwargs)

    @classmethod
    def __init(cls):
        if not cls.__initialized:
            cls.__initialized = True
            if cls.look_for[0] != '"':
                cls.look_for = '"' + cls.look_for
            if cls.look_for[-1] != '"':
                cls.look_for += '"'

    @classmethod
    def parse(cls, *args, **kwargs):
        cls.__init()
        super(PHBaseString, cls).parse(*args, **kwargs)
        

class PHBaseSubParsers(PHBase):
    operation = 'and'  # ['and'|'or'|'best']
    parsers = None

    def __init__(self, *parsers, operation=None, **kwargs):
        self.parsers = parsers or self.parsers
        self.operation = operation or self.operation
        super(PHBaseSubParsers, self).__init__(**kwargs)

    @staticmethod
    def _and(parse_obj, position=0, *parsers, **kwargs):
        tmp_ret = parse_obj.fb(position)

        for p in parsers:
            tmp_item = p(parse_obj, position + tmp_ret, **kwargs)

            if tmp_item:
                tmp_ret += tmp_item
            else:
                return parse_obj.fb(position)

        return tmp_ret

    @staticmethod
    def _or(parse_obj, position=0, *parsers, **kwargs):
        for p in parsers:
            tmp_item = p(parse_obj, position, **kwargs)
            if tmp_item:
                return tmp_item

        return parse_obj.fb(position)

    @staticmethod
    def _best(parse_obj, position=0, *parsers, **kwargs):

        tmp_best = parse_obj.fb(position)

        for p in parsers:
            tmp_item = p(parse_obj, position, **kwargs)
            tmp_best = tmp_best.max(tmp_item)

        return tmp_best

    @classmethod
    def parse(cls, parse_obj, position=0, **kwargs):
        if cls.operation == 'and':
            return cls._and(parse_obj, position, *make_list(cls.parsers))
        elif cls.operation == 'or':
            return cls._or(parse_obj, position, *make_list(cls.parsers))
        elif cls.operation == 'best':
            return cls._best(parse_obj, position, *make_list(cls.parsers))


class PHBaseSubSegment(PHBase):
    segment = None

    @classmethod
    def parse(cls, *args, **kwargs):
        return cls.segment(*args, **kwargs)


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  OUTER PARSERS  ">
# **********************************************************************************


class PHSegment(object):
    # parser = True
    is_history_item = True
    is_segment_item = True

    _lookups = None
    _parser_segment_defs = None

    name = None
    description = None
    references = None
    messages = None

    on_pass_msg = None  # 'VALID'
    on_fail_msg = None  # 'ERROR'

    # parse_object = ParsingObj
    __initialized = False

    def __init__(self, *args, **kwargs):
        self.__init()
        super(PHSegment, self).__init__(*args, **kwargs)

    @classmethod
    def __init(cls):
        if not cls.__initialized:
            cls.__initialized = True
            cls._lookups = {}

            cls.name = cls.name or cls.__class__.__name__
            cls.on_pass_msg = make_list(cls.on_pass_msg)
            cls.on_fail_msg = make_list(cls.on_fail_msg)
            cls._parser_segment_defs = {}
            if cls.description is not None:
                cls._parser_segment_defs['description'] = cls.description
            if cls.references is not None:
                cls._parser_segment_defs['references'] = cls.references

    @classmethod
    def _update_messages(cls, parser_obj):
        cls.__init()
        if parser_obj.message_lookup.name not in cls._lookups:
            if cls.is_segment_item and cls.name:
                parser_obj.message_lookup.segment(cls.name, **cls._parser_segment_defs)
            if cls.messages is not None:
                parser_obj.message_lookup.add(messages=cls.messages)
            cls._lookups[parser_obj.message_lookup.name] = None

    @classmethod
    def parse(cls, parse_obj, position=0, **kwargs):
        """
        must call:
            cls.super_call(parse_obj, position, **kwargs)
        """
        tmp_err = None
        position = int(position)

        cls._update_messages(parse_obj)

        if cls.is_segment_item:
            parse_obj.begin_stage(cls.name, position=position)

        raise_error = False

        if not parse_obj.at_end(position):
            try:
                tmp_ret = super().parse(parse_obj, position, **kwargs)
            except ParsingError as err:
                tmp_err = err
                raise_error = True
                tmp_ret = err.results
        else:
            tmp_ret = parse_obj.fb(position)

        tmp_ret.set_done(set_history=cls.is_history_item, pass_msg=cls.on_pass_msg, fail_msg=cls.on_fail_msg)

        if cls.is_segment_item:
            parse_obj.end_stage(tmp_ret, raise_error=raise_error)

        if raise_error:
            raise tmp_err

        return tmp_ret

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)


class PHFullLength(object):
    not_full_length_msg = 'INVALID_CHAR'

    @classmethod
    def parse(cls, parse_obj, position=0, *args, **kwargs):
        tmp_ret = super(PHFullLength, cls).parse(parse_obj, position, *args, **kwargs)
        if tmp_ret.l != len(parse_obj):
            tmp_ret(cls.not_full_length_msg)
        return tmp_ret

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)


class PHLoop(object):
    parser = True
    min_loop = None
    min_loop_fail_msg = 'TOO_FEW_SEGMENTS'
    max_loop = None
    max_loop_fail_msg = 'TOO_MANY_SEGMENTS'
    max_loop_fail = False

    @classmethod
    def parse(cls, parse_obj, position=0, **kwargs):
        loop_count = 0
        tmp_ret = parse_obj.fb(position)

        min_loop = cls.min_loop or 0
        max_loop = cls.max_loop or sys.maxsize

        while True:
            tmp_loop = super().parse(parse_obj, position+tmp_ret, **kwargs)
            if not tmp_loop:
                break
            loop_count += 1
            if loop_count > max_loop:
                if cls.max_loop_fail:
                    tmp_ret(cls.max_loop_fail_msg)
                break
            else:
                tmp_ret += tmp_loop

        if loop_count < min_loop:
            tmp_ret(cls.min_loop_fail_msg)

        tmp_ret.data['loops'] = loop_count
        return tmp_ret

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)


class PHInvalidNext(object):
    invalid_next_char = None
    invalid_next_char_msg = 'INVALID_NEXT_CHAR'

    @classmethod
    def parse(cls, parse_obj, position=0, **kwargs):
        tmp_ret = super().parse(parse_obj, position, **kwargs)
        if tmp_ret and not parse_obj.at_end(position + 1) and parse_obj[position + 1] in cls.invalid_next_char:
            tmp_ret(cls.invalid_next_char_msg, set_length=0)
        return tmp_ret

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)


class PHEnclosed(object):
    parser = True
    enclosure_start = '"'
    enclosure_end = '"'
    skip_quoted = True
    unclosed_msg = 'UNCLOSED_STRING'
    __initialized = False

    @classmethod
    def __init(cls):
        if not cls.__initialized:
            cls.__initialized = True
            if not issubclass(cls.enclosure_start.__class__, PHBase):
                cls.enclosure_start = PHBaseSingleChar(cls.enclosure_start)
            if not issubclass(cls.enclosure_end.__class__, PHBase):
                cls.enclosure_end = PHBaseSingleChar(cls.enclosure_end)

    @classmethod
    def parse(cls, parse_obj, position=0, **kwargs):

        tmp_ret = cls.enclosure_start(parse_obj, position)
        if not tmp_ret:
            return parse_obj.fb(position)

        tmp_ret += super().parse(parse_obj, position + tmp_ret, **kwargs)

        tmp_closed = cls.enclosure_end(parse_obj, position + tmp_ret)
        tmp_ret += tmp_closed

        if not tmp_closed:
            tmp_ret(cls.unclosed_msg)
            tmp_ret.set_length(0)

        return tmp_ret

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)


class PHMinLen(object):
    min_length = None
    min_length_msg = 'SEGMENT_TOO_SHORT'

    @classmethod
    def parse(cls, parse_obj, position=0, **kwargs):
        tmp_ret = super().parse(parse_obj, position, **kwargs)
        # print('checking min length (%s v min %s)' % (tmp_ret.l, cls.min_length))
        if tmp_ret.l < cls.min_length:
            # print('%s is smaller than min langth %s' % (tmp_ret.l, cls.min_length))
            tmp_ret(cls.min_length_msg)
            # print(repr(tmp_ret))

        return tmp_ret

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)


class PHMaxLen(object):
    max_length = None
    max_length_msg = 'SEGMENT_TOO_LONG'

    @classmethod
    def parse(cls, parse_obj, position=0, **kwargs):
        tmp_ret = super().parse(parse_obj, position, **kwargs)
        if tmp_ret.l > cls.max_length:
            tmp_ret(cls.max_length_msg)
        return tmp_ret

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)


class PHMinMaxLen(object):
    min_length = None
    min_length_msg = 'SEGMENT_TOO_SHORT'
    max_length = None
    max_length_msg = 'SEGMENT_TOO_LONG'

    @classmethod
    def parse(cls, parse_obj, position=0, **kwargs):
        tmp_ret = super().parse(parse_obj, position, **kwargs)
        if tmp_ret.l > cls.max_length:
            tmp_ret(cls.max_length_msg)
        elif tmp_ret.l < cls.min_length:
            tmp_ret(cls.min_length_msg)

        return tmp_ret

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)


class PHInvalidStartStop(object):
    invalid_start_chars = None
    invlaid_start_chars_msg = 'INVALID_START'
    invalid_end_chars = None
    invlaid_end_chars_msg = 'INVALID_END'

    __initialized = True
    
    @classmethod
    def __init(cls):
        if not cls.__initialized:
            cls.__initialized = True    
            if cls.invalid_start_chars is not None and not issubclass(cls.invalid_start_chars.__class__, PHBase):
                cls.invalid_start_chars = PHBaseChar(cls.invalid_start_chars)
            if cls.invalid_end_chars is not None and not issubclass(cls.invalid_end_chars.__class__, PHBase):
                cls.invalid_end_chars = PHBaseChar(cls.invalid_end_chars)

    @classmethod
    def parse(cls, parse_obj, position=0, **kwargs):
        cls.__init()
        tmp_fail = parse_obj.fb(position)
        tmp_ret = cls.invalid_start_chars(parse_obj, position)
        if tmp_ret:
            return tmp_fail(cls.invlaid_start_chars_msg)

        tmp_ret += super().parse(parse_obj, position + tmp_ret, **kwargs)

        tmp_closed = cls.invalid_end_chars(parse_obj, position + tmp_ret)
        tmp_ret += tmp_closed

        if tmp_closed:
            return tmp_ret(cls.invlaid_end_chars_msg)

        return tmp_ret

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)



# **********************************************************************************
# </editor-fold>
# **********************************************************************************

'''
# **********************************************************************************
# <editor-fold desc="  ShortCutBases  ">
# **********************************************************************************


class CharNoSegment(CharParser):
    inner_parser = CharParser
    is_segment = False
    is_history = False


class StringNoSegment(StringParser):
    inner_parser = StringParser
    is_segment = False
    is_history = False


class SingleCharNoSegment(SingleCharParser):
    inner_parser = SingleCharParser
    is_segment = False
    is_history = False


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


