"""Schedule Task"""
import datetime

from discord.ext import tasks

from game import db
from game.log import logger


@tasks.loop(seconds=5)
async def clear_buff():
    """清理过期buff/debuff"""
    query = db.PlayerBuff.delete().where(
        db.PlayerBuff.expire_time < datetime.datetime.now()
    )
    count = query.execute()
    logger.info(f"清理{count}条buff/debuff")


@tasks.loop(time=datetime.time(hour=0, minute=0))
async def reset_ap():
    """重置体力"""
    all_players = db.Player.select()
    for user in all_players:
        if user.ap < 5:
            user.ap = 5
            user.save()
    logger.info("重置体力完成")
