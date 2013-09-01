from cocos.actions import *


class SetMovementDirection(InstantAction):

    def init(self, direction):
        self.direction = direction

    def start(self):
        self.target.movement_direction = self.direction

class InterpolateMovement(IntervalAction):

    def init(self, duration, entity, new_position):
        self.duration = duration
        self.entity = entity
        self.new = new_position
        self.old = entity.position

    def update(self, t):
        d = self.entity.position - self.old
        self.target.position = (self.old  + d * t)