import cocos
from cocos.director import director
from cocos import collision_model as cm
from cocos.euclid import Vector2
from cocos.rect import Rect
import pyglet
import Box2D

import logging
from game import collision

logger = logging.getLogger()
from collections import namedtuple

import entity
import events
import level
import audio
import tilemap

import interface.gui

LERP_TIME = 0.1
LERP_MAX_VEL = 80

PIXEL_TO_METER = 20.0  # Conversion rate of physics meter to screen pixels

# TODO: Get rid of these global variables. Possibly use director.scene or director functions instead?
game = None
layer = None
scroller = None


def start():
    global scroller
    global game
    global collision_map

    #Setup the game
    #The scene structure is like this:
    #Scene
    #  ScrollingManager
    #    ScrollingLayer
    #      Batch
    #    TileMap
    #  Layer
    #    Controls
    #    Gui

    scroller = cocos.layer.ScrollingManager()
    scrolling_layer = cocos.layer.ScrollableLayer()
    scroller.s_layer = scrolling_layer  # TODO: Ugh it reeks of nastiness
    layer = cocos.layer.Layer()
    game = Game()

    scroller.add(scrolling_layer)

    lvl = level.BasicLevel()
    game.set_level(lvl)
    audio.play_music()

    #load game data
    entity.load_data()

    batch = cocos.batch.BatchNode()
    game.sprite_batch = batch
    scrolling_layer.add(batch)

    #load the map
    background, collision_map = tilemap.init()
    scroller.add(background, z=-2)
    scroller.add(collision_map, z=-1)
    scroller.add(scrolling_layer)

    #initalize the pathfinding map
    collision.init_collision(collision_map)

    #initalize the general collision system
    grid = collision.get_map_grid()
    for x, i in enumerate(grid):
        for y, tile in enumerate(i):
            if tile:
                # TODO: non-static tile width/height
                scale = 32.0/PIXEL_TO_METER
                body = game.collision_world.CreateStaticBody(
                    position=(x*scale, y*scale),
                )
                body.CreatePolygonFixture(box=(scale, scale))

    #add an enemy for testing purposes
    #enemy = entity.get_entity_type("basicenemy")()
    #enemy.position = Vector2(100, 100)
    #enemy.movement_speed = 0.35
    #game.spawn(enemy)

    #Setup controls
    import interface.controls  # TODO: Add init functions for modules so late import isnt needed
    c = interface.controls.init()
    layer.add(c)

    scrolling_layer.schedule(game.update)
    scrolling_layer.schedule(game.update_render)

    #Load the gui
    game.gui = interface.gui.Gui()  # TODO: would be better to have this is instance in the interface package
    layer.add(game.gui)
    game.gui.log.add_message("Welcome to RPGame.")
    return game, layer, scroller


class Game():
    """Game state

    Handles both game state and in-game world state

    """

    def __init__(self):
        self.player_id = 0 # Our client id, 0 means server/single player/not yet set.
        self.entities = {}
        self.local_entities = {}
        self.controlled_player = None
        self.tick = 0
        self.entity_count = 0
        self.local_entity_count = 0

        w, h = director.get_window_size()
        cell_size = 64*1.25  # The size used for grids for the collision manager
        self.collision = cm.CollisionManagerGrid(0, w, 0, h, cell_size, cell_size)
        self.tile_collider = collision.MapCollider()
        self.collision_world = Box2D.b2World(gravity=(0, 0))

    def update(self, t):
        #Update position then velocity
        self.tick += t

        #update the level
        #self.level.on_update(t)

        for i in self.get_entities():
            self.update_entity(i, t)

        #Assuming all entities have collision
        for e in self.get_entities():
            # Update physics body movement
            v = e.move_dir.copy()
            if v.magnitude() > 1.0:
                v.normalize()
            v *= e.movement_speed * 5.0  # Meters per tick at 100% movementspeed
            #e.body.linearVelocity = v.copy()

            # The collision detection requires objects with .cshape attributes, so we do this.
            obj = namedtuple('Shape', ("cshape", "entity"))
            obj.cshape = e.update_collision()
            obj.entity = e
            self.collision.add(obj)

        #self.run_collision()
        self.run_physics(t)

    def update_render(self, t):
        player = game.get_player()
        if player:  # Update scrolling layer
            scroller.set_focus(*(player.position * PIXEL_TO_METER), force=True)
        for e in self.get_entities():
            if e.sprite:
                e.sprite.position = e.position.copy()*PIXEL_TO_METER
                e.sprite.rotation = e.rotation
                if False:
                    #Interpolation
                    #Interpolate over LERP_TIME
                    # TODO: Do not interpolate local objects/objects owned by us
                    v = e.position/PIXEL_TO_METER - e.sprite.position
                    if v.magnitude() > LERP_MAX_VEL:
                        e.sprite.position = e.position*PIXEL_TO_METER
                    else:
                        e.sprite.position += (v * t / LERP_TIME)*PIXEL_TO_METER
                    e.sprite.rotation = (e.sprite.rotation + e.rotation) / 2

    def run_physics(self, dt):
        world = self.collision_world

        PHYS_VEL_ITERS = 10
        PHYS_POS_ITERS = 10  # box2d simulation parameters

        world.Step(dt, PHYS_POS_ITERS, PHYS_VEL_ITERS)

        world.ClearForces()
        for e in self.get_entities():
            e.position.x = e.body.position.x
            e.position.y = e.body.position.y

    def run_collision(self):
        self.collision.clear()

        # First we check the tile map collision
        for e in self.get_entities():
            last = Rect(e.old_pos.x, e.old_pos.y, width=e.size, height=e.size)
            new = Rect(e.position.x, e.position.y, width=e.size, height=e.size)
            dx, dy = e.position - e.old_pos

            self.tile_collider.collide_map(collision_map, last, new, dx, dy)

            e.position = Vector2(*new.bottomleft)

        # Then entity collision
        for a, b in self.collision.iter_all_collisions():
            a = a.entity
            b = b.entity
            #check if the types of the two should result in collision
            if any((a.etype == "projectile" and b.etype == "projectile",)):
                continue

            a.on_collision(b)
            b.on_collision(a)

    def update_entity(self, ent, t):
        ent.update(t)

    def set_level(self, lvl):
        self.level = lvl

    def get_entity(self, eid):
        return self.entities.get(eid)

    def get_player(self):
        return self.get_entity(self.controlled_player)

    def get_players(self):
        """ Returns entities (not eids) that are considered players

        """
        return (self.get_entity(i) for i in self.entities if i and self.get_entity(i).is_player)

    def get_entities(self):
        r = [e for e in self.entities.values() + self.local_entities.values() if e is not None]
        return r

    def set_player(self, eid):
        self.controlled_player = eid

    def set_player_id(self, i):
        self.player_id = i

    def get_player_id(self):
        return self.player_id

    def is_controlled(self, entity):
        return entity.controlled_by == self.get_player_id()

    def is_client(self):
        return self.player_id != 0

    def spawn(self, e, force=False):
        """Spawn an entity to the game world

        e: type of entity that should be spawned
        force: if True will ignore regular checks that would prevent the spawning
        """
        if not force:
            # First figure out if we should spawn
            if not e.controlled_by == self.get_player_id():
                return

        if not force and self.is_client(): # We need confirmation from the server
            if not hasattr(e, "eid"):
                e.eid = self.local_entity_count + 1
                self.local_entity_count += 1
            self.local_entities[e.eid] = e
        else:
            if not hasattr(e, "eid"):
                e.eid = self.entity_count + 1
                self.entity_count += 1
            self.entities[e.eid] = e

        if e.image:
            img = pyglet.resource.image(e.image)
            e.sprite = cocos.sprite.Sprite(img)
            e.sprite.position = e.position.copy() * PIXEL_TO_METER
            e._init_sprite(e.sprite)
            #if e.attached_to:
            #    anchor = self.get_entity(e.attached_to)
            #    anchor.sprite.add(e.sprite)
            #else:
            self.sprite_batch.add(e.sprite)

        #Physics body, this should be in WorldEntity, not here.
        if e.etype == "projectile":
            e.body = self.collision_world.CreateKinematicBody(position=e.position.copy())
            e.body.CreateCircleFixture(radius=(e.size/PIXEL_TO_METER)/2, restitution=0, density=0.2)
        else:
            e.body = self.collision_world.CreateDynamicBody(position=e.position.copy(), linearDamping=4.0)
            e.body.CreateCircleFixture(radius=(e.size/PIXEL_TO_METER)/2, restitution=0)

        e.on_init()

    def despawn(self, e):
        if e.sprite:
            self.sprite_batch.remove(e.sprite)
            e.sprite = None
        if e.eid in self.local_entities.keys():
            self.local_entities[e.eid] = None # It is now dead
        if e.eid in self.entities.keys():
            self.entities[e.eid] = None # DEAD!
        if hasattr(e, "body"):
            self.collision_world.DestroyBody(e.body)


    def get_entity_type(self, name):
        return entity.types["name"]
