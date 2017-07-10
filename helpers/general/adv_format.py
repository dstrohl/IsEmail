from string import Formatter, _string

__all__ = ['AdvFormatter', 'DEF_STR', 'adv_format']


DEF_STR = '__default_str__'
RECURSION_LIST = '__adv_fmt_recursion_list__'
OPTIONAL_ENCLOSURES = '__optional_enclosures__'
REPLACEMENT_ENTITIES = dict(
    coln=":",
    bang="!",
    ocb="{",
    ccb="}",
    hash="#",
)


class AdvFormatter(Formatter):
    """
    adds additional formatting options:
        {? <format_string> <format_string>?} = will only produce any text if the internal formatted object(s) produce content.
            use "<" and ">" as replacements for the "{" and "}".
            Some characters can cause challenges since they are used in format scripts, these can be escaped by using html
            entity like replacement codes:
                &coln; = ":"
                &bang; = "!"
                &ocb; = "{"
                &ccb; = "}"
                &hash; = "#"


        {<field>&<join_string>!l} = adds a conversion type that will join a iterable with the following join string.

        conversion type of "S", which will replace None with ''

        __default_str__="a_default_string" can be passed as a kwarg, if so, will replace any failed lookup with this string.
            if "{}" in the default_str, this will be replaced with the failed field name.

        fields can also be passed within the fields thereby creating a recursive lookup.

    Examples:
        
    Using a default string for lookup fail
        >>> adv_format('Test {} {}', __default_str__='foobar')
        >>> 'Test foobar foobar'

        Note: If you include "{}" in the default string, the failed lookup string will be included
        >>> adv_format('Test {} {}', 'Case', __default_str__='foobar-{}')
        >>> 'Test Case foobar-1'

        >>> adv_format('Test {0} {1}', 'Case', __default_str__='foobar-{}')
        >>> 'Test Case foobar-1'

        >>> adv_format('Test {d}', c='Case', __default_str__='foobar[{}]')
        >>> 'Test foobar[d]'

        Note: you can format the default string using the format spec,
              however this may fail if the expected return is of a different type from the default str.
        >>> adv_format('Test {d:.>15} {e:.<15}', c='Case', __default_str__='foobar')
        >>> 'Test .........foobar foobar.........'

    Joining a string before formatting using the "l" conversion. (The join string defaults to " ")
        >>> adv_format('Test {!l}', ['Case', 'foobar'])
        >>> 'Test Case foobar'

        Note, If you include a "&" before the "!", everything between the "&" and the "!" will be used as a join string.
        >>> adv_format('Test {c&, !l}', c=['Case', 'snafu'])
        >>> 'Test Case, snafu'

        Note: This shows using a join string of "".
        >>> adv_format('Test {&!l} {}', ['Case', 'snafu'], __default_str__='foobar')
        >>> 'Test Casesnafu foobar'

        Note: you can also use a "\n" as a join string.
        >>> adv_format('Test {&\n!l}', ['Case', 'snafu'], __default_str__='foobar')
        >>> 'Test Case\nsnafu'

        Note: You can still provide a format spec for the resulting string.
        >>> adv_format('Test {!l:>20}', ['Case', 'snafu'], __default_str__='foobar')
        >>> 'Test           Case snafu'

    Providing a block of replacements that will not return if the fields are blank.
        This allows you to have characters that will only show if there are fields to include.
        For the internal format string, replace the "{" and "}" with "<" and ">".

        >>> adv_format('Test{? <c>?} foobar', c='Case')
        >>> 'Test Case foobar'

        You can see here that the extra space was not included in the returned string.
        >>> adv_format('Test{? <c>?} foobar', c='')
        >>> 'Test foobar'

        Note: if ANY of the internal fields are returned, the full string is returned.
        >>> adv_format('Test{? <c><d>?} {f}', c='Case', d='', f='foobar')
        >>> 'Test Case foobar'

        Note: you can also change the optional enclosures by including new ones in the kwargs.
            This can be helpfull if you wish to use the '<' or '>' in the format_spec
        >>> adv_format('Test{? [][]?} {}', '', '', 'foobar', __optional_enclosures__='[]')
        >>> 'Test foobar'

        Note: you can also pass the optional enclosures with a set of strings if you wish to use more than one char.
        >>> adv_format('Test{? %start%c%end%%start%d%end%?} {f}', c='Case', d='', f='foobar', __optional_enclosures__=('%start%', '%end%'))
        >>> 'Test Case foobar'


    Include data in fields (recursive formatting).
        >>> adv_format('Test {c}', c='Case')
        >>> 'Test Case'

        Note: you can also recurse multiple levels (up to 20).
        >>> adv_format('Test {c}', c='{d}', d='Case')
        >>> 'Test Case'

        >>> adv_format('Test {c}', c='{e}', d='Case', e='{d}')
        >>> 'Test Case'

        >>> adv_format('{a}', a='{b} {c}', b='Test', c='{e}', d='Case', e='{d}')
        >>> 'Test Case'

        Note: using blank fields does work in the main format string, but will NOT work in the passed fields.
            This will raise an RecursionError containing a list of the recursed objects.
        >>> adv_format('{}', '{b} {c}', b='Test', c='{e}', d='Case', e='{d}')
        >>> 'Test Case'

        Note: you can use integer offset based fields in the passed fields.
        >>> adv_format('{}', '{1} {2}', 'Test', '{e}', d='Case', e='{d}')
        >>> 'Test Case'

        Note: you can also include format strings in both the recursed objects and the fields.
        >>> adv_format('{a:.^25}', a='{b} {c}', b='Test', c='{e}', d='Case', e='{d}')
        >>> '........Test Case........'

        >>> adv_format('{a}', a='{b} {c:.>10}', b='Test', c='{e}', d='Case', e='{d}')
        >>> 'Test ......Case'

    """
    @staticmethod
    def fix_entities(string_in):
        if '&' in string_in:
            for k, i in REPLACEMENT_ENTITIES.items():
                key = '&%s;' % k
                string_in = string_in.replace(key, i)
        return string_in

    def get_field(self, field_name, args, kwargs):
        tmp_ret, first = super(AdvFormatter, self).get_field(field_name, args, kwargs)
        if isinstance(tmp_ret, str) and '{' in tmp_ret and '}' in tmp_ret:

            # handle recursive lookups

            if RECURSION_LIST not in kwargs:
                kwargs[RECURSION_LIST] = []
            kwargs[RECURSION_LIST].append(tmp_ret)

            if len(kwargs[RECURSION_LIST]) > 20:
                raise RecursionError('Recursion Error: %r' % kwargs[RECURSION_LIST])

            return self.format(tmp_ret, *args, **kwargs), first
        return tmp_ret, first

    def convert_field(self, value, conversion):

        # handle list conversion

        if conversion is not None and conversion[0] == 'l':
            join_str = conversion[1:]
            return join_str.join(value)
        elif conversion is not None and conversion[0] == 'S':
            if value is None:
                return ''
            else:
                return value
        else:
            return super().convert_field(value, conversion)

    def parse(self, format_string):
        for literal_text, field_name, format_spec, conversion in super().parse(format_string):

            # setup list conversion field

            if conversion is not None and conversion == 'l':
                field = field_name.split('&', maxsplit=1)
                if len(field) == 1:
                    conversion = 'l '
                else:
                    conversion = 'l%s' % field[1]
                    field_name = field[0]
            yield literal_text, field_name, format_spec, conversion

    def _vformat(self, format_string, args, kwargs, used_args, recursion_depth, auto_arg_index=0):
        if recursion_depth < 0:
            raise ValueError('Max string recursion exceeded')
        result = []
        if OPTIONAL_ENCLOSURES in kwargs and kwargs[OPTIONAL_ENCLOSURES]:
            tmp_enc = kwargs[OPTIONAL_ENCLOSURES]
            if isinstance(tmp_enc, str) and len(tmp_enc) != 2:
                raise AttributeError('Error parsing optional enclosures: %r' % tmp_enc)
            opt_start = tmp_enc[0]
            opt_end = tmp_enc[1]
        else:
            opt_start = '<'
            opt_end = '>'

        for literal_text, field_name, format_spec, conversion in self.parse(format_string):

            # output the literal text
            if literal_text:
                result.append(literal_text)

            # if there's a field, output it
            if field_name is not None:
                # this is some markup, find the object and do
                #  the formatting

                # handle arg indexing when empty field_names are given.

                if field_name == '':
                    if auto_arg_index is False:
                        raise ValueError('cannot switch from manual field '
                                         'specification to automatic field '
                                         'numbering')
                    field_name = str(auto_arg_index)
                    auto_arg_index += 1
                elif field_name.isdigit():
                    if auto_arg_index:
                        raise ValueError('cannot switch from manual field '
                                         'specification to automatic field '
                                         'numbering')
                    # disable auto arg incrementing, if it gets
                    # used later on, then an exception will be raised
                    auto_arg_index = False

                # Check for optional replacements

                if field_name[0] == '?' and field_name[-1] == '?':

                    tmp_fmt_str = field_name.replace(opt_start, '{').replace(opt_end, '}')[1:-1]

                    # make empty args and kwargs for test string:
                    tmp_args = []
                    for a in args:
                        tmp_args.append('')
                    tmp_kwargs = dict.fromkeys(kwargs, '')

                    test_string = self.format(tmp_fmt_str, *tmp_args, **tmp_kwargs)

                    # make live string and verify
                    obj, auto_arg_index = self._vformat(
                        tmp_fmt_str, args, kwargs,
                        used_args, recursion_depth - 1,
                        auto_arg_index=auto_arg_index)

                    if obj == test_string:
                        obj = ''
                        format_spec = ''
                    else:
                        obj = self.fix_entities(obj)

                    arg_used = field_name
                else:
                    # given the field_name, find the object it references
                    #  and the argument it came from
                    try:
                        obj, arg_used = self.get_field(field_name, args, kwargs)
                    except (KeyError, AttributeError, IndexError):
                        # handle case of a default string
                        if DEF_STR not in kwargs:
                            raise
                        arg_used, rest = _string.formatter_field_name_split(field_name)

                        if '{}' in kwargs[DEF_STR]:
                            obj = kwargs[DEF_STR].format(field_name)
                        else:
                            obj = kwargs[DEF_STR]

                used_args.add(arg_used)

                # do any conversion on the resulting object
                obj = self.convert_field(obj, conversion)

                # expand the format spec, if needed
                format_spec, auto_arg_index = self._vformat(
                    format_spec, args, kwargs,
                    used_args, recursion_depth - 1,
                    auto_arg_index=auto_arg_index)

                # format the object and append to the result
                result.append(self.format_field(obj, format_spec))

        return ''.join(result), auto_arg_index

adv_format = AdvFormatter().format
