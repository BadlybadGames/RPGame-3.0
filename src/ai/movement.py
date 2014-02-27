__author__ = 'Sebsebeleb'


class MoveBasic(object):
    """Ai that tries to move directly (confined to the pathing) to its target"""


    @staticmethod
    def get_next(me, target):
        """ Returns the next position to walk to


        """
        import game.collision

        path = game.collision.get_path(me.position, target.position)

        if not path:
            return False

        if len(path) == 1:  # If there is only one(two?) waypoint left, there's no obstacles so we just move directly
            return target.position
        else:
            return path[0]

