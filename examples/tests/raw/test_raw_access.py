"""測試 Raw escape hatch。

驗證項目:
- bot.raw.js_bot → raw JS proxy
- bot.raw.on(event_name, handler) 註冊 raw 事件
- bot.raw.off(event_name, handler) 取消註冊
- bot.raw.plugin(name) → raw JS module
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_not_none,
    failed,
    info,
    passed,
    run_test,
    section,
)

from minethon import Bot


async def test_raw_access(bot: Bot) -> None:
    # -- js_bot --
    section("js_bot")
    try:
        js_bot = bot.raw.js_bot
        check_not_none("bot.raw.js_bot", js_bot)
        info(f"js_bot 類型: {type(js_bot).__name__}")
        passed("js_bot 存取成功")
    except Exception as exc:
        failed(f"js_bot 存取失敗: {exc}")
        return

    # -- 讀取 raw 屬性 --
    section("讀取 raw 屬性")
    try:
        username = js_bot.username
        info(f"js_bot.username = {username}")
        passed("讀取 raw property 成功")
    except Exception as exc:
        failed(f"讀取 raw property 失敗: {exc}")

    # -- on / off --
    section("on / off (raw 事件)")
    event_received = asyncio.Event()

    async def on_chat(payload: dict) -> None:
        info(f"收到 raw chat 事件: {payload}")
        event_received.set()

    try:
        bot.raw.on("chat", on_chat)
        passed("on('chat', handler) 註冊成功")
    except Exception as exc:
        failed(f"on 失敗: {exc}")

    try:
        bot.raw.off("chat", on_chat)
        passed("off('chat', handler) 取消註冊成功")
    except Exception as exc:
        failed(f"off 失敗: {exc}")

    # -- plugin --
    section("plugin (raw 插件載入)")
    try:
        # 嘗試載入一個已知的插件模組
        raw_module = bot.raw.plugin("mineflayer-pathfinder")
        check_not_none("raw.plugin('mineflayer-pathfinder')", raw_module)
        info(f"raw module 類型: {type(raw_module).__name__}")
        passed("raw.plugin() 載入成功")
    except Exception as exc:
        info(f"raw.plugin() 失敗（可能未安裝）: {exc}")

    info("raw_access 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("raw_access", test_raw_access))
