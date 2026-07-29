"""Internal JS bridge bootstrap.

Not part of the public API. Everything here returns raw JS proxies from
JSPyBridge; callers in `bot.py` are responsible for presenting Pythonic types.

Version pinning policy (AGENTS.md):
    npm packages are pinned to specific versions. First-run lazy install is
    avoided by running `./setup.sh` before the user's first script, which
    pre-installs the modules into the `javascript` package's node_modules.
"""

from __future__ import annotations

import atexit
import contextlib
import json
from typing import Any

from javascript import connection, eval_js
from javascript import require as _js_require

# Pinned — bumped by humans, never `latest`.
# Ref: mineflayer package.json engines.node >= 22
BUNDLED_VERSIONS: dict[str, str] = {
    "mineflayer": "4.37.0",
    "vec3": "0.1.10",
    "mineflayer-pathfinder": "2.4.5",
}
MINEFLAYER_VERSION = BUNDLED_VERSIONS["mineflayer"]
VEC3_VERSION = BUNDLED_VERSIONS["vec3"]


def _suppress_mojang_auth_warning() -> None:
    """Inject JS to intercept and drop specific auth deprecation stdout."""
    eval_js("""
        const original = console['warn'];
        console['warn'] = function(...args) {
            if (typeof args[0] === 'string') {
                if (args[0].includes('mojang auth servers no longer')) {
                    return;
                }
                if (args[0].includes('How-to-Migrate-Your-Mojang')) {
                    return;
                }
            }
            original.apply(console, args);
        };
    """)


def _suppress_via_parse_noise() -> None:
    """Drop console spam from packets ViaVersion/ViaBackwards mistranslates.

    When the server runs a version newer than mineflayer can speak natively and
    a Via proxy translates the stream, a few cosmetic packets still arrive with
    a layout the bundled schema can't read. protodef then floods stdout via
    `console.log(e.stack)` (protodef/src/serializer.js) even though the bot
    works fine.

    The logged arg is the stack STRING (not an Error). We swallow ONLY those
    known-cosmetic parse errors (matched by the compiled `packet_<name>` frame);
    every other log still prints. Add a name here if another packet leaks.
    """
    benign = ["world_particles"]
    markers = json.dumps([f"packet_{name}" for name in benign])
    # IIFE: eval_js shares one global scope, so keep locals from leaking.
    eval_js(f"""
        (function () {{
            const markers = {markers};
            const original = console['log'];
            console['log'] = function(...args) {{
                const s = args[0];
                if (typeof s === 'string'
                    && s.includes('PartialReadError')
                    && markers.some(m => s.includes(m))) {{
                    return;
                }}
                original.apply(console, args);
            }};
        }})();
    """)


_BRIDGE_EXIT_TIMEOUT = 2.0


def _stop_bridge_at_exit() -> None:
    """Tear down the node subprocess and its pipes on interpreter exit.

    Importing `javascript` spawns node, so even a bare `import minethon` leaves a
    live child behind; without this the interpreter exits with
    `ResourceWarning: subprocess <pid> is still running` plus unclosed
    BufferedReader/BufferedWriter (reproducible under
    `python -X dev -c "import minethon"`, and at pytest teardown).

    `connection.stop()` only calls `proc.terminate()` — it never reaps the child
    nor closes stdin/stderr (ref: javascript/connection.py `stop`), so we finish
    the job here. `proc.stdout` is None unless the bridge chose `PIPE` for it
    (notebook / redirected stdout), so closing it when set never touches
    `sys.stdout`.

    Best-effort by design: the bridge may already be gone, and a failure here
    must never turn a clean run into a crash. `_bot_runtime._stop_with_message`
    calls `os._exit`, which skips atexit entirely — it stops the bridge itself,
    so the two paths don't overlap.
    """
    with contextlib.suppress(Exception):
        connection.stop()
    proc = getattr(connection, "proc", None)
    if proc is None:
        return
    # Reap first: connection.com_io's read loop is gated on `proc.poll() is None`,
    # so a reaped child lets that daemon thread fall out before the pipes vanish.
    with contextlib.suppress(Exception):
        proc.wait(timeout=_BRIDGE_EXIT_TIMEOUT)
    for pipe in (proc.stdin, proc.stdout, proc.stderr):
        if pipe is not None:
            with contextlib.suppress(Exception):
                pipe.close()


atexit.register(_stop_bridge_at_exit)

_suppress_mojang_auth_warning()
_suppress_via_parse_noise()


def get_mineflayer() -> Any:
    """Load the pinned mineflayer module.

    Ref: mineflayer/index.js — `module.exports.createBot`
    """
    return _js_require("mineflayer", MINEFLAYER_VERSION)


def get_vec3() -> Any:
    """Load the pinned vec3 module (position math).

    Ref: vec3/index.js — `module.exports.Vec3`
    """
    return _js_require("vec3", VEC3_VERSION)
