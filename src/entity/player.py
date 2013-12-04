from cocos import euclid
from cocos import collision_model as cm

import util

import entity


class Player(entity.Entity):

    name = "player"

    def __init__(self):
        self.entity_name = "player"
        self.image = "player.png"

        super(Player, self).__init__()

        self.is_player = True
        self.local = True  # TODO: This might be a little dirty
        self.player = 0  # Who controls this player? 0 = local, n = external

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

    def update_collision(self):
        self.cshape = cm.CircleShape(center=self.position, r=self.size)

    def attack(self):
        if self.weapon:
            self.weapon.attack()

    def update_input(self, state):
        self.attacking = state["attacking"]
        self.aim = state["aim"]
        self.move_dir = euclid.Vector2(*state["movement"])

        if self.move_dir.magnitude() > 1:
            self.move_dir.normalize()  # We only want the direction (at least when using a keyboard)

entity.new_entity(Player)
