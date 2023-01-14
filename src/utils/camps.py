"""阵营"""
import random

from game import config


def new_player_join():
    """新玩家进入阵营"""
    return random.choice(list(config.camps.keys()))
