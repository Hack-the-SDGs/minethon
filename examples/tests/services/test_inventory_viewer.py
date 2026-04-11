"""測試 InventoryViewerAPI（mineflayer-web-inventory）。

驗證項目:
- bot.inventory_viewer.initialize(port=3008)
- await bot.inventory_viewer.start()
- await bot.inventory_viewer.stop()
- bot.inventory_viewer.is_running
- bot.inventory_viewer.is_initialized
- bot.inventory_viewer.port

前置條件:
- 確保 port 3008 未被佔用
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check,
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


async def test_inventory_viewer(bot: Bot) -> None:
    iv = bot.inventory_viewer

    # -- 初始化前狀態 --
    section("初始化前狀態")
    check_false("is_initialized (初始化前)", iv.is_initialized)
    check_false("is_running (初始化前)", iv.is_running)
    check("port (初始化前)", iv.port, None)

    # -- initialize --
    section("initialize")
    try:
        iv.initialize(port=3008)
        passed("initialize(port=3008) 成功")
    except Exception as exc:
        failed(f"initialize 失敗: {exc}")
        return

    check_true("is_initialized (初始化後)", iv.is_initialized)
    check_false("is_running (未啟動)", iv.is_running)
    check("port", iv.port, 3008)

    # -- start --
    section("start")
    try:
        await iv.start()
        passed("start() 成功")
    except Exception as exc:
        failed(f"start 失敗: {exc}")
        return

    check_true("is_running (啟動後)", iv.is_running)

    wait_prompt("請在瀏覽器開啟 http://localhost:3008 確認物品欄 UI 正常顯示")

    # -- stop --
    section("stop")
    try:
        await iv.stop()
        passed("stop() 成功")
    except Exception as exc:
        failed(f"stop 失敗: {exc}")

    check_false("is_running (停止後)", iv.is_running)
    check_true("is_initialized (停止後仍保持初始化)", iv.is_initialized)

    info("inventory_viewer 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("inventory_viewer", test_inventory_viewer))
