import entity
from cocos import collision_model as cm


class Projectile(entity.Entity):
    image = "arrow.png"

    etype = "projectile"
    size = 50

    def __init__(self, position, **kwargs):
        super(Projectile, self).__init__(position)

        self.position = position
        self.duration = kwargs["duration"]

    def update(self, t):
        super(Projectile, self).update(t)

        self.duration -= t
        if self.duration <= 0:
            self.die()

    def update_collision(self):
        self.cshape = cm.CircleShape(center=self.position, r=self.size/2.0)
