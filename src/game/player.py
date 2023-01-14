"""Player.py"""
import datetime
import random
from datetime import timedelta

from game import db
from game.buff import check_for_interaction
from game.exception import ActionPointNotEnough
from utils.camps import new_player_join


class Player:
    """玩家"""

    def __init__(self, discord_id) -> None:
        self.player: db.Player = db.Player.get(db.Player.discord_id == discord_id)
        self._sync_db_data()

    def _sync_db_data(self):
        self.discord_id = self.player.discord_id
        self.name = self.player.name
        self.ap = self.player.ap
        self.board = self.player.board
        self.cell = self.player.cell
        self.camp = self.player.camp

    @classmethod
    def register(cls, discord_id, name):
        """新用户"""
        # todo: 阵营人数平衡
        camp = new_player_join()
        db.Player.create(discord_id=discord_id, name=name, camp=camp)
        return cls(discord_id=discord_id)

    def move(self) -> bool:
        """玩家移动"""
        action_phase = "move"
        if self.player.ap < 1:
            raise ActionPointNotEnough("AP Is not enough.")
        modifier = check_for_interaction(self.player, action_phase)
        if modifier:
            if True in [m.disable_move for m in modifier]:
                return False, None
            modifier_steps = sum([m.steps for m in modifier])
            if modifier_steps < -2:
                steps = 0
            else:
                steps = random.randint(1, 3 + modifier_steps)
        else:
            steps = random.randint(1, 3)
        self.player.ap -= 1
        self.player.cell += steps
        self.player.save()
        self._sync_db_data()
        return True, steps

    def apply_affect(self, buff: str, duration_time: timedelta):
        """受到buff/debuff"""
        buff = db.Buff.get(db.Buff.name == buff)
        now = datetime.datetime.now()
        player_buff = db.PlayerBuff.get_or_none(
            player_id=self.player, buff_cata=buff.cata, buff=buff
        )
        if player_buff:  # 刷新buff时间
            player_buff.expire_time = now + duration_time
            player_buff.save()
        else:  # 新buff
            db.PlayerBuff.create(
                player_id=self.player,
                buff_cata=buff.cata,
                buff=buff,
                expire_time=now + duration_time,
            )

    def add_ap(self, count):
        """增加体力"""
        self.player.ap += count
        self.player.save()
        self._sync_db_data()

    def get_item(self, item: str, count: int):
        """获得道具"""
        item = db.Item.get(db.Item.name == item)
        player_items, _ = db.PlayerItems.get_or_create(player_id=self.player, item=item)
        player_items.count += count
        player_items.save()

    # def remove_affect(self, buff: str):
    #     """移除buff/debuff"""
    #     buff = db.Buff.get(db.Buff.name == buff)
    #     db.PlayerBuff.delete().where(db.PlayerBuff.player_id == self, buff == buff)
