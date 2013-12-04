from cocos import euclid
import util
from game.game import game
import entity

class Equipment(entity.Entity):
    pass

class Weapon(Equipment):

    def __init__(self, wielder=None):
        self.wielder = wielder and wielder.eid or None
        self.damage = (1, 6)
        self.attack_speed = 0.20

    def get_wielder(self):
        return game.get_entity(self.wielder)


class BowWeapon(Weapon):
    name = "BasicBow"

    def __init__(self, wielder=None):
        super(BowWeapon, self).__init__(wielder)

        self.proj_length = 40
        self.proj_life = 3.0
        self.proj_speed = 10

    def attack(self):
        wielder = self.get_wielder()
        e = entity.get_entity_type("Projectile")()
        e.position = wielder.position.copy()
        e.duration = self.proj_life
        e.rotation = wielder.rotation
        e.move_dir = euclid.Vector2(*util.rot_to_vec(e.rotation))

        game.spawn(e)


class MeleeWeapon(Weapon):
    name = "BasicMeleeWeapon"

    def __init__(self, wielder=None):
        super(MeleeWeapon, self).__init__(wielder)

        self.width = 5
        self.length = 50
        self.duration = 1.0

    def attack(self):
        e = entity.get_entity_type("MeleeWeaponEntity")

weapons = (BowWeapon, MeleeWeapon)

for w in weapons:
    entity.new_entity(w)