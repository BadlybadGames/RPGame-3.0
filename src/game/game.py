import cocos
import cocos.particle_systems
from cocos.director import director
from cocos import euclid

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
		self.tick = 0

	def update(self, t):
		#Update position then velocity
		self.tick += t
		for i in self.entities.values():
			self.update_entity(i, t)

	def update_entity(self, ent, t):			
		#Set our acceleration according to user input
		ent.mov_acc = ent.move_dir * ent.acc_speed

		ent.position += ent.mov_vel * t + (ent.mov_acc * t / 2)
		ent.mov_vel += ent.mov_acc * t

		#perform friction. Improve pls!
		ent.mov_vel = ent.mov_vel *((1-t)*0.5)

		#Update aiming
		target_aim = util.vec_to_rot(ent.aim)
		dr = target_aim - ent.rotation
		if dr < 0 and abs(dr) < 180: #TODO: add wrapping 360->0 
			ent.rotation += max((ent.turn_speed * t)*-1, dr) #Dont rotate too far
		else:
			ent.rotation += min(ent.turn_speed * t, dr)

		#update display accordingly
		if ent.sprite:
			#Interpolation
			ent.sprite.position = (ent.sprite.position + ent.position) / 2
			ent.sprite.rotation = (ent.sprite.rotation + ent.rotation) / 2

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