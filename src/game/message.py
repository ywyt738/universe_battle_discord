"""response message"""
import datetime

import discord

from game import config, db
from game.item import PlayerItems
from game.player import Player


def human_delta(tdelta):
    d = dict(days=tdelta.days)
    d["hrs"], rem = divmod(tdelta.seconds, 3600)
    d["min"], d["sec"] = divmod(rem, 60)

    if d["min"] == 0:
        fmt = "{sec} sec"
    elif d["hrs"] == 0:
        fmt = "{min} min {sec} sec"
    elif d["days"] == 0:
        fmt = "{hrs} hr(s) {min} min {sec} sec"
    else:
        fmt = "{days} day(s) {hrs} hr(s) {min} min {sec} sec"

    return fmt.format(**d)


def player_info_msg(player: Player) -> discord.Embed:
    """玩家信息"""
    now = datetime.datetime.now()
    items = PlayerItems.select().where(PlayerItems.player_id == player.discord_id)
    items_value = (
        "\n".join(
            [
                f"- **{player_item.item.name}** \*{player_item.count}"  # pyling: diable=anomalous-backslash-in-string
                for player_item in items  # pylint: disable=not-an-iterable
            ]
        )
        or "无"
    )
    player_buffs = db.PlayerBuff.select().where(
        (db.PlayerBuff.player_id == player.player) & (db.PlayerBuff.buff_cata == 0)
    )
    player_debuffs = db.PlayerBuff.select().where(
        (db.PlayerBuff.player_id == player.player) & (db.PlayerBuff.buff_cata == 1)
    )
    buff_value = (
        " | ".join(
            [
                f"{buff.buff.name}({human_delta(buff.expire_time- now)})"
                for buff in player_buffs
            ]
        )
        or "无"
    )
    debuff_value = (
        " | ".join(
            [
                f"{debuff.buff.name}({human_delta(debuff.expire_time- now)})"
                for debuff in player_debuffs
            ]
        )
        or "无"
    )
    embed_player_info = discord.Embed(
        colour=discord.Colour(0xF5D0A1),
        title="银河星云之战",
        fields=[
            discord.EmbedField(name="玩家:", value=player.name, inline=True),
            discord.EmbedField(
                name="阵营:", value=config.camps.get(player.camp), inline=True
            ),
            discord.EmbedField(
                name="位置:",
                value=f"{player.board}-{player.cell}",
                inline=True,
            ),
            discord.EmbedField(
                name="行动力:",
                value=player.ap,
                inline=True,
            ),
            discord.EmbedField(
                name="道具:",
                value=items_value,
            ),
            discord.EmbedField(name="Buff:", value=buff_value, inline=True),
            discord.EmbedField(name="Debuff:", value=debuff_value, inline=True),
        ],
    )
    return embed_player_info


def players_rank(query) -> discord.Embed:
    """排名"""
    desc_str = "\n".join([f"{i.name}" for i in query])

    rank_embed = discord.Embed(
        colour=discord.Colour(0xF5D0A1),
        title="排名",
        description=desc_str,
    )
    return rank_embed


WELCOME_TITLE = "欢迎加入新年活动 银河星云之战"
WELCOME_DESCRIPTION = "背景故事：在遥远的宇宙，有一个乌托邦星系，在四年一度的星球比赛中，有两个星球---银河星球和星云星球进入了最终决赛，比赛组在距离20光年的陨石台上放置了许多的宇宙之心，银河星人与宇宙为了争夺宇宙之心展开了一场激烈的斗争，银河星人和星云星人 双方派遣出各方战士从比赛赛场出发，他们要经历3个赛道地图，每个地图有25格，赛道内陷阱多多，危难重重，还要提防小心他人暗算，最后两方战士在获得宇宙之心之后返程回比赛赛场进行统计，获得最多的宇宙之心的星球获得胜利。"
USER_ACTION_POINT_IS_NOT_ENOUGH = "体力不足，无法前进。"
USER_FORWARD_SUCCESS = "前进{}格。"
USER_USE_ITEM_SUCCESS = "你使用了【{}】。"
USER_USE_ITEM_FAIL = "【{}】数量不足."
ADMIN_AP_SUCCESS = "为{user}增加了{count}点体力。"
ADMIN_ITEM_NOT_EXIST = "【{}】不存在。"
ADMIN_ITEM_SUCCESS = "为{user}增加了{count}个【{item}】。"
USER_CANT_FORWARD = "你不能向前移动。"
