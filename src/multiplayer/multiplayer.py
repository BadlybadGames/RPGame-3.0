import socket
import json
import logging

import cocos
from cocos import euclid

import entity
import equipment

class jsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, euclid.Vector2):
            return {"Vector2":[obj[0], obj[1]]}
        elif isinstance(obj, entity.Entity):
            d = entity.Entity.to_json(obj)
            return {"Entity":d}
        elif isinstance(obj, equipment.equipment.Equipment): # TODO: Fix/add this
            return False
        return json.JSONEncoder.default(self, obj)


def json_decode(obj):
    if "Vector2" in obj:
        data = obj["Vector2"]
        return euclid.Vector2(data[0],data[1])
    # if "Entity" in obj:
    #     data = obj["Entity"]
    #     e = entity.types[data["name"]]() # make an instance from the proper entity class
    #     for k, v in data.items():
    #         setattr(e, k, v)
    return obj



IS_MULTIPLAYER = False
IS_SERVER = False

#Update interval in ms
SERVER_UPDATE_INTERVAL = 1.0 / 30.0
CLIENT_UPDATE_INTERVAL = 1.0 / 30.0



def host():
    """host -> CClayer

    Initializes a server and sets it up

    """
    import server

    global IS_MULTIPLAYER
    global IS_SERVER

    IS_MULTIPLAYER = True
    IS_SERVER = True

    layer = cocos.layer.Layer()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", 30035))
    s.setblocking(0)
    server.server = s

    layer.schedule_interval(server.update, SERVER_UPDATE_INTERVAL)

    return layer


def join():
    import client

    global IS_SERVER
    global IS_MULTIPLAYER

    IS_MULTIPLAYER = True
    IS_SERVER = False

    layer = cocos.layer.Layer()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("localhost", 30035))
    s.setblocking(0)
    client.server = s

    layer.schedule_interval(client.update, CLIENT_UPDATE_INTERVAL)

    return layer


def is_server():
    return IS_SERVER


def is_multiplayer():
    return IS_MULTIPLAYER