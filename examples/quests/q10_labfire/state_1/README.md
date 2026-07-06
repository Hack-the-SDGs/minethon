# q10_labfire — 實驗室滅火任務工具示範

搭配競賽伺服器的 `q10_labfire` 關卡（三間實驗室接連起火，機器人逐間撲滅半數
火點啟動灑水系統，每間限時 180 秒）。

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
2. minethon 依**實際登入帳號**加工成 `/trigger <帳號小寫>_put_out` 送出
   （帳號 `q_labfire_1` → `q_labfire_1_put_out`）
3. 關卡 datapack 驗證：執行者是不是機器人、任務是否開始、前方一格是否真的有火
4. 驗證通過 → 伺服器直接熄掉該格火焰（不經 WG、無水流）；不通過 → 靜默忽略

> **命名契約注意**：objective 名稱取自真正登入的帳號名。活動 PC 的
> `create_bot` 速記會依識別檔產生前綴帳號（`U<電腦>_...`／`G<組>_...`），
> 若 labfire 改走速記帳號，datapack 端宣告的 objective 要跟著實際帳號名調整。

客戶端全程不動方塊，任何時刻斷線都不會留下損壞。同一機制可擴充到其他關卡
（例如 `action("ride")`、`action("lay")`），只要對應 datapack 有註冊該 trigger。

偵測輔助也可以用既有 API：`bot.find_block("fire")`（最近的火點座標）、
`bot.find_blocks("fire", max=16)`（一次列出多個火點）。

## 前置

- 機器人帳號：`q_labfire_1`（由關卡 datapack／Skript 控管：任務未啟動會被踢下線，
  登入後會自動傳送到該間實驗室的出生點）。
- 執行前先啟動任務（管理員 `/function quests:q10_labfire/start`）。

## 執行

```bash
uv run python examples/quests/q10_labfire/state_1/main.py
```

`main.py` 是第一間（直線走廊）的示範解法：一路向前，看到前方著火就請伺服器滅火。
第二、三間是 DFS 迷宮與 online DFS 建圖，留給學員自己發揮。
