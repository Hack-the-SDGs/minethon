from minethon import create_bot

bot = create_bot("bonus")

cipher = "反轉文字"

print(cipher[::-1])

bot.chat("答案")
