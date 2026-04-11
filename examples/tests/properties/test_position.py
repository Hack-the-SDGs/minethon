"""測試位置相關的屬性。

驗證項目:
- position (Vec3: x, y, z 為 float)
- get_spawn_point() (Vec3)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_type,
    info,
    run_test,
    section,
)

from minethon import Bot, Vec3


async def test_position(bot: Bot) -> None:
    # -- position --
    section("position")
    pos = bot.position
    check_type("position", pos, Vec3)
    check_type("position.x", pos.x, float)
    check_type("position.y", pos.y, float)
    check_type("position.z", pos.z, float)
    info(f"position = ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")

    # -- get_spawn_point --
    section("get_spawn_point")
    try:
        sp = await bot.get_spawn_point()
        check_type("spawn_point", sp, Vec3)
        info(f"spawn_point = ({sp.x:.2f}, {sp.y:.2f}, {sp.z:.2f})")
    except Exception as exc:
        info(f"get_spawn_point() 拋出例外（伺服器可能尚未發送 spawn_position）: {exc}")


if __name__ == "__main__":
    asyncio.run(run_test("position", test_position))
