"""測試睡覺與起床。

驗證項目:
- await bot.sleep(bed_block) 在床上睡覺
- await bot.wake() 起床

前置條件:
- 在 bot 附近放置一張床
- 設為夜晚（/time set night）
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    failed,
    info,
    passed,
    run_test,
    section,
    wait_prompt,
)

from minethon import Bot

# Bed block names vary by wood type
_BED_NAMES = [
    "white_bed",
    "orange_bed",
    "red_bed",
    "blue_bed",
    "black_bed",
    "green_bed",
    "yellow_bed",
    "cyan_bed",
    "gray_bed",
    "light_gray_bed",
    "pink_bed",
    "lime_bed",
    "light_blue_bed",
    "magenta_bed",
    "purple_bed",
    "brown_bed",
]


async def test_sleep_wake(bot: Bot) -> None:
    wait_prompt("請在 bot 附近放置一張床，並設為夜晚（/time set night），然後按 Enter")

    # -- 尋找床 --
    section("尋找床方塊")
    bed = None
    for name in _BED_NAMES:
        blocks = await bot.find_block(name, max_distance=8, count=1)
        if blocks:
            bed = blocks[0]
            break

    if bed is None:
        failed("附近找不到任何床方塊")
        return

    info(f"找到: {bed.name} at {bed.position}")

    # -- sleep --
    section("sleep")
    try:
        await bot.sleep(bed)
        passed("sleep 成功 — bot 正在睡覺")
    except Exception as exc:
        failed(f"sleep 失敗: {exc}")
        return

    wait_prompt("在遊戲中確認 bot 正躺在床上，然後按 Enter 執行 wake")

    # -- wake --
    section("wake")
    try:
        await bot.wake()
        passed("wake 成功 — bot 已起床")
    except Exception as exc:
        failed(f"wake 失敗: {exc}")

    info("sleep_wake 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("sleep_wake", test_sleep_wake))
