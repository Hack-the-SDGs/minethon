from minethon import create_bot

bot = create_bot("g_swim")

bot.turn_left()
bot.turn_left()
bot.move_forward()
bot.turn_left()

for i in range(8):
    bot.dig()
    bot.move_forward()

bot.turn_right()
bot.turn_right()

for i in range(8):
    bot.move_forward()

bot.turn_right()
bot.move_forward()
