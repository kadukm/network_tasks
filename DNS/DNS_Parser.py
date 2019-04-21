import struct


TYPES = {1: 'A', 2: 'NS', 5: 'CNAME', 28: 'AAAA'}


def get_data_about_query(msg, offset):
    name = get_domain_name(msg, offset)
    offset += len(name) + 2
    q_type = struct.unpack('!H', msg[offset: offset + 2])[0]
    offset += 2
    return name, q_type, offset


def get_domain_name(query, offset):
    res = []
    if query[offset] // 16 == 12:
        offset =\
            struct.unpack('!H', msg[offset: offset + 4])[0] - 12 * (16 ** 3)
    while query[offset] != 0:
        cur_len = query[offset]
        res.append(query[offset + 1: offset + cur_len + 1].decode())
        offset += 1 + cur_len
    return '.'.join(res)


def get_offset_for_name(msg, offset):
    if msg[offset] // 16 == 12:
        return 2
    else:
        res = 0
        while msg[offset] != 0:
            cur_len = msg[offset]
            offset += 1 + cur_len
            res += 1 + cur_len
        return res + 1


def parse_header(msg):
    id_ = struct.unpack('!H', msg[:2])[0]
    is_query = parse_flags(msg[2: 4])
    query_count = struct.unpack('!H', msg[4: 6])[0]
    answer_count = struct.unpack('!H', msg[6: 8])[0]
    auth_count = struct.unpack('!H', msg[8: 10])[0]
    add_count = struct.unpack('!H', msg[10:12])[0]
    return is_query, query_count, answer_count, auth_count, add_count


def parse_flags(flags_msg):
    the_int = struct.unpack('!H', flags_msg)[0]
    str_flags = bin(the_int)[2:]
    return len(str_flags) < 16 or str_flags[0] == '0'
