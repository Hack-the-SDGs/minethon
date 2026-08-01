from minethon import create_bot

bot = create_bot("bonus")

# 把公告的密文貼進來
cipher = "少多是二乘三"

# 印出解開後的題目
print(cipher[::-1])

# 把算出來的答案說出來
bot.chat(6)
