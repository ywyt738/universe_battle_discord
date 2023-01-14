"""board"""
from typing import Any, Callable

from .board import BoardEvent

board_creation_funcs: dict[str, Callable[..., BoardEvent]] = {}


def register(event_name: str, creation_func: Callable[..., BoardEvent]):
    """注册一个新地图事件"""
    board_creation_funcs[event_name] = creation_func


def unregister(event_name: str):
    """注销一个地图事件"""
    board_creation_funcs.pop(event_name, None)


def create(player, arguments: dict[str, Any]) -> BoardEvent:
    """创建一个地图事件根据参数"""
    args_copy = arguments.copy()
    board_event_name = args_copy.pop("event")
    try:
        creation_func = board_creation_funcs[board_event_name]
        return creation_func(player=player, **args_copy)
    except KeyError:
        raise ValueError(f"Unknown board event type {board_event_name!r}") from None
