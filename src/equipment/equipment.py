from cocos import euclid
import util
import entity
import events
import game
class Equipment(entity.Entity):
    pass

class Weapon(Equipment):
    attack_sounds = ()

    def __init__(self, wielder=None):
        self.wielder = wielder and wielder.eid or None
        self.damage = (1, 6)
        self.attack_speed = 0.20

    def get_wielder(self):
        return game.Game.get_entity(self.wielder)


class BowWeapon(Weapon):
    name = "BasicBow"
    attack_sounds = ("arrow.mp3", )

    def __init__(self, wielder=None):
        super(BowWeapon, self).__init__(wielder)

        self.proj_length = 40
        self.proj_life = 3.0
        self.proj_speed = 10

    def attack(self):
        wielder = self.get_wielder()

        e = entity.get_entity_type("Projectile")()

        e.damage = 20
        e.controlled_by = wielder.controlled_by
        e.position = wielder.position.copy()
        e.duration = self.proj_life
        e.rotation = wielder.rotation
        e.move_dir = euclid.Vector2(*util.rot_to_vec(e.rotation))
        game.Game.spawn(e)
        
        if game.Game.is_controlled(e):
            events.dispatch("on_attack", self.get_wielder(), self, e)


class MeleeWeapon(Weapon):
    name = "BasicMeleeWeapon"
    attack_sounds = ("swish-1.mp3", )

    def __init__(self, wielder=None):
        super(MeleeWeapon, self).__init__(wielder)

        self.width = 5
        self.arc = 120
        self.duration = 1.0
        self.attack_speed = 1.1
        self.offset = 30

    def attack(self):
        real_wielder = self.get_wielder() # The real entity (not the eid)
        e = entity.get_entity_type("MeleeWeaponEntity")()
        e.attached_to = self.wielder
        e.wielder = self.wielder
        e.controlled_by = real_wielder.controlled_by
        e.position = real_wielder.position.copy()
        e.duration = self.duration
        e.duration_left = e.duration
        e.offset = self.offset
        e.arc = self.arc
        e.rotation_off = -self.arc/2
        game.Game.spawn(e)


        if game.Game.is_controlled(e):
            events.dispatch("on_attack", self.get_wielder(), self, e)

weapons = (BowWeapon, MeleeWeapon)

for w in weapons:
    entity.new_entity(w)