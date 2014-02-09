import cocos
import pyglet
from cocos.director import director
import cocos.menu as menu

import entity

class MainMenu(cocos.menu.Menu):

    def __init__(self):
        super(MainMenu, self).__init__("")

        self.menu_valign = menu.CENTER
        self.menu_halign = menu.CENTER

        items = [
            (menu.MenuItem('Singleplayer', self.on_start)),
            (menu.MenuItem('Host', self.on_host)),
            (menu.MenuItem('Join', self.on_join)),
            (menu.MenuItem('Quit', self.on_quit))
        ]

        self.create_menu(items, menu.shake_back(), menu.shake_back())

    def on_quit(self):
        pyglet.app.exit()

    def on_start(self):
        import game.game

        scene = cocos.scene.Scene()

        scene.add(game.game.start())

        g = game.game.game

        player = entity.get_entity_type("player")()
        player.position.x, player.position.y = (200, 200)

        g.spawn(player)
        g.set_player(player.eid)

        director.push(scene)

    def on_host(self):
        import multiplayer
        import game.game

        scene = cocos.scene.Scene()

        scene.add(game.game.start())
        scene.add(multiplayer.host())

        g = game.game.game

        player = entity.get_entity_type("player")()
        player.position.x, player.position.y = (200, 200)

        g.spawn(player)
        g.set_player(player.eid)

        sword = entity.get_entity_type("BasicMeleeWeapon")(player)
        player.weapon = sword

        director.push(scene)

    def on_join(self):
        import multiplayer
        import game.game

        scene = cocos.scene.Scene()

        scene.add(game.game.start())
        scene.add(multiplayer.join())

        director.push(scene)

