"""single pattern bot"""
import discord

from game import config
from game.log import logger

from .task import clear_buff, reset_ap

intents = discord.Intents.default()
intents.members = True  # pylint: disable=assigning-non-slot
intents.message_content = True  # pylint: disable=assigning-non-slot


BOT = discord.Bot(intents=intents, proxy=config.proxy)


# 事件处理
@BOT.event
async def on_ready():
    """机器人ready"""
    logger.info(f"Bot have logged in as {BOT.user}")
    clear_buff.start()
    reset_ap.start()


@BOT.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    """命令错误处理"""
    match type(error).__name__:
        case "PlayerExist" | "PlayerNotExist":
            await ctx.respond(error)
        case "MissingRole":
            await ctx.respond("请先加入游戏。")
        case _:
            logger.error(error)
