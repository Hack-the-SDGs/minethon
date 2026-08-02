from minethon import create_bot

bot = create_bot("bonus")

x, y, z = bot.get_pos()
bot.chat(int(x) + int(y) + int(z))
