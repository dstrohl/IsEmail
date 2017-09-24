__all__ = ['BaseParser', 'SingleCharParser', 'CharParser', 'StringParser', 'SubParsersParser',
           'LoopMixin', 'EnclosedWrapper', 'MaxLenWrapper', 'MinLenWrapper', 'InvalidNextWrapper',
           'InvalidStartStopWrapper',
           'FullLengthWrapper', 'MinMaxLenWrapper',
           'CharNoSegment', 'SingleCharNoSegment', 'StringNoSegment'
           ]

from ValidationParser.exceptions import ParsingError, WrapperStop
from helpers.general.general import make_list
import sys


# **********************************************************************************
# <editor-fold desc="  BASE Parsers  ">
# **********************************************************************************

class ConfigObject(object):
    def __init__(self, owner, *args, spec_args=None, auto_spec=True, arg_list=None, skip_keys=None, **kwargs):
        """
        :param owner:
        :param args:
        :param spec_args:  either {'field_name': 'dict'|'list', ...}
        :param auto_spec:
        :param arg_list:
        :param kwargs:
        """
        self._data = {}
        self._owner = owner
        self._spec_args = spec_args or {}
        if skip_keys:
            self._skip_keys = make_list(skip_keys)
        else:
            self._skip_keys = []
        self._auto_spec = auto_spec
        self._arg_list = make_list(arg_list)
        self._load()
        self._update(*args, **kwargs)

    def _load(self, from_obj=None):
        from_obj = from_obj or self._owner
        if from_obj is not None:
            for key in dir(from_obj):
                if key[0] != '_' and key not in self._skip_keys and hasattr(from_obj, key):
                    self._set_field(key, getattr(from_obj, key), self._data, force_set=True)

    def _update(self, *args, force_set=False, _to_data=None, **kwargs):
        _to_data = _to_data or self._data
        for field, arg in zip(self._arg_list, args):
            self._set_field(field, arg, _to_data=_to_data, force_set=force_set)
        if not force_set and (self._auto_spec or self._spec_args):
            for field, value in kwargs.items():
                self._set_field(field, value, _to_data=_to_data)
        else:
            _to_data.update(kwargs)

    def _set(self, *args, **kwargs):
        self._update(*args, force_set=True, **kwargs)

    def _set_field(self, field, value, _to_data, force_set=False):

        if self._auto_spec and field not in _to_data and not force_set:
            if isinstance(value, (list, tuple)):
                self._spec_args[field] = 'list'
                _to_data[field] = []
            elif isinstance(value, dict):
                self._spec_args[field] = 'dict'
                _to_data[field] = {}

        if not force_set and field in self._spec_args:
            if self._spec_args[field] == 'list':
                if isinstance(value, (list, tuple)):
                    _to_data[field].extend(value)
                else:
                    _to_data[field].append(value)
            elif self._spec_args[field] == 'dict':
                _to_data[field].update(value)
            else:
                raise AttributeError('Invalid data type: %s' % self._spec_args[field])
        else:
            _to_data[field] = value

    def _kwargs(self, *args, **kwargs):
        tmp_data = self._data.copy()
        self._update(*args, _to_data=tmp_data, **kwargs)
        return tmp_data

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError('Invalid Attribute: %s' % item)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._set_field(key, value, self._data)

    def __repr__(self):
        return 'ConfigObject(%s)' % ', '.join(self._data.keys())

class BaseParser(object):
    __skip_keys = []
    __arg_list = []
    __spec_args = {'messages': 'list', 'wrappers': 'list', 'references': 'list'}

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
        self._skip_keys = []
        self._arg_list = []
        self._spec_args = []

        self._update_local_fields('BaseParser')

        self.wrappers = make_list(kwargs.pop('wrappers', self.wrappers), force_list=True)
        self.messages = make_list(kwargs.pop('messages', self.messages))

        self.c = ConfigObject(self, *args, arg_list=self._arg_list, spec_args=self._spec_args, skip_keys=self._skip_keys, **kwargs)

        self.name = self.name or self.__class__.__name__
        self.on_pass_msg = make_list(self.on_pass_msg)
        self.on_fail_msg = make_list(self.on_fail_msg)


        # if kwargs:
        #     for key in list(kwargs):
        #         setattr(self, key, kwargs.pop(key) or getattr(self, key))

        self._load_parsers()

        # if self.inner_parser is None:
        #     raise AttributeError('Parser must be defined')

        self._lookups = {}
        self._parser_segment_defs = {}

        if self.description is not None:
            self._parser_segment_defs['description'] = self.c.description
        if self.references is not None:
            self._parser_segment_defs['references'] = self.c.references


    def _update_local_fields(self, obj_name):
        for field_name in ['_strip_keys', '_arg_list', '_spec_args']:
            local_name = '__%s%s' % (obj_name, field_name)
            try:
                local_field = getattr(self, local_name)
            except AttributeError:
                pass
            else:
                if field_name == '_spec_args':
                    getattr(self, field_name).update(local_field)
                else:
                    getattr(self, field_name).extend(local_field)

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

        tmp_ret.data['loop_count'] = loop_count

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
    not_full_length_msg = 'UNPARSED_CONTENT'

    def post_process(self, tmp_ret, parse_obj, position, **kwargs):
        if parse_obj.at_end(position):
            raise WrapperStop(self, tmp_ret(self.not_full_length_msg))



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


