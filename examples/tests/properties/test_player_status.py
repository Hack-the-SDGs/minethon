"""測試玩家狀態相關的唯讀屬性。

驗證項目:
- health (0..20)
- food (0..20)
- food_saturation (0..20)
- oxygen_level (0..20)
- experience (Experience dataclass: level, points, progress)
- is_sleeping (bool)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_range,
    check_type,
    info,
    run_test,
    section,
)

from minethon import Bot, Experience


async def test_player_status(bot: Bot) -> None:
    # -- health --
    section("health")
    health = bot.health
    check_range("health", health, 0.0, 20.0)

    # -- food --
    section("food")
    food = bot.food
    check_range("food", food, 0.0, 20.0)

    # -- food_saturation --
    section("food_saturation")
    saturation = bot.food_saturation
    check_range("food_saturation", saturation, 0.0, 20.0)

    # -- oxygen_level --
    section("oxygen_level")
    oxygen = bot.oxygen_level
    check_range("oxygen_level", float(oxygen), 0.0, 20.0)

    # -- experience --
    section("experience")
    exp = bot.experience
    check_type("experience", exp, Experience)
    info(f"level={exp.level}, points={exp.points}, progress={exp.progress}")
    check_range("experience.level", float(exp.level), 0.0, 32767.0)
    check_range("experience.progress", exp.progress, 0.0, 1.0)

    # -- is_sleeping --
    section("is_sleeping")
    sleeping = bot.is_sleeping
    check_type("is_sleeping", sleeping, bool)
    info(f"is_sleeping = {sleeping}")


if __name__ == "__main__":
    asyncio.run(run_test("player_status", test_player_status))
