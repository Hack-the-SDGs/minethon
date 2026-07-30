# 文件盤點（階段一）

日期：2026-07-29 · 範圍：repo 內所有非第三方 `.md`
程式碼只讀不改，作為驗證來源。

## 假設（未先問，直接採用）

1. **`minethon_reference/` 是已死的舊文件樹，不是外部發布用的文件站。**
   依據：repo 內零引用、內容全是已移除的 decorator API、目錄索引指向三個不存在的檔案。
   後果：階段二會建議整棵刪除而非逐行壓縮。若它其實是要發到別處的，請在確認時說。
2. **`bot.pyi` 的中文 hover 是學員 API 的 single source of truth。**
   依據：`AGENTS.md:110`、`AGENTS.md:114-118` 都這樣寫。
   後果：`IDEA.md` / `SKILL.md` / `api-reference.md` 裡逐方法的語意重述，凡與 `.pyi`
   一致者歸「可推導」，但**不會**直接刪掉整份表——`SKILL.md` 的表是給 AI 讀的，
   不能要求 AI 去 parse `.pyi`。
3. **`.pytest_cache/README.md` 屬自動生成，不列入、不動。**

---

## 1. 檔案清單

「字數」＝字元數（含空白，CJK 逐字計）。

| # | 路徑 | 行 | 字元 | 宣稱用途 | 實際目標讀者 | 狀態 |
|---|------|----|----|---------|------------|------|
| 1 | `AGENTS.md` | 283 | 15,929 | 專案 ground truth、設計決策 | AI agent + 維護者 | 現行、密度高 |
| 2 | `CLAUDE.md` | 4 | 71 | 指向 AGENTS.md | Claude Code | 現行、已最小 |
| 3 | `README.md` | 227 | 6,473 | 專案門面、安裝、快速開始 | GitHub 訪客 + 新貢獻者 | **部分過時** |
| 4 | `IDEA.md` | 70 | 3,057 | 學員 API 原始設計草稿 | 維護者（歷史） | **已實作完，落後 3 個方法** |
| 5 | `skills/minethon/SKILL.md` | 151 | 7,794 | AI 寫學員程式的入口 | AI agent | 現行、**有 1 條錯誤規則** |
| 6 | `skills/minethon/api-reference.md` | 338 | 14,800 | 逐方法完整語意 | AI agent | 現行、**缺 1 個公開方法** |
| 7 | `minethon_reference/index.md` | 88 | 2,299 | 「快速入門」 | 不明（無人引用） | **幽靈：API 已移除** |
| 8 | `minethon_reference/events.md` | 220 | 8,615 | 事件系統 + BotEvent 表 | 同上 | **幽靈：API 已移除** |
| 9 | `minethon_reference/bot_methods.md` | 420 | 8,979 | Bot 屬性/方法表 | 同上 | **幽靈：API 已移除** |
| 10 | `docs/architecture/plugin-expansion-plan.md` | 26 | 693 | 「這份文件已作廢」的墓碑 | 維護者 | **墓碑本身也過時了** |
| 11 | `examples/demos/drasl_auth/README.md` | 32 | 1,001 | demo 說明 | 學員/貢獻者 | 現行、準確 |
| 12 | `examples/quests/q10_labfire/state_1/README.md` | 9 | 138 | 關卡解法說明 | 學員 | 現行 |
| 13 | `examples/quests/q10_labfire/state_2/README.md` | 9 | 167 | 同上 | 學員 | 現行 |
| 14 | `examples/quests/q10_labfire/state_3/README.md` | 9 | 181 | 同上 | 學員 | 現行 |

合計 **14 檔 / 1,886 行 / 70,197 字元**。
其中 `minethon_reference/` 三檔佔 **728 行（39%）/ 19,893 字元（28%）**，且**全部描述已刪除的 API**。

---

## 2. 跨檔重複（臃腫主因）

十個主題各自被寫了 3–5 次。下表「來源」欄是我認為該留的唯一副本。

| 主題 | 出現位置 | 來源應為 | 重複量估計 |
|------|---------|---------|-----------|
| A. minethon 是什麼 / 特色 | `README:10-24`、`AGENTS:9-20`、`SKILL:8-15`、`ref/index:1-3` | README（門面） | ~4× |
| B. EventAdaptor + bind 用法 | `README:68-132`（**檔內自己重複 2 次**）、`AGENTS:22-48`、`SKILL:113-135`、`api-ref:155-210`、`ref/events` 全檔 | api-reference（給 AI）＋ README 一份短的 | ~6× |
| C. 版本釘選規則 | `README:144-155`、`AGENTS:158-181`、`api-ref:233-247` ＋ `api-ref:274-276`（**檔內重複**）、`ref/bot_methods:382-399` | AGENTS | ~5× |
| D. 檢查指令 | `README:188-205`（**少了 `check_stubs.py`**）、`AGENTS:220-254` | AGENTS | 2×，README 版是劣化副本 |
| E. 學員 API 方法表 | `IDEA.md` 全檔、`SKILL:47-85`、`api-ref:13-151`、`bot.pyi`（生成） | `bot.pyi` ＋ SKILL 快查表 | ~4× |
| F. 前置需求 / 安裝 | `README:26-46`、`AGENTS:158-161`、`api-ref:277-278`、`ref/index:7-17`（**內容是錯的**） | README | ~4× |
| G. callback thread 不可 blocking | `AGENTS:183-188`、`api-ref:180-182` ＋ `api-ref:270`（**檔內重複**）、`ref/events:39` | AGENTS | ~4× |
| H. 公開錯誤類清單 | `AGENTS:190-198`、`api-ref:251-262`、`ref/index:54-58`、`errors.py` | `errors.py` ＋ api-reference | ~4× |
| I. `create_bot` 參數表 | `ref/index:63-78`、`api-ref:214-229`、`SKILL:24-45` | api-reference | ~3× |
| J. dismount 契約 | `AGENTS:97-107`（why-heavy，**必留**）、`ref/bot_methods:151-152`、`SKILL` 表列、`api-ref:76-85` | AGENTS（why）＋ api-ref（what） | ~4× |

**檔案內部**的重複（不必跨檔就能刪）：

- `README.md:72-102` 與 `README.md:108-124` — 兩段幾乎一樣的 `EventAdaptor` 範例，中間只隔一節。
- `README.md:126-132` — 列出三種「已移除」的 decorator 寫法。對新讀者是純噪音；
  對舊使用者有遷移價值，但這個 repo 沒有舊使用者（v0.4.x、教學用）。**標記待確認，不自行刪。**
- `api-reference.md:233-247` 的版本規則與 `:274-276` 的 "Version pinning" gotcha 是同一件事。
- `api-reference.md:180-182` 與 `:270` 的「不要在 handler 裡 block」是同一句話。

---

## 3. 程式碼 ↔ 文件雙向比對

提取來源：`src/minethon/**` 的 `__all__`、`class Commands` 公開方法、`create_bot` 簽名、
`scripts/`、`setup.sh`、`pc_setup/`、`.github/workflows/`。

### 3.1 有程式碼、無文件（缺漏）

按嚴重度排序。

| 嚴重度 | 符號 / 功能 | 位置 | 說明 |
|--------|------------|------|------|
| **極高** | `create_bot("g_swim")` / `create_bot("swim")` 簡寫 | `_bot_runtime.py:647-672`、`_event_login.py` | **這是學員的主要入口**。`examples/quests/` 全部 5 個範例都用它。所有 `.md` 零提及——README、AGENTS、SKILL、api-reference 都只教 `create_bot(host=..., username=...)` |
| **極高** | `~/.htsdg.json` 機器識別檔 | `_event_login.py:31` | 上面那個簡寫的前提。沒有它 `create_bot("swim")` 直接丟 `MinethonError`。零文件 |
| **極高** | `pc_setup/`（`build_setup.py` / `setup.sh` / `setup.ps1`） | `pc_setup/` | 工作人員標記學生 PC 的整套流程、`GROUP_RANGES` 對照表。零文件、README 的專案結構也沒列 |
| **高** | 腳本結束後自動保活（`atexit.register(bot.run_forever)`） | `_bot_runtime.py:715` | 直接**牴觸**現有文件（見 §3.3） |
| **高** | 簡寫路徑會自動 `wait_spawn()` ＋ settle 等待 | `_bot_runtime.py:716-721` | 同上，牴觸 SKILL.md 的 CRITICAL 規則 |
| **中** | `bot.get_player_pos(username)` | `_commands.py`、`bot.pyi:3017` | 已在 `.pyi` 有中文 hover、`examples/quests/q08_drill` 有用，但 `SKILL.md` 快查表與 `api-reference.md` 都漏了。AI 讀 SKILL 不會知道它存在 |
| **中** | `instruction_sleep` / `bypass_instruction_sleep` | `_bot_runtime.py:650-651` | 只有 `AGENTS.md:95` 提到。學員面向文件（README/SKILL/api-ref）零提及 |
| **中** | `examples/quests/q01,q02,q07,q08` | `examples/quests/` | 四個關卡範例無 README（q10 的三個 state 有），README 範例表也沒列 |
| **低** | `minethon.models` 的 66 個型別 shell | `models/__init__.py` | README:139 只舉 6 個，`ref/index:86` 指向不存在的 `models.md` |
| **低** | `.github/workflows/stubs.yml` 的 paths gate 與「不要設成 required check」 | `stubs.yml:12-16` | 理由寫在 workflow 註解裡，`AGENTS.md`「檢查指令」段沒有對應說明 |

### 3.2 有文件、無程式碼（幽靈）

| 嚴重度 | 文件宣稱 | 位置 | 現況 |
|--------|---------|------|------|
| **極高** | `@bot.on_spawn` / `@bot.on(BotEvent.CHAT)` / `@bot.once(...)` | `ref/index:32-40`、`ref/events:1-31` | decorator API 已**全數移除**（`AGENTS.md:44`）。照抄會 `AttributeError` |
| **極高** | `BotHandlers` | `ref/index:53`、`ref/events:43-64`、`ref/bot_methods:402` | 類別已改名 `EventAdaptor`，`minethon.__all__` 無此名 |
| **高** | `uv add minethon` / `pip install minethon` | `ref/index:9-15` | PyPI 上沒有這個套件（`pyproject.toml` 有 `publish.yml` 但版本 0.4.9 私有）；正確流程是 `./setup.sh` |
| **高** | `examples/demos/linear_actions/main.py` | `README:161` | **檔案不存在**。`examples/demos/` 只有 `drasl_auth/` |
| **高** | `src/minethon/_type_shells.py` | `README:174` | **檔案不存在** |
| **高** | `models.md` / `pathfinder.md` / `errors.md` | `ref/index:86-88` | 三個連結全部 404 |
| **中** | `bot.py` ＝「runtime façade：event decorator、plugin loading、版本 guard」 | `README:169` | 現在 `bot.py` 是純 re-export；runtime 在 `_bot_runtime.py`（`AGENTS.md:125-130`）。README 的專案結構樹整段落後 |
| **中** | 「公開事件入口同時支援 `@bot.on_chat`、`@bot.on(BotEvent.CHAT)`」 | `docs/architecture/plugin-expansion-plan.md:18` | 這是一份「宣告自己已作廢」的墓碑，**它列的「目前正式決策摘要」本身也過時了** |
| **中** | `PlayerNotFoundError` — 「Reserved: nothing raises this yet」 | `errors.py:17-19`（docstring，非 .md） | `use_player` 與 `get_player_pos` 都會丟。docstring 落後 |
| **低** | `bot.activateEntity` / `activateEntityAt` 用於 `use_player` | `AGENTS.md:78` 第一句 | 同一條 bullet 的第二段（`:79`）明說「**完全不呼叫**」這兩個方法。前後自相矛盾，第一句是修改前的殘留 |

### 3.3 文件與程式碼**互相矛盾**（比缺漏更危險）

| 文件說 | 程式碼做 | 影響 |
|--------|---------|------|
| 「Linear script ends instantly, events never fire → 用 `bot.run_forever()` 結尾」<br>`SKILL.md:145`、`SKILL.md:110`、`api-ref:159`、`README:101` | `create_bot` 有 `atexit.register(bot.run_forever)`（`_bot_runtime.py:715`），腳本跑完自動保活 | 文件教的仍能運作（冪等），但「Common mistakes」表把一個**已經不會發生**的錯誤列為常見錯誤，AI 會依此加無用的行 |
| 「**Always** `bot.wait_spawn()` before doing anything」`SKILL.md:45`、`SKILL.md:144` | 簡寫路徑（`create_bot("g_swim")`）內部已 `wait_spawn()` ＋ `_SPAWN_SETTLE_SECONDS` | `examples/quests/` 五個範例全都**沒有** `wait_spawn()`。文件的 CRITICAL 規則與官方範例直接打架 |
| `AGENTS.md:78`「依序呼叫 mineflayer `activateEntityAt`、`activateEntity`」 | `_write_use_entity` 自己送 `use_entity` 封包 | 同 bullet 內部自相矛盾（見 §3.2） |
| `README:197`「對應的個別指令」列 5 條 | `AGENTS.md:229-238` 列 6 條（多 `check_stubs.py`） | 照 README 做會漏掉 stub drift gate |

---

## 4. 其他不對勁的事（不在上述範圍）

1. **`minethon_reference/` 這個目錄名字本身有問題。** 它不在 `src/` 下、不在 `docs/` 下、
   沒有任何檔案引用它、內容全錯。從 git log 看最後一次動它是 `63f4257 fix(bot_methods)`，
   在 decorator API 移除之前。這是「刪除時忘了刪」的殘骸，佔全 repo 文件 39% 行數。

2. **`README.md` 有兩個 `EventAdaptor` 章節。**「快速開始 › 事件寫法」和「事件 API」講同一件事，
   中間只隔一個 code block。看起來是兩次不同時間的編輯各加了一節，沒人合併。

3. **`docs/architecture/plugin-expansion-plan.md` 是一份會自我複製的過時來源。**
   它的存在理由是「告訴你別看這份」，但它同時又寫了一段「目前正式決策摘要」——
   而那段摘要已經過時（列了已移除的 decorator API）。墓碑長出了新的錯誤資訊。
   一個只說「這份作廢，看 AGENTS.md」的檔案不需要 26 行。

4. **`IDEA.md` 已經完成任務但沒有標記。** `AGENTS.md:52` 說它是同步 API 的來源、
   `AGENTS.md:278` 打勾說「IDEA.md 全數實作」。但 `IDEA.md` 本身還是現在式的提案語氣
   （「＋補：」「建議新增」「（選）競賽若要打怪再加」），且落後於實作三個方法
   （`dismount`、`use_player`、`get_player_pos`）。讀者無法從檔案本身判斷它是規格還是歷史。

5. **`AGENTS.md` 有一條 bullet 長 1,100 字元。** `AGENTS.md:106`（dismount 取代理由）
   是單一 bullet 塞了兩個編號理由＋三段 source 引用＋一段 threading 陷阱。
   內容全部是「為什麼」，依保留規則**必須保留**，但它可以拆成子項而不損失任何字。
   同段 `:97-107` 整體是全 repo 資訊密度最高的一段，也是最難讀的一段。

6. **中英混用沒有規則。** `AGENTS.md` / `README.md` / `IDEA.md` / `minethon_reference/`
   是中文；`skills/minethon/*` 是英文；`examples/demos/drasl_auth/README.md` 是英文；
   `examples/quests/*/README.md` 是中文。skills 用英文可能是刻意的（給 AI），
   但沒有任何地方寫下這個規則，下一個人會亂猜。**標記待確認。**

7. **`launcher_accounts.json` 存在於工作目錄。** 已被 `.gitignore:984` 擋住、未被 track，
   所以沒有洩漏。但沒有任何文件說明它是什麼、誰產生的、學員會不會有。
   考量 `.gitignore` 特地為它寫了「must never be committed」，這件事值得一行文件。

8. **`examples/demos/drasl_auth/.env` 實際存在於本機。** 同樣被 gitignore 擋住（`:242`），
   未 track。只是提醒：這個 repo 的工作目錄裡有真實憑證檔。

9. **`skills/minethon/SKILL.md` 的 description 是英文長句，但觸發詞裡沒有中文。**
   學員與助教的提問幾乎必然是中文（「機器人怎麼往前走」）。這個 skill 可能根本不會被觸發。
   不確定是否刻意，**標記待確認**。

10. **README「特色」清單有 7 條，其中 3 條在講同一件事**（「單一事件入口」「Class-based
    handler」「同步 callback API」都是 EventAdaptor）。這屬於「填充」但也可能是刻意的
    行銷式重複，**改前會逐條說明**。

---

## 5. 我看不懂用途、不動、要問你的

| # | 位置 | 問題 |
|---|------|------|
| Q1 | `README.md:126-132` | 「歷史寫法已全部移除」清單——是給遷移用的，還是純歷史？v0.4.x 教學專案應該沒有需要遷移的使用者。刪還是留？ |
| Q2 | `IDEA.md:1` | 第一行「預設大家的聊天室不會共用（透過其他插件做到）」——這是伺服器端的事實陳述，不是 API 設計。它為什麼在這份 API 草稿的第一行？是背景還是需求？ |
| Q3 | `IDEA.md:60` | `# def attack(self) -> bool: ... # （選）競賽若要打怪再加` — 註解掉的提案。競賽已經在跑了（`examples/quests/` 有 10 個關卡），這條還算 open 嗎？ |
| Q4 | `IDEA.md:69-70` | `_BotAdvance` 未實作的說明——這是有價值的「為什麼不那樣做」，我傾向留。但它在一份「已完成的草稿」裡，也許該搬進 `AGENTS.md`？ |
| Q5 | `minethon_reference/` | 假設它是死的（見開頭假設 1）。若其實要發布到別處，請說，我改成逐行修正而非刪除 |
| Q6 | 全 repo | 中英文分工規則（§4.6）——要不要寫進 `AGENTS.md` 維護規則？ |

---

## 6. 階段二預估

若確認上述假設，**不刪任何「為什麼」的內容**，預估：

| 動作 | 依據 | 減少 |
|------|------|------|
| 刪 `minethon_reference/`（3 檔） | 過時（描述已移除的 API）＋ 幽靈 | −728 行 / −19,893 字元 |
| `plugin-expansion-plan.md` 縮成 3 行墓碑或刪除 | 過時 | −23 行 |
| README 合併兩個 EventAdaptor 章節、修專案結構樹、修範例表、補 `check_stubs.py` | 重複＋過時 | −40 行，**淨資訊量增加** |
| `api-reference.md` 消除檔內重複（版本規則 ×2、callback thread ×2） | 重複 | −15 行 |
| `IDEA.md` 加一行狀態標頭、補三個方法 | 過時 | +5 行（**增加**） |
| `SKILL.md` 補 `get_player_pos`、補簡寫入口、修 `run_forever`/`wait_spawn` 矛盾 | 過時 | +12 行（**增加**） |
| 新增：簡寫登入 ＋ `pc_setup/` 的文件 | 缺漏 | +30 行（**增加**） |
| `AGENTS.md` — 只拆 `:106` 的巨型 bullet、修 `:78` 的自我矛盾 | 過時（矛盾那半句） | ±0 行 |

**淨效果：約 −760 行 / −20,000 字元（−29%），同時修掉 4 個矛盾、7 個幽靈引用、補 3 塊缺漏文件。**

壓縮量幾乎全部來自「刪一整棵死掉的文件樹」，不是來自逐句瘦身——
逐句瘦身的空間其實很小，因為 `AGENTS.md` 已經是高密度的 why-heavy 文字。

---

以上為階段一，等你確認後執行階段二。
資安 / 正確性 / 設計疑慮另記於 [`findings.md`](findings.md)（只記錄不修復）。
