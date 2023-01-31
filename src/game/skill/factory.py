"""skill factory"""
from typing import Callable

import discord

from game.player import Player

from .skill import BaseSkill

skill_creation_funcs: dict[str, Callable[..., BaseSkill]] = {}


def register(skill_name: str, creation_func: Callable[..., BaseSkill]):
    """注册一个新技能"""
    skill_creation_funcs[skill_name] = creation_func


def unregister(skill_name: str):
    """注销一个技能"""
    skill_creation_funcs.pop(skill_name, None)


def create(source: Player, skill_name: str) -> BaseSkill:
    """创建一个技能根据参数"""
    try:
        creation_func = skill_creation_funcs[skill_name]
        return creation_func(source=source)
    except KeyError:
        raise ValueError(f"Unknown skill: {skill_name!r}") from None
