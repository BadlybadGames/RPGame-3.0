import pyglet
from cocos.director import director

import random

import events

def _play(sound, position=None):
	player = pyglet.media.ManagedSoundPlayer()
	src = pyglet.resource.media(sound, streaming=True)
	player.queue(src)
	if position:
		wx, wy = director.get_window_size()
		x = ((position[0] - wx/2.0) / wx * 10) 
		y = ((position[1] - wy/2.0) / wy * 10)
		player.position = x, 0, y
	player.play()
	#src.play()

class SoundHandler(object):

    def on_attack(self, attacker, weapon, entity):
    	if not weapon.attack_sounds:
    		return
        sound = random.choice(weapon.attack_sounds)
        if sound:
        	pos = (attacker.position.x, attacker.position.y)
        	_play(sound, position=pos)

events.handler.push_handlers(SoundHandler())
