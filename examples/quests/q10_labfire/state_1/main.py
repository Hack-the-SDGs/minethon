"""q10_labfire 第一間（直線走廊）示範：偵測前方火焰並請伺服器滅火。

流程：機器人重生在金磚出生點、面向走廊方向 → 一路往前走，
每一步先看正前方一格是什麼：

- 是火焰 → ``bot.action("put out")`` 送出滅火請求。實際只是送
  ``/trigger <實際登入帳號小寫>_put_out`` 給伺服器（帳號 ``q_labfire_1``
  → ``q_labfire_1_put_out``），由關卡 datapack 驗證「執行者是機器人、
  任務進行中、前方真的有火」後代為滅火；客戶端不動任何方塊，
  斷線也不會損壞地圖。

  ⚠️ 命名契約跟著**實際登入帳號**走：在活動 PC 上，``create_bot`` 速記
  會依本機識別檔產生前綴帳號（如 ``U5_...``／``G1_...``），datapack 端
  必須對「真正登入的帳號名」宣告對應 trigger objective，兩邊要對齊。
- 其他固體方塊 → 走到走廊盡頭（牆），結束
- 沒東西 → 往前走一格

滅掉半數火點時伺服器會啟動灑水系統，本腳本只管往前清火即可。
"""

from minethon import create_bot

bot = create_bot("q_labfire_1")
bot.wait_spawn()

doused = 0
for _ in range(64):  # 安全上限，避免無限重試
    front = bot.get_block_in_front()
    if front is not None and front[1] == "fire":
        bot.action("put out")  # 請伺服器滅火（datapack 驗證後執行）
        bot.wait(0.3)  # 給伺服器一刻處理
        if bot.get_block_in_front() != front:  # 火真的熄了才計數
            doused += 1
            bot.chat(f"撲滅第 {doused} 處火點！")
        continue
    if front is not None:
        break  # 前方是牆或其他固體，走廊到底了
    bot.move_forward(1)

bot.chat(f"第一間掃完，共撲滅 {doused} 處火點。")
