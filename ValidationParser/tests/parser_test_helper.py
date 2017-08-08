from ValidationParser.parser import parse, RETURN_TYPE_LOOKUP
from ValidationParser.footballs import RESULT_CODES, ParsingObj
from helpers.general import _UNSET, make_list, copy_none


__all__ = ['ParserTestItem', 'ParserTests']


PARSER_TEST_ITEM_DEFS = dict(
    test_id=None,  # required
    skip=False,
    parse_script=parse,
    parse_all=False,
    parse_script_kwargs={},
    parse_script_parser=None,  # required
    parse_return_type='short',  # [bool, short, long]
    
    parse_string=None,  # required
    parse_kwargs={},
    
    # return values
    parsed_string=None,  # defaults to parse_str if None
    parsed_string_len=0,        # either the string PR the qty can be passed.
                          # if set to 0 will also set the status to ERROR
    contains_parsers=None,  # ['parser_1', 'parser_2'],
    
    status=RESULT_CODES.OK,  # or other result codes
    
    history_str=None,
    history_level=None,
    
    max_message=None,  # 'segment.message'
    messages=None,  # [(segment, message), (segment, (message, message))]
    data=None)

STATUS_LOOKUP = dict(
    w = RESULT_CODES.WARNING,
    e = RESULT_CODES.ERROR,
    o = RESULT_CODES.OK)

class ParserTestItem(object):
    def __init__(self, params, default_kwargs=None):
        """
        :param args: [test_id, parse_str, parsed_str_len, history_str, messages, kwargs]

            [test_id, parse_str,
            parsed_str_len   # (first int),
            history_str,
            messages,   # (first list)
            status,  # first RESULT_CODE
            kwargs    # first dict)
        :param kwargs:

        If parsed_string and parsed_string_len are both empty, we assume a passed test for the full length

        """
        self.skip = False
        self.test_id = None  # required
        self.parse_script = parse
        self.parse_all = False
        self.parse_script_kwargs = dict(
            def_pass_msg=None,
            def_fail_msg=None,
            def_empty_msg=None,
            def_unparsed_content_msg=None)

        self.parse_script_parser = None  # required
        self.parse_return_type = 'long'  # [bool, short, long]

        self.parse_string = None  # required
        self.parse_kwargs = {}

        # return values
        self.parsed_string = None      # defaults to parse_str if None
        self.parsed_string_len = None  # defauls to 0 if unset

        self.contains_parsers = None  # ['parser_1', 'parser_2'],

        self.status = _UNSET  # or other result codes

        self.history_str = None
        self.history_level = None

        self.max_message = None  # 'segment.message'
        self.messages = None  # [(segment, message), (segment, (message, message))]
        self.data = None

        if default_kwargs is not None:
            self.update(default_kwargs)

        if isinstance(params, dict):
            self.update(params)
        else:
            params = make_list(params, force_list=True)
            string_order = ['parse_string', 'history_str']
            string_order.reverse()
            param_dict = {}
            for param in params:
                if 'test_id' not in param_dict:
                    param_dict['test_id'] = param
                elif isinstance(param, str):
                    if param in ['w', 'e', 'o']:
                        param_dict['status'] = STATUS_LOOKUP[param]
                    elif string_order:
                        if param == '!':
                            param_dict['skip'] = False
                        else:
                            param_dict[string_order.pop()] = param
                elif isinstance(param, dict):
                    param_dict.update(param)
                elif isinstance(param, (list, tuple)):
                    param_dict['messages'] = param
                elif isinstance(param, int):
                    param_dict['parsed_string_len'] = param
                else:
                    raise AttributeError('Invalid Argument: %r' % param)
            self.update(param_dict)

        if self.parsed_string_len is None:
            if self.parsed_string is None:
                self.parsed_string = self.parse_string
                self.parsed_string_len = len(self.parse_string)
            else:
                self.parsed_string_len = len(self.parsed_string)
        else:
            if self.parsed_string is None:
                self.parsed_string = self.parse_string[:self.parsed_string_len]
            else:
                self.parsed_string_len = len(self.parsed_string)

        if self.status is _UNSET:
            if self.parsed_string_len:
                self.status = RESULT_CODES.OK
            else:
                self.status = RESULT_CODES.ERROR

        self._split_messages()

        # holding vars
        self._football = _UNSET
        self._parsing_obj = _UNSET

    def copy(self, **kwargs):
        tmp_kwargs = dict(
            test_id=self.test_id,  # required
            parse_script=self.parse_script,
            skip=self.skip,
            parse_all=self.parse_all,
            parse_script_kwargs=copy_none(self.parse_script_kwargs),
            parse_script_parser=self.parse_script_parser,  # required
            parse_return_type=self.parse_return_type,  # [bool, short, long]
            parse_string=self.parse_string,  # required
            parse_kwargs=self.parse_kwargs,
            parsed_string=self.parsed_string,  # defaults to parse_str if None
            contains_parsers=self.contains_parsers,  # ['parser_1', 'parser_2'],
            status=self.status,  # or other result codes
            history_str=self.history_str,
            history_level=self.history_level,
            max_message=self.max_message,  # 'segment.message'
            messages=copy_none(self.messages),  # [(segment, message), (segment, (message, message))]
            data=copy_none(self.data))
        tmp_kwargs.update(kwargs)
        return self.__class__(tmp_kwargs)

    def update(self, kwargs):
        for key, value in kwargs.items():
            if key == 'test_id' and self.test_id is not None:
                self.test_id += value
            elif key == 'parse_all':
                if not value:
                    self.parse_script_kwargs['def_unparsed_content_msg'] = None
            else:
                if not hasattr(self, key):
                    raise AttributeError('Attribute %s does not exist in ParseTestItem' % key)
                if isinstance(value, dict):
                    tmp_item = getattr(self, key)
                    if not isinstance(tmp_item, dict):
                        setattr(self, key, value)
                    else:
                        tmp_item.update(value)
                else:
                    setattr(self, key, value)

    def _split_messages(self):
        if self.messages is not None:
            tmp_msgs = []

            if isinstance(self.messages, str):
                if '.' not in self.messages:
                    msg = '*.' + self.messages
                    tmp_msgs.append(msg)
                else:
                    tmp_msgs.append(self.messages)
            else:
                for msg in self.messages:
                    if isinstance(msg, str):
                        if '.' not in msg:
                            msg = '*.' + msg
                        tmp_msgs.append(msg)
                    else:
                        if isinstance(msg[1], str):
                            tmp_msgs.append('%s.%s' % (msg[0], msg[1]))
                        else:
                            for m in msg[1]:
                                tmp_msgs.append('%s.%s' % (msg[0], m))
            self.messages = tmp_msgs

    @property
    def parsing_obj(self):
        if self._parsing_obj is _UNSET:
            self._parsing_obj = ParsingObj(self.parse_string, **self.parse_kwargs)
        return self._parsing_obj

    @property
    def football(self):
        if self._football is _UNSET:
            if self.parse_script_parser is None:
                self._football = self.parse_script(self.parsing_obj, return_type='football', **self.parse_script_kwargs)
            else:
                self._football = self.parse_script(self.parsing_obj, self.parse_script_parser, return_type='football', **self.parse_script_kwargs)
        return self._football

    @property
    def trace(self):
        return str(self.parsing_obj.trace)

    @property
    def test_name(self):
        return '%s - %s - %r - %s' % (self.test_id, self.parse_string, self.parse_script_parser, self.parse_return_type)

    def _make_msg(self, name, expected, returned):
        return '%s:\n    Expected: %r\n    Returned: %r' % (name, expected, returned)

    def _test_item(self, name, expected_item, returned_item, ret_list, old_answ=True):
        if expected_item is not None and expected_item != returned_item:
            ret_list.append(self._make_msg(name, expected=expected_item, returned=returned_item))
            return False
        return old_answ

    def _test_data_item(self, test_ret, ret_list, old_answ=True):
        if self.data is not None:
            for key, value in self.data.items():
                if key in test_ret.data:
                    old_answ = self._test_item(
                        'data-'+key,
                        value,
                        test_ret.data[key],
                        ret_list=ret_list,
                        old_answ=old_answ)
                else:
                    ret_list.append(self._make_msg('data-'+key, value, '-- KEY NOT PRESENT --'))
                    old_answ = False
        return old_answ

    @staticmethod
    def _test_list_item(name, expected_list, returned_list, ret_list, old_answ=True):
        if expected_list is None:
            return old_answ
        else:
            expected_list = expected_list.copy()
            returned_list = returned_list.copy()
            expected_items = list(range(len(expected_list)))
            skip_extra = False

            for index in reversed(expected_items):
                expected_item = expected_list[index]
                if isinstance(expected_item, str) and expected_item == '*':
                    skip_extra = True
                else:
                    try:
                        other_index = returned_list.index(expected_item)
                    except ValueError:
                        pass
                    else:
                        returned_list.remove(expected_item)
                        expected_list.remove(expected_item)

            if skip_extra:
                returned_list.clear()
            else:
                returned_items = list(range(len(returned_list)))
                for index in reversed(returned_items):
                    try:
                        other_index = expected_list.index(returned_list[index])
                        expected_list.remove(returned_list[index])
                        returned_list.remove(returned_list[index])
                    except ValueError:
                        pass

            if expected_list or returned_list:
                tmp_ret = [name+':']
                old_answ = False
                for item in expected_list:
                    tmp_ret.append('    Missing: %r' % item)
                for item in returned_list:
                    tmp_ret.append('    Extra:   %r' % item)
                tmp_ret = '\n'.join(tmp_ret)
                ret_list.append(tmp_ret)

            return old_answ

    def _test_bool_ret(self, test_return, ret_list, old_answ=True):
        old_answ = self._test_item('Bool Check', self.status != RESULT_CODES.ERROR, bool(test_return), ret_list, old_answ=old_answ)
        return old_answ

    def _test_short_ret(self, test_return, ret_list, old_answ=True):
        passed = old_answ
        passed = self._test_item('Parse Str Check', self.parse_string, test_return.parse_str, ret_list, old_answ=passed)
        passed = self._test_item('Parsed Str Check', self.parsed_string, test_return.parsed_str, ret_list, old_answ=passed)

        passed = self._test_item('Status Check', self.status, test_return.status, ret_list, old_answ=passed)
        passed = self._test_item('History Check', self.history_str, test_return.history_str, ret_list, old_answ=passed)
        if test_return.max_message is None:
            test_max_msg = None
        else:
            test_max_msg = test_return.max_message.key
        passed = self._test_item('Max Message Check', self.max_message, test_max_msg, ret_list, old_answ=passed)
        return passed

    def _test_long_ret(self, test_return, ret_list, old_answ=True):
        passed = old_answ
        
        passed = self._test_data_item(test_return, ret_list, old_answ=passed)
        passed = self._test_list_item('Messages Check',
                                      self.messages,
                                      test_return.messages.keys(inc_message_key=False, inc_segment_key=False),
                                      ret_list,
                                      old_answ=passed)

        return passed

    def _wrap_test(self, ret_list):
        tmp_ret = ['\n\nFAILED Test [%s]\n%s' % (self, ''.ljust(80, '*'))]
        tmp_ret.extend(ret_list)
        tmp_ret.append('\n\nTRACE:\n%s\n%s\n' % (''.ljust(80, '*'), self.trace))
        
        tmp_ret = '\n'.join(tmp_ret)
        
        return tmp_ret
    
    def __call__(self, **kwargs):
        self.update(kwargs)
        
        tmp_ret = []
        passed = True
        
        test_return_obj = RETURN_TYPE_LOOKUP[self.parse_return_type]
        
        test_ret = test_return_obj(self.football)

        passed = self._test_bool_ret(test_ret, tmp_ret, passed)                        
        
        if self.parse_return_type in ['short', 'long']:
            passed = self._test_short_ret(test_ret, tmp_ret, passed)                        

        if self.parse_return_type == 'long':
            passed = self._test_long_ret(test_ret, tmp_ret, passed)

        if passed:
            return True, None
        else:
            return False, self._wrap_test(tmp_ret)
        
    def __str__(self):
        return self.test_name


class LimitedTestFail(object):
    def __init__(self, test_name=None):
        self.test_name = test_name

    def __call__(self, *args, **kwargs):
        return False, str(self)

    def __str__(self):
        if self.test_name is None:
            return 'Limited Test'
        else:
            return 'Test limited to: %s' % self.test_name

class ParserTests(object):
    
    def __init__(self, tests, **default_kwargs):
        self.default_kwargs = default_kwargs
        self.tests = []
        for test in tests:
            tmp_defaults = default_kwargs.copy()
            if isinstance(test, dict):
                tmp_defaults.update(test.pop('default', {}))

            tmp_test = ParserTestItem(test, tmp_defaults)

            if tmp_test.parse_return_type == 'all':
                for t in ['bool', 'short', 'long']:
                    tmp_new_test = tmp_test.copy(parse_return_type=t)
                    self.tests.append(tmp_new_test)
            else:
                self.tests.append(tmp_test)

    def items(self, limit_to=None, limit_ret_type=None):
        skipped_items = limit_to
        tests_ran = 0
        tests_skipped = 0
        # if self.default_kwargs.get('skip', False):
        #     skipped_items = 'Limited by "skip" argument'
        #     for item in self.tests:
        #         if item.skip:
        #             tests_skipped += 1
        #         else:
        #             tests_ran += 1
        #             yield item
        # else:
        for item in self.tests:
            test_ran = False
            if limit_to is None or item.test_id == limit_to:
                if not item.skip:
                    if limit_ret_type is None or item.parse_return_type == limit_ret_type:
                        tests_ran += 1
                        test_ran = True
                        yield item
            if not test_ran:
                if skipped_items is None:
                    skipped_items = 'Limited by "skip" argument'
                tests_skipped += 1

        if tests_skipped:
            if limit_ret_type is not None:
                if skipped_items is None:
                    skipped_items = '%s' % limit_ret_type
                else:
                    skipped_items += ' - %s' % limit_ret_type

            yield LimitedTestFail(str(skipped_items) + ' (%s Ran / %s Skipped)' % (tests_ran, tests_skipped))

    def __iter__(self):
        for test in self.tests:
            yield test
            
