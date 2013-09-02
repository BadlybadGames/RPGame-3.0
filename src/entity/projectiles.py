import entity


class Projectile(entity.Entity):
    image = "arrow.png"

    def __init__(self, position, **kwargs):
        super(Projectile, self).__init__(position)

        self.position = position
        self.duration = kwargs["duration"]

    def update(self, t):
        super(Projectile, self).update(t)

        self.duration -= t
        if self.duration <= 0:
            self.die()
