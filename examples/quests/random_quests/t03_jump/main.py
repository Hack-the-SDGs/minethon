from minethon import create_bot

bot = create_bot("bonus")

for i in range(10):
    bot.jump()
    bot.wait(0.5)
