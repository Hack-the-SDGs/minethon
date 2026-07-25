from minethon import create_bot

START_ROW = 34
START_COL = 4

MAZE = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 0, 1, 0, 0, 1, 0],
    [0, 1, 1, 0, 1, 1, 0, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 1, 0],
    [0, 1, 0, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 1, 1],
    [0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 1, 1],
    [0, 1, 0, 1, 0, 1, 1, 1, 1],
    [0, 1, 0, 1, 0, 0, 0, 0, 1],
    [0, 1, 0, 1, 0, 1, 1, 0, 1],
    [0, 1, 0, 1, 0, 0, 1, 0, 1],
    [0, 1, 0, 1, 0, 0, 1, 0, 1],
    [0, 1, 0, 1, 0, 0, 1, 0, 1],
    [0, 1, 0, 1, 1, 1, 1, 0, 1],
    [0, 1, 0, 0, 0, 0, 1, 0, 1],
    [0, 1, 1, 1, 1, 0, 1, 0, 1],
    [0, 0, 1, 0, 0, 0, 0, 0, 1],
    [0, 0, 1, 1, 0, 1, 1, 1, 1],
    [0, 0, 0, 1, 0, 1, 1, 1, 1],
    [0, 0, 0, 1, 0, 1, 1, 1, 1],
    [0, 0, 0, 1, 0, 1, 1, 1, 1],
]

DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

bot = create_bot("g_labfire_2")

visited = set()
current_direction = 0  # 出生面向北，也就是方向 0


def is_open(row, col):
    return 0 <= row < len(MAZE) and 0 <= col < len(MAZE[0]) and MAZE[row][col] == 0


def turn_to(direction):
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
    while bot.get_block_in_front() == "fire":
        bot.action("put out")
    bot.move_forward()


def dfs(row, col):
    visited.add((row, col))

    for direction, (dr, dc) in enumerate(DIRS):
        next_row = row + dr
        next_col = col + dc

        if not is_open(next_row, next_col) or (next_row, next_col) in visited:
            continue

        move_to(direction)
        dfs(next_row, next_col)

        turn_to(direction + 2)
        bot.move_forward()


dfs(START_ROW, START_COL)
