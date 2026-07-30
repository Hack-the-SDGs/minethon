# 階段一：對照報告（受眾落差）

> 立場：我是那個學員。上午剛學完 Python 基礎，下午要用 minethon 做出東西。
> 方法：只讀程式碼推導，不看文件宣稱；能實測的都連上 `mc.ntust.camp:50213` 實測過。
> 日期：2026-07-29　　版本：minethon 0.4.9

## ⚠️ 版本修訂記錄

**初版寫於 `c2cd317`，事後發現落後 10 個 commit，已對 `dfd9564` 全面重驗。**

| 落後期間動到的東西 | 對本報告的影響 |
|---|---|
| `minethon_reference/` **整棵刪除**（31ae3d6） | **假設 3 失效**，該問題已解決 |
| `README.md` 重寫（65e7d50） | 文件漂移類發現大部分已修，**簡寫已補上** |
| `skills/minethon/*` 重寫（f0fece9） | **簡寫已補上**，AI 輔助路徑已通 |
| `AGENTS.md` / `IDEA.md` / `pc_setup/README.md` | 引用需更新 |
| `src/minethon/_event_login.py`（+4 -1，多接 `TypeError`） | 不影響任何發現 |
| 新增 `docs/review/findings.md` + `inventory.md` | **已存在一份文件面審查**，見下方對照 |

**關鍵：`_commands.py` / `_bot_runtime.py` / `bot.pyi` / `errors.py` 一行都沒動。**
所以第 1～4 節的能力對照、以及 `design-findings.md` 的 P0～P3 全部成立，
實測結果也全部有效（測試當下磁碟上的原始碼與現在相同）。

## 與既有 `docs/review/findings.md` 的關係

那份是**文件面**審查（11 條 F-xx，關注正確性與資安）。
本報告是**受眾面**審查（學員能不能用）。兩者互補，不重複。
重疊處我在 `design-findings.md` 逐條標了 `= F-xx`。
其中 **F-06（腳本拋例外後掛住）** 我實測到了更嚴重的數字，見該報告 P3-1。

---

## 使用的假設（會改變做法的關鍵歧義）

1. **「下午目標」＝ `examples/quests/` 那批關卡。**
   repo 內只有 q01 / q02 / q07 / q08 / q10 五個，但伺服器的 trigger 清單顯示
   實際至少有 `labfire`、`stack`、`drill`、`library`、`restaurant` 五種任務
   （實測 `bot.tabComplete("/trigger ")` 回傳 58 個 objective）。
   所以 repo 裡的範例**不是全集**，`library` / `restaurant` 我沒有樣本。
   下面的「需要的能力」是從這五個推導的，缺的兩個可能會擴大差集。

2. **學員讀的是 `examples/quests/*/main.py`。**
   ~~README 的快速開始用 `create_bot(host=..., username=...)`，簡寫只在範例裡出現。~~
   **修訂（65e7d50 / f0fece9）**：README:50-59 與 `SKILL.md`:29-35 現在都把簡寫
   放在最前面並說明 `~/.htsdg.json`。這個落差已經沒有了，兩份文件都能當入口。
   `examples/quests/` **本身未被修改**，所以第 3 節的「6/7 支超出能力邊界」不變。

3. ~~**`minethon_reference/` 不會發給學員。**~~
   **已作廢**：整棵目錄在 31ae3d6 被刪除（既有審查的 F-09）。
   我原本把它列為「若會發下去就是最高優先項」——這個風險已經不存在。

4. **這批學員今天下午之前沒碰過 Ctrl-C。**
   既有的 `findings.md` F-06 明確寫了課程有教「看懂錯誤行數、錯誤原因」，
   但沒教 Ctrl-C。本報告的 P3-1 建立在這個前提上，並實測到
   **程式印完 traceback 後 100 秒仍未結束**。

---

## 1. 能力對照：暴露了什麼 vs. 下午需要什麼

### 1.1 實際暴露的量（用 AST 數 `bot.pyi` 的 `class Bot`，非估計）

| 層 | 內容 | 數量 |
|---|---|---|
| A. 同步學員 API | `_commands.py` 的 `Commands` mixin | **45** |
| B. 事件 API | `EventAdaptor.on_*` + `bind` + `run_forever` | **99 個事件** |
| C. mineflayer 直通 | `__getattr__` 落到 JS proxy，`bot.pyi` 全數列出 | **127** |
| — | `bot.` 在 PyCharm 的補全總數 | **172**（130 方法 + 42 屬性） |
| D. 其他公開面 | `BotEvent`、`minethon.models`（60+ 型別）、5 個錯誤類、`load_plugin` / `require` | — |

### 1.2 五個關卡範例實際用到的名字（全集）

```
create_bot            move_forward    turn_left     turn_right
get_front_block       action          dig           sneak
wait                  is_riding       use_player    get_player_pos
look_at               username
```

**14 個。** 其中 `username` 還不在學員 API 裡（走 C 層直通）。

### 1.3 差集

#### 有但用不到（噪音）— 約 158 個名字

- **C 層 127 個全部**。`activateEntityAt`、`putSelectedItemRange`、`writeBook`、
  `openEnchantmentTable`、`recipesFor`、`elytraFly`…… 學員打 `bot.` 就全部看到，
  camelCase 混在 snake_case 中間。**沒有一個是下午用得到的。**
- **99 個事件裡有 97 個用不到**（實際可能只有 `on_chat` / `on_spawn` 有場景，
  而這兩個也需要 class 語法，見第 3 節 → 實際是 **99 個全部用不到**）。
- **A 層 45 個裡有 31 個用不到**：`get_x/y/z`、`get_yaw/pitch`、`get_sneak`、
  `get_hand`、`get_block`、`get_block_property`、`look_block`、`find_block(s)`、
  `move_backward/left/right`、`jump`、`turn`、`set_turn`、`get_height`、
  `set_height`、`hold`、`unhold`、`drop`、`place`、`use`、`dismount`、
  `wait_spawn`、`chat`、`bind`、`run_forever`、`load_plugin`、`require`。
  （`wait_spawn` 特別諷刺：`create_bot("g_xxx")` 簡寫**已經內建呼叫它**，
  所有範例都不寫，但 README 和 skill 文件都教「一定要先呼叫」。）
- **`minethon.models`（60+ 型別 shell）**：存在的唯一用途是寫型別註記。
  學員不會寫型別註記。
- **`load_plugin` / `require` / `VersionPinRequiredError` / pathfinder**：零使用。
  但 pathfinder 被 `setup.sh` 預裝、被 `bot.pyi` 列出、被 README 當賣點。

#### 需要但沒開（缺口）— 5 個，其中 2 個是致命的

| # | 缺什麼 | 為什麼致命 |
|---|---|---|
| **G1** | **沒有辦法把視線拉平（沒有 `set_pitch` / `look_level`）** | 實測：機器人一 spawn 就是 `pitch = -67.7°`（低頭看地板）。`dig()` / `place()` / `look_block()` **全部**作用在 `blockAtCursor` 看到的方塊 = 地板。q01_swim 的 `for i in range(8): bot.dig(); bot.move_forward()` 挖的是腳下不是前面。學員唯一能改 pitch 的是 `look_at(x,y,z)`，要自己算前方座標 → 超出能力邊界。**`set_turn` 只改 yaw，刻意保留 pitch，所以轉向也救不回來。** |
| **G2** | **沒有「這個動作到底成功了嗎」的回報** | `dig()` / `action()` / `use()` / `set_height()` / `move_forward()` 全部在失敗時回傳成功值。詳見階段二 P0 群。 |
| G3 | 沒有辦法知道方塊名稱 / 動作名稱寫對了 | `find_block("oak_wood")`（正確是 `oak_log`）回傳 `None`，和「附近沒有」完全同形。`action("putout")` 靜默無事。 |
| G4 | `username` 不在學員 API（q07_stack 用了） | 走 C 層，`bot.pyi` 有列，但和 127 個噪音混在一起。 |
| G5 | 沒有「腳本結束了」的訊號 | 見第 2 節第 8 步。 |

---

## 2. 走完一個最小可運作範例，學員要吞多少東西

以 `q01_swim/main.py` 為基準（它是**唯一**一支完全落在能力邊界內的範例）。

### 2.1 要先理解的概念：7 個

| # | 概念 | 上午教過？ |
|---|---|---|
| 1 | `from minethon import create_bot` | ✅ import 教過 |
| 2 | `create_bot(...)` 回傳一個物件，存進變數 | ✅ 變數＋物件 |
| 3 | `bot.turn_left()` 是「對物件呼叫方法」 | ✅ 點運算子 |
| 4 | `for i in range(8):` 重複 8 次 | ✅ for-range |
| 5 | **`"g_swim"` 這個字串對應到某個任務帳號** | ❌ 純記憶，沒有規則可推 |
| 6 | **每個指令是「阻塞」的，會等做完才跑下一行** | ⚠️ 沒教過但符合直覺，可接受 |
| 7 | **腳本跑完不會自己結束，要按 Ctrl-C** | ❌ 沒教過，也沒有任何提示 |

### 2.2 要記住的名字：4 個

`minethon`、`create_bot`、任務簡寫字串、以及該關要用的 1～3 個動作名。
**這部分是好的。** 最小腳本的記憶負擔確實很低。

### 2.3 要照順序做的事：9 步

| # | 步驟 | 誰做 | 風險 |
|---|---|---|---|
| 1 | 工作人員跑 `pc_setup/setup.sh`，寫 `~/.htsdg.json` | 工作人員 | 沒跑 → `MinethonError: 找不到本機識別檔`（訊息很好） |
| 2 | 跑 `./setup.sh`（uv sync + 預裝 npm） | 工作人員/學員 | 需要 Node 22+ 與 uv；四十台機器的最大變數 |
| 3 | 開 PyCharm，選對 interpreter | 學員 | README 自己承認 editable 安裝會讓專案被標成 excluded，要手動改 SDK Paths |
| 4 | 寫 `main.py` | 學員 | — |
| 5 | 執行 | 學員 | — |
| 6 | **等約 6 秒**才連上（實測 5.4～6.8s） | — | 沒有任何「連線中…」提示，畫面全黑 |
| 7 | 看機器人動（每個動作後有 0.2s 停頓） | — | — |
| 8 | 腳本邏輯跑完 → **畫面停住，沒有任何輸出，行程不會結束** | 學員 | **實測：無 `quit()` 的腳本永遠不結束；有 `quit()` 的也要再等 ~30 秒才真的退出** |
| 9 | Ctrl-C（終端機下有效，會印「程式已結束。」） | 學員 | 若太快重跑 → `Connection throttled! Please wait before reconnecting.` |

**第 8 步是整條路徑上最糟的一格。** 實測資料：

```
[  5.7s] connected
[  5.9s] LAST LINE OF MY SCRIPT   ← 學員的最後一行 print
（此處 30 秒完全無輸出）
[ 35.7s] 機器人已斷線，程式結束。
```

而且這還是**有寫 `bot.quit()`** 的情況。所有 quests 範例都沒寫 `quit()`，
那種形狀下行程**永遠不會結束**（實測 60 秒後仍在跑）。
原因是 `create_bot` 裡的 `atexit.register(bot.run_forever)` — 這是刻意設計
（「讓學員不必記得寫 run_forever」），但它把「腳本寫完了」和「程式還活著」
變成同一個畫面：什麼都沒有。

---

## 3. 哪些 API 在能力邊界內根本寫不出來

判準：需要 `def` / `class` / 繼承 / `while` / dict / 例外處理 / comprehension /
async / decorator / 型別註記 其中之一。

### 3.1 完全寫不出來

| API | 卡在哪 | 影響 |
|---|---|---|
| **整個事件 API**：`EventAdaptor` + `bind()` | 需要 `class`、繼承、`def`、`self`、`*_` | README 的**頭號賣點**、99 個事件、`BotEvent`、`minethon.models` 全部連帶報廢 |
| `run_forever()` | 呼叫本身沒問題，但只有配 `bind()` 才有意義 | 孤兒 |
| `load_plugin(name, ver, export_key=...)` | keyword argument + 版本字串概念 | 孤兒 |
| `bot.pathfinder.goto(pf.goals.GoalNear(...))` | 需要建構物件、巢狀屬性 | 孤兒（skill 文件也明講「不要用」） |
| `bot.require(...)` | 同上 | 孤兒 |

**結論：B 層（事件）+ D 層（plugin/型別）對這批學員是 0% 可達。**
這不是「進階選項」，是**佔了公開 API 一半以上篇幅、但這個受眾一個都碰不到的東西**。

### 3.2 勉強能寫但會絆倒

| API | 問題 |
|---|---|
| `get_pos()` → `tuple` | `x, y, z = bot.get_pos()` 需要 tuple 解包（邊界外，但好教）。`bot.get_pos()[0]` 可行。 |
| `look_block()` → `((x,y,z), name)` | **巢狀 tuple**。要拿名字得寫 `bot.look_block()[1]`，還要先確認不是 `None`。 |
| `find_blocks()` → `list[tuple]` | 兩層。`for p in ...: p[0]` 勉強。 |
| 所有 `X or None` 的回傳 | 要寫 `if x == None:`（`is None` 沒教）。可行但沒人教過為什麼要判。 |
| `q08_drill` 的 `x, y, z = bot.get_player_pos(guide)` | 除了解包，**這個呼叫會在玩家離線／離開載入範圍時丟 `PlayerNotFoundError`**，而學員**不會寫 try/except** → 引導員走遠一步，程式直接死。這是 API 契約與受眾能力的正面衝突。 |

### 3.3 官方範例自己就超出邊界

| 範例 | 用到的邊界外語法 |
|---|---|
| `q01_swim` | ✅ **無**（唯一合格） |
| `q02_toilet` | `while True` |
| `q07_stack` | `while not`、f-string、`bot.username` |
| `q08_drill` | `while True`、tuple 解包、無法捕捉的例外 |
| `q10_labfire/state_1` | `while True`、`break` |
| `q10_labfire/state_2` | `def`、`global`、`set()`、**遞迴**、`enumerate`、tuple 解包 |
| `q10_labfire/state_3` | 同上 + 更複雜的狀態機 |
| `README` 快速開始 | f-string 格式化 `{x:.0f}` |
| `skills/minethon` 兩個範例 | `class`、繼承、`*_`、f-string |

**7 支範例裡 6 支學員讀不懂。** 教學終點是「能讀懂並修改別人的程式碼」——
以這批範例當「別人的程式碼」，`q10` 那兩支是大學演算法課的難度。

---

## 4. 為了通用性 / 未來擴充付出的複雜度（對這個受眾是負債）

| # | 設計 | 通用性換來的東西 | 對這個受眾的代價 |
|---|---|---|---|
| D1 | **`bot.pyi` 完整鏡射 mineflayer `index.d.ts`**（3134 行） | 進階使用者可以用任何 mineflayer 功能且有補全 | `bot.` 補全 **172 項**，其中 127 項用不到且命名風格不同。學員找 `move_forward` 要在 camelCase 海裡撈。 |
| D2 | **`__getattr__` 直通 JS proxy** | 任何 mineflayer 屬性都能用 | **打錯字不會報錯**：`bot.usernam` → `None`（實測），`bot.move_foward(3)` → `TypeError: 'NoneType' object is not callable`（實測）。這是 D1 的直接後果。 |
| D3 | **`EventAdaptor` 生成 99 個事件方法** | IDE 的 Override methods 一鍵填入 | 398 行、學員 0% 可達。`_handlers.py` 是第二大的 public 檔。 |
| D4 | **移動有兩套實作**（datapack grid provider + physics fallback） | 同一份 API 在有／無 datapack 的伺服器都能跑 | **實測：同一支 `move_forward(3)`，任務未啟動時走 physics（落在小數座標、撞牆靜默放棄），任務啟動後走精確格移。學員無從得知現在是哪一套。** 這是把伺服器狀態耦合進了 API 語意。 |
| D5 | `_normalize_handler` 的 emitter 注入偵測 | 相容 Node 14/15 | pinned runtime 永遠不會注入（AGENTS.md 自己講了）。純死重量。 |
| D6 | `load_plugin` / `require` / 版本 pin / `VersionPinRequiredError` | 可重現的 plugin 生態 | 零使用。 |
| D7 | `minethon.models` 60+ 型別 shell | 可寫 annotation | 學員不寫 annotation。 |
| D8 | `drop(name_or_id: str \| int \| None, count)` 的三態多載 | 一個名字涵蓋四種行為 | 學員只需要「丟掉手上的東西」。多載讓 hover 說明變長。 |
| D9 | `get_block_property(x,y,z,property_name)` | 讀任意 block state | 要先知道 `"lit"` / `"facing"` 這種名字才用得動。 |
| D10 | `_commands.py` **1472 行**，超出專案自訂的 800 行上限 | 全部同步指令集中一處 | 學員 ctrl+click 進去會看到 `@_paced` decorator、`threading.Lock`、`object.__setattr__`、`contextlib.suppress`、PEP 758 的 `except A, B, C:`（3.14 才合法，Google 會說是語法錯誤）。**原始碼本身也是教材，這份教材讀不了。** |

### 4.1 一個獨立的命名負債

`get_y()` 回傳 Y 座標（高度）。
`get_height()` 回傳**大小等級 1~5**（實體 scale）。

同一個詞在相鄰的兩個 API 指兩件事，而且 `set_height(4)` 實測**只寫本機**、
`get_height()` 會讀回 4，遊戲裡什麼都沒發生。詳見階段二 P0-2。

---

## 5. 一句話總結

> minethon 把 mineflayer 的**全部**表面積搬進了 Python，再在旁邊加了一層 45 個
> 好名字的同步指令。對「已經會寫 Python、想控制 Minecraft」的人，這個取捨是對的。
> 對「今天早上第一次看到 `for` 迴圈」的人，那 45 個好名字被埋在 172 個補全項、
> 99 個事件、和 6 支讀不懂的官方範例底下；而真正會殺死他們的不是複雜度，
> 是 **`dig()` 挖了地板卻回報成功**（G1 + G2）。

---

## 下一步

階段二（`design-findings.md`）已同步進行，含 P0～P5 分級、實測輸出、
「營期前必須處理 / 營期後再說」兩欄，以及「我沒能驗證的部分」。
