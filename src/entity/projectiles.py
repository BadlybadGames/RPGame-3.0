import entity


class Projectile(entity.Entity):
    image = "player.png"

    def __init__(self, position, *args):
        super(Projectile, self).__init__(*args)

