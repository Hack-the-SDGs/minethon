"""test_jump.py -- 測試 bot.jump() 跳躍動作。

驗證項目:
- 記錄跳躍前的 Y 座標
- 呼叫 jump() 後短暫等待
- 確認 Y 座標有變化（跳躍上升）
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


async def test_jump(bot: Bot) -> None:
    section("jump() 跳躍測試")

    start_y = bot.position.y
    info(f"跳躍前 Y 座標: {start_y:.4f}")

    await bot.jump()
    info("已呼叫 jump()")

    # 短暫等待讓跳躍動作產生效果
    await asyncio.sleep(0.3)

    peak_y = bot.position.y
    info(f"跳躍後 Y 座標: {peak_y:.4f}")

    jumped = peak_y > start_y
    check_true("Y 座標上升（跳躍成功）", jumped)

    # 等待落地
    await asyncio.sleep(1.0)
    landed_y = bot.position.y
    info(f"落地後 Y 座標: {landed_y:.4f}")


if __name__ == "__main__":
    asyncio.run(run_test("jump", test_jump))
