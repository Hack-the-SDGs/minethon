# Findings — 資安 / 正確性 / 設計疑慮

**只記錄，不修復。** 發現當下 append。
產生於階段一文件盤點過程（2026-07-29），來源是為了驗證文件而讀的程式碼。

嚴重度：CRITICAL（阻擋）/ HIGH（應修）/ MEDIUM（考慮）/ LOW（備註）

---

## 使用者情境（2026-07-29 由專案擁有者提供，用來重新評級）

**這段是後續所有嚴重度的判斷依據，不要在沒有新資訊時重新爭論。**

- 學員：國高中生，**一半是第一次接觸程式語言**，一半有少量基礎。
- 營期：5 天，**隊輔全程在場**。
- 課程涵蓋：`print`、變數、型別、四則運算、縮排、
  **錯誤處理（只到「看懂錯誤行數、錯誤原因」）**、轉型、條件判斷、迴圈、陣列、
  物件的方法與屬性呼叫。
- 課程**不涵蓋**：`try`/`except`、`sys.exit`、context manager、執行緒。

推論（影響評級）：

1. **惡意行為不在威脅模型內** → F-01 / F-02 降為「已接受的風險」。
2. **學員必然會寫出錯誤程式，而且「讀錯誤訊息」是課程的一部分** →
   任何讓錯誤訊息變難讀、或讓程式在錯誤後行為不明的路徑，**升為 HIGH**。
   這是這個專案真正的失敗模式。
3. 學員不會寫 `try/finally` → F-07 關閉。

---

## F-01 — 帳號密碼可由公開程式碼完整枚舉 · ~~HIGH~~ → **已接受的風險** · 資安

> **2026-07-29 結案（專案擁有者判斷）**：學員為國高中初學者、營期 5 天、隊輔在場，
> 不具備也沒有時間執行這個攻擊。**不修，不需再評估。**
> 以下技術描述保留，理由是：(a) 若日後改成長期開放或線上賽，威脅模型會變；
> (b) 賽後帳號輪換時需要知道推導規則。
> 唯一仍建議的動作：賽後若要把 `minethon` 發到 PyPI（`publish.yml` 會在 tag 時觸發），
> 先把 `_event_login.py` 的 `_SALT` 與 `_DEFAULTS` 抽掉——那不是安全問題，
> 是「賽事設定不該混進通用 SDK」的整潔問題。


**位置**：`src/minethon/_event_login.py:28,65-79` ＋ `pc_setup/build_setup.py:GROUP_RANGES`

密碼是純確定性推導，salt 寫死在**會被 import 的程式碼**裡：

```
group   password = sha256("Hack-The-SDGs-Python@" + <group>)
personal password = sha256("Hack-The-SDGs-Python@" + <group> + ":" + <computer>)
```

`pc_setup/build_setup.py` 的 `GROUP_RANGES` 同時公開了完整參數空間：
**group 只有 1–6，computer 只有 1–67**。

使用者名稱同樣是可推導的（`G<group>_<task>` / `U<computer>_<task>`），
而 `<task>` 直接寫在 `examples/quests/` 的目錄名裡（`swim`、`toilet`、`stack`、
`drill`、`labfire`）。

**結果**：任何拿到 SDK 的人可以在數秒內離線算出全部 6 組 × N 關卡的帳密，
以及 67 台個人機的帳密。不需要暴力破解——是查表。

**放大條件**：

1. repo 是 public（`README.md` badge 指向 `github.com/Hack-the-SDGs/minethon`）。
2. `.github/workflows/publish.yml` 在 tag 時**發布到 PyPI**。也就是 salt、
   `mc.ntust.camp:50213`、drasl auth/session URL 會隨套件公開發行。

**已知的緩解主張**（`_event_login.py:14-16` 的 docstring）：

> the salt below lives in importable code, so these passwords are NOT secret …
> This is casual deterrence only — real account protection is server-side
> (event-scoped accounts, rate limits, rotation).

這個決策**已被明確記錄且看起來是刻意的**，所以不列 CRITICAL。但兩點要指出：

- docstring 說「casual deterrence」，實際上是**零 deterrence**：參數空間 6 和 67，
  不是「難猜」而是「可列印」。措辭低估了風險程度。
- 「real account protection is server-side」是**對伺服器的假設，repo 內無法驗證**。
  若伺服器端沒有真的做 event-scoped + rate limit，這條防線不存在。
  依 `AGENTS.md`「Source-Verified 原則」，這種未驗證假設不該被當成既定契約。

**實際影響**：學員可以用別組的帳號登入並破壞對方的關卡進度。
競賽公平性問題，不是資料外洩問題。

---

## F-02 — 賽事基礎設施座標隨套件發布 · LOW · 資安

**位置**：`src/minethon/_event_login.py:34-41`

```python
"host": "mc.ntust.camp", "port": 50213,
"auth_server": "https://drasl.ntust.camp/auth",
"session_server": "https://drasl.ntust.camp/session",
```

註解寫「public infrastructure, safe to ship in the SDK」——同意，單獨看沒問題。

但**與 F-01 合起來**，這個套件就是一套 turnkey：位址、驗證端點、帳號推導、
密碼推導全在一個 import 裡。任何人 `pip install minethon` 就能對賽事伺服器
發起已驗證的連線。至少值得在賽後把 `_DEFAULTS` 抽成環境變數或另一個未發布的套件。

---

## F-03 — 文件教的規則已被程式碼作廢，而文件把它列為「常見錯誤」 · MEDIUM · 正確性

**位置**：`_bot_runtime.py:715-721` vs `skills/minethon/SKILL.md:45,110,144-145`、
`skills/minethon/api-reference.md:159`、`README.md:101`

`create_bot` 現在做了兩件文件不知道的事：

```python
atexit.register(bot.run_forever)      # :715 — 腳本跑完自動保活
if account is not None:
    bot.wait_spawn()                  # :717 — 簡寫路徑自動等 spawn
    time.sleep(_SPAWN_SETTLE_SECONDS) # :721 — 再等 3.5 秒
```

而文件仍然說：

- `SKILL.md:145`「Linear script ends instantly, events never fire」→ 列在
  **Common mistakes 表**裡。這個錯誤現在**不會發生**。
- `SKILL.md:45`「**Always** `bot.wait_spawn()` before doing anything」→
  但 repo 自己的 5 個關卡範例（`examples/quests/`）**全都沒有** `wait_spawn()`，
  因為簡寫路徑已經內建。

**影響**：AI 依 SKILL.md 生成的程式碼會多出無用的行，且會與官方範例的寫法不一致。
兩邊都能跑，所以是文件正確性問題不是 bug——但 `SKILL.md` 的存在意義就是讓 AI 寫對，
規則本身過時會直接侵蝕它的價值。

---

## F-04 — `AGENTS.md` 同一條 bullet 內部自相矛盾 · MEDIUM · 正確性

**位置**：`AGENTS.md:78` vs `AGENTS.md:79-89`

第一句：

> 以碰撞箱中心為絕對點**依序呼叫 mineflayer `activateEntityAt`、`activateEntity`**

第二段（同一條 bullet）：

> **完全不呼叫 mineflayer 的 `activateEntity` / `activateEntityAt`**，而是 …
> `bot._client.write('use_entity', ...)`

程式碼（`_commands.py:_write_use_entity`）證實是後者。第一句是修改前的殘留。

`AGENTS.md` 自我宣告是 ground truth 且被 `CLAUDE.md` 直接 `@` 進每個 session，
所以 AI 每次都會同時讀到正確與錯誤的版本。這是所有矛盾裡影響面最大的一條。

---

## F-05 — `PlayerNotFoundError` docstring 說「還沒有人丟」，實際已有兩處 · LOW · 正確性

**位置**：`src/minethon/errors.py:17-19`

> Reserved: no current student command looks up players by name, so nothing
> raises this yet

實際上 `_commands.py` 的 `use_player()` 與 `get_player_pos()` 都會丟。
docstring 沒跟上。

---

## F-06 — 學員腳本拋例外後程式會掛住 · ~~MEDIUM~~ → **HIGH** · 設計

> **2026-07-29 升級**：課程明列「錯誤處理（看懂錯誤行數、錯誤原因）」是教學內容，
> 且一半學員是第一次寫程式 → **程式出錯是預期中的、每天都會發生的路徑**，
> 不是邊緣案例。而學員沒學過 Ctrl-C 的意義，看到「印完錯誤但游標不動」
> 只會判斷成「電腦當了」。與 F-11 疊加後是本次審查影響最大的一條。


**位置**：`_bot_runtime.py:715`（`atexit.register(bot.run_forever)`）
＋ `:280-299`（`_hook` excepthook）

流程：學員腳本拋出**自己的** bug（`TypeError`、`IndexError`…）
→ excepthook 走到 `previous(exc_type, exc, tb)` 印出正常 traceback
→ Python 開始跑 atexit
→ `bot.run_forever()` 阻塞，直到伺服器斷線或 Ctrl-C。

也就是：**學員看到一段 traceback，然後程式看起來當掉了。**

excepthook 對 KeyboardInterrupt、per-call timeout、bridge failure 三種情況都有
處理（會 `os._exit`，跳過 atexit），唯獨「學員自己寫錯」這個**最常發生**的情況
會落到保活分支。

不確定是否刻意（「腳本壞了但機器人還在線」對事件驅動腳本是合理的）。
但對直線腳本的學員，體驗是「當掉」。**這條需要你確認意圖，我沒有改。**

---

## F-07 — `os._exit(1)` 繞過所有 cleanup · ~~LOW~~ → **關閉（不適用）** · 設計

> **2026-07-29 結案**：課程不教 `try`/`finally`、context manager，
> 學員程式裡不會有需要被 cleanup 的東西。原本的顧慮不成立。**不需任何動作。**


**位置**：`_bot_runtime.py:76-96`（`_stop_with_message`）

docstring 已經寫清楚理由與代價：

> os._exit skips atexit and buffered writers by design — flush both streams first

主執行緒可能卡在 `wait_spawn`、`run_forever` 或死掉的 bridge call 裡，async
interrupt 打不斷——這個推理成立，程式碼也先 flush 了。

**記錄而非質疑**：代價是學員的 `try/finally`、context manager `__exit__`
都不會執行。教學情境下幾乎不會有人寫，但這是 SDK 對使用者程式的單方面約束，
且**沒有寫在任何面向學員的文件裡**。

---

## F-08 — README 指向不存在的檔案 · LOW · 正確性

**位置**：`README.md:161`（`examples/demos/linear_actions/main.py`）、
`README.md:174`（`src/minethon/_type_shells.py`）

兩個檔案都不存在。`README.md:169` 對 `bot.py` 的描述（「runtime façade：
event decorator、plugin loading、版本 guard」）也與現況不符——decorator 已移除，
runtime 已搬到 `_bot_runtime.py`。

已列入 `inventory.md` §3.2，在此重複記錄是因為它會直接絆倒新貢獻者。

---

## F-09 — `minethon_reference/` 會主動產生錯誤的程式碼 · MEDIUM · 正確性

**位置**：`minethon_reference/{index,events,bot_methods}.md`（728 行）

不只是「過時的雜物」。這三份文件**教的是會直接 `AttributeError` 的 API**：

- `@bot.on_spawn` / `@bot.on(BotEvent.CHAT)` / `@bot.once(...)` — decorator 全數已移除
- `BotHandlers` — 已改名 `EventAdaptor`，`minethon.__all__` 無此名
- `uv add minethon` / `pip install minethon` — 正確流程是 `./setup.sh`

repo 內零引用，但**它們在 repo 裡**：任何 AI agent（包含 Claude Code 自己）
做全文檢索時都會命中，且行數比正確的 `skills/minethon/` 還多。
主動的錯誤資訊來源，不是被動的死碼。

---

## F-10 — `_read_identity` 的錯誤路徑吞掉 `MinethonError` 之外的資訊 · LOW · 設計

**位置**：`src/minethon/_event_login.py:56-58`

```python
except (ValueError, KeyError, OSError) as exc:
    msg = f"本機識別檔 {IDENTITY_FILE} 內容無效，請重跑 setup.sh / setup.ps1。"
    raise MinethonError(msg) from exc
```

`from exc` 有保留 chain，訊息也符合「優先告訴下一步該做什麼」的規則——這條沒問題。

記錄的是相鄰的一件事：`resolve_account(shorthand)` 對 `shorthand` **完全不做驗證**。
空字串會產出 `U<n>_`；含空白或 `-` 的字串會直接變成使用者名稱送去登入
（`_event_login.py:7` 註解說「server forbids "-"」，但只在 `g-` 前綴那條路轉換）。
失敗時學員看到的是 F-03 那條「找不到此任務」的登入錯誤訊息，
而非「你的任務名稱格式不對」。`action()` 有做名稱字元驗證（丟 `ValueError`），
這裡沒有，兩者不一致。

---

## F-11 — 打錯方法名字 → `'NoneType' object is not callable` · HIGH · 設計

**2026-07-29 新增。** 由「課程包含錯誤訊息閱讀、學員為初學者」的情境反推而發現。

**位置**：`_bot_runtime.py:440-463`（`Bot.__getattr__`），關鍵證據在 `:456-460` 的註解：

> The real JSPyBridge proxy returns **None for missing JS attributes** instead of
> raising AttributeError (bridge.js answers 'void' for undefined), so the
> except-branch above never fires against a live bridge — check the value too, or
> students get a bare **"'NoneType' object has no attribute 'goto'"** instead of this hint.

也就是說，維護者**已經知道這個失敗模式**，但只針對 `pathfinder` 這一個名字做了修補
（`:453-454`、`:461-462`）。其他所有名字仍走原路。

**學員實際會遇到的情況**：

```python
bot.mvoe_forward(3)      # 打錯字
```

→ `__getattr__("mvoe_forward")` → JS proxy 回 `None`（**不是** `AttributeError`）
→ `None(3)` → `TypeError: 'NoneType' object is not callable`

對照課程目標「看懂錯誤行數、錯誤原因」：

| | 學員得到什麼 |
|---|---|
| 錯誤**行數** | ✅ 正確指向他那一行 |
| 錯誤**原因** | ❌ 「NoneType 不能被呼叫」。真正原因是「你把方法名字拼錯了」。訊息不但沒幫助，還把學員的注意力導向 `None` 這個他當天可能還沒學到的概念 |

屬性讀取更糟——`bot.usernaem` 靜靜回 `None`，**完全不報錯**，
`print(bot.usernaem)` 印出 `None`，學員會以為是伺服器的問題。

**與 F-06 疊加**：上面那個 `TypeError` 印出來之後，atexit 的 `run_forever()`
接手，程式**繼續掛著不結束**。所以完整體驗是：

> 印出一個看不懂的錯誤 → 游標不動 → 學員舉手叫隊輔

這是 5 天營隊裡最會消耗隊輔時間的單一路徑。

**不修，只記錄。** 但指出兩件事：

1. 修補成本很低——`__getattr__` 已經有 `pathfinder` 的特例分支，
   把它推廣成「`value is None` 且 `name` 不在已知 mineflayer 屬性表 → 丟
   `AttributeError('Bot 沒有 xxx 方法，你是不是要打 yyy？')`」是同一個位置的擴充。
   `bot.pyi` 已經有完整的合法名稱清單可以拿來做拼字建議。
2. 這件事**沒有寫在任何文件裡**。`AGENTS.md` 的「錯誤處理」段（`:190-218`）
   列了 5 條失敗路徑的規則，沒有這一條——而它是學員最常撞到的一條。

---

## 統計（2026-07-29 重新評級後）

| 嚴重度 | 數量 | 編號 |
|--------|------|------|
| CRITICAL | 0 | — |
| **HIGH** | **2** | **F-06、F-11** — 都是「初學者撞到錯誤之後會發生什麼」 |
| MEDIUM | 3 | F-03、F-04、F-09 |
| LOW | 4 | F-05、F-08、F-10、F-02 |
| 已接受 / 關閉 | 2 | F-01（威脅模型不成立）、F-07（不教 try/finally） |

**重新評級後的結論**：這次審查真正該處理的不是資安，是
**「初學者寫錯之後，SDK 給他什麼」**。F-06（掛住）與 F-11（錯誤訊息無意義）
是同一條學員路徑的前後兩半，且兩者的修補點都在 `_bot_runtime.py` 同一個檔案。

**需要你決定的**：F-06 的保活行為在「腳本崩潰」時是否為刻意設計。
其餘皆為可直接修的文件或 docstring 漂移。
