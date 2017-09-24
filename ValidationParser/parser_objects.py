__all__ = ['BaseParser', 'SingleCharParser', 'CharParser', 'StringParser', 'SubParsersParser',
           'EnclosedWrapper', 'MaxLenWrapper', 'MinLenWrapper', 'InvalidNextWrapper',
           'InvalidStartStopWrapper',
           'FullLengthWrapper', 'MinMaxLenWrapper',
           'CharNoSegment', 'SingleCharNoSegment', 'StringNoSegment',
           'register_parser'
           ]

from ValidationParser.exceptions import ParsingLocalError, ParsingFatalError
from ValidationParser.parser_messages import get_message_lookup
from helpers.general.general import make_list
import sys


# **********************************************************************************
# <editor-fold desc="  BASE Parsers  ">
# **********************************************************************************

# def register_parser(message_lookup=None, run_also=None):
#     message_lookup = get_message_lookup(message_lookup)
#     run_this = ['_init'] + make_list(run_also)
#
#     def parse_decorator(cls):
#         for f in run_this:
#             try:
#                 func_2 = getattr(cls, f)
#             except AttributeError:
#                 pass
#             else:
#                 func_2(cls)
#
#         message_lookup.add_parser(cls)
#         return cls
#     return parse_decorator


# def register_parsers(register_item, message_lookup=None):
#     message_lookup = get_message_lookup(message_lookup)
#
#     def register_class(cls):
#         for f in dir(cls):
#             if f.endswith('_init'):
#                 try:
#                     func_2 = getattr(cls, f)
#                 except AttributeError:
#                     pass
#                 else:
#                     func_2(cls)
#
#         message_lookup.add_parser(cls)
#
#     if issubclass(register_item, module):
#         for item in dir(register_item):
#             if issubclass(item, BaseParser):
#                 register_item(item)
#
#     elif issubclass(register_item, BaseParser):
#         register_class(register_item)

def register_parser(cls, message_lookup=None):
    message_lookup = get_message_lookup(message_lookup)
    for f in dir(cls):
        if f.endswith('_init'):
            try:
                func_2 = getattr(cls, f)
            except AttributeError:
                pass
            else:
                func_2()
    message_lookup.add_parser(cls)
    return cls

# class MetaInitLaunch(type):
#     def __new__(cls, name, bases, dct):
#         tmp_ret = type.__new__(cls, name, bases, dct)
#         try:
#             if not tmp_ret.name:
#                 tmp_ret.name = name
#         except AttributeError:
#             tmp_ret.name = name
#         for key in dir(tmp_ret):
#             if key.endswith('_init'):
#                 tmp_func = getattr(tmp_ret, key)
#                 tmp_func(tmp_ret)
#         return tmp_ret


class KwargsOverride(object):
    def __init__(self, parent, *kwargs):
        self._parent = [parent]
        self._data = {}

        self._set_kwargs(*kwargs)

    def _set_kwargs(self, *kwargs, clear=True, save_none=False):
        if clear:
            self._data.clear()
        for k in kwargs:
            for key, item in k.items():
                if save_none or item is not None:
                    self._data[key] = item

    @property
    def _kwargs(self):
        return self._data

    def _push(self, parent):
        self._parent.append(parent)
    
    def _pop(self):
        self._parent.pop()

    def _get_item(self, key):
        try:
            return self._data[key]
        except KeyError:
            for p in self._parent:
                try:
                    return getattr(p, key)
                except AttributeError:
                    continue
        raise AttributeError('Attribute Error, could not find: %s' % key)

    def __getattr__(self, item):
        return self._get_item(item)

    def __getitem__(self, item):
        return self._get_item(item)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, item):
        return item in self._data


class BaseParser(object):  #  metaclass=MetaInitLaunch):
    # _meta_keys = ('_skip_keys', '_args_list')
    # _skip_keys = []
    # _args_list = []

    _lookups = None
    _parser_segment_defs = None
    wrappers = None
    is_history = True
    is_segment = True

    name = None
    description = None
    references = None
    messages = None

    on_pass_msg = None  # 'VALID'
    on_fail_msg = None  # 'ERROR'

    min_loop = 0
    min_loop_fail_msg = 'TOO_FEW_SEGMENTS'
    max_loop = 0
    max_loop_fail_msg = 'TOO_MANY_SEGMENTS'
    max_loop_fail = False

    raise_error = False
    should_loop = False

    has_pre_wrappers = False
    has_post_wrappers = False

    initialized = False

    @classmethod
    def _init(cls):
        cls.initialized = True
        cls.wrappers = make_list(cls.wrappers, force_list=True)
        cls.reversed_wrappers = reversed(cls.wrappers)
        cls.messages = make_list(cls.messages)

        cls.name = cls.name or cls.__class__.__name__
        cls.on_pass_msg = make_list(cls.on_pass_msg)
        cls.on_fail_msg = make_list(cls.on_fail_msg)

        if cls.max_loop is None:
            cls.max_loop = sys.maxsize
        if cls.max_loop > 0:
            cls.should_loop = True

        # if kwargs:
        #     for key in list(kwargs):
        #         setattr(cls, key, kwargs.pop(key) or getattr(cls, key))

        for wrapper in cls.wrappers:
            if wrapper.messages:
                cls.messages.extend(make_list(wrapper.messages))
            if wrapper.has_pre:
                cls.has_pre_wrappers = True
            if wrapper.has_post:
                cls.has_post_wrappers = True

        cls._lookups = {}
        cls._parser_segment_defs = {}

        if cls.description is not None:
            cls._parser_segment_defs['description'] = cls.description
        if cls.references is not None:
            cls._parser_segment_defs['references'] = cls.references

        # cls._subinit()
        
    # @classmethod
    # def _subinit(cls):
    #     pass

    @classmethod
    def _update_messages(cls, parser_obj, config):
        if parser_obj.message_lookup.name not in cls._lookups:
            if config.is_segment and config.name:
                parser_obj.message_lookup.segment(config.name, **cls._parser_segment_defs)
            if config.messages is not None:
                parser_obj.message_lookup.add(messages=config.messages)
            cls._lookups[parser_obj.message_lookup.name] = None

    @classmethod
    def _loop_parse(cls, parse_obj, position, config):
        loop_count = 0
        loop_stage = parse_obj.begin_stage('loop', position=position)
        football = parse_obj.fb(position)
        if parse_obj.at_end(position + football):
            return football('END_OF_STRING')

        while True:
            tmp_loop = cls._parse(parse_obj, position + football, config)

            if not parse_obj.is_ok(tmp_loop):
                break

            loop_count += 1

            if loop_count > config.max_loop:
                if config.max_loop_fail:
                    football(config.max_loop_fail_msg)
                break
            else:
                football += tmp_loop

            if parse_obj.at_end(position + football):
                break

        if loop_count < config.min_loop:
            football(config.min_loop_fail_msg)

        parse_obj.end_stage(football, raise_error=False, stage_id=loop_stage)
        football.data['loop_count'] = loop_count

        return football

    @classmethod
    def _parse(cls, parse_obj, position, config):
        return parse_obj.fb(position)

    @classmethod
    def run(cls, parse_obj, position=0, **kwargs):
        if not cls.initialized:
            cls._init()
        config = KwargsOverride(cls, kwargs)
        cls._update_messages(parse_obj, config)
        segment_stage = None
        if config.is_segment:
            segment_stage = parse_obj.begin_stage(config.name, position=position)

        tmp_ret = cls._run(parse_obj, position, config)

        parse_obj.end_stage(tmp_ret, stage_id=segment_stage)

        tmp_ret.set_done(set_history=config.is_history, pass_msg=config.on_pass_msg, fail_msg=config.on_fail_msg)

        return tmp_ret

    @classmethod
    def _run(cls, parse_obj, position, config):
        tmp_err = None

        football = parse_obj.fb(position, is_history=config.is_history)

        if parse_obj.at_end(position):
            return football('END_OF_STRING')

        # *********** pre wrapper processing **************************
        if config.has_pre_wrappers:
            pre_wrap_stage = parse_obj.begin_stage('pre-parse wrappers', position=position + football)
            for wrapper in config.wrappers:
                if wrapper.has_pre:
                    tmp_loop = wrapper.pre_process(parse_obj, position + football, config)
                    football += tmp_loop
                    if not parse_obj.is_ok(tmp_loop):
                        parse_obj.end_stage(football, raise_error=(tmp_err is not None and config.raise_error))
                        return football

            parse_obj.end_stage(football, stage_id=pre_wrap_stage, raise_error=False)

        # *********** main processing **************************
        main_stage = None
        if cls.wrappers:
            main_stage = parse_obj.begin_stage('wrapped parse', position=position + football)

        if config.should_loop:
            main_fb = cls._loop_parse(parse_obj, position + football, config)
        else:
            main_fb = cls._parse(parse_obj, position + football, config)
        football += main_fb

        if cls.wrappers:
            parse_obj.end_stage(football, stage_id=main_stage)

        if not parse_obj.is_ok(main_stage):
            return football

        # *********** pre wrapper processing **************************
        if config.has_post_wrappers:
            post_wrap_stage = parse_obj.begin_stage('post-parse wrappers', position=position + football)

            for wrapper in reversed(config.wrappers):
                if wrapper.has_post:
                    tmp_loop = wrapper.post_process(parse_obj, position + football, config)
                    football += tmp_loop
                    if not parse_obj.is_ok(tmp_loop):
                        return football
            parse_obj.end_stage(football, stage_id=post_wrap_stage)

        return football
    
    @classmethod
    def __repr__(cls):
        return cls.name


# class LoopMixin(object):
#     min_loop = 0
#     min_loop_fail_msg = 'TOO_FEW_SEGMENTS'
#     max_loop = sys.maxsize
#     max_loop_fail_msg = 'TOO_MANY_SEGMENTS'
#     max_loop_fail = False
#
#     def _call(self, tmp_ret, parse_obj, position, **kwargs):
#
#         for wrapper in self.wrappers:
#             try:
#                 wrapper.pre_process(tmp_ret, parse_obj, position + tmp_ret, **kwargs)
#             except WrapperStop as err:
#                 return err.results
#
#
#         if tmp_ret:
#             for wrapper in reversed(self.wrappers):
#                 try:
#                     wrapper.post_process(tmp_ret, parse_obj, position + tmp_ret, **kwargs)
#                 except WrapperStop as err:
#                     return err.results
#
#         return tmp_ret

@register_parser
class CharParser(BaseParser):
    look_for = None
    char_until_char = None
    min_char_count = None
    max_char_count = None
    min_char_count_msg = 'SEGMENT_TOO_SHORT'
    caps_sensitive = True

    @classmethod
    def _parse(cls, parse_obj, position, config):
        if parse_obj.at_end(position):
            return 'END_OF_STRING'

        return parse_obj.next_char_in(position, config.look_for,
                                      min_count=config.min_char_count,
                                      max_count=config.max_char_count,
                                      caps_sensitive=config.caps_sensitive,
                                      min_error_msg=config.min_char_count_msg)


@register_parser
class SingleCharParser(BaseParser):
    look_for = None
    caps_sensitive = True

    @classmethod
    def _parse(cls, parse_obj, position, config):
        if parse_obj.at_end(position):
            return 'END_OF_STRING'

        return parse_obj.next_1_char_in(position, config.look_for,
                                        caps_sensitive=config.caps_sensitive)


@register_parser
class StringParser(BaseParser):
    look_for = None
    caps_sensitive = True

    @classmethod
    def _parse(cls, parse_obj, position, config):
        if parse_obj.at_end(position):
            return 'END_OF_STRING'

        return parse_obj.next_string_in(position, config.look_for,
                                        min_count=config.min_char_count,
                                        max_count=config.max_char_count,
                                        caps_sensitive=config.caps_sensitive,
                                        min_error_msg=config.min_char_count_msg)


@register_parser
class SubParsersParser(BaseParser):
    operation = 'and'  # ['and'|'or'|'best']
    parsers = None

    @classmethod
    def _subinit(cls):
        # super(SubParsersParser, cls).__init__(**kwargs)
        cls.parsers = make_list(cls.parsers)
        cls._operation = getattr(cls, '_' + cls.operation)

    @staticmethod
    def _and(parse_obj, position, config):
        tmp_and = parse_obj.fb(position)

        for p in config.parsers:
            tmp_item = p.run(parse_obj, position + tmp_and, **config._kwargs)
            if parse_obj.is_ok(tmp_item):
                tmp_and += tmp_item
            else:
                return None
        return tmp_and

    @staticmethod
    def _or(parse_obj, position, config):
        for p in config.parsers:
            tmp_item = p.run(parse_obj, position, **config._kwargs)
            if parse_obj.is_ok(tmp_item):
                return tmp_item
        return None

    @staticmethod
    def _best(parse_obj, position, config):
        tmp_best = parse_obj.fb(position)
        for p in config.parsers:
            tmp_item = p.run(parse_obj, position, **config._kwargs)
            tmp_best = tmp_best.max(tmp_item)
        return tmp_best

    @classmethod
    def _parse(cls, parse_obj, position, config):
        op_stage = parse_obj.begin_stage(cls.operation, position=position)
        tmp_ret = cls._operation(parse_obj, position, config)
        parse_obj.end_stage(tmp_ret, stage_id=op_stage)
        return tmp_ret

# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  OUTER PARSERS  ">
# **********************************************************************************

class BaseWrapper(object):
    messages = None
    references = None
    has_pre = False
    has_post = False
    # _skip_keys = ('messages', 'pre_process', 'post_process')

    @classmethod
    def pre_process(cls, parse_obj, position, config):
        if cls.has_pre:
            config._push(cls)
            pre_wrap = parse_obj.begin_stage(cls.__name__+'-PRE', position=position)
            tmp_ret = cls._pre_process(parse_obj, position, config)
            parse_obj.end_stage(tmp_ret, False, stage_id=pre_wrap)
            config._pop()
            return tmp_ret
        return True

    @classmethod
    def _pre_process(cls, parse_obj, position, config):
        return None

    @classmethod
    def post_process(cls, parse_obj, position, config):
        if cls.has_post:
            config._push(cls)
            post_wrap = parse_obj.begin_stage(cls.__name__+'-POST', position=position)
            tmp_ret = cls._post_process(parse_obj, position, config)
            parse_obj.end_stage(tmp_ret, False, stage_id=post_wrap)
            config._pop()
            return tmp_ret
        return True

    @classmethod
    def _post_process(cls, parse_obj, position, config):
        return None


class FullLengthWrapper(BaseWrapper):
    not_full_length_msg = 'UNPARSED_CONTENT'
    has_post = True

    @classmethod
    def _post_process(cls, parse_obj, position, config):
        if not parse_obj.at_end(position):
            return config.not_full_length_msg
        return True


class InvalidNextWrapper(BaseWrapper):
    invalid_next_char = None
    invalid_next_char_msg = 'INVALID_NEXT_CHAR'
    has_post = True

    @classmethod
    def _post_process(cls, parse_obj, position, config):
        if not parse_obj.at_end(position) and parse_obj[position] in config.invalid_next_char:
            return config.invalid_next_char_msg
        return True


class EnclosedWrapper(BaseWrapper):
    enclosure_start = '"'
    enclosure_end = '"'
    skip_quoted = True
    unopened_msg = 'UNOPENED_ENCLOSURE'
    unclosed_msg = 'UNCLOSED_ENCLOSURE'
    has_pre = True
    has_post = True

    @classmethod
    def _pre_process(cls, parse_obj, position, config):
        if parse_obj.at_end(position) or parse_obj[position] != config.enclosure_start:
            return config.unopened_msg
        return len(config.enclosure_start)

    @classmethod
    def _post_process(cls, parse_obj, position, config):
        if parse_obj.at_end(position) or parse_obj[position] != config.enclosure_end:
            return config.unclosed_msg
        return len(config.enclosure_end)


class MinLenWrapper(BaseWrapper):
    min_length = None
    min_length_msg = 'SEGMENT_TOO_SHORT'
    has_post = True

    @classmethod
    def _post_process(cls, parse_obj, position, config):
        if position < config.min_length:
            return config.min_length_msg
        return True


class MaxLenWrapper(BaseWrapper):
    max_length = None
    max_length_msg = 'SEGMENT_TOO_LONG'
    has_post = True

    @classmethod
    def _post_process(cls, parse_obj, position, config):
        if position > config.max_length:
            return config.max_length_msg
        return True


class MinMaxLenWrapper(BaseWrapper):
    min_length = None
    min_length_msg = 'SEGMENT_TOO_SHORT'
    max_length = None
    max_length_msg = 'SEGMENT_TOO_LONG'
    has_post = True

    @classmethod
    def _post_process(cls, parse_obj, position, config):
        if position > config.max_length:
            return config.max_length_msg
        elif position < config.min_length:
            return config.min_length_msg
        return True


class InvalidStartStopWrapper(BaseWrapper):
    invalid_start_chars = None
    invalid_start_chars_msg = 'INVALID_START'
    invalid_end_chars = None
    invalid_end_chars_msg = 'INVALID_END'
    has_pre = True
    has_post = True

    @classmethod
    def _pre_process(cls, parse_obj, position, config):
        if config.invalid_start_chars:
            if not parse_obj.at_end(position) and parse_obj[position] in config.invalid_start_chars:
                return config.invalid_start_chars_msg
        return True

    @classmethod
    def _post_process(cls, parse_obj, position, config):
        if config.invalid_end_chars:
            if not parse_obj.at_end(position) and parse_obj[position] in config.invalid_end_chars:
                return config.invalid_end_chars_msg
        return True

# **********************************************************************************
# </editor-fold>
# **********************************************************************************
# **********************************************************************************
# <editor-fold desc="  ShortCutBases  ">
# **********************************************************************************


# @register_parser
class CharNoSegment(CharParser):
    is_segment = False
    is_history = False


# @register_parser
class StringNoSegment(StringParser):
    is_segment = False
    is_history = False


# @register_parser
class SingleCharNoSegment(SingleCharParser):
    is_segment = False
    is_history = False


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


