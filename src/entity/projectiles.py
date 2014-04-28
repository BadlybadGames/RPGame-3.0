from Box2D import Box2D
import math
import constants
import entity
from cocos import collision_model as cm
from cocos.euclid import Vector2
import game
import util


class Projectile(entity.WorldEntity):
    image = "arrow.png"

    etype = "projectile"
    name = "Projectile"
    friendly = False

    mask_collision = 0b000
    mask_event = 0b101

    def __init__(self, **kwargs):
        super(Projectile, self).__init__()

    def init_physics(self, world):
        _ud = {"type": "projectile",
               "entity": self.eid,
               "mask_collision": self.mask_collision,
               "mask_event": self.mask_event,
               "friendly": self.friendly}  # TODO: keeping a reference to the actual entity might be harmful in multiplayer environment.

        self.body = world.CreateDynamicBody(position=self.position.copy(), linearDamping=4.0,
                                            userData=_ud)

        self.body.CreateCircleFixture(radius=(float(self.size) / constants.PIXEL_TO_METER) / 2, restitution=0)


    def update(self, t):
        super(Projectile, self).update(t)

        self.duration -= t
        if self.duration <= 0:
            self.die()

    def update_movement(self, t):
        super(Projectile, self).update_movement(t)

    def update_collision(self):
        return cm.CircleShape(center=self.position, r=self.size)

    def on_collision(self, other, typ):

        if typ == "wall":
            self.die()
            return

        success = False
        owner = game.Game.get_entity(self.controlled_by)
        if not owner:
            return

        if other is owner:
            return

        self.on_hit(other)

    def on_hit(self, other):
        """Called when a collision occurs"""
        other.take_damage(self.damage)
        self.die()

    def get_real_owner(self):
        return game.Game.get_entity(self.controlled_by)


class MeleeWeaponEntity(Projectile):
    """
    Important parameters:

    Offset: length from center of player to center of collision detection
    Arc: Swing arc
    Size: Size used for collision detection
    """
    name = "MeleeWeaponEntity"
    etype = "Projectile"

    def __init__(self, **kwargs):
        self.controlled_by = None  # set after initialization
        self.image = "sword.png"
        super(MeleeWeaponEntity, self).__init__()

    def init_physics(self, world):
        owner = self.get_real_owner()

        _ud = {"type": "projectile",
               "entity": self.eid,
               "mask_collision": self.mask_collision,
               "mask_event": self.mask_event,
               "friendly": self.friendly}  # TODO: keeping a reference to the actual entity might be harmful in multiplayer environment.

        self.body = world.CreateDynamicBody(position=self.position.copy(), linearDamping=0.0,
                                            userData=_ud)

        t = owner.rotation


        fixture = self.body.CreatePolygonFixture(box=(self.width / 2, self.length / 2), density=1, friction=0.1)

        self.body.angle=t


        self.joint = world.CreateRevoluteJoint(bodyA=self.body, bodyB=owner.body, anchor=owner.body.worldCenter, enableMotor=True,
                                               motorSpeed=50.0, maxMotorTorque=10.0)

    def _init_sprite(self, sprite):  # TODO: Sprite still isnt centered on player
        sprite.image_anchor = (sprite.image.width/2, 0) #(sprite.image.width/2, sprite.image.height/2)

    def update_sprite(self, t):
        wielder = game.Game.get_entity(self.wielder)
        s = (wielder.size/2.0)
        self.sprite.position = ((self.position.copy() * constants.PIXEL_TO_METER + (s, s)))
        self.sprite.rotation = self.rotation

    def update(self, t):
        super(MeleeWeaponEntity, self).update(t)

        wielder = game.Game.get_entity(self.wielder)

        #print(self.joint.angle)
        self.rotation = self.body.angle  # FIXME: Super dirty
        #swing_v = float(self.arc) / self.duration
        #self.rotation_off = self.rotation_off + swing_v * t
        #self.rotation = wielder.rotation + self.rotation_off

        #self.duration_left -= t
        #if self.duration_left <= 0:
        #   self.die()

    def update_collision(self):
        center = Vector2(*self.position) + util.rot_to_vec(self.rotation) * self.offset
        #print center, self.size
        return cm.CircleShape(center=center, r=self.size)

    def on_hit(self, other):
        other.take_damage(self.damage)


entity.new_entity(MeleeWeaponEntity)
entity.new_entity(Projectile)
