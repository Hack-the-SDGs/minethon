from minethon import PlayerNotFoundError, create_bot

target = "玩家名稱"
bots = []

for number in range(1, 8):
    bot = create_bot(f"g_stack_{number}")

    while bot.entity.vehicle is None:
        try:
            bot.use_player(target)
        except PlayerNotFoundError:
            pass
        bot.wait(0.5)

    bots.append(bot)
    target = str(bot.username)

bots[-1].run_forever()
