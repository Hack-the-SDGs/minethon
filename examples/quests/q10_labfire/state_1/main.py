from minethon import create_bot

bot = create_bot("g_labfire_1")

while True:
    block = bot.get_block_in_front()
    if block is None:
        bot.move_forward()
    elif block == "fire":
        bot.action("put out")
    else:
        break
