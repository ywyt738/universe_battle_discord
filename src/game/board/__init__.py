"""Game Map"""
import json

from game.player import Player

from . import factory
from .board import (
    ActionPointResetEvent,
    BoardEvent,
    DropRandomItemEvent,
    GetItemEvent,
    MoveEvent,
    NonthingEvent,
    TrapEvent,
)

GAME_MAP = None


def get_board_event(player: Player) -> BoardEvent:
    """获取地图事件实例"""
    map_args = GAME_MAP.get(str(player.board)).get(str(player.cell))
    return factory.create(player, map_args)


def load_map():
    """加载地图文件"""
    global GAME_MAP
    with open("map.json", "r", encoding="utf-8") as mapfile:
        GAME_MAP = json.load(mapfile)
    # loader.load_plugins()
    factory.register("NonthingEvent", NonthingEvent)
    factory.register("TrapEvent", TrapEvent)
    factory.register("GetItemEvent", GetItemEvent)
    factory.register("ActionPointResetEvent", ActionPointResetEvent)
    factory.register("MoveEvent", MoveEvent)
    factory.register("DropRandomItemEvent", DropRandomItemEvent)
