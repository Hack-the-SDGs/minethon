from minethon import create_bot

bot = create_bot("bonus")

cipher = "密文"

plain = ""
for n in cipher.split():
    plain = plain + chr(int(n))
print(plain)

bot.chat("答案")
