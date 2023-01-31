"""Skill"""
import datetime
import random
from dataclasses import dataclass

import discord
from peewee import fn

from game import db
from game.exception import ActionPointNotEnough
from game.player import Player


class BaseSkill:
    """Skill Protocol"""

    source: Player
    consume: int

    def func(self, target: discord.User) -> None:
        """User define skill"""

    def release(self, target: discord.User = None) -> None:
        """Use skill"""
        if self._check():
            self.func(target)
            self._consume()
        else:
            raise ActionPointNotEnough

    def _check(self) -> bool:
        """check release condition"""
        return bool(self.source.player.ap >= self.consume)

    def _consume(self) -> None:
        """consume action point"""
        self.source.player.ap -= self.consume
        self.source.player.save()


@dataclass
class SpaceTransit(BaseSkill):
    """时空转移"""

    source: Player
    consume: int = 3

    def func(self, target: discord.User) -> None:
        """Use skill"""
        target_player = Player(discord_id=target.id)
        back_steps = random.randint(2, 10)
        if target_player.player.cell - back_steps >= 0:
            target_player.player.cell -= back_steps
            target_player.player.save()
        else:
            target_player.player.cell = 0
            target_player.player.save()


@dataclass
class Steal(BaseSkill):
    """偷窃术"""

    source: Player
    consume: int = 2

    def func(self, target: discord.User) -> None:
        """Use skill"""
        target_player = Player(discord_id=target.id)
        item_query = (
            db.PlayerItems.select()
            .where(db.PlayerItems.player_id == target_player.player)
            .order_by(fn.Random())
            .limit(1)
        )
        if item_query:
            item = item_query[0]
            item.count -= 1
            item.save()
            item_name = db.Item.get_by_id(item.item_id).name
            self.source.get_item(item=item_name, count=1)

        if random.choices([0, 1], weights=[90, 10], k=1)[0]:  # 10%概率
            back_steps = random.randint(2, 10)
            if target_player.player.cell - back_steps >= 0:
                target_player.player.cell -= back_steps
                target_player.player.save()
            else:
                target_player.player.cell = 0
                target_player.player.save()


@dataclass
class SpaceMove(BaseSkill):
    """空间术"""

    source: Player
    consume: int = 3

    def func(self, target: discord.User) -> None:
        """Use skill"""
        forward_steps = random.randint(5, 10)
        if self.source.player + forward_steps <= 25:
            self.source.player.cell += forward_steps
        else:
            self.source.player.cell = 25
        self.source.player.save()

        if random.choices([0, 1], weights=[85, 15], k=1)[0]:  # 10%概率
            self.source.get_item("体力药水", 1)


@dataclass
class DiffcultAlong(BaseSkill):
    """有难同当"""

    source: Player
    consume: int = 2

    def func(self, target: discord.User) -> None:
        """Use skill"""
        query = (
            db.PlayerBuff.select()
            .where(
                (db.PlayerBuff.player_id == self.source.player)
                & (db.PlayerBuff.buff_cata == 1)
            )
            .get()
        )
        debuff = query
        now = datetime.datetime.now()
        debuff.expire_time = now + (debuff.expire_time - now) / 2
        debuff.save()
