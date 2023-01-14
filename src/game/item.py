"""道具"""
import datetime
import random
from typing import Callable

import discord

from game import db
from game.player import Player


class ItemProtocol:
    """道具"""

    id: int
    name: str
    describtion: str

    def __init__(
        self, player: discord.User, target_player: discord.User = None
    ) -> None:
        self.player = player
        self.target_player = target_player

    def use(self):
        """使用道具"""
        self._pre()
        self._use()
        self._post()
        self._consume()

    def _use(self):
        """道具正在使用"""

    def _pre(self):
        """使用道具前"""

    def _post(self):
        """使用道具后"""

    def _consume(self):
        """道具扣除"""
        item = db.Item.get(db.Item.name == self.name)
        player_item = db.PlayerItems.get_or_none(player_id=self.player.id, item=item)
        player_item.count -= 1
        player_item.save()


class Portal(ItemProtocol):
    """道具:传送门"""

    id: int = 1
    name: str = "传送门"
    describtion: str = "传送至前方2-5格内任意位置。"
    response: str = "你使用【传送门】前进了{}个格子。"

    def _use(self) -> None:
        """使用传送门"""
        player = db.Player.get_or_none(discord_id=self.player.id)
        steps = random.randint(2, 5)
        player.cell += steps
        player.save()
        self.response = self.response.format(steps)


class ApPotionSelf(ItemProtocol):
    """道具:体力药水"""

    id: int = 2
    name: str = "体力药水"
    describtion: str = "恢复体力至初始。"
    response: str = "你使用【体力药水(个人)】恢复了体力。"

    def _use(self) -> None:
        """使用体力药水(个人)"""
        player = db.Player.get_or_none(discord_id=self.player.id)
        player.ap = 5
        player.save()


class ConfusePotion(ItemProtocol):
    """道具:致幻剂"""

    id: int = 3
    name: str = "致幻剂"
    describtion: str = "指定一名玩家使用，让人迷失方向，随机后退3-5格。"
    response: str = "你使用【致幻剂】让{}后退了{}格。"

    def _use(self) -> None:
        """使用致幻剂"""
        target = db.Player.get_or_none(discord_id=self.target_player.id)
        steps = random.randint(3, 5)
        if target.cell < steps:
            target.cell = 0
        else:
            target.cell -= steps
        target.save()
        self.response = self.response.format(self.target_player.name, steps)


class BattleSupply(ItemProtocol):
    """道具:战斗补给"""

    id: int = 4
    name: str = "战斗补给"
    describtion: str = "使用可以给自身恢复满体力，给已方所有人恢复1点体力值。"
    response: str = "你使用【战斗补给】恢复了体力。"

    def _use(self) -> None:
        """使用战斗补给"""
        player = db.Player.get_or_none(discord_id=self.player.id)
        player.ap = 5
        player.save()
        camps_players = db.Player.select().where(db.Player.camp == player.camp)
        for camps_player in camps_players:
            if camps_player.ap < 5:
                camps_player.ap += 1
                camps_player.save()


class Adrenaline(ItemProtocol):
    """道具:肾上腺素"""

    id: int = 5
    name: str = "肾上腺素"
    describtion: str = "使用后精神百倍，今日向前移动最大距离增加2格。"
    response: str = "你使用【肾上腺素】，今日向前移动最大距离增加2。"

    def _use(self) -> None:
        """使用肾上腺素"""
        player = Player(discord_id=self.player.id)
        now = datetime.datetime.now()
        duration_time = (
            datetime.datetime(
                year=now.year, month=now.month, day=now.day + 1, hour=0, minute=0
            )
            - now
        )
        player.apply_affect(buff="肾上腺素", duration_time=duration_time)


class DebuffCleaner(ItemProtocol):
    """道具:负面buff消除剂"""

    id: int = 6
    name: str = "负面buff消除剂"
    describtion: str = "可解除遇到的所有陷阱/负面buff"
    response: str = "你使用【负面buff消除剂】,已经解除所有陷阱/负面buff"

    def _use(self) -> None:
        """使用负面buff消除剂"""
        player = Player(discord_id=self.player.id)
        query = db.PlayerBuff.delete().where(
            (db.PlayerBuff.player_id == player.player) & (db.PlayerBuff.buff_cata == 1)
        )
        query.execute()


class PlayerItems(db.PlayerItems):
    """玩家的道具"""

    @classmethod
    def add(cls, player_id: str, item_name: str, count: int) -> bool:
        """玩家获得道具"""
        player = db.Player.get_or_none(discord_id=player_id)
        try:
            item = db.Item.get(db.Item.name == item_name)
        except db.Item.DoesNotExist:  # pylint: disable=no-member
            return False
        else:
            player_items, _ = cls.get_or_create(player_id=player, item=item)
            player_items.count += count
            player_items.save()
            return True

    @classmethod
    def how_many(cls, player_id: str, item_name: str) -> int:
        """玩家有多少个指定道具"""
        item = db.Item.get(db.Item.name == item_name)
        player_item = cls.get_or_none(player_id=player_id, item=item)
        if player_item:
            return player_item.count
        else:
            return None


ENABLE_ITEM: dict[str, Callable] = {
    "传送门": Portal,
    "体力药水": ApPotionSelf,
    "致幻剂": ConfusePotion,
    "战斗补给": BattleSupply,
    "肾上腺素": Adrenaline,
    "负面buff消除剂": DebuffCleaner,
}


def load_item_into_db():
    """插入道具数据库"""
    for _, item_cls in ENABLE_ITEM.items():
        db.Item.get_or_create(
            id=item_cls.id, name=item_cls.name, describtion=item_cls.describtion
        )
