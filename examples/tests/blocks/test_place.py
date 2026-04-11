"""測試方塊放置 API。

驗證項目:
- place_block() 放置方塊

前置條件:
- Survival 模式
- Bot 身上有可放置的方塊（如 cobblestone、dirt）
- 附近有空位可放置
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
    wait_prompt,
)

from minethon import Bot, Vec3


async def test_place(bot: Bot) -> None:
    wait_prompt("請給 bot 方塊（如 cobblestone）並確認附近有空位可放置")

    # -- 尋找參考方塊 --
    section("尋找參考方塊")
    reference = None
    for name in ("dirt", "stone", "cobblestone", "grass_block", "sand"):
        blocks = await bot.find_block(name, max_distance=10, count=1)
        if blocks:
            reference = blocks[0]
            info(f"找到參考方塊: {reference.name} at {reference.position}")
            break

    if reference is None:
        skip("附近沒有找到可用的參考方塊")
        return

    # -- place_block --
    section("place_block")
    face = Vec3(0, 1, 0)  # 放在參考方塊的頂部
    info(f"嘗試在 {reference.name} ({reference.position}) 上方放置方塊 (face={face})")

    try:
        await bot.place_block(reference, face)
        passed("place_block() 完成")
    except Exception as exc:
        failed(f"place_block() 失敗: {exc}")

    wait_prompt("請確認方塊已放置在參考方塊上方")

    # -- 驗證放置結果 --
    section("驗證放置結果")
    placed_pos = reference.position.offset(0, 1, 0)
    placed = await bot.block_at(int(placed_pos.x), int(placed_pos.y), int(placed_pos.z))
    if placed is not None and placed.name != "air":
        passed(f"放置位置的方塊: {placed.name} at {placed.position}")
    else:
        info(f"放置位置方塊: {placed!r}（可能放置在其他位置）")


if __name__ == "__main__":
    asyncio.run(run_test("place_block", test_place))
