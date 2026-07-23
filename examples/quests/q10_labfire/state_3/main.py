"""q10_labfire state 3: 用 online DFS 探索未知迷宮。"""

from minethon import create_bot

DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

bot = create_bot("g_labfire_3")
bot.wait_spawn()

visited = set()
current_direction = 0  # 出生面向北，也就是方向 0


def turn_to(direction):
    """用 turn_left / turn_right 轉到指定方向。"""
    global current_direction
    steps = (direction - current_direction) % 4
    if steps == 1:
        bot.turn_right()
    elif steps == 2:
        bot.turn_right()
        bot.turn_right()
    elif steps == 3:
        bot.turn_left()
    current_direction = direction % 4


def move_to(direction):
    turn_to(direction)
    block = bot.get_block_in_front()

    if block is not None and not str(block[1]).endswith("fire"):
        return False

    while block is not None and str(block[1]).endswith("fire"):
        bot.action("put out")
        block = bot.get_block_in_front()

    bot.move_forward(1)
    return True


def dfs(row, col):
    visited.add((row, col))

    for direction, (dr, dc) in enumerate(DIRS):
        next_row = row + dr
        next_col = col + dc

        if (next_row, next_col) in visited:
            continue
        if not move_to(direction):
            continue
        dfs(next_row, next_col)

        turn_to(direction + 2)
        bot.move_forward(1)


dfs(0, 0)
