"""q08_drill 逃生演練：機器人跟隨引導員走到集合點。

minethon 底層的 JS 橋（JSPyBridge）一個行程只有一條，多隻機器人不能用 thread
（會互搶橋而 timeout，5 隻同時登入也會擠爆 Node）。多隻請「一隻一個終端」跑，
每個終端帶不同編號 1..5：

    uv run examples/quests/q08_drill/main.py 1
    uv run examples/quests/q08_drill/main.py 2
    uv run examples/quests/q08_drill/main.py 3
    uv run examples/quests/q08_drill/main.py 4
    uv run examples/quests/q08_drill/main.py 5

先讓引導員在全像上「右鍵開始演練」，再把 guide 改成帶隊玩家的 ID。
"""

import sys

from minethon import PlayerNotFoundError, create_bot

guide = "使用者 ID"  # ← 帶隊玩家的遊戲名稱
# 機器人編號 1..5（從指令參數帶入）；先驗證，避免打錯組成無效帳號難以除錯
arg = sys.argv[1] if len(sys.argv) > 1 else "1"
if not arg.isdigit() or not 1 <= int(arg) <= 5:
    raise SystemExit("機器人編號只能是 1 到 5，例如：uv run main.py 3")
number = int(arg)

bot = create_bot(f"g_drill_{number}", instruction_sleep=0)
bot.wait_spawn()

while True:
    try:
        bot.look_at(*bot.get_player_pos(guide))  # 面向引導員
    except PlayerNotFoundError:
        bot.wait(0.5)  # 引導員暫時不在範圍，稍等再找
        continue
    bot.move_forward(1)  # 往前跟上
