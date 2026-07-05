# q10_labfire — 實驗室滅火任務工具示範

搭配競賽伺服器的 `q10_labfire` 關卡（三間實驗室接連起火，機器人逐間撲滅半數
火點啟動灑水系統，每間限時 180 秒）。

本任務用到兩個 minethon API：

| API | 用途 |
|-----|------|
| `bot.get_block_in_front()` | 回報正前方一格的方塊（**火焰會被回報**），回傳 `((x, y, z), 名稱)` 或 `None` |
| `bot.action("put_water")` | 拿出水桶對正前方潑水撲滅火焰，稍候把水收回、不淹場地 |

火焰在準心 raytrace 下不可選取（vanilla 行為），所以 `look_block()`／`use()`
對著火焰會失準——這正是這兩個 API 存在的原因：

- `get_block_in_front()` 用「前方一格」的網格判定，不吃 raytrace。
- `action("put_water")` 內部用 `lookAt` 對準火點再使用水桶，潑完再收回水源。

輔助偵測也可以用既有 API：`bot.find_block("fire")`（最近的火點座標）、
`bot.find_blocks("fire", max=16)`（一次列出多個火點）。

## 前置

- 機器人帳號：`q_labfire_1`（由關卡 datapack／Skript 控管：任務未啟動會被踢下線，
  登入後會自動傳送到該間實驗室的出生點並發給水桶）。
- 執行前先啟動任務（管理員 `/function quests:q10_labfire/start`）。

## 執行

```bash
uv run python examples/quests/q10_labfire/state_1/main.py
```

`main.py` 是第一間（直線走廊）的示範解法：一路向前，看到前方著火就潑水。
第二、三間是 DFS 迷宮與 online DFS 建圖，留給學員自己發揮。
