"""測試 ViewerAPI（prismarine-viewer）。

驗證項目:
- await bot.viewer.start(port=3007, view_distance=6, first_person=False)
- bot.viewer.stop()
- bot.viewer.is_started

前置條件:
- 確保 port 3007 未被佔用
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
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


async def test_viewer(bot: Bot) -> None:
    # -- 啟動前狀態 --
    section("啟動前狀態")
    check_false("is_started (啟動前)", bot.viewer.is_started)

    # -- start --
    section("start")
    try:
        await bot.viewer.start(port=3007, view_distance=6, first_person=False)
        passed("viewer.start(port=3007) 成功")
    except Exception as exc:
        failed(f"viewer.start 失敗: {exc}")
        return

    check_true("is_started (啟動後)", bot.viewer.is_started)

    wait_prompt("請在瀏覽器開啟 http://localhost:3007 確認 3D 場景正常顯示")

    # -- 再次啟動（冪等性） --
    section("start (冪等性)")
    try:
        await bot.viewer.start(port=3007)
        passed("重複呼叫 start() 未拋出異常（冪等）")
    except Exception as exc:
        failed(f"重複 start() 拋出異常: {exc}")

    # -- stop --
    section("stop")
    try:
        bot.viewer.stop()
        passed("viewer.stop() 成功")
    except Exception as exc:
        failed(f"viewer.stop 失敗: {exc}")

    check_false("is_started (停止後)", bot.viewer.is_started)

    # -- 再次停止（安全呼叫） --
    section("stop (安全呼叫)")
    try:
        bot.viewer.stop()
        passed("重複呼叫 stop() 未拋出異常")
    except Exception as exc:
        failed(f"重複 stop() 拋出異常: {exc}")

    info("viewer 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("viewer", test_viewer))
