"""測試方塊搜尋與查詢 API。

驗證項目:
- find_block() 搜尋附近方塊
- block_at() 取得指定座標方塊
- block_at_cursor() 取得注視方塊
- can_see_block() 視線檢查
- Block 所有欄位: name, display_name, position, hardness, is_solid, is_liquid, bounding_box
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_not_none,
    check_true,
    check_type,
    info,
    run_test,
    section,
    skip,
    wait_prompt,
)

from minethon import Block, Bot, Vec3


def print_block(label: str, block: Block) -> None:
    """Print all fields of a Block."""
    info(f"{label}:")
    info(f"  name          = {block.name!r}")
    info(f"  display_name  = {block.display_name!r}")
    info(f"  position      = {block.position}")
    info(f"  hardness      = {block.hardness}")
    info(f"  is_solid      = {block.is_solid}")
    info(f"  is_liquid     = {block.is_liquid}")
    info(f"  bounding_box  = {block.bounding_box!r}")


async def test_find_block(bot: Bot) -> None:
    # -- find_block --
    section("find_block")

    for block_name in ("stone", "dirt", "grass_block", "cobblestone"):
        blocks = await bot.find_block(block_name, max_distance=64, count=1)
        if blocks:
            info(f"find_block({block_name!r}) found {len(blocks)} result(s)")
            block = blocks[0]
            check_type("result type", block, Block)
            print_block("found block", block)

            # -- Block field types --
            section("Block 欄位型別驗證")
            check_type("name", block.name, str)
            check_type("display_name", block.display_name, str)
            check_type("position", block.position, Vec3)
            check_type("is_solid", block.is_solid, bool)
            check_type("is_liquid", block.is_liquid, bool)
            check_type("bounding_box", block.bounding_box, str)
            break
    else:
        skip("附近沒有找到 stone/dirt/grass_block/cobblestone")
        return

    # -- block_at (腳下方塊) --
    section("block_at (腳下方塊)")
    pos = bot.position
    under_block = await bot.block_at(int(pos.x), int(pos.y) - 1, int(pos.z))
    if under_block is not None:
        check_not_none("block_at 結果", under_block)
        check_type("block_at type", under_block, Block)
        print_block("腳下方塊", under_block)
        check_true("腳下方塊 is_solid", under_block.is_solid)
    else:
        skip("block_at 回傳 None（chunk 可能未載入）")

    # -- find_block 多結果 --
    section("find_block 多結果")
    multi = await bot.find_block(block.name, max_distance=32, count=5)
    info(f"find_block({block.name!r}, count=5) 找到 {len(multi)} 個方塊")
    for i, b in enumerate(multi[:3]):
        info(f"  [{i}] {b.name} at {b.position}")

    # -- can_see_block --
    section("can_see_block")
    if blocks:
        visible = await bot.can_see_block(blocks[0])
        check_type("can_see_block 型別", visible, bool)
        info(f"can_see_block({blocks[0].name} at {blocks[0].position}) = {visible}")

    # -- block_at_cursor --
    section("block_at_cursor")
    wait_prompt("請讓 bot 面朝一個方塊，然後按 Enter")
    cursor_block = await bot.block_at_cursor(max_distance=10)
    if cursor_block is not None:
        check_not_none("block_at_cursor 結果", cursor_block)
        check_type("block_at_cursor type", cursor_block, Block)
        print_block("注視方塊", cursor_block)
    else:
        skip("block_at_cursor 回傳 None（沒有方塊在視線範圍內）")


if __name__ == "__main__":
    asyncio.run(run_test("find_block", test_find_block))
