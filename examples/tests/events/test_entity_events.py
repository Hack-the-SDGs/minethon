"""測試實體相關事件。

驗證項目:
- EntitySpawnEvent 實體生成事件
- EntityGoneEvent 實體消失事件
- PlayerJoinedEvent 玩家加入事件
- PlayerLeftEvent 玩家離開事件

前置條件:
- 附近有生物生成/消失活動
- 或有玩家加入/離開伺服器
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_type,
    info,
    passed,
    run_test,
    section,
    skip,
    wait_prompt,
)

from minethon import Bot
from minethon.models.events import (
    EntityGoneEvent,
    EntitySpawnEvent,
    PlayerJoinedEvent,
    PlayerLeftEvent,
)

_LISTEN_SECONDS = 30


async def test_entity_events(bot: Bot) -> None:
    spawn_events: list[EntitySpawnEvent] = []
    gone_events: list[EntityGoneEvent] = []
    join_events: list[PlayerJoinedEvent] = []
    left_events: list[PlayerLeftEvent] = []

    # -- 註冊 handlers --
    section("註冊實體事件 handlers")

    @bot.observe.on(EntitySpawnEvent)
    async def on_spawn(event: EntitySpawnEvent) -> None:
        spawn_events.append(event)
        entity_name = event.entity.name if event.entity else "unknown"
        info(f"[EntitySpawnEvent] entity_id={event.entity_id}, name={entity_name!r}")

    @bot.observe.on(EntityGoneEvent)
    async def on_gone(event: EntityGoneEvent) -> None:
        gone_events.append(event)
        info(f"[EntityGoneEvent] entity_id={event.entity_id}")

    @bot.observe.on(PlayerJoinedEvent)
    async def on_join(event: PlayerJoinedEvent) -> None:
        join_events.append(event)
        info(f"[PlayerJoinedEvent] username={event.username!r}, uuid={event.uuid}")

    @bot.observe.on(PlayerLeftEvent)
    async def on_left(event: PlayerLeftEvent) -> None:
        left_events.append(event)
        info(f"[PlayerLeftEvent] username={event.username!r}")

    info("所有 handler 已註冊")

    # -- 等待事件 --
    section(f"監聽事件 ({_LISTEN_SECONDS} 秒)")
    wait_prompt(
        f"請在接下來 {_LISTEN_SECONDS} 秒內執行以下操作:\n"
        "  - 在 bot 附近生成或擊殺生物\n"
        "  - 或讓玩家加入/離開伺服器\n"
        "按 Enter 開始監聽"
    )

    info(f"開始監聽，持續 {_LISTEN_SECONDS} 秒 ...")
    await asyncio.sleep(_LISTEN_SECONDS)

    # -- 報告結果 --
    section("EntitySpawnEvent 結果")
    if spawn_events:
        passed(f"收到 {len(spawn_events)} 個 EntitySpawnEvent")
        for evt in spawn_events[:5]:
            check_type("EntitySpawnEvent type", evt, EntitySpawnEvent)
            check_type("entity_id type", evt.entity_id, int)
            entity_name = evt.entity.name if evt.entity else "unknown"
            info(f"  entity_id={evt.entity_id}, name={entity_name!r}")
        if len(spawn_events) > 5:
            info(f"  ... 以及 {len(spawn_events) - 5} 個其他事件")
    else:
        skip("沒有收到 EntitySpawnEvent（附近可能沒有新實體生成）")

    section("EntityGoneEvent 結果")
    if gone_events:
        passed(f"收到 {len(gone_events)} 個 EntityGoneEvent")
        for evt in gone_events[:5]:
            check_type("EntityGoneEvent type", evt, EntityGoneEvent)
            info(f"  entity_id={evt.entity_id}")
        if len(gone_events) > 5:
            info(f"  ... 以及 {len(gone_events) - 5} 個其他事件")
    else:
        skip("沒有收到 EntityGoneEvent（附近可能沒有實體消失）")

    section("PlayerJoinedEvent 結果")
    if join_events:
        passed(f"收到 {len(join_events)} 個 PlayerJoinedEvent")
        for evt in join_events:
            check_type("PlayerJoinedEvent type", evt, PlayerJoinedEvent)
            check_type("username type", evt.username, str)
            check_type("uuid type", evt.uuid, str)
            info(f"  username={evt.username!r}, uuid={evt.uuid}")
            info(f"  ping={evt.ping}, game_mode={evt.game_mode}")
            info(f"  display_name={evt.display_name!r}")
    else:
        skip("沒有收到 PlayerJoinedEvent（沒有玩家加入）")

    section("PlayerLeftEvent 結果")
    if left_events:
        passed(f"收到 {len(left_events)} 個 PlayerLeftEvent")
        for evt in left_events:
            check_type("PlayerLeftEvent type", evt, PlayerLeftEvent)
            check_type("username type", evt.username, str)
            info(f"  username={evt.username!r}")
    else:
        skip("沒有收到 PlayerLeftEvent（沒有玩家離開）")

    # -- 統計總覽 --
    section("事件統計")
    total = len(spawn_events) + len(gone_events) + len(join_events) + len(left_events)
    info(f"EntitySpawnEvent:  {len(spawn_events)}")
    info(f"EntityGoneEvent:   {len(gone_events)}")
    info(f"PlayerJoinedEvent: {len(join_events)}")
    info(f"PlayerLeftEvent:   {len(left_events)}")
    info(f"總計:              {total}")

    # -- 清理 --
    bot.observe.off(EntitySpawnEvent, on_spawn)
    bot.observe.off(EntityGoneEvent, on_gone)
    bot.observe.off(PlayerJoinedEvent, on_join)
    bot.observe.off(PlayerLeftEvent, on_left)
    info("所有 handler 已取消註冊")


if __name__ == "__main__":
    asyncio.run(run_test("entity_events", test_entity_events))
