"""測試 DashboardAPI（@ssmidge/mineflayer-dashboard, experimental）。

驗證項目:
- bot.dashboard.log(*messages) 寫入 dashboard log

前置條件:
- dashboard 使用 blessed terminal UI，可能與 Python stdout 衝突

注意:
- @ssmidge/mineflayer-dashboard 開發於 mineflayer ^2.28.1，
  目前版本 4.37.0 可能存在相容性問題
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    failed,
    info,
    passed,
    run_test,
    section,
    skip,
)

from minethon import Bot


async def test_dashboard(bot: Bot) -> None:
    # -- 載入插件 --
    section("載入 @ssmidge/mineflayer-dashboard")
    try:
        if not bot.plugins.is_loaded("@ssmidge/mineflayer-dashboard"):
            bot.plugins.load("@ssmidge/mineflayer-dashboard")
        passed("@ssmidge/mineflayer-dashboard 已載入")
    except Exception as exc:
        skip(f"無法載入 dashboard: {exc}")
        return

    # -- log --
    section("dashboard.log")
    try:
        bot.dashboard.log("Hello from minethon!")
        passed("log('Hello from minethon!') 成功")
    except Exception as exc:
        failed(f"log 失敗: {exc}")

    try:
        bot.dashboard.log("Line 1", "Line 2", "Line 3")
        passed("log 多行訊息成功")
    except Exception as exc:
        failed(f"log 多行訊息失敗: {exc}")

    info("dashboard 測試完成 — 請注意 blessed UI 可能影響終端顯示")


if __name__ == "__main__":
    asyncio.run(run_test("dashboard", test_dashboard))
