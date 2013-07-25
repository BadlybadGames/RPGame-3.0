import cocos
from cocos.director import director
import game.game 

director.init(width=800, height=600, do_not_scale=False,caption="Goblin Fortress!")

game.game.start()