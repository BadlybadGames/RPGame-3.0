import socket
import json
import collections

import entity.entity
from game.game import game #Yeeeaaah.... Time to figure out python packages!

server = None
clients = {} #(addr, player eid)
old_data = ""


def add_client(addr):
	clients.append(addr)

def recieve():
	"""Check for updates from clients"""
	try:
		raw_data, addr = server.recvfrom(1024)
	except socket.error as e:
	    if e.errno == 10035:
	        pass
	else:
		if raw_data:
			print "[SERVER] Recieved data from %s: %s"%(addr, raw_data)
			if not addr in clients.keys(): #A new client connecting
				on_new_client(addr)

			handle_data(clients[addr], raw_data)

def on_new_client(addr):
	print "A new client connected, lets create a new player for them"
	#Create a new player for them
	e = entity.player.Player()
	e.local = False
	game.spawn(e)

	clients[addr] = (addr, e.eid)
	send("set_control", {"eid":e.eid})

def _send(addr, data):
	"""send(addr, data) -> packet size

	Low level socket data sending.

	"""
	#print "[SERVER] Sending data to %s: '%s' \n"%(addr, data)

	size = server.sendto(data, addr)
	return size


def send(command, data, to=None):
	"""Send data to one or multiple clients.

	Data is sent as a '{lengthofdata}|{json}' string

	"""

	if not to:
		to = clients.values()

	if not isinstance(to, collections.Iterable):
		to = (to)

	msg = json.dumps({"command":command, "data":data})

	for client in to:
		_send(client[0], msg)


def handle_data(client, raw_data):
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

	elif data["command"] == "update_controls": #The client wants to update the state of his controls
		e = game.get_entity(client[1])
		e.update_input(data["data"])

def send_world():
	for e in game.entities.values():
		send("update", e.to_json())

def update(t):
	recieve()

	#send world update
	send_world()