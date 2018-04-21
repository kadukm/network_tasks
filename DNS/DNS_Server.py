import socket
import struct
import DNS_Parser
from Response import Response


MAX_DATA_LEN = 2048


class DNS_Server:
	def __init__(self, def_server):
		self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.def_server = (def_server, 53)
		self.host_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.host_sock.bind(('localhost', 53))
		self.cur_msg = None
		self.cur_addr = None
		self.cache = {}

	def start(self):
		while True:
			try:
				data, addr = self.host_sock.recvfrom(MAX_DATA_LEN)
			except OSError:
				continue
			self.cur_addr = addr
			self.cur_msg = data
			print('======================================')
			print(f'Received packet from {addr}')
			self.parse_cur_msg()

	def parse_cur_msg(self):
		is_query, queryies_count, answer_count, auth_count, add_count =\
									DNS_Parser.parse_header(self.cur_msg)
		if is_query:
			print(f'Received {queryies_count} queries')
			self.parse_queries(queryies_count)
		else:
			print(f'Received unexpected msg type: Response')

	def parse_queries(self, count):
		offset = 12
		for _ in range(count):
			name, q_type, offset =\
					DNS_Parser.get_data_about_query(self.cur_msg, offset)
			offset += 2
			if q_type not in DNS_Parser.TYPES:
				print(f'Received unexpected msg type: {q_type}')
				continue
			answer = self.get_answer_for(q_type, name)
			if answer is not None:
				self.send_answer(answer)


	def get_answer_for(self, q_type, name):
		if (q_type, name) in self.cache and self.cache[q_type, name].is_valid():
			print(f'Found info about {DNS_Parser.TYPES[q_type]} {name} in the cache')
			return self.cache[q_type, name].collect(self.cur_msg[:2])
		else:
			print(f'Ask info about {DNS_Parser.TYPES[q_type]} {name} from the server')
			self.serv_sock.sendto(self.cur_msg, self.def_server)
			try:
				answer = self.serv_sock.recv(MAX_DATA_LEN)
				self.cache[q_type, name] = Response(answer)
			except Exception as e:
				print("Can't handle answer:\n" + str(e))
				return None
			return answer

	def send_answer(self, answer):
		self.host_sock.sendto(answer, self.cur_addr)
