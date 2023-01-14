"""道具"""
from typing import Callable

from game import db


class Modifier:
    ...


class MoveModifier(Modifier):
    def __init__(self, disable_move: bool, steps: int = 0) -> None:
        self.disable_move = disable_move
        self.steps = steps


class BuffProtocol:
    """Buff/Debuff"""

    id: int
    name: str
    cata: int
    describtion: str
    phase: str

    def get_modifier(self):
        ...


class Adrenaline(BuffProtocol):
    """肾上腺素"""

    id = 1
    name = "肾上腺素"
    cata = 0
    describtion = "向前移动最大距离增加2格"
    phase = "move"

    def get_modifier(self):
        return MoveModifier(disable_move=False, steps=2)


class Imprison(BuffProtocol):
    """禁锢"""

    id = 2
    name = "禁锢"
    cata = 1
    describtion = "无法向前移动"
    phase = "move"

    def get_modifier(self):
        return MoveModifier(disable_move=True)


ENABLE_BUFF: dict[str, Callable] = {
    "肾上腺素": Adrenaline,
    "禁锢": Imprison,
}


MODIFIER_DICT: dict[str, Callable] = {"move": MoveModifier}


def modifier_factory(buff: db.Buff) -> Modifier:
    buff_cls = ENABLE_BUFF.get(buff.name)
    return buff_cls().get_modifier()


def check_for_interaction(player: db.Player, phase: str) -> tuple[Modifier]:
    """玩家阶段buff/debuff交互"""
    # player_buff = db.PlayerBuff.select().where(
    #     db.PlayerBuff.player_id == player.player, db.PlayerBuff.buff.phase == phase
    # )
    player_buff = (
        db.PlayerBuff.select()
        .join(db.Buff)
        .where((db.Buff.phase == phase) & (db.PlayerBuff.player_id == player))
    )
    data = [modifier_factory(buff.buff) for buff in player_buff]
    return set(data)


def load_buff_into_db():
    """插入buff数据库"""
    for _, buff_cls in ENABLE_BUFF.items():
        db.Buff.get_or_create(
            id=buff_cls.id,
            name=buff_cls.name,
            cata=buff_cls.cata,
            describtion=buff_cls.describtion,
            phase=buff_cls.phase,
        )
