# 階段二：對抗測試與設計缺陷

> 立場：我是那個學員。對手是「困惑」，不是惡意。
> 方法：全部在乾淨環境對 `mc.ntust.camp:50213` 實測（帳號 `create_bot("bot")`）。
> 每一則的「他當下看到什麼」都是**貼上實際輸出**，不是推測；推測的地方會標「未驗證」。
> 日期：2026-07-29　版本：minethon 0.4.9　上場：8/4 下午

## ✅ 修正狀態（2026-07-30）

高信心的項目已經修完並實機驗證。`./scripts/format.sh` 全綠
（ruff / pyright 0 errors / 261 unit tests / stub drift gate）。

| ID | 狀態 | 實測前 → 實測後 |
|---|---|---|
| P0-1 `dig()` 假成功 | ✅ 修 | `((341,62,-473),'grass_block')` → `None` ＋「沒有被破壞。這裡可能不允許挖方塊，或是任務還沒開始。」 |
| P0-2 出生就低頭 | ✅ 修 | `pitch=-67.7` → `pitch=-0.00`；新增 `bot.look_level()`，`create_bot` 自動呼叫 |
| P0-3 `set_height` 自我確認 | ✅ 修 | `set_height(4)`→`get_height()`==4（謊） → ==1（實話），改走 `action("set height", level)` |
| P0-4 撞牆／負數靜默 | ✅ 修 | 無輸出 → 「前面有東西擋住，只走了 N 格就走不動了」／「格數要大於 0」 |
| P0-5 `action()` 零回饋 | ✅ 修 | 無輸出 → 「伺服器現在不接受動作「X」…目前可用的動作：…」；`action(123)` → `TypeError` |
| P0-6 屬性打錯回 `None` | ✅ 修 | `bot.usernam` → `None` → `AttributeError: …你是不是要找 username、uuidToUsername、useOn？` |
| P0-7 `use_player(自己)` | ✅ 修 | 回傳 `True` 同時被踢 → `ValueError: 不能對自己…按右鍵` |
| P0-8 方塊名字打錯 | ✅ 修 | `None` → 「沒有叫做「stonee」的方塊。你是不是要找 stone、stonecutter、sponge？」 |
| P1-1 方法打錯 | ✅ 修 | `'NoneType' object is not callable` → `AttributeError` ＋ did-you-mean |
| P1-2 `place()` 原始 JS stack | ✅ 修 | 12 行 node stack → 「這裡不能放方塊。可能是保護區，或是任務還沒開始。」 |
| P1-3 連不上 → 77 行 stack | ✅ 修 | 77 行 ＋ 10.5 秒 ＋ 空訊息 → **1 行 ＋ 0.3 秒** |
| P1-4 kick 原因是 dict | ✅ 修 | `{'type':'compound',...}` → `duplicate_login`；throttle 另有專屬訊息 |
| P1-5 型別錯指向 lib | ✅ 修 | `'<=' not supported…` → 「移動的格數要用數字，收到的是str：'3'。…要先用 int() 轉換」 |
| P3-1 出錯／跑完後掛住 | ✅ 修 | **100 秒不結束 → traceback ＋「程式因為上面的錯誤停止了。」後退出**；正常跑完會印「程式已經跑完了…按 Ctrl-C 結束」 |
| P5-1 連線節流 | ✅ 修 | 「被伺服器踢出：Connection throttled!…」→ 「連線太密集了…等幾秒再跑一次就好。」 |
| F-05 docstring 漂移 | ✅ 修 | `errors.py` 已改成實情 |
| P1-6 `@_paced` traceback 雜訊 | ⏸ 沒動 | 一層 frame，代價低於重構風險 |
| P2-1 事件 API 需要 class | ⏸ 沒動 | 改 API 風險太高；改成在 `SKILL.md` 加零基礎守則（見下） |
| P2-2 範例超出邊界 | ⏸ 沒動 | 課程決定，不是我的 call。建議仍是 `while True:` → `for i in range(1000):` |
| P2-3 `get_player_pos` 丟例外 | ⏸ 沒動 | 「回 `None` 還是丟例外」是產品決定 |
| P3-2/3/4 命名 | ⏸ 沒動 | 改名是破壞性變更 |
| P4-1 172 個補全 | ⏸ 沒動 | 大改，營期後 |
| P5-2/3 環境 | ⏸ 沒動 | 需要你在教室機器上實測 |

**一項修正時自己踩到的 bug，留在這裡當紀錄：** 第一版的拼字建議用 live proxy 的
own-keys 當合法名稱清單，結果 `bot.vehicle`（沒騎車時 JS 端是 `undefined`）被判成
`moveVehicle` 的錯字。改成由 generator 從 `bot.pyi` 產生 `_members.py`。
另外 `suggest()` 走訪外部物件時，遇到只實作 `__getitem__` 的 fake 會無限迭代
（Python 舊式迭代協定），一度讓整個 test suite 卡死——現在由 `bounded_keys()` 擋住，
並有專門的回歸測試。兩者都寫進 `AGENTS.md`。

**一處事實更正：** 初版 P0-8 拿 `find_block("oak_wood")` 當「名字打錯」的例子是錯的
——`oak_wood` 是真實存在的方塊名（六面樹皮的原木），那次回傳 `None` 是「附近沒有」。
底層發現（「名字錯」和「附近沒有」用同一個值表示）不變，例子換成 `stonee`。

新增測試：`tests/unit/test_silent_failures.py`（24 個，每一則都對應上面一列）。

## ⚠️ 版本修訂

**初版寫於 `c2cd317`，事後發現落後 10 個 commit，已對 `dfd9564` 全面重驗。**

那 10 個 commit **只動文件與 `_event_login.py`（+4 -1）**。
`_commands.py` / `_bot_runtime.py` / `bot.pyi` / `errors.py` **一行都沒動**
（`git diff --stat c2cd317..dfd9564` 驗證），所以：

- **P0-1 ～ P3-4 全部成立**，實測輸出全部有效。
- **P4 文件類三條需要修正**，已在下方逐條標註（P4-2 整條作廢、P4-3 大部分已修）。
- **P3-1 反而要升級** —— 重驗時實測到比初版更嚴重的數字。

## 與既有 `docs/review/findings.md`（11 條 F-xx）的對照

| 本報告 | 既有 | 狀態 |
|---|---|---|
| P1-1 打錯方法名 → `'NoneType' not callable` | **F-11 · HIGH** | 同一條，已知，**未修** |
| P3-1 腳本結束／出錯後掛住 | **F-06 · HIGH** | 同根因，我補上實測數字並**升級** |
| P2-3 附帶：`PlayerNotFoundError` docstring | **F-05 · LOW** | 同一條，**未修**（`errors.py` 沒被動到） |
| P4-2 `minethon_reference/` | **F-09 · MEDIUM** | **已修**（目錄已刪），本報告該條作廢 |
| P4-3 README 幽靈連結 | **F-08 · LOW** | **已修** |
| P0-1 ～ P0-8、P1-2 ～ P1-6、P2-1/2、P3-2/3/4、P4-1/4、P5-1/2/3 | 無對應 | **本報告新增**（既有審查只看文件，沒有實機跑） |

**測試環境注意**：測試世界裝了禁止破壞／放置方塊的插件。這反而是好事——
它讓「伺服器拒絕動作時 SDK 怎麼表現」這一整類問題現形，而那正是關卡現場會發生的事
（權限、任務未開始、目標不對）。

---

## 嚴重度定義（依「學員會不會卡死」，不依技術優雅度）

| 級 | 定義 |
|---|---|
| **P0** | 靜默錯誤：能跑、不報錯、結果錯的。沒有 traceback 就沒有出路。 |
| **P1** | traceback 指向 lib 內部，而不是他自己寫的那一行。 |
| **P2** | 需要未教過的語法才能使用。 |
| **P3** | 順序／狀態耦合：順序錯了才爆，訊息看不出是順序問題。 |
| **P4** | 概念負擔：第一支能跑的程式之前要吞太多東西。 |
| **P5** | 環境脆弱：四十台筆電、一百分鐘，裝不起來就是全班停擺。 |

---

# 營期前必須處理

---

## P0-1　`dig()` 在什麼都沒挖掉的時候回報成功

**位置**　`src/minethon/_commands.py:1272-1312`（`dig`）；根因在
`mineflayer/lib/plugins/digging.js:131` — `waitTimeout = setTimeout(finishDigging, waitTime)`

**學員會怎麼踩到**　`q01_swim/main.py` 的核心迴圈就是這個形狀：

```python
for i in range(8):
    bot.dig()
    bot.move_forward()
```

只要伺服器不允許破壞（保護區、冒險模式、任務未開始、工具不對），這個迴圈照跑。

**他當下看到什麼**　實測輸出：

```
dig() returned: ((341, 62, -473), 'grass_block')
block at 341,62,-473 is now: 'grass_block'  (was 'grass_block')
  -> dig() reported success but the block is still there?
```

回傳一個看起來完全成功的 tuple。終端機沒有任何字，遊戲裡沒有任何變化。

**根因**　mineflayer 的 `dig()` 用**純客戶端計時器**結束：
`bot.digTime(block)` 估一個毫秒數，`setTimeout` 到了就 resolve，
**從不等伺服器確認方塊真的破了**。minethon 在 `self._js.dig(...)` 之後
無條件 `return result`，把那個估計值當成事實。

**能不能自救**　不能。沒有 traceback、沒有回傳值差異、沒有 log。
唯一線索是「遊戲裡沒動靜」，而他同時還在跟 P0-2（挖錯地方）搏鬥，
兩個症狀長得一模一樣。

**建議方向**　`dig()` 挖完後重讀一次 `blockAt(pos)`：名字沒變就回傳 `None`
並印一行「這個方塊挖不動（可能是保護區或任務還沒開始）」。
和既有的「太硬了，挖不動。」同一條路徑，成本很低。

---

## P0-2　機器人一出生就低頭看地板，而學員沒有任何辦法把視線拉平

**位置**　`_commands.py:1056-1103`（`set_turn` / `turn` / `look_at`）——**沒有 `set_pitch`**

**學員會怎麼踩到**　什麼都不用做。實測，一連上去：

```
spawn      yaw=333.3 pitch=-67.7
look_block: ((341, 62, -473), 'grass_block')   ← 這是腳下的地板
front: None                                    ← 前面其實沒有東西
```

`dig()` / `place()` / `use()` / `look_block()` **全部**作用在
`blockAtCursor` 看到的方塊。低頭 67 度時那永遠是地板。

`dig()` 的 fallback（「沒瞄準東西就挖前面那格」）**永遠不會觸發**，
因為 `blockAtCursor` 有回傳值（地板），只是回傳了錯的東西。

**他當下看到什麼**　`bot.dig()` 回傳 `((341, 62, -473), 'grass_block')`——
一個他沒打算挖的座標。而且因為 P0-1，連「挖失敗」都看不出來。

**這件事會蔓延**　`set_turn()` 刻意保留 pitch（`_commands.py:1078`：
`self._js.look(math.radians(yaw), float(entity.pitch), True)`），
所以 `turn_left()` / `turn_right()` **會把低頭狀態帶著走**。實測：

```
after turn_left yaw=63.3 pitch=-67.7
```

**能不能自救**　不能。學員能改 pitch 的唯一 API 是 `look_at(x, y, z)`，
要自己算出「正前方同高度」的座標——需要 yaw、三角函數，或至少
`get_pos()` + 方向判斷。全部超出能力邊界。

**建議方向**　二選一（我建議兩個都做）：
1. 加 `bot.look_level()`（把 pitch 設成 0，一行），放進學員 API 表。
2. `create_bot` spawn settle 之後自動把 pitch 歸零——反正 `_SPAWN_SETTLE_SECONDS`
   那 3.5 秒已經在等了。

> 注意：這**不是**「多加一個功能」的問題。`dig` / `place` / `use` / `look_block`
> 四個學員 API 的語意全部建立在「瞄準哪裡」上，而「瞄準哪裡」目前是不可控的。

---

## P0-3　`set_height()` 只改本機，`get_height()` 讀回自己剛寫的謊

**位置**　`_commands.py:1114-1133`

**學員會怎麼踩到**　`bot.set_height(4)`，然後想確認：`print(bot.get_height())`。

**他當下看到什麼**　實測：

```
get_height() before -> 1
set_height(4)       -> None
get_height() after  -> 4     ← 但遊戲裡的機器人沒有變大
```

`set_height` 做的事是 `attributes[key] = {"value": 4.0, "modifiers": []}`——
寫進 JS proxy 上的本機屬性。`get_height` 讀同一個地方。
**這是一個會自我確認的謊**：學員用最自然的方式驗證，得到「成功」。

**能不能自救**　不能，而且比一般 P0 更糟——他做了正確的除錯動作，
拿到了確認他是對的的答案。

**建議方向**　三選一：
1. 刪掉 `set_height`（IDEA.md 列了但伺服器不配合就是空的）。
2. 改成 `action("set height", level)`，走既有的伺服器權威路徑。
3. 保留但 `get_height()` **只讀伺服器回報的值**，`set_height` 不寫本機
   （這樣 `get_height()` 回 1 就誠實地說「沒生效」）。

我建議 2。既有機制、零新概念。

---

## P0-4　`move_forward()` 會在兩套完全不同的實作之間靜默切換

**位置**　`_commands.py:897-937`（`_walk`）、`745-793`（`_grid_move_context`）

**學員會怎麼踩到**　寫 `bot.move_forward(3)`。就這樣。

**實測，同一台伺服器、同一個帳號**：

```
scoreboard 'q.labfire.step' title='minethon:grid_move:v1'   ← provider 確實存在
_is_grid_provider: True
score for me: None
enabled triggers: {...58 個...}   ← 但 q.labfire.step 不在裡面（任務沒開始）
_grid_move_context(): None        ← 所以走 fallback

start pos       (336.80, 63.0, -471.46)
move_forward(3) (339.99, 63.0, -471.66)   ← 走了 3.19 格，落在小數座標
```

任務**開始後**同一行會走伺服器逐格移動，落在整數格中心。
**同一支程式、同一行、兩種結果，沒有任何提示告訴他現在是哪一種。**

**三個衍生的靜默失敗**（都實測過）：

| 情況 | 實際行為 |
|---|---|
| 撞牆 | 卡 5 秒（`_WALK_STALL_TIMEOUT`）後 `break` 跳出迴圈，**正常回傳**，無例外 |
| `move_forward(0.5)` | 有 provider → `ValueError: 格數必須是整數`；無 provider → 默默走 0.5 格 |
| `move_forward(-2)` | `blocks <= 0` → 直接回傳現在位置，什麼都不做，無警告 |

**他當下看到什麼**　什麼都沒有。走到錯的地方，或原地不動。
在 `q10_labfire` 的迷宮裡，這代表他的座標模型和實際位置從某一步開始就對不上，
而 DFS 會繼續跑完，回報「完成」。

**能不能自救**　不能。他不知道有兩套實作存在，更不知道要怎麼判斷。

**建議方向**
1. 撞牆的 stall timeout 不要靜默 `break`——印一行「前面有東西擋住，走不動了」。
   （不要丟例外，學員不會 try/except；印字就好。）
2. `blocks <= 0` 印一行提醒。
3. 兩套實作的**行為**要收斂：fallback 也應該落在整數格（走完後 round 到最近格）。
   否則 `q10` 這種依賴格線的關卡在 provider 沒啟用時必然算錯。
4. 至少在 `create_bot` 連上時印一行「精確移動：開／關」，讓他知道自己在哪個模式。

---

## P0-5　`action()` 是整個關卡玩法的核心，而它完全沒有回饋

**位置**　`_commands.py:1432-1461`

**學員會怎麼踩到**　`q10_labfire` 的整個玩法就是 `bot.action("put out")`。

**實測**：

```
action("not a real action")  -> None      ← 不存在的動作，沒有任何錯誤
action(123)                  -> None      ← 型別完全錯，也通過驗證（"123" 全是合法字元）
```

`action()` 做的事是 `self._js.chat("/trigger u100_bot_put_out")`。
vanilla 的 `/trigger` 對未啟用的 objective **靜默無效**——這是刻意的設計
（AGENTS.md：「客戶端零副作用」），設計本身是對的。
但對學員來說結果是：**打錯名字、任務沒開始、站錯位置、面錯方向，四種情況長得一模一樣：什麼都沒發生。**

**能不能自救**　不能。沒有錯誤、沒有回傳值、沒有 log。
他能做的只有反覆改字串重跑（每次 40 秒，見 P3-1）。

**建議方向**　不用改動伺服器權威的設計，只要加**送出端的回饋**：
1. 送出前先用既有的 `_enabled_trigger_objectives()`（已經寫好了，
   `_commands.py:707`）檢查 `<username>_<action>` 在不在清單裡；
   不在就印「伺服器現在不接受動作 `put out`（任務可能還沒開始，或名字打錯了）」
   **並列出目前可用的動作名**。這比任何文件都有效。
2. `action(123)` 這種非字串輸入應該丟 `ValueError`，不要正規化成 `"123"`。

> 這一則我認為是**投資報酬率最高的一項**。既有程式碼已經有能力做這件事
> （tab-complete 那條路），只是沒接上。

---

## P0-6　打錯屬性名回傳 `None`，永遠不會報錯

**位置**　`_bot_runtime.py:440-463`（`Bot.__getattr__`）

**學員會怎麼踩到**　`bot.usernam`、`bot.helth`、`bot.postion`。

**實測**：

```
bot.usernam  ->  None
```

註解自己寫了原因（`_bot_runtime.py:456`）：
「真實 JSPyBridge proxy 對不存在的 JS 屬性回傳 None 而不是丟 AttributeError」。

**他當下看到什麼**　`if bot.usernam == "U100_bot":` 永遠是 False。
`print(bot.helth)` 印出 `None`。沒有 traceback，沒有出路。

**能不能自救**　不能。這是 P0 的定義本身。

**建議方向**　`__getattr__` 已經對 `pathfinder` 做了 `None` 檢查
（`:461`）。把它一般化：值是 `None` 且名字不在已知的 mineflayer 成員表裡
（`bot.pyi` 已經有那張表，`scripts/check_stubs.py` 就在讀它）→ 丟
`AttributeError: Bot 沒有 'usernam' 這個東西。你是不是要打 'username'？`
（difflib.get_close_matches，標準庫，三行）。

---

## P0-7　`use_player()` 回傳 `True`，同時機器人正在被踢下線

**位置**　`_commands.py:1376-1421`

**學員會怎麼踩到**　`q07_stack` 要求對別人按右鍵。學員把名字打成自己的，
或迴圈裡的 `target` 還沒更新。

**實測**：

```
機器人被伺服器踢出：{'type': 'string', 'value': 'Cannot interact with self!'}
bot.use_player(自己)  -> True
```

回傳 `True`（成功），而伺服器已經把它踢了。
`q07_stack` 的迴圈是 `while not bot.is_riding(): bot.use_player(target)`——
踢線後 `_stop_with_message` 會結束整個程式，但在那之前
`use_player` 已經回報過成功。

**能不能自救**　訊息裡有 `Cannot interact with self!`，算是有線索。
但它混在一個 Python dict 的 repr 裡（見 P1-4），而且緊接著程式就死了。

**建議方向**　`use_player` 回傳值目前恆為 `True`（`return True` 寫死），
沒有攜帶任何資訊。要嘛讓它回傳 `None`（誠實地說「我只是送了封包」），
要嘛加一個明確的 self-check：`username == bot.username` → 丟
`ValueError("不能對自己按右鍵")`，在送封包之前。

---

## P0-8　名字打錯 / 型別給錯，一律靜默回傳 `None` 或 `False`

**位置**　`_commands.py:568-576`（`_block_id`）、`653-685`（`find_block(s)`）、
`578-586`（`get_block`）、`1157-1168`（`hold`）

**實測**：

```
find_block("oak_wood")        -> None    （正確名字是 oak_log）
find_blocks("stonee")         -> []
get_block("1","2","3")        -> None    （型別完全錯）
find_block(5)                 -> None    （型別完全錯）
hold("nonexistent_item")      -> False
```

**問題不是回傳 `None`，是「名字錯」和「附近沒有」用同一個值表示。**
Minecraft 有一千多個方塊名，學員沒有任何查詢管道
（`bot.registry.blocksByName` 是 C 層直通，超出邊界）。

**能不能自救**　不能區分。他會一直改座標、改位置，而問題在字串。

**建議方向**　`_block_id` 回 `None` 時（＝ registry 裡沒這個名字，
和「附近沒有」是不同的事）印一行：
「沒有叫做 `oak_wood` 的方塊。你是不是要找 `oak_log`？」
——同樣用 `difflib.get_close_matches` 對 `blocksByName` 的 key 比對。

---

## P1-1　打錯方法名 → `TypeError: 'NoneType' object is not callable`　（= 既有 **F-11 · HIGH**，未修）

**位置**　`_bot_runtime.py:440`（`__getattr__`）——與 P0-6 同根，但這個至少會爆

> **重驗更正**：`_bot_runtime.py` 在那 10 個 commit 裡沒被動到，行為完全不變。
> 但 cc45ad6 已經把**兩半都寫進 `AGENTS.md:215-222`**
> （`bot.mvoe_forward(3)` → TypeError、`bot.usernaem` → 安靜的 `None`），
> 並列為「未完成」清單的最優先項（`AGENTS.md:278-279`）。
> 所以初版說 P0-6「既有審查沒有涵蓋」是**錯的**，維護者已經知道兩半。
>
> 這兩條仍然留在報告裡，理由是：**寫進 AGENTS.md 不會幫到學員**。
> AGENTS.md 是給 AI 和維護者讀的；8/4 下午撞到 `'NoneType' object is not
> callable` 的十五歲學員不會去讀它。已知 ≠ 已解決，而距離上場剩五天。

**實測**：

```
bot.move_foward(3)   !! TypeError: 'NoneType' object is not callable
bot.Chat('hi')       !! TypeError: 'NoneType' object is not callable
bot.get_poss()       !! TypeError: 'NoneType' object is not callable
```

**他當下看到什麼**　traceback 的頂端**確實**指著他自己的那一行（這點是好的），
但訊息裡**沒有出現他打錯的那個名字**。上午剛學會讀 traceback 的人，
看到 `'NoneType' object is not callable` 完全無法連結到「我 move_forward 少打一個 r」。

正常的 Python 是 `AttributeError: 'Bot' object has no attribute 'move_foward'`——
那個訊息他看得懂。這裡是被 `__getattr__` 的直通設計換掉的。

**能不能自救**　勉強，如果有人教過他「NoneType not callable 通常代表名字打錯」。
不會自己想到。

**建議方向**　同 P0-6，一起修。

---

## P1-2　`place()` 失敗 → 一整面 Node.js 堆疊

**位置**　`_commands.py:1314-1334`

**學員實際看到的完整畫面**（實測，未刪減）：

```
☕  JavaScript Error  Call to 'placeBlock' failed:
> bot.place()          # <-- 學員寫的這一行爆了
  at <module> (.../tb1.py:4)
> result = method(self, *args, **kwargs)
  at wrapper (/Users/.../src/minethon/_commands.py:398)      ← @_paced 產生的雜訊
> self._js.placeBlock(ref, _make_vec3(*offset))
  at place (/Users/.../src/minethon/_commands.py:1329)

... across the bridge ...

  at async Bridge.onMessage (.../javascript/js/bridge.js:231:7)
  at async Bridge.call (.../javascript/js/bridge.js:136:17)
  at async EventEmitter.placeBlock (.../mineflayer--342e33372e30/lib/plugins/place_block.js:33:5)
  at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
  at placeBlockWithOptions (.../mineflayer--342e33372e30/lib/plugins/place_block.js:13:36)
  at onceWithCleanup (.../mineflayer--342e33372e30/lib/promise_utils.js:62:26)
> const timeoutError = new Error(`Event ${event} did not fire within timeout of ${timeout}ms`)
🌉 Error: Event blockUpdate:(338, 63, -475) did not fire within timeout of 5000ms
```

**公道話**：第一行就是他自己的那一行，這比我預期的好。
**問題**：下面十二行全是他無法理解也無法行動的內容，
而最後那句英文（`blockUpdate did not fire`）的真正意思是
**「伺服器不讓你放方塊」**——這件事在整段輸出裡完全沒有出現。

而且 `place()` 前面已經有兩層防禦（手上沒東西 → `None`；沒瞄到 → `None`），
唯獨「伺服器拒絕」這個現場最常見的情況直接漏出原始例外。

**能不能自救**　不能。

**建議方向**　`place()` 包住 `placeBlock` 的例外，訊息裡含
`blockUpdate ... did not fire` 時 → 印「這裡不能放方塊（可能是保護區或任務還沒開始）」
並回傳 `None`。和 `dig()` 的「太硬了，挖不動。」同一個模式。

---

## P1-3　伺服器連不上 → 77 行 Node 堆疊，最後一行中文是空的

**位置**　`_bot_runtime.py:687`（`Once(js_bot, ERROR)` 註冊得太晚）

**學員會怎麼踩到**　伺服器沒開、WiFi 斷、host 打錯。**營期現場一定會發生。**

**實測**（`create_bot(host="localhost", ...)`，沒有東西在聽）：

```
[JSE] node:internal/process/promises:332
[JSE]     triggerUncaughtException(err, true /* fromPromise */);
[JSE] AggregateError [ECONNREFUSED]:
[JSE]     at internalConnectMultiple (node:net:1193:18)
[JSE]     at Client.<anonymous> (/Users/.../mineflayer--342e33372e30/lib/loader.js:110:9)
...（共 77 行）...
[JSE] Node.js v25.9.0
Timed out get 16 message <Thread(Thread-3 (loop), started daemon 6177697792)>

連線發生錯誤：
```

**耗時 10.5 秒**，最後那行中文**冒號後面是空的**——
因為 bridge 已經死了，`_on_login_error` 讀不到 error 物件的內容。

**根因**　`createBot()` 一回傳就開始 ping 伺服器；ping 失敗時
mineflayer 在 `loader.js:110` 把 client error 轉發成 bot error。
而 minethon 的 `Once(js_bot, ERROR)` 是在 `createBot()` **回傳之後**
才跨 bridge 註冊的——中間那個空隙裡沒有 listener，Node 的 EventEmitter
就直接 throw，整個 node 行程死掉。
帳密錯誤沒事（那發生得晚很多，listener 早就裝好了，實測會正確印
「找不到此任務。請檢查任務名稱是否正確，或是任務是否開放。」），
**但「連不上」這個最常見的失敗剛好落在空隙裡。**

**能不能自救**　不能。

**建議方向**　在 `mineflayer.createBot()` **之前**先做一次可達性檢查
（`socket.create_connection((host, port), timeout=3)`，標準庫），
連不上就直接印「連不到伺服器 mc.ntust.camp:50213。請確認網路正常。」
——這比想辦法贏那個 race 簡單得多，而且訊息更準。

---

## P1-4　被踢的原因印成 Python dict

**位置**　`_bot_runtime.py:134-143`（`_on_kicked` 的 `str(reason)`）

**實測**（兩次不同的踢線）：

```
機器人被伺服器踢出：{'type': 'compound', 'value': {'translate': {'type': 'string', 'value': 'multiplayer.disconnect.duplicate_login'}}}
機器人被伺服器踢出：{'type': 'string', 'value': 'Cannot interact with self!'}
```

`reason` 是 protodef 的 NBT 結構，`str()` 之後就是這樣。
真正的訊息（`duplicate_login`、`Cannot interact with self!`）埋在裡面。

**能不能自救**　第二個例子他可能猜得出來。第一個不可能。

**建議方向**　`_component_plaintext()` 這個函式已經存在
（`_commands.py:290`），而且已經處理了 `{type:"string", value:...}` 和
`extra` 的攤平。直接拿來用；`translate` key 再加一行 fallback 即可。

---

## P1-5　型別給錯 → traceback 落在 lib 內部，訊息與他寫的東西無關

**位置**　`_commands.py:398`（`_paced` wrapper）、`904`（`_walk`）、`1122`（`set_height`）、`382`（`_bridge_safe_sleep`）

**實測**：

```
bot.move_forward("3")  !! TypeError: '<=' not supported between instances of 'str' and 'int'
                          → _commands.py:398 → :942 → :904
bot.wait("3")          !! TypeError: '>' not supported between instances of 'str' and 'int'
bot.set_height("3")    !! TypeError: '<=' not supported between instances of 'int' and 'str'
```

三層 lib frame，訊息在講 `<=` 運算子。學員寫的是 `bot.move_forward("3")`。

**對照組（做得好的）**：

```
bot.move_forward(3, 5) !! TypeError: Commands.move_forward() takes from 1 to 2 positional arguments but 3 were given
bot.sneak()            !! TypeError: Commands.sneak() missing 1 required positional argument: 'on'
bot.set_height(0)      !! ValueError: 大小等級只能是 1~5，收到 0。
```

這三個很好——方法名在訊息裡，或訊息是中文的。**差別在有沒有在入口驗證。**

**建議方向**　學員 API 的數值參數在函式開頭統一驗一次：
「`move_forward` 的格數要是數字，收到的是文字 `'3'`。
（如果是從 `input()` 或字串來的，要先用 `int()` 轉換）」——
上午剛教過型別轉換，這個訊息直接接得上。

---

## P1-6　`@_paced` 讓每一個動作的 traceback 都多一層無意義的 frame

**位置**　`_commands.py:386-402`

每個 `@_paced` 動作出事時，traceback 裡都會有：

```
> result = method(self, *args, **kwargs)
  at wrapper (/Users/.../src/minethon/_commands.py:398)
```

學員讀 traceback 時要學會跳過它。

**建議方向**　小事，但便宜：`_paced` 的 wrapper 不要包住呼叫，
改成 `try/finally` 之外的形式其實無解；比較實際的是接受它，
或把停頓移到呼叫端（`Bot.__getattribute__` 層）以保持 `_commands.py` 的
函式是「乾淨的」。優先度低於上面所有項目。

---

## P2-1　整個事件 API 需要 `class` 和繼承——這批學員 0% 可達

**位置**　`_handlers.py`（398 行、99 個事件）、`_bot_runtime.py:534-587`（`bind`）

唯一的事件寫法是：

```python
class Greeter(EventAdaptor):        # class + 繼承
    def on_chat(self, username, message, *_):   # def + self + *args
        ...
bot.bind(Greeter())
```

`class`、繼承、`def`、`self`、`*_` **四樣**都在能力邊界外。

**影響範圍**：99 個事件、`BotEvent`、`minethon.models` 的 60+ 型別、
`run_forever()`、README 的第二和第三個賣點、`skills/minethon` 的兩個範例。
**佔公開 API 篇幅的一半以上，這個受眾一個都碰不到。**

**建議方向**　營期前不要改 API（風險太高）。改**發下去的教材**：
把事件那一整段從學員視野裡拿掉，只留同步指令。
營期後再考慮要不要提供一個免 class 的入口
（例如 `bot.on_chat_run(函式)`——但那需要 `def`，一樣不可達；
或者乾脆承認事件 API 是給助教／進階組的）。

---

## P2-2　7 支官方範例裡有 6 支學員讀不懂

**位置**　`examples/quests/**`、`README.md`、`skills/minethon/SKILL.md`

| 範例 | 邊界外的語法 |
|---|---|
| `q01_swim` | ✅ 無 |
| `q02_toilet` | `while True` |
| `q07_stack` | `while not`、f-string、`bot.username` |
| `q08_drill` | `while True`、tuple 解包、無法捕捉的例外（見 P2-3） |
| `q10_labfire/state_1` | `while True`、`break` |
| `q10_labfire/state_2` | `def`、`global`、`set()`、**遞迴 DFS**、`enumerate` |
| `q10_labfire/state_3` | 同上，更複雜 |
| `README` 快速開始 | f-string 格式化 `{x:.0f}` |
| `SKILL.md` 兩個範例 | `class`、繼承、`*_`、f-string |

教學終點是「能讀懂並修改別人的程式碼」。`q10` 那兩支是大學演算法課的題目。

**建議方向**
1. `while True:` → `for i in range(1000):`。語意夠接近，且在邊界內。
   這一個代換就救回 q02 / q08 / q10_state_1 三支。
2. `q10_state_2` / `state_3` 明確標成「挑戰題／助教示範」，不要當成範例。
3. 每支 `main.py` 開頭加三行註解說明「這支用到了什麼」。

---

## P2-3　`get_player_pos()` 會在迴圈裡丟出學員無法捕捉的例外

**位置**　`_commands.py:1349-1374`；範例 `q08_drill/main.py`

```python
while True:
    x, y, z = bot.get_player_pos(guide)   # 引導員走遠 → PlayerNotFoundError
    bot.look_at(x, y, z)
    bot.move_forward()
```

**實測**：

```
get_player_pos('nobody') !! PlayerNotFoundError: 找不到玩家 'nobody'。請確認對方在線、與機器人在同一世界，且位於已載入範圍內。
```

訊息本身**很好**。問題是：這是一個**暫時性**的狀況（玩家走出載入範圍
是隨時會發生的正常事件），而 API 的反應是丟例外，
**而學員不會寫 `try/except`**。引導員走快一點，程式就死。

**能不能自救**　訊息看得懂，但他唯一能做的是「叫引導員站近一點」。
沒辦法在程式裡處理。

**建議方向**　暫時性狀況不該丟例外給不能捕捉例外的人。
加一個回傳 `None` 的變體，或讓 `get_player_pos` 在找不到時回 `None`
並印一行提醒（把丟例外留給 `use_player` 那種一次性動作）。

> 附帶（= 既有 **F-05 · LOW**，**未修**）：`errors.py:14-20` 的
> `PlayerNotFoundError` docstring 還寫著「Reserved: no current student command
> looks up players by name, so nothing raises this yet」——
> `get_player_pos` 和 `use_player` 兩個都在丟它。
> 重驗確認 `errors.py` 沒被那 10 個 commit 動到，這條仍然成立。

---

## P3-1　程式印完 traceback 之後掛住 —— 實測 100 秒仍未結束　**（重驗後升級）**

> **升級理由**：初版我只測了「正常跑完」的情況（30 秒／永遠）。
> 重驗時補測了**學員自己寫錯**的情況，結果嚴重得多。
> 這條 = 既有審查的 **F-06 · HIGH**，我補上的是數字與第三種表現形式。
> **依「學員會不會卡死」的排序，這條應該和 P0 群並列在最前面。**

**位置**　`_bot_runtime.py:715`（`atexit.register(bot.run_forever)`）
＋ `:280-299`（`_install_quiet_interrupt` 的 excepthook）

**根因**　excepthook 對 `KeyboardInterrupt`、per-call timeout、bridge failure
三種情況都有處理（`os._exit`，跳過 atexit），**唯獨「學員自己寫錯」這個最常發生的
情況會落到保活分支**：印完正常 traceback → 進 atexit → `run_forever()` 永久阻塞。

### 實測 C（最嚴重，重驗新增）：學員自己的 bug

腳本：`bot.move_forward(1)` 之後 `print(names[5])` —— 一個標準的 `IndexError`。

```
[6.8s] 接下來這行是學員自己的 bug：
Traceback (most recent call last):
  File "f06.py", line 8, in <module>
    print(names[5])          # IndexError
          ~~~~~^^^
IndexError: list index out of range
```

**traceback 本身是完美的** —— Python 3.14 的彩色輸出、`~~~~~^^^` 精確指到
`names[5]`、行號正確。這正是上午教「看懂錯誤行數、錯誤原因」想要的效果。

**然後游標停住。實測 100 秒後行程仍在跑，被 timeout 砍掉。**

學員的認知是：「我按照老師教的讀懂了錯誤 → 然後電腦當了」。
**教學工具在它最該發揮作用的那一刻，緊接著製造了一個看起來像當機的畫面。**
而他沒學過 Ctrl-C。

### 實測 A（有寫 `bot.quit("bye")`）：

```
[  5.7s] connected
[  5.9s] LAST LINE OF MY SCRIPT — 從這裡開始學員什麼都看不到
（30 秒完全靜默）
[ 35.7s] 機器人已斷線，程式結束。
```

### 實測 B（沒寫 `quit()`，也就是**所有 quests 範例的形狀**）：

```
[6.80s] ready; script ends here (no quit, no run_forever)
（60 秒後仍在跑，被 timeout 砍掉）
```

行程永遠不會自己結束。這是刻意設計（讓學員不必記得寫 `run_forever()`），
但代價是「程式跑完了」和「程式卡住了」在畫面上**完全相同：什麼都沒有**。

**加成傷害**　學員的除錯循環變成：改一行 → 跑 → 等 6 秒連線 →
看動作 → **不知道跑完了沒** → 等一下 → Ctrl-C → 再改。
每輪 40 秒以上。一百分鐘裡跑不了幾次。

**能不能自救**　會 Ctrl-C，但不知道什麼時候該按。

**建議方向**（兩件事，都很小）

1. **出錯就不要保活。** excepthook 已經對三種情況做了 `os._exit`，
   把「學員自己的例外」加進去即可 —— 印完 traceback 就結束，
   和學員對「程式壞了會停下來」的直覺一致。
   （事件驅動腳本想保活的話，讓它自己寫 `run_forever()`，那本來就是它的用途。）
2. **正常跑完時印一行**，在 `run_forever` 開始 block 之前：

   ```
   （你的程式已經跑完了。機器人還在線上，按 Ctrl-C 結束。）
   ```

第 2 項是一行 `print`。**這兩項的成本效益比整份報告最高。**

> Ctrl-C 本身是好的：實測在真實終端機（pty）下按 Ctrl-C 會正確印出
> 「程式已結束。」並乾淨退出。
> **但**單獨對 Python 行程送 SIGINT（不含 node 子行程）時會卡住，
> 需要 SIGKILL——PyCharm 的停止鈕屬於哪一種我**沒有驗證**，見最後一節。

---

## P3-2　`get_block()` 和 `get_front_block()` 對「空氣」的回答相反

**位置**　`_commands.py:578-586` vs `631-651`

| 呼叫 | 空氣 | 沒載入 | 有方塊 |
|---|---|---|---|
| `get_block(x,y,z)` | `"air"` | `None` | 名字 |
| `get_front_block()` | `None` | `None` | 名字 |

`_commands.py:640-645` 的 docstring 自己承認了這個差異
（"Beware the difference from get_block"）。但學員不讀 docstring，
他寫的是：

```python
if bot.get_front_block() == "air":   # 永遠是 False
```

**建議方向**　名字裡就講清楚，或統一語意。
最小改動：`get_front_block()` 改名為 `has_block_in_front()` 回傳 bool +
`get_front_block()` 保持回傳名字但空氣回 `"air"`。營期前只改文件也行。

---

## P3-3　`get_height()` 不是高度

**位置**　`_commands.py:1106`（大小等級 1~5） vs `486`（`get_y` 才是高度）

同一個詞、相鄰的 API、兩個意思。而且 `get_height` 還是壞的（P0-3）。

**建議方向**　改名 `get_size()` / `set_size()`。
若 P0-3 選擇「刪掉」，這一則自動消失。

---

## P3-4　`look_block()` 長得像命令，其實是查詢

`look_at(x,y,z)` 是動作（轉頭）。`look_block()` 是查詢（回傳看到什麼），
**不會轉頭**。兩個都以 `look` 開頭，排在一起。

**建議方向**　`look_block()` → `get_aimed_block()`，和其他 `get_*` 一致。

---

# 營期後再說

---

## P4-1　`bot.` 有 172 個補全項，127 個用不到

**位置**　`bot.pyi`（3134 行）

實測（AST 解析 `class Bot`）：130 methods + 42 attributes = **172**。
學員 API 只佔 45，其餘 127 是 mineflayer 直通的 camelCase
（`putSelectedItemRange`、`openEnchantmentTable`、`elytraFly`、`writeBook`…）。

這也是 P0-6 / P1-1 的根因：為了讓直通可用，`__getattr__` 不能對未知名稱報錯。

**建議方向**（營期後）　把學員 API 和 mineflayer 全表分成兩個型別
（`Bot` 只有 45 個 + `bot.raw` 掛全部）。這是大改，不要在 8/4 前動。

---

## ~~P4-2　`minethon_reference/` 整份文件描述的是已經刪掉的 API~~　**✅ 已修，本條作廢**

初版針對 `minethon_reference/index.md` / `events.md` / `bot_methods.md`（共 728 行）
教 `@bot.on_spawn`、`@bot.on(BotEvent.CHAT)`、`BotHandlers`、`pip install minethon`
全部是已移除 API 的問題。

**重驗結果：整棵目錄已在 31ae3d6 刪除**（＝ 既有審查的 F-09）。
`git diff --stat` 確認三個檔案 -728 行。**不需要任何動作。**

---

## ~~P4-3　README 與實際結構的漂移~~　**✅ 幾乎全修，僅剩一項觀察**

初版列的五項漂移，重驗後逐條確認：

| 初版指出的 | 重驗（`dfd9564`） |
|---|---|
| `examples/demos/linear_actions/main.py` 幽靈連結 | ✅ 已移除（`grep` 為空）＝ F-08 |
| `src/minethon/_type_shells.py` 幽靈檔案 | ✅ 已移除 |
| `bot.py` 描述錯誤（說它是 runtime façade） | ✅ 已改成「純 re-export 自 `_bot_runtime`」 |
| `_bridge.py` 描述錯誤 | ✅ 已改成「bundled npm 版本 pin、bridge 生命週期」 |
| 結構圖漏 `_commands.py` / `_bot_runtime.py` / `_event_login.py` | ✅ 三個都補上了 |
| **README 沒提 `create_bot("g_swim")` 簡寫** | ✅ **已修**：README:50-59 專門一段，含 `~/.htsdg.json` 說明 |
| **`skills/minethon/` 沒提簡寫** | ✅ **已修**：SKILL.md:29-35、:108、:156（甚至補了「簡寫已經等過 spawn，`wait_spawn()` 那行可以刪」） |

**不需要任何動作。** 初版把「AI 會寫出學員填不出來的 `create_bot(host=...)`」
列為營期前必做 —— 那條路現在通了。

### 唯一殘留的觀察（不是漂移，是取捨）

`SKILL.md` 仍然把 **EventAdaptor 當成兩大入口之一**（:15、:21、:106-140 兩個完整範例）。
從 SDK 的角度沒錯，但對這批學員那是 0% 可達的語法（見 P2-1）。
AI 讀了這份 skill，面對「幫我寫個聊天時會回話的機器人」會產出 `class` + 繼承。

**建議方向**　`SKILL.md` 加一句話就好：
「若使用者是零基礎營隊學員（用 `create_bot("g_xxx")` 簡寫連線），
只用同步指令表，不要產出 `class` / `EventAdaptor` / `while` / `def`。」

---

## P4-4　忘記加括號 → 靜默無動作

```
bot.turn_left   ->  <bound method Commands.turn_left of <Bot object at 0x...>>
bot.dig         ->  <bound method Commands.dig of <Bot object at 0x...>>
```

沒有錯誤、沒有動作。這是 Python 通病不是 minethon 的錯，
但因為這個 API **全部都是副作用指令**，少一個括號就等於少一個動作，
而且和 P0 群（動作靜默失敗）的症狀完全一樣，兩者會互相掩護。

**建議方向**　教材裡明講。程式面無解（除非 `__repr__` 動手腳，不值得）。

---

## P5-1　連線節流：四十台電腦、同一個出口 IP

**實測**（同一台機器連續重跑）：

```
機器人被伺服器踢出："Connection throttled! Please wait before reconnecting."
```

vanilla 的 `connection-throttle` 預設是 **4000 ms／IP**。
如果電腦教室走同一個 NAT 出口，四十個學員的每一次重跑都在爭同一個 4 秒窗口。
學員每輪除錯要跑一次，**這會從頭吵到尾**。

而且它表現成「被踢」而不是「請稍等」，學員會以為自己的程式壞了。

**建議方向**　營期前確認伺服器的 `connection-throttle`
（建議設 0 或很小），或確認學員不共用出口 IP。
另外 `_on_kicked` 對這個字串特判一下，印
「連太快了，等三秒再跑一次。」

---

## P5-2　重複登入會踢掉前一個，而且會終止整支程式

**實測**（同一支腳本開兩個同帳號的 bot，也就是 `q07_stack` 的形狀）：

```
bot A: U100_bot
機器人被伺服器踢出：{...duplicate_login...}
機器人已斷線，程式結束。
```

兩個層面：
1. 學員上一次的程式沒關乾淨（因為 P3-1 行程不會自己結束），
   再跑一次就把自己踢掉。**這會很常發生。**
2. `_INTERRUPT` 是**模組層級**的全域狀態，`_stop_with_message` 呼叫
   `os._exit()`。所以在 `q07_stack` 那種多 bot 腳本裡，
   **任何一個 bot 斷線都會殺掉整支程式**，包括另外六個健康的 bot。

**建議方向**　(1) 靠 P3-1 的修正緩解。
(2) 多 bot 的情境營期前先確認 `q07_stack` 真的能跑完
（我沒有多個有效帳號可以驗證，見最後一節）。

---

## P5-3　安裝鏈

| 項目 | 風險 |
|---|---|
| Python **3.14+**（硬性） | 很新。`_commands.py:272` 用了 PEP 758 的 `except A, B, C:`，3.13 以下是**語法錯誤**。學員若誤用系統 Python，看到的是 `SyntaxError` 指著 lib 內部。 |
| Node.js **22+** | `setup.sh` 有檢查，訊息清楚 ✅ |
| `uv` | `setup.sh` 有檢查 ✅ |
| `~/.htsdg.json` | 沒有 → 錯誤訊息很好 ✅ |
| PyCharm SDK Paths | README 自己說 editable 安裝會讓整個專案被標成 excluded，要手動去 Project Structure 改。**四十台機器手動改一個 IDE 設定**是最容易全班卡住的一步。 |
| npm 預裝 | `setup.sh` 用 `require()` 預熱 JSPyBridge 的 alias cache，做法正確 ✅ |

**建議方向**　營期前在一台**乾淨**的示範機（和教室同型號、同 OS）
從零跑一次完整流程並計時。PyCharm 那一步如果能改成
「專案自帶 `.idea` 設定」或改用非 editable 安裝，就少一個全班停擺點。

---

# 我沒能驗證的部分

不做自我審查。以下是跑不動、看不懂、或直覺不對但講不清楚的。

## 跑不動 / 缺條件

1. **`dig()` 在允許破壞的世界裡的行為。**
   測試世界禁止破壞，所以我只證明了「被拒絕時回報成功」。
   我**沒有**證明它在正常情況下回報正確——不過從
   `digging.js:131` 的 `setTimeout(finishDigging, waitTime)` 看，
   它從頭到尾就沒有等伺服器確認，所以我對 P0-1 的機制判斷有把握，
   對「正常情況下也可能誤報」只是推論。

2. **grid-move provider 真正啟用時的路徑（`_walk_server_grid` / `_turn_server_grid`）。**
   `q.labfire.step` 的 trigger 在我測的時候沒有為這個帳號啟用，
   所以**整條伺服器權威移動與轉向的程式碼我一行都沒跑到**。
   那是 `_commands.py` 裡最複雜的一塊（sequence、ACK、wrap-around、
   scoreless fallback、tab-complete drain），也是關卡真正會走的路。
   **這一塊需要在真正的任務進行中重測。** 我對它的所有描述都是讀原始碼推的。

3. **`q07_stack` 的多 bot 疊羅漢。** 只有一個測試帳號，
   無法驗證七個 bot 同時在線的行為，也無法驗證
   「一個斷線殺掉全部」在實際關卡裡的後果有多大。

4. **`bot.action()` 在任務進行中真的生效。**
   只驗證了「不生效時完全靜默」。沒驗證生效時有沒有回饋
   （從程式碼看是沒有——`action()` 回傳 `None`，不讀任何狀態）。

5. **PyCharm 的實際體驗。** 我在終端機測的。
   補全清單長度（172）是從 `bot.pyi` 用 AST 算的，
   PyCharm 實際怎麼排序、怎麼分組、`ctrl+click` 跳到 `.pyi` 還是 `.py`，
   **都沒有驗證**。P3-1 提到的「停止鈕送 SIGINT 還是 SIGKILL」也沒驗證——
   這會決定學員按停止鈕之後 bot 是乾淨下線還是變成殭屍。
   **這一項我認為值得在營期前花十分鐘實測**，因為它影響 P5-2。

6. **Windows。** `pc_setup/setup.ps1` 的 BOM 處理、
   `__init__.py` 的 UTF-8 reconfigure、中文訊息在 cp950 終端機的顯示——
   我只有 macOS。教室大機率是 Windows。**這是我最大的盲區。**

7. **`dismount()` 用潛行鍵下車。** AGENTS.md 自己標明這是推測、
   只有 integration test 能驗。我沒有可以騎的載具，沒驗到。

## 直覺不對但講不清楚的

8. **`create_bot` 的 3.5 秒 spawn settle 是一個 magic number。**
   `_SPAWN_SETTLE_SECONDS = 3.5`，註解說是「post-login invulnerability window」。
   如果伺服器 lag 或 TPS 低，3.5 秒不夠會怎樣？如果夠了但學員的第一個動作
   還是被吃掉？我沒有辦法測，但「用固定 sleep 對抗伺服器狀態」
   通常是會在現場咬人的那種東西。它也貢獻了那 6 秒啟動時間的一半以上。

9. **`_grid_move_context()` 在沒有 provider 時每次移動都重掃一遍。**
   有 provider 時會 cache，沒有時不會（`:761` 只在 cache 失效時清掉）。
   我實測單次 `_enabled_trigger_objectives()` 是 0.01s，不成問題。
   但那是在一個 tab-complete 回應很快的伺服器上、只有我一個人連著。
   四十個 bot 同時每步都送 tab-complete request，我不知道會怎樣。
   **這個直覺我沒有數據支撐，但它讓我不安。**

10. **`_paced` 的 0.2 秒停頓乘上關卡規模。**
    `q10_labfire/state_2` 的迷宮是 35×9。DFS 走完加上轉向，
    輕鬆上千個動作 × 0.2s = **好幾分鐘**，而且中間畫面完全沒有輸出。
    學員會以為當掉了。我沒有實際跑過那個關卡所以不敢給數字，
    但 `instruction_sleep` 這個「讓學員看清楚」的設計，
    在演算法類關卡上可能是反效果。

11. **`atexit` + JSPyBridge callback table 的互動。**
    `_install_dismount_repair` 用 `On`（永久註冊）掛了兩個 callback，
    `_bot_runtime.py:223-227` 的 docstring 承認這會在 JSPyBridge 的
    callback table 留下永久項目（"that table is already permanently
    non-empty"），並論證「不是新的危害」。我在 P3-1 觀察到的
    「單獨 SIGINT 會卡住、需要 SIGKILL」**可能**就是這個
    （JSPyBridge 的 atexit 會在還有 callback 且 node 活著時空轉），
    但我**沒有把它證實**——我只證明了現象，沒證明因果。
    如果 PyCharm 的停止鈕走的是這條路，那 P3-1 就要升級成 P0。

12. **我審查的是落後 10 個 commit 的版本。**
    初版全程對著 `c2cd317` 寫，session 中途 repo 已更新到 `dfd9564`。
    我沒有在開始前 `git fetch`，這是流程失誤。
    重驗後確認那 10 個 commit **只動文件與 `_event_login.py`**，
    所有行為面發現與實測結果都還活著——**但那是運氣**。
    若那批 commit 動的是 `_commands.py`，整份報告會作廢。

13. **我對「下午目標」的推斷可能是錯的。**
    整份報告的權重都押在 `examples/quests/` 那五個關卡上。
    伺服器上有 `library` 和 `restaurant` 兩種我沒有樣本的任務。
    如果那兩個需要 `place()` / `hold()` / `find_block()`（我判定為噪音的那批），
    那我的「噪音／缺口」劃分就要重畫。
