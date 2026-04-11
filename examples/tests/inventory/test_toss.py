"""test_toss.py -- 測試 bot.toss() 丟棄物品。

驗證項目:
- 列出物品欄
- 丟棄第一個可用物品
- 重新列出物品欄確認數量變化
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _common import (
    Bot,
    check_true,
    failed,
    info,
    passed,
    run_test,
    section,
    wait_prompt,
)


async def test_toss(bot: Bot) -> None:
    section("toss() 丟棄物品測試")

    wait_prompt("請確認 bot 有物品可以丟棄，然後按 Enter")

    items_before = await bot.get_inventory_items()
    info(f"丟棄前物品數量: {len(items_before)}")

    if len(items_before) == 0:
        failed("物品欄為空，無法測試丟棄")
        return

    for item in items_before:
        info(f"  [{item.slot:>2}] {item.display_name} ({item.name}) x{item.count}")

    target = items_before[0]
    info(f"準備丟棄: {target.display_name} ({target.name}) x1")

    section("toss() 丟棄 1 個物品")

    try:
        await bot.toss(target.name, count=1)
        passed(f"toss({target.name!r}, count=1) 呼叫成功")
    except Exception as exc:
        failed(f"toss() 失敗: {exc}")
        return

    await asyncio.sleep(1.0)

    items_after = await bot.get_inventory_items()
    info(f"丟棄後物品數量: {len(items_after)}")

    for item in items_after:
        info(f"  [{item.slot:>2}] {item.display_name} ({item.name}) x{item.count}")

    # 計算目標物品的總數變化
    count_before = sum(i.count for i in items_before if i.name == target.name)
    count_after = sum(i.count for i in items_after if i.name == target.name)
    info(f"{target.name} 數量變化: {count_before} -> {count_after}")
    check_true("物品數量減少", count_after < count_before)

    wait_prompt("請在遊戲中確認地上有被丟出的物品")


if __name__ == "__main__":
    asyncio.run(run_test("toss", test_toss))
