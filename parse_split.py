def split_email(email_in):
    """
    returns:

    local_part, domain_part

    :param str email_in:
    :return:
    """
    if '@' not in email_in:
        raise ValueError('No @ found in email_in')

    start_skip = 0
    if '"' in email_in:
        quote_count = email_in.count('"')
        if quote_count % 2 != 0:
            raise IndexError('unbalanced quotes')

        quote_loc = email_in.find('"')
        first_at = email_in.find('@')

        if quote_loc > first_at:
            return email_in.split('@', maxsplit=1)

        next_quote = email_in.find('"', start=quote_loc, end=)



    else:
        return email_in.split('@', maxsplit=1)


def remove_comments(email_in):
    """
    returns email string without comments
    :param email_in:
    :return: new_email, [(comment1, pos), (comment2, pos), (comment3, pos)]
    """
    comment_list = []
    email_out = []
    in_comment = False
    comment_pointer = -1
    current_comment = None
    for position, c in enumerate(email_in):
        if c == '(':
            comment_pointer += 1
            try:
                current_comment = comment_list[comment_pointer]
            except IndexError:
                comment_list.append([])
                current_comment = comment_list[comment_pointer]
            in_comment = True
        elif c == ')':
            comment_pointer -= 1
            if comment_pointer == -1:
                in_comment = False
            elif comment_pointer == -2:
                raise IndexError('close comment found without open comment')
            else:
                current_comment = comment_list[comment_pointer]

        else:
            if in_comment:
                current_comment.append((c, position))
            else:
                email_out.append(c)

    return email_out, comment_list


