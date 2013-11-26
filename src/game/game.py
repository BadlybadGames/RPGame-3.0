import cocos
from cocos.director import director
from cocos import collision_model as cm

import entity.player
import equipment


game = None
layer = None


def start():
    global game
    global layer

    #Setup the game
    layer = cocos.layer.Layer()
    game = Game()

    player = entity.player.Player(position=(200, 200))
    player.weapon = equipment.BowWeapon(player)

    enemy = entity.BasicEnemy(position=(400, 400))

    game.spawn(enemy)

    #Setup controls
    import interface.controls  # TODO: Add init functions for modules so late import isnt needed
    c = interface.controls.init()
    layer.add(c)

    game.spawn(player)
    game.set_player(player.eid)
    layer.schedule(game.update)

    return layer


class Game():
    """Game state

    Handles both game state and in-game world state

    """

    def __init__(self):
        self.entities = {}
        self.controlled_player = None
        self.tick = 0

        w, h = director.get_window_size()
        cell_size = 64*1.25  # The size used for grids for the collision manager
        self.collision = cm.CollisionManagerGrid(0, w, 0, h, cell_size, cell_size)

    def update(self, t):
        self.collision.clear()

        #Update position then velocity
        self.tick += t
        for i in self.entities.values():
            self.update_entity(i, t)

        #Assuming all entities have collision
        for e in self.entities.values():
            e.update_collision()
            self.collision.add(e)

        self.run_collision()

    def run_collision(self):
        for a, b in self.collision.iter_all_collisions():
            print "Collision!"
            #check if the types of the two should result in collision
            if any(
                ((a.etype == "projectile" and b.etype == "projectile"),)
                ):
                continue

            a.on_collision(b)
            b.on_collision(a)

    def update_entity(self, ent, t):
        ent.update(t)

    def get_entity(self, eid):
        return self.entities.get(eid)

    def get_player(self):
        return self.get_entity(self.controlled_player)

    def set_player(self, eid):
        self.controlled_player = eid

    def spawn(self, e):
        if not hasattr(e, "eid"):
            e.eid = len(self.entities) + 1
        self.entities[e.eid] = e

        if e.attached_to:
            anchor = self.get_entity(e.attached_to)
            anchor.sprite.add(e.sprite)
        else:
            print "added: ", e.sprite
            layer.add(e.sprite)

    def despawn(self, e):
        if e.sprite:
            print "Want to remove: ", e.sprite
            layer.remove(e.sprite)
