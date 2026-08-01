from minethon import create_bot

bot = create_bot("bonus")

while True:
    for i in range(10):
        bot.jump()
