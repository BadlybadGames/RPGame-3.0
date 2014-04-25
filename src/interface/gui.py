import cocos
import math
from pyglet import graphics
from pyglet.gl import *
import game

import resources

_textures = {"default":{}}

def init():
    global _textures

    bar_left = pyglet.resource.texture("left.png")
    bar_right = pyglet.resource.texture("right.png")
    middle_unfilled = pyglet.resource.texture("middle_unfilled.png")
    middle_filled = pyglet.resource.texture("middle_filled.png")
    _textures["default"]["left"] = bar_left
    _textures["default"]["right"] = bar_right
    _textures["default"]["unfilled"] = middle_unfilled
    _textures["default"]["filled"] = middle_filled
    _textures["default"]["fill_color_border"] = 5

class Bar(cocos.cocosnode.CocosNode):

    def __init__(self, x, y, w, h, color=(255,)*3*4, factor=1.0, style="default", text_display = None):
        """

        @param x:
        @param y:
        @param w:
        @param h:
        @param color: (R,G,B) * 4, color parameters for each vertex
        @param factor: how filled the bar is, 0.0 is 0% filled, 1.0 is 100% filled
        @param style: border graphics style
        @param text_display: if given, should be a function that returns a string for the bar to display on itself based on factor
        """
        super(Bar, self).__init__()

        self.x = x
        self.y = y
        self.w = w
        self.h = h#128.0
        self.factor = factor
        self.color = color
        self._texes = _textures[style]
        self.text_f = text_display
        if text_display:
            pos = ((self.w//2), (self.h//2))
            fnt = resources.font("gui_bars")
            self.text = cocos.text.Label("", position=pos, anchor_x="center", anchor_y="center", font_size=11, font_name=fnt)
            self.add(self.text, z=1)

        self._update(init=True)

    def _update(self, init=False):
        """
        Recalculates vertex list

        """
        x = self.x
        y = self.y
        w = self.w  #* self.factor
        h = self.h

        if self.text_f and not init:
            self.text.element.text = self.text_f(self.factor)


        OUTLINE_THICKNESS = 2

        tex = self._texes["unfilled"]#.get_image_data()#.get_data("RGBA", 4)
        #h = self.h = tex.height
        tw = w/tex.width
        th = h/tex.height #self.h/tex.width

        length_of_fill = self.w - self._texes["left"].width*2
        tx = x + self._texes["left"].width
        pw = w - self._texes["left"].width - self._texes["right"].width
        pw *= self.factor
        unw = w - self._texes["left"].width - self._texes["right"].width  # This is the same as pw, just not modified by factor (yes, needs some refactoring)

        _pos = (tx, y,
                     tx+pw, y,
                     tx+pw, y+h,
                     tx, y+h)
        _tex = (0,0, tw,0, tw,th, 0,th)

        fh = h - self._texes["fill_color_border"] * 2
        fy = y + self._texes["fill_color_border"]
        _fill_pos = (tx, fy,
                            tx+pw, fy,
                            tx+pw, fy+fh,
                            tx, fy+fh)
        _unfill_pos = (tx, y,
                         tx+unw, y,
                         tx+unw, y+h,
                         tx, y+h)

        th = OUTLINE_THICKNESS
        _outline_pos = (x - th, y - th,
                     x+w + th, y - th,
                     x+w + th, y+h + th,
                     x - th, y+h + th)


        #self.outline_vlist = graphics.vertex_list(4,
        #                                          ("v2f", _outline_pos),
        #                                          ("c3B", (0,)*3*4))


        self.unfill_vlist = graphics.vertex_list(4,
                                                ("v2f", _unfill_pos),
                                                ("t2f", _tex))

        self.vertex_list = graphics.vertex_list(4,
                                                ("v2f", _pos),
                                                ("t2f", _tex))

        self.fill_colour_vlist = graphics.vertex_list(4,
                                                         ("v2f", _fill_pos),
                                                         ("c3B", self.color))

    def draw(self):
        #left_fill = length_of_fill * self.factor

        if self.vertex_list:
            offset = self._texes["right"].width
            self._texes["left"].blit(self.x, self.y)
            self._texes["right"].blit(self.x+self.w-offset, self.y)

            #Draw the fill background
            tex = self._texes["unfilled"]
            glTexParameterf(tex.target, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(tex.target, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glEnable(tex.target)
            glBindTexture(tex.target, tex.id)

            self.unfill_vlist.draw(GL_QUADS)

            #Draw the fill
            glBindTexture(tex.target, False)  # We need to unset the texture for the colour drawing
            self.fill_colour_vlist.draw(GL_QUADS)
            tex = self._texes["filled"]#.get_image_data()#.get_data("RGBA", 4)
            glBindTexture(tex.target, tex.id)

            self.vertex_list.draw(GL_QUADS)


            glDisable(tex.target)

    def set_colour(self, color):
        """

        @param color: RGBA colour to use
        """
        if color == self.color:
            return

        self.color = color
        self._update()

    def set_factor(self, factor):
        """Sets the length of the bar compared to maximum

        @param factor:
        @return:
        """
        if factor == self.factor:
            return

        self.factor = factor
        self._update()


class MessageLog(cocos.layer.Layer):

    ENTRY_FADE_DELAY = 5.0  # Seconds before a newly pushed message fades out
    ENTRY_FADE_DURATION = 2.0
    ENTRY_FONT_SIZE = 14

    def __init__(self):
        super(MessageLog, self).__init__()

        self.log = []  # Logs are stored as [message, time_until_fade]
        self.schedule(self.update)

    def add_message(self, message):
        """Add a message to the message log and display it

        @param message: Message to be pushed to the message log

        TODO: Coloured strings
        TODO: Fadeout
        """

        entry = cocos.text.Label(text=message, font_size=self.ENTRY_FONT_SIZE)

        for e in self.log:
            x, y = e[0].position
            e[0].position = (x, y+self.ENTRY_FONT_SIZE+6)

        self.log.append((entry,  self.ENTRY_FADE_DELAY))
        self.add(entry)

    def update(self, t):
        new_log = []
        for text, time in self.log:
            new_time = time-t
            new_log.append((text, new_time))
            if new_time <= 0.0:
                f = max(0, min(new_time * 1.0 / -self.ENTRY_FADE_DURATION, 1.0))
                text.opacity = 255 * -f
        self.log = new_log


class Gui(cocos.layer.Layer):
    def __init__(self):
        super(Gui, self).__init__()

        self.bars = []

        red = (255, 0, 0)*4
        blue = (0, 0, 255)*4
        green = (0, 255, 0)*4

        hp_f = lambda f: "{hp}/{max_hp}".format(hp=int(math.ceil(game.Game.get_player().hp)), max_hp=game.Game.get_player().max_hp)
        xp_f = lambda f: "{xp}/{xp_needed}".format(xp=game.Game.get_player().xp, xp_needed=game.Game.get_player().xp_needed)

        self.hp_bar = Bar(50, 50, 200, 32, color=red, text_display=hp_f)
        self.mana_bar = Bar(50, 50+40*1, 200, 32, color=blue)
        self.xp_bar = Bar(50, 50+40*2, 200, 32, color=green, text_display=xp_f)

        self.bars.extend((self.hp_bar, self.mana_bar, self.xp_bar))

        self.log = MessageLog()
        self.log.position = (50, 160)

        self.add(self.hp_bar)
        self.add(self.mana_bar)
        self.add(self.xp_bar)
        self.add(self.log)

        self.schedule(self.update)

    def update(self, dt):
        player = game.Game.get_player()

        if not player:
            return

        f = min(max(float(player.hp) / player.max_hp, 0), 1.0)
        self.hp_bar.set_factor(f)

        f = min(max(float(player.xp) / player.xp_needed, 0), 1.0)
        self.xp_bar.set_factor(f)

        for bar in self.bars:
            bar._update()

