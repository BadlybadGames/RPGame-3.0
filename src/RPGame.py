import cocos
from cocos.director import director

import logging
import sys

import interface.menus

def init_logging():
	logging.basicConfig(format='[%(levelname)s]%(name)s:%(lineno)d> %(message)s', filename='debug.log',level=logging.DEBUG)
	f = open("error.log", "w")
	sys.stderr = f
	log_server = logging.getLogger("server")
	log_server.format = '[Server][%(levelname)s]%(name)s:%(lineno)d> %(message)s'
	log_client = logging.getLogger("client")
	log_client.format = '[Client][%(levelname)s]%(name)s:%(lineno)d> %(message)s'

init_logging()

logging.info("Starting game")
director.init(width=800, height=600, do_not_scale=False, caption="RPGame 3.0!")

scene = cocos.scene.Scene()
scene.add(interface.menus.MainMenu())

director.run(scene)

