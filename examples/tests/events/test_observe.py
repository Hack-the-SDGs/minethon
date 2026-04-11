"""測試 ObserveAPI 事件系統核心機制。

驗證項目:
- on() decorator 模式
- on() 直接呼叫模式
- off() 取消訂閱後不再收到事件
- wait_for() 等待單次事件

前置條件:
- 需要另一個玩家在線上以發送聊天訊息
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_type,
    failed,
    info,
    passed,
    run_test,
    section,
    wait_prompt,
)

from minethon import Bot, ChatEvent


async def test_observe(bot: Bot) -> None:
    # -- on() decorator 模式 --
    section("on() decorator 模式")

    decorator_received: list[ChatEvent] = []

    @bot.observe.on(ChatEvent)
    async def on_chat_decorator(event: ChatEvent) -> None:
        decorator_received.append(event)
        info(
            f"[decorator] 收到 ChatEvent: sender={event.sender!r}, message={event.message!r}"
        )

    info("已註冊 decorator handler")
    wait_prompt("請在遊戲中發送一則聊天訊息，然後按 Enter")

    # 給一點時間讓事件傳遞
    await asyncio.sleep(1.0)

    if decorator_received:
        passed(f"decorator handler 收到 {len(decorator_received)} 個事件")
        check_type("事件型別", decorator_received[0], ChatEvent)
    else:
        failed("decorator handler 沒有收到任何事件")

    # -- on() 直接呼叫模式 --
    section("on() 直接呼叫模式")

    direct_received: list[ChatEvent] = []

    async def on_chat_direct(event: ChatEvent) -> None:
        direct_received.append(event)
        info(
            f"[direct] 收到 ChatEvent: sender={event.sender!r}, message={event.message!r}"
        )

    bot.observe.on(ChatEvent, on_chat_direct)
    info("已註冊 direct handler")
    wait_prompt("請再發送一則聊天訊息，然後按 Enter")

    await asyncio.sleep(1.0)

    if direct_received:
        passed(f"direct handler 收到 {len(direct_received)} 個事件")
    else:
        failed("direct handler 沒有收到任何事件")

    # 此時 decorator handler 應該也有收到
    decorator_count_before_off = len(decorator_received)
    info(f"decorator handler 累計收到 {decorator_count_before_off} 個事件")

    # -- off() 取消訂閱 --
    section("off() 取消訂閱")

    bot.observe.off(ChatEvent, on_chat_direct)
    info("已取消 direct handler 訂閱")

    direct_count_before = len(direct_received)
    wait_prompt("請再發送一則聊天訊息（驗證 off 後不再收到），然後按 Enter")

    await asyncio.sleep(1.0)

    if len(direct_received) == direct_count_before:
        passed("off() 後 direct handler 沒有收到新事件")
    else:
        failed(
            f"off() 後 direct handler 仍收到了 {len(direct_received) - direct_count_before} 個新事件"
        )

    # decorator handler 應該仍然有收到
    if len(decorator_received) > decorator_count_before_off:
        passed("decorator handler 在 off(direct) 後仍正常接收事件")
    else:
        info("decorator handler 沒有收到新事件（可能訊息未送達）")

    # 清理 decorator handler
    bot.observe.off(ChatEvent, on_chat_decorator)
    info("已取消 decorator handler 訂閱")

    # -- wait_for() --
    section("wait_for()")
    info("等待一個 ChatEvent（timeout=30s）")
    wait_prompt("請發送一則聊天訊息，然後按 Enter")

    try:
        event = await bot.observe.wait_for(ChatEvent, timeout=30.0)
        passed("wait_for() 成功收到事件")
        check_type("wait_for 結果型別", event, ChatEvent)
        info(f"sender={event.sender!r}, message={event.message!r}")
    except TimeoutError:
        failed("wait_for() 超時（30 秒內沒有收到 ChatEvent）")

    # -- wait_for() timeout 測試 --
    section("wait_for() timeout")
    info("測試 wait_for() 短暫 timeout (2s)，不要發送訊息")
    try:
        await bot.observe.wait_for(ChatEvent, timeout=2.0)
        info("意外收到了事件（可能有其他來源的聊天訊息）")
    except TimeoutError:
        passed("wait_for() 正確拋出 TimeoutError")


if __name__ == "__main__":
    asyncio.run(run_test("observe", test_observe))
