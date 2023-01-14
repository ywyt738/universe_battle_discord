"""bot command"""
import discord
import discord.utils
from discord.ext import commands

from game.board import get_board_event
from game.exception import ActionPointNotEnough
from game.item import ENABLE_ITEM, PlayerItems
from game.message import (
    ADMIN_AP_SUCCESS,
    ADMIN_ITEM_NOT_EXIST,
    ADMIN_ITEM_SUCCESS,
    USER_ACTION_POINT_IS_NOT_ENOUGH,
    USER_CANT_FORWARD,
    USER_FORWARD_SUCCESS,
    USER_USE_ITEM_FAIL,
    WELCOME_DESCRIPTION,
    WELCOME_TITLE,
    player_info_msg,
)
from game.player import Player
from utils.checks import new_player


class User(commands.Cog, name="玩家命令"):
    """玩家"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    @new_player()
    async def _join(self, ctx: commands.Context):
        """加入银河星云之战的游戏。"""
        # 获取用户id
        discord_id = ctx.author.id
        name = ctx.author.name
        player = Player.register(discord_id=discord_id, name=name)
        embed_welcome = discord.Embed(
            colour=discord.Colour(0xF5D0A1),
            title=WELCOME_TITLE,
            description=WELCOME_DESCRIPTION,
        )
        uvplayer_role = discord.utils.get(ctx.guild.roles, name="uvplayer")
        if uvplayer_role in ctx.author.roles:
            pass
        else:
            await ctx.author.add_roles(uvplayer_role)
        await ctx.reply(embed=embed_welcome)
        await ctx.reply(embed=player_info_msg(player))

    @commands.command(name="go")
    @commands.has_role("uvplayer")
    async def _go(self, ctx: commands.Context):
        """消耗一点体力向赛场航线前方移动1-3格。"""
        player: Player = Player(discord_id=ctx.author.id)
        try:
            res, steps = player.move()
        except ActionPointNotEnough:
            await ctx.reply(USER_ACTION_POINT_IS_NOT_ENOUGH)
        else:
            if res:
                await ctx.reply(USER_FORWARD_SUCCESS.format(steps))
                # await ctx.reply(embed=player_info_msg(player))
                event = get_board_event(player)
                await event.trigger(ctx)
            else:
                await ctx.reply(USER_CANT_FORWARD)

    @commands.command(name="use")
    @commands.has_role("uvplayer")
    async def _use_item(
        self,
        ctx: commands.Context,
        item_name: str = None,
        target_player: discord.User = None,
    ):
        """使用道具"""
        item_count = PlayerItems.how_many(player_id=ctx.author.id, item_name=item_name)
        item = ENABLE_ITEM.get(item_name)(
            player=ctx.author, target_player=target_player
        )
        if item_count:
            item.use()
            await ctx.reply(item.response)
        else:
            await ctx.reply(USER_USE_ITEM_FAIL.format(item_name))

    @commands.command(name="info")
    @commands.has_role("uvplayer")
    async def _myinfo(self, ctx: commands.Context):
        """查看自身的游戏进程/拥有的道具信息/使用的道具次数/使用的技能次数/体力/位置"""
        player = Player(discord_id=ctx.author.id)
        embed = player_info_msg(player)
        await ctx.reply(embed=embed)


class Admin(commands.Cog, name="管理员命令"):
    """管理员"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ap")
    @commands.has_role("uvadmin")
    async def _ap(
        self, ctx: commands.Context, user: discord.User = None, count: int = 0
    ):
        """为玩家增加体力"""
        player = Player(discord_id=user.id)
        player.add_ap(count=count)
        await ctx.reply(ADMIN_AP_SUCCESS.format(user=user.name, count=count))

    @commands.command(name="item")
    @commands.has_any_role("uvadmin")
    async def _item(
        self,
        ctx: commands.Context,
        user: discord.User = None,
        item_name: str = None,
        count: int = 0,
    ):
        """给玩家道具"""
        result = PlayerItems.add(player_id=user.id, item_name=item_name, count=count)
        if result:
            await ctx.reply(
                ADMIN_ITEM_SUCCESS.format(user=user.name, item=item_name, count=count)
            )
        else:
            await ctx.reply(ADMIN_ITEM_NOT_EXIST.format(item_name))

    # @commands.command(name="test")
    # async def _test(self, ctx: commands.Context):
    #     role = discord.utils.get(ctx.guild.roles, name="uvplayer")
    #     member = ctx.guild.get_member(ctx.author.id)
    #     await member.add_roles(role)
