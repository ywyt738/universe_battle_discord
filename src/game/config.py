"""game configuration"""
from environs import Env

env = Env()
env.read_env()

proxy = env("HTTP_PROXY", None)

token = env("TOKEN")
database = env("DATABASE")

camps: dict[int, str] = {1: "银河", 2: "星云"}
camps_skill: dict[str, list[str]] = {
    "银河": ["时空转移", "偷窃术"],
    "星云": ["空间术", "有难同当"],
}
