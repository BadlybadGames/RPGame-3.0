import entity
from cocos import collision_model as cm


class Projectile(entity.WorldEntity):
    image = "arrow.png"

    etype = "projectile"
    name = "Projectile"

    def __init__(self, **kwargs):
        super(Projectile, self).__init__()

    def update(self, t):
        super(Projectile, self).update(t)

        self.duration -= t
        if self.duration <= 0:
            self.die()

    def update_collision(self):
        self.cshape = cm.CircleShape(center=self.position, r=self.size)

    def on_collision(self, other):
        from game.game import game

        success = False
        owner = game.get_entity(self.controlled_by)

        if owner.etype == "player":
            if other.etype == "enemy":
                success = True
        elif owner.etype == "enemy":
            if other.etype == "player":
                success = True

        if success:
            other.take_damage(self.damage)
            self.die()

entity.new_entity(Projectile)
