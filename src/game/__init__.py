# -*- coding: utf-8 -*-
import cocos
from cocos.director import director

import _game
from _game import PIXEL_TO_METER

Game = None
Layer = None  # This might not need to be public, Scene could possibly be used instead (or director)
Scene = None
scroller = None  # TODO: There should be a different interface for this important layer


def start():
    """ Initializes the game


    """
    global Game, Layer, Scene, scroller

    Scene = cocos.scene.Scene()
    Game, layer, scroller = _game.start()
    Scene.add(scroller, z=1)
    Scene.add(layer, z=2)

    director.push(Scene)
