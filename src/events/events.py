import pyglet


def dispatch(event, *args, **kwargs):
	handler.dispatch_event(event, *args, **kwargs)

handler = pyglet.event.EventDispatcher()

handler.register_event_type("on_shoot")
