from minethon import create_bot

bot = create_bot("bonus")

# 把公告的密文貼進來
cipher = "20116 21152 20845 26159 22810 23569"

plain = ""
for n in cipher.split():
    plain = plain + chr(int(n))
print(plain)

# 把算出來的答案說出來
bot.chat(11)
