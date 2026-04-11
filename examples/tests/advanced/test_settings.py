"""測試客戶端設定與雜項功能。

驗證項目:
- await bot.set_settings(**options) 更新客戶端設定
- bot.support_feature(name) 查詢協議功能支援
- await bot.tab_complete(text) 請求 tab 補全
- await bot.wait_for_chunks_to_load() 等待區塊載入
- await bot.wait_for_ticks(ticks) 等待指定 ticks
- await bot.accept_resource_pack() / await bot.deny_resource_pack()
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
)

from minethon import Bot


async def test_settings(bot: Bot) -> None:
    # -- set_settings --
    section("set_settings")
    try:
        await bot.set_settings(viewDistance=8)
        passed("set_settings(viewDistance=8) 成功")
    except Exception as exc:
        failed(f"set_settings 失敗: {exc}")

    # -- support_feature --
    section("support_feature")
    try:
        result = bot.support_feature("signedChat")
        check_type("support_feature 回傳", result, bool)
        info(f"support_feature('signedChat') = {result}")
        passed("support_feature 成功")
    except Exception as exc:
        failed(f"support_feature 失敗: {exc}")

    try:
        result = bot.support_feature("nonexistentFeature")
        info(f"support_feature('nonexistentFeature') = {result}")
    except Exception as exc:
        info(f"support_feature 對未知功能: {exc}")

    # -- tab_complete --
    section("tab_complete")
    try:
        suggestions = await bot.tab_complete("/game")
        check_type("tab_complete 回傳", suggestions, list)
        info(f"tab_complete('/game') 建議數量: {len(suggestions)}")
        for s in suggestions[:5]:
            info(f"  - {s}")
        if len(suggestions) > 5:
            info(f"  ... 及其他 {len(suggestions) - 5} 個")
        passed("tab_complete 成功")
    except Exception as exc:
        failed(f"tab_complete 失敗: {exc}")

    # -- wait_for_chunks_to_load --
    section("wait_for_chunks_to_load")
    try:
        await bot.wait_for_chunks_to_load()
        passed("wait_for_chunks_to_load 完成")
    except Exception as exc:
        failed(f"wait_for_chunks_to_load 失敗: {exc}")

    # -- wait_for_ticks --
    section("wait_for_ticks")
    try:
        info("等待 20 ticks (~1 秒)...")
        await bot.wait_for_ticks(20)
        passed("wait_for_ticks(20) 完成")
    except Exception as exc:
        failed(f"wait_for_ticks 失敗: {exc}")

    # -- accept/deny_resource_pack --
    section("accept_resource_pack / deny_resource_pack")
    info("這些方法僅在伺服器發送 resource pack 時有意義")
    try:
        await bot.accept_resource_pack()
        passed("accept_resource_pack 呼叫成功（無論伺服器是否有發送 pack）")
    except Exception as exc:
        info(f"accept_resource_pack: {exc}")

    try:
        await bot.deny_resource_pack()
        passed("deny_resource_pack 呼叫成功")
    except Exception as exc:
        info(f"deny_resource_pack: {exc}")

    info("settings 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("settings", test_settings))
