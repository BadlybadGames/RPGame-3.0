import cocos
from cocos.director import director

import entity.player

game = None

def start():
	global game

	#Set up the game
	scene = cocos.scene.Scene()
	game = Game()

	#Set up multiplayer
	mp = True
	if mp:
		if False:
			import multiplayer.server

			multiplayer.server.host()
			scene.schedule_interval(multiplayer.server.update, 0.5)
		else:
			import multiplayer.client

			multiplayer.client.join()
			scene.schedule_interval(multiplayer.client.update, 0.5)

	player = entity.player.Player()
	scene.add(player.sprite)

	game.spawn(player)
	scene.schedule(game.update)
	director.run(scene)


class Game():

	def __init__(self):
		self.entities = {}	

	def update(self, t):
		#Update position then velocity
		print "Tick: ",t
		for i in self.entities.values():
			i.position += i.mov_vel * t + (i.mov_acc * t / 2)
			print "i.position: ",i.position
			i.mov_vel += i.mov_acc * t
			print"i.vel now: ",i.mov_vel
			print "i.mov_acc: ", i.mov_acc

			#update display accordingly
			if i.sprite:
				i.sprite.position = i.position

	def get_entity(eid):
		return self.entities[eid]


	def spawn(self, entity):
		entity.id = len(self.entities)+1
		self.entities[entity.id] = entity