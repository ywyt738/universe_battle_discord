"""game configuration"""
from environs import Env

env = Env()
env.read_env()

proxy = env("HTTP_PROXY", None)

token = env("TOKEN")
database = env("DATABASE")

camps: dict[int, str] = {1: "银河", 2: "星云"}
