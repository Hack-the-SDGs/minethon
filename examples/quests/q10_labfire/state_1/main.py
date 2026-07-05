"""q10_labfire 第一間（直線走廊）示範：偵測前方火焰並潑水撲滅。

流程：機器人重生在金磚出生點、面向走廊方向 → 一路往前走，
每一步先看正前方一格是什麼：

- 是火焰 → ``bot.action("put_water")`` 潑水撲滅（潑完會自動把水收回）
- 其他固體方塊 → 走到走廊盡頭（牆），結束
- 沒東西 → 往前走一格

滅掉半數火點時伺服器會啟動灑水系統，本腳本只管往前清火即可。
"""

from minethon import create_bot

bot = create_bot("q_labfire_1")
bot.wait_spawn()

doused = 0
for _ in range(32):  # 安全上限，避免無限前進
    front = bot.get_block_in_front()
    if front is not None and front[1] == "fire":
        if bot.action("put_water"):
            doused += 1
            bot.chat(f"撲滅第 {doused} 處火點！")
        continue  # 潑完再看一次前方（水可能沒潑準）
    if front is not None:
        break  # 前方是牆或其他固體，走廊到底了
    bot.move_forward(1)

bot.chat(f"第一間掃完，共撲滅 {doused} 處火點。")
