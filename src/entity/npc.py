# -*- coding: utf-8 -*-
from cocos import collision_model as cm
import constants
import entity
import ai

import logging
import game


class npc(entity.WorldEntity):

    ai_type = ai.BasicEnemyAi
    etype = "enemy"
    name = "npc"

    mask_collision = 0b011
    mask_event = 0b010

    attack_damage = 13
    attack_speed = 1.0
    attack_cooldown = 0.0

    def __init__(self):
        super(npc, self).__init__()

    def on_init(self):
        """Called after eid is created"""

        if self.ai_type and not hasattr(self, "ai"):
            self.ai = self.ai_type()
            self.ai.owner = self.eid

    def on_die(self):
        players = game.Game.get_players()
        for i in players:
            i.xp += self.xp_worth

    def update(self, t):
        super(npc, self).update(t)

        if self.attack_cooldown > 0:
            self.movement_speed_mod = 0.00
        else:
            self.movement_speed_mod = 1.0

        if self.ai:
            self.ai.update_ai()

    def update_collision(self):
        return cm.CircleShape(center=self.position, r=self.size)

    def on_collision(self, other, typ):
        pass

    def can_attack(self):
        return self.attack_cooldown < 0

    def attack(self, other):
        other.take_damage(self.attack_damage)
        self.attack_cooldown = self.attack_speed


class BasicEnemy(npc):
    image = "player.png"
    name = "basicenemy"

    xp_worth = 20
    attack_range = 0.5  # The attack_range is the reach from the edge of the body's shape, to the intended range in box2d meters

    def init_physics(self, world):
        super(npc, self).init_physics(world)

        r = self.size / constants.PIXEL_TO_METER + self.attack_range
        sensor = self.body.CreateCircleFixture(radius=r, isSensor=True)

        def callback(us, detected, dt):
            if not self.can_attack():
                return
            else:
                for typ, other in detected:
                    if not typ == "entity":
                        continue

                    other = game.Game.get_entity(other)
                    if other and other.is_player:
                        self.attack(other)
        game.Game.register_sensor(sensor, callback)
        #del(sensor)


entity.new_entity(BasicEnemy)
