import logging

import cocos
from cocos import euclid

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


def load_data():
    """Loads entity data from data files"""
    execfile("player.py")
    execfile("npc.py")

class Entity(object):
    """An entity found in the game world"""

    etype = "Entity"

    def __init__(self, position=(0,0)):
        self.is_player = False
        if self.image:
            self.sprite = cocos.sprite.Sprite(self.image)

        self.attached_to = None

        #Movement variables
        self.position = euclid.Vector2(*position)
        self.rotation = 0
        self.mov_vel = euclid.Vector2(0.0, 0.0)
        self.mov_acc = euclid.Vector2(0.0, 0.0)
        self.move_dir = euclid.Vector2(0.0, 0.0)
        self.acc_speed = 200
        self.turn_speed = 400  # Degrees/second
        self.aim = (30, 30)  # Our desired point of target
        self.size = 32

        #which player_id it is controlled by. 0 means server
        self.controlled_by = 0

        #init sprite position too
        if self.sprite:
            self.sprite.position = self.position
            self.sprite.rotation = self.rotation

        self.attacking = False
        self.attack_cooldown = 0.0

        self.dead = False

    @classmethod
    def from_json(cls, json):
        """Build an object from jsoned data"""
        e = cls()
        e.update_from_json(json)
        return e

    def update(self, t):
        #Set our acceleration according to user input
        self.mov_acc = self.move_dir * self.acc_speed

        self.position += self.mov_vel * t + (self.mov_acc * t / 2)
        self.mov_vel += self.mov_acc * t

        #perform friction. Improve pls!
        self.mov_vel = self.mov_vel * ((1 - t) * 0.5)

        #See if we want to and can attack
        if self.attacking and self.attack_cooldown < 0:
            self.attack()
            self.attack_cooldown += self.weapon.attack_speed

        if self.attack_cooldown >= 0:
            self.attack_cooldown -= t

        #update display accordingly
        if self.sprite:
            #Interpolation
            self.sprite.position = (self.sprite.position + self.position) / 2
            self.sprite.rotation = (self.sprite.rotation + self.rotation) / 2

    def update_from_json(self, json):
        for k, v in json.items():
            if k == "eid":  # We dont want to update an eid after the entity has been made. Especially not if its from a client
                continue

            # if isinstance(v, dict):  # The value requires a construction of a type
            #     if v["type"] == "Vector2":
            #         v = euclid.Vector2(v["args"][0], v["args"][1])
            setattr(self, k, v)

    def to_json(self):
        d = {}
        for k in dir(self):
            if k.startswith("_"):  # Ignore builtins
                continue

            if k in ("sprite",):
                continue

            v = getattr(self, k)

            if callable(v):  # Ignore functions
                continue

            else:
                d[k] = v
        return d

    def die(self):
        if not self.dead:
            from game.game import game
            self.dead = True
            game.despawn(self)

    def on_collision(self, other):
        pass

