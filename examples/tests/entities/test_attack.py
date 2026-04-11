"""測試攻擊實體 API。

驗證項目:
- attack() 攻擊一個實體

前置條件:
- Survival 模式
- 附近有可攻擊的生物
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


async def test_attack(bot: Bot) -> None:
    wait_prompt("請確認 bot 附近有可攻擊的生物（如殭屍、骷髏、牛、豬等）")

    # -- 搜尋可攻擊的生物 --
    section("搜尋可攻擊的生物")

    target = None
    # 先找敵對生物
    target = await bot.find_entity(kind=EntityKind.HOSTILE, max_distance=16)
    if target is not None:
        info(f"找到敵對生物: {target.name} (id={target.id}) at {target.position}")
    else:
        # 再找動物
        target = await bot.find_entity(kind=EntityKind.ANIMAL, max_distance=16)
        if target is not None:
            info(f"找到動物: {target.name} (id={target.id}) at {target.position}")
        else:
            # 最後找任何 MOB
            target = await bot.find_entity(kind=EntityKind.MOB, max_distance=16)
            if target is not None:
                info(f"找到生物: {target.name} (id={target.id}) at {target.position}")

    if target is None:
        skip("附近沒有找到可攻擊的生物")
        return

    # -- attack --
    section("attack")
    info(f"攻擊 {target.name} (id={target.id}) ...")
    try:
        await bot.attack(target)
        passed("attack() 完成")
    except Exception as exc:
        failed(f"attack() 失敗: {exc}")

    wait_prompt("請確認 bot 揮擊了生物（應該看到揮擊動畫和傷害效果）")

    # -- 連續攻擊 --
    section("連續攻擊測試")
    info("嘗試連續攻擊 3 次 (間隔 0.5 秒)")
    for i in range(3):
        # 重新搜尋（目標可能已移動或死亡）
        refreshed = await bot.find_entity(kind=target.kind, max_distance=16)
        if refreshed is None:
            info(f"第 {i + 1} 次: 目標已不在範圍內")
            break
        try:
            await bot.attack(refreshed)
            info(f"第 {i + 1} 次攻擊完成 (目標: {refreshed.name})")
        except Exception as exc:
            info(f"第 {i + 1} 次攻擊失敗: {exc}")
            break
        await asyncio.sleep(0.5)

    wait_prompt("請確認連續攻擊效果")


if __name__ == "__main__":
    asyncio.run(run_test("attack", test_attack))
