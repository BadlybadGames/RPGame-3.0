import cocos
import pyglet

control = None

def init():
    global control
    
    control = PlayerController()
    return control

def get_state():
    return control.state


class Controller(cocos.layer.Layer):
    """Base class for input handlers"""

    def __init__(self):
        super(Controller, self).__init__()
    
        #The state is what the player ultimately wants to achieve, after keybinds. This is what is sent to the server from clients
        self.state = {
            "movement":[0,0], #Vector target direction
            "rotation":0,               #Angle of player rotation 
        }

        self.state["updated"] = False #Do we need to send an update to the server?

class PlayerController(Controller):
    """Keyboard + mouse"""

    is_event_handler = True

    def on_key_press(self,key,modifiers):
        skey = pyglet.window.key.symbol_string(key) #String representation of the key
        print "[CONTROLS] Key pressed: ", skey

        if skey in ("LEFT", "RIGHT", "UP", "DOWN"):
            self.state["updated"] = True

            if skey == "LEFT":
                self.state["movement"][0] -= 1 
            elif skey == "RIGHT":
                self.state["movement"][0] += 1
            elif skey == "UP":
                self.state["movement"][1] += 1
            elif skey == "DOWN":
                self.state["movement"][1] -= 1

        #Notify server/client about the update
        # if multiplayer.is_multiplayer():
        #     data = {}
        #     if skey in ["LEFT","RIGHT","UP","DOWN"]: #Update position and movement info
        #         data = {
        #             "eid":self.player.eid,
        #             "mov_acc":{
        #                 "type":"Vector2", "args":[d.x, d.y]
        #                 },
        #             "position":{
        #                 "type":"Vector2", "args":[self.player.position.x, self.player.position.y]
        #                 },
        #         }

        #     if data:
        #         if multiplayer.is_server():
        #             multiplayer.server.send(command = "update", data = data)
        #         else:
        #             multiplayer.client.send(command = "update", data = data)        

    def on_key_release(self,key,modifiers):
        skey = pyglet.window.key.symbol_string(key) #String representation of the key
        print "[CONTROLS] Key released: ", skey

        if skey in ("LEFT", "RIGHT", "UP", "DOWN"):
            self.state["updated"] = True
            
            if skey == "LEFT":
                self.state["movement"][0] += 1 
            elif skey == "RIGHT":
                self.state["movement"][0] -= 1
            elif skey == "UP":
                self.state["movement"][1] -= 1
            elif skey == "DOWN":
                self.state["movement"][1] += 1
