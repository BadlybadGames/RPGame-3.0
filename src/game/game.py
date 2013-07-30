import cocos
import cocos.particle_systems
from cocos.director import director

import entity.player
import multiplayer

import util

game = None
layer = None

def start():
	global game
	global layer

	#Setup the game
	layer = cocos.layer.Layer()
	game = Game()

	player = entity.player.Player()

	#Setup controls
	import interface.controls #TODO: Add init functions for modules so late import isnt needed
	c = interface.controls.init()
	layer.add(c)

	game.spawn(player)
	game.set_player(player.eid)
	layer.schedule(game.update)

	return layer


class Game():
	"""Game state

	Handles both game state and in-game world state

	"""

	def __init__(self):
		self.entities = {}	
		self.controlled_player = None

	def update(self, t):
		#Update position then velocity
		#print "Tick: ",t
		for i in self.entities.values():			
			#Set our acceleration according to user input
			i.mov_acc = i.move_dir * i.acc_speed

			i.position += i.mov_vel * t + (i.mov_acc * t / 2)
			i.mov_vel += i.mov_acc * t

			#perform friction. Improve pls!
			i.mov_vel = i.mov_vel *((1-t)*0.5)

			#Update aiming
			target_aim = util.vec_to_rot(i.aim)
			dr = target_aim - i.rotation
			if dr < 0: #TODO: add wrapping 360->0 
				i.rotation += max((i.turn_speed * t)*-1, dr) #Dont rotate too far
			else:
				i.rotation += min(i.turn_speed * t, dr)

			#update display accordingly
			if i.sprite:
				i.sprite.position = i.position
				i.sprite.rotation = i.rotation

	def get_entity(self, eid):
		return self.entities.get(eid)

	def get_player(self):
		return self.get_entity(self.controlled_player)

	def set_player(self, eid):
		self.controlled_player = eid

	def spawn(self, e):
		if not hasattr(e, "eid"):
			e.eid = len(self.entities)+1
		self.entities[e.eid] = e

		layer.add(e.sprite)

		#if multiplayer.is_server():
		#	multiplayer.server.send(command="spawn",data={"type":e.name, "data":{}})