"""測試村民交易。

驗證項目:
- await bot.open_villager(villager) → VillagerSession (id, title, trades)
- await bot.trade(session, trade_index, times=1) → VillagerSession
- await bot.close_window(session)

前置條件:
- 附近需有村民（建議先治療殭屍村民或用 /summon）
- 交易需要對應物品
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_not_none,
    check_type,
    failed,
    info,
    passed,
    run_test,
    section,
    skip,
    wait_prompt,
)

from minethon import Bot
from minethon.models.entity import EntityKind
from minethon.models.window import VillagerSession


async def test_villager(bot: Bot) -> None:
    wait_prompt("請確保附近有一個村民（villager），然後按 Enter")

    # -- 尋找村民 --
    section("尋找村民")
    villager = await bot.find_entity(name="villager", max_distance=8)
    if villager is None:
        villager = await bot.find_entity(kind=EntityKind.MOB, max_distance=8)
        if villager is not None:
            info(f"找到 mob: {villager.name}（非 villager，嘗試使用）")
    if villager is None:
        failed("附近找不到村民")
        return

    info(f"找到: {villager.name} (id={villager.id})")

    # -- open_villager --
    section("open_villager")
    try:
        session = await bot.open_villager(villager)
        check_type("VillagerSession", session, VillagerSession)
        check_not_none("session.id", session.id)
        info(f"session.id = {session.id}")
        info(f"session.title = {session.title!r}")
        info(f"交易數量: {len(session.trades)}")
        for i, trade in enumerate(session.trades):
            info(
                f"  交易 [{i}]: "
                f"{trade.first_input.name} x{trade.first_input.count}"
                f"{(' + ' + trade.secondary_input.name + ' x' + str(trade.secondary_input.count)) if trade.secondary_input else ''}"
                f" → {trade.output.name} x{trade.output.count}"
                f" (uses={trade.uses}/{trade.max_uses}, disabled={trade.disabled})"
            )
        passed("open_villager 成功")
    except Exception as exc:
        failed(f"open_villager 失敗: {exc}")
        return

    # -- trade --
    section("trade")
    if not session.trades:
        skip("村民沒有交易選項")
    else:
        tradable = [
            i
            for i, t in enumerate(session.trades)
            if not t.disabled and t.uses < t.max_uses
        ]
        if not tradable:
            skip("所有交易均已禁用或用完")
        else:
            trade_idx = tradable[0]
            info(f"嘗試執行交易 [{trade_idx}]")
            try:
                updated = await bot.trade(session, trade_idx, times=1)
                check_type("更新後的 VillagerSession", updated, VillagerSession)
                info(f"交易後交易數量: {len(updated.trades)}")
                passed("trade 成功")
                session = updated
            except Exception as exc:
                info(f"trade 失敗（可能缺少交易物品）: {exc}")

    # -- close_window --
    section("close_window")
    try:
        await bot.close_window(session)
        passed("close_window 成功")
    except Exception as exc:
        failed(f"close_window 失敗: {exc}")

    info("villager 測試完成")


if __name__ == "__main__":
    asyncio.run(run_test("villager", test_villager))
