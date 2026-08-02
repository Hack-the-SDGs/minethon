from minethon import create_bot

bot = create_bot("bonus")

for i in range(10, 0, -1):
    bot.chat(i)
