import pyglet

try:
	player = pyglet.media.Player()
except: # Should except avbin error
	enabled = False
	raise
else:
	enabled = True
	player.volume = 0.2

fall  = "thefallofarcana.mp3"

def play_music():
	if not enabled:
		return

	source = pyglet.resource.media(fall)
	player.queue(source)
	if player.playing:
		player.next()
	else:
		player.play()

def play_song(song_name, repeat=False, fade_out=False):
	source = pyglet.resource.media(song_name)
	player.queue(source)
	if player.playing:
		player.next()
	else:
		player.play()
