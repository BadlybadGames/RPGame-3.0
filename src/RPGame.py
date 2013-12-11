import cocos
from cocos.director import director

import logging
import logging.config
import sys
import json

import interface.menus

def init_logging():
    with open("logging.json", 'rt') as f:
        config = json.load(f)
    logging.config.dictConfig(config)
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

