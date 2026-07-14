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
  already spawned. **Call this once before any world action**; otherwise reads
  raise `NotSpawnedError`.
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
- `get_hand() -> tuple[str, int] | None` — `(item_name, count)`, or `None` when
  empty-handed.

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
  raises `ValueError`. Note: an entity's real scale is server-authoritative, so
  the in-world change depends on the competition server's plugin honouring it.

## Items

- `hold(name) -> bool` — equip the inventory item named `name` to the main hand.
  `True` on success, `False` if it isn't carried.
- `unhold() -> bool` — put the held item back; `False` if already empty-handed.
- `drop() -> bool` — toss the whole held stack; `False` if empty-handed.

## Actions (operate on the block/face you're aiming at)

- `dig() -> ((x,y,z), name) | None` — break the aimed block; returns what was
  broken, or `None` if nothing is in reach. (No argument — it's the renamed
  "break" action.)
- `place() -> ((x,y,z), name) | None` — place the held block against the aimed
  face; returns the new block's position+name, or `None`.
- `use() -> bool` — right-click: interact with the aimed block (door, button,
  lever…), or use the held item if not aiming at a block.
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
wire the instance with `bot.bind(instance)`. End the script with
`bot.run_forever()` so the process stays alive while events fire.

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

## `create_bot(**options)` — connection options

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

Returns a `Bot` immediately; connection happens in the background.

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

`set_height` raises the built-in `ValueError` for a level outside 1–5.

---

## Runtime gotchas

- **Spawn first.** World reads/actions before `wait_spawn()` raise
  `NotSpawnedError`.
- **Don't block in event handlers** — they run on the bridge callback thread.
- **Degrees, not radians**, throughout the student API.
- **Movement is approximate** (control-state + polling) and times out if stuck;
  it won't path around obstacles.
- **Version pinning**: bundled `mineflayer` / `vec3` / `mineflayer-pathfinder`
  auto-pin; any other npm package needs an explicit version in
  `load_plugin`/`require`.
- **Setup**: run `./setup.sh` once (installs Python deps + pinned npm packages).
  Needs Python 3.14+ and Node.js 22+.

---

## Recipes (student request → correct code)

Each assumes `bot = create_bot(...)` and (for linear tasks) `bot.wait_spawn()`.

**"Walk forward to a tree, chop the log, come back."**
```python
bot.wait_spawn()
spot = bot.find_block("oak_log")          # (x, y, z) or None
if spot:
    bot.look_at(*spot)                    # face it
    bot.move_forward(4)                   # close the gap (no pathfinder)
    bot.dig()                             # break the block I'm aiming at
    bot.move_backward(4)
```

**"Patrol: walk a 5×5 square forever."**
```python
bot.wait_spawn()
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
bot.wait_spawn()
for _ in range(3):
    x, y, z = bot.get_pos()
    bot.look_at(int(x), int(y) - 1, int(z))   # aim at the block under my feet
    if bot.dig() is None:                      # nothing left to dig
        break
    bot.wait(0.3)                              # let me fall onto the new floor
```

**"Grow to size 5, sneak, and announce it."**
```python
bot.wait_spawn()
bot.set_height(5)                         # 1..5 only, else ValueError
bot.sneak(True)
bot.chat(f"size={bot.get_height()}, sneaking={bot.get_sneak()}")
```

When a request mixes "do a sequence" with "react to chat/events", bind an
`EventAdaptor` for the reactions, run the linear part, then `bot.run_forever()`.
