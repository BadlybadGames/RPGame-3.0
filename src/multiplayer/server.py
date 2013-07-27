import socket
import json
import collections

from game.game import game #Yeeeaaah.... Time to figure out python packages!

server = None
clients = []
old_data = ""

def host():
	global server
	global clients
	server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server.bind(("",30035))
	server.setblocking(0)

def add_client(addr):
	clients.append(addr)


def recieve():
	"""Check for updates from clients"""
	try:
		raw_data, client = server.recvfrom(1024)
	except socket.error as e:
	    if e.errno == 10035:
	        pass
	else:
		if raw_data:
			print "[SERVER] Recieved data from %s: %s"%(client, raw_data)
			if not client in clients:
				clients.append(client)
			handle_data(raw_data)

def _send(addr, data):
	"""send(addr, data) -> packet size

	Low level socket data sending.

	"""
	print "[SERVER] Sending data to %s: '%s' \n"%(addr, data)

	size = server.sendto(data, client)
	return size


def send(command, data, to=None):
	"""Send data to one or multiple clients.

	Data is sent as a '{lengthofdata}|{json}' string

	"""

	if not to:
		to = clients

	if not isinstance(to, collections.Iterable):
		to = (to)

	msg = json.dumps({"command":command, "data":data})

	for addr in to:
		_send(addr, msg)


def handle_data(raw_data):
	data = json.loads(raw_data)

	#Perform the command --this part is equal in server and client. Should have common function in base class
	if data["command"] == "update":
		#Time to update an entity
		d = data["data"]
		eid = d["eid"]
		entity = game.get_entity(eid)
		for k,v in d.items():
			if isinstance(v, dict): #The value is an object and must be constructed
				if v["type"] == "Vector2":
					args = v["args"]
					import cocos.euclid
					v = cocos.euclid.Vector2(args[0],args[1])
				else:
					print "[WARNING] Client recieved undefined data type" #Should ignore it most likely
					continue 
			setattr(entity, k, v) #YOLO

def update(t):
	recieve()