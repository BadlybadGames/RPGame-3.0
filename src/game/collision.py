__author__ = 'Sebsebeleb'

import numpy as np

import _pathfinding

pathf = None
tw = 0
th = 0


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
