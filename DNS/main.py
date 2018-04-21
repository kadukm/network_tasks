import sys
from threading import Thread
from DNS_Server import DNS_Server


def main(def_server):
	server = DNS_Server(def_server)
	server_thread = Thread(target=server.start, args=(), daemon=True)
	server_thread.start()
	while server_thread.isAlive():
		pass
	print('Server was stopped')



if __name__ == '__main__':
	def_server = '8.8.8.8'
	if len(sys.argv) > 1:
		def_server = sys.argv[1]
	main(def_server)
