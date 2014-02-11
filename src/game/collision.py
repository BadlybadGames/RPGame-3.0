# -*- coding: utf-8 -*-

import numpy as np
import collections

class Theta_star(object):

    @classmethod
    def line_of_sight(cls, s, s1):
        x0 = s.x
        y0 = s.y
        x1 = s1.x
        y1 = s1.y
        dy = y1 - y0
        dx = x1 - x0
        f = 0
        if dy < 0:
            dy *= -1
            s.y = -1
        else:
            s.y = 1
        if dx < 0:
            dx *= -1
            s.x = -1
        else:
            s.y = 1
        if dx >= dy:
            while x0 != x1:
                f = f + dy
                if f >= dx:
                    if cls.map[x0+((s.x - 1)/2), y0 + ((s.y - 1/2))]:
                        return False
                    y0 = y0 + s.y
                    f = f - dx
                if f != 0 and cls.map[x0 + ((s.x - 1)/2), y0 + ((s.y - 1)/2)]:
                    return False
                if dy == 0 and cls.map[x0+((s.x - 1)/2),y0] and cls.map[x0 + ((s.x - 1)/2), y0 - 1]:
                    return False
                x0 = x0 + s.x
        else:
            while y0 != y1:
                f = f + dx
                if f >= dy:
                    if cls.map[x0 + ((s.x - 1)/2), y0+((s.y - 1)/2)]:
                        return False
                    x0 = x0+s.x
                    f = f - dy
                if f != 0 and cls.map[x0 + ((s.x - 1)/2), y0 + ((s.y - 1)/2)]:
                    return False
                if dx == 0 and cls.map[x0, y0 + ((s.y -1)/2)] and cls.map[x0 - 1, y0+((s.y-1)/2)]:
                    return False
                y0 = y0 + s.y
        return True

    @classmethod
    def update_vertex(cls, s, s1):
        g_old = s1.g
        ComputeCost(s, s1)
        if s1.g < g_old:
            if s1.g < g_old:
                if s1 in open_list:
                    open.remove(s1)
                open.insert(s1, s1.g + s1.h)

    @classmethod
    def compute_cost(cls, s, s1):
        if cls.line_of_sight(s.parent, s1):
            # Path 2
            s1.parent = s.parent
            s1.g = s.g + c(s, s1) # c? c=compute_cost?
        else:
            # Path 1
            if s.g + c(c, s1) < s1.g:
                s1.parent = s
                s1.g = s.g + c(s, s1)

class Node(object):
    def __init__(self):
        self.cost = 1
        self.weight = 9999
        self.parent = None

class Pathfinding(object):

    _cache = {}

    def __init__(self, map):
        self.map = map

    def _astar(self, start, goal):
        map = [Node(n) for n in m for m in self.map]
        open_list = collections.deque()
        closed_list = []

        open_list.append(map[start])

        while open_list:
            node = open_list.popleft()
            if node == goal:
                return find_path

    def _lazy_theta(self, start, goal):
        open_list = collections.deque()
        closed_list = collections.deque()



    def _smooth_path(self, path):
        # First remove all consecutive movements with the same movement vector
        # Then from remaining paths, remove redundant nodes so remaining nodes all have line of sight to each other
    def get_path(self, v1, v2):
        """Returns the path needed to take on the collision grid map from v1 to v2.

        get_path(v1, v2) should be inverse of get_path(v2, v1)

        @param v1: From position
        @param v2: To position

        @return: array of positions to traverse
        """

        # The very first thing we do is check if the path is cached
        if self._cache.has_key((v1, v2)) or self._cache.has_key((v2, v1)):
            path = self._cache.get((v1, v2)) or reversed(self._cache.get((v2, v1)))
            return path

        path = self._astar(v1, v2)
        return self._smooth_path(path)

    def clear(self):
        """ Should be called when the map is updated. Clears cache


        """
        self._cache = {}

class CollisionGrid(object):

    def __init__(self, tile_width=48, tile_height=48, width=20, height=20):
        """

        @param tile_width: Width of one tile in pixels
        @param tile_height: Height of one tile in pixels
        @param width: Number of tiles in the width
        @param height: Number of tiles in the height
        """
        self.grid = np.zeros((width, height))

    def show(self):
        import cocos

        layer = cocos.layer.Layer()
