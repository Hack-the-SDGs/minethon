"""測試 ArmorAPI（mineflayer-armor-manager）。

驗證項目:
- await bot.armor.equip_best() 自動裝備最佳盔甲

前置條件:
- 給 bot 盔甲片（/give 鐵甲、鑽石甲等）
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


async def test_armor(bot: Bot) -> None:
    # -- 載入插件 --
    section("載入 mineflayer-armor-manager")
    if not bot.plugins.is_loaded("mineflayer-armor-manager"):
        bot.plugins.load("mineflayer-armor-manager")
    passed("mineflayer-armor-manager 已載入")

    # -- equip_best --
    section("equip_best")
    wait_prompt(
        "請給 bot 盔甲（例如 /give <bot> iron_helmet, iron_chestplate, "
        "iron_leggings, iron_boots），然後按 Enter"
    )

    try:
        await bot.armor.equip_best()
        passed("equip_best() 完成")
    except Exception as exc:
        failed(f"equip_best 失敗: {exc}")

    wait_prompt("在遊戲中觀察 bot 是否已穿上盔甲，確認後按 Enter")
    info("armor 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("armor", test_armor))
