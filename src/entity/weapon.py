from cocos import collision_model as cm
from cocos.euclid import Vector2

import entity
import game
import util


class MeleeWeaponEntity(entity.WorldEntity):
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

    def update(self, t):
        super(MeleeWeaponEntity, self).update(t)

        wielder = game.Game.get_entity(self.wielder)

        self.position = wielder.position.copy()

        swing_v = float(self.arc) / self.duration
        self.rotation_off = self.rotation_off + swing_v * t
        self.rotation = wielder.rotation + self.rotation_off

        self.duration_left -= t
        if self.duration_left <= 0:
            self.die()

    def update_collision(self):
        center = self.position + Vector2(util.rot_to_vec(self.rotation)) * self.offset
        self.cshape = cm.CircleShape(center=center, r=self.size)

entity.new_entity(MeleeWeaponEntity)
