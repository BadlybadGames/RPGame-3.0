__author__ = 'Sebsebeleb'

from cocos import tiles


def init():
    level = tiles.load("../data/maps/desert.tmx")
    background_map = level["background"]
    collision_map = level["collision"]
    return background_map, collision_map
