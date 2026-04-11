"""測試線上玩家列表與 Tab 列表。

驗證項目:
- players dict（遍歷並印出每位玩家的 PlayerInfo）
- get_tablist() 的 header / footer
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_not_none,
    check_true,
    check_type,
    info,
    run_test,
    section,
)

from minethon import Bot, PlayerInfo


async def test_players_tablist(bot: Bot) -> None:
    # -- players --
    section("players")
    players = bot.players
    check_type("players", players, dict)
    check_true("players 非空", len(players) > 0)
    info(f"線上玩家數: {len(players)}")

    for username, player in players.items():
        check_type(f"players[{username!r}]", player, PlayerInfo)
        info(
            f"  {username}: uuid={player.uuid}, "
            f"ping={player.ping}ms, "
            f"game_mode={player.game_mode}, "
            f"display_name={player.display_name!r}"
        )

    # -- get_tablist --
    section("get_tablist")
    header, footer = await bot.get_tablist()
    check_not_none("header", header)
    check_not_none("footer", footer)
    check_type("header", header, str)
    check_type("footer", footer, str)
    info(f"header = {header!r}")
    info(f"footer = {footer!r}")


if __name__ == "__main__":
    asyncio.run(run_test("players_tablist", test_players_tablist))
