---
name: minethon
description: Use when writing, reviewing, or debugging Python code that uses the minethon Minecraft bot SDK — connecting a bot with create_bot, the synchronous student API (bot.wait_spawn / move_forward / dig / look_block / get_pos / chat …), the EventAdaptor event API, or pathfinder — or when a student describes Minecraft bot behavior to turn into minethon code.
---

# minethon

## Overview

minethon is a teaching-oriented Python SDK for Minecraft bots (mineflayer under the hood, via JSPyBridge). It exposes a **synchronous, blocking** API so beginners write straight-line scripts — **no `async`/`await`, no event loop, no Node.js**. Every call returns only when the action is done.

There are **two ways** to drive the bot, and real scripts often combine them:

1. **Synchronous student API** — blocking commands for linear "do A, then B, then C" scripts: `bot.wait_spawn()`, `bot.move_forward(3)`, `bot.dig()`, `bot.get_pos()`. **This is the default.**
2. **EventAdaptor** — subclass it, override `on_<event>` methods, wire with `bot.bind(...)`, keep the process alive with `bot.run_forever()`. Use it to *react* (chat commands, taking damage, players joining).

## CRITICAL rules (these are where AI gets it wrong)

- **Movement uses the student API, never pathfinder or yaw math.** To walk forward 5 blocks: `bot.move_forward(5)`. Do NOT write `bot.pathfinder.goto(...)`, `bot.entity.position` math, or `import math`. Pathfinder exists but is an advanced opt-in, not for basic movement.
- **Method names are minethon's own snake_case** — use the Quick Reference below. Do NOT invent names or use mineflayer camelCase. It is `bot.dig()` (no arguments — digs the block you're aiming at), `bot.look_block()`, `bot.find_block("oak_log")` — NOT `bot.blockAtCursor()` / `bot.dig(block)` / `block_at_cursor()`.
- **A linear task that must also react to chat** = bind an `EventAdaptor` for the reaction, run the linear actions, then `bot.run_forever()` to stay online.
- **Angles are in degrees**; `get_height`/`set_height` are size **levels 1–5**.

## Connecting

```python
import os
from minethon import create_bot

# Simple local server:
bot = create_bot(host="localhost", username="student_bot")

# The NTUST competition server (custom Drasl auth) — values from env vars:
bot = create_bot(
    host=os.environ["MC_HOST"],
    port=int(os.environ.get("MC_PORT", "25565")),
    username=os.environ["MC_USERNAME"],
    password=os.environ["MC_PASSWORD"],
    auth="mojang",
    auth_server=os.environ["MC_AUTH_SERVER"],      # snake_case kwargs
    session_server=os.environ["MC_SESSION_SERVER"],
)
```

`create_bot` returns immediately and connects in the background. **Always `bot.wait_spawn()` before doing anything in the world.**

## Quick Reference — synchronous student API

| Method | Returns | Purpose |
|--------|---------|---------|
| `wait_spawn()` | `None` | Block until the bot is in the world (call first) |
| `wait(seconds)` | `None` | Sleep while staying connected |
| `get_x() / get_y() / get_z()` | `float` | One coordinate |
| `get_pos()` | `(x, y, z)` | Position tuple |
| `get_yaw() / get_pitch()` | `float` | Facing, in **degrees** |
| `get_sneak()` | `bool` | Is sneaking? |
| `get_hand()` | `(name, count)` or `None` | Held item |
| `get_block(x, y, z)` | `str` or `None` | Block name at coords |
| `look_block()` | `((x,y,z), name)` or `None` | Block I'm aiming at |
| `find_block(name)` | `(x,y,z)` or `None` | Nearest block by name |
| `find_blocks(name, max=16)` | `list[(x,y,z)]` | Nearest N blocks by name |
| `move_forward(blocks=1)` | `(x,y,z)` | Walk forward; also `move_backward/left/right` |
| `jump()` | `(x,y,z)` | Jump once |
| `turn_left() / turn_right()` | `(yaw, pitch)` | Turn 90° |
| `turn(degrees)` | `(yaw, pitch)` | Relative turn (+ = left) |
| `set_turn(yaw)` | `(yaw, pitch)` | Face absolute yaw (degrees) |
| `look_at(x, y, z)` | `(yaw, pitch)` | Aim at a point |
| `get_height()` | `int` | Size level 1–5 |
| `set_height(level)` | `None` | Set size 1–5 (else `ValueError`) |
| `hold(name)` | `bool` | Equip item by name to hand |
| `unhold()` | `bool` | Put held item away |
| `drop()` | `bool` | Toss the held stack |
| `dig()` | `((x,y,z), name)` or `None` | Break the block I'm aiming at |
| `place()` | `((x,y,z), name)` or `None` | Place held block on the aimed face |
| `use()` | `bool` | Right-click aimed block, else use item |
| `sneak(on)` | `bool` | Hold/release sneak |
| `chat(obj)` | `None` | Send `str(obj)` to public chat |

Anything not listed (e.g. `bot.quit("bye")`, `bot.username`, `bot.entity`) falls through to the raw mineflayer proxy and still works.

## Example 1 — linear script that also reacts to chat

This is the canonical shape: bind events for reactions, run linear actions, stay alive.

```python
import os
from minethon import EventAdaptor, create_bot

bot = create_bot(host="localhost", username="student_bot")


class Commands(EventAdaptor):
    def on_chat(self, username, message, *_):
        if message == "stop":
            bot.quit("bye")


bot.bind(Commands())            # wire reactions first
bot.wait_spawn()                # block until in-world
bot.move_forward(5)             # walk forward 5 blocks (no pathfinder!)
dug = bot.dig()                 # break the block I'm aiming at -> ((x,y,z), name) or None
x, y, z = bot.get_pos()
bot.chat(f"我在 ({x:.1f}, {y:.1f}, {z:.1f})")
bot.run_forever()               # keep the process alive so on_chat keeps firing
```

## Example 2 — purely event-driven

```python
from minethon import EventAdaptor, create_bot

bot = create_bot(host="localhost", username="greeter")


class Greeter(EventAdaptor):
    def on_spawn(self):
        bot.chat("hello!")

    def on_chat(self, username, message, *_):
        if username == bot.username:
            return
        if message == "where":
            x, y, z = bot.get_pos()
            bot.chat(f"({x:.0f}, {y:.0f}, {z:.0f})")


bot.bind(Greeter())
bot.run_forever()
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `bot.pathfinder.goto(...)` / yaw math to move | `bot.move_forward(5)` |
| `bot.blockAtCursor()` / `block_at_cursor()` | `bot.look_block()` |
| `bot.dig(block)` (with an argument) | `bot.dig()` (no arg; digs the aimed block) |
| Doing world actions before spawn | `bot.wait_spawn()` first (else `NotSpawnedError`) |
| Linear script ends instantly, events never fire | end with `bot.run_forever()` |
| Treating angles as radians | student API is **degrees** |
| `bot.chat` only sends to one person | it's normal public chat; group visibility is a server plugin |

## Going deeper

See [api-reference.md](api-reference.md) for every method's full semantics, the complete `EventAdaptor` event list and handler signatures, all `create_bot` options, plugins (`load_plugin` / `require`), error classes, and runtime gotchas (callback thread, version pinning).
