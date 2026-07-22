# 事件系統

minethon 的事件 API 有兩種等價寫法，選一種就好：

```python
# 寫法一：@bot.on_<event>  ← 推薦，IDE completion 最穩
@bot.on_chat
def handler(username, message, translate, json_msg, matches):
    ...

# 寫法二：@bot.on(BotEvent.X)  ← 適合動態決定事件名稱
from minethon import BotEvent

@bot.on(BotEvent.CHAT)
def handler(username, message, translate, json_msg, matches):
    ...
```

---

## `bot.once(...)` — 一次性事件

只觸發一次後自動解綁：

```python
@bot.once(BotEvent.SPAWN)
def first_spawn():
    bot.chat("已生成！")
```

shortcut 寫法：`@bot.once_spawn`

---

## Callback 參數規則

- 參數比 d.ts 宣告**少**也沒關係，minethon 會補 `None`
- 多餘的參數可以用 `*_` 忽略
- 所有 handler 跑在 JSPyBridge callback thread，**不要在裡面做耗時或 blocking 工作**

---

## BotHandlers — class-based 寫法

適合把多個 handler 組織成同一個類別：

```python
from minethon import BotHandlers

class MyHandlers(BotHandlers):
    def on_login(self):
        print(f"已登入：{bot.username}")

    def on_spawn(self):
        bot.chat("Hello!")

    def on_chat(self, username, message, *_):
        if message == "hi":
            bot.chat(f"Hi, {username}!")

bot.bind(MyHandlers())
```

只需 override 你關心的方法，`bot.bind()` 會自動跳過未 override 的。

---

## BotEvent 完整列表

### 聊天 & 訊息

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `CHAT` | `on_chat` | `username, message, translate, json_msg, matches` | 公開聊天（自己發的也會觸發） |
| `WHISPER` | `on_whisper` | `username, message, translate, json_msg, matches` | 收到私聊 |
| `MESSAGE` | `on_message` | `json_msg, position` | 任何文字訊息 |
| `MESSAGESTR` | `on_messagestr` | `message, message_position, json_msg` | 純字串版訊息 |
| `UNMATCHED_MESSAGE` | `on_unmatched_message` | `message, metadata` | 未匹配 chat pattern 的系統訊息 |
| `ACTION_BAR` | `on_action_bar` | `json_msg` | 動作列懸浮文字 |
| `TITLE` | `on_title` | `title_text` | 伺服器大型標題 |

### 連線 & 生命週期

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `LOGIN` | `on_login` | *(無)* | 登入成功但尚未進入世界 |
| `SPAWN` | `on_spawn` | *(無)* | 生成/重生進入世界，可開始操作 |
| `RESPAWN` | `on_respawn` | *(無)* | 重生 |
| `DEATH` | `on_death` | *(無)* | 機器人死亡 |
| `END` | `on_end` | `reason` | 連線斷開（正常、踢出、網路斷線都觸發） |
| `KICKED` | `on_kicked` | `reason, logged_in` | 被踢出 |
| `ERROR` | `on_error` | `err` | 不致命的例外 |
| `INJECT_ALLOWED` | `on_inject_allowed` | *(無)* | 允許插件 inject |

### 實體

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `ENTITY_SPAWN` | `on_entity_spawn` | `entity` | 新實體進入視野 |
| `ENTITY_GONE` | `on_entity_gone` | `entity` | 實體離開視野或被移除 |
| `ENTITY_MOVED` | `on_entity_moved` | `entity` | 實體位置變動（高頻） |
| `ENTITY_UPDATE` | `on_entity_update` | `entity` | 實體 metadata 變動 |
| `ENTITY_HURT` | `on_entity_hurt` | `entity` | 實體受傷 |
| `ENTITY_DEAD` | `on_entity_dead` | `entity` | 實體死亡 |
| `ENTITY_ATTRIBUTES` | `on_entity_attributes` | `entity` | 屬性表（速度/血量上限）變動 |
| `ENTITY_EQUIP` | `on_entity_equip` | `entity` | 實體換裝備 |
| `ENTITY_SWING_ARM` | `on_entity_swing_arm` | `entity` | 實體揮手 |
| `ENTITY_EFFECT` | `on_entity_effect` | `entity, effect` | 套上狀態效果 |
| `ENTITY_EFFECT_END` | `on_entity_effect_end` | `entity, effect` | 狀態效果消失 |
| `ENTITY_ATTACH` | `on_entity_attach` | `entity, vehicle` | 實體騎上載具 |
| `ENTITY_DETACH` | `on_entity_detach` | `entity, vehicle` | 實體離開載具 |
| `ENTITY_ELYTRA_FLEW` | `on_entity_elytra_flew` | `entity` | 張開鞘翅飛行 |
| `ENTITY_TAMED` | `on_entity_tamed` | `entity` | 動物被馴服 |
| `ENTITY_TAMING` | `on_entity_taming` | `entity` | 嘗試馴服中 |
| `ENTITY_CROUCH` | `on_entity_crouch` | `entity` | 實體蹲下 |
| `ENTITY_UNCROUCH` | `on_entity_uncrouch` | `entity` | 實體取消蹲下 |
| `ENTITY_SLEEP` | `on_entity_sleep` | `entity` | 實體睡覺 |
| `ENTITY_WAKE` | `on_entity_wake` | `entity` | 實體醒來 |
| `ENTITY_EAT` | `on_entity_eat` | `entity` | 實體進食 |
| `ENTITY_EATING_GRASS` | `on_entity_eating_grass` | `entity` | 羊吃草 |
| `ENTITY_HAND_SWAP` | `on_entity_hand_swap` | `entity` | 左右手物品互換 |
| `ENTITY_SHAKING_OFF_WATER` | `on_entity_shaking_off_water` | `entity` | 動物抖水 |
| `ENTITY_CRITICAL_EFFECT` | `on_entity_critical_effect` | `entity` | 暴擊效果 |
| `ENTITY_MAGIC_CRITICAL_EFFECT` | `on_entity_magic_critical_effect` | `entity` | 魔法暴擊效果 |

### 方塊 & 世界

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `BLOCK_UPDATE` | `on_block_update` | `old_block, new_block` | 任何方塊變動（高頻） |
| `BLOCK_BREAK_PROGRESS_OBSERVED` | `on_block_break_progress_observed` | `block, destroy_stage` | 看到別人挖方塊 |
| `BLOCK_BREAK_PROGRESS_END` | `on_block_break_progress_end` | `block` | 挖掘動作結束 |
| `DIGGING_COMPLETED` | `on_digging_completed` | `block` | 自己挖成功 |
| `DIGGING_ABORTED` | `on_digging_aborted` | `block` | 自己挖被中斷 |
| `CHUNK_COLUMN_LOAD` | `on_chunk_column_load` | `point` | 區塊柱載入 |
| `CHUNK_COLUMN_UNLOAD` | `on_chunk_column_unload` | `point` | 區塊柱卸載 |
| `PISTON_MOVE` | `on_piston_move` | `block, powered, action` | 活塞推/拉 |
| `CHEST_LID_MOVE` | `on_chest_lid_move` | `block, is_open, block2` | 箱子開/關 |

### 移動 & 物理

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `MOVE` | `on_move` | *(無)* | 機器人位置/視角改變（高頻） |
| `FORCED_MOVE` | `on_forced_move` | *(無)* | 被伺服器傳送 |
| `PHYSICS_TICK` | `on_physics_tick` | *(無)* | 每個物理 tick ~20Hz（高頻） |
| `PHYSIC_TICK` | `on_physic_tick` | *(無)* | 同 PHYSICS_TICK（舊別名） |
| `MOUNT` | `on_mount` | *(無)* | 騎上載具 |
| `DISMOUNT` | `on_dismount` | `entity` | 下載具 |

### 玩家

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `PLAYER_JOINED` | `on_player_joined` | `player` | 有玩家進入伺服器 |
| `PLAYER_LEFT` | `on_player_left` | `player` | 有玩家離線 |
| `PLAYER_UPDATED` | `on_player_updated` | `player` | 玩家資訊更新（高頻） |
| `PLAYER_COLLECT` | `on_player_collect` | `collector, collected` | 玩家撿起掉落物 |

### 狀態 & 遊戲

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `HEALTH` | `on_health` | *(無)* | 血量/飽食度變動，讀 `bot.health` / `bot.food` |
| `BREATH` | `on_breath` | *(無)* | 氧氣量變動，讀 `bot.oxygenLevel` |
| `EXPERIENCE` | `on_experience` | *(無)* | 經驗值變動，讀 `bot.experience` |
| `SLEEP` | `on_sleep` | *(無)* | 機器人入睡 |
| `WAKE` | `on_wake` | *(無)* | 機器人醒來 |
| `RAIN` | `on_rain` | *(無)* | 天氣變化，讀 `bot.isRaining` |
| `SPAWN_RESET` | `on_spawn_reset` | *(無)* | 重生點重置 |
| `GAME` | `on_game` | *(無)* | 遊戲模式/維度/難度變更，讀 `bot.game` |
| `TIME` | `on_time` | *(無)* | 時間更新（非常高頻，避免做耗時工作） |
| `RESOURCE_PACK` | `on_resource_pack` | *(無)* | 伺服器推送資源包 |
| `ITEM_DROP` | `on_item_drop` | `entity` | 實體掉落物品 |

### 記分板 & 隊伍

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `SCOREBOARD_CREATED` | `on_scoreboard_created` | `scoreboard` | 新記分板建立 |
| `SCOREBOARD_DELETED` | `on_scoreboard_deleted` | `scoreboard` | 記分板刪除 |
| `SCOREBOARD_TITLE_CHANGED` | `on_scoreboard_title_changed` | `scoreboard` | 記分板標題變動 |
| `SCOREBOARD_POSITION` | `on_scoreboard_position` | `position, scoreboard` | 顯示位置切換 |
| `SCORE_UPDATED` | `on_score_updated` | `scoreboard, item` | 分數更新 |
| `SCORE_REMOVED` | `on_score_removed` | `scoreboard, item` | 分數條目移除 |
| `TEAM_CREATED` | `on_team_created` | `team` | 隊伍建立 |
| `TEAM_REMOVED` | `on_team_removed` | `team` | 隊伍移除 |
| `TEAM_UPDATED` | `on_team_updated` | `team` | 隊伍資訊變動 |
| `TEAM_MEMBER_ADDED` | `on_team_member_added` | `team, member` | 成員加入隊伍 |
| `TEAM_MEMBER_REMOVED` | `on_team_member_removed` | `team, member` | 成員離開隊伍 |

### Boss Bar & 音效

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `BOSS_BAR_CREATED` | `on_boss_bar_created` | `boss_bar` | Boss 血條出現 |
| `BOSS_BAR_DELETED` | `on_boss_bar_deleted` | `boss_bar` | Boss 血條消失 |
| `BOSS_BAR_UPDATED` | `on_boss_bar_updated` | `boss_bar` | Boss 血條更新 |
| `SOUND_EFFECT_HEARD` | `on_sound_effect_heard` | `sound_name, position, volume, pitch` | 音效 |
| `HARDCODED_SOUND_EFFECT_HEARD` | `on_hardcoded_sound_effect_heard` | `sound_id, sound_category, position, volume, pitch` | 舊版硬編碼音效 |
| `NOTE_HEARD` | `on_note_heard` | `block, instrument, pitch` | 音符盒 |
| `PARTICLE` | `on_particle` | `particle` | 粒子效果 |
| `USED_FIREWORK` | `on_used_firework` | `firework_entity` | 使用煙火 |

### 視窗

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `WINDOW_OPEN` | `on_window_open` | `window` | 視窗開啟 |
| `WINDOW_CLOSE` | `on_window_close` | `window` | 視窗關閉 |

### Pathfinder（需先載入插件）

| BotEvent | shortcut | callback 參數 | 說明 |
|----------|----------|--------------|------|
| `GOAL_REACHED` | `on_goal_reached` | `goal` | 到達目標 |
| `GOAL_UPDATED` | `on_goal_updated` | `goal, dynamic` | 目標更新 |
| `PATH_RESET` | `on_path_reset` | `reason` | 路線重置 |
| `PATH_STOP` | `on_path_stop` | *(無)* | 停止尋路 |
| `PATH_UPDATE` | `on_path_update` | `results` | 路線更新 |
