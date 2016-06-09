import socket, json

def master_cmd(data):
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		s.connect("/tmp/pokecan.sock")
	except (OSError, IOError) as e:
		return ""
	else:
		s.send(json.dumps(data))
		data = s.recv(1024)
		res = {}
		try:
			res = json.loads(data)
		except ValueError as e:
			return ""
		else:
			return res