
__all__ = ['simple_char', 'single_char', 'simple_str', 'parse_and', 'parse_or', 'parse_loop', 'parse_best']

from helpers.footballs import ParseResultFootball


def simple_char(email_info, position, parse_for, min_count=-1, max_count=99999, parse_until=None):
    tmp_ret = email_info.fb(position)
    tmp_count = 0

    if parse_until is None:
        looper = email_info.remaining_complex(begin=position, count=max_count)
    else:
        looper = email_info.remaining_complex(begin=position, count=max_count, until_char=parse_until)

    for i in looper:
        if i in parse_for:
            tmp_count += 1
        else:
            if tmp_count >= min_count:
                return tmp_ret(tmp_count)
            else:
                return tmp_ret

    if tmp_count >= min_count:
        return tmp_ret(tmp_count)
    return tmp_ret


def single_char(email_info, position, parse_for):
    tmp_ret = email_info.fb(position)
    if email_info[position] == parse_for:
        return tmp_ret(1)
    else:
        return tmp_ret


def simple_str(email_info, position, parse_for, caps_sensitive=True):
    tmp_ret = email_info.fb(position)
    tmp_len = len(parse_for)

    tmp_check = email_info.mid(position, tmp_len)

    if not caps_sensitive:
        tmp_check = tmp_check.lower()
        parse_for = parse_for.lower()

    if tmp_check == parse_for:
        tmp_ret += tmp_len

    return tmp_ret



'''
def _try_action(email_info, position, action_dict):
    if isinstance(action_dict, dict):
        action_dict = action_dict.copy()
        if 'string_in' in action_dict:
            parse_for = action_dict.pop('string_in')
            return email_info.simple_char(position, parse_for=parse_for, **action_dict)

        elif 'function' in action_dict:
            tmp_func = action_dict.pop('function')
            return tmp_func(position, **action_dict)
        else:
            raise AttributeError('Invalid dictionary passed: %r' % action_dict)
    elif isinstance(action_dict, str):
        return email_info.simple_char(position, parse_for=action_dict)

    else:
        return action_dict(position)
'''


def _make_ret(email_info, position, parser, *args, **kwargs):
    if isinstance(parser, ParseResultFootball):
        return parser
    elif isinstance(parser, str):
        if len(parser) > 1 and parser[0] == '"' and parser[-1] == '"':
            return simple_str(email_info, position, parser[1:-1])
        else:
            return simple_char(email_info, position, parser)
    else:
        return parser(email_info, position, *args, **kwargs)


def parse_or(email_info, position, *parsers, **kwargs):
    email_info.begin_stage('OR', position)
    for p in parsers:
        tmp_ret = _make_ret(email_info, position, p, **kwargs)
        if tmp_ret:
            email_info.end_stage(results=tmp_ret)
            return tmp_ret
    email_info.end_stage(results=email_info.fb(position))
    return email_info.fb(position)


def parse_and(email_info, position, *parsers, **kwargs):
    email_info.begin_stage('OR', position)
    tmp_ret = email_info.fb(position)
    for p in parsers:
        tmp_ret_2 = _make_ret(email_info, position + tmp_ret, p, **kwargs)
        if not tmp_ret_2:
            email_info.end_stage(results=tmp_ret)
            return email_info.fb(position)
        tmp_ret += tmp_ret_2
    email_info.end_stage(results=tmp_ret)
    return tmp_ret


def parse_loop(email_info, position, parser, *args, min_loop=1, max_loop=256, ret_count=False, **kwargs):
    email_info.begin_stage('LOOP', position)
    tmp_ret = email_info.fb(position)
    loop_count = 0

    while loop_count in range(max_loop):
        email_info.begin_stage('Loop #%s, @ %s' % (loop_count, position + tmp_ret), position + tmp_ret)

        tmp_loop_ret = parser(email_info, position + tmp_ret, *args, **kwargs)
        email_info.end_stage(results=tmp_loop_ret)

        if tmp_loop_ret:
            tmp_ret += tmp_loop_ret
        else:
            break

        loop_count += 1

    email_info.end_stage(results=tmp_ret)

    if loop_count >= min_loop:
        if ret_count:
            return loop_count, tmp_ret
        else:
            return tmp_ret
    else:
        if ret_count:
            return 0, email_info.fb(position)
        else:
            return email_info.fb(position)


def parse_best(email_info, position, *parsers, try_all=False, **kwargs):
    email_info.begin_stage('BEST', position)
    tmp_ret = email_info.fb(position)

    for p in parsers:
        tmp_ret_2 = _make_ret(email_info, position, p, **kwargs)
        if not try_all and tmp_ret_2 and email_info.at_end(position + tmp_ret_2):
            tmp_ret = tmp_ret_2
            break

        tmp_ret = tmp_ret.max(tmp_ret_2)
    email_info.end_stage(results=tmp_ret)
    return tmp_ret


'''

def football_max(email_info, *footballs, names=None):
    names = names or []

    email_info.add_note_trace('Comparing Footballs')
    if email_info._set_trace(1):
        for index, fb in enumerate(footballs):
            if len(names) < index + 1:
                if fb.segment_name == '':
                    names.append('#%s' % index)
                else:
                    names.append(fb.segment_name)

            if fb.error:
                email_info.add_note_trace('Comp %s [ERROR] (%s/%s)' % (names[index], int(fb), fb._max_length))
            else:
                email_info.add_note_trace('Comp %s (%s/%s)' % (names[index], int(fb), fb._max_length))
            email_info.add_note_trace('        %r' % fb.diags())

    tmp_ret = None
    tmp_index = -1
    a_index = -1
    b_index = -1
    ab_note = ''

    for index, fb in enumerate(footballs):
        if tmp_ret is None:
            tmp_ret = fb
            tmp_index = index
            continue

        a_index = tmp_index
        b_index = index
        ab_note = ''
        update_ret = False

        if tmp_ret.error != fb.error:
            if tmp_ret.error:
                if fb:
                    update_ret = False
                    ab_note = '(B has error, A haa content)'
            elif fb.error:
                if not tmp_ret:
                    update_ret = False
                    ab_note = '(A has Error, B no content)'
        else:
            if fb > tmp_ret:
                update_ret = False
                ab_note = '(A is larger)'
            elif fb == tmp_ret:
                if fb._max_length > tmp_ret._max_length:
                    update_ret = False
                    ab_note = '(A max length longer)'

        if update_ret:
            tmp_ret = fb
            tmp_index = index
            a_index = index
            b_index = tmp_index

        if email_info._set_trace():
            email_info.add_note_trace('Test #%s: %s > %s  %s' % (index, names[a_index], names[b_index], ab_note))

    if email_info._set_trace(-1):
        email_info.add_note_trace('Returning %s' % names[tmp_index])
    return tmp_ret
'''