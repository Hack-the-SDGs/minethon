# q10_labfire — 實驗室滅火任務工具示範

搭配競賽伺服器的 `q10_labfire` 關卡（三間實驗室接連起火，機器人逐間撲滅目標
火點啟動灑水系統；前兩間限時 180 秒，第三間限時 300 秒）。每組會進入自己的
`world-g<N>`，不同組可平行進行。

本任務用到兩個 minethon API：

| API | 用途 |
|-----|------|
| `bot.get_block_in_front()` | 回報正前方一格的方塊（**火焰會被回報**），回傳 `((x, y, z), 名稱)` 或 `None` |
| `bot.action("put out")` | 請伺服器滅火——送 `/trigger <帳號>_put_out`，由 datapack 驗證後執行 |

## 為什麼 `action()` 是「請伺服器做」而不是客戶端自己潑水

早期構想是讓機器人自己用水桶潑水再收回，但有實際風險：水能放在哪需要
WorldGuard 大量子區域授權、潑水瞬間斷線或掉包會來不及收水而損壞地圖、
水流的微小推動會讓機器人瞄準偏移導致收不回。因此改為**伺服器權威**設計：

1. 前端手打 `bot.action("put out")`
2. minethon 依 ** 實際登入帳號 ** 加工成 ` /trigger <帳號小寫>_put_out ` 送出
  （帳號 ` G1_labfire_1 ` → ` g1_labfire_1_put_out `
3. 關卡 datapack 驗證：執行者是不是機器人、任務是否開始、前方一格是否真的有火
4. 驗證通過 → 伺服器直接熄掉該格火焰（不經 WG、無水流）；不通過 → 靜默忽略

> **命名契約注意**：objective 名稱取自真正登入的帳號名。活動 PC 的
> `create_bot` 速記會依組別識別檔產生 `G<組>_...` 帳號；labfire 的世界、狀態與
> trigger objective 都依真正登入帳號中的組別及帳號名隔離。

客戶端全程不動方塊，任何時刻斷線都不會留下損壞。同一機制可擴充到其他關卡
（例如 `action("ride")`、`action("lay")`），只要對應 datapack 有註冊該 trigger。

偵測輔助也可以用既有 API：`bot.find_block("fire")`（最近的火點座標）、
`bot.find_blocks("fire", max=16)`（一次列出多個火點）。

## 前置

- 機器人帳號：`G<N>_labfire_1`（由關卡 datapack／Skript 控管：任務未啟動會被踢下線，
  登入後會自動傳送到 `world-g<N>` 該間實驗室的出生點）。
- 執行前先啟動同一組任務（管理員 `/function quests:q10_labfire/start {group:N}`）。

## 執行

```bash
uv run python examples/quests/q10_labfire/state_1/main.py
```

`main.py` 是第一間（直線走廊）的示範解法：一路向前，看到前方著火就請伺服器滅火。
第二、三間是 DFS 迷宮與 online DFS 建圖，留給學員自己發揮。

第二、三間補充：迷宮內移動由**伺服器接管**（速度變慢、自動格點吸附、不合法的步伐
會被退回）。轉向或前進前可先呼叫 `bot.action("snap")` 請伺服器把機器人對齊到目前
格子的中心，走迷宮會穩定很多。帳號尾碼（`_1`/`_2`/`_3`）只是命名慣例，伺服器不驗證，
但建議照關卡換帳號，方便辨識。
