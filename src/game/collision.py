__author__ = 'Sebsebeleb'

import numpy as np

import cocos.tiles

import _pathfinding

pathf = None
tw = 0
th = 0


class MapCollider(cocos.tiles.RectMapCollider):
    """Makes sure entities confirm to the map.

    Is equivalent to cocos2d's RectMapCollider except it does not check for tile properties (the map should be
    the collision layer => all tiles are obstacles)
    """
    def do_collision(self, cell, last, new, dy, dx):
        if last.bottom >= cell.top > new.bottom:
            dy = last.y - new.y
            new.bottom = cell.top
            if dy: self.collide_bottom(dy)
        if last.right <= cell.left < new.right:
            dx = last.x - new.x
            new.right = cell.left
            if dx: self.collide_right(dx)
        if last.left >= cell.right > new.left:
            dx = last.x - new.x
            new.left = cell.right
            if dx: self.collide_left(dx)
        if last.top <= cell.bottom < new.top:
            dy = last.y - new.y
            new.top = cell.bottom
            if dy: self.collide_top(dy)
        return dx, dy

def init_collision(collision_layer):
    """Initalizes the collision map used for pathfinding with the layer passed

    @param collision_layer: RectMapLayer loaded from a tiled map to be used as collision
    """
    global pathf, tw, th

    tw = collision_layer.tw
    th = collision_layer.th

    w, h = len(collision_layer.cells), len(collision_layer.cells[0])
    pathf = _pathfinding.Pathfinding(w, h)
    for x, _xcell in enumerate(collision_layer.cells):
        for y, cell in enumerate(_xcell):
            if cell.tile:
                pathf.grid[x, y] = True
            else:
                pathf.grid[x, y] = False


def get_path(start, goal):
    """

    @param start: Start position in world position
    @param goal: Goal position in world position
    @return: List of path waypoints in world positions
    """

    # Converts from world position to closest vertex in the grid
    x1 = int(max(0, min(round(start[0] / tw), pathf.width-1)))
    y1 = int(max(0, min(round(start[1] / th), pathf.height-1)))
    x2 = int(max(0, min(round(goal[0] / tw), pathf.width-1)))
    y2 = int(max(0, min(round(goal[1] / th), pathf.height-1)))


    path = pathf.get_path((x1, y1), (x2, y2))
    if not path:
        return None

    array = (np.array([(n.x, n.y) for n in path]) * (tw, th))[1:]

    return array.tolist()

def get_map_grid():
    """Returns array of static collision map"""
    return pathf.grid
