# minethon 快速入門

minethon 是教學導向的 Python Minecraft 機器人 SDK，封裝 [mineflayer](https://github.com/PrismarineJS/mineflayer) JS 引擎。你不需要懂 Node.js 或 asyncio，只要寫 Python 同步 callback 就好。

---

## 安裝

```bash
# 使用 uv（推薦）
uv add minethon

# 或 pip
pip install minethon
```

Node.js 22+ 必須已安裝。

---

## 最小範例

```python
from minethon import create_bot, BotEvent

bot = create_bot(
    host="localhost",
    port=25565,
    username="my_bot",
)

@bot.on_spawn
def on_spawn():
    bot.chat("Hello from minethon!")

@bot.on(BotEvent.CHAT)
def on_chat(username, message, *_):
    if message == "quit":
        bot.quit("bye")

bot.run_forever()
```

---

## 公開 API 一覽

| 名稱 | import 路徑 | 說明 |
|------|------------|------|
| `create_bot` | `from minethon import create_bot` | 建立並連線機器人 |
| `Bot` | `from minethon import Bot` | 機器人主類別 |
| `BotEvent` | `from minethon import BotEvent` | 所有事件名稱的 StrEnum |
| `BotHandlers` | `from minethon import BotHandlers` | class-based 事件處理基類 |
| `MinethonError` | `from minethon import MinethonError` | 錯誤基類 |
| `NotSpawnedError` | `from minethon import NotSpawnedError` | 尚未 spawn 就呼叫 API |
| `PlayerNotFoundError` | `from minethon import PlayerNotFoundError` | 找不到玩家 |
| `PluginNotInstalledError` | `from minethon import PluginNotInstalledError` | 插件未載入 |
| `VersionPinRequiredError` | `from minethon import VersionPinRequiredError` | npm 套件需要版本號 |
| 型別 (Vec3, Entity, …) | `from minethon.models import Vec3` | 可用於 annotation 的型別 |

---

## `create_bot()` 常用參數

```python
bot = create_bot(
    host="mc.example.com",      # 伺服器位址
    port=25565,                  # 埠號（預設 25565）
    username="bot_name",         # 使用者名稱
    password="secret",           # 密碼（Mojang / Drasl auth 用）
    auth="mojang",               # 驗證方式："mojang" | "microsoft" | "offline"
    auth_server="https://...",   # 自定義 auth server URL（Drasl）
    session_server="https://...",# 自定義 session server URL（Drasl）
    version="1.20.1",            # 指定 Minecraft 版本（建議明確指定）
)
```

snake_case 參數會自動轉為 camelCase 傳給 mineflayer（`auth_server` → `authServer`）。

---

## 其他參考文件

- [events.md](events.md) — 事件系統、BotEvent 完整列表
- [bot_methods.md](bot_methods.md) — Bot 所有屬性與方法
- [models.md](models.md) — 型別參考（Vec3、Entity、Block、Item…）
- [pathfinder.md](pathfinder.md) — Pathfinder 插件與尋路 Goal
- [errors.md](errors.md) — 錯誤類別與處理方式
