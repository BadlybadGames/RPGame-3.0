import entity


class MeleeWeaponEntity(entity.Entity):

    name = "MeleeWeaponEntity"
    etype = "Projectile"

    def __init__(self, weapon, **kwargs):
        self.image = "weapon.png"
        super(MeleeWeaponEntity, self).__init__()
        self.weapon = weapon
        self.owner = self.weapon.owner

        #Attack stats
        self.duration = kwargs["duration"]
        self.swing_speed = kwargs["swing_speed"]
        self.radius = kwargs["size"]

    def update(self, t):
        self.duration -= t

        self.rotation = self.rotation + self.swing_speed * t

        if self.duration >= 0:
            self.die()

entity.new_entity(MeleeWeaponEntity)
