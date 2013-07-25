import socket
import json

from game.game import game #Yeeeaaah.... Time to figure out python packages!

server = None
old_data = ""

def join():
	global server

	server = socket.socket()
	server.connect(("localhost",30035))
	server.setblocking(0)

def recieve():
	"""Check for data from server"""

	try:
		raw_data = server.recv(1024)
	except socket.error as e:
	    if e.errno == 10035:
	        pass
	else:
		if raw_data:
			stop = False
			while not stop:
				raw_data = old_data + raw_data
				print "[SERVER] Raw data to process: ", raw_data
				
				length, data = raw_data.split("|",1)
				length = int(length)

			
				if len(data) > length:
					global old_data
					handle_data(data[:length])
					raw_data = data[length:]
				else:
					stop = True
					if len(data) < length: #Not enough data, so lets wait for it
						old_data = old_data + data
					else: #Data is correct length. Process it
						handle_data(data)

def send(command, data):
	"""Send data to the server"""
	print "[CLIENT] Sending data: Command: '%s' Data: '%s'"%(command,data)
	d = json.dumps({"command":command, "data":data})
	msg = str(len(d)) + "|" + d
	server.send(msg)


def handle_data(raw_data):
	print "[CLIENT] Recieved data, json: ", raw_data
	data = json.loads(raw_data)

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

	elif data["command"] == "spawn":
		e = data["data"]
		t = e["type"]
		game.spawn(t)

def update(t):
	recieve()

