"""測試 NavigationAPI（mineflayer-pathfinder）。

驗證項目:
- goto(x, y, z, radius=1.0) 導航到指定座標
- follow(username, distance=2.0) 跟隨玩家
- stop() 停止導航
- is_navigating 屬性在導航期間為 True

前置條件:
- mineflayer-pathfinder 自動載入
- follow 測試需要另一位玩家在場
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_false,
    check_true,
    failed,
    info,
    passed,
    run_test,
    section,
    wait_prompt,
)

from minethon import Bot


async def test_pathfinder(bot: Bot) -> None:
    # -- goto --
    section("goto")
    pos = bot.position
    if pos is None:
        failed("bot.position is None, cannot test goto")
        return

    target_x = pos.x + 20
    target_y = pos.y
    target_z = pos.z
    info(f"目前位置: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})")
    info(f"目標位置: ({target_x:.1f}, {target_y:.1f}, {target_z:.1f})")

    # Start goto in a task so we can check is_navigating
    goto_task = asyncio.create_task(
        bot.navigation.goto(target_x, target_y, target_z, radius=2.0)
    )
    await asyncio.sleep(0.5)
    check_true("is_navigating (導航中)", bot.navigation.is_navigating)

    try:
        await goto_task
        passed("goto 完成，bot 已到達目標")
    except Exception as exc:
        failed(f"goto 失敗: {exc}")

    check_false("is_navigating (導航結束)", bot.navigation.is_navigating)

    arrival = bot.position
    if arrival is not None:
        info(f"到達位置: ({arrival.x:.1f}, {arrival.y:.1f}, {arrival.z:.1f})")

    # -- follow --
    section("follow")
    print("\n  >>> 請輸入附近玩家名稱（留空跳過 follow 測試）:")
    player_name = input("  玩家名稱: ").strip()  # noqa: ASYNC250
    if not player_name:
        info("未輸入玩家名稱，跳過 follow 測試")
    else:
        try:
            await bot.navigation.follow(player_name, distance=3.0)
            check_true("is_navigating (跟隨中)", bot.navigation.is_navigating)
            passed(f"follow({player_name!r}) 已開始")
            wait_prompt("觀察 bot 是否在跟隨玩家移動，確認後按 Enter 停止")
        except Exception as exc:
            failed(f"follow 失敗: {exc}")

    # -- stop --
    section("stop")
    await bot.navigation.stop()
    check_false("is_navigating (已停止)", bot.navigation.is_navigating)
    passed("stop() 成功")


if __name__ == "__main__":
    asyncio.run(run_test("pathfinder", test_pathfinder))
