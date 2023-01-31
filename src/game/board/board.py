"""Game map"""
from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol

import discord
from peewee import fn

from game import db
from game.player import Player

from . import factory


class BoardEvent(Protocol):
    """地图事件Protocol"""

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发"""


@dataclass
class NonthingEvent:
    """无"""

    player: Player
    desc: str

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        await ctx.respond(self.desc, ephemeral=True)


@dataclass
class TrapEvent:
    """陷阱事件"""

    player: Player
    desc: str
    duration: int

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        self.player.apply_affect("禁锢", timedelta(minutes=self.duration))
        await ctx.respond(self.desc, ephemeral=True)


@dataclass
class GetItemEvent:
    """道具事件"""

    player: Player
    desc: str
    item: str
    count: int

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        self.player.get_item(item=self.item, count=int(self.count))
        await ctx.respond(self.desc, ephemeral=True)


@dataclass
class ActionPointEvent:
    """体力变化事件"""

    player: Player
    desc: str
    ap: str

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        if self.ap.startswith("+") or self.ap.startswith("-"):
            self.player.player.ap += int(self.ap)
        else:
            self.player.player.ap = self.ap
        self.player.player.save()
        await ctx.respond(self.desc, ephemeral=True)


@dataclass
class MoveEvent:
    """移动事件"""

    player: Player
    desc: str
    step: int

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        self.player.player.cell += int(self.step)
        self.player.player.save()
        await ctx.respond(self.desc, ephemeral=True)


@dataclass
class DropRandomItemEvent:
    """随机丢失道具事件"""

    player: Player
    desc: str

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        item_query = (
            db.PlayerItems.select()
            .where(db.PlayerItems.player_id == self.player.player)
            .order_by(fn.Random())
            .limit(1)
        )
        if item_query:
            item = item_query[0]
            item.count -= 1
            item.save()
            await ctx.respond(self.desc, ephemeral=True)


@dataclass
class DropAllItemEvent:
    """丢失所有物品"""

    player: Player
    desc: str

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        query = db.PlayerItems.delete().where(
            db.PlayerItems.player_id == self.player.player
        )
        query.execute()
        await ctx.respond(self.desc, ephemeral=True)


@dataclass
class DropDropRandomItemWithoutEnoughActionPointEvent:
    """随机丢失道具，在体力无法扣除的情况下事件"""

    player: Player
    desc: str
    decrease_ap: int

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        if self.player.player.ap < self.decrease_ap:
            item_query = (
                db.PlayerItems.select()
                .where(db.PlayerItems.player_id == self.player.player)
                .order_by(fn.Random())
                .limit(1)
            )
            item = item_query[0]
            item.count -= 1
            item.save()
            await ctx.respond(self.desc, ephemeral=True)
        else:
            self.player.player.ap = self.player.player.ap - self.decrease_ap
            self.player.player.save()
            await ctx.respond(self.desc, ephemeral=True)


@dataclass
class LocaionEvent:
    """位置变化事件"""

    player: Player
    desc: str
    cell: int

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        self.player.player.cell = self.cell
        self.player.player.save()
        await ctx.respond(self.desc, ephemeral=True)


class BuffEvent:
    """Buff/Debuff事件"""

    player: Player
    desc: str
    buff_name: str
    duration: int

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        self.player.apply_affect(
            buff=self.buff_name, duration_time=timedelta(minutes=self.duration)
        )
        await ctx.respond(self.desc, ephemeral=True)


@dataclass
class DeathOrAliveEvent:
    """生死门事件"""

    player: Player
    desc: str
    alive: dict
    death: dict

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        bot = ctx.bot
        alive_key = self.alive.pop("key")
        death_key = self.death.pop("key")
        alive_event = factory.create(self.player, self.alive)
        death_event = factory.create(self.player, self.death)
        await ctx.respond(self.desc, ephemeral=True)
        event_funcs: dict[str, BoardEvent] = {
            alive_key: alive_event,
            death_key: death_event,
        }
        while True:
            user_reply = await bot.wait_for(
                "message", check=lambda message: message.author == ctx.author
            )
            event = event_funcs.get(user_reply.content, None)
            if event_funcs:
                await event.trigger(ctx)
                break
            else:
                await ctx.respond(
                    f"输入错误。可以输入的回答：{alive_key}，{death_key}", ephemeral=True
                )


@dataclass
class PortalEvent:
    """传送门事件"""

    player: Player
    desc: str

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        self.player.player.board += 1
        self.player.player.cell = 0
        self.player.player.save()
        await ctx.respond(self.desc, ephemeral=True)


@dataclass
class EndEvent:
    """终点事件"""

    player: Player
    desc: str

    async def trigger(self, ctx: discord.ApplicationContext) -> None:
        """触发事件"""
        await ctx.respond(self.desc, ephemeral=True)
