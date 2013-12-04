import cocos
import pyglet
from pyglet import input

from game.game import game

control = None


def init():
    global control

    #control = GamepadController()
    control = PlayerController()
    return control


def get_state():
    return control.state


class Controller(cocos.layer.Layer):
    """Base class for input handlers"""

    def __init__(self):
        super(Controller, self).__init__()

        # The state is what the player ultimately wants to achieve, after keybinds. This is what is sent to the server from clients
        self.state = {
            "movement": [0, 0],  # Vector target direction
            "aim": [0, 0],       # The point the player is aiming towards
            "attacking": False,
        }

        self.state["updated"] = False  # Do we need to send an update to the server?


class PlayerController(Controller):
    """Keyboard + mouse"""

    is_event_handler = True

    def on_key_press(self, key, modifiers):
        skey = pyglet.window.key.symbol_string(key)  # String representation of the key
        #print "[CONTROLS] Key pressed: ", skey

        updated = False

        if skey in ("A", "D", "W", "S"):
            updated = True
            self.state["updated"] = True

            if skey == "A":
                self.state["movement"][0] -= 1
            elif skey == "D":
                self.state["movement"][0] += 1
            elif skey == "W":
                self.state["movement"][1] += 1
            elif skey == "S":
                self.state["movement"][1] -= 1

        if updated:
            player = game.get_player()
            if player:
                player.update_input(self.state)
            return True
        else:
            return False

    def on_key_release(self, key, modifiers):
        skey = pyglet.window.key.symbol_string(key)  # String representation of the key
        #print "[CONTROLS] Key released: ", skey

        updated = False
        if skey in ("A", "D", "W", "S"):
            updated = True
            self.state["updated"] = True

            if skey == "A":
                self.state["movement"][0] += 1
            elif skey == "D":
                self.state["movement"][0] -= 1
            elif skey == "W":
                self.state["movement"][1] -= 1
            elif skey == "S":
                self.state["movement"][1] += 1

        if updated:
            player = game.get_player()
            if player:
                player.update_input(self.state)
            return True
        else:
            return False

    def on_mouse_motion(self, x, y, dx, dy):
        self.state["updated"] = True

        player = player = game.get_player()
        if not player:
            return

        px, py = player.position
        fx, fy = x - px, y - py

        self.state["aim"][0] = fx
        self.state["aim"][1] = fy


        player.update_input(self.state)
        return True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.state["attacking"] = True
        #print "[CONTROLS] Mouse key pressed: ", a, b, c,

    def on_mouse_release(self, x, y, buttons,  modifiers):
        self.state["attacking"] = False

    def on_joyaxis_motion(self, axis, value):
        #print "Recieved joystick input"
        pass


class GamepadController(Controller):

    def __init__(self):
        super(GamepadController, self).__init__()
        self.schedule(lambda x: 0)

    def on_enter(self):
        super(GamepadController, self).on_enter()
        self.joy = input.get_joysticks()[0]
        self.joy.on_joyaxis_motion = self.on_joyaxis_motion
        self.joy.on_joyhat_motion = self.on_joyhat_motion
        self.joy.on_joybutton_press = self.on_joybutton_press
        self.joy.on_joybutton_release = self.on_joybutton_release
        self.joy.open()

    def on_joyaxis_motion(self, joystick, axis, value):
        #print "Recieved joystick input: ", repr(axis), repr(value)

        updated = False

        if axis in ("x", "y"):  # main directional axis is changed, update movement
            self.state["updated"] = True
            updated = True
            x, y = self.state["movement"]

            if axis == "x":
                x = value
            else:
                y = value * -1  # y-axis is inverted

            self.state["movement"] = x, y

        elif axis in ("z", "rz"):  # secondary directional axis is changed, update aim
            if abs(value) < 0.005:  # clamp values that result from leaving the dpad at center
                return
            self.state["updated"] = True
            updated = True
            x, y = self.state["aim"]

            if axis == "z":
                x = value
            else:
                y = value * -1  # y-axis is inverted

            self.state["aim"] = x, y

        if updated:
            player = game.get_player()
            if player:
                player.update_input(self.state)

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        #print "Recieved joystick input: ", hat_x, hat_y
        pass

    def on_joybutton_press(self, joystick, button):
        #print "joybutton press: ", button
        if button == 5:
            self.state["attacking"] = True

        player = game.get_player()
        if player:
            player.update_input(self.state)

    def on_joybutton_release(self, joystick, button):
        #print "joybutton release: ", button
        if button == 5:
            self.state["attacking"] = False

        player = game.get_player()
        if player:
            player.update_input(self.state)
