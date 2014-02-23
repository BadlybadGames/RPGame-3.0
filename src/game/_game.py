import cocos
from cocos.director import director
from cocos import collision_model as cm
import pyglet

import logging
logger = logging.getLogger()
from collections import namedtuple

import entity
import events
import level
import audio
import tilemap

import interface.gui

LERP_TIME =  0.1
LERP_MAX_VEL = 80

# TODO: Get rid of these global variables. Possibly use director.scene or director functions instead?
game = None
layer = None
scroller = None


def start():
    global scroller
    global game

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

    background, collision = tilemap.init()
    scroller.add(background)
    scroller.add(collision)
    scroller.add(scrolling_layer)

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

    def update(self, t):
        self.collision.clear()

        #Update position then velocity
        self.tick += t

        #update the level
        self.level.on_update(t)

        for i in self.get_entities():
            self.update_entity(i, t)

        #Assuming all entities have collision
        for e in self.get_entities():
            # The collision detection requires objects with .cshape attributes, so we do this.
            obj = namedtuple('Shape', ("cshape", "entity"))
            obj.cshape = cm.CircleShape(center=e.position, r=e.size)
            obj.entity = e
            self.collision.add(obj)

        self.run_collision()

    def update_render(self, t):
        player = game.get_player()
        if player:  # Update scrolling layer
            scroller.set_focus(*player.position, force=True)

        for e in self.get_entities():
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
        """ Returns entities that are considered players

        """
        return (i for i in self.entities if i.is_player)

    def get_entities(self):
        return (e for e in self.entities.values() + self.local_entities.values() if e)

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
            e._init_sprite(e.sprite)
            #if e.attached_to:
            #    anchor = self.get_entity(e.attached_to)
            #    anchor.sprite.add(e.sprite)
            #else:
            self.sprite_batch.add(e.sprite)

        e.on_init()

    def despawn(self, e):
        if e.sprite:
            self.sprite_batch.remove(e.sprite)
            e.sprite = None
        if e.eid in self.local_entities.keys():
            self.local_entities[e.eid] = None # It is now dead
        if e.eid in self.entities.keys():
            self.entities[e.eid] = None # DEAD!

    def get_entity_type(self, name):
        return entity.types["name"]
