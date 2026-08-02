import base64

from minethon import create_bot

bot = create_bot("bonus")

cipher = "密文"

plain = base64.b64decode(cipher).decode()
print(plain)

bot.chat(plain)
