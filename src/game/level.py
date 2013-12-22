import random

import entity
import game

class Level(object):
	"""Object responsible for spawning enemies, events, etc."""

	def on_update(self, t):
		pass

class BasicLevel(Level):
	spawn_freq = 0.1 

	def __init__(self):
		super(BasicLevel, self).__init__()
		self.spawn_t = 0.0

	def on_update(self, t):
		g = game.game

		self.spawn_t += self.spawn_freq * t

		if random.random() < self.spawn_t * t:
			self.spawn_t = 0
			e = entity.get_entity_type("basicenemy")()
			g.spawn(e)

