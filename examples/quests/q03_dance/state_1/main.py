from minethon import create_bot

bot = create_bot("g_dance")

while True:
    if bot.get_block_property(40, 66, -406, "lit"):
        bot.move_forward()
        bot.move_backward()
    if bot.get_block_property(38, 66, -406, "lit"):
        bot.move_backward()
        bot.move_forward()
    if bot.get_block_property(36, 66, -406, "lit"):
        bot.move_left()
        bot.move_right()
    if bot.get_block_property(42, 66, -406, "lit"):
        bot.move_right()
        bot.move_left()