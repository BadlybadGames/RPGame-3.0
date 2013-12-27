# -*- coding: utf-8 -*-
import random
from cocos import euclid

from util import AttrDict

class Ai(object):

    def __init__(self):
        self.owner = -1
        self.state = AttrDict()

    def update_ai(self):
        pass

    def _get_owner(self):
        from game.game import game
        return game.get_entity(self.owner)

class BasicEnemyAi(Ai):
    name = "BasicEnemyAi"

    def __init__(self):
        super(BasicEnemyAi, self).__init__()
        self.new_destination()

    def update_ai(self):
        owner = self._get_owner()
        if not owner:
            return
            
        owner.move_dir = (self.state.destination - owner.position).normalized()
        
        dv = self.state.destination - owner.position
        if dv.magnitude() < 40:
            self.new_destination()

    def new_destination(self):
        x, y = random.randint(50, 600), random.randint(50, 400)
        self.state.destination = euclid.Vector2(x, y)