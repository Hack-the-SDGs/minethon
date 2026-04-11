"""測試實體搜尋與查詢 API。

驗證項目:
- get_entities() 取得所有追蹤中的實體
- get_entity() 取得 bot 自身實體
- find_entity(kind="player") 搜尋玩家
- find_entity(max_distance=30) 搜尋最近實體
- entity_at_cursor() 取得注視實體
- Entity 所有欄位: id, name, kind, position, velocity, health, metadata
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

from minethon import Bot, Entity, EntityKind, Vec3


def print_entity(label: str, entity: Entity) -> None:
    """Print all fields of an Entity."""
    info(f"{label}:")
    info(f"  id        = {entity.id}")
    info(f"  name      = {entity.name!r}")
    info(f"  kind      = {entity.kind}")
    info(f"  position  = {entity.position}")
    info(f"  velocity  = {entity.velocity}")
    info(f"  health    = {entity.health}")
    info(f"  metadata  = {entity.metadata!r}")


async def test_find_entity(bot: Bot) -> None:
    # -- get_entity (bot 自身) --
    section("get_entity (bot 自身)")
    self_entity = await bot.get_entity()
    check_not_none("get_entity() 結果", self_entity)
    check_type("get_entity type", self_entity, Entity)
    print_entity("Bot 自身", self_entity)

    # -- Entity 欄位型別驗證 --
    section("Entity 欄位型別驗證")
    check_type("id", self_entity.id, int)
    check_type("kind", self_entity.kind, EntityKind)
    check_type("position", self_entity.position, Vec3)
    if self_entity.name is not None:
        check_type("name", self_entity.name, str)
    if self_entity.velocity is not None:
        check_type("velocity", self_entity.velocity, Vec3)

    # -- get_entities --
    section("get_entities")
    entities = await bot.get_entities()
    check_type("get_entities type", entities, dict)
    info(f"追蹤中的實體數量: {len(entities)}")

    shown = 0
    for eid, ent in entities.items():
        if shown >= 5:
            info(f"  ... 以及 {len(entities) - shown} 個其他實體")
            break
        info(f"  [{eid}] {ent.name} ({ent.kind.value}) at {ent.position}")
        shown += 1

    # -- find_entity (玩家) --
    section("find_entity (搜尋玩家)")
    player = await bot.find_entity(kind=EntityKind.PLAYER, max_distance=64)
    if player is not None:
        check_type("find_entity player type", player, Entity)
        print_entity("找到的玩家", player)
    else:
        skip("附近沒有其他玩家")

    # -- find_entity (最近實體) --
    section("find_entity (最近實體)")
    nearest = await bot.find_entity(max_distance=30)
    if nearest is not None:
        check_type("find_entity nearest type", nearest, Entity)
        print_entity("最近的實體", nearest)
        dist = self_entity.position.distance_to(nearest.position)
        info(f"距離 bot: {dist:.1f} blocks")
        check_true("距離 <= 30", dist <= 35)  # 容許些許誤差
    else:
        skip("30 格內沒有實體")

    # -- find_entity (動物) --
    section("find_entity (搜尋動物)")
    animal = await bot.find_entity(kind=EntityKind.ANIMAL, max_distance=32)
    if animal is not None:
        print_entity("找到的動物", animal)
    else:
        skip("附近沒有動物")

    # -- find_entity (敵對生物) --
    section("find_entity (搜尋敵對生物)")
    hostile = await bot.find_entity(kind=EntityKind.HOSTILE, max_distance=32)
    if hostile is not None:
        print_entity("找到的敵對生物", hostile)
    else:
        skip("附近沒有敵對生物")

    # -- entity_at_cursor --
    section("entity_at_cursor")
    wait_prompt("請讓 bot 面朝一個實體（生物或玩家），然後按 Enter")
    cursor_entity = await bot.entity_at_cursor(max_distance=5)
    if cursor_entity is not None:
        check_not_none("entity_at_cursor 結果", cursor_entity)
        check_type("entity_at_cursor type", cursor_entity, Entity)
        print_entity("注視實體", cursor_entity)
    else:
        skip("entity_at_cursor 回傳 None（沒有實體在視線範圍內）")


if __name__ == "__main__":
    asyncio.run(run_test("find_entity", test_find_entity))
