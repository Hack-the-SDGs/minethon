from minethon import create_bot

bot = create_bot("g_labfire_1")

while True:
    block = bot.get_front_block()
    if block is None:
        bot.move_forward()
    elif block == "fire":
        bot.action("put out")
    else:
        break
