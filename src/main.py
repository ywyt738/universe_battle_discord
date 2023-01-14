"""A game bot for UK guild"""


from game import config, db
from game.board import load_map
from game.bot import BOT
from game.buff import load_buff_into_db
from game.item import load_item_into_db

# 初始化数据库
db.init_db()
# 初始化道具
load_item_into_db()
# 初始化buff
load_buff_into_db()
# 加载地图
load_map()
# 启动bot
BOT.run(token=config.token)
