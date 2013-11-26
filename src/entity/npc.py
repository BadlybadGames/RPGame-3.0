# -*- coding: utf-8 -*-
from cocos import collision_model as cm
import entity
import ai


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
        self.cshape = cm.CircleShape(center=self.position, r=self.size/2.0)

    def on_collision(self, other):
        if other.etype == "projectile":
            other.die()
            #self.die()

class BasicEnemy(npc):
    image = "player.png"
