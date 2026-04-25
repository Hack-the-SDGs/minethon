<div align="center">

[![Banner](https://github.com/Hack-the-SDGs/minethon/blob/main/.github/assets/banner.png?raw=true)](https://github.com/Hack-the-SDGs/minethon)
[![License](https://img.shields.io/github/license/Hack-the-SDGs/minethon?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.14%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-22%2B-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org)

</div>

## 總覽

minethon 是**教學導向**的 Python mineflayer SDK。

底層透過 [JSPyBridge](https://github.com/extremeheat/JSPyBridge) 驅動 [mineflayer](https://github.com/PrismarineJS/mineflayer)，但公開 API 收斂成同步 callback、薄門面、完整 stub — 讓學生不需要先學 Node.js、EventEmitter、asyncio，也能一行一行看懂並自己仿寫。

### 特色

- **同步 callback API** — 繼承 `EventAdaptor`、覆寫 `on_<event>`、用 `bot.bind(...)` 一次綁完，沒有 `await` 也沒有 event loop
- **完整型別層** — `bot.pyi` 由 mineflayer 官方 `index.d.ts` 自動生成，IDE hover 顯示中文說明
- **單一事件入口** — 所有事件統一走 `EventAdaptor` 子類別 + `bot.bind(...)`，避免多套 API 並存造成學習負擔
- **Class-based handler** — `EventAdaptor` 內附完整型別簽名，IDE 的「Override methods」可一鍵填入正確參數
- **Pathfinding** — 內建 typed 支援的 `mineflayer-pathfinder`，`bot.pathfinder.goto(...)` 直接可用
- **顯式版本釘選** — 非內建 plugin 必須傳版本字串，避免 JSPyBridge 在 runtime 偷裝 latest

## 前置需求

| 項目             | 需求          |
| ---------------- | ------------- |
| Python           | 3.14+         |
| Node.js          | 22+           |
| Minecraft Server | Java Edition  |

## 安裝

```bash
./setup.sh
```

`setup.sh` 會：

- 跑 `uv sync` 安裝 Python 依賴
- 檢查 Node.js 22+
- 預裝 pinned 的 `mineflayer`、`vec3`、`mineflayer-pathfinder`

> Node.js 必須在 PATH 中可用。`setup.sh` 啟動時會自動檢查。

## 快速開始

```python
from minethon import EventAdaptor, create_bot
from minethon.models import ChatMessage

bot = create_bot(host="localhost", username="pybot")


class Greeter(EventAdaptor):
    def on_spawn(self) -> None:
        bot.chat("hello")

    def on_chat(
        self,
        username: str,
        message: str,
        translate: str | None,
        json_msg: ChatMessage,
        matches: list[str] | None,
    ) -> None:
        if username == bot.username:
            return
        if message == "quit":
            bot.quit("bye")

    def on_end(self, reason: str) -> None:
        print(f"Disconnected: {reason}")


bot.bind(Greeter())
bot.run_forever()
```

## 事件 API

唯一公開寫法：繼承 `EventAdaptor`、覆寫想要的 `on_<event>` 方法、用 `bot.bind(instance)` 綁定。

```python
from minethon import EventAdaptor, create_bot


class My(EventAdaptor):
    def on_spawn(self) -> None:
        print(f"Spawned as {bot.username}")

    def on_chat(self, username, message, *_):
        if message == "quit":
            bot.quit("bye")


bot = create_bot(host="localhost", username="pybot")
bot.bind(My())
bot.run_forever()
```

歷史寫法已**全部移除**，不再是公開 API：

- `@bot.on("chat")`（字串）
- `@bot.on(BotEvent.CHAT)` / `@bot.once(BotEvent.CHAT)`（enum decorator）
- `@bot.on_<event>` / `@bot.once_<event>`（屬性 shortcut）

統一只剩 `EventAdaptor` 一條路，避免初學者在多套 API 之間迷失方向。

## 型別與匯入

常用型別可從 `minethon.models` 匯入：

```python
from minethon.models import Block, ChatMessage, Entity, Item, Player, Vec3
```

這些是公開型別 shell，實際成員面以 [`src/minethon/bot.pyi`](src/minethon/bot.pyi) 為準。

## 版本規則

- `create_bot(...)` 內部固定使用 pinned 的 `mineflayer`
- `bot.load_plugin("mineflayer-pathfinder")` 可省略版本，會用內建 pin
- 其他 npm 套件必須顯式版本：

```python
viewer = bot.require("prismarine-viewer", "1.33.0")
tool = bot.load_plugin("mineflayer-tool", "1.5.0", export_key="plugin")
```

這是刻意設計，用來避免 JSPyBridge 在 runtime 偷裝 latest，確保教學範例在學生環境可重現。

## 範例

| 範例                                                                  | 說明                                  |
| --------------------------------------------------------------------- | ------------------------------------- |
| [drasl_auth](examples/demos/drasl_auth/main.py)                       | 透過自建 Drasl 驗證伺服器連線並回應聊天 |

## 專案結構

```
src/minethon/
├── __init__.py         # 使用者入口（re-export create_bot / Bot / BotEvent / EventAdaptor / 錯誤類）
├── bot.py              # runtime façade：event decorator、plugin loading、版本 guard
├── bot.pyi             # 生成的 IDE 型別層（由 scripts/generate_stubs.py 產出）
├── _events.py          # 生成的 BotEvent StrEnum
├── _handlers.py        # 生成的 EventAdaptor 基底類別
├── _bridge.py          # JSPyBridge 封裝：callback thread、emitter 注入、handler 正規化
├── _type_shells.py     # 內部型別 shell 實作
├── errors.py           # 公開錯誤類（MinethonError、NotSpawnedError、VersionPinRequiredError 等）
├── py.typed            # PEP 561 型別支援標記
└── models/             # 可匯入的公開型別 shell
    ├── __init__.py
    └── __init__.pyi

scripts/
├── generate_stubs.py   # 從 mineflayer / pathfinder d.ts 生成 bot.pyi / _events.py / _handlers.py
└── format.sh           # 一鍵 regen → ruff → pyright → pytest
```

> hover 說明的中文 docstring 直接住在 `src/minethon/bot.pyi` 內；`generate_stubs.py` regen 時會從現有 `.pyi` 讀回 docstring 再注入新生成的 stub，所以人工編輯不會被沖掉。

## 開發

一鍵跑完（regen stubs → format → lint → type-check → test）：

```bash
./scripts/format.sh            # 寫回格式修正
./scripts/format.sh --check    # 只檢查不寫入（CI 模式）
```

對應的個別指令：

```bash
uv run python scripts/generate_stubs.py
uv run ruff format src scripts tests
uv run ruff check src scripts tests
uv run pyright src/
uv run pytest -m "not integration" --tb=short -q
```

### IntelliJ / PyCharm 使用者注意

`uv sync` 會以 editable 模式安裝本專案，導致 IDEA 的 Python SDK 將專案目錄同時視為外部 library，可能使整個專案被標記為 excluded。

**解法：** File → Project Structure → SDKs → 選擇 Python interpreter → Paths 頁籤，移除指向本專案以及本專案 `src/` 的路徑，然後 Apply。

## 貢獻

歡迎 PR 與 Issue！

送出前請確認：

1. 遵循現有的程式碼風格與架構慣例（細節見 [`AGENTS.md`](AGENTS.md)）
2. 通過所有檢查
   - `./scripts/format.sh --check`
3. 以 `feature/your-feature` 或 `fix/your-fix` 命名分支
4. 發布 PR 時，目標分支為 `dev`

## 授權

本專案採用 [GNU Affero General Public License v3.0](LICENSE) 授權。
