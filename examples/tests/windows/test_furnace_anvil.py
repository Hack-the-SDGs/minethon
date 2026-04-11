"""測試熔爐、附魔台、鐵砧操作及寫書。

驗證項目:
- await bot.open_furnace(block) → WindowHandle
- await bot.open_enchantment_table(block) → WindowHandle
- await bot.open_anvil(block) → WindowHandle
- await bot.write_book(slot, pages)
- await bot.close_window(window)

前置條件:
- 在 bot 附近放置熔爐、附魔台、鐵砧
- write_book 需要在物品欄有 writable_book（書與羽毛筆）
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
    skip,
    wait_prompt,
)

from minethon import Bot
from minethon.models.window import WindowHandle


async def _test_open_block(
    bot: Bot,
    block_name: str,
    open_fn: str,
) -> None:
    """共用的方塊開啟測試邏輯。"""
    blocks = await bot.find_block(block_name, max_distance=8, count=1)
    if not blocks:
        skip(f"附近找不到 {block_name}")
        return

    block = blocks[0]
    info(f"找到 {block_name} at {block.position}")

    try:
        method = getattr(bot, open_fn)
        window = await method(block)
        check_type("WindowHandle", window, WindowHandle)
        check_not_none("window.id", window.id)
        info(f"window.id = {window.id}")
        info(f"window.title = {window.title!r}")
        info(f"window.kind = {window.kind!r}")
        passed(f"{open_fn} 成功")

        await bot.close_window(window)
        passed("close_window 成功")
    except Exception as exc:
        failed(f"{open_fn} 失敗: {exc}")


async def test_furnace_anvil(bot: Bot) -> None:
    # -- open_furnace --
    section("open_furnace")
    wait_prompt("請在 bot 附近放置熔爐（furnace），然後按 Enter")
    await _test_open_block(bot, "furnace", "open_furnace")

    # -- open_enchantment_table --
    section("open_enchantment_table")
    wait_prompt("請在 bot 附近放置附魔台（enchanting_table），然後按 Enter")
    await _test_open_block(bot, "enchanting_table", "open_enchantment_table")

    # -- open_anvil --
    section("open_anvil")
    wait_prompt("請在 bot 附近放置鐵砧（anvil），然後按 Enter")
    await _test_open_block(bot, "anvil", "open_anvil")

    # -- write_book --
    section("write_book")
    wait_prompt(
        "請給 bot 一本書與羽毛筆（/give <bot> writable_book），"
        "放在快捷列第一格（slot 36），然後按 Enter"
    )
    try:
        pages = ["Page 1: Hello from minethon!", "Page 2: Testing write_book."]
        await bot.write_book(slot=36, pages=pages)
        passed("write_book 成功")
    except Exception as exc:
        failed(f"write_book 失敗: {exc}")

    info("furnace_anvil 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("furnace_anvil", test_furnace_anvil))
