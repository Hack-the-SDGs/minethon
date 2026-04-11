"""測試方塊挖掘 API。

驗證項目:
- can_dig_block() 判斷方塊是否可挖
- dig_time() 估算挖掘時間
- dig() 挖掘方塊
- stop_digging() 中斷挖掘

前置條件:
- Survival 模式
- 附近有可挖掘方塊 (dirt / stone)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_true,
    check_type,
    info,
    run_test,
    section,
    skip,
    wait_prompt,
)

from minethon import Bot


async def test_dig(bot: Bot) -> None:
    # -- 尋找可挖掘方塊 --
    section("尋找可挖掘方塊")
    target = None
    for name in ("dirt", "stone", "cobblestone", "sand", "gravel"):
        blocks = await bot.find_block(name, max_distance=32, count=1)
        if blocks:
            target = blocks[0]
            info(f"找到 {target.name} at {target.position}")
            break

    if target is None:
        skip("附近沒有找到可挖掘的方塊 (dirt/stone/cobblestone/sand/gravel)")
        return

    # -- can_dig_block --
    section("can_dig_block")
    can_dig = await bot.can_dig_block(target)
    check_type("can_dig_block 型別", can_dig, bool)
    check_true("can_dig_block", can_dig)

    # -- dig_time --
    section("dig_time")
    dt = await bot.dig_time(target)
    check_type("dig_time 型別", dt, int)
    info(f"dig_time({target.name}) = {dt} ms")
    check_true("dig_time > 0", dt > 0)

    # -- dig --
    section("dig")
    info(f"開始挖掘 {target.name} at {target.position} ...")
    await bot.dig(target)
    info("dig() 完成")
    wait_prompt("請在遊戲中確認方塊已被挖掘")

    # -- stop_digging --
    section("stop_digging")
    target2 = None
    for name in ("dirt", "stone", "cobblestone", "sand", "gravel"):
        blocks = await bot.find_block(name, max_distance=32, count=1)
        if blocks:
            target2 = blocks[0]
            break

    if target2 is None:
        skip("附近沒有第二個方塊可供測試 stop_digging")
        return

    info(f"找到第二個方塊 {target2.name} at {target2.position}")
    info("測試: 嘗試挖掘後立即停止")

    # 用 asyncio.create_task 啟動挖掘，然後短暫延遲後停止
    dig_task = asyncio.create_task(bot.dig(target2))
    await asyncio.sleep(0.3)

    try:
        await bot.stop_digging()
        info("stop_digging() 已呼叫")
    except Exception as exc:
        info(f"stop_digging() 異常（可預期）: {exc}")

    # 等待 dig task 結束（可能因停止而失敗）
    try:
        await asyncio.wait_for(dig_task, timeout=5.0)
        info("dig task 完成（方塊可能在停止前已挖完）")
    except Exception as exc:
        info(f"dig task 異常（預期行為）: {type(exc).__name__}: {exc}")

    wait_prompt("請確認第二個方塊是否仍存在（stop_digging 應中斷挖掘）")


if __name__ == "__main__":
    asyncio.run(run_test("dig", test_dig))
