# Entity Tests

實體搜尋、攻擊、互動的手動整合測試。

## 遊戲模式

**Survival** -- 攻擊和互動需要在生存模式下才能正確觸發。

## 前置條件

- Bot 已連線至伺服器
- 附近有生物（被動生物、敵對生物、或其他玩家）
- 若測試攻擊，需要附近有可攻擊的生物
- 若測試互動，需要附近有可互動實體（如村民）

## 測試清單

| 腳本 | 測試範圍 |
|------|---------|
| `test_find_entity.py` | `get_entities()`、`get_entity()`、`find_entity()`、`entity_at_cursor()`、Entity 欄位 |
| `test_attack.py` | `attack()` |
| `test_interact_entity.py` | `activate_entity()`、`use_on()` |

## 執行

```bash
uv run --env-file examples/tests/.env examples/tests/entities/test_find_entity.py
uv run --env-file examples/tests/.env examples/tests/entities/test_attack.py
uv run --env-file examples/tests/.env examples/tests/entities/test_interact_entity.py
```
