"""skill module"""
from .factory import *
from .skill import *


def load_skill():
    """load skills"""
    register("时空转移", SpaceTransit)
    register("偷窃术", Steal)
    register("空间术", SpaceMove)
    register("有难同当", DiffcultAlong)
