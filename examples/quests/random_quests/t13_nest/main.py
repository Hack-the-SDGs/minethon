from minethon import create_bot

bot = create_bot("bonus")

for i in range(4):
    for j in range(3):
        bot.jump()
        bot.wait(0.5)
    bot.turn_right()
