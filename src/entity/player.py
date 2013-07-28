from cocos import euclid

import entity
from interface import controls

class Player(entity.Entity):

	def __init__(self):
		self.name = "player"
		self.image = "player.png"

		super(Player, self).__init__()

		self.is_player = True
		self.local = True #TODO: This might be a little dirty
		self.player = 0 #Who controls this player? 0 = local, n = external
		

	def update_input(self, state=None):
		if not state:
			state = controls.get_state()
		else:
			pass #TODO: implement multiplayer state update

		if not state["updated"]: #The controls are the same, no need to update
			return

		self.rotation = state["rotation"]
		self.move_dir = euclid.Vector2(*state["movement"])
		self.move_dir.normalize() #We only want the direction (at least when using a keyboard)
