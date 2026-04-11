"""測試 ToolAPI（mineflayer-tool）。

驗證項目:
- await bot.tool.equip_for_block(block, require_harvest=False, timeout=10.0)

前置條件:
- 給 bot 至少一把工具（鎬、斧等）
- 附近需有可挖掘的方塊（如 stone）
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


async def test_tool(bot: Bot) -> None:
    # -- 載入插件 --
    section("載入 mineflayer-tool")
    if not bot.plugins.is_loaded("mineflayer-tool"):
        bot.plugins.load("mineflayer-tool")
    passed("mineflayer-tool 已載入")

    wait_prompt("請給 bot 一把鎬（例如 /give <bot> iron_pickaxe），然後按 Enter")

    # -- 尋找石頭方塊 --
    section("尋找 stone 方塊")
    blocks = await bot.find_block("stone", max_distance=16, count=1)
    if not blocks:
        blocks = await bot.find_block("cobblestone", max_distance=16, count=1)
    if not blocks:
        blocks = await bot.find_block("dirt", max_distance=16, count=1)

    if not blocks:
        skip("附近找不到 stone/cobblestone/dirt 方塊，無法測試 equip_for_block")
        return

    target_block = blocks[0]
    info(f"目標方塊: {target_block.name} at {target_block.position}")

    # -- 記錄裝備前的 held_item --
    held_before = bot.held_item
    info(f"裝備前 held_item: {held_before}")

    # -- equip_for_block --
    section("equip_for_block")
    try:
        await bot.tool.equip_for_block(target_block, require_harvest=False)
        passed("equip_for_block() 完成")
    except Exception as exc:
        failed(f"equip_for_block 失敗: {exc}")

    held_after = bot.held_item
    info(f"裝備後 held_item: {held_after}")

    if held_after is not None:
        passed(f"bot 現在手持: {held_after.name}")
    else:
        info("held_item 為 None（可能沒有合適工具或已使用空手）")


if __name__ == "__main__":
    asyncio.run(run_test("tool", test_tool))
