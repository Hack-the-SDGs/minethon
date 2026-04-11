"""測試 CombatAPI（minecrafthawkeye）。

驗證項目:
- auto_attack(entity, weapon) 開始自動攻擊
- shoot(entity, weapon) 單發射擊
- stop() 停止攻擊
- simply_shot(yaw, pitch) 方向射擊

前置條件:
- bot 需要持有弓和箭
- 附近需有可攻擊的生物
"""

import asyncio
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_true,
    failed,
    info,
    passed,
    run_test,
    section,
    skip,
    wait_prompt,
)

from minethon import Bot
from minethon.models.entity import EntityKind
from minethon.models.weapon import Weapon


async def test_hawkeye(bot: Bot) -> None:
    wait_prompt(
        "請給 bot 一把弓和箭（/give <bot> bow, /give <bot> arrow 64），"
        "並確保附近有生物（zombie 等）"
    )

    # -- 尋找目標 --
    section("尋找攻擊目標")
    target = await bot.find_entity(name="zombie", max_distance=32)
    if target is None:
        target = await bot.find_entity(name="skeleton", max_distance=32)
    if target is None:
        target = await bot.find_entity(name="cow", max_distance=32)
    if target is None:
        info("找不到 zombie/skeleton/cow，嘗試任意 mob")
        target = await bot.find_entity(kind=EntityKind.MOB, max_distance=32)

    if target is None:
        failed("附近找不到任何可攻擊的生物，無法進行戰鬥測試")
        return

    info(f"找到目標: {target.name} (id={target.id})")

    # -- auto_attack --
    section("auto_attack")
    try:
        result = bot.combat.auto_attack(target, Weapon.BOW)
        check_true("auto_attack 回傳 True", result)
        passed("auto_attack 已開始")
    except Exception as exc:
        failed(f"auto_attack 失敗: {exc}")

    wait_prompt("觀察 bot 是否在自動射擊目標，確認後按 Enter 停止")

    # -- stop --
    section("stop")
    try:
        bot.combat.stop()
        passed("stop() 成功")
    except Exception as exc:
        failed(f"stop 失敗: {exc}")

    # -- shoot (single shot) --
    section("shoot (單發)")
    target2 = await bot.find_entity(name=target.name, max_distance=32)
    if target2 is None:
        skip("目標已消失，跳過 shoot 測試")
    else:
        try:
            result = bot.combat.shoot(target2, Weapon.BOW)
            check_true("shoot 回傳 True", result)
            passed("shoot 已發射")
        except Exception as exc:
            failed(f"shoot 失敗: {exc}")
        bot.combat.stop()

    # -- simply_shot --
    section("simply_shot (方向射擊)")
    wait_prompt("bot 即將朝正前方射箭，確認 bot 手持弓後按 Enter")
    try:
        yaw = 0.0
        pitch = -math.pi / 6  # 稍微向上
        info(f"射擊方向: yaw={yaw:.2f}, pitch={pitch:.2f}")
        await bot.combat.simply_shot(yaw, pitch)
        passed("simply_shot 完成")
    except Exception as exc:
        failed(f"simply_shot 失敗: {exc}")


if __name__ == "__main__":
    asyncio.run(run_test("hawkeye", test_hawkeye))
