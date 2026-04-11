"""test_vehicle.py -- 測試 bot 的載具操作 API。

驗證項目:
- mount() 騎乘附近的生物（馬/豬等）
- move_vehicle() 控制載具移動
- dismount() 下馬
- elytra_fly() 鞘翅飛行（需要特殊條件，僅提示）
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
    skip,
    wait_prompt,
)

from minethon import Entity, EntityKind


async def test_vehicle(bot: Bot) -> None:
    # -- 騎乘測試 --
    section("mount() / move_vehicle() / dismount() 載具測試")

    wait_prompt("請將 bot 附近放置一隻可騎乘的生物（馬/豬），然後按 Enter")

    info("搜尋附近的生物...")
    entities = await bot.get_entities()

    mountable: Entity | None = None
    bot_pos = bot.position
    closest_dist = float("inf")

    for entity in entities.values():
        if entity.kind in (EntityKind.MOB, EntityKind.ANIMAL):
            dx = entity.position.x - bot_pos.x
            dy = entity.position.y - bot_pos.y
            dz = entity.position.z - bot_pos.z
            dist = (dx * dx + dy * dy + dz * dz) ** 0.5
            if dist < closest_dist:
                closest_dist = dist
                mountable = entity

    if mountable is None:
        failed("附近未找到可騎乘的生物")
        info("請確認附近有馬、豬或其他可騎乘的生物")
        return

    info(f"找到生物: {mountable.name} (id={mountable.id}, 距離={closest_dist:.2f})")

    info("嘗試騎乘...")
    try:
        await bot.mount(mountable)
        passed("mount() 呼叫成功")
    except Exception as exc:
        failed(f"mount() 失敗: {exc}")
        return

    await asyncio.sleep(1.0)

    info("嘗試控制載具前進...")
    try:
        await bot.move_vehicle(0.0, 1.0)
        passed("move_vehicle(0, 1) 呼叫成功")
    except Exception as exc:
        failed(f"move_vehicle() 失敗: {exc}")

    await asyncio.sleep(2.0)
    wait_prompt("請在遊戲中觀察 bot 是否騎在生物上並移動，然後按 Enter")

    info("嘗試下馬...")
    try:
        await bot.dismount()
        passed("dismount() 呼叫成功")
    except Exception as exc:
        failed(f"dismount() 失敗: {exc}")

    await asyncio.sleep(0.5)

    # -- 鞘翅飛行 --
    section("elytra_fly() 鞘翅飛行測試")

    skip(
        "鞘翅飛行需要特殊條件:\n"
        "    1. Bot 裝備鞘翅（Elytra）\n"
        "    2. Bot 站在高處\n"
        "    3. 需要先跳躍再啟動飛行\n"
        "    如需測試，請手動設定環境後執行以下程式碼:\n"
        "      await bot.jump()\n"
        "      await asyncio.sleep(0.1)\n"
        "      await bot.elytra_fly()"
    )


if __name__ == "__main__":
    asyncio.run(run_test("vehicle", test_vehicle))
