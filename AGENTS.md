# AGENTS.md — minethon 開發指引

## 維護規則

- 本文件是目前專案的 ground truth。
- 發現實作與本文件不一致時，先修其中一邊，不要讓兩邊長期漂移。
- 記錄原則、公開 API 形狀、版本規則；不要把每個細節 API 簽名重複抄在這裡。

## 產品目標

minethon 是教學導向的 Python mineflayer SDK。

- 學生不需要先懂 Node.js、EventEmitter、asyncio
- 公開 API 以同步 callback 為主
- 補全與 hover 體驗由生成的 `bot.pyi` 承擔
- **已否決的方向**：早期的 async facade / registry 設計（`bot.raw.plugin()`、
  `wait_until_spawned()`、大量 plugin bridge）已放棄，因為它要求學生先懂 asyncio，
  違反上面第一條。不要再提案

第一驗收標準：

> 學生能一行一行看懂並自己仿寫。

## 事件 API

事件入口**只保留一種公開寫法**：繼承 `EventAdaptor` + `bot.bind(instance)`。

```python
from minethon import EventAdaptor


class Greeter(EventAdaptor):
    def on_spawn(self) -> None:
        bot.chat("hello")

    def on_chat(self, username, message, *_):
        if message == "quit":
            bot.quit("bye")


bot.bind(Greeter())
```

設計決策：

- 所有 decorator 形式（`@bot.on(...)`, `@bot.once(...)`, `@bot.on_<event>`, `@bot.once_<event>`）皆已移除——只剩 class-based handler
- `EventAdaptor` 子類別只需覆寫想處理的 `on_<event>`，其餘維持基底類別 no-op
- `bot.bind(handlers)` 走訪 `EVENT_ATTRIBUTE_MAP`，把每個被 override 的方法接到對應 mineflayer 事件
- `BotEvent` 仍以 `StrEnum` 對外公開，作為事件名稱常數（例如 logging、檢查）使用，但**不再**作為註冊參數
- event callback 參數以 upstream d.ts 為主；若 JS runtime 明確更嚴格或更少參數，由 `_normalize_handler` 自動補 `None` / 截斷

## 同步命令式 API（學員主要入口）

`IDEA.md` 描述的同步、阻塞、命令式 `Bot` 方法群，讓學員寫直線腳本（`bot.wait_spawn()` → `bot.move_forward(3)` → `bot.dig()`），不需要 callback / await。

設計決策：

- 實作在 `src/minethon/_commands.py` 的 `Commands` mixin；`Bot` 繼承它，所以方法直接掛在 `Bot` 上，未覆寫的名稱仍走 `__getattr__` 委託回 JS proxy
- 全部回傳原生型別（`tuple` / `str` / `bool` / `int`），不對學員暴露 `Vec3` / `Block` / `Item` 物件
- **移動與轉向：不依賴 pathfinder，有 provider 時為伺服器權威**。datapack 可用任意名稱的 trigger objective 宣告 grid-move provider，但 display title
  必須精確為 `minethon:grid_move:v1`、objective 必須放進同步 display slot，且只為已授權 bot enable trigger。
  `move_*` 從 `bot.scoreboards` 自動發現唯一 provider，整數 `blocks>1` 拆成逐格 trigger；若 client 收得到
  score，使用負 payload ACK，否則用 Brigadier completion 驗證 trigger 對本 bot 已 enable，並以 datapack
  重新 enable trigger 作 ACK。找不到 provider 時維持 `setControlState` + 位置輪詢 fallback，多個 provider
  則明確報錯。**fallback 也落在格線上**：整數格數且面向四正向時，瞄準的是目的地格子的**中心**
  （目前所在格 + 格數 ± 0.5），不是「從現在位置再走 N 格」。理由：放開控制鍵不會讓機器人停下，
  地面摩擦會多滑約 0.2 格（實測 `move_forward(3)` 落在 3.19 格、小數座標），逐格累積後整個座標
  模型會偏掉一格——`q10_labfire` 這種依賴格線的關卡就是這樣靜默算錯。每一步重新以「現在站的格子」
  為錨點，誤差就留在該步之內、不會累積。小數格數與斜向面向沒有格子可落，維持原本的距離語意。
  滑過頭跨到隔壁格時印一行（走不動則由既有的 stall timeout 負責，兩者互斥，同一次失敗只印一句）。轉向亦為伺服器權威：provider 存在時 `set_turn`（含 `turn`/`turn_left`/`turn_right` 委託路徑）
  把目標 yaw 量化到最近四正向，送出轉向碼 payload（方向碼＋4，即 5..8＝面向北東南西）並等相同交易的
  ACK；datapack 以帶絕對角度的 tp 執行，ACK 返回時 client/server yaw 保證一致。理由：client `look` 封包
  無送達保證（撞上伺服器 teleport confirm 窗口會被丟棄且 mineflayer 去重後不重送），會造成遊戲內朝向
  與 SDK 認知永久分歧。無 provider 時 `set_turn` 維持原本 client-side `look` fallback。SDK 不解析 group、帳號格式或關卡命名；快取只保存 objective 名，每次使用仍驗證 marker
  及本 bot 的 score／trigger 授權。同一 Bot 的 provider discovery／sequence／ACK 交易必須由 per-instance
  lock 序列化，避免 main 與 callback 共用 ACK channel
- 角度一律「度」；`get_height`/`set_height` 是大小等級 1~5。`get_height` 讀 entity `scale`
  屬性（伺服器回報），`set_height` **只委派給 `action("set height", level)`**、不寫本機。
  理由：舊版把 scale 寫進本機 proxy，而 `get_height` 讀同一個欄位，所以
  `set_height(4)` → `get_height()` 回 4，遊戲裡卻沒變大——學員用最自然的方式驗證，
  得到確認他是對的的答案。現在請求沒生效時 `get_height()` 會照實回傳舊等級。
  需要 datapack 實作 `<帳號>_set_height` trigger；沒實作就是無害 no-op。
  **驗證要在收窄之前做**：`int(3.9)` 是 `3`，會通過範圍檢查然後送出學員沒要求的
  等級。小數丟 `ValueError`，不無條件捨去——這與上面那條同一個道理，靜默送出
  別的結果比報錯難查
- **`bot.look_level()`**：把 pitch 歸零、保留 yaw。`dig`/`place`/`use`/`look_block` 全部
  作用在 `blockAtCursor`，而機器人出生時不是平視（實測 -52°～-68°，看著自己腳邊），
  這時 `dig()` 挖的是腳下地板。`create_bot` 在 spawn settle 之後自動呼叫一次；
  `set_turn` 刻意保留 pitch，所以轉向不會清掉低頭狀態。`dig()` 與 `look_at()` 會自己轉視線，
  之後需要平視就再叫一次
- **動作要能被檢查，不能靜默**：`dig()` 事後重讀方塊確認真的破了（mineflayer 的 `dig()`
  是 client 端 `setTimeout` 結束、從不等伺服器確認，所以保護區／任務未開始會回報成功）；
  `place()` 攔 `blockUpdate ... did not fire` 改印中文（那句英文的真正意思是「伺服器拒絕」）；
  `action()` 送出前用 `_enabled_trigger_objectives()` 比對，沒被啟用就印出目前可用的動作名
  （warn-and-send，不阻止送出——偵測不到不該擋掉有效動作）；`_walk` 撞牆的 stall timeout
  與非正數格數都改成印一行，不再靜默返回；`find_block` 遇到 registry 沒有的名字會印
  did-you-mean（`difflib`）
- `chat(obj)` 送一般公開聊天（`str(obj)`）；分組可見性由伺服器插件處理
- 與事件 API 並存：直線動作跑主執行緒，`EventAdaptor` + `bind` 處理反應，最後 `run_forever` 保活
- `chat` / `dig` / `dismount` / `drop` 四個名稱刻意覆寫 mineflayer 同名方法；generator 用 `_STUDENT_API_OVERRIDES` 在 `bot.pyi` 裡略過 upstream 版本，避免重複定義（改動這組名字時要同步改 generator 的那個 frozenset）
- **不新增 `bot.sleep`**：mineflayer 已用 `bot.sleep(bedBlock)`（上床睡覺）。暫停用既有的 `bot.wait(seconds)` 或直接 `time.sleep`；因為 mineflayer 的 physics tick 跑在 Node 端（`physics.js` 的 `setInterval`），Python 主執行緒 block 不會凍結遊戲內角色，控制狀態（sneak 等）也會維持
- **具名進階動作走 `bot.action(name, value=None)`——伺服器權威**：客戶端不模擬行為，只送 vanilla `/trigger <username>_<action>`（全小寫、空格/連字號→底線；`value` 為可選整數 payload），由關卡 datapack 驗證（執行者身分、任務狀態、目標存在）後代為執行或忽略。客戶端零副作用——不動方塊、不用物品，斷線也不會損壞地圖；trigger 未被伺服器 enable 時指令安全無效。名稱含不合法字元丟 `ValueError`；關卡專屬示範放 `examples/quests/<quest_id>/`
- `action()` 的 `<username>_<action>` 是既有公開契約；grid-move provider 則刻意採 scoreboard title 自動發現，
  兩者不共用命名推導。不要把 group／stage 或 provider objective 參數加進公開 `move_*` API
- **玩家互動走 `bot.use_player(username)`**：每次呼叫先讀 named player 的即時 entity 位置，以碰撞箱中心為絕對點送出與真實客戶端右鍵相同的 INTERACT_AT → INTERACT；不同高度不需學員自行算 yaw/pitch。玩家離線、不同世界或不在已載入範圍時丟 `PlayerNotFoundError`；實際可互動距離仍由伺服器的 entity-interaction range 驗證。
  **完全不呼叫 mineflayer 的 `activateEntity` / `activateEntityAt`**，而是 `lookAt(point, True)`
  對準碰撞箱中心，再用 `bot._client.write('use_entity', ...)` 依序送 INTERACT_AT 與 INTERACT
  （`mouse` 0／2，payload 照抄 `inventory.js`，hit vector 相對 entity 位置）。
  理由：那兩個 mineflayer 方法開頭是 `await bot.lookAt(point, false)`，非 force 的 look 等的是
  physics tick 發出的 `'move'`，而 `bot.on('mount', ...)` 會關掉 `shouldUsePhysics`（只有伺服器
  teleport 會重開），所以機器人一旦騎在別的實體上，該 promise 永不 settle，JSPyBridge 會在
  10 秒 per-call timeout 砍掉學生的程式。**「只在 `bot.vehicle` 為 null 時才呼叫」也不夠**：
  mount 通知可以落在檢查之後、它那次 look 還在 await 的空檔；**先 force 對準也不夠**：
  mineflayer 是在呼叫當下才用 `entity.position` 與 `bot.entity.position` 重算角度，任何一邊在
  我們取樣後被封包更新就又會 await。自己送封包是唯一能讓「所有路徑都不可能 await look」的
  做法——SDK 這層要先把問題擋掉，不要留窗口給學生踩。
  那個 forced `lookAt` **只負責讓 SDK 自己的 `get_yaw`/`get_pitch` 與呼叫者的意圖一致**，不要
  期待它在遊戲內轉頭：競賽伺服器上客戶端 `look` 沒有送達保證（撞上伺服器 teleport confirm
  窗口會被丟棄、mineflayer 去重後不重送），這正是 `set_turn` 改成 provider 伺服器權威的原因；
  而 provider 目前沒有「任意角度 look」的 payload，所以互動前的可見轉頭暫時做不到。已實機
  確認：單隻機器人也不會轉頭，加大緩衝無效（封包送出去了，是伺服器丟掉）。
- **每個行為指令收尾有 `instruction_sleep` 停頓**（預設 0.2s），讓學員逐行看出動作。實作是 `_commands.py` 的 `_paced` decorator，只掛在「葉節點」動作上（`turn_left`→`turn`→`set_turn` 只有 `set_turn` 被 pace，避免重複停頓）；讀取類指令（`get_*`/`find_*`/`is_*`）不 pace；`sneak` 也刻意不 pace，讓 sneak 開關的 toggle 迴圈不被延遲拖慢。`create_bot(instruction_sleep=0.1)` 調整間隔、`bypass_instruction_sleep=True` 關閉（設成 0）；值存在 `Bot._instruction_sleep`
- **物理模擬預設開著，不需要也不要去「啟動」它**：mineflayer 的 `physicsEnabled ?? true`（`physics.js`）讓自然下墜、方塊碰撞、水/岩漿、梯子本來就在跑，模擬迴圈是 Node 端的 `setInterval`，minethon 沒有任何地方覆蓋它。要求「開啟物理」時先確認是不是下面兩個已知洞之一，不要加 `physicsEnabled` 選項
- **mineflayer 在 1.9+ 伺服器上不會發出 `dismount` 事件**（上游 bug，minethon 自己補）。三個 emit 點：`attach_entity` 要求 `vehicleId === -1`（1.9 之後載具改走 `set_passengers`，這條推測只剩拴繩會用，**未在 repo 內驗證**）；`set_passengers` 要求 `passengers.includes(bot.entity.id) && entityId === -1`，但下車時送來的**預期**是載具 id ＋已移除 bot 的乘客列表（這是整套修正的大前提，只有 integration test 驗得到）；`entityGone` 的事件發在 `bot` 上（`entities.js:302`），handler 卻掛在 `bot._client`（`:812`）——**emitter 不同，那條路是死的**（這條純 source，確定）。後果是 `bot.vehicle` 下車後永遠不清，`is_riding()` 一旦騎過就恆真。
  `create_bot` 因此裝 `_install_dismount_repair`，三層修正：
  1. **下車** — 在 `bot._client` 上聽 `set_passengers`，「我現在的載具送了一份不含我的乘客列表」就清掉 `bot.vehicle` 並補發 `dismount`，讓 `EventAdaptor.on_dismount` 真的會觸發。與 mineflayer 自己那條分支互斥（它要求 bot **在**列表內），不會重複觸發。同一 handler 也負責「同 tick dismount+remount」的回填：Python callback 是排隊逐一執行的，JS 狀態早已定案在「在車上」，所以看到「我在名單內但 `bot.vehicle` 是 None」時要補回去
  2. **重生（死亡／換維度）** — 在 `bot` 上聽 `respawn`（`health.js` 直接由 clientbound respawn 封包發出）清掉，並補發同一個 `dismount` 事件，讓「騎馬時死掉」跟正常下車對學員是一樣的。「這兩種情況不會送 `set_passengers`、`entity_destroy` 也不涵蓋舊維度的實體」是**推測，未在 repo 內驗證**；但重生後的機器人不可能還在騎，所以就算伺服器另外有送，第 1 條也是冪等的，這層不會有反效果
  3. **載具在腳下消失** — 由 `is_riding()` 在讀取端檢查 `vehicle.isValid`（`entity_destroy` 仍會翻這個旗標，`prismarine-entity` 建構時是 `true`）。判斷式是 `is not False` 不是 `bool(...)`：bridge proxy 對不存在的 JS 屬性回 `None`，把 `None` 當成「沒在騎」是錯誤的失敗方向。
     刻意**不**掛 `On(bot, 'entityGone')`（那是正確的 emitter，掛得起來，而且能一併補發 `dismount`）：`entityGone` 每有實體離開視野就觸發，等於每次都要在 callback thread 上讀一次 `bot.vehicle`；讀取端檢查只在學員真的呼叫 `is_riding()` 時才多一次 bridge read（實測 0.05→0.11 ms/call），不會隨場上實體數量成長。代價是 despawn 這條路不會發出 `on_dismount`——需要的話再換
  
  兩個實作陷阱：listener 必須掛在 `bot._client`（協定封包）而不是 `bot`（事件）——掛錯 emitter 正是上游踩的坑；packet payload 必須用 **subscript** 取值（`packet["entityId"]`）不能用屬性，因為 protodef 產生的是 plain JS object，JSPyBridge 的 `pyi.js` 只對 `constructor.name` 不是 `Object`/`Array` 的值配 ffid，所以它是 by-value 的 Python `dict` 而不是 Proxy。
  `bot.entity.vehicle` 與 `vehicle.passengers` 仍是髒的（mineflayer 只走新乘客名單），SDK 內部沒有讀者，`bot.pyi` 的 hover 已加警告要學員改用 `is_riding()`。
  `_commands.py` 另外**完全取代**（不是包一層）mineflayer 的 `dismount()`，兩個理由：(1) 它在 1.21.3+ 按錯鍵——vanilla 是用潛行鍵下車，legacy `steer_vehicle` 的 `jump` 欄位是個 bitmask、`0x02` 位元就是 unmount，移植到 `player_input` 時把**欄位名**當成布林旗標搬過去，變成送出跳躍。minecraft-data 1.21.4 的 flags 是 `[forward, backward, left, right, jump, shift, sprint]`，而 `physics.js` 正是用 `player_input {shift: state}` 實作 sneak，所以改走 `sneak(True)` → 停 0.1s → `sneak(False)`。注意 `setControlState` 在值沒變時直接 return，所以本來就在潛行的機器人要先放開再按，事後再把學員原本的狀態放回去；1.21.3 以前 sneak 走的是 `entity_action`（不是下車輸入），那條路直接照抄 mineflayer 的 `steer_vehicle` payload。(2) 它在沒騎乘時 `bot.emit('error', 'dismount: not mounted')`，而 minethon 對任何 bot `error` 都 `os._exit(1)`——完全不呼叫它才能真的關掉這條路，只加 `if is_riding()` 守衛會留下 callback thread 可以插隊的窗口（同 `_write_use_entity` 的理由）。`_STUDENT_API_OVERRIDES` 同步加了名字。跟 mixin 其他方法一樣是 blocking：送出輸入後輪詢 `is_riding()`，2 秒沒下車就丟 `MinethonError`（不要安靜返回——「潛行鍵能下車」正是這整條最沒被驗證的假設）。但**在 callback thread 上不輪詢**：結束條件由 `_clear_stale_vehicle` 設定，而 JSPyBridge 所有 Python callback 共用一條 executor thread，handler 裡等於自己卡住唯一能放行的執行緒。**「潛行鍵能下車」是推測，要靠 integration test 驗。**
  「下車真的會送 `set_passengers`」這個大前提**只有 integration test 能驗**：`tests/integration/test_vehicle_dismount.py`（上車→下車→`is_riding()` 轉 False ＋ `on_dismount` 有觸發）。單元測試全部是照這個形狀假設寫的，改動這塊時務必連 integration 一起跑
- **被攻擊瞬間位置變 NaN（mineflayer 4.37.0 ↔ minecraft-data 配對斷層，minethon 自己補）**：
  entities.js 的 `entity_velocity` handler 把 1.21.2+ 的巢狀 `velocity`（vec3i16）形狀藏在
  `supportFeature('entityVelocityIsLpVec3')` 後面，但它實際安裝到的 minecraft-data（≤3.110.x）
  從未收錄這個 feature——查詢恆為 false，走 legacy 分支讀 `packet.velocityX`（undefined），
  `fromNotchVelocity(Vec3(undefined))` 把 NaN 寫進 `entity.velocity`。對機器人自己，這個封包
  正是被打的 knockback：下一個 physics tick 把 NaN 積分進 `bot.entity.position`（NaN+x=NaN），
  JSPyBridge 的 JSON 層把 NaN 序列化成 null，之後 Python 端所有位置讀取都是 None——學員的
  `move_forward()` 在被打的瞬間死於 `float(None)`，之後 `get_pos()` 也全壞。`create_bot` 因此裝
  `_install_velocity_repair`：用 `eval_js` 在 node 端補一個 `entity_velocity` listener 重新解析
  巢狀形狀（每包零 bridge 往返——理由同 `is_riding` 拒掛 `entityGone`）；EventEmitter 同步派發、
  我們的 listener 排在 mineflayer 之後，physics interval 不可能在兩者之間觀察到 NaN。守衛是
  「`velocityX` 缺席且 `velocity` 存在」：舊平面形狀（<1.21.2 伺服器）不動，健康配對（新
  minecraft-data 已有 feature）只是重寫同值，冪等無害。上游已修（minecraft-data master 已加
  feature、mineflayer master 移除 gate 直接讀巢狀），bundled mineflayer pin 升過 4.37.x 後此
  修補可移除，留著也無害。JS 邏輯由 `tests/integration/test_velocity_repair_js.py` 驗證——該測試
  只需要 node，不需要 Minecraft 伺服器
- **已知洞 1：騎乘後物理可能永久關閉（尚未修，修之前必須先實測）**。`physics.js` 有 `bot.on('mount', () => { shouldUsePhysics = false })`，唯一設回 true 的地方是 clientbound `position` handler。前提未驗證：vanilla 下車時伺服器很可能本來就會 tp 玩家（`Entity#dismountTo` → `ServerPlayer` teleport），若成立則物理自己就復原，整個修都是多餘。合成 `position` 封包重新武裝是可行手段，但會偷走 `physics.js` 死亡後 2 秒內那個 one-shot 的 respawn 延遲，有 `Invalid move player packet` 踢線風險，所以先量再修
- **已知洞 2：推動碰撞（被其他實體推開）根本沒實作**：`prismarine-physics` 只建方塊與液體的 AABB，完全沒有 entity-vs-entity collision；vanilla 這塊是 client 權威，所以伺服器也不會代勞。要有就得自己在 Node 端寫，且會與 datapack grid-move 的 server-authoritative ACK 打架——現階段刻意不做
- 完整方法清單與中文 hover 見 `src/minethon/bot.pyi`；AI 替學員寫程式用的說明見 `skills/minethon/`

## IDE 與型別層

- `src/minethon/bot.pyi` 是 IDE completion 的主要來源，必須由 `scripts/generate_stubs.py` 生成
- generator 的 source of truth 優先讀 `.venv/.../javascript/js/node_modules/` 的實際安裝版本；缺少時才 fallback 到 repo vendored `src/mineflayer/js/node_modules/`
- 中文 hover docstring 直接住在 `bot.pyi` 內；regen 時從現有 `.pyi` 讀回 docstring 再注入，所以人工編輯不會被沖掉（過去的 `docs/stubs_zh_tw.md` 已停用並刪除）
- `src/minethon/_events.py` 由 generator 生成，提供 `BotEvent`
- `src/minethon/models/` 提供可 import 的公開型別 shell，方便使用者寫 annotation；實際成員面仍以 `bot.pyi` 為準

## 公開模組分層

| 模組 | 角色 | 為什麼這樣切 |
| --- | --- | --- |
| `__init__.py` | 使用者入口 | re-export `create_bot`、`Bot`、`BotEvent`、`EventAdaptor`、公開錯誤類 |
| `bot.py` | 公開 module 名 | 純 re-export 自 `_bot_runtime`；維持薄殼，`from minethon.bot import Bot` 不會把 runtime 細節帶進 IDE 視野 |
| `_bot_runtime.py` | 真正的 runtime façade | `class Bot(Commands)`、`__getattr__` JS proxy 委託、`bind()` 事件分派、plugin loading、version pin guard。從 `bot.py` 拆出，避免 `.py` + `.pyi` 雙重 `class Bot` 在 IDE 解析時產生衝突源 |
| `_commands.py` | 同步命令式學員 API | `Commands` mixin（見上方「同步命令式 API」段） |
| `_event_login.py` | `create_bot("g_swim")` 簡寫 | 讀 `~/.htsdg.json` 的組別/電腦編號 → 推導帳密＋補上賽事伺服器預設值。刻意獨立成檔：賽後要把它連同 `_DEFAULTS` 一起抽掉，minethon 本體不該綁死某一屆營隊 |
| `bot.pyi` | 生成的型別面 | `minethon.bot` 模組的 sole `class Bot` declaration |
| `models/` | 可 import 的型別 shell | 給使用者寫 annotation 用 |
| `errors.py` | 使用者可見的錯誤類 | |

> 補充：PyCharm 的 completion popup 對 Python class member 預設右側顯示 owner class，不顯示型別 annotation — 這是 PyCharm 對 Python 的 UI 設計（純 `class Foo: a = 10` 也是這樣），跟 stub / .pyi 結構無關。要看完整型別請按 `Ctrl+J` (Quick Documentation) 或 hover；assign 後變數型別會正確顯示。

## Source-Verified 原則

所有設計決策必須有 mineflayer / plugin 原始碼依據。

主要來源：

- mineflayer d.ts：`.venv/lib/python3.14/site-packages/javascript/js/node_modules/mineflayer--*/index.d.ts`
- mineflayer JS：`.venv/lib/python3.14/site-packages/javascript/js/node_modules/mineflayer--*/lib/**/*.js`
- pathfinder d.ts：`.venv/lib/python3.14/site-packages/javascript/js/node_modules/mineflayer-pathfinder--*/index.d.ts`

禁止：

- 只看 README 就定義 Python API
- 用 sleep / monkey-patch 硬繞 bridge 問題
- 在沒有 source 依據時擅自把 runtime 行為講成既定契約

## 版本規則

- Python 3.14+
- Node.js 22+
- bundled / pinned npm packages：
  - `mineflayer`
  - `vec3`
  - `mineflayer-pathfinder`
- 對 bundled package，`bot.load_plugin(...)` / `bot.require(...)` 可省略版本；
  其他 npm 套件**必須**顯式版本（`bot.load_plugin(name, "x.y.z", export_key=...)`）
- Python 端的 `javascript` (JSPyBridge) 套件在 `pyproject.toml` 用 minor 級 ceiling 鎖（目前 `>=1!1.2.6,<1!1.3`）。理由：minethon 依賴 `On`/`Once` 在 pinned runtime **不注入 emitter**（`needsNodePatches` 只在 Node 14/15 成立）與 Promise `await`-before-return 行為，這兩件事是實作細節不是正式契約；升 minor 前要先跑 `./scripts/format.sh` 與 integration smoke。

理由：

- 避免 JSPyBridge 在 runtime 偷裝 latest
- 讓教學範例與學生環境可重現

## Plugin scope

- **內建 typed / documented plugin 只有 `mineflayer-pathfinder`**（注意 bundled ≠ typed：
  `vec3` 也是 bundled 但沒有 typed façade）
- 其他 plugin 不提供 typed façade，走上面版本規則那條顯式版本的路

## Callback thread 規則

- 所有 event handler 跑在 JSPyBridge callback thread
- handler 內不要 blocking
- pinned runtime 不注入 emitter（理由見「版本規則」的 ceiling 鎖那條）；`_normalize_handler` 的 emitter 偵測僅靠 `_REAL_ARGC` 已知表與 emitter identity，多餘參數一律**從尾端截斷**（短簽名 handler 拿到的是最前面的參數）
- handler 內未捕捉的例外由 `_normalize_handler` 攔截：印友善訊息＋traceback 後略過該次事件，不回流 JS（避免 unhandled rejection 殺死 node 進程）

## 錯誤處理

至少要維持下列公開錯誤類存在：

- `MinethonError`
- `NotSpawnedError`
- `PlayerNotFoundError`
- `PluginNotInstalledError`
- `VersionPinRequiredError`

使用者訊息優先告訴下一步該做什麼。

登入失敗（帳密錯誤）不可外洩 yggdrasil 原始 stack。`create_bot` 註冊 `Once(bot, 'error')` →
`_on_login_error`：偵測 `invalid credentials` / `invalid username or password` 時印
「找不到此任務。請檢查任務名稱是否正確，或是任務是否開放」再 clean exit（`_stop_with_message`
→ 關 node bridge + `os._exit`）；同時也解掉會永久卡住的 `wait_spawn`（登入失敗 `spawn`
永不觸發）。註冊任一 `error` listener 也讓 mineflayer 的 EventEmitter 不再 throw 原始錯誤。

其他失敗路徑的規則：

- exit code：正常結束（quit / 伺服器關閉 session）為 0；失敗（登入錯誤、bridge 逾時/斷線）
  為 1，讓 shell / CI 能分辨。`_stop_with_message(code=...)` 統一處理並先 flush 輸出。
- `create_bot` 另註冊 `Once(bot, 'kicked')` 印出被踢原因（版本不合、白名單、任務踢線），
  否則 `logErrors=False` 下原因會被整條吞掉。`reason` 是 protodef NBT 不是字串，
  一定要走 `component_plaintext()` 攤平（`str()` 會印出 Python dict repr，真正的訊息
  埋在 `{'type': 'compound', 'value': {'translate': ...}}` 裡）；`Connection throttled`
  另外特判——vanilla 對每個 IP 有重連節流，整間教室共用一個 NAT 出口會一直撞到，
  而「被伺服器踢出」這句讀起來像學員自己的程式壞了。
- **學員自己的例外要結束程式，不要保活。** excepthook 對 Ctrl-C／per-call timeout／
  bridge failure 都 `os._exit`，唯獨「學員寫錯」這個最常發生的情況以前會落到
  `atexit` 的 `run_forever()`，變成「印完一份漂亮的 traceback 之後畫面永遠不動」
  （實測 100 秒仍未結束）。學員沒學過 Ctrl-C，那個畫面等於當機。現在 `previous()`
  印完 traceback 後接 `_stop_with_message(_SCRIPT_FAILED, code=1)`。
  事件驅動腳本要保活就自己呼叫 `run_forever()`，那本來就是它的用途。
- **正常跑完也要說一句。** `atexit` 註冊的是 `_announce_then_keep_alive`（不是
  `bot.run_forever` 本身），先印「程式已經跑完了，機器人還在線上，按 Ctrl-C 結束」。
  沒有這行時「跑完」和「卡住」在畫面上完全一樣（都是什麼都沒有），而所有 quests
  範例都沒寫 `quit()` / `run_forever()`。只有隱式路徑會印。
- **`createBot` 之前先探測 TCP 埠**（`_require_reachable`）。mineflayer 一回傳就 ping
  伺服器，ping 失敗會在 `loader.js` 轉發成 bot `error`，而我們的 listener 要等下一個
  bridge round-trip 才裝上——連線被拒剛好落在那個空隙，Node 的 EventEmitter 直接
  throw，node 進程死掉，學員看到 77 行 `AggregateError [ECONNREFUSED]`，最後那行
  「連線發生錯誤:」冒號後面還是空的（bridge 已死，讀不到 error 物件）。實測 10.5 秒。
  與其去贏那個 race，不如直接回答「有沒有人在聽」——改完是 1 行、0.3 秒。
  TCP 之後的失敗（帳密、版本、白名單）照舊走 `error` / `kicked`。
- JSPyBridge 的 per-call 逾時（`Call to 'X' timed out.`）由 excepthook 轉成友善訊息後
  結束（逾時後的遲到回應會毒化 bridge IO loop，不硬撐）。
- `bind()` 對「拼錯的 `on_xxx`（不對應任何事件）」印提醒，不再靜默忽略。
- `bot.pathfinder` 未載入時（真實 bridge 回 `None`）拋 `PluginNotInstalledError`
   並附下一步指引。

**打錯名字的拼字建議（`Bot._reject_misspelling`）。** JSPyBridge 對 JS 端不存在的
屬性**回 `None` 而不是丟 `AttributeError`**（`bridge.js` 對 undefined 答 `'void'`），
所以 `bot.mvoe_forward(3)` 以前是 `TypeError: 'NoneType' object is not callable`
（沒說是哪個名字打錯），`bot.usernaem` 更是安靜地變成 `None`。課程只教「看懂錯誤
行數、錯誤原因」——行數對，原因完全沒有。現在 `__getattr__` 讀到 `None` 時比對合法
名稱，close match 就丟 `AttributeError` 附 did-you-mean（`difflib`，大小寫不敏感）。

兩個關鍵約束，改這塊時不要退回去：

- **合法名稱要用生成的 `_members.py`（`BOT_MEMBERS`），不能只用 live proxy 的 key。**
  `list(bot_proxy)` 只給 JavaScript 的 *own enumerable* key，所以「文件有、但 JS 還沒
  賦值」的屬性不在裡面——`bot.vehicle` 在第一次上車前就是 `undefined`。第一版用 proxy
  key 當清單，結果沒騎過車的機器人讀 `bot.vehicle` 會被判定成 `moveVehicle` 的錯字。
  `_members.py` 由 `generate_stubs.py` 從最終的 `bot.pyi` AST 產生（涵蓋 mineflayer
  面 ＋ 學員 API），proxy key 仍然 union 進來以涵蓋 plugin 執行期加的東西。
  順帶：`bot.vehicle` 是 runtime 真實存在但 mineflayer `index.d.ts` **從未宣告**的屬性，
  所以它由 `_STUDENT_API_STUB` 手動補進 `bot.pyi`。
- **只在有 close match 時才丟。** 找不到相近名稱就照舊回 `None`：誤判會弄壞本來能跑的
  程式，比少一個提示糟。合法但確實是 `None` 的屬性（`bot.entity` spawn 前、
  `bot.heldItem` 空手、`bot.vehicle` 沒騎車、`bot.targetDigBlock` 沒在挖）都必須安靜通過。
- **走訪外部物件一律用 `bounded_keys()`。** 只實作 `__getitem__` 的物件（正是模擬
  JS proxy 的方式：不存在的 key 回 `None` 而不是丟 `IndexError`）滿足 Python 的舊式
  迭代協定，直接 `for x in obj` 會無限要 index 0、1、2……。這不是假設性問題：它曾經
  讓整個 test suite 卡死。`bounded_keys` 要求 `__iter__` 並加上數量上限。

## 檢查指令

一鍵跑完（regen stubs → format → lint → type-check → test）：

```bash
./scripts/format.sh            # 寫回格式修正
./scripts/format.sh --check    # 只檢查不寫入（CI 模式）
```

對應的個別指令（與 `format.sh` 內部順序相同）：

```bash
uv run python scripts/generate_stubs.py
uv run ruff format src scripts tests
uv run ruff check src scripts tests
uv run pyright src/
uv run pytest -m "not integration" --tb=short -q
uv run python scripts/check_stubs.py        # TS d.ts ↔ bot.pyi drift gate
```

Integration smoke（bridge↔mineflayer 實連路徑，JSPyBridge / bundled npm 升版前必跑）：

```bash
uv run pytest -m integration   # 需要可連線的 Minecraft 伺服器
```

預設連 `localhost:25565`（offline mode），可用 `MINETHON_IT_HOST` /
`MINETHON_IT_PORT` / `MINETHON_IT_USERNAME` 覆寫；伺服器連不上時測試會
skip（不會卡死）。預設的 `pytest -m "not integration"` 與 CI 不會執行它。

`scripts/parse_dts.py` 是 TS 解析器的 stable public surface（目前 façade
re-export 自 `generate_stubs.py`）；`scripts/check_stubs.py` 用它比對
mineflayer d.ts 跟現存 `bot.pyi` 的 class member 列表，缺項會 exit 1。

`src/mineflayer/` 是 legacy / scratch 區，不納入目前 package 的 lint 與 pyright 範圍。

## Lint 策略

- `[tool.ruff.lint]` 全域 `select = ["ALL"]`，只對「全案都不適用」的規則做全域忽略。
- 針對情境的豁免一律走 `[tool.ruff.lint.per-file-ignores]`，不要擴張全域 `ignore`。
- **現有的 per-file 區塊與逐條 rationale 直接看 `pyproject.toml`**，不在這裡複製一份。
  之前這裡有一份摘要清單，已經漂移（漏了 `_commands.py`），而 `pyproject.toml`
  的註解本來就寫得更完整。
- 新增豁免時：先嘗試用更具體的規則號（`PIE790`、`RUF022`）而不是整個家族（`PYI`、`RUF`）；只在「整個家族都不適用」時才用前綴。
- generator 輸出要符合 ruff 的規則，`format.sh` 跑完必須 idempotent（第二次跑不再變動）。

## 未完成

已完成的項目不列在這裡——本文件其餘各節描述的就是現況。

- [ ] 自家 collection wrapper（`bot.players` / `bot.entities` 目前仍是 bridge proxy）
- [ ] 更完整的 user-facing error wrapping（最優先的一條見「錯誤處理」段末：
      打錯方法名字時的 `'NoneType' object is not callable`）
- [ ] 除 pathfinder 以外的 plugin typed 支援
