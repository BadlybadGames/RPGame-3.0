import logging

import cocos
from cocos import euclid
from cocos.euclid import Vector2
import game

logger = logging.getLogger("entity")

types = {}


def new_entity(entity):
    global types

    assert hasattr(entity, "name"), "Entities need a unique name"

    logger.info("Loading entity type with name '%s'", entity.name)
    name = entity.name

    if name in types.items(): #Something with the same name has already been loaded, append _2 to the name
        logger.warning("Entity with name '%s' already exists", name)
        entity.name = entity.name + "_2"
        name = name + "_2"

    types[name] = entity

def get_entity_type(name):
    return types[name]


def load_data():
    """Loads entity data from data files"""
    import player
    import npc
    import projectiles
    import equipment

class Entity(object):
    """A physical or abstract entity

    Physical entites should derive from WorldEntity and will in general be spawned by game
    Abstract entities are simply abstract data that need to be able to be serialized
    """

    etype = "entity"

    def __init__(self):
        self.is_player = False

        #which player_id it is controlled by. 0 means server
        self.controlled_by = 0

    def _init_sprite(self, sprite):
        """Called by game when a sprite is initialized to allow modification of the sprite"""
        pass

    @classmethod
    def from_json(cls, json):
        """Build an object from jsoned data"""
        e = cls()
        e.update_from_json(json)
        return e




    def update(self, t):
        pass

    def update_from_json(self, json):
        for k, v in json.items():
            if k == "eid":  # We dont want to update an eid after the entity has been made. Especially not if its from a client
                continue

            # if isinstance(v, dict):  # The value requires a construction of a type
            #     if v["type"] == "Vector2":
            #         v = euclid.Vector2(v["args"][0], v["args"][1])
            setattr(self, k, v)

    def update_from(self, new):
        # Updates self based on a new entity it should become
        for k in dir(new):
            if k.startswith("_"):  # Ignore builtins
                continue

            if k in ("sprite", "xp_needed"):
                continue

            v = getattr(new, k)

            if callable(v):  # Ignore functions
                continue

            else:
                setattr(self, k, v)

    def to_json(self):
        d = {}
        for k in dir(self):
            if k.startswith("_"):  # Ignore builtins
                continue

            if k in ("sprite", "xp_needed", "body", "ai"):  # TODO: Possibly try to find a cleaner way
                continue

            v = getattr(self, k)

            if callable(v):  # Ignore functions
                continue

            else:
                d[k] = v
        return d


class WorldEntity(Entity):
    """A physical entity that usually has a physical appearance"""

    def __init__(self, position=(0,0)):
        super(WorldEntity, self).__init__()

        self.attached_to = None

        #Movement variables
        self.position = euclid.Vector2(*position)
        self.old_pos = self.position.copy()
        self.rotation = 0
        self.mov_vel = euclid.Vector2(0.0, 0.0)
        self.mov_acc = euclid.Vector2(0.0, 0.0)
        self.move_dir = euclid.Vector2(0.0, 0.0)
        self.movement_speed = 1.0
        self.acc_speed = 200
        self.turn_speed = 400  # Degrees/second
        self.aim = (30, 30)  # Our desired point of target
        self.size = 30

        self.max_hp = 100
        self.hp = self.max_hp

        self.xp_worth = 0
        self.level = 1

        self.attacking = False
        self.attack_cooldown = 0.0

        self.dead = False

    def on_init(self):
        pass

    def update(self, t):
        super(WorldEntity, self).update(t)

        #Set our acceleration according to user input
        self.update_movement(t)

        #See if we want to and can attack
        if self.attacking and self.attack_cooldown < 0:
            self.attack()

        if self.attack_cooldown >= 0:
            self.attack_cooldown -= t

    def update_movement(self, t):
            """This is called by update and explicitly by the server when updating
            input from clients. Override for entities with a non-standard way of updating their position (see: melee
             weapons"""
            self.old_pos = self.position.copy()
            self.mov_acc = self.move_dir * self.acc_speed

            f = self.move_dir * t * self.movement_speed * 930
            self.body.ApplyForceToCenter(force=f, wake=True)
            self.mov_vel += self.mov_acc * t

            #perform friction. Improve pls!
            self.mov_vel = self.mov_vel * ((1 - t) * 0.5)

    def die(self):
        self.on_die()
        game.Game.despawn(self)

    def on_die(self):
        """ Called when we die, should be safe to overload. usually

        """
        pass

    def on_collision(self, other):
        pass

    def take_damage(self, damage):
        """Deal damage to this entity

        @param damage: damage to be dealt
        @return: final damage taken
        """
        self.hp -= damage
        if self.hp <= 0:
            self.die()

        return damage
