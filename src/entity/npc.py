# -*- coding: utf-8 -*-
from cocos import collision_model as cm
import entity
import ai

import logging


class npc(entity.WorldEntity):

    ai_type = ai.BasicEnemyAi
    etype = "enemy"
    name = "npc"

    def __init__(self):
        super(npc, self).__init__()

    def on_init(self):
        """Called after eid is created"""

        if self.ai_type and not hasattr(self, "ai"):
            self.ai = self.ai_type()
            self.ai.owner = self.eid

    def update(self, t):
        super(npc, self).update(t)

        if self.ai:
            self.ai.update_ai()

    def update_collision(self):
        self.cshape = cm.CircleShape(center=self.position, r=self.size)

    def on_collision(self, other):
        pass

class BasicEnemy(npc):
    image = "player.png"

    name = "basicenemy"

entity.new_entity(BasicEnemy)
