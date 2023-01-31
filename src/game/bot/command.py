"""bot command"""
import discord
import discord.utils
from discord.ext import commands

from game import config, skill
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
    players_rank,
)
from game.player import Player
from utils.checks import new_player


class User(commands.Cog, name="玩家命令"):
    """玩家"""

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="join")
    @new_player()
    async def _join(self, ctx: discord.ApplicationContext):
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
        await ctx.respond(embed=embed_welcome, ephemeral=True)
        await ctx.respond(embed=player_info_msg(player), ephemeral=True)

    @discord.slash_command(name="go")
    @commands.has_role("uvplayer")
    async def _go(self, ctx: discord.ApplicationContext):
        """消耗一点体力向赛场航线前方移动1-3格。"""
        player: Player = Player(discord_id=ctx.author.id)
        try:
            res, steps = player.move()
        except ActionPointNotEnough:
            await ctx.respond(USER_ACTION_POINT_IS_NOT_ENOUGH, ephemeral=True)
        else:
            if res:
                await ctx.respond(USER_FORWARD_SUCCESS.format(steps), ephemeral=True)
                event = get_board_event(player)
                await event.trigger(ctx)
            else:
                await ctx.respond(USER_CANT_FORWARD, ephemeral=True)

    @discord.slash_command(name="use")
    @commands.has_role("uvplayer")
    async def _use_item(
        self,
        ctx: discord.ApplicationContext,
        item_name: str,
        target_player: discord.User = None,
    ):
        """使用道具"""
        player = Player(discord_id=ctx.author.id)
        init_cell = player.cell
        item_count = PlayerItems.how_many(player_id=ctx.author.id, item_name=item_name)
        item = ENABLE_ITEM.get(item_name)(
            player=ctx.author, target_player=target_player
        )
        if item_count:
            item.use()
            await ctx.respond(item.response, ephemeral=True)
        else:
            await ctx.respond(USER_USE_ITEM_FAIL.format(item_name), ephemeral=True)
        if player.player.cell != init_cell:
            event = get_board_event(player)
            await event.trigger(ctx)

    @discord.slash_command(name="info")
    @commands.has_role("uvplayer")
    async def _myinfo(self, ctx: discord.ApplicationContext):
        """查看自身的游戏进程/拥有的道具信息/使用的道具次数/使用的技能次数/体力/位置"""
        player = Player(discord_id=ctx.author.id)
        embed = player_info_msg(player)
        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="skill")
    @commands.has_role("uvplayer")
    async def _skill(
        self,
        ctx: discord.ApplicationContext,
        skill_name: str,
        target: discord.User = None,
    ):
        """使用技能"""
        player = Player(discord_id=ctx.author.id)
        init_cell = player.cell
        player_camps = config.camps[player.camp]
        if skill_name in config.camps_skill[player_camps]:
            player_skill = skill.create(player, skill_name)
            player_skill.release(target)
            await ctx.respond("技能使用成功。", ephemeral=True)
        else:
            await ctx.respond("你所在阵营没有该技能。", ephemeral=True)
        if player.player.cell != init_cell:
            event = get_board_event(player)
            await event.trigger(ctx)

    @discord.slash_command(name="rank")
    @commands.has_role("uvplayer")
    async def _rank(self, ctx: discord.ApplicationContext):
        """排名"""
        embed = players_rank(Player.rank())
        await ctx.respond(embed=embed, ephemeral=True)


class Admin(commands.Cog, name="管理员命令"):
    """管理员"""

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="ap")
    @commands.has_role("uvadmin")
    async def _ap(
        self, ctx: discord.ApplicationContext, user: discord.User, count: int
    ):
        """【管理员命令】为玩家增加体力"""
        player = Player(discord_id=user.id)
        player.add_ap(count=count)
        await ctx.respond(
            ADMIN_AP_SUCCESS.format(user=user.name, count=count), ephemeral=True
        )

    @discord.slash_command(name="item")
    @commands.has_any_role("uvadmin")
    async def _item(
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
        item_name: str,
        count: int,
    ):
        """【管理员命令】给玩家道具"""
        result = PlayerItems.add(player_id=user.id, item_name=item_name, count=count)
        if result:
            await ctx.respond(
                ADMIN_ITEM_SUCCESS.format(user=user.name, item=item_name, count=count),
                ephemeral=True,
            )
        else:
            await ctx.respond(ADMIN_ITEM_NOT_EXIST.format(item_name), ephemeral=True)
