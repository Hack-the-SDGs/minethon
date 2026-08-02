from minethon import create_bot

bot = create_bot("bonus")

cipher = "密文"

for shift in range(1, 26):
    plain = ""
    for c in cipher:
        if c == " ":
            plain = plain + " "
        else:
            plain = plain + chr((ord(c) - 97 - shift) % 26 + 97)
    print(shift, plain)

bot.chat("答案")
