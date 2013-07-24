import cocos
from cocos.director import director

import entity.player

def start():

	scene = cocos.scene.Scene()
	player = entity.player.Player()
	scene.add(player.sprite)
	game = Game()
	game.spawn(player)
	scene.schedule(game.update)
	director.run(scene)


class Game():

	def __init__(self):
		self.entities = []


	def update(self, t):
		#Update position then velocity
		print "Tick: ",t
		for i in self.entities:
			i.position += i.mov_vel * t + (i.mov_acc * t / 2)
			print "i.position: ",i.position
			i.mov_vel += i.mov_acc * t
			print"i.vel now: ",i.mov_vel
			print "i.mov_acc: ", i.mov_acc

			#update display accordingly
			if i.sprite:
				i.sprite.position = i.position


	def spawn(self, entity):
		self.entities.append(entity)