"""Integration: run the velocity-repair JS against a real node EventEmitter.

`_bot_runtime._VELOCITY_REPAIR_JS` is a string of JavaScript — no unit test
can prove it parses, registers, or fixes anything. This test evaluates it over
JSPyBridge against a fake bot built from node's own `events` module and replays
the three packet shapes that matter:

* nested 1.21.2+ `velocity` (the shape mineflayer 4.37.0 mis-parses into NaN)
  must be re-parsed into `raw / 8000` per axis;
* legacy flat `velocityX` must be left untouched (mineflayer already parsed
  it correctly on those servers);
* an unknown entityId must be ignored without throwing.

Unlike the other integration tests this needs **no Minecraft server** — only
the node runtime JSPyBridge ships against. It still lives under the
`integration` marker because the unit CI job runs on a fresh checkout with no
bridge node_modules and must never spawn node.

Same subprocess isolation as `test_smoke.py`: the bridge owns atexit and
signal behaviour, which must not leak into the pytest process.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

pytestmark = pytest.mark.integration

_CHILD_TIMEOUT_SECONDS = 120.0

_CHILD_SCRIPT = """
import os


def finish(code):
    # os._exit alone leaks the node subprocess, which inherited this process's
    # stdout — the parent's communicate() would then block on a pipe that never
    # closes. Ref: javascript/connection.py — the node Popen inherits stdout.
    try:
        from javascript import connection
        connection.stop()
    except BaseException:
        pass
    os._exit(code)


try:
    from javascript import eval_js

    from minethon._bot_runtime import _VELOCITY_REPAIR_JS

    install = eval_js(_VELOCITY_REPAIR_JS)

    fake = eval_js('''
    return (() => {
      const { EventEmitter } = require('events')
      const bot = new EventEmitter()
      bot._client = new EventEmitter()
      const vec = (x, y, z) => ({
        x, y, z,
        set (a, b, c) { this.x = a; this.y = b; this.z = c }
      })
      bot.entities = { 7: { velocity: vec(9, 9, 9) }, 8: { velocity: vec(9, 9, 9) } }
      return bot
    })()
    ''')

    install(fake)

    def velocity_of(entity_id):
        v = fake.entities[entity_id].velocity
        return (float(v.x), float(v.y), float(v.z))

    def close(got, want):
        return all(abs(g - w) < 1e-9 for g, w in zip(got, want))

    # Nested 1.21.2+ shape: raw shorts divided by 8000, exactly what
    # mineflayer's own conversions.fromNotchVelocity would have produced.
    fake._client.emit(
        "entity_velocity",
        {"entityId": 7, "velocity": {"x": 8000, "y": -8000, "z": 4000}},
    )
    got = velocity_of(7)
    assert close(got, (1.0, -1.0, 0.5)), f"nested shape not repaired: {got}"

    # Legacy flat shape: mineflayer parsed it correctly, the repair must not
    # second-guess it.
    fake._client.emit(
        "entity_velocity",
        {"entityId": 8, "velocityX": 8000, "velocityY": 8000, "velocityZ": 8000},
    )
    got = velocity_of(8)
    assert close(got, (9.0, 9.0, 9.0)), f"flat shape was touched: {got}"

    # Unknown entity: emit() re-raises a listener throw synchronously, so
    # surviving this call is the assertion.
    fake._client.emit(
        "entity_velocity",
        {"entityId": 99, "velocity": {"x": 1, "y": 2, "z": 3}},
    )

    print("VELOCITY_OK", flush=True)
    finish(0)
except AssertionError as exc:
    print(f"VELOCITY_FAIL {exc}", flush=True)
    finish(1)
except BaseException as exc:  # noqa: BLE001 — the parent needs the reason
    print(f"VELOCITY_ERROR {type(exc).__name__}: {exc}", flush=True)
    finish(1)
"""


def test_velocity_repair_js_fixes_nested_and_spares_flat_packets() -> None:
    proc = subprocess.run(  # noqa: S603 — fixed argv, our own interpreter
        [sys.executable, "-c", _CHILD_SCRIPT],
        capture_output=True,
        text=True,
        timeout=_CHILD_TIMEOUT_SECONDS,
        check=False,
    )
    output = proc.stdout + proc.stderr
    assert "VELOCITY_OK" in output, output
