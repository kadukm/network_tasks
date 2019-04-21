import time
import struct
import DNS_Parser


class Response:
    def __init__(self, data):
        self.data = data
        self.creation_time = time.time()
        self.ttl = 4294967295
        self.ttl_positions = []
        self.find_ttl_positions()

    def find_ttl_positions(self):
        is_query, queryies_count, answer_count, auth_count, add_count =\
                                        DNS_Parser.parse_header(self.data)
        if is_query:
            raise Exception('Inncorrect msg type')
        offset = 12
        for _ in range(queryies_count):
            _1, _2, offset =\
                    DNS_Parser.get_data_about_query(self.data, offset)
            offset += 2
        for _ in range(answer_count + auth_count + add_count):
            offset += DNS_Parser.get_offset_for_name(self.data, offset)
            type_ = struct.unpack('!H', self.data[offset: offset + 2])[0]
            if type_ not in DNS_Parser.TYPES:
                raise Exception(f'Unexpected msg type: {type_}')
            offset += 4  # skip type and class
            self.ttl_positions.append(offset)
            self.ttl = min(self.ttl,
                struct.unpack('!L', self.data[offset: offset + 4])[0])
            offset += 4
            data_len = struct.unpack('!H', self.data[offset: offset + 2])[0]
            offset += 2 + data_len

    def is_valid(self):
        seconds_left = time.time() - self.creation_time
        return seconds_left < self.ttl

    def collect(self, id_):
        res = [id_]
        prev_pos = 2
        cur_ttl = self.ttl - time.time() + self.creation_time
        b_cur_ttl = struct.pack('!H', int(cur_ttl))
        for ttl_pos in self.ttl_positions:
            res.append(self.data[prev_pos: ttl_pos])
            res.append(b_cur_ttl)
            prev_pos = ttl_pos + 2
        res.append(self.data[prev_pos:])
        return b''.join(res)
