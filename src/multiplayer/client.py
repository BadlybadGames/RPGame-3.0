import socket
import json

from game.game import game #Yeeeaaah.... Time to figure out python packages!

server = None

def join():
	global server

	server = socket.socket()
	server.connect(("localhost",30035))
	server.setblocking(0)

def recieve():
	try:
		raw_data = server.recv(1024)
	except socket.error as e:
	    if e.errno == 10035:
	        pass
	else:
		if raw_data:
			handle_data(raw_data)

def handle_data(raw_data):
	data = json.loads(raw_data)

	if data["command"] == "update":
		eid = data["eid"]
		entity = game.get_entity(eid)
		for k,v in data["data"]:
			setattr(entity, k, v) #YOLO

def update(t):
	recieve()

