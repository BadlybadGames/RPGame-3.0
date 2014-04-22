import cocos
import math
from pyglet import graphics
from pyglet.gl import *
import game

_textures = {}

def init():
    global _textures

    bar_left = pyglet.resource.texture("left.png")
    middle_empty = pyglet.resource.texture("test_3.png")
    middle_filled = pyglet.resource.texture("middle_filled.png")
    _textures["left"] = bar_left
    _textures["empty"] = middle_empty
    _textures["filled"] = middle_filled

class Bar(cocos.cocosnode.CocosNode):

    def __init__(self, x, y, w, h, color=(255,)*3*4, factor=1.0):
        """

        @param x:
        @param y:
        @param w:
        @param h:
        @param color: (R,G,B) * 4, color parameters for each vertex
        @param factor: how filled the bar is, 0.0 is 0% filled, 1.0 is 100% filled
        """
        super(Bar, self).__init__()

        self.x = x
        self.y = y
        self.w = 64.0
        self.h = 32.0#128.0
        self.factor = factor
        self.color = color

        self._update()

    def _update(self):
        """
        Recalculates vertex list

        """
        x = self.x
        y = self.y
        w = self.w  #* self.factor
        h = self.h

        print(self.w, self.h)

        OUTLINE_THICKNESS = 2

        tex = _textures["empty"]#.get_image_data()#.get_data("RGBA", 4)
        #h = self.h = tex.height
        tw = w/tex.width
        th = h/tex.height #self.h/tex.width
        _pos = (x, y,
                     x+w, y,
                     x+w, y+h,
                     x, y+h)
        _tex = (0,0, tw,0, tw,th, 0,th)

        th = OUTLINE_THICKNESS
        _outline_pos = (x - th, y - th,
                     x+w + th, y - th,
                     x+w + th, y+h + th,
                     x - th, y+h + th)


        #self.outline_vlist = graphics.vertex_list(4,
        #                                          ("v2f", _outline_pos),
        #                                          ("c3B", (0,)*3*4))

        self.vertex_list = graphics.vertex_list(4,
                                                ("v2f", _pos),
                                                ("t2f", _tex))
                                                #("c3B", self.color))

    def draw(self):
        length_of_middle = self.w - _textures["left"].width*2

        #_textures["left"].blit(x, y)
        #x += _textures["left"].width

        #if self.outline_vlist and self.factor != 0.0:
        #    self.outline_vlist.draw(GL_QUADS)
        if self.vertex_list:
            tex = _textures["empty"]#.get_image_data()#.get_data("RGBA", 4)
            glEnable(tex.target)
            glBindTexture(tex.target, tex.id)
            glTexParameterf(tex.target, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(tex.target, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

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

        #Gradiented colours
        red = (255, 0, 0, 255, 0, 0, 255, 130, 130, 255, 130, 130)
        blue = (0, 0, 255, 0, 0, 255, 130, 130, 255, 130, 130, 255)
        green = (0, 255, 0, 0, 255, 0, 130, 255, 130, 130, 255, 130)
        self.hp_bar = Bar(50, 50, 200, 30, color=red)
        self.mana_bar = Bar(50, 50+40*1, 200, 30, color=blue)
        self.xp_bar = Bar(50, 50+40*2, 200, 30, color=green)

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
        #self.xp_bar.set_factor(f)
