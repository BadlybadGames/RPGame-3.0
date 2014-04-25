__author__ = 'Sebsebeleb'

import pyglet.font

RESOURCES = {"fonts":
     {"gui_bars":"Cantarell"}
}

class ResourceNotFoundError(Exception):
    pass


def init():
    pyglet.font.add_file("../res/fonts/Cantarell-Regular.ttf")

def font(name):
    if not name in RESOURCES["fonts"].keys():
        raise ResourceNotFoundError("Font '{font}' was not found in resources".format(font=name))
    return RESOURCES["fonts"][name]


def sprite(sprite_name):
    pass
