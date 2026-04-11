"""test_use_consume.py -- 測試物品使用相關 API。

驗證項目:
- use_item() 使用手持物品
- deactivate_item() 停止使用物品
- swing_arm() 揮動手臂
- consume() 食用/飲用手持物品
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


async def test_use_consume(bot: Bot) -> None:
    section("swing_arm() 揮動手臂")

    info("揮動右手...")
    await bot.swing_arm("right")
    passed("swing_arm('right') 呼叫成功")

    await asyncio.sleep(0.5)

    info("揮動左手...")
    await bot.swing_arm("left")
    passed("swing_arm('left') 呼叫成功")

    wait_prompt("請在遊戲中觀察 bot 是否揮動了手臂")

    section("use_item() / deactivate_item() 使用物品")

    held = bot.held_item
    if held is not None:
        info(f"當前手持: {held.display_name} ({held.name})")
    else:
        info("當前沒有手持物品")

    info("呼叫 use_item()...")
    try:
        await bot.use_item()
        passed("use_item() 呼叫成功")
    except Exception as exc:
        failed(f"use_item() 失敗: {exc}")

    await asyncio.sleep(1.0)

    info("呼叫 deactivate_item()...")
    try:
        await bot.deactivate_item()
        passed("deactivate_item() 呼叫成功")
    except Exception as exc:
        failed(f"deactivate_item() 失敗: {exc}")

    section("consume() 食用/飲用測試")

    wait_prompt("請給 bot 食物（例如麵包、蘋果）並放在手上，然後按 Enter")

    held = bot.held_item
    if held is not None:
        info(f"手持物品: {held.display_name} ({held.name})")
    else:
        info("注意: 目前沒有手持物品，consume() 可能會失敗")

    info("呼叫 consume()...")
    try:
        await bot.consume()
        passed("consume() 呼叫成功")
    except Exception as exc:
        failed(f"consume() 失敗: {exc}")

    await asyncio.sleep(0.5)

    held_after = bot.held_item
    if held_after is not None:
        info(f"食用後手持: {held_after.display_name} x{held_after.count}")
    else:
        info("食用後手持: None（食物已吃完或欄位已空）")

    wait_prompt("請在遊戲中確認 bot 的進食動畫與效果")


if __name__ == "__main__":
    asyncio.run(run_test("use_consume", test_use_consume))
