import cocos
import pyglet

from cocos import euclid

from game.game import game
import multiplayer

class Controller(cocos.layer.Layer):
    """Base class for input handlers"""

class PlayerController(Controller):
    """Keyboard + mouse"""

    is_event_handler = True

    def __init__(self, *args, **kwargs):
        self.player = kwargs["player"]

        super(PlayerController,self).__init__()

    def on_key_press(self,key,modifiers):
        skey = pyglet.window.key.symbol_string(key) #String representation of the key
        print "[CONTROLS] Key pressed: ", skey
        d = self.player.mov_acc #temporary dirty direct code
        print dir(d)
        if skey == "LEFT":
            d.x -= 220
        elif skey == "RIGHT":
            d.x += 220
        elif skey == "UP":
            d.y += 220
        elif skey == "DOWN":
            d.y -= 220

        #Notify server/client about the update
        if game.multiplayer:
            data = {}
            if skey in ["LEFT","RIGHT","UP","DOWN"]: #Update position and movement info
                data = {
                    "eid":self.player.eid,
                    "mov_acc":{
                        "type":"Vector2", "args":[d.x, d.y]
                        },
                    "position":{
                        "type":"Vector2", "args":[self.player.position.x, self.player.position.y]
                        },
                }

            if data:
                if game.multiplayer_type == "server":
                    multiplayer.server.send(command = "update", data = data)
                elif game.multiplayer_type == "client":
                    multiplayer.client.send(command = "update", data = data)        

    def on_key_release(self,key,modifiers):
        skey = pyglet.window.key.symbol_string(key) #String representation of the key
        print "[CONTROLS] Key released: ", skey
        d = self.player.mov_acc #temporary dirty direct code
        if skey == "LEFT":
            d.x += 220
        elif skey == "RIGHT":
            d.x -= 220
        elif skey == "UP":
            d.y -= 220
        elif skey == "DOWN":
            d.y += 220

        if game.multiplayer:
            data = {}
            if skey in ["LEFT","RIGHT","UP","DOWN"]: #Update position and movement info
                data = {
                    "eid":self.player.eid,
                    "mov_acc":{
                        "type":"Vector2", "args":[d.x, d.y]
                        },
                    "position":{
                        "type":"Vector2", "args":[self.player.position.x, self.player.position.y]
                        },
                }

            if data:
                if game.multiplayer_type == "server":
                    multiplayer.server.send(command = "update", data = data)
                elif game.multiplayer_type == "client":
                    multiplayer.client.send(command = "update", data = data)        