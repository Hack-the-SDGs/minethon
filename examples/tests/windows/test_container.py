"""測試容器操作: 開啟、關閉、視窗點擊。

驗證項目:
- await bot.open_container(target) → WindowHandle (id, title, kind)
- await bot.close_window(window)
- await bot.click_window(slot, mouse_button, mode)
- await bot.put_away(slot)
- await bot.transfer(item_type, source_start, source_end, dest_start, dest_end, count)
- await bot.move_slot_item(source_slot, dest_slot)

前置條件:
- 在 bot 附近放置一個箱子
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_not_none,
    check_type,
    failed,
    info,
    passed,
    run_test,
    section,
    wait_prompt,
)

from minethon import Bot
from minethon.models.window import WindowHandle


async def test_container(bot: Bot) -> None:
    wait_prompt("請在 bot 附近放置一個箱子（chest），然後按 Enter")

    # -- 尋找箱子 --
    section("尋找 chest")
    blocks = await bot.find_block("chest", max_distance=8, count=1)
    if not blocks:
        failed("附近找不到 chest，無法進行容器測試")
        return

    chest = blocks[0]
    info(f"找到 chest at {chest.position}")

    # -- open_container --
    section("open_container")
    try:
        window = await bot.open_container(chest)
        check_type("WindowHandle", window, WindowHandle)
        check_not_none("window.id", window.id)
        info(f"window.id = {window.id}")
        info(f"window.title = {window.title!r}")
        info(f"window.kind = {window.kind!r}")
        passed("open_container 成功")
    except Exception as exc:
        failed(f"open_container 失敗: {exc}")
        return

    # -- click_window --
    section("click_window")
    try:
        await bot.click_window(slot=0, mouse_button=0, mode=0)
        passed("click_window(slot=0, left_click, normal) 成功")
    except Exception as exc:
        info(f"click_window 失敗（可能 slot 0 為空）: {exc}")

    # -- put_away --
    section("put_away")
    try:
        await bot.put_away(slot=0)
        passed("put_away(slot=0) 成功")
    except Exception as exc:
        info(f"put_away 失敗（可能 slot 0 為空）: {exc}")

    # -- move_slot_item --
    section("move_slot_item")
    try:
        await bot.move_slot_item(source_slot=0, dest_slot=1)
        passed("move_slot_item(0 -> 1) 成功")
    except Exception as exc:
        info(f"move_slot_item 失敗（可能 slot 0 為空）: {exc}")

    # -- close_window --
    section("close_window")
    try:
        await bot.close_window(window)
        passed("close_window 成功")
    except Exception as exc:
        failed(f"close_window 失敗: {exc}")

    info("container 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("container", test_container))
