"""測試實體互動 API。

驗證項目:
- activate_entity() 右鍵互動
- use_on() 使用物品於實體

前置條件:
- 附近有可互動的實體（如村民、盔甲架、物品展示框等）
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

from minethon import Bot, EntityKind


async def test_interact_entity(bot: Bot) -> None:
    wait_prompt("請在 bot 附近放置一個可互動的實體（如村民、盔甲架）")

    # -- 搜尋可互動實體 --
    section("搜尋可互動實體")

    # 嘗試依序搜尋不同類型的可互動實體
    target = None
    for name in ("villager", "wandering_trader", "armor_stand", "item_frame"):
        found = await bot.find_entity(name=name, max_distance=16)
        if found is not None:
            target = found
            info(f"找到可互動實體: {target.name} (id={target.id}) at {target.position}")
            break

    if target is None:
        # 嘗試搜尋任何非玩家、非敵對的實體
        target = await bot.find_entity(kind=EntityKind.MOB, max_distance=16)
        if target is not None:
            info(f"找到 MOB: {target.name} (id={target.id}) at {target.position}")

    if target is None:
        target = await bot.find_entity(kind=EntityKind.ANIMAL, max_distance=16)
        if target is not None:
            info(f"找到動物: {target.name} (id={target.id}) at {target.position}")

    if target is None:
        skip("附近沒有找到可互動的實體")
        return

    # -- activate_entity --
    section("activate_entity")
    info(f"嘗試互動 {target.name} (id={target.id}) ...")
    try:
        await bot.activate_entity(target)
        passed("activate_entity() 完成")
    except Exception as exc:
        failed(f"activate_entity() 失敗: {exc}")

    wait_prompt("請確認 bot 與實體發生了互動（如開啟村民交易介面）")

    # -- use_on --
    section("use_on")
    wait_prompt("請確認 bot 手持物品，然後按 Enter 測試 use_on()")

    # 重新搜尋實體（可能因互動後狀態改變）
    refreshed = await bot.find_entity(name=target.name, max_distance=16)
    if refreshed is None:
        refreshed = await bot.find_entity(max_distance=16)

    if refreshed is not None:
        info(f"嘗試 use_on {refreshed.name} (id={refreshed.id}) ...")
        try:
            await bot.use_on(refreshed)
            passed("use_on() 完成")
        except Exception as exc:
            failed(f"use_on() 失敗: {exc}")
        wait_prompt("請確認 use_on 效果")
    else:
        skip("實體已不在範圍內，跳過 use_on 測試")


if __name__ == "__main__":
    asyncio.run(run_test("interact_entity", test_interact_entity))
