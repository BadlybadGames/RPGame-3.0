import entity
from cocos import euclid
import util


class Equipment(object):
    pass


class Weapon(Equipment):

    def __init__(self, wielder):
        self.wielder = wielder
        self.damage = (1, 6)
        self.attack_speed = 0.20


class BowWeapon(Weapon):

    def __init__(self, wielder):
        super(BowWeapon, self).__init__(wielder)

        self.proj_length = 40
        self.proj_life = 3.0
        self.proj_speed = 10

    def attack(self):
        from game.game import game

        e = entity.Projectile(position=self.wielder.position.copy(), duration=self.proj_life)

        e.rotation = self.wielder.rotation
        e.move_dir = euclid.Vector2(*util.rot_to_vec(e.rotation))

        game.spawn(e)


class MeleeWeapon(Weapon):

    def __init__(self, wielder):
        super(MeleeWeapon, self).__init__(wielder)

        self.width = 5
        self.length = 50
        self.duration = 1.0

    def attack(self):
        e = entity.MeleeWeaponEntity(self)
