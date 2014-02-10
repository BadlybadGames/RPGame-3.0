import cocos
from pyglet import graphics
from pyglet.gl import *

class Bar(cocos.cocosnode.CocosNode):
    def __init__(self, x, y, w, h, color=(255,)*3*4, factor=1.0):
        """

        @param x:
        @param y:
        @param w:
        @param h:
        @param factor: how filled the bar is, 0.0 is 0% filled, 1.0 is 100% filled
        """
        super(Bar, self).__init__()

        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.factor = factor
        self.color = color

        self._update()

    def _update(self):
        """
        Recalculates vertex list

        """
        x = self.x
        y = self.y
        w = self.w * self.factor
        h = self.h

        _pos = (self.x, self.y,
                     x+w, y,
                     x+w, y+h,
                     x, y+h)

        self.vertex_list = graphics.vertex_list(4,
                                                ("v2f", _pos),
                                                ("c3B", self.color))

    def draw(self):
        if self.vertex_list:
            self.vertex_list.draw(GL_QUADS)

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


class Gui(cocos.layer.Layer):
    def __init__(self):
        super(Gui, self).__init__()

        #Gradiented colours
        red = (255, 0, 0, 255, 0, 0, 255, 130, 130, 255, 130, 130)
        blue = (0, 0, 255, 0, 0, 255, 130, 130, 255, 130, 130, 255)
        self.hp_bar = Bar(50, 50, 200, 30, color=red)
        self.mana_bar = Bar(50, 90, 200, 30, color=blue)

        self.add(self.hp_bar)
        self.add(self.mana_bar)

        self.schedule(self.update)

    def update(self, dt):
        from game.game import game
        player = game.get_player()

        if not player:
            return

        self.hp_bar.set_factor(float(player.hp) / player.max_hp)