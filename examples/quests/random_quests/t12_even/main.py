from minethon import create_bot

bot = create_bot("bonus")

for i in range(1, 21):
    if i % 2 == 0:
        bot.chat(i)
