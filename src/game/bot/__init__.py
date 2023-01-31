"""bot module"""
from typing import Tuple

from .bot import BOT
from .command import Admin, User

__all__: Tuple[str, ...] = ("BOT",)

BOT.add_cog(User(bot))
BOT.add_cog(Admin(bot))
