"""test_equip_unequip.py -- 測試 bot.equip() 和 bot.unequip() 裝備操作。

驗證項目:
- equip() 裝備指定物品到手上
- unequip() 卸下手上的物品
- 錯誤處理: 裝備不存在的物品
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _common import (
    Bot,
    failed,
    info,
    passed,
    run_test,
    section,
    wait_prompt,
)


async def test_equip_unequip(bot: Bot) -> None:
    section("equip() / unequip() 裝備測試")

    wait_prompt("請給 bot 一些裝備（劍、盔甲等），然後按 Enter")

    items = await bot.get_inventory_items()
    info(f"目前物品欄共 {len(items)} 個物品")
    for item in items:
        info(f"  [{item.slot:>2}] {item.display_name} ({item.name}) x{item.count}")

    section("equip() 裝備至主手")

    # 嘗試裝備物品欄中的第一個物品
    if len(items) > 0:
        target = items[0]
        info(f"嘗試裝備: {target.name}")
        try:
            await bot.equip(target.name, "hand")
            passed(f"equip({target.name!r}, 'hand') 成功")
            await asyncio.sleep(0.5)

            held = bot.held_item
            if held is not None:
                info(f"手持物品: {held.display_name} ({held.name})")
            else:
                info("手持物品: None")
        except Exception as exc:
            failed(f"equip() 失敗: {exc}")
    else:
        info("物品欄為空，跳過裝備測試")

    section("equip() 裝備不存在的物品")

    try:
        await bot.equip("nonexistent_item_xyz", "hand")
        failed("equip() 應該要失敗但沒有拋出例外")
    except Exception as exc:
        passed(f"equip() 正確拋出例外: {type(exc).__name__}: {exc}")

    section("unequip() 卸下主手物品")

    try:
        await bot.unequip("hand")
        passed("unequip('hand') 成功")
        await asyncio.sleep(0.5)

        held = bot.held_item
        info(f"卸下後手持物品: {held!r}")
    except Exception as exc:
        failed(f"unequip() 失敗: {exc}")

    wait_prompt("請在遊戲中確認 bot 的裝備狀態")


if __name__ == "__main__":
    asyncio.run(run_test("equip_unequip", test_equip_unequip))
