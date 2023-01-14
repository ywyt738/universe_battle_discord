"""single pattern bot"""
import discord
from discord.ext import commands

from game import config
from game.log import logger

from .task import clear_buff

intents = discord.Intents.default()
intents.members = True  # pylint: disable=assigning-non-slot
intents.message_content = True  # pylint: disable=assigning-non-slot


class HelpCommand(commands.DefaultHelpCommand):
    """帮助命令"""

    def __init__(self):
        super().__init__()
        self.no_category = "其他"
        self.command_attrs["help"] = "显示命令帮助"

    # def get_ending_note(self):
    #     return "银河星云之战@UG"


BOT = commands.Bot(
    command_prefix="g.",
    help_command=HelpCommand(),
    intents=intents,
    proxy=config.proxy,
)


# 事件处理
@BOT.event
async def on_ready():
    """机器人ready"""
    logger.info(f"Bot have logged in as {BOT.user}")
    clear_buff.start()


@BOT.event
async def on_command_error(ctx, error):
    """命令错误处理"""
    match type(error).__name__:
        case "PlayerExist":
            await ctx.reply(error)
        case _:
            logger.error(error)
