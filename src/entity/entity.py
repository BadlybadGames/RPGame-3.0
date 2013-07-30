import cocos
from cocos import euclid

class Entity(object):
	"""An entity found in the game world"""

	def __init__(self):
		self.is_player = False
		if self.image:
			self.sprite = cocos.sprite.Sprite(self.image)

		#Movement variables
		self.position = euclid.Vector2(200.0,200.0)
		self.rotation = 0
		self.mov_vel = euclid.Vector2(0.0,0.0)
		self.mov_acc = euclid.Vector2(0.0,0.0)
		self.move_dir = euclid.Vector2(0.0,0.0)
		self.acc_speed = 200
		self.turn_speed = 400 #Degrees/second
		self.aim = (30,30) #Vector from where we are standing to the point we want to aim towards

	@classmethod
	def from_json(cls, json):
		"""Build an object from jsoned data"""
		e = cls()
		e.update_from_json(json)
		return e

	def update_from_json(self, json):
		for k, v in json.items():
			if k == "eid": #We dont want to update an eid after the entity has been made. Especially not if its from a client
				continue

			if isinstance(v, dict): #The value requires a construction of a type
				if v["type"] == "Vector2":
					v = euclid.Vector2(v["args"][0], v["args"][1])
			setattr(self, k, v)

	def to_json(self):
		d = {}
		for k in dir(self):
			if k.startswith("_"): #Ignore builtins
				continue

			if k in ("sprite",):
				continue
			
			v = getattr(self, k)

			if callable(v): #Ignore functions
				continue

			if isinstance(v, euclid.Vector2):
				d[k] = {"type":"Vector2", "args":(v.x, v.y)}
			else:
				d[k] = v
		return d