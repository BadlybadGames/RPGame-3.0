import cocos
from cocos.director import director

import entity.player

game = None
scene = None

def start():
	global game
	global scene

	#Setup the game
	scene = cocos.scene.Scene()
	game = Game()

	#Setup multiplayer
	if game.multiplayer:
		global multiplayer
		if game.multiplayer_type == "server":
			import multiplayer.server

			multiplayer.server.host()
			scene.schedule_interval(multiplayer.server.update, 0.5)
		else:
			import multiplayer.client

			multiplayer.client.join()
			scene.schedule_interval(multiplayer.client.update, 0.5)

	player = entity.player.Player()
	scene.add(player.sprite)

	#Setup controls
	import controls.controls #TODO: Add init functions for modules so late import isnt needed
	control = controls.controls.PlayerController(player=player)
	scene.add(control)

	game.spawn(player)
	scene.schedule(game.update)
	director.run(scene)


class Game():
	"""Game state

	Handles both game state and in-game world state

	"""

	def __init__(self):
		self.multiplayer = True
		self.multiplayer_type = "client"
		self.entities = {}	

	def update(self, t):
		#Update position then velocity
		#print "Tick: ",t
		for i in self.entities.values():
			#print "Updating entity ", i.eid
			i.position += i.mov_vel * t + (i.mov_acc * t / 2)
			#print "i.position: ",i.position
			i.mov_vel += i.mov_acc * t
			#print"i.vel now: ",i.mov_vel
			#print "i.mov_acc: ", i.mov_acc

			#perform friction. Improve pls!
			i.mov_vel = i.mov_vel *((1-t)*0.5)

			#update display accordingly
			if i.sprite:
				i.sprite.position = i.position

	def get_entity(self, eid):
		return self.entities[eid]


	def spawn(self, e):
		if e == "player": #Temporary testing convenience
			e = entity.player.Player()
			scene.add(e.sprite)
		if not hasattr(e, "eid"):
			e.eid = len(self.entities)+1
		self.entities[e.eid] = e

		if self.multiplayer and self.multiplayer_type == "server":
			multiplayer.server.send(command="spawn",data={"type":e.name, "data":{}})