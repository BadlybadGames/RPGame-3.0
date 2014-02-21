# -*- coding: utf-8 -*-
from itertools import product
import cocos
from cocos.euclid import Vector2

import numpy as np
import collections

class Node(object):
    def __init__(self, x, y):
        self.g = 0
        self.h = 0
        self.parent = None
        self.x, self.y = x, y

    def __repr__(self):
        return "Node({x}, {y})".format(x=self.x, y=self.y)

class ThetaStar(object):
    """Implemtents theta*: http://aigamedev.com/open/tutorials/theta-star-any-angle-paths/

    TODO: Use lazy theta* instead: http://aigamedev.com/open/tutorial/lazy-theta-star/
    TODO: This should be a functional class
    """

    def __init__(self, graph, grid):
        self.graph = graph
        self.grid = grid

    def search(self, start, end):
        self.open_set = []
        closed_set = []
        current = start
        current.g = 0
        current.parent = current
        self.open_set.append(current)
        while self.open_set:
            current = min(self.open_set, key=lambda o: o.g + self.c(o, end))  # c is used for calculating the heuristics
            if current == end:
                path = []
                while current != start:
                    path.append(current)
                    current = current.parent
                path.append(current)
                return path[::-1]
            self.open_set.remove(current)
            closed_set.append(current)
            for node in self.graph[current]:
                if node in closed_set:
                    continue
                if node not in self.open_set:
                    node.g = 99999
                    node.parent = None
                self.update_vertex(current, node)
        return None


    def line_of_sight(self, s, s1):
        x0 = s.x
        y0 = s.y
        x1 = s1.x
        y1 = s1.y
        dy = y1 - y0
        dx = x1 - x0
        f = 0
        if dy < 0:
            dy *= -1
            sy = -1
        else:
            sy = 1
        if dx < 0:
            dx *= -1
            sx = -1
        else:
            sx = 1
        if dx >= dy:
            while x0 != x1:
                f = f + dy
                if f >= dx:
                    if self.grid[x0+((sx - 1)/2)][y0 + ((sy - 1)/2)]:
                        return False
                    y0 = y0 + sy
                    f = f - dx
                if f != 0 and self.grid[x0 + ((sx - 1)/2)][y0 + ((sy - 1)/2)]:
                    return False
                if dy == 0 and self.grid[x0+((sx - 1)/2)][y0] and self.grid[x0 + ((sx - 1)/2)][y0 - 1]:
                    return False
                x0 = x0 + sx
        else:
            while y0 != y1:
                f = f + dx
                if f >= dy:
                    if self.grid[x0 + ((sx - 1)/2)][y0+((sy - 1)/2)]:
                        return False
                    x0 = x0+sx
                    f = f - dy
                if f != 0 and self.grid[x0 + ((sx - 1)/2)][y0 + ((sy - 1)/2)]:
                    return False
                if dx == 0 and self.grid[x0][y0 + ((sy -1)/2)] and self.grid[x0 - 1][y0+((sy-1)/2)]:
                    return False
                y0 = y0 + sy
        return True

    def update_vertex(self, s, s1):
        g_old = s1.g
        self.compute_cost(s, s1)
        if s1.g < g_old:
            if s1 in self.open_set:
                self.open_set.remove(s1)
            self.open_set.append(s1)

    def compute_cost(self, s, s1):
        if self.line_of_sight(s.parent, s1):
            # Path 2
            if s.parent.g + self.c(s.parent, s1) < s1.g:
                s1.parent = s.parent
                s1.g = s.parent.g + self.c(s.parent, s1)
        else:
            # Path 1
            if s.g + self.c(s, s1) < s1.g:
                s1.parent = s
                s1.g = s.g + self.c(s, s1)

    def c(self, s, s1):  # Should s1 always be the goal node?
        """returns the length of straight line from vertex s to s1"""
        return (Vector2(s.x, s.y) - Vector2(s1.x, s1.y)).magnitude() * 32  # this might be incorrect

def make_graph(w, h):
    w, h = w + 1, h + 1  # We are making a vertex graph out of a grid map
    nodes = [[Node(x, y) for y in range(h)] for x in range(w)]
    graph = {}
    for x, y in product(range(w), range(h)):
        node = nodes[x][y]
        graph[node] = []
        for i, j in product([-1, 0, 1], [-1, 0, 1]):
            if not (0 <= x + i < w):
                continue
            if not (0 <= y + j < h):
                continue
            graph[nodes[x][y]].append(nodes[x+i][y+j])
    return graph, nodes


class Pathfinding(object):

    _cache = {}

    def __init__(self, map, width, height):
        self.map = map
        self.grid = np.zeros((width, height))
        self.width = width
        self.height = height

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

        graph, nodes = make_graph(self.width, self.height)
        t = ThetaStar(graph, self.grid)
        start, end = nodes[v1[0]][v1[1]], nodes[v2[0]][v2[1]]
        path = t.search(start, end)
        return path

    def clear(self):
        """ Should be called when the map is updated. Clears cache


        """
        self._cache = {}

class CollisionGrid(object):

    def __init__(self, tile_width=48, tile_height=48, width=20, height=20):
        """Grid representation of the collision map

        @param tile_width: Width of one tile in pixels
        @param tile_height: Height of one tile in pixels
        @param width: Number of tiles in the width
        @param height: Number of tiles in the height
        """
        self.grid = np.zeros((width, height))
        mp = cocos.tiles.load_tmx("test.tmx")


    def show(self):
        import cocos

        layer = cocos.layer.Layer()
