import cocos
from cocos.director import director

import entity.player
import multiplayer

game = None

def start():
	global game

	#Setup the game
	layer = cocos.layer.Layer()
	game = Game()

	player = entity.player.Player()
	layer.add(player.sprite)

	#Setup controls
	import controls.controls #TODO: Add init functions for modules so late import isnt needed
	control = controls.controls.PlayerController(player=player)
	layer.add(control)

	game.spawn(player)
	layer.schedule(game.update)
	
	return layer


class Game():
	"""Game state

	Handles both game state and in-game world state

	"""

	def __init__(self):
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

		if multiplayer.is_server():
			multiplayer.server.send(command="spawn",data={"type":e.name, "data":{}})