import socket
import json

from game.game import game #Yeeeaaah.... Time to figure out python packages!

conn = None
clients = []

def host():
	global conn
	global clients
	server = socket.socket()
	server.bind(("",30035))
	server.listen(1)
	conn, addr = server.accept()
	conn.setblocking(0)
	clients.append((conn,addr))


def recieve():
	for conn, addr in clients:
		try:
			raw_data = conn.recv(1024)
		except socket.error as e:
		    if e.errno == 10035:
		        pass
		else:
			if raw_data:
				handle_data(raw_data)


def handle_data(raw_data):
	data = json.loads(raw_data)

	#Perform the command
	if data["command"] == "update":
		#Time to update an entity
		eid = data["eid"]
		entity = game.get_entity(eid)
		for k,v in data["data"]:
			setattr(entity, k, v) #YOLO

	#Send the update to other clients (this might be omitted in favour of synchronised updates only)
	for c, a in clients:
		if c is conn:
			continue
		c.send(raw_data)


def update(t):
	recieve()