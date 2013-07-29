import socket
import json

from game.game import game #Yeeeaaah.... Time to figure out python packages!
import interface.controls
import entity

server = None
old_data = ""

def recieve():
	"""Check for data from server"""
	raw_data = True
	while raw_data:
		try:
			raw_data = server.recv(1024)
		except socket.error as e:
			raw_data = False
			if e.errno == 10035:
				pass
		else:
			handle_data(raw_data)

def send(command, data):
	"""Send data to the server"""
	#print "[CLIENT] Sending data: Command: '%s' Data: '%s'"%(command,data)
	d = json.dumps({"command":command, "data":data})
	server.send(d)


def handle_data(raw_data):
	#print "[CLIENT] Recieved data, json: ", raw_data
	data = json.loads(raw_data)

	if data["command"] == "update":
		#Time to update an entity
		d = data["data"]
		eid = d["eid"]
		e = game.get_entity(eid)
		
		if not e:
			if d.get("entity_name") == "player":
				game.spawn(entity.player.Player.from_json(d))
			else:
				game.spawn(entity.entity.Entity.from_json(d))
		else:
			e.update_from_json(d)



def update(t):
	recieve()

	#Check if we need to send an update of our controls
	state = interface.controls.get_state()
	if state["updated"]:
		send("update_controls",state)
		state["updated"] = False 

