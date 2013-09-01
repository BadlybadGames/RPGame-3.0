import entity


class Projectile(entity.Entity):

    def __init__(self, position, *args):
        super(Projectile, self).__init__(*args)

