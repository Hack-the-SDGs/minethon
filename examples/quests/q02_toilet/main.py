import time

from minethon import create_bot

bot = create_bot("g_toilet_1")

while True:
    bot.sneak(True)
    bot.wait(0.1)
    bot.sneak(False)
    bot.wait(0.1)
