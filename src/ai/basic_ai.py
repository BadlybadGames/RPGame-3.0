# -*- coding: utf-8 -*-
import random
from cocos import euclid


class ai(object):

    def __init__(self, owner):
        self.owner = owner

    def update_ai(self):
        pass


class BasicEnemyAi(ai):

    def __init__(self, owner):
        super(BasicEnemyAi, self).__init__(owner)
        self.new_destination()

    def new_destination(self):
        x, y = random.randint(50, 600), random.randint(50, 400)
        self.destination = euclid.Vector2(x, y)
        self.owner.move_dir = (self.destination - self.owner.position).normalized()

    def update_ai(self):
        dv = self.destination - self.owner.position
        if dv.magnitude() < 40:
            self.new_destination()