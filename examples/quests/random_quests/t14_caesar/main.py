from minethon import create_bot

bot = create_bot("bonus")

# 把公告的密文貼進來。題目沒有說推了幾格，所以 25 種都印出來，
# 自己挑出讀得懂的那一行。
cipher = "wkuhh soxv ilyh"

for shift in range(1, 26):
    plain = ""
    for c in cipher:
        if c == " ":
            plain = plain + " "
        else:
            plain = plain + chr((ord(c) - 97 - shift) % 26 + 97)
    print(shift, plain)

# 把算出來的答案說出來
bot.chat(8)
