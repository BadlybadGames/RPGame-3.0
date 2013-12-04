import cocos
from cocos.director import director
from cocos import collision_model as cm

import logging
from collections import namedtuple

import entity

LERP_TIME =  0.1
LERP_MAX_VEL = 80

game = None
layer = None

def start():
    global game
    global layer

    #load game data
    entity.load_data()

    #Setup the game
    layer = cocos.layer.Layer()
    game = Game()

    batch = cocos.batch.BatchNode()
    game.sprite_batch = batch
    layer.add(batch)

    player = entity.get_entity_type("player")()
    player.position.x, player.position.y = (200, 200)

    #Setup controls
    import interface.controls  # TODO: Add init functions for modules so late import isnt needed
    c = interface.controls.init()
    layer.add(c)

    game.spawn(player)
    game.set_player(player.eid)
    



    layer.schedule(game.update)
    layer.schedule(game.update_render)

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
            # The collision detection requires objects with .cshape attributes, so we do this.
            obj = namedtuple('Shape', ("cshape", "entity"))
            obj.cshape = cm.CircleShape(center=e.position, r=e.size)
            obj.entity = e
            self.collision.add(obj)

        self.run_collision()

    def update_render(self, t):
        for e in self.entities.values():
            if e.sprite:
                #Interpolation
                #Interpolate over LERP_TIME
                # TODO: Do not interpolate local objects/objects owned by us
                v = e.position - e.sprite.position
                if v.magnitude() > LERP_MAX_VEL:
                    e.sprite.position = e.position
                else:
                    e.sprite.position += v * t / LERP_TIME
                e.sprite.rotation = (e.sprite.rotation + e.rotation) / 2

    def run_collision(self):
        for a, b in self.collision.iter_all_collisions():
            a = a.entity
            b = b.entity
            logging.info("Collision between %i and %i", a.eid, b.eid)
            #check if the types of the two should result in collision
            if any((a.etype == "projectile" and b.etype == "projectile",)):
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
            if e.image:
                e.sprite = cocos.sprite.Sprite(e.image)
                self.sprite_batch.add(e.sprite)

    def despawn(self, e):
        if e.sprite:
            logging.info("Want to remove: ", e.sprite)
            self.sprite_batch.remove(e.sprite)

    def get_entity_type(self, name):
        return entity.types["name"]
