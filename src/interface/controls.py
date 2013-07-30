import cocos
import pyglet

from game.game import game
import util

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
            "aim":[0,0],      #The point the player is aiming towards 
        }

        self.state["updated"] = False #Do we need to send an update to the server?

class PlayerController(Controller):
    """Keyboard + mouse"""

    is_event_handler = True

    def on_key_press(self,key,modifiers):
        skey = pyglet.window.key.symbol_string(key) #String representation of the key
        print "[CONTROLS] Key pressed: ", skey

        updated = False

        if skey in ("LEFT", "RIGHT", "UP", "DOWN"):
            updated = True
            self.state["updated"] = True

            if skey == "LEFT":
                self.state["movement"][0] -= 1 
            elif skey == "RIGHT":
                self.state["movement"][0] += 1
            elif skey == "UP":
                self.state["movement"][1] += 1
            elif skey == "DOWN":
                self.state["movement"][1] -= 1

        if updated:
            game.get_player().update_input(self.state)
            return True
        else:
            return False

    def on_key_release(self,key,modifiers):
        skey = pyglet.window.key.symbol_string(key) #String representation of the key
        print "[CONTROLS] Key released: ", skey

        updated = False
        if skey in ("LEFT", "RIGHT", "UP", "DOWN"):
            updated = True
            self.state["updated"] = True
            
            if skey == "LEFT":
                self.state["movement"][0] += 1 
            elif skey == "RIGHT":
                self.state["movement"][0] -= 1
            elif skey == "UP":
                self.state["movement"][1] -= 1
            elif skey == "DOWN":
                self.state["movement"][1] += 1

        if updated:
            game.get_player().update_input(self.state)
            return True
        else:
            return False

    def on_mouse_motion(self, x, y, dx, dy):
        self.state["updated"] = True

        player = game.get_player()

        px, py = player.position
        fx, fy = x - px, y - py

        self.state["aim"][0] = fx
        self.state["aim"][1] = fy

        game.get_player().update_input(self.state)
        return True
