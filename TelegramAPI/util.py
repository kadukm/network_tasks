def try_add_info(attribute, user, answer, answer_list):
    res = user.get(attribute)
    if res is not None:
        answer_list.append(answer.format(res))
