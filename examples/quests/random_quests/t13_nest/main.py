from minethon import create_bot

bot = create_bot("bonus")

for i in range(4):
    for j in range(3):
        bot.jump()
    bot.turn_right()
