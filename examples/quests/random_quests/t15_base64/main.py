import base64

from minethon import create_bot

bot = create_bot("bonus")

cipher = "SSBsb3ZlIE5UVVNU"

plain = base64.b64decode(cipher).decode()
print(plain)

bot.chat(plain)
