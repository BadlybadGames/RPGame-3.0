import socket
import json
import collections
import logging

import entity.entity
from multiplayer import *
from game.game import game  # Yeeeaaah.... Time to figure out python packages!

logger = logging.getLogger("server")

server = None
clients = {}  # (addr, player eid, client id)
old_data = ""


def add_client(addr):
    clients.append(addr)


def recieve():
    """Check for updates from clients"""
    try:
        raw_data, addr = server.recvfrom(1024)
    except socket.error as e:
        if e.errno == 10035:
            pass
    else:
        if raw_data:
            logger.info("Recieved data from %s: %s", addr, raw_data)
            if not addr in clients.keys():  # A new client connecting
                on_new_client(addr)

            handle_data(clients[addr], raw_data)


def on_new_client(addr):
    logger.info("A new client connected, lets create a new player for them")
    #Create a new player for them
    client_id = len(clients)+1

    game.gui.log.add_message("Player connected from {ip}".format(ip=addr[0]))

    e = entity.player.Player()
    e.local = False

    game.spawn(e)
    e.controlled_by = client_id

    bow = entity.get_entity_type("BasicBow")(e)
    e.weapon = bow

    clients[addr] = (addr, e.eid, client_id)
    to = [clients[addr]]

    send("set_control", {"eid": e.eid}, to=to)
    send("set_player", {"player":client_id}, to=to)
    send("update", e)
    send("set_tick", {"tick":game.tick}, to=to)

def _send(addr, data):
    """send(addr, data) -> packet size

    Low level socket data sending.

    """
    #print "[SERVER] Sending data to %s: '%s' \n"%(addr, data)

    size = server.sendto(data, addr)
    return size


def send(command, data, to=None):
    """Send data to one or multiple clients.


    """

    if not clients: #no need to send anything if there are no clients
        return

    if not to:
        to = clients.values()

    if not isinstance(to, collections.Iterable):
        to = (to)

    data = {
        "command": command,
        "data": data,
        "tick": game.tick
    }

    msg = json.dumps(data, cls=jsonEncoder)
    logger.info("Sending: %s", msg)


    for client in to:
        _send(client[0], msg)


def handle_data(client, raw_data):
    data = json.loads(raw_data, object_hook=json_decode)
    logger.info("Handling data: %s", data)

    #Perform the command --this part is equal in server and client. Should have
    #common function in base class
    if data["command"] == "update":
        #Time to update an entity
        d = data["data"]
        eid = d["eid"]
        entity = game.get_entity(eid)

    elif data["command"] == "update_controls":  # The client wants to update the state of his controls
        d = data["data"]
        tick = d["tick"]
        state = d["state"]
        position = d["position"]

        e = game.get_entity(client[1])
        if position:
            e.position = position
        e.update_input(state)
        tick = max(0, game.tick - tick) / 100.0
        #print "tick: ", tick
        e.update_movement(tick)

    elif data["command"] == "spawn_entity":
        entity = data["data"]
        if hasattr(entity, "eid"):
            logger.warning("Client sent a spawn_entity with an entity with eid")
            delattr(entity, "eid")
        game.spawn(entity, force=True)
        d = {
            "packet_reference": data["packet_id"],
            "eid":entity.eid
        }
        send("accept_attack", d, to=[clients[client[0]]]) # TODO: Having to list this is silly. Gotta improve _send

def send_world():
    for e in game.get_entities():
        to = [c for c in clients.values() if not e.controlled_by == c[2]] # Don't send updates about their own controlled stuff
        if to:
            send("update", e, to)


def update(t):
    recieve()

    #send world update
    send_world()
