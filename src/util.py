"""Various functional functions"""

from math import *


def points_to_rotation(p1, p2=None):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    x, y = x2 - x1, y2 - y1

    if x == 0 and y == 0:
        pass
    else:
        r = degrees(acos(x / sqrt(x ** 2 + y ** 2)))
        if y < 0:
            r = r + 90
        else:
            r = 90 - r
    return r


def vec_to_rot(vec):
    """vec_to_rot(x,y) -> degrees

    Should be reflection of rot_to_vec

    """
    x, y = vec

    if x == 0 and y == 0:
        r = 0
    else:
        r = degrees(acos(float(x) / sqrt(float(x) ** 2 + float(y) ** 2)))
        if y < 0:
            r = r + 90
        else:
            r = 90 - r
    return r


def rot_to_vec(r):
    """rot_to_vec(r) -> (x,y)

    Should be reflection of vec_to_rot

    """
    r = radians(r)

    y = cos(r)
    x = sin(r)
    return (x, y)