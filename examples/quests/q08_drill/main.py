"""q08_drill 逃生演練：跟著引導員走到集合點。

一隻機器人配一個終端（JS 橋一個行程只有一條，開 thread 會互搶而 timeout）。
要跑 5 隻就開 5 個終端，每個終端啟動時輸入不同的編號 1..5。
"""

from minethon import PlayerNotFoundError, create_bot

guide = "玩家名稱"  # ← 帶隊玩家的遊戲 ID
number = int(input("請輸入機器人編號（1..5）："))

# 一台電腦同時跑多隻時，縮短視距比較不卡；instruction_sleep=0 讓跟隨不落拍。
bot = create_bot(f"g_drill_{number}", instruction_sleep=0, view_distance="short")

while True:
    try:
        x, y, z = bot.get_player_pos(guide)
    except PlayerNotFoundError:
        bot.wait(0.5)  # 引導員還沒進入視野，等一下再找
        continue

    bot.look_at(x, y, z)
    bot.move_forward()
