"""linear_actions — 同步命令式 API 的最小範例。

直線腳本:等出生 → 走幾步 → 轉向 → 挖一格 → 回報座標。
另外綁一個聊天事件:有人說 'stop' 就讓機器人離線。

跑法（連本機離線伺服器）:
    uv run examples/demos/linear_actions/main.py

或先設環境變數連別的伺服器:
    MC_HOST=play.example.com MC_USERNAME=mybot uv run examples/demos/linear_actions/main.py
"""

from __future__ import annotations

import os

from minethon import EventAdaptor, create_bot


def main() -> None:
    bot = create_bot(
        host=os.environ.get("MC_HOST", "localhost"),
        port=int(os.environ.get("MC_PORT", "25565")),
        username=os.environ.get("MC_USERNAME", "pybot"),
    )

    # 反應:有人說 'stop' 就離線（事件 handler 跑在 callback thread，保持簡短）。
    class Commands(EventAdaptor):
        def on_chat(self, username, message, *_):
            if username != bot.username and message == "stop":
                bot.quit("bye")

    bot.bind(Commands())

    # 直線動作跑主執行緒。
    bot.wait_spawn()
    print(f"spawned as {bot.username}")

    bot.move_forward(3)  # 往前 3 格（不用 pathfinder）
    bot.turn_right()  # 右轉 90 度
    bot.move_forward(2)

    dug = bot.dig()  # 挖掉正在看的方塊
    print("dug:", dug)

    x, y, z = bot.get_pos()
    bot.chat(f"我在 ({x:.0f}, {y:.0f}, {z:.0f})")

    bot.run_forever()  # 保活，讓 on_chat 持續運作


if __name__ == "__main__":
    main()
