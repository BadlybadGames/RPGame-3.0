import cocos
from cocos.director import director
import pyglet

import logging
import logging.config
import sys
import os
import json

import interface.menus
import audio
import interface

pyglet.resource.path = [".", "../data/maps", "../res/sfx", "../res/sprites", "../res/music"]
pyglet.resource.reindex()

audio.play_song("maintheme.mp3")

def init_logging():
    with open("logging.json", 'rt') as f:
        config = json.load(f)
    if interface.settings.get("game", "enable-logging") == "True":
        print "is debug"
        f = open("error.log", "w")
        sys.stderr = f
        logging.config.dictConfig(config)
        log_server = logging.getLogger("server")
        log_server.format = '[Server][%(levelname)s]%(name)s:%(lineno)d> %(message)s'
        log_client = logging.getLogger("client")
        log_client.format = '[Client][%(levelname)s]%(name)s:%(lineno)d> %(message)s'
    else:  # Do not bother logging anything at all in production-like builds
        logging.getLogger("").addHandler(logging.NullHandler())

init_logging()

logging.info("Starting game")
director.init(width=800, height=600, do_not_scale=False, caption="RPGame 3.0!")

scene = cocos.scene.Scene()
scene.add(interface.menus.MainMenu())

director.run(scene)

