import entity
from game.game import game


class MeleeWeaponEntity(entity.WorldEntity):

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

        wielder = game.get_entity(self.wielder)

        self.position = wielder.position.copy()

        swing_v = float(self.arc) / self.duration
        self.rotation_off = self.rotation_off + swing_v * t
        self.rotation = wielder.rotation + self.rotation_off

        self.duration_left -= t
        if self.duration_left <= 0:
            self.die()

entity.new_entity(MeleeWeaponEntity)
