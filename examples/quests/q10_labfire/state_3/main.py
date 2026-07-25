from minethon import create_bot

DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

bot = create_bot("g_labfire_3")

visited = set()
walls = set()


def scan(here, facing):
    while bot.get_block_in_front() == "fire":
        bot.action("put out")
    if bot.get_block_in_front() is not None:
        dr, dc = DIRS[facing]
        walls.add((here[0] + dr, here[1] + dc))


def turn_to(here, facing, direction):
    while facing != direction:
        if (direction - facing) % 4 == 3:
            bot.turn_left()
            facing = (facing - 1) % 4
        else:
            bot.turn_right()
            facing = (facing + 1) % 4
        scan(here, facing)
    return facing


def step(here, facing):
    bot.move_forward()
    scan(here, facing)


def explore(here, facing):
    visited.add(here)

    for direction, (dr, dc) in enumerate(DIRS):
        target = (here[0] + dr, here[1] + dc)
        if target in visited or target in walls:
            continue

        facing = turn_to(here, facing, direction)
        if target in walls:
            continue

        step(target, facing)
        facing = explore(target, facing)
        facing = turn_to(target, facing, (direction + 2) % 4)
        step(here, facing)

    return facing


scan((0, 0), 0)
explore((0, 0), 0)
