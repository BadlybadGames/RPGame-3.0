import entity

class Player(entity.Entity):

	def __init__(self):
		self.name = "player"
		self.image = "player.png"
		super(Player, self).__init__()