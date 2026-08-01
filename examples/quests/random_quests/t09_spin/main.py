from minethon import create_bot

bot = create_bot("bonus")

for i in range(4):
    bot.turn_right()
    bot.wait(0.6)
