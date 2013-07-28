import cocos
from cocos.director import director

import interface.menus

director.init(width=800, height=600, do_not_scale=False,caption="RPGame 3.0!")

scene = cocos.scene.Scene()
scene.add(interface.menus.MainMenu())

director.run(scene)