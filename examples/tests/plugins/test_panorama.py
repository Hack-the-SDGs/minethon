"""測試 PanoramaAPI（mineflayer-panorama, experimental）。

驗證項目:
- await bot.panorama.raw_take_panorama(camera_height=None) — raw escape hatch
- await bot.panorama.raw_take_picture(point, direction) — raw escape hatch

前置條件:
- 需要 native node-canvas-webgl 環境（可能在某些平台無法運行）

注意:
- 所有 capture 方法都是 raw escape hatch，回傳 JS proxy 而非 typed Python 值
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_not_none,
    failed,
    info,
    passed,
    run_test,
    section,
    skip,
)

from minethon import Bot
from minethon.models.vec3 import Vec3


async def test_panorama(bot: Bot) -> None:
    # -- 載入插件 --
    section("載入 mineflayer-panorama")
    try:
        if not bot.plugins.is_loaded("mineflayer-panorama"):
            bot.plugins.load("mineflayer-panorama")
        passed("mineflayer-panorama 已載入")
    except Exception as exc:
        skip(f"無法載入 mineflayer-panorama（可能缺少 node-canvas-webgl）: {exc}")
        return

    # -- raw_take_panorama --
    section("raw_take_panorama")
    try:
        result = await bot.panorama.raw_take_panorama()
        check_not_none("raw_take_panorama() 結果", result)
        info(f"回傳類型: {type(result).__name__}")
        passed("raw_take_panorama 成功（回傳 raw JS proxy）")
    except Exception as exc:
        failed(f"raw_take_panorama 失敗: {exc}")

    # -- raw_take_panorama with camera_height --
    section("raw_take_panorama (camera_height=20)")
    try:
        result = await bot.panorama.raw_take_panorama(camera_height=20.0)
        check_not_none("raw_take_panorama(camera_height=20) 結果", result)
        passed("raw_take_panorama with camera_height 成功")
    except Exception as exc:
        failed(f"raw_take_panorama(camera_height=20) 失敗: {exc}")

    # -- raw_take_picture --
    section("raw_take_picture")
    pos = bot.position
    if pos is None:
        skip("bot.position is None, 無法測試 raw_take_picture")
        return

    point = Vec3(pos.x, pos.y + 10, pos.z)
    direction = Vec3(0.0, -1.0, 0.0)  # 向下看
    info(f"拍攝位置: {point}, 方向: {direction}")

    try:
        result = await bot.panorama.raw_take_picture(point, direction)
        check_not_none("raw_take_picture() 結果", result)
        info(f"回傳類型: {type(result).__name__}")
        passed("raw_take_picture 成功（回傳 raw JS proxy）")
    except Exception as exc:
        failed(f"raw_take_picture 失敗: {exc}")


if __name__ == "__main__":
    asyncio.run(run_test("panorama", test_panorama))
