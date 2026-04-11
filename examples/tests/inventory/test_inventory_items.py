"""test_inventory_items.py -- 測試物品欄查詢與快捷列操作。

驗證項目:
- get_inventory_items() 列出所有物品
- held_item 當前手持物品
- quick_bar_slot 當前快捷列欄位
- set_quick_bar_slot() 切換快捷列欄位
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _common import (
    Bot,
    check,
    check_type,
    info,
    passed,
    run_test,
    section,
)

from minethon import ItemStack


async def test_inventory_items(bot: Bot) -> None:
    section("get_inventory_items() 物品清單")

    items = await bot.get_inventory_items()
    info(f"物品數量: {len(items)}")

    if len(items) == 0:
        info("物品欄為空。如需更完整的測試，請先給 bot 一些物品。")
    else:
        for item in items:
            check_type(f"  slot {item.slot}", item, ItemStack)
            info(
                f"  [{item.slot:>2}] {item.display_name} ({item.name}) "
                f"x{item.count} (max={item.max_stack_size})"
            )

    section("held_item 手持物品")

    held = bot.held_item
    if held is not None:
        check_type("held_item 型別", held, ItemStack)
        info(f"手持物品: {held.display_name} ({held.name}) x{held.count}")
    else:
        info("目前沒有手持物品 (None)")

    section("quick_bar_slot 快捷列")

    slot = bot.quick_bar_slot
    check_type("quick_bar_slot 型別", slot, int)
    info(f"當前快捷列欄位: {slot}")

    section("set_quick_bar_slot() 切換快捷列")

    for target_slot in range(3):
        await bot.set_quick_bar_slot(target_slot)
        await asyncio.sleep(0.2)
        current = bot.quick_bar_slot
        check(f"切換至 slot {target_slot}", current, target_slot)

        held_after = bot.held_item
        if held_after is not None:
            info(
                f"  slot {target_slot} 手持: {held_after.display_name} x{held_after.count}"
            )
        else:
            info(f"  slot {target_slot} 手持: None（空欄位）")

    # 恢復原始欄位
    await bot.set_quick_bar_slot(slot)
    passed(f"已恢復至原始快捷列欄位 {slot}")


if __name__ == "__main__":
    asyncio.run(run_test("inventory_items", test_inventory_items))
