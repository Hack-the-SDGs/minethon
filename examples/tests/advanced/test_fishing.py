"""測試釣魚。

驗證項目:
- await bot.fish() 拋竿並等待魚上鉤

前置條件:
- 給 bot 一把釣竿（fishing_rod）
- bot 需面向水面
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
    wait_prompt,
)

from minethon import Bot


async def test_fishing(bot: Bot) -> None:
    wait_prompt(
        "請給 bot 一把釣竿（/give <bot> fishing_rod），"
        "讓 bot 面向水面站好，然後按 Enter"
    )

    # -- fish --
    section("fish")
    info("呼叫 bot.fish()，等待魚上鉤（最長 120 秒）...")
    try:
        await bot.fish()
        passed("fish 完成 — 釣到東西了")
    except Exception as exc:
        failed(f"fish 失敗: {exc}")

    wait_prompt("在遊戲中確認 bot 是否釣到物品，然後按 Enter")
    info("fishing 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("fishing", test_fishing))
