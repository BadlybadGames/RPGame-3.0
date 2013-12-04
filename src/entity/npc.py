# -*- coding: utf-8 -*-
from cocos import collision_model as cm
import entity
import ai

import logging


class npc(entity.Entity):

    ai = ai.BasicEnemyAi
    etype = "enemy"

    def __init__(self, position):
        super(npc, self).__init__(position)

        if self.ai:
            self.ai = self.ai(owner = self)

    def update(self, t):
        super(npc, self).update(t)

        if self.ai:
            self.ai.update_ai()

    def update_collision(self):
        self.cshape = cm.CircleShape(center=self.position, r=self.size)

    def on_collision(self, other):
        logging.info("I was hit! by: ", other.etype)
        if other.etype == "projectile":
            self.die()

class BasicEnemy(npc):
    image = "player.png"
