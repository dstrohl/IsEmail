import unittest
from helpers.general.adv_format import AdvFormatter, adv_format
from string import Formatter

fmt = adv_format


class TestEntityReplacement(unittest.TestCase):
    def test_ent_replacement(self):
        self.assertEqual(AdvFormatter.fix_entities('...&coln;...'), '...:...')
        self.assertEqual(AdvFormatter.fix_entities('...&bang;...'), '...!...')
        self.assertEqual(AdvFormatter.fix_entities('...&ocb;...'), '...{...')
        self.assertEqual(AdvFormatter.fix_entities('...&ccb;...'), '...}...')
        self.assertEqual(AdvFormatter.fix_entities('...&hash;...'), '...#...')
        self.assertEqual(AdvFormatter.fix_entities('...&hash3;...'), '...&hash3;...')
        self.assertEqual(AdvFormatter.fix_entities('...&hash...'), '...&hash...')
        self.assertEqual(AdvFormatter.fix_entities('...hash;...'), '...hash;...')


class TestAdvFormat(unittest.TestCase):

    # NORMAL ******************************************
    def test_normal_empty_arg(self):
        tmp_str = fmt('{} {}', 'Test', 'Case')
        self.assertEqual(tmp_str, 'Test Case')

    def test_normal_numb_arg(self):
        tmp_str = fmt('{1} {0}', 'Case', 'Test')
        self.assertEqual(tmp_str, 'Test Case')

    def test_normal_kwarg(self):
        tmp_str = fmt('{b} {c}', b='Test', c='Case')
        self.assertEqual(tmp_str, 'Test Case')

    # DEFAULT ******************************************

    def test_default_arg(self):
        tmp_str = fmt('Test {} {}', 'Case', __default_str__='foobar-{}')
        self.assertEqual(tmp_str, 'Test Case foobar-1')

    def test_default_numb_arg(self):
        tmp_str = fmt('Test {0} {1}', 'Case', __default_str__='foobar-{}')
        self.assertEqual(tmp_str, 'Test Case foobar-1')

    def test_default_kwarg(self):
        tmp_str = fmt('Test {d}', c='Case', __default_str__='foobar[{}]')
        self.assertEqual(tmp_str, 'Test foobar[d]')

    def test_default_2_arg(self):
        tmp_str = fmt('Test {} {}', __default_str__='foobar')
        self.assertEqual(tmp_str, 'Test foobar foobar')

    def test_default_2_kwarg(self):
        tmp_str = fmt('Test {d} {e}', c='Case', __default_str__='foobar')
        self.assertEqual(tmp_str, 'Test foobar foobar')

    def test_default_2_num_arg(self):
        tmp_str = fmt('Test {0} {1}', __default_str__='foobar')
        self.assertEqual(tmp_str, 'Test foobar foobar')

    def test_default_2_kwarg_w_formatting(self):
        tmp_str = fmt('Test {d:.>15} {e:.<15}', c='Case', __default_str__='foobar')
        self.assertEqual(tmp_str, 'Test .........foobar foobar.........')

    # LIST ******************************************

    def test_list_arg(self):
        tmp_str = fmt('Test {& !l}', ['Case', 'foobar'])
        self.assertEqual(tmp_str, 'Test Case foobar')

    def test_list_kwarg(self):
        tmp_str = fmt('Test {c&, !l}', c=['Case', 'snafu'])
        self.assertEqual(tmp_str, 'Test Case, snafu')

    def test_list_arg_no_joinstr(self):
        tmp_str = fmt('Test {&!l} {}', ['Case', 'snafu'], __default_str__='foobar')
        self.assertEqual(tmp_str, 'Test Casesnafu foobar')

    def test_list_arg_with_spaces(self):
        tmp_str = fmt('Test {&\n!l}', ['Case', 'snafu'], __default_str__='foobar')
        self.assertEqual(tmp_str, 'Test Case\nsnafu')

    def test_list_arg_with_spaces_format_codes(self):
        tmp_str = fmt('Test {!l:>20}', ['Case', 'snafu'], __default_str__='foobar')
        self.assertEqual(tmp_str, 'Test           Case snafu')

    # OPTIONAL ******************************************

    def test_optional_kwarg_full(self):
        tmp_str = fmt('Test{? <c>?} foobar', c='Case')
        self.assertEqual(tmp_str, 'Test Case foobar')

    def test_optional_kwarg_empty(self):
        tmp_str = fmt('Test{? <c>?} foobar', c='')
        self.assertEqual(tmp_str, 'Test foobar')

    def test_optional_arg_full(self):
        tmp_str = fmt('Test{? <>?} {}', 'Case', 'foobar')
        self.assertEqual(tmp_str, 'Test Case foobar')

    def test_optional_arg_empty(self):
        tmp_str = fmt('Test{? <>?} {}', '', 'foobar')
        self.assertEqual(tmp_str, 'Test foobar')

    def test_optional_kwarg_full_mult(self):
        tmp_str = fmt('Test{? <c><d>?} {f}', c='Case', d='', f='foobar')
        self.assertEqual(tmp_str, 'Test Case foobar')

    def test_optional_kwarg_empty_mult(self):
        tmp_str = fmt('Test{? <c><d>?} {f}', c='', d='', f='foobar')
        self.assertEqual(tmp_str, 'Test foobar')

    def test_optional_kwarg_full_mult_extra(self):
        tmp_str = fmt('Test{? <c>--<d>?} {f}', c='Case', d='snafu', f='foobar')
        self.assertEqual(tmp_str, 'Test Case--snafu foobar')

    def test_optional_kwarg_empty_mult_extra(self):
        tmp_str = fmt('Test{? <c>--<d>?} {f}', c='', d='', f='foobar')
        self.assertEqual(tmp_str, 'Test foobar')

    def test_optional_arg_used_mult(self):
        tmp_str = fmt('Test{? <><>?} {}', 'Case', '', 'foobar')
        self.assertEqual(tmp_str, 'Test Case foobar')

    def test_optional_arg_used_with_colon_and_specials(self):
        tmp_str = fmt('Test{? &ocb;<>&coln;<>&ccb;?} {}', 'Case', '', 'foobar',
                      colon=':', opsbracket='{', clsbracket='}')
        self.assertEqual(tmp_str, 'Test {Case:} foobar')

    def test_optional_arg_unused_with_colon_and_specials(self):
        tmp_str = fmt('Test{? &ocb;<>&coln;<>&ccb;?} {}', '', '', 'foobar',
                      colon=':', opsbracket='{', clsbracket='}')
        self.assertEqual(tmp_str, 'Test foobar')

    def test_optional_arg_unused_mult(self):
        tmp_str = fmt('Test{? <><>?} {}', '', '', 'foobar')
        self.assertEqual(tmp_str, 'Test foobar')

    def test_optional_kwarg_full_mult_extra_with_fmt_spec(self):
        tmp_str = fmt('Test{? <c>--<d>?:.^20} {f}', c='Case', d='snafu', f='foobar')
        self.assertEqual(tmp_str, 'Test.... Case--snafu.... foobar')

    def test_optional_kwarg_empty_mult_extra_with_fmt_spec(self):
        tmp_str = fmt('Test{? <c>--<d>?:.>20} {f}', c='', d='', f='foobar')
        self.assertEqual(tmp_str, 'Test foobar')

    def test_optional_arg_unused_mult_replace(self):
        tmp_str = fmt('Test{? [][]?} {}', '', '', 'foobar', __optional_enclosures__='[]')
        self.assertEqual(tmp_str, 'Test foobar')

    def test_optional_kwarg_full_mult_replace(self):
        tmp_str = fmt('Test{? (c)(d)?} {f}', c='Case', d='', f='foobar', __optional_enclosures__='()')
        self.assertEqual(tmp_str, 'Test Case foobar')

    def test_optional_kwarg_full_mult_replace(self):
        tmp_str = fmt('Test{? %start%c%end%%start%d%end%?} {f}', c='Case', d='', f='foobar', __optional_enclosures__=('%start%', '%end%'))
        self.assertEqual(tmp_str, 'Test Case foobar')

    # RECURSIVE  ******************************************

    def test_rec_karg_1(self):
        tmp_str = fmt('Test {c}', c='{d}', d='Case')
        self.assertEqual(tmp_str, 'Test Case')

    def test_rec_karg_2(self):
        tmp_str = fmt('Test {c}', c='{e}', d='Case', e='{d}')
        self.assertEqual(tmp_str, 'Test Case')

    def test_rec_karg_3(self):
        tmp_str = fmt('{a}', a='{b} {c}', b='Test', c='{e}', d='Case', e='{d}')
        self.assertEqual(tmp_str, 'Test Case')

    def test_rec_arg_1(self):
        tmp_str = fmt('{}', '{b} {c}', b='Test', c='{e}', d='Case', e='{d}')
        self.assertEqual(tmp_str, 'Test Case')

    def test_rec_arg_2(self):
        tmp_str = fmt('{}', '{1} {2}', 'Test', '{e}', d='Case', e='{d}')
        self.assertEqual(tmp_str, 'Test Case')

    def test_rec_num_arg_1(self):
        tmp_str = fmt('{0}', '{b} {c}', b='Test', c='{e}', d='Case', e='{d}')
        self.assertEqual(tmp_str, 'Test Case')

    def test_rec_num_arg_2(self):
        tmp_str = fmt('{0}', '{1} {2}', 'Test', '{e}', d='Case', e='{d}')
        self.assertEqual(tmp_str, 'Test Case')


    def test_rec_karg_w_fmt_spec(self):
        tmp_str = fmt('{a:.^25}', a='{b} {c}', b='Test', c='{e}', d='Case', e='{d}')
        self.assertEqual(tmp_str, '........Test Case........')

    def test_rec_karg_w_fmt_spec_in_field(self):
        tmp_str = fmt('{a}', a='{b} {c:.>10}', b='Test', c='{e}', d='Case', e='{d}')
        self.assertEqual(tmp_str, 'Test ......Case')


if __name__ == '__main__':
    unittest.main()
