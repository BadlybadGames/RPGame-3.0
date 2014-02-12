from cocos import euclid
from cocos import collision_model as cm

import util

import entity


class Player(entity.WorldEntity):

    name = "player"
    etype = "player"

    def __init__(self):
        self._xp = 0
        self.entity_name = "player"
        self.image = "player.png"

        super(Player, self).__init__()

        self.is_player = True
        self.local = True  # TODO: This might be a little dirty
        self.player = 0  # Who controls this player? 0 = local, n = external
        self.weapon = None

    def update(self, t):
        super(Player, self).update(t)

        #Update aiming
        target_aim = util.vec_to_rot(self.aim)

        #temp test:
        if True:
            self.rotation = target_aim
            return

        dr = target_aim - self.rotation
        v = 0

        if abs(dr) >= 180:  # Rotate clockwise
            v = -1
        else:
            v = 1

        self.rotation += min((self.turn_speed * t * v), dr)
        if self.rotation > 360:
            self.rotation -= 360
        if self.rotation < 0:
            self.rotation += 360

    def attack(self):
        if self.weapon:
            self.weapon.attack()
            self.attack_cooldown += self.weapon.attack_speed

    def update_input(self, state):
        self.attacking = state["attacking"]
        self.aim = state["aim"]
        self.move_dir = euclid.Vector2(*state["movement"])

        if self.move_dir.magnitude() > 1:
            self.move_dir.normalize()  # We only want the direction (at least when using a keyboard)

    @property
    def xp(self):
        return self._xp


    @xp.setter
    def xp(self, value):
        self._xp = value
        if self._xp > self.xp_needed:
            self.level_up()

    @property
    def xp_needed(self):
        return int(20 + self.level+1 ** 1.5 * 5)

    def level_up(self):
        self.xp -= self.xp_needed
        self.level += 1


entity.new_entity(Player)
