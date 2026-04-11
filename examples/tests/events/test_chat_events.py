"""測試聊天相關事件。

驗證項目:
- ChatEvent 聊天事件
- MessageEvent 解析後訊息事件
- MessageStrEvent 原始字串訊息事件
- ActionBarEvent 動作列訊息事件
- 事件欄位正確性

前置條件:
- 需要另一個玩家在線上以發送聊天訊息
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_not_none,
    check_type,
    info,
    passed,
    run_test,
    section,
    skip,
    wait_prompt,
)

from minethon import Bot, ChatEvent
from minethon.models.events import ActionBarEvent, MessageEvent, MessageStrEvent


async def test_chat_events(bot: Bot) -> None:
    chat_events: list[ChatEvent] = []
    message_events: list[MessageEvent] = []
    message_str_events: list[MessageStrEvent] = []
    action_bar_events: list[ActionBarEvent] = []

    # -- 註冊所有聊天相關 handler --
    section("註冊聊天事件 handlers")

    @bot.observe.on(ChatEvent)
    async def on_chat(event: ChatEvent) -> None:
        chat_events.append(event)
        info(
            f"[ChatEvent] sender={event.sender!r}, message={event.message!r}, timestamp={event.timestamp}"
        )

    @bot.observe.on(MessageEvent)
    async def on_message(event: MessageEvent) -> None:
        message_events.append(event)
        info(
            f"[MessageEvent] message={event.message!r}, position={event.position!r}, sender={event.sender!r}"
        )

    @bot.observe.on(MessageStrEvent)
    async def on_message_str(event: MessageStrEvent) -> None:
        message_str_events.append(event)
        info(
            f"[MessageStrEvent] message={event.message!r}, position={event.position!r}, sender={event.sender!r}"
        )

    @bot.observe.on(ActionBarEvent)
    async def on_action_bar(event: ActionBarEvent) -> None:
        action_bar_events.append(event)
        info(f"[ActionBarEvent] message={event.message!r}")

    info("所有 handler 已註冊")

    # -- 等待聊天訊息 --
    section("等待聊天訊息")
    wait_prompt("請在遊戲中發送聊天訊息，然後按 Enter")

    await asyncio.sleep(2.0)

    # -- 檢查 ChatEvent --
    section("ChatEvent 結果")
    if chat_events:
        passed(f"收到 {len(chat_events)} 個 ChatEvent")
        evt = chat_events[0]
        check_type("ChatEvent type", evt, ChatEvent)
        check_type("sender type", evt.sender, str)
        check_type("message type", evt.message, str)
        check_type("timestamp type", evt.timestamp, float)
        info(f"  sender    = {evt.sender!r}")
        info(f"  message   = {evt.message!r}")
        info(f"  timestamp = {evt.timestamp}")
    else:
        skip("沒有收到 ChatEvent")

    # -- 檢查 MessageEvent --
    section("MessageEvent 結果")
    if message_events:
        passed(f"收到 {len(message_events)} 個 MessageEvent")
        evt = message_events[0]
        check_type("MessageEvent type", evt, MessageEvent)
        info(f"  message   = {evt.message!r}")
        info(f"  position  = {evt.position!r}")
        info(f"  sender    = {evt.sender!r}")
        info(f"  verified  = {evt.verified}")
    else:
        skip("沒有收到 MessageEvent")

    # -- 檢查 MessageStrEvent --
    section("MessageStrEvent 結果")
    if message_str_events:
        passed(f"收到 {len(message_str_events)} 個 MessageStrEvent")
        evt = message_str_events[0]
        check_type("MessageStrEvent type", evt, MessageStrEvent)
        info(f"  message   = {evt.message!r}")
        info(f"  position  = {evt.position!r}")
        info(f"  sender    = {evt.sender!r}")
        info(f"  verified  = {evt.verified}")
    else:
        skip("沒有收到 MessageStrEvent")

    # -- 檢查 ActionBarEvent --
    section("ActionBarEvent 結果")
    if action_bar_events:
        passed(f"收到 {len(action_bar_events)} 個 ActionBarEvent")
        evt = action_bar_events[0]
        check_type("ActionBarEvent type", evt, ActionBarEvent)
        info(f"  message = {evt.message!r}")
    else:
        skip("沒有收到 ActionBarEvent（需要伺服器發送 action bar 訊息）")

    # -- wait_for(ChatEvent) --
    section("wait_for(ChatEvent)")
    wait_prompt("請再發送一則聊天訊息，然後按 Enter")
    try:
        event = await bot.observe.wait_for(ChatEvent, timeout=30.0)
        passed("wait_for(ChatEvent) 成功")
        check_not_none("event", event)
        info(f"sender={event.sender!r}, message={event.message!r}")
    except TimeoutError:
        skip("wait_for(ChatEvent) 超時")

    # -- 清理 --
    bot.observe.off(ChatEvent, on_chat)
    bot.observe.off(MessageEvent, on_message)
    bot.observe.off(MessageStrEvent, on_message_str)
    bot.observe.off(ActionBarEvent, on_action_bar)
    info("所有 handler 已取消註冊")


if __name__ == "__main__":
    asyncio.run(run_test("chat_events", test_chat_events))
