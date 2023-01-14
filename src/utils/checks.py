"""命令校验"""
from discord.ext import commands

from game import db
from game.exception import PlayerExist, PlayerNotExist


def new_player():
    """新玩家校验"""

    async def predicate(ctx):
        if db.Player.get_or_none(discord_id=ctx.author.id):
            raise PlayerExist("你已经加入活动。")
        return True

    return commands.check(predicate)
