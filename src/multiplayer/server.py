import socket
import json

from game.game import game #Yeeeaaah.... Time to figure out python packages!

conn = None
clients = []
old_data = ""

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
	"""Check for updates from clients"""
	for conn, addr in clients:
		try:
			raw_data = conn.recv(4096)
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
	"""Send data to the server

	Data is sent as a '{lengthofdata}|{json}' string

	"""
	print "[SERVER] Sending data: Command: '%s' Data: '%s'"%(command,data), "\n"
	d = json.dumps({"command":command, "data":data})
	msg = str(len(d)) + "|" + d
	print "[SERVER] Raw msg: ", msg, "\n"

	for conn, addr in clients:
		size = conn.send(msg)
		print size


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

	#Send the update to other clients (this might be omitted in favour of synchronised updates only)
	for c, a in clients:
		if c is conn:
			continue
		c.send(raw_data)


def update(t):
	recieve()