from minethon import create_bot

target = "玩家名稱"

for number in range(1, 8):
    bot = create_bot(f"g_stack_{number}")

    while bot.entity.vehicle is None:
        bot.use_player(target)
        bot.wait(0.5)

    target = bot.username
