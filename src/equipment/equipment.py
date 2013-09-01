class Equipment(object):
	pass

class Weapon(Equipment):

	def __init__(self):
		self.damage = (1,6)
		self.attack_speed = 0.20

class BowWeapon(Weapon):
	
	def __init__(self):
		super(BowWeapon, self).__init__()

		self.proj_length = 40
		self.proj_life = 3.0
		self.proj_speed = 10

	def attack(self):
		e = Entity.entity()
		e.image = "arrow.png"
		
		e.position = self.wielder.position
		e.rotation = self.wielder.rotation
		e.

class MeleeWeapon(Weapon):

	def __init__(self):
		super(MeleeWeapon, self).__init__()

		self.width = 5
		self.length = 50
		self.duration = 1.0

	def attack(self):
		e = entity.MeleeWeaponEntity(self)
		