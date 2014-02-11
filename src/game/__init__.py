# -*- coding: utf-8 -*-
import cocos
from cocos.director import director

import game

Game = None
Layer = None  # This might not need to be public, Scene could possibly be used instead (or director)
Scene = None


def start():
    """ Initializes the game


    """
    global Game, Layer, Scene

    Scene = cocos.scene.Scene()
    Game, Layer = game.start()
    Scene.add(Layer)

    director.push(Scene)
