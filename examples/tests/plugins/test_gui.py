"""測試 GuiAPI（mineflayer-gui）。

驗證項目:
- await bot.gui.click_item(name, window=False) 點擊物品
- await bot.gui.drop_item(name, count=1) 丟棄物品
- bot.gui.raw_query() 取得 raw JS Query builder

前置條件:
- 給 bot 一些物品（如 cobblestone）
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
    wait_prompt,
)

from minethon import Bot


async def test_gui(bot: Bot) -> None:
    # -- 載入插件 --
    section("載入 mineflayer-gui")
    if not bot.plugins.is_loaded("mineflayer-gui"):
        bot.plugins.load("mineflayer-gui")
    passed("mineflayer-gui 已載入")

    wait_prompt(
        "請給 bot 一些 cobblestone（/give <bot> cobblestone 64）和一把劍"
        "（/give <bot> stone_sword），然後按 Enter"
    )

    # -- click_item --
    section("click_item")
    try:
        result = await bot.gui.click_item("stone_sword", window=False)
        info(f"click_item('stone_sword') 回傳: {result}")
        if result:
            passed("click_item 找到並裝備了 stone_sword")
        else:
            info("click_item 回傳 False — 可能物品不存在")
    except Exception as exc:
        failed(f"click_item 失敗: {exc}")

    # -- drop_item --
    section("drop_item")
    try:
        result = await bot.gui.drop_item("cobblestone", count=1)
        info(f"drop_item('cobblestone', count=1) 回傳: {result}")
        if result:
            passed("drop_item 成功丟棄 1 個 cobblestone")
        else:
            info("drop_item 回傳 False — 可能物品不存在")
    except Exception as exc:
        failed(f"drop_item 失敗: {exc}")

    wait_prompt("在遊戲中觀察 bot 是否丟出了 cobblestone，確認後按 Enter")

    # -- raw_query --
    section("raw_query (escape hatch)")
    try:
        query = bot.gui.raw_query()
        check_not_none("raw_query()", query)
        info(f"raw_query 類型: {type(query).__name__}")
        passed("raw_query() 回傳成功（raw JS proxy）")
    except Exception as exc:
        failed(f"raw_query 失敗: {exc}")


if __name__ == "__main__":
    asyncio.run(run_test("gui", test_gui))
