"""測試鞘翅飛行。

驗證項目:
- await bot.elytra_fly() 啟動鞘翅飛行
- await bot.get_firework_rocket_duration() 取得煙火助推剩餘 ticks

前置條件:
- bot 需裝備鞘翅（elytra）
- 建議站在高處以測試滑翔

注意:
- 鞘翅飛行需要在空中才能啟動
- 此測試較為情境性，主要驗證 API 呼叫本身是否正常
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

from minethon import Bot


async def test_elytra(bot: Bot) -> None:
    # -- get_firework_rocket_duration (未飛行) --
    section("get_firework_rocket_duration (地面)")
    try:
        duration = await bot.get_firework_rocket_duration()
        check_type("firework_rocket_duration", duration, int)
        info(f"firework_rocket_duration = {duration} (預期 0，未飛行)")
        passed("get_firework_rocket_duration 成功")
    except Exception as exc:
        failed(f"get_firework_rocket_duration 失敗: {exc}")

    # -- elytra_fly --
    section("elytra_fly")
    wait_prompt(
        "請給 bot 裝備鞘翅（elytra），站在高處，"
        "讓 bot 跳起來後按 Enter（需要在空中啟動）"
    )

    try:
        await bot.elytra_fly()
        passed("elytra_fly 成功 — 鞘翅已啟動")
    except Exception as exc:
        info(f"elytra_fly 失敗（可能不在空中）: {exc}")

    wait_prompt("觀察 bot 是否在滑翔，確認後按 Enter")
    info("elytra 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("elytra", test_elytra))
