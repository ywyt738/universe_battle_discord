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
