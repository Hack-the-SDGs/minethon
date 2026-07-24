from minethon import create_bot

target = "玩家名稱"
bots = []

for number in range(1, 8):
    bot = create_bot(f"g_stack_{number}")
    bot.use_player(target)

    while bot.entity.vehicle is None:
        bot.wait(0.1)

    bots.append(bot)
    target = str(bot.username)

bots[-1].run_forever()
