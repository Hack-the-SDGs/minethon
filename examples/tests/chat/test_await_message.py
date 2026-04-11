"""test_await_message.py -- 測試 bot.await_message() 等待聊天訊息。

驗證項目:
- 使用 regex 匹配任意訊息
- 等待玩家在遊戲中發送訊息
- 印出接收到的訊息內容
"""

import asyncio
import re
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
    wait_prompt,
)


async def test_await_message(bot: Bot) -> None:
    section("await_message() 等待訊息測試")

    wait_prompt("準備好後按 Enter，然後在 30 秒內於遊戲中對 bot 說一句話")

    info("等待聊天訊息（timeout=30s）...")
    info("使用 regex r'.*' 匹配任意訊息")

    try:
        message = await bot.await_message(re.compile(r".*"), timeout=30.0)
        passed("成功接收到訊息")
        info(f"訊息內容: {message!r}")
    except TimeoutError:
        failed("等待逾時（30 秒內未收到任何訊息）")
        return

    section("await_message() 精確匹配測試")

    keyword = "ping"
    info(f"等待包含 {keyword!r} 的訊息（timeout=30s）...")
    wait_prompt(f'請在遊戲中發送包含 "{keyword}" 的訊息（例如 "ping"）')

    try:
        message = await bot.await_message(
            re.compile(rf".*{keyword}.*", re.IGNORECASE),
            timeout=30.0,
        )
        passed("成功匹配到訊息")
        info(f"訊息內容: {message!r}")
    except TimeoutError:
        failed(f'等待逾時（30 秒內未收到包含 "{keyword}" 的訊息）')


if __name__ == "__main__":
    asyncio.run(run_test("await_message", test_await_message))
