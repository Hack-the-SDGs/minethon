# Bot 屬性與方法

`Bot` 物件由 `create_bot()` 回傳，所有未列出的 mineflayer 屬性也可以直接存取（透過 JS proxy fallback）。

---

## 連線 & 狀態屬性

| 屬性 | 型別 | 說明 |
|------|------|------|
| `bot.username` | `str \| None` | 機器人使用者名稱 |
| `bot.version` | `str` | 完整版本字串，例如 `"1.20.1"` |
| `bot.majorVersion` | `str` | 主版本，例如 `"1.20"` |
| `bot.protocolVersion` | `str` | 協定版本號 |
| `bot.entity` | `Entity \| None` | 機器人自己的實體（含位置、速度） |
| `bot.players` | `Mapping[str, Player]` | 線上玩家清單，key 為使用者名稱 |
| `bot.entities` | `Mapping[str, Entity]` | 視野內所有實體，key 為 entity ID |
| `bot.spawnPoint` | `Vec3` | 重生點座標 |
| `bot.game` | `GameState` | 遊戲模式、維度、難度 |
| `bot.settings` | `GameSettings` | 視野距離、主手等用戶端設定 |
| `bot.physics` | `PhysicsOptions` | 物理參數 |
| `bot.physicsEnabled` | `bool` | 物理模擬是否啟用 |
| `bot.world` | `object` | prismarine-world WorldSync |
| `bot.registry` | `object` | minecraft-data 資料庫 |
| `bot.time` | `Time` | 世界時間（age、day、timeOfDay） |

---

## 生命體徵

| 屬性 | 型別 | 說明 |
|------|------|------|
| `bot.health` | `float` | 血量 0–20 |
| `bot.food` | `float` | 飢餓值 0–20 |
| `bot.foodSaturation` | `float` | 飽和度 |
| `bot.oxygenLevel` | `float` | 氧氣 0–20（水中才會下降） |
| `bot.experience` | `Experience` | 經驗值（level、points、progress） |
| `bot.isSleeping` | `bool` | 是否在睡覺 |

---

## 物品 & 背包

| 屬性 | 型別 | 說明 |
|------|------|------|
| `bot.inventory` | `Window` | 玩家背包視窗 |
| `bot.currentWindow` | `Window \| None` | 目前開啟的容器視窗 |
| `bot.heldItem` | `Item \| None` | 主手手持物品 |
| `bot.quickBarSlot` | `float` | 快捷列槽位 0–8 |
| `bot.usingHeldItem` | `bool` | 是否正在使用手持物品 |

---

## 其他屬性

| 屬性 | 型別 | 說明 |
|------|------|------|
| `bot.isRaining` | `bool` | 是否下雨 |
| `bot.thunderState` | `float` | 雷暴強度 |
| `bot.controlState` | `ControlStateStatus` | 各方向鍵狀態 |
| `bot.chatPatterns` | `list[ChatPattern]` | 已註冊的聊天 pattern |
| `bot.scoreboards` | `dict[str, ScoreBoard]` | 所有記分板 |
| `bot.teams` | `dict[str, Team]` | 所有隊伍 |
| `bot.tablist` | `Tablist` | tab 清單（header/footer/players） |
| `bot.targetDigBlock` | `Block \| None` | 目前正在挖的方塊 |
| `bot.creative` | `creativeMethods` | 創意模式專屬操作 |
| `bot.pathfinder` | `Pathfinder` | Pathfinder（需先呼叫 `load_plugin`） |

---

## 生命週期

### `bot.run_forever()`
阻擋 main thread，直到機器人斷線或 Ctrl-C。通常是腳本最後一行。

```python
bot.run_forever()
```

### `bot.end(reason=None)`
立刻關閉連線。

### `bot.quit(reason=None)`
先送出離線封包再關閉連線（比 `end()` 更乾淨）。

### `bot.respawn()`
死亡後重生。

---

## 聊天 & 溝通

### `bot.chat(message)`
發送公開聊天訊息，超過 256 字元會自動拆行。

```python
bot.chat("Hello, world!")
```

### `bot.whisper(username, message)`
私聊指定玩家。

### `bot.awaitMessage(*patterns)`
等待符合 pattern 的訊息後回傳訊息字串（阻擋式，不建議在 handler 內呼叫）。

### `bot.addChatPattern(name, pattern, options=None)`
新增自訂聊天 pattern，回傳 ID。

### `bot.removeChatPattern(name_or_id)`
移除已新增的 pattern。

### `bot.tabComplete(str_, assume_command=None, ...)`
取得 tab 補全建議，回傳 `list[str]`。

---

## 移動 & 控制

### `bot.setControlState(control, state)`
按下/放開方向鍵。

```python
from minethon.models import ControlState  # 僅 annotation 用

bot.setControlState("forward", True)   # 開始前進
bot.setControlState("forward", False)  # 停止前進
bot.setControlState("jump", True)      # 跳躍
```

可用的 control 字串：`"forward"` `"back"` `"left"` `"right"` `"jump"` `"sprint"` `"sneak"`

### `bot.getControlState(control) -> bool`
查詢目前按鍵狀態。

### `bot.clearControlStates()`
一次放開所有方向鍵。

### `bot.look(yaw, pitch, force=False)`
設定視角（弧度）。

### `bot.lookAt(point, force=False)`
轉頭看向指定 Vec3 座標。

```python
bot.lookAt(target.entity.position)
```

### `bot.mount(entity)`
騎上載具實體（馬、船、礦車）。

### `bot.dismount()`
下載具。

### `bot.moveVehicle(left, forward)`
控制已騎乘的載具移動。

### `bot.elytraFly()`
展開鞘翅飛行。

---

## 方塊互動

### `bot.blockAt(point, extra_infos=True) -> Block | None`
取得指定座標的方塊。

```python
import math
pos = bot.entity.position.floored()
block_below = bot.blockAt(pos.offset(0, -1, 0))
```

### `bot.blockAtCursor(max_distance=256, matcher=None) -> Block | None`
取得視線前方的方塊。

### `bot.blockInSight(max_steps, vector_length) -> Block | None`
沿視線方向掃描方塊。

### `bot.canSeeBlock(block) -> bool`
判斷機器人能否看見方塊（視線無遮蔽）。

### `bot.findBlock(options) -> Block | None`
在附近搜尋一個符合條件的方塊。

```python
chest = bot.findBlock({
    "matching": 54,       # 方塊 ID（或 list / callable）
    "maxDistance": 32,
})
```

### `bot.findBlocks(options) -> list[Vec3]`
搜尋多個符合條件的方塊，回傳座標列表。

### `bot.canDigBlock(block) -> bool`
判斷是否可挖此方塊。

### `bot.dig(block, force_look=None)`
挖掘方塊（阻擋到挖完，完成後觸發 `DIGGING_COMPLETED`）。

```python
target = bot.blockAtCursor()
if target and bot.canDigBlock(target):
    bot.dig(target)
```

### `bot.stopDigging()`
中止正在進行的挖掘。

### `bot.digTime(block) -> float`
計算挖掘此方塊需要的毫秒數。

### `bot.placeBlock(reference_block, face_vector)`
在指定面放置手持方塊。

---

## 物品 & 裝備

### `bot.setQuickBarSlot(slot)`
切換快捷列槽位（0–8）。

### `bot.equip(item_or_id, destination)`
裝備物品到指定部位。

```python
bot.equip(sword_item, "hand")
bot.equip(helmet_item, "head")
```

`destination` 可為：`"hand"` `"off-hand"` `"head"` `"torso"` `"legs"` `"feet"`

### `bot.unequip(destination)`
卸除指定部位的裝備。

### `bot.drop(name_or_id=None, count=None) -> bool`
丟棄物品至地上。
- 不傳參數時：丟出手上拿著的物品（若空手回傳 `False`）。
- 傳入物品名稱字串（如 `"gold_ingot"`）或數字 ID 時：搜尋背包中對應物品並丟出。
- 可搭配 `count` 指定丟棄數量；若未傳入 `count` 或數量大於等於總持有量則丟出全部。
- 背包無此物品時回傳 `False`；若 `count <= 0` 則拋出 `ValueError`。

### `bot.moveSlotItem(source_slot, dest_slot)`
在背包內移動物品。

### `bot.activateItem(offhand=False)`
使用手持物品（右鍵使用，例如吃食物、射箭）。

### `bot.deactivateItem()`
停止使用物品。

### `bot.consume()`
吃食物或喝藥水。

---

## 攻擊 & 互動

### `bot.attack(entity)`
攻擊實體。

### `bot.swingArm(hand=None, show_hand=True)`
揮手動畫（`"left"` / `"right"`）。

### `bot.activateBlock(block, direction=None, cursor_pos=None)`
右鍵互動方塊（開門、按鈕、拉桿等）。

### `bot.activateEntity(entity)`
右鍵互動實體。

### `bot.use_player(username) -> bool`
面向指定玩家當下的實體中心並送出右鍵互動。成功送出互動時回傳 `True`。

這是疊疊樂等需要「右鍵其他玩家」的關卡建議使用的方法。每次呼叫時，
Minethon 都會重新讀取目標玩家的位置與實體高度，瞄準其碰撞箱中心後再互動；
即使玩家站在不同堆疊層，機器人也不需要自行計算 yaw、pitch 或累加每層高度。

```python
from minethon import PlayerNotFoundError

try:
    bot.use_player("Alice")
except PlayerNotFoundError:
    bot.chat("目前看不到 Alice，請靠近後再試一次")
```

注意事項：

- `username` 必須是完整且大小寫正確的玩家名稱。
- 目標必須在線、與機器人在同一世界，而且其 entity 已載入到機器人客戶端。
- 找不到可互動的玩家 entity 時會丟出 `PlayerNotFoundError`。
- 互動封包送出後是否成功仍由伺服器判定；關卡可提高 entity interaction range，
  但即使距離設得很大，也無法互動尚未載入客戶端的玩家 entity。
- 建議機器人維持 1 倍大小；此方法會使用目標的即時實體高度，因此不依賴固定層高。

疊疊樂的分工建議是由 Minethon 負責「找到玩家、即時瞄準、送出互動」，
datapack 則負責驗證關卡狀態、決定是否允許疊上去，以及建立實際的騎乘或堆疊關係。

### `bot.activateEntityAt(entity, position)`
在指定位置右鍵互動實體。

### `bot.useOn(target_entity)`
對實體使用手持物品。

### `bot.entityAtCursor(max_distance=3) -> Entity | None`
取得視線內最近的實體。

### `bot.nearestEntity(filter_=None) -> Entity | None`
取得最近的實體，可傳入 callable 過濾。

```python
nearest_mob = bot.nearestEntity(lambda e: e.type == "mob")
```

---

## 容器 & 交易

### `bot.openChest(chest, ...) -> Chest`
開啟箱子（支援 Block 或 Minecart Chest Entity）。

### `bot.openFurnace(furnace) -> Furnace`
開啟熔爐。

### `bot.openDispenser(dispenser) -> Dispenser`
開啟發射器。

### `bot.openEnchantmentTable(table) -> EnchantmentTable`
開啟附魔台。

### `bot.openAnvil(anvil) -> Anvil`
開啟鐵砧。

### `bot.openVillager(villager) -> Villager`
開啟村民交易介面。

### `bot.openContainer(chest_or_entity, ...) -> Chest | Dispenser`
通用容器開啟。

### `bot.openBlock(block, ...) -> Window`
通用方塊開啟，回傳 Window。

### `bot.closeWindow(window)`
關閉視窗。

### `bot.trade(villager_instance, trade_index, times=None)`
與村民交易。

### `bot.transfer(options)`
在背包與容器之間轉移物品。

---

## 製作 & 合成

### `bot.recipesFor(item_type, metadata, min_result_count, crafting_table) -> list[Recipe]`
查詢物品的合成配方。

### `bot.recipesAll(item_type, metadata, crafting_table) -> list[Recipe]`
查詢所有配方（含不完整的）。

### `bot.craft(recipe, count=None, crafting_table=None)`
執行合成（需確保材料在背包內）。

---

## 睡眠

### `bot.sleep(bed_block)`
使用指定床方塊睡覺（只有夜晚或雷暴才能睡）。

### `bot.isABed(block) -> bool`
判斷方塊是否為床。

### `bot.wake()`
強制醒來。

---

## 插件 & 進階

### `bot.load_plugin(name, version=None, *, export_key=None, **options) -> module`
載入 mineflayer Type A 插件。

```python
# 載入內建（version 可省略）
pf = bot.load_plugin("mineflayer-pathfinder")

# 載入第三方（必須指定版本）
bot.load_plugin("some-plugin", "1.2.3")
```

### `bot.require(name, version=None) -> module`
載入任意 npm 模組，回傳原始 JS proxy。適合非標準插件。

```python
viewer = bot.require("prismarine-viewer", "1.28.0")
viewer.mineflayer(bot, {"port": 3000})
```

### `bot.bind(handlers) -> handlers`
綁定 `BotHandlers` 實例的所有 override 方法。詳見 [events.md](events.md)。

---

## 其他實用方法

| 方法 | 說明 |
|------|------|
| `bot.waitForChunksToLoad()` | 等待附近區塊全部載入 |
| `bot.waitForTicks(ticks)` | 等待指定 tick 數 |
| `bot.fish()` | 執行完整釣魚流程 |
| `bot.updateSign(block, text, back=False)` | 更新告示牌文字 |
| `bot.writeBook(slot, pages)` | 寫書 |
| `bot.setSettings(options)` | 更新用戶端設定 |
| `bot.setCommandBlock(pos, command, options)` | 設定命令方塊 |
| `bot.acceptResourcePack()` | 接受資源包 |
| `bot.denyResourcePack()` | 拒絕資源包 |
| `bot.respawn()` | 重生 |
| `bot.connect(options)` | 重新連線 |
