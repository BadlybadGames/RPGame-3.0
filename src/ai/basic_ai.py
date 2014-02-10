# -*- coding: utf-8 -*-
import random
from cocos import euclid
from cocos.euclid import Vector2
from ai.movement import MoveBasic

import logging
logger = logging.getLogger()

from util import AttrDict

class Ai(object):

    def __init__(self):
        self.owner = None
        self.state = AttrDict()

    def update_ai(self):
        pass

    def _get_owner(self):
        if not self.owner:
            return None

        from game.game import game
        return game.get_entity(self.owner)

class BasicEnemyAi(Ai):
    name = "BasicEnemyAi"

    def update_ai(self):
        from game.game import game

        owner = self._get_owner()
        if not owner:
            return

        target = game.get_player()

        if not target:
            return

        destination = MoveBasic.get_next(target)
        v = Vector2(*destination) - Vector2(*owner.position)
        v.normalize()

        owner.move_dir = v
