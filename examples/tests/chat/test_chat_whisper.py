"""test_chat_whisper.py -- 測試 bot.chat() 和 bot.whisper() 聊天功能。

驗證項目:
- chat() 發送公開聊天訊息
- whisper() 發送私訊
- 測試者需在遊戲中目視確認訊息
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _common import (
    Bot,
    info,
    passed,
    run_test,
    section,
    wait_prompt,
)


async def test_chat_whisper(bot: Bot) -> None:
    section("chat() 公開聊天")

    msg = "Hello from minethon integration test!"
    info(f"發送公開訊息: {msg!r}")
    await bot.chat(msg)
    passed("chat() 呼叫成功")
    wait_prompt("請在遊戲中確認看到公開聊天訊息")

    section("chat() 發送中文訊息")

    msg_zh = "minethon 整合測試 -- 中文訊息"
    info(f"發送中文訊息: {msg_zh!r}")
    await bot.chat(msg_zh)
    passed("chat() 中文呼叫成功")
    wait_prompt("請在遊戲中確認看到中文聊天訊息")

    section("whisper() 私訊")

    target = bot.username
    info(f"私訊目標: {target}")
    info("（預設對自己發送私訊，如需測試對其他玩家私訊請修改腳本）")

    whisper_msg = "This is a whisper test from minethon"
    info(f"發送私訊: {whisper_msg!r}")
    await bot.whisper(target, whisper_msg)
    passed("whisper() 呼叫成功")
    wait_prompt("請在遊戲中確認看到私訊（/msg 格式）")


if __name__ == "__main__":
    asyncio.run(run_test("chat_whisper", test_chat_whisper))
