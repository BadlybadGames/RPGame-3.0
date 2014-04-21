import entity
from cocos import collision_model as cm
from cocos.euclid import Vector2
import game
import util


class Projectile(entity.WorldEntity):
    image = "arrow.png"

    etype = "projectile"
    name = "Projectile"
    collides_with = entity.F_WALL + entity.F_ENTITY

    def __init__(self, **kwargs):
        super(Projectile, self).__init__()

    def update(self, t):
        super(Projectile, self).update(t)

        self.duration -= t
        if self.duration <= 0:
            self.die()

    def update_movement(self, t):
        super(Projectile, self).update_movement(t)

    def update_collision(self):
        return cm.CircleShape(center=self.position, r=self.size)

    def on_collision(self, other, typ):

        if typ == "wall":
            self.die()
            return

        success = False
        owner = game.Game.get_entity(self.controlled_by)
        if not owner:
            return

        if other is owner:
            return

        self.on_hit(other)

    def on_hit(self, other):
        """Called when a collision occurs"""
        other.take_damage(self.damage)
        self.die()


class MeleeWeaponEntity(Projectile):
    """
    Important parameters:

    Offset: length from center of player to center of collision detection
    Arc: Swing arc
    Size: Size used for collision detection
    """
    name = "MeleeWeaponEntity"
    etype = "Projectile"

    def __init__(self, **kwargs):
        self.controlled_by = None  # set after initialization
        self.image = "sword.png"
        super(MeleeWeaponEntity, self).__init__()

    def _init_sprite(self, sprite): # TODO: Sprite still isnt centered on player
        sprite.transform_anchor = sprite.get_rect().midbottom

    def update_movement(self, t):
        wielder = game.Game.get_entity(self.wielder)

        self.position = wielder.position.copy()

    def update(self, t):
        super(MeleeWeaponEntity, self).update(t)

        wielder = game.Game.get_entity(self.wielder)

        swing_v = float(self.arc) / self.duration
        self.rotation_off = self.rotation_off + swing_v * t
        self.rotation = wielder.rotation + self.rotation_off

        #self.duration_left -= t
        #if self.duration_left <= 0:
        #   self.die()

    def update_collision(self):
        center = Vector2(*self.position) + util.rot_to_vec(self.rotation) * self.offset
        #print center, self.size
        return cm.CircleShape(center=center, r=self.size)

    def on_hit(self, other):
        other.take_damage(self.damage)

entity.new_entity(MeleeWeaponEntity)
entity.new_entity(Projectile)
