# -*- coding: utf-8 -*-
from itertools import product
import cocos
from cocos.euclid import Vector2

import numpy as np
import collections


### TODO: Remove this, just for reference
class AStar(object):
    def __init__(self, graph):
        self.graph = graph

    def heuristic(self, node, start, end):
        raise NotImplementedError

    def search(self, start, end):
        openset = set()
        closedset = set()
        current = start
        openset.add(current)
        while openset:
            current = min(openset, key=lambda o:o.g + o.h)
            if current == end:
                path = []
                while current.parent:
                    path.append(current)
                    current = current.parent
                path.append(current)
                return path[::-1]
            openset.remove(current)
            closedset.add(current)
            for node in self.graph[current]:
                if node in closedset:
                    continue
                if node in openset:
                    new_g = current.g + current.move_cost(node)
                    if node.g > new_g:
                        node.g = new_g
                        node.parent = current
                else:
                    node.g = current.g + current.move_cost(node)
                    node.h = self.heuristic(node, start, end)
                    node.parent = current
                    openset.add(node)
        return None

class AStarNode(object):
    def __init__(self):
        self.g = 0
        self.h = 0
        self.parent = None

    def move_cost(self, other):
        raise NotImplementedError

####end reference

class Node(object):
    def __init__(self, x, y):
        self.g = 0
        self.h = 0
        self.parent = None
        self.x, self.y = x, y

class ThetaStar(object):
    """Implemtents theta*: http://aigamedev.com/open/tutorials/theta-star-any-angle-paths/

    TODO: Use lazy theta* instead: http://aigamedev.com/open/tutorial/lazy-theta-star/
    TODO: This should be a functional class
    """

    def __init__(self, graph):
        self.graph = graph

    def search(self, start, end):
        open_set = set()
        closed_set = set()
        current = start
        open_set.add(current)
        while open_set:
            current = min(open_set, key=lambda o: o.g + o.h)
            if current == end:
                path = []
                while current.parent:
                    path.append(current)
                    current = current.parent
                path.append(current)
                return path[::-1]
            open_set.remove(current)
            closed_set.add(current)
            for node in self.graph[current]:
                if node in closed_set:
                    continue
                if node in open_set:
                    new_g = current.g + self.c(current, node)
                    if node.g > new_g:
                        node.g = new_g
                        node.parent = current
                else:
                    node.g = current.g + self.c(current, node)
                    node.parent = current
                    open_set.add(node)
        return None


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
        cls.compute_cost(s, s1)
        if s1.g < g_old:
            if s1 in cls.open_list:
                if s1 in cls.open_list:
                    cls.open_list.remove(s1)
                cls.open_list.insert(s1, s1.g + s1.h)

    @classmethod
    def compute_cost(cls, s, s1):
        if cls.line_of_sight(s.parent, s1):
            # Path 2
            if s.parent.g + cls.c(s.parent, s1) < s1.g:
                s1.parent = s.parent
                s1.g = s.parent.g + cls.c(s.parent, s1)
        else:
            # Path 1
            if s.g + cls.c(s, s1) < s1.g:
                s1.parent = s
                s1.g = s.g + cls.c(s, s1)

    @classmethod
    def c(cls, s, s1):
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
        t = ThetaStar(graph)
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
