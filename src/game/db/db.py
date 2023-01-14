"""game model"""
from peewee import (
    BigIntegerField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    SmallIntegerField,
    SqliteDatabase,
    TextField,
)

from game import config
from game.log import logger

database = SqliteDatabase(
    config.database,
    pragmas={
        "journal_mode": "wal",
        "cache_size": -1 * 64000,  # 64MB
        "foreign_keys": 1,
        "ignore_check_constraints": 0,
        "synchronous": 0,
    },
)


class BaseModel(Model):
    """db base model"""

    class Meta:
        """define database"""

        database = database


class Player(BaseModel):
    """玩家 Model"""

    discord_id = BigIntegerField(primary_key=True, unique=True)
    name = CharField()
    ap = SmallIntegerField(default=5)
    board = SmallIntegerField(default=1)
    cell = SmallIntegerField(default=0)
    camp = SmallIntegerField(null=False)


class Item(BaseModel):
    """道具"""

    id = SmallIntegerField(primary_key=True)
    name = CharField()
    describtion = TextField()


class PlayerItems(BaseModel):
    """玩家的道具"""

    player_id = ForeignKeyField(Player)
    item = ForeignKeyField(Item)
    count = SmallIntegerField(null=False, default=0)


class Buff(BaseModel):
    """游戏所有的buff/debuff"""

    id = SmallIntegerField(primary_key=True)
    name = CharField()
    cata = SmallIntegerField(choices=[(0, "buff"), (1, "debuff")])
    describtion = TextField()
    phase = CharField()


class PlayerBuff(BaseModel):
    """玩家的buff/debuff"""

    player_id = ForeignKeyField(Player)
    buff_cata = SmallIntegerField()
    buff = ForeignKeyField(Buff)
    expire_time = DateTimeField()


def init_db():
    """初始化数据库"""
    if not database.get_tables():
        logger.info("创建数据库")
        database.create_tables([Player, PlayerItems, Item, Buff, PlayerBuff])
        logger.info(database.get_tables())
    else:
        database.connect(reuse_if_open=True)
