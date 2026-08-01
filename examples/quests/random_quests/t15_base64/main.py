import base64

from minethon import create_bot

bot = create_bot("bonus")

# 把公告的密文貼進來
cipher = "SSBsb3ZlIE5UVVNU"

plain = base64.b64decode(cipher).decode()
print(plain)

bot.chat(plain)
