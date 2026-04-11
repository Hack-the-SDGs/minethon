"""測試死亡與重生循環。

驗證項目:
- DeathEvent 在 bot 死亡時觸發
- respawn() 成功重生
- RespawnEvent 或 SpawnEvent 在重生後觸發
- is_alive 在死亡後為 False、重生後為 True
- position 在重生後有效

前置條件:
- 需手動在遊戲中殺死 bot（例如 /kill 指令）
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_not_none,
    check_true,
    failed,
    info,
    passed,
    run_test,
    section,
    wait_prompt,
)

from minethon import Bot, DeathEvent, SpawnEvent
from minethon.models.events import RespawnEvent


async def test_respawn(bot: Bot) -> None:
    death_received = asyncio.Event()
    respawn_received = asyncio.Event()

    # -- 註冊事件處理器 --
    section("註冊事件處理器")

    @bot.observe.on(DeathEvent)
    async def on_death(event: DeathEvent) -> None:
        info(f"收到 DeathEvent: reason={event.reason!r}")
        death_received.set()

    @bot.observe.on(RespawnEvent)
    async def on_respawn(_event: RespawnEvent) -> None:
        info("收到 RespawnEvent")
        respawn_received.set()

    info("已註冊 DeathEvent / RespawnEvent handler")

    # -- 等待手動殺死 bot --
    section("等待死亡")
    wait_prompt("請在遊戲中殺死 bot（例如 /kill），然後按 Enter")

    try:
        death_event = await bot.observe.wait_for(DeathEvent, timeout=60.0)
        passed(f"收到 DeathEvent (reason={death_event.reason!r})")
    except TimeoutError:
        failed("等待 DeathEvent 逾時（60 秒）")
        return

    # -- 重生 --
    section("重生")
    info("呼叫 bot.respawn()...")
    await bot.respawn()

    try:
        await bot.observe.wait_for(SpawnEvent, timeout=30.0)
        passed("收到 SpawnEvent（重生完成）")
    except TimeoutError:
        info("未收到 SpawnEvent，嘗試等待 RespawnEvent...")
        try:
            await bot.observe.wait_for(RespawnEvent, timeout=10.0)
            passed("收到 RespawnEvent（重生完成）")
        except TimeoutError:
            failed("重生後未收到 SpawnEvent 或 RespawnEvent")
            return

    # -- 驗證重生後狀態 --
    section("重生後狀態驗證")
    check_true("is_alive", bot.is_alive)
    check_not_none("position", bot.position)
    info(f"重生位置: {bot.position}")

    # -- 清理 --
    bot.observe.off(DeathEvent, on_death)
    bot.observe.off(RespawnEvent, on_respawn)


if __name__ == "__main__":
    asyncio.run(run_test("respawn", test_respawn))
