"""測試創造模式操作。

驗證項目:
- await bot.creative_fly_to(destination) — destination 為 Vec3
- await bot.creative_set_inventory_slot_raw(slot, item) — raw item
- await bot.creative_clear_slot(slot)
- await bot.creative_clear_inventory()

前置條件:
- bot 必須處於創造模式（/gamemode creative）
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
from minethon.models.vec3 import Vec3


async def test_creative(bot: Bot) -> None:
    wait_prompt("請確保 bot 處於創造模式（/gamemode creative），然後按 Enter")

    # -- creative_fly_to --
    section("creative_fly_to")
    pos = bot.position
    if pos is None:
        failed("bot.position is None")
        return

    dest = Vec3(pos.x + 10.5, pos.y + 5, pos.z + 10.5)
    info(f"目前位置: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})")
    info(f"飛行目標: ({dest.x:.1f}, {dest.y:.1f}, {dest.z:.1f})")

    try:
        await bot.creative_fly_to(dest)
        passed("creative_fly_to 完成")
        arrival = bot.position
        if arrival is not None:
            info(f"到達位置: ({arrival.x:.1f}, {arrival.y:.1f}, {arrival.z:.1f})")
    except Exception as exc:
        failed(f"creative_fly_to 失敗: {exc}")

    # -- creative_clear_inventory --
    section("creative_clear_inventory")
    try:
        await bot.creative_clear_inventory()
        passed("creative_clear_inventory 完成")
    except Exception as exc:
        failed(f"creative_clear_inventory 失敗: {exc}")

    wait_prompt("確認 bot 物品欄已清空，然後按 Enter")

    # -- creative_set_inventory_slot_raw --
    section("creative_set_inventory_slot_raw")
    info("此方法需要 raw JS prismarine-item，透過 bot.raw 取得")
    info("跳過自動測試 — 需要手動使用 bot.raw 建構 JS item")
    info("範例用法: await bot.creative_set_inventory_slot_raw(36, raw_item)")

    # -- creative_clear_slot --
    section("creative_clear_slot")
    try:
        await bot.creative_clear_slot(36)
        passed("creative_clear_slot(36) 完成")
    except Exception as exc:
        failed(f"creative_clear_slot 失敗: {exc}")

    info("creative 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("creative", test_creative))
