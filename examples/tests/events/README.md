# Event Tests

ObserveAPI 事件系統的手動整合測試。

## 遊戲模式

**Any** -- 事件系統在任何遊戲模式下皆可測試。

## 前置條件

- Bot 已連線至伺服器
- 測試聊天事件時，需要有另一個玩家在線上發送訊息
- 測試實體事件時，需要附近有生物生成/消失

## 測試清單

| 腳本 | 測試範圍 |
|------|---------|
| `test_observe.py` | `on()` decorator、`on()` 直接呼叫、`off()` 取消訂閱、`wait_for()` |
| `test_chat_events.py` | ChatEvent、MessageEvent、MessageStrEvent、ActionBarEvent |
| `test_entity_events.py` | EntitySpawnEvent、EntityGoneEvent、PlayerJoinedEvent、PlayerLeftEvent |

## 執行

```bash
uv run --env-file examples/tests/.env examples/tests/events/test_observe.py
uv run --env-file examples/tests/.env examples/tests/events/test_chat_events.py
uv run --env-file examples/tests/.env examples/tests/events/test_entity_events.py
```
