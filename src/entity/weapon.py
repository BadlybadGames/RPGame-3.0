import entity

class MeleeWeaponEntity(entity.Entity):

	def __init__(self, weapon):
		self.image = "weapon.png"
		super(MeleeWeapon, self).__init__()
		self.weapon = weapon
		self.duration = self.weapon.duration

	def update(self, t):
		self.duration -= t
		
		if self.duration >= 0:
			self.die()
		
		