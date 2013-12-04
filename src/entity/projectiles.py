import entity
from cocos import collision_model as cm


class Projectile(entity.Entity):
    image = "arrow.png"

    etype = "projectile"
    name = "projectile"

    def __init__(self, **kwargs):
        super(Projectile, self).__init__()

    def update(self, t):
        super(Projectile, self).update(t)

        self.duration -= t
        if self.duration <= 0:
            self.die()

    def update_collision(self):
        self.cshape = cm.CircleShape(center=self.position, r=self.size)

entity.new_entity(Projectile)
