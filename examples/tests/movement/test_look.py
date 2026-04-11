"""test_look.py -- 測試 bot.look_at() 和 bot.look() 視角控制。

驗證項目:
- look_at() 朝向指定座標
- look(yaw, pitch) 設定具體視角角度
- 測試者需在遊戲中目視確認 bot 頭部朝向
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _common import (
    Bot,
    info,
    run_test,
    section,
    wait_prompt,
)


async def test_look(bot: Bot) -> None:
    pos = bot.position

    section("look_at() 視角控制")

    target_x = pos.x + 10
    target_y = pos.y + 5
    target_z = pos.z + 10
    info(f"Bot 位置: x={pos.x:.2f}, y={pos.y:.2f}, z={pos.z:.2f}")
    info(f"look_at 目標: x={target_x:.2f}, y={target_y:.2f}, z={target_z:.2f}")

    await bot.look_at(target_x, target_y, target_z)
    info("已呼叫 look_at()")
    wait_prompt("請在遊戲中觀察 bot 的頭部朝向是否指向偏移座標 (+10, +5, +10)")

    section("look(yaw=0, pitch=0)")

    await bot.look(0.0, 0.0)
    info("已呼叫 look(yaw=0, pitch=0) — 朝南方水平")
    wait_prompt("請在遊戲中觀察 bot 是否朝向南方（+Z 方向），視線水平")

    section("look(yaw=3.14, pitch=-0.5)")

    await bot.look(3.14, -0.5)
    info("已呼叫 look(yaw=3.14, pitch=-0.5) — 朝北方略微仰視")
    wait_prompt("請在遊戲中觀察 bot 是否朝向北方（-Z 方向），視線略微朝上")

    section("look(yaw=1.57, pitch=0, force=True)")

    await bot.look(1.57, 0.0, force=True)
    info("已呼叫 look(yaw=1.57, pitch=0, force=True) — 強制朝西方水平")
    wait_prompt("請在遊戲中觀察 bot 是否朝向西方（-X 方向），視線水平")


if __name__ == "__main__":
    asyncio.run(run_test("look", test_look))
