# minethon — full API reference

Companion to [SKILL.md](SKILL.md). Read SKILL.md first for the overview, the
two API styles, and the Quick Reference table. This file has full semantics,
the event list, `create_bot` options, plugins, errors, gotchas, and recipes.

All synchronous student methods live on `Bot` (the object `create_bot` returns).
They **block** until the action completes and use **native Python types** —
no `Vec3`/`Block`/`Item` objects, no `await`.

---

## Lifecycle

- `wait_spawn() -> None` — Block until the bot has spawned. Returns instantly if
  already spawned. Needed once before any world action **on the explicit-options
  form of `create_bot` only** — the camp shorthand already waited. Otherwise
  reads raise `NotSpawnedError`.
- `wait(seconds: float) -> None` — Sleep `seconds` while the connection stays
  alive. Use between actions (`bot.wait(0.5)`).

## Position & orientation (read)

- `get_x() / get_y() / get_z() -> float` — single coordinate. `y` is height.
- `get_pos() -> tuple[float, float, float]` — `(x, y, z)`.
- `get_yaw() -> float` — horizontal facing in **degrees**, normalised to
  `[0, 360)`. `0` faces −Z (north); larger yaw turns counter-clockwise (left).
- `get_pitch() -> float` — vertical facing in degrees (`+90` up, `−90` down).

## State (read)

- `get_sneak() -> bool` — currently sneaking?
- `is_riding() -> bool` — currently sitting on / riding another entity (a boat,
  a minecart, or another player via the server's sit plugin). Use it to wait for
  a mount to take effect: `while not bot.is_riding(): ...`. Always use this
  rather than reading `bot.entity.vehicle` or `vehicle.passengers` — mineflayer
  doesn't clear those when the bot gets off, so they keep pointing at the old
  vehicle until it next mounts something. `is_riding()` is the repaired accessor.
- `get_hand() -> tuple[str, int] | None` — `(item_name, count)`, or `None` when
  empty-handed.
- `get_player_pos(username) -> tuple[float, float, float]` — the named player's
  live `(x, y, z)`, read at call time. Lets a follow loop do
  `bot.look_at(*bot.get_player_pos(name))` then `bot.move_forward()` without
  touching `Vec3`. Raises `PlayerNotFoundError` when the player is offline, in
  another world, or outside the bot's loaded entity range.

## World sensing (read)

- `get_block(x, y, z) -> str | None` — block name (e.g. `"stone"`) at integer
  coords, or `None` if that chunk isn't loaded.
- `get_block_property(x, y, z, property_name) -> str | int | bool | None` — get
  a specific block state property (e.g. `"lit"` for redstone lamps, `"facing"`
  for furnaces, `"powered"` for levers) of the block at integer coordinates.
  Returns the property value, or `None` if the chunk isn't loaded or the block
  does not have this property.
- `look_block() -> tuple[tuple[int,int,int], str] | None` — the block the bot is
  aiming at as `((x, y, z), name)`, or `None` if nothing is within ~6 blocks.
- `get_front_block() -> str | None` — name of the solid block one step ahead
  (feet level first, then head level), or `None` when only air/liquid is ahead.
  Fire **is** reported, so a script can check
  `bot.get_front_block() == "fire"` before acting. No coordinate: it is
  always one step along the facing axis. Note `None` here means "nothing solid
  ahead", not "read failed" as it does for `get_block`.
- `find_block(name) -> tuple[int,int,int] | None` — nearest block matching the
  name, or `None`. Names are Minecraft ids like `"diamond_ore"`, `"oak_log"`.
- `find_blocks(name, max=16) -> list[tuple[int,int,int]]` — up to `max` nearest
  matches, closest first; empty list if none / unknown name.

## Movement

Relative to the bot's current facing. No pathfinder — these press a control key
and poll position until the distance is covered, with a safety timeout so
walking into a wall can't hang the script.

- `move_forward(blocks=1.0) -> (x, y, z)` — walk forward; returns new position.
- `move_backward(blocks=1.0) -> (x, y, z)`
- `move_left(blocks=1.0) -> (x, y, z)` — strafe left.
- `move_right(blocks=1.0) -> (x, y, z)` — strafe right.
- `jump() -> (x, y, z)` — one hop; returns position just after takeoff.

## Vehicles

- `dismount() -> None` — get off the current vehicle by tapping sneak, the key a
  player presses to get off; your own sneak state is restored afterwards. Safe
  to call when the bot isn't riding: it does nothing. Blocks until the server
  actually takes the bot off (up to 2s) and raises `MinethonError` if it never
  does — it will not silently return as though it worked. Inside an event
  handler it sends the input and returns immediately instead of waiting, since
  the handler occupies the thread that would deliver the confirmation. Always
  use this rather than mineflayer's own `dismount()`, which presses jump instead
  on 1.21.3+ and emits a fatal bot `error` when there is no vehicle.

## Orientation (write) — all angles in degrees

- `turn_left() -> (yaw, pitch)` — turn 90° left.
- `turn_right() -> (yaw, pitch)` — turn 90° right.
- `turn(degrees) -> (yaw, pitch)` — relative turn; positive = left.
- `set_turn(yaw) -> (yaw, pitch)` — face an absolute yaw; pitch unchanged.
- `look_at(x, y, z) -> (yaw, pitch)` — aim the head at an exact point.

## Size

- `get_height() -> int` — size **level 1–5**, read from the server-reported
  `scale` attribute (`1` when the server hasn't sent one).
- `set_height(level) -> None` — request a size level; `level` outside `1..5`
  raises `ValueError`, and so does a fractional one (`set_height(3.9)` is an
  error, **not** a silent truncation to `3`). Note: an entity's real scale is
  server-authoritative, so the in-world change depends on the competition
  server's plugin honouring it.

## Items

- `hold(name) -> bool` — equip the inventory item named `name` to the main hand.
  `True` on success, `False` if it isn't carried.
- `unhold() -> bool` — put the held item back; `False` if already empty-handed.
- `drop(name_or_id=None, count=None) -> bool` — toss the whole held stack if no args; or toss item from inventory by name (e.g. `"gold_ingot"`) or ID. `False` if empty-handed or not carried.

## Actions (operate on the block/face you're aiming at)

- `dig() -> ((x,y,z), name) | None` — break the aimed block; if not aiming at
  one, falls back to the solid block one step ahead. Returns what was broken,
  `None` when there is nothing solid to break — or when the block is too hard
  to break in reasonable time (prints a friendly line). (No argument — it's
  the renamed "break" action.)
- `place() -> ((x,y,z), name) | None` — place the held block against the aimed
  face; returns the new block's position+name, or `None` when nothing is in
  reach or the hand is empty (`hold(...)` something first).
- `use() -> bool` — right-click: interact with the aimed block (door, button,
  lever…), or use the held item if not aiming at a block.
- `use_player(username) -> bool` — look at the named player's current entity
  center and right-click it. This reads the live position immediately before
  interacting, so callers do not calculate yaw/pitch for players at different
  heights. Returns `True`; raises `PlayerNotFoundError` when the player is
  offline, in another world, or outside the bot's loaded entity range. The
  server still enforces its entity-interaction distance.
- `action(name, value=None) -> None` — ask the **server** to perform a named
  quest action. Sends the vanilla trigger `/trigger <username>_<action>`
  (all lowercased; spaces/hyphens → underscores), with `value` as an optional
  integer payload (`set <value>`). The competition datapack validates the
  request (right bot, quest active, target in front…) and performs or silently
  ignores it — there is **no client-side effect**, so a dropped connection
  mid-action can never damage the map. Example: bot `G1_labfire_1` calling
  `action("put out")` fires `/trigger g1_labfire_1_put_out`. Bad characters in
  `name` raise `ValueError`. Known labfire actions: `action("put out")`
  (extinguish the fire in front) and `action("snap")` — in labfire stages 2–3
  the server takes over movement (slower speed, grid snapping / step
  rejection); `action("snap")` asks it to align the bot to the current cell
  centre before turning or moving.
- `sneak(on: bool) -> bool` — hold (`True`) or release (`False`) sneak; a
  persistent state. Returns the new state.

## Chat

- `chat(obj) -> None` — send `str(obj)` as a normal public chat message. Group
  visibility is handled by the competition's server-side chat plugin; the bot
  just sends/receives normally. Accepts any object: `bot.chat(bot.get_pos())`.

Anything not on this list falls through to the raw mineflayer proxy, so
`bot.quit("reason")`, `bot.username`, `bot.entity`, `bot.players`, etc. still work.

---

## Event API — `EventAdaptor`

Subclass `EventAdaptor`, override the `on_<event>` methods you care about, and
wire the instance with `bot.bind(instance)`. Ending with `bot.run_forever()` is
optional (see `create_bot` above) but states the intent for an event-only script.

```python
from minethon import EventAdaptor, create_bot

bot = create_bot(host="localhost", username="pybot")


class My(EventAdaptor):
    def on_spawn(self):
        bot.chat("hi")

    def on_chat(self, username, message, *_):   # *_ absorbs extra params
        if message == "quit":
            bot.quit("bye")


bot.bind(My())
bot.run_forever()
```

**Handlers run on the JSPyBridge callback thread — do not block in them** (no
long `wait()`, no long loops). Keep handlers short; do heavy/linear work on the
main thread.

Commonly used events (override only what you need; trailing params can be
absorbed with `*_`):

| Method | Fires when | Key params |
|--------|-----------|------------|
| `on_spawn(self)` | bot enters the world | — |
| `on_chat(self, username, message, *_)` | a player chats | `username`, `message` |
| `on_whisper(self, username, message, *_)` | a private message | `username`, `message` |
| `on_death(self)` | bot dies | — |
| `on_health(self)` | health/food changes | read `bot.health`, `bot.food` |
| `on_player_joined(self, player)` | someone joins | `player` |
| `on_player_left(self, player)` | someone leaves | `player` |
| `on_entity_hurt(self, entity, *_)` | an entity is hurt | `entity` |
| `on_kicked(self, reason, logged_in)` | server kicks the bot | `reason` |
| `on_end(self, reason)` | connection ends | `reason` |
| `on_error(self, err)` | an error is raised | `err` |
| `on_message(self, msg, position)` | any system/chat message | `msg` |

The full event set (≈90 methods, e.g. `on_move`, `on_physics_tick`,
`on_block_update`, `on_player_collect`, pathfinder's `on_goal_reached` /
`on_path_update`) is the `on_<event>` method list on `EventAdaptor` — your IDE's
"override methods" shows them all with correct signatures. `BotEvent` is a
`StrEnum` of the raw event-name constants (for logging/checks), not for
registration.

`bot.bind(handlers)` returns the handlers instance (chainable) and only wires
methods you actually overrode.

---

## `create_bot(...)` — connection

### Form 1: camp shorthand (default for student scripts)

`create_bot("g_swim")` / `create_bot("swim")`. The first positional argument is
a task shorthand; host and credentials are resolved from this PC's identity file
(`~/.htsdg.json`, written once per machine by staff — see `pc_setup/README.md`).

| Shorthand | Username | Account |
|-----------|----------|---------|
| `"g_swim"` / `"g-swim"` | `G<group>_swim` | shared by the group |
| `"swim"` | `U<computer>_swim` | that PC only |

**This form blocks until the bot has spawned and settled**, then returns — so
the caller must NOT add `bot.wait_spawn()`. Explicit keyword options still
override the resolved ones. Raises `MinethonError` (with a Chinese
"go find staff" message) when the identity file is missing or corrupt.

### Form 2: explicit options

snake_case keyword args, converted to mineflayer's camelCase internally.

| Option | Meaning |
|--------|---------|
| `host` | server address |
| `port` | server port (default 25565) |
| `username` | bot's name (or account email for premium auth) |
| `password` | account password (premium / Drasl auth) |
| `version` | force a protocol version (e.g. `"1.20.4"`); omit to auto-detect |
| `auth` | `"mojang"`, `"microsoft"`, or `"offline"` |
| `auth_server` | custom auth server URL (Drasl / Yggdrasil-compatible) |
| `session_server` | custom session server URL |

Returns a `Bot` immediately; connection happens in the background, so this form
**does** need `bot.wait_spawn()` before world reads/actions.

### Both forms

| Option | Meaning |
|--------|---------|
| `instruction_sleep` | seconds to pause after each action command (default `0.2`, so students can watch each step) |
| `bypass_instruction_sleep` | `True` sets that pause to 0 |

`create_bot` also registers an `atexit` keep-alive: after the last line of a
straight-line script runs, the bot stays connected and events keep firing. A
trailing `bot.run_forever()` is therefore optional — it makes the intent
explicit for a purely event-driven script, but nothing breaks without it.

---

## Plugins (advanced)

- `bot.load_plugin(name, version=None, *, export_key=None, **options)` — install
  a mineflayer plugin. The **bundled** `mineflayer-pathfinder` may omit the
  version; every other package needs an explicit version string. Returns the raw
  JS module.
- `bot.require(name, version)` — load any npm module and get its raw proxy
  (escape hatch for plugins that need manual setup). Version is mandatory for
  non-bundled packages.

Pathfinder is the only typed/documented plugin. After
`bot.load_plugin("mineflayer-pathfinder")`, `bot.pathfinder.goto(...)` is
available — but for ordinary "walk a few blocks" tasks prefer the student
`move_forward/backward/left/right`; reach for pathfinder only for real
navigation around obstacles.

---

## Errors

All inherit from `MinethonError` (import from `minethon`):

- `MinethonError` — base class.
- `NotSpawnedError` — a world read/action was used before `wait_spawn()`.
- `PlayerNotFoundError` — a named player couldn't be found.
- `PluginNotInstalledError` — a plugin attribute (e.g. `bot.pathfinder`) used
  before `load_plugin`.
- `VersionPinRequiredError` — a non-bundled package was loaded without a version.

`set_height` raises the built-in `ValueError` for a level outside 1–5 or a
fractional one; a non-number raises `TypeError`.

---

## Runtime gotchas

- **Spawn first — explicit-options form only.** The shorthand already waited;
  see `create_bot` above.
- **Degrees, not radians**, throughout the student API.
- **Movement is approximate** (control-state + polling) and times out if stuck;
  it won't path around obstacles.
- **A misspelled name doesn't raise `AttributeError`.** `Bot.__getattr__`
  forwards to the JS proxy, which answers `None` for anything it doesn't have —
  so `bot.mvoe_forward(3)` surfaces as
  `TypeError: 'NoneType' object is not callable`, and a misspelled attribute
  (`bot.usernaem`) silently evaluates to `None`. Check spelling first when
  debugging either symptom.
- **Setup**: run `./setup.sh` once (installs Python deps + pinned npm packages).
  Needs Python 3.14+ and Node.js 22+.

---

## Recipes (student request → correct code)

Each assumes `bot = create_bot("g_<task>")` (already spawned). With the
explicit-options form, add `bot.wait_spawn()` as the first line of each.

**"Walk forward to a tree, chop the log, come back."**
```python
spot = bot.find_block("oak_log")          # (x, y, z) or None
if spot:
    bot.look_at(*spot)                    # face it
    bot.move_forward(4)                   # close the gap (no pathfinder)
    bot.dig()                             # break the block I'm aiming at
    bot.move_backward(4)
```

**"Patrol: walk a 5×5 square forever."**
```python
while True:
    for _ in range(4):
        bot.move_forward(5)
        bot.turn_right()
```

**"Answer chat: reply with my coordinates when someone says 'where'."**
```python
class Answers(EventAdaptor):
    def on_chat(self, username, message, *_):
        if message == "where":
            x, y, z = bot.get_pos()
            bot.chat(f"({x:.0f}, {y:.0f}, {z:.0f})")

bot.bind(Answers())
bot.run_forever()
```

**"Dig straight down 3 blocks."**
```python
for _ in range(3):
    x, y, z = bot.get_pos()
    bot.look_at(int(x), int(y) - 1, int(z))   # aim at the block under my feet
    if bot.dig() is None:                      # nothing left to dig
        break
    bot.wait(0.3)                              # let me fall onto the new floor
```

**"Grow to size 5, sneak, and announce it."**
```python
bot.set_height(5)                         # 1..5 only, else ValueError
bot.sneak(True)
bot.chat(f"size={bot.get_height()}, sneaking={bot.get_sneak()}")
```

When a request mixes "do a sequence" with "react to chat/events", bind an
`EventAdaptor` for the reactions, run the linear part, then `bot.run_forever()`.
