# -*- coding: utf-8 -*-
from cocos import collision_model as cm
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

        if self.ai:
            self.ai.update_ai()

    def update_collision(self):
        return cm.CircleShape(center=self.position, r=self.size)

    def on_collision(self, other, typ):
        pass

class BasicEnemy(npc):
    image = "player.png"

    name = "basicenemy"
    attack_range = 1.0  # The attack_range is the reach from the edge of the body's shape, to the intended range in box2d meters

    xp_worth = 20

    def init_physics(self, world):
        super(npc, self).init_physics(world)
        sensor = self.body.CreateCircleFixture(radius=self.attack_range, isSensor=True)

        def callback(us, other):
            if other and other.is_player:
                other.take_damage(10)

        self.sensor_callbacks[sensor] = callback


entity.new_entity(BasicEnemy)
