"""q10_labfire state 2: DFS on a known maze."""

from minethon import create_bot

ROWS = 35
COLS = 9
START_ROW = 34
START_COL = 4
TARGET_DOUSED = 4

OPEN = 0
WALL = 1

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
    [0, 1, 0, 1, 0, 1, 0, 1, 0],
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
bot.wait_spawn()

visited = set()
state = {"facing": 0, "doused": 0}


def block_name(block):
    if block is None:
        return ""
    if isinstance(block, (tuple, list)) and len(block) > 1:
        return str(block[1])
    return str(block)


def is_fire(block):
    name = block_name(block)
    return name == "fire" or name.endswith(":fire")


def is_open(row, col):
    return 0 <= row < ROWS and 0 <= col < COLS and MAZE[row][col] == OPEN


def turn_to(direction):
    direction %= 4
    turns = (direction - state["facing"]) % 4

    if turns == 1:
        bot.turn_right()
    elif turns == 2:
        bot.turn_right()
        bot.turn_right()
    elif turns == 3:
        bot.turn_left()

    state["facing"] = direction


def put_out_front():
    for _ in range(3):
        bot.action("put out")
        bot.wait(0.3)
        if not is_fire(bot.get_block_in_front()):
            state["doused"] += 1
            return True

    return False


def move_one(direction):
    turn_to(direction)

    if is_fire(bot.get_block_in_front()) and not put_out_front():
        return False

    bot.move_forward(1)
    bot.wait(0.05)
    return True


def go_back(direction):
    turn_to(direction + 2)
    bot.move_forward(1)
    bot.wait(0.05)


def dfs(row, col):
    visited.add((row, col))

    if state["doused"] >= TARGET_DOUSED:
        return True

    for direction, (dr, dc) in enumerate(DIRS):
        next_row = row + dr
        next_col = col + dc

        if not is_open(next_row, next_col):
            continue
        if (next_row, next_col) in visited:
            continue
        if not move_one(direction):
            continue
        if dfs(next_row, next_col):
            return True

        go_back(direction)

    return False


if len(MAZE) != ROWS or any(len(row) != COLS for row in MAZE):
    raise ValueError("MAZE must be 35 x 9")

dfs(START_ROW, START_COL)
bot.chat(f"第二間完成，撲滅 {state['doused']} 處火點")
