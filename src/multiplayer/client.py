import socket
import json
import logging

from game.game import game  # Yeeeaaah.... Time to figure out python packages!
from multiplayer import json_decode, jsonEncoder
import interface.controls
import entity

logger = logging.getLogger("client")

server = None
old_data = ""

entity_ticks = {}  # Last tick we recieved updates for entities


def recieve():
    """Check for data from server"""
    raw_data = True
    while raw_data:
        try:
            raw_data = server.recv(1024)
        except socket.error as e:
            raw_data = False
            if e.errno == 10035:
                pass
        else:
            handle_data(raw_data)


def send(command, data):
    """Send data to the server"""

    msg = {
        "command": command,
        "data": data,
        "tick": game.tick
    }
    msg = json.dumps(msg, cls=jsonEncoder)
    
    logging.info("Sending msg: " + msg)
    server.send(msg)


def handle_data(raw_data):
    #print "[CLIENT] Recieved data, json: ", raw_data
    data = json.loads(raw_data, object_hook = json_decode)

    if data["command"] == "update":
        #Time to update an entity
        tick = data["tick"]

        e_data = data["data"]["Entity"]
        eid = e_data["eid"]

        #check for tick
        if not tick in entity_ticks.keys():  # First time we recieve a tick
            entity_ticks[eid] = tick
        elif tick < entity_ticks[eid]:  # The new update is old! lets disregard it
            return
        else:
            entity_ticks[eid] = tick

        e = game.get_entity(eid)

        if not e:
            e = entity.types[e_data["name"]]()
            game.spawn(e)
            e.from_json(e_data)
        else:
            if e.eid == game.controlled_player: # TODO: This shouldnt even be sent from the server
                pass
            else:
                e.update_from_json(e_data)

    elif data["command"] == "set_control":
        d = data["data"]
        eid = d["eid"]
        game.set_player(eid)

    elif data["command"] == "set_tick":
        d = data["data"]
        tick = d["tick"]
        game.tick = tick

    else:
        assert(False, "We recieved a command but have no idea what to do with it")


def update(t):
    recieve()

    #Check if we need to send an update of our controls
    state = interface.controls.get_state()
    if state["updated"]:
        player = game.get_player()
        position = None
        if player:
            position = player.position
        data = {"state":state, "tick":game.tick, "position":position}
        send("update_controls", data)
        state["updated"] = False

