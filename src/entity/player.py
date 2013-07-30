from cocos import euclid

import entity

class Player(entity.Entity):

	def __init__(self):
		self.entity_name = "player"
		self.image = "player.png"

		super(Player, self).__init__()

		self.is_player = True
		self.local = True #TODO: This might be a little dirty
		self.player = 0 #Who controls this player? 0 = local, n = external

	def update_input(self, state):

		self.aim = state["aim"]
		self.move_dir = euclid.Vector2(*state["movement"])
		self.move_dir.normalize() #We only want the direction (at least when using a keyboard)