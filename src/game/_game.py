from Box2D.Box2D import b2ContactListener
import cocos
from cocos.director import director
from cocos import collision_model as cm
from cocos.euclid import Vector2
from cocos.rect import Rect
import time
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
import constants
import resources

import interface
import interface.gui


LERP_TIME = 0.1
LERP_MAX_VEL = 80

# TODO: Get rid of these global variables. Possibly use director.scene or director functions instead?
game = None
layer = None
scroller = None


def start():
    global scroller
    global game
    global collision_map

    resources.init()

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
                scale = 64.0 / constants.PIXEL_TO_METER
                body = game.collision_world.CreateStaticBody(
                    position=(x * scale, y * scale),
                    userData = {"type": "wall",
                                "friendly": False,
                                "mask_collision": 0b110,
                                "mask_event": 0b000}
                )
                body.CreatePolygonFixture(box=(scale/2.0, scale/2.0))

    #add an enemy for testing purposes
    #enemy = entity.get_entity_type("basicenemy")()
    #enemy.position = Vector2(100, 100)
    #enemy.movement_speed = 0.35
    #game.spawn(enemy)

    #Setup controls
    import interface.controls  # TODO: Add init functions for modules so late import isnt needed

    interface.gui.init()  # TODO: Figure out why it has to go here instead of earlier

    c = interface.controls.init()
    layer.add(c)

    scrolling_layer.schedule(game.update)
    #scrolling_layer.schedule(game.update_render)

    #Load the gui
    game.gui = interface.gui.Gui()  # TODO: would be better to have this is instance in the interface package
    layer.add(game.gui)
    game.gui.log.add_message("Welcome to RPGame.")
    return game, layer, scroller


# TODO: Should there be a physics.py module for this + other physics stuff?
class _ContactListener(Box2D.b2ContactListener):

    def BeginContact(self, contact):
        a, b = contact.fixtureA, contact.fixtureB
        if a.sensor ^ b.sensor:
            sensor, other = a.sensor and (a, b) or (b, a)
            entity = sensor.body.userData.get("entity")
            if not sensor in game.sensor_detections.keys():
                game.sensor_detections[sensor.userData["sid"]] = [entity, []]
            typ, other_entity = other.body.userData["type"], other.body.userData.get("entity")
            game.sensor_detections[sensor.userData["sid"]][1].append((typ, other_entity))

    def EndContact(self, contact):
        a, b = contact.fixtureA, contact.fixtureB
        if a.sensor ^ b.sensor:
            sensor, other = a.sensor and (a, b) or (b, a)

            entity = sensor.body.userData.copy().get("entity")
            #if entity and entity.dead:  # If they are dead, we ignore them
            #    del(game.sensor_callbacks[sensor])

            if sensor.userData["sid"] in game.sensor_detections.keys():
                typ = other.body.userData.get("type")
                if not typ or typ == "projectile":
                    return
                other_entity = other.body.userData.get("entity")
                if game.sensor_detections[sensor.userData["sid"]] and game.sensor_detections[sensor.userData["sid"]][1]:
                    if (typ, other_entity) in game.sensor_detections[sensor.userData["sid"]][1]:  # FIXME: Destroyed bodies act weird so they arent removed from the callback list. !important!
                        game.sensor_detections[sensor.userData["sid"]][1].remove((typ, other_entity))
                    if len(game.sensor_detections[sensor.userData["sid"]][1]) == 0:
                        del(game.sensor_detections[sensor.userData["sid"]])

    def PreSolve(self, contact, oldManifold):
        """Handles collision events

        Possible cases:
        Entity vs Entity: collide + event
        Entity vs Wall: collide
        Entity vs Projectile: event
        Projectile vs Wall: event (should collide if die?)
        Projectile vs Projectile: Nothing? (or event?)
        """
        #Userdata is the only thing used to resolve collisions
        #type: entity type
        #friendly: friendly to player? if it is, do not generate collision but generate event
        #mask_collision: collision mask
        #mask_event: event mask

        a = contact.fixtureA.body.userData
        b = contact.fixtureB.body.userData


        collision = (a["mask_collision"] & b["mask_collision"]) and not (a["friendly"] and b["friendly"])
        event_a = a["mask_event"] & b["mask_collision"]
        event_b = b["mask_event"] & a["mask_collision"]

        if event_a:
            ent_a = game.get_entity(a.get("entity"))
            ent_b = game.get_entity(b.get("entity"))
            ent_a.on_collision(other=ent_b, typ=b["type"])
        if event_b:
            ent_a = game.get_entity(a.get("entity"))
            ent_b = game.get_entity(b.get("entity"))
            ent_b.on_collision(other=ent_a, typ=a["type"])

        contact.enabled=bool(collision)

    def PostSolve(self, contact, impulse):
        pass


class Game():
    """Game state

    Handles both game state and in-game world state

    """

    def __init__(self):
        self.player_id = 0  # Our client id, 0 means server/single player/not yet set.
        self.entities = {}
        self.local_entities = {}
        self.controlled_player = None
        self.tick = 0
        self.entity_count = 0
        self._sensor_count = 0

        w, h = director.get_window_size()
        cell_size = 64 * 1.25  # The size used for grids for the collision manager
        self.collision = cm.CollisionManagerGrid(0, w, 0, h, cell_size, cell_size)
        self.tile_collider = collision.MapCollider()
        self.collision_world = Box2D.b2World(gravity=(0, 0),
                                             contactListener=_ContactListener())

        self.sensor_detections = {}
        self.sensor_callbacks = {}

    def update(self, t):
        #print time.time()
        #print(t)
        #Update position then velocity
        self.tick += t

        #update the level
        if hasattr(self, "level"):
            self.level.on_update(t)

        for i in self.get_entities():
            self.update_entity(i, t)

        #self.run_collision()
        self.run_physics(t)

        #Update sensor calbacks
        for sensor, data in self.sensor_detections.items():
            sensing_actor = data[0]
            detections = data[1]
            self.sensor_callbacks[sensor](sensing_actor, detections, t)


        self.update_render(t)

    def update_render(self, t):
        player = game.get_player()
        if player:  # Update scrolling layer
            scroller.set_focus(*(player.position * constants.PIXEL_TO_METER), force=True)
        for e in self.get_entities():
            if e.sprite:
                e.update_sprite(t)
                if False:
                    #Interpolation
                    #Interpolate over LERP_TIME
                    # TODO: Do not interpolate local objects/objects owned by us
                    v = e.position / constants.PIXEL_TO_METER - e.sprite.position
                    if v.magnitude() > LERP_MAX_VEL:
                        e.sprite.position = e.position * constants.PIXEL_TO_METER
                    else:
                        e.sprite.position += (v * t / LERP_TIME) * constants.PIXEL_TO_METER
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
        if ent.dead:
            self.despawn(ent)

    def register_sensor(self, sensor, callback):
        self._sensor_count += 1
        sensor.userData = {"sid": self._sensor_count}

        self.sensor_callbacks[sensor.userData["sid"]] = callback

    def set_level(self, lvl):
        self.level = lvl

    def get_entity(self, eid):
        all_entities = dict(self.entities.items() + self.local_entities.items())
        return all_entities.get(eid)

    def get_player(self):
        return self.get_entity(self.controlled_player)

    def get_players(self):
        """ Returns entities (not eids) that are considered players

        """
        ents = dict(self.entities.items()+self.local_entities.items())
        return (e for e in ents.values() if e and e.is_player)

    def get_entities(self):
        """Return all entities in the world

        @rtype: list
        @return: List of entities
        """
        r = [e for e in self.entities.values() + self.local_entities.values() if e is not None]
        return r

    def set_player(self, eid):
        self.controlled_player = eid
        self.set_player_id(eid)

    def set_player_id(self, i):
        """Set the client's player id

        @type i: int
        @param i: Id to set the player id to
        """
        self.player_id = i

    def get_player_id(self):
        """Return the client's player id

        @rtype: int
        @return:
        """
        return self.player_id

    def is_controlled(self, ent):
        """Return True if ent is an entity our player owns

        @type ent: entity.Entity

        @rtype: bool
        """
        return ent.controlled_by == self.get_player_id()

    def is_client(self):
        """
        Return True if we are a client in a multiplayer game.

        @rtype: bool
        @return: True if we are a client in a multiplayer game
        """
        return self.player_id != 0

    def spawn(self, ent, force=False):
        """
        Spawn an entity to the game world

        @type ent: entity.WorldEntity
        @param ent: entity to add to the game world
        @type force: bool
        @param force: if True will ignore regular checks that would prevent the spawning
        """

        if not force and self.is_client():  # We need confirmation from the server
            if not hasattr(ent, "eid"):
                ent.eid = self.entity_count + 1
                self.entity_count += 1
            self.local_entities[ent.eid] = ent
        else:
            if not hasattr(ent, "eid"):
                ent.eid = self.entity_count + 1
                self.entity_count += 1
            self.entities[ent.eid] = ent

        if ent.image:
            img = pyglet.resource.image(ent.image)
            ent.sprite = cocos.sprite.Sprite(img)
            ent.sprite.position = ent.position.copy() * constants.PIXEL_TO_METER
            ent._init_sprite(ent.sprite)
            #if e.attached_to:
            #    anchor = self.get_entity(e.attached_to)
            #    anchor.sprite.add(e.sprite)
            #else:
            self.sprite_batch.add(ent.sprite)

        #Physics body, this should be in WorldEntity, not here.
        #if ent.etype == "projectile":
        #    ent.body = self.collision_world.CreateKinematicBody(position=ent.position.copy())
        #    #e.body.CreateCircleFixture(radius=(e.size/PIXEL_TO_METER)/2, restitution=0, density=0.2)

        ent.init_physics(self.collision_world)

        ent.on_init()

    def despawn(self, ent):
        """Remove an entity from the game world

        @type ent: entity.Entity
        @param ent:
        @return:
        """
        if ent.sprite:
            self.sprite_batch.remove(ent.sprite)
            ent.sprite = None
        if ent.eid in self.local_entities.keys():
            self.local_entities[ent.eid] = None  # It is now dead
        if ent.eid in self.entities.keys():
            self.entities[ent.eid] = None  # DEAD!
        if hasattr(ent, "body") and ent.body:
            for fix in ent.body.fixtures:
                if fix.sensor and fix.userData["sid"] in self.sensor_callbacks.keys():
                    pass
                    #del(self.sensor_callbacks[fix.userData["sid"]])
            self.collision_world.DestroyBody(ent.body)
            del(ent.body)


    def get_entity_type(self, name):
        return entity.types["name"]
