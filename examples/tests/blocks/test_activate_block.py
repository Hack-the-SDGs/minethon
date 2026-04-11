"""測試方塊啟動（互動）API。

驗證項目:
- activate_block() 觸發可互動方塊（門、拉桿、按鈕等）

前置條件:
- 附近有可互動的方塊（門、拉桿、按鈕、柵欄門等）
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
    skip,
    wait_prompt,
)

from minethon import Bot

# 常見可互動方塊名稱（部分列舉）
_INTERACTABLE_BLOCKS = (
    "oak_door",
    "spruce_door",
    "birch_door",
    "jungle_door",
    "acacia_door",
    "dark_oak_door",
    "iron_door",
    "oak_fence_gate",
    "spruce_fence_gate",
    "birch_fence_gate",
    "jungle_fence_gate",
    "acacia_fence_gate",
    "dark_oak_fence_gate",
    "lever",
    "stone_button",
    "oak_button",
    "oak_trapdoor",
    "spruce_trapdoor",
    "chest",
    "crafting_table",
)


async def test_activate_block(bot: Bot) -> None:
    wait_prompt("請在 bot 附近放置一扇門、拉桿、按鈕或其他可互動方塊")

    # -- 搜尋可互動方塊 --
    section("搜尋可互動方塊")
    target = None
    for name in _INTERACTABLE_BLOCKS:
        blocks = await bot.find_block(name, max_distance=16, count=1)
        if blocks:
            target = blocks[0]
            info(f"找到可互動方塊: {target.name} at {target.position}")
            break

    if target is None:
        skip("附近沒有找到可互動方塊")
        info("支援搜尋的方塊類型:")
        for name in _INTERACTABLE_BLOCKS:
            info(f"  - {name}")
        return

    # -- activate_block --
    section("activate_block")
    info(f"嘗試啟動 {target.name} at {target.position} ...")

    try:
        await bot.activate_block(target)
        passed("activate_block() 完成")
    except Exception as exc:
        failed(f"activate_block() 失敗: {exc}")

    wait_prompt("請確認門/拉桿/按鈕已被觸發")


if __name__ == "__main__":
    asyncio.run(run_test("activate_block", test_activate_block))
