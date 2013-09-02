import entity


class Projectile(entity.Entity):
    image = "player.png"

    def __init__(self, **kwargs):
        super(Projectile, self).__init__()

        self.position = kwargs["position"]
        self.duration = kwargs["duration"]

    def update(self, t):
        super(Projectile, self).update(t)

        self.duration -= t
        if self.duration <= 0:
            self.die()
