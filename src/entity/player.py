from cocos import euclid
from cocos import collision_model as cm
from cocos.euclid import Vector2
import constants

import util

import entity


class Player(entity.WorldEntity):

    name = "player"
    etype = "player"

    friendly = True
    mask_collision = 0b011
    mask_event = 0b010

    def __init__(self):
        self._xp = 0
        self.entity_name = "player"
        self.image = "player.png"

        super(Player, self).__init__()

        self.is_player = True
        self.local = True  # TODO: This might be a little dirty
        self.player = 0  # Who controls this player? 0 = local, n = external
        self.weapon = None

    def init_physics(self, world):
        _ud = {"type": "entity",
               "entity": self.eid,
               "mask_collision": self.mask_collision,
               "mask_event": self.mask_event,
               "friendly": self.friendly}  # TODO: keeping a reference to the actual entity might be harmful in multiplayer environment.

        self.body = world.CreateDynamicBody(position=self.position.copy(), linearDamping=7.0,
                                            userData=_ud)

        self.body.CreateCircleFixture(radius=(float(self.size) / constants.PIXEL_TO_METER) / 2, restitution=0)

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
        """Update our entity state based on player input

        @type state: dict
        @param state: A state from interface.controls
        """
        self.attacking = state["attacking"]
        self.aim = state["aim"]
        v = Vector2(state["movement"][0], state["movement"][1])
        self.move_dir = euclid.Vector2(*state["movement"])

        if self.move_dir.magnitude() > 1:
            self.move_dir.normalize()  # We only want the direction (at least when using a keyboard)

    def update_collision(self):
        return cm.CircleShape(center=self.position, r=self.size)

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
