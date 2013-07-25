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
				#first handle command splitting
				while raw_data:
					l, data = raw_data.split("|", 1) #Only split the first |
					l = int(l)
					raw_data = data[l:] #continue processing the rest of the data
					if len(raw_data) < l:
						pass #TODO: Handle too much data at once
					else:
						handle_data(data[:l]) #handle the recieved command

def send(command, data):
	"""Send data to the server

	Data is sent as a '{lengthofdata}|{json}' string

	"""
	print "[SERVER] Sending data: Command: '%s' Data: '%s'"%(command,data)
	d = json.dumps({"command":command, "data":data})
	msg = str(len(d)) + "|" + d
	print "[SERVER] Raw msg: ", msg

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