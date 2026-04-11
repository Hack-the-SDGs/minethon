"""測試遊戲狀態相關的唯讀屬性。

驗證項目:
- game_mode (str)
- difficulty (str)
- game (GameState dataclass 各欄位)
- time (TimeState dataclass 各欄位)
- is_raining (bool)
- rain_state (float)
- thunder_state (float)
- version (str)
- physics_enabled (bool)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_not_none,
    check_type,
    info,
    run_test,
    section,
)

from minethon import Bot, GameState, TimeState


async def test_game_state(bot: Bot) -> None:
    # -- game_mode --
    section("game_mode")
    gm = bot.game_mode
    check_not_none("game_mode", gm)
    check_type("game_mode", gm, str)
    info(f"game_mode = {gm!r}")

    # -- difficulty --
    section("difficulty")
    diff = bot.difficulty
    check_not_none("difficulty", diff)
    check_type("difficulty", diff, str)
    info(f"difficulty = {diff!r}")

    # -- game (GameState) --
    section("game (GameState)")
    game = bot.game
    check_type("game", game, GameState)
    info(f"game_mode    = {game.game_mode!r}")
    info(f"dimension    = {game.dimension!r}")
    info(f"difficulty   = {game.difficulty!r}")
    info(f"hardcore     = {game.hardcore}")
    info(f"max_players  = {game.max_players}")
    info(f"server_brand = {game.server_brand!r}")
    info(f"min_y        = {game.min_y}")
    info(f"height       = {game.height}")

    # -- time (TimeState) --
    section("time (TimeState)")
    time = bot.time
    check_type("time", time, TimeState)
    info(f"time_of_day      = {time.time_of_day}")
    info(f"day              = {time.day}")
    info(f"is_day           = {time.is_day}")
    info(f"moon_phase       = {time.moon_phase}")
    info(f"age              = {time.age}")
    info(f"do_daylight_cycle = {time.do_daylight_cycle}")

    # -- weather --
    section("weather")
    check_type("is_raining", bot.is_raining, bool)
    info(f"is_raining    = {bot.is_raining}")
    info(f"rain_state    = {bot.rain_state}")
    info(f"thunder_state = {bot.thunder_state}")

    # -- version --
    section("version")
    ver = bot.version
    check_not_none("version", ver)
    check_type("version", ver, str)
    info(f"version = {ver!r}")

    # -- physics_enabled --
    section("physics_enabled")
    phys = bot.physics_enabled
    check_type("physics_enabled", phys, bool)
    info(f"physics_enabled = {phys}")


if __name__ == "__main__":
    asyncio.run(run_test("game_state", test_game_state))
