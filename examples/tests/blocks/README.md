# Block Tests

方塊搜尋、挖掘、放置、啟動的手動整合測試。

## 遊戲模式

**Survival** -- 挖掘和放置需要在生存模式下才能正確觸發。

## 前置條件

- Bot 已連線至伺服器
- 附近有可挖掘的方塊（dirt、stone 等）
- 若測試放置，需要先給 bot 方塊物品
- 若測試啟動，需要附近有可互動方塊（門、拉桿、按鈕）

## 測試清單

| 腳本 | 測試範圍 |
|------|---------|
| `test_find_block.py` | `find_block()`、`block_at()`、`block_at_cursor()`、`can_see_block()`、Block 欄位 |
| `test_dig.py` | `can_dig_block()`、`dig_time()`、`dig()`、`stop_digging()` |
| `test_place.py` | `place_block()` |
| `test_activate_block.py` | `activate_block()` |

## 執行

```bash
uv run --env-file examples/tests/.env examples/tests/blocks/test_find_block.py
uv run --env-file examples/tests/.env examples/tests/blocks/test_dig.py
uv run --env-file examples/tests/.env examples/tests/blocks/test_place.py
uv run --env-file examples/tests/.env examples/tests/blocks/test_activate_block.py
```
