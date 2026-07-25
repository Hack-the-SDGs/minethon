from minethon import create_bot

guide = "玩家名稱"
number = input()

bot = create_bot(f"g_drill_{number}")

while True:
    x, y, z = bot.get_player_pos(guide)

    bot.look_at(x, y, z)
    bot.move_forward()
