"""Integration: verify the premise the `set_passengers` repair rests on.

`_bot_runtime._clear_stale_vehicle` assumes vanilla's dismount reaches the
client as a `set_passengers` whose `entityId` is the *vehicle* and whose
`passengers` no longer contain the bot. Every unit test asserts that shape
rather than observing it, so this is the only check that the repair works
against a real server:

    uv run pytest -m integration

Requires a rideable entity within reach. The child tries ``/summon`` first (a
no-op unless the account is opped) and otherwise looks for one already nearby;
finding none, it skips — an empty world proves nothing either way. **A skip
therefore verifies nothing**: to actually exercise the premise, op the test
account or park a boat within ``MOUNT_RANGE`` of the spawn point. Failing to
board a vehicle that *was* in range is a failure, not a skip.

Same subprocess isolation as ``test_smoke.py``: minethon ends the whole process
via ``os._exit`` on disconnect, which must not take pytest with it.
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys

import pytest

pytestmark = pytest.mark.integration

_HOST = os.environ.get("MINETHON_IT_HOST", "localhost")
_PORT = int(os.environ.get("MINETHON_IT_PORT", "25565"))
_REACH_TIMEOUT_SECONDS = 5.0
_RIDE_TIMEOUT_SECONDS = 120.0

_CHILD_SCRIPT = """
import os
import time

HOST = os.environ.get("MINETHON_IT_HOST", "localhost")
PORT = int(os.environ.get("MINETHON_IT_PORT", "25565"))
USERNAME = os.environ.get("MINETHON_IT_USERNAME", "it_vehicle")

# Anything a player can sit on. The bot only needs one of them in range.
RIDEABLE = {
    "boat", "oak_boat", "birch_boat", "spruce_boat", "chest_boat",
    "minecart", "chest_minecart", "pig", "horse", "donkey", "mule",
    "camel", "strider", "llama",
}
SETTLE_SECONDS = 2.0
POLL_SECONDS = 0.2
STATE_TIMEOUT_SECONDS = 10.0
# Mounting is a server-side reach check; anything further away just fails.
MOUNT_RANGE = 4.0


def finish(code):
    # os._exit alone leaks the node subprocess, which inherited this process's
    # stdout — the parent's communicate() would then block on a pipe that never
    # closes and every outcome would surface as a timeout. Ref:
    # javascript/connection.py — the node Popen inherits sys.stdout.
    # Imported here so a bridge that fails to import still reaches the marker
    # print in the caller rather than dying bare.
    try:
        from javascript import connection
        connection.stop()
    except BaseException:
        pass
    os._exit(code)


seen_dismount = []
seen_packets = []

try:
    from javascript import On

    from minethon import EventAdaptor, create_bot
    from minethon.errors import MinethonError

    bot = create_bot(
        host=HOST,
        port=PORT,
        username=USERNAME,
        auth="offline",
        bypass_instruction_sleep=True,
    )

    class Watch(EventAdaptor):
        def on_dismount(self, vehicle=None):
            seen_dismount.append(vehicle)

    bot.bind(Watch())

    # Record the raw packets so the run can prove *which* path did the work.
    # `bot._js._client`, not `bot._client`: Bot.__getattr__ refuses every
    # underscore name, so the latter is an AttributeError.
    @On(bot._js._client, "set_passengers")
    def _record(packet, *_a, **_k):
        seen_packets.append((packet["entityId"], list(packet["passengers"])))

    bot.wait_spawn()

    def distance_to(entity):
        bx, by, bz = bot.get_pos()
        pos = entity.position
        dx, dy, dz = float(pos.x) - bx, float(pos.y) - by, float(pos.z) - bz
        return (dx * dx + dy * dy + dz * dz) ** 0.5

    def find_rideable():
        entities = bot.entities
        try:
            keys = list(entities)
        except TypeError:
            # Proxy.__next__ compares self._ix against a `length` that stays
            # None for a JS object with no keys at all. Can't happen on a live
            # connection (the bot's own entity is always there), but a crash
            # here would read as a failure rather than "nothing to ride".
            return None
        for key in keys:
            entity = entities[key]
            if entity is None:
                continue
            name = getattr(entity, "name", None)
            if name is None or str(name) not in RIDEABLE:
                continue
            if distance_to(entity) <= MOUNT_RANGE:
                return entity
        return None

    def wait_until(predicate):
        deadline = time.monotonic() + STATE_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(POLL_SECONDS)
        return False

    # No-op unless the account is opped; harmless either way.
    bot.chat("/summon minecraft:oak_boat ~ ~ ~")
    time.sleep(SETTLE_SECONDS)

    target = find_rideable()
    if target is None:
        print("VEHICLE_NONE no rideable entity within reach", flush=True)
        finish(0)

    if bot.is_riding():
        # Spawned already seated — nothing to prove about a mount we didn't do.
        print("VEHICLE_NONE the bot spawned already riding something", flush=True)
        finish(0)
    vehicle_id = int(target.id)
    bot.mount(target)
    if not wait_until(bot.is_riding):
        # A rideable was in range, so this is a real failure, not an unusable
        # world — folding it into the skip would hide a mount regression.
        print("MOUNT_FAIL never got aboard a reachable vehicle", flush=True)
        finish(1)
    print("MOUNT_OK", flush=True)
    # Reset both records, then confirm the bot is still aboard immediately
    # before pressing sneak — otherwise a boat drifting apart on its own would
    # satisfy every marker below and the run would "pass" having proved nothing
    # about the input.
    seen_packets.clear()
    seen_dismount.clear()
    if not bot.is_riding():
        print("VEHICLE_NONE came off on its own before the test could act",
              flush=True)
        finish(0)

    # dismount() blocks until the server acts and raises if it never does, so
    # there is nothing left to poll — catch the raise separately from the
    # generic handler so "the server ignored the input" reads as its own
    # outcome rather than an unexpected crash.
    try:
        bot.dismount()
    except MinethonError as exc:
        print(f"DISMOUNT_FAIL {exc}", flush=True)
        finish(1)
    if bot.is_riding():
        print("DISMOUNT_FAIL dismount() returned while still riding", flush=True)
        finish(1)
    print("DISMOUNT_OK", flush=True)

    if not wait_until(lambda: bool(seen_dismount)):
        print("EVENT_FAIL on_dismount never fired", flush=True)
        finish(1)
    print("EVENT_OK", flush=True)

    # The load-bearing premise: the dismount reaches the client as a
    # set_passengers naming the *vehicle*, with the bot no longer listed. If
    # this fails, `_clear_stale_vehicle`'s detection is built on the wrong
    # packet shape and only happened to work for some other reason.
    bot_id = int(bot.entity.id)
    matching = [
        entry
        for entry in seen_packets
        if entry[0] == vehicle_id and bot_id not in entry[1]
    ]
    if not matching:
        print(f"SHAPE_FAIL vehicle={vehicle_id} bot={bot_id} saw={seen_packets}",
              flush=True)
        finish(1)
    print(f"SHAPE_OK {matching}", flush=True)
except BaseException as exc:
    print(f"VEHICLE_FAIL {type(exc).__name__}: {exc}", flush=True)
    finish(1)
bot.quit()
finish(0)
"""


def _server_reachable() -> bool:
    try:
        with socket.create_connection((_HOST, _PORT), _REACH_TIMEOUT_SECONDS):
            return True
    except OSError:
        return False


def test_dismount_clears_is_riding_against_a_real_server() -> None:
    if not _server_reachable():
        pytest.skip(f"no Minecraft server reachable at {_HOST}:{_PORT}")

    # New session so a timeout can kill the whole process group — otherwise
    # JSPyBridge's node grandchild survives the kill and keeps the bot online.
    proc = subprocess.Popen(  # noqa: S603 — fixed argv: own interpreter + static script
        [sys.executable, "-c", _CHILD_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=_RIDE_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
        pytest.fail(
            f"vehicle child timed out after {_RIDE_TIMEOUT_SECONDS}s — "
            f"server at {_HOST}:{_PORT} reachable but not usable?"
        )
    if "VEHICLE_NONE" in stdout:
        pytest.skip(f"nothing to ride on this server: {stdout.strip()}")
    report = f"(exit {proc.returncode})\nstdout:\n{stdout}\nstderr:\n{stderr}"
    assert "MOUNT_OK" in stdout, f"could not mount {report}"
    assert "DISMOUNT_OK" in stdout, f"is_riding() stuck after dismount {report}"
    assert "EVENT_OK" in stdout, f"on_dismount never fired {report}"
    assert "SHAPE_OK" in stdout, (
        f"dismount did not arrive as the set_passengers shape the repair "
        f"detects — its premise is wrong {report}"
    )
