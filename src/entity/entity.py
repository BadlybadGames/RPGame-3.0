import cocos
from cocos import euclid

class Entity(object):
	"""An entity found in the game world"""

	def __init__(self):
		assert(self.name)
		self.is_player = False
		if self.image:
			self.sprite = cocos.sprite.Sprite(self.image)

		#Movement variables
		self.position = euclid.Vector2(200.0,200.0)
		self.mov_vel = euclid.Vector2(0.0,0.0)
		self.mov_acc = euclid.Vector2(0.0,0.0)
		self.move_dir = euclid.Vector2(0.0,0.0)
		self.acc_speed = 200
