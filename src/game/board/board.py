"""Game map"""
from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol

from discord.ext import commands
from peewee import fn

from game import db
from game.player import Player


class BoardEvent(Protocol):
    """地图时间Protocol"""

    def trigger(self, ctx: commands.Context) -> None:
        """触发"""


@dataclass
class NonthingEvent:
    """无"""

    player: Player
    desc: str

    async def trigger(self, ctx: commands.Context) -> None:
        """触发事件"""
        await ctx.reply(self.desc)


@dataclass
class TrapEvent:
    """陷阱事件"""

    player: Player
    desc: str

    async def trigger(self, ctx: commands.Context) -> None:
        """触发事件"""
        self.player.apply_affect("禁锢", timedelta(hours=2))
        await ctx.reply(self.desc)


@dataclass
class GetItemEvent:
    """道具事件"""

    player: Player
    desc: str
    item: str
    count: str

    async def trigger(self, ctx: commands.Context) -> None:
        """触发事件"""
        self.player.get_item(item=self.item, count=int(self.count))
        await ctx.reply(self.desc)


@dataclass
class ActionPointResetEvent:
    """体力归零事件"""

    player: Player
    desc: str

    async def trigger(self, ctx: commands.Context) -> None:
        """触发事件"""
        self.player.player.ap = 0
        self.player.player.save()
        await ctx.reply(self.desc)


@dataclass
class MoveEvent:
    """移动事件"""

    player: Player
    desc: str
    step: str

    async def trigger(self, ctx: commands.Context) -> None:
        """触发事件"""
        self.player.player.cell += int(self.step)
        self.player.player.save()
        await ctx.reply(self.desc)


@dataclass
class DropRandomItemEvent:
    """随机丢失道具事件"""

    player: Player
    desc: str

    async def trigger(self, ctx: commands.Context) -> None:
        """触发事件"""
        item_query = (
            db.PlayerItems.select()
            .where(db.PlayerItems.player_id == self.player.player)
            .order_by(fn.Random())
            .limit(1)
        )
        item = item_query[0]
        item.count -= 1
        item.save()
        await ctx.reply(self.desc)
