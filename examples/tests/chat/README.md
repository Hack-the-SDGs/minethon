# 聊天測試

測試 bot 的聊天相關 API：公開聊天、私訊、等待訊息。

## 測試清單

| 腳本 | 說明 |
|------|------|
| `test_chat_whisper.py` | `chat()` 公開聊天、`whisper()` 私訊 |
| `test_await_message.py` | `await_message()` 等待並接收聊天訊息 |

## 建議遊戲模式

任何模式皆可。私訊測試需要另一位玩家（或 bot 自己的帳號名稱）。

## 執行

```bash
uv run --env-file examples/tests/.env examples/tests/chat/test_chat_whisper.py
uv run --env-file examples/tests/.env examples/tests/chat/test_await_message.py
```
