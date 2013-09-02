# -*- coding: utf-8 -*-
import entity
import ai


class npc(entity.Entity):

    ai = ai.BasicEnemyAi

    def __init__(self, position):
        super(npc, self).__init__(position)

        if self.ai:
            self.ai = self.ai(owner = self)

    def update(self, t):
        super(npc, self).update(t)

        if self.ai:
            self.ai.update_ai()


class BasicEnemy(npc):
    image = "player.png"
