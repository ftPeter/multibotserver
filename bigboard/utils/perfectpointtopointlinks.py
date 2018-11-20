import socket

"""
perfectpointtopointlinks.py

PP2PL object with send and deliver methods
"""
class PerfectPointToPointLinks:
	# initialize a server socket to deliver message
	def __init__(self, port, addr_str):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind((addr_str, port))
		self.server.listen(5)

	# send a message to another process
	def send(self, recipient_process_port, addr_str, message):
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect((addr_str, recipient_process_port))
		client.sendall(message.encode())
		client.close()

	# deliver a message
	def deliver(self):
		client, addr = self.server.accept()
		msg = client.recv(2048)
		if msg == b'':
			return None
		return msg.decode()

	# close the link when done
	def close(self):
		self.server.close()
