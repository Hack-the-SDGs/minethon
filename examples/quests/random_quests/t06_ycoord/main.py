from minethon import create_bot

bot = create_bot("bonus")

while True:
    y = bot.get_y()
    bot.chat(int(y))
