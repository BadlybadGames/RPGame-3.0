import socket
import json

from game.game import game #Yeeeaaah.... Time to figure out python packages!
import interface.controls
import entity

server = None
old_data = ""

entity_ticks = {} #Last tick we recieved updates for entities

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
	d = json.dumps({"command":command, "data":data, "tick":game.tick})
	server.send(d)


def handle_data(raw_data):
	#print "[CLIENT] Recieved data, json: ", raw_data
	data = json.loads(raw_data)

	if data["command"] == "update":
		#Time to update an entity
		tick = data["tick"]

		d = data["data"]
		eid = d["eid"]

		#check for tick
		if not entity_ticks.has_key(tick): #First time we recieve a tick
			entity_ticks[eid] = tick
		elif tick < entity_ticks[eid]: #The new update is old! lets disregard it
			return
		else:
			entity_ticks[eid] = tick

		e = game.get_entity(eid)
		
		if not e:
			if d.get("entity_name") == "player":
				game.spawn(entity.player.Player.from_json(d))
			else:
				game.spawn(entity.entity.Entity.from_json(d))
		else:
			e.update_from_json(d)

	elif data["command"] == "set_control":
		d = data["data"]
		eid = d["eid"]
		game.set_player(eid)

	elif data["command"] == "set_tick":
		d = data["data"]
		tick = d ["tick"]
		game.tick = tick

	else:
		assert(False, "We recieved a command but have no idea what to do with it")



def update(t):
	recieve()

	#Check if we need to send an update of our controls
	state = interface.controls.get_state()
	if state["updated"]:
		send("update_controls",state)
		state["updated"] = False 

