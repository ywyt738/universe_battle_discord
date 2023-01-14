from discord.ext import commands


class PlayerNotExist(commands.CheckFailure):
    """玩家还未加入游戏"""


class PlayerExist(commands.CheckFailure):
    """玩家已经存在"""


class ActionPointNotEnough(BaseException):
    """玩家体力不足"""
