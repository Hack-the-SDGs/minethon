"""測試合成系統。

驗證項目:
- await bot.recipes_for(item_name) → list[Recipe]
- await bot.recipes_all(item_name) → list[Recipe]
- await bot.craft(recipe, count=1)

前置條件:
- 給 bot 一些木板（planks）以合成木棍（sticks）
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
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


async def test_crafting(bot: Bot) -> None:
    wait_prompt("請給 bot 一些木板（/give <bot> oak_planks 16），然後按 Enter")

    # -- recipes_all --
    section("recipes_all('stick')")
    try:
        all_recipes = await bot.recipes_all("stick")
        check_type("recipes_all 回傳", all_recipes, list)
        info(f"stick 的所有配方數量: {len(all_recipes)}")
        for i, recipe in enumerate(all_recipes):
            info(f"  配方 [{i}]: id={recipe.id}")
    except Exception as exc:
        failed(f"recipes_all 失敗: {exc}")
        return

    # -- recipes_for --
    section("recipes_for('stick')")
    try:
        craftable = await bot.recipes_for("stick")
        check_type("recipes_for 回傳", craftable, list)
        info(f"stick 的可用配方數量: {len(craftable)}")
        for i, recipe in enumerate(craftable):
            info(f"  配方 [{i}]: id={recipe.id}")
    except Exception as exc:
        failed(f"recipes_for 失敗: {exc}")
        return

    if not craftable:
        skip("沒有可用的 stick 配方（可能缺少材料）")
        return

    # -- craft --
    section("craft")
    recipe = craftable[0]
    info(f"使用配方 id={recipe.id} 合成 1 次")
    try:
        await bot.craft(recipe, count=1)
        passed("craft 成功")
    except Exception as exc:
        failed(f"craft 失敗: {exc}")

    wait_prompt("在遊戲中確認 bot 物品欄是否多了木棍，然後按 Enter")
    info("crafting 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("crafting", test_crafting))
