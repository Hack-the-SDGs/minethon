"""q10_labfire state 1: 直線前進並撲滅火焰。"""

from minethon import create_bot

bot = create_bot("g_labfire_1")
bot.wait_spawn()

while True:
    block = bot.get_front_block()
    if block is not None and block.endswith("fire"):
        bot.action("put out")
    elif block is not None:
        break
    else:
        bot.move_forward()
