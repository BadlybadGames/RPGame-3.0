import entity
import cocos.collision_model as cm


class MeleeWeaponEntity(entity.Entity):

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

    def update_collision(self):
        self.cshape = cm.CircleShape(center=self.position, r=self.size)
