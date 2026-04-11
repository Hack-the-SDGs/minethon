"""test_goto.py -- 測試 bot.goto() 導航至指定座標。

驗證項目:
- 記錄起始位置
- 呼叫 goto(x+10, y, z+10) 移動至偏移座標
- 確認移動後位置與起始位置不同
- 呼叫 stop() 停止移動
- 印出移動前後的座標
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _common import (
    Bot,
    check_true,
    info,
    run_test,
    section,
)


async def test_goto(bot: Bot) -> None:
    section("goto() 導航測試")

    start = bot.position
    info(f"起始位置: x={start.x:.2f}, y={start.y:.2f}, z={start.z:.2f}")

    target_x = start.x + 10
    target_y = start.y
    target_z = start.z + 10
    info(f"目標位置: x={target_x:.2f}, y={target_y:.2f}, z={target_z:.2f}")

    info("正在導航...")
    await bot.goto(target_x, target_y, target_z, radius=2.0)

    end = bot.position
    info(f"結束位置: x={end.x:.2f}, y={end.y:.2f}, z={end.z:.2f}")

    moved = (
        abs(end.x - start.x) > 1.0
        or abs(end.y - start.y) > 1.0
        or abs(end.z - start.z) > 1.0
    )
    check_true("位置已改變", moved)

    dx = end.x - target_x
    dz = end.z - target_z
    distance = (dx * dx + dz * dz) ** 0.5
    info(f"與目標的水平距離: {distance:.2f}")

    section("stop() 停止移動")
    await bot.stop()
    info("已呼叫 stop()")

    await asyncio.sleep(0.5)
    after_stop = bot.position
    info(
        f"stop() 後位置: x={after_stop.x:.2f}, y={after_stop.y:.2f}, z={after_stop.z:.2f}"
    )


if __name__ == "__main__":
    asyncio.run(run_test("goto", test_goto))
