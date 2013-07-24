import cocos.actions import *

class SetMovementDirection(InstantAction):

	def init(self, direction):
		self.direction = direction

	def start(self):
		self.target.movement_direction = self.direction