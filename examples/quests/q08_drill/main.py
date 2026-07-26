from minethon import create_bot

guide = "玩家名稱"

bot = create_bot("g_drill_1")

while True:
    x, y, z = bot.get_player_pos(guide)

    bot.look_at(x, y, z)
    bot.move_forward()
