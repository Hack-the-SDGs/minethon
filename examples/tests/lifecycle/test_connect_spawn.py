"""測試 Bot 連線、重生、斷線的基本生命週期。

驗證項目:
- connect() 成功連線
- wait_until_spawned() 等待重生
- is_connected 連線後為 True
- is_alive 重生後為 True
- username 有效
- version 有效
- disconnect() 斷線後 is_connected 為 False
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_false,
    check_not_none,
    check_true,
    create_bot,
    info,
    section,
)


async def main() -> None:
    bot = create_bot()

    # -- 連線 --
    section("connect + wait_until_spawned")
    await bot.connect()
    await bot.wait_until_spawned()
    info(f"Bot 已連線並重生於 {bot.position}")

    # -- 連線狀態 --
    section("連線狀態")
    check_true("is_connected", bot.is_connected)
    check_true("is_alive", bot.is_alive)

    # -- 基本屬性 --
    section("username / version")
    check_not_none("username", bot.username)
    info(f"username = {bot.username}")
    check_not_none("version", bot.version)
    info(f"version = {bot.version}")

    # -- 斷線 --
    section("disconnect")
    await bot.disconnect()
    check_false("is_connected", bot.is_connected)

    info("生命週期測試完成")


if __name__ == "__main__":
    asyncio.run(main())
