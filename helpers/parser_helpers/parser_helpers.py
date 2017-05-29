
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


# **********************************************************************************
# </editor-fold desc="PARSER HELPERS">
# **********************************************************************************



# **********************************************************************************
# <editor-fold desc="PARSERS">
# **********************************************************************************


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

def try_or(email_info, position, *args):
    """
    :param position:
    :param args:

     args =
        dict(
            name=<action_name>,
            string_in="parse_string",
            kwargs for simple_str),
        dict(
            name=<action_name>,
            function="function_name",
            kwargs fpr function)
    :return:  (<action_name>, football)
    """
    position = email_info.pos(position)
    for act in args:
        if isinstance(act, dict):
            tmp_name = act.pop('name')
        elif isinstance(act, str):
            tmp_name = act
        else:
            tmp_name = act.__name__

        tmp_ret = email_info._try_action(position, act)
        if tmp_ret or tmp_ret.error:
            return tmp_name, tmp_ret

    return '', ParseResultFootball(email_info)

def try_counted_and(email_info, position, *args, min_loop=1, max_loop=1):

    final_loop_count = 0
    position = email_info.pos(position)
    tmp_ret = ParseResultFootball(email_info)
    exit_break = False
    empty_return = False

    # email_info.add_note_trace('looping begin outside AND at: ', position + tmp_ret.l)
    # email_info.trace_level += 1
    for loop_count in range(max_loop):
        tmp_loop_ret = ParseResultFootball(email_info)
        email_info.add_begin_trace(position + tmp_ret.l)
        # email_info.add_note_trace('looping begin inside  AND at: ', position + tmp_ret.l + tmp_loop_ret.l)
        # email_info.trace_level += 1
        for act in args:
            # if isinstance(act, dict):
            #     tmp_name = act.pop('name', '')
            # elif isinstance(act, str):
            #     tmp_name = act
            # else:
            #     tmp_name = act.__name__

            tmp_ret_1 = email_info._try_action(position + tmp_ret.l + tmp_loop_ret.l, act)

            if not tmp_ret_1:
                exit_break = True
                # email_info.add_note_trace('Breaking inside loop')
                break

            tmp_loop_ret += tmp_ret_1

        # email_info.trace_level -= 1
        # email_info.add_note_trace('looping end inside  AND', position + tmp_ret.l + tmp_loop_ret.l)
        email_info.add_end_trace(position + tmp_ret.l, tmp_ret)
        if exit_break:
            if tmp_loop_ret:
                # email_info.add_note_trace('Breaking outside loop - 1')
                break
            else:
                tmp_ret += tmp_loop_ret
                # email_info.add_note_trace('Breaking outside loop - 2')
                break

        else:
            if tmp_loop_ret:
                tmp_ret += tmp_loop_ret
            else:
                # email_info.add_note_trace('Breaking outside loop - 3')
                break

        final_loop_count += 1

    # email_info.trace_level -= 1
    # email_info.add_note_trace('looping end of outside AND at: ', position + tmp_ret.l)

    if final_loop_count >= min_loop and not empty_return:
        return final_loop_count, tmp_ret
    else:
        return 0, ParseResultFootball(email_info)

def try_and(email_info, position, *args, min_loop=1, max_loop=1):
    count, tmp_ret = email_info.try_counted_and(position, *args, min_loop=min_loop, max_loop=max_loop)
    return tmp_ret

def ipv6_segment(email_info, position, min_count=1, max_count=7):
    tmp_ret = email_info.fb(position)
    tmp_ret += email_info.ipv6_hex(position)

    if tmp_ret:
        if max_count == 1:
            return 1, tmp_ret

        if not email_info.at_end(position + tmp_ret.l + 1) and \
                        email_info.this_char(position + tmp_ret.l) == ':' and \
                        email_info.this_char(position + tmp_ret.l + 1) == ':' and \
                        min_count <= 1:
            email_info.add_note_trace('Double Colons found, exiting')
            return 1, tmp_ret

        tmp_colon_str = {'string_in': email_info.COLON, 'min_count': 1, 'max_count': 1}
        tmp_count, tmp_ret_2 = email_info.try_counted_and(position + tmp_ret.l,
                                                    email_info.colon,
                                                    email_info.ipv6_hex, min_loop=min_count - 1, max_loop=max_count - 1)
    else:
        return 0, ParseResultFootball(email_info)

    if tmp_ret_2:
        return tmp_count + 1, tmp_ret(tmp_ret_2)
    else:
        return 0, ParseResultFootball(email_info)

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