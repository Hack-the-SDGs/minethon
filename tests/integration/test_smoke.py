"""Integration smoke: connect → spawn → read → chat → quit over the real bridge.

This is the minimum check that the JSPyBridge ↔ mineflayer path works end to
end. Run it before upgrading the pinned ``javascript`` (JSPyBridge) package or
bundled npm packages (see AGENTS.md 版本規則):

    uv run pytest -m integration

Target server defaults to an offline-mode server on ``localhost:25565``;
override with ``MINETHON_IT_HOST`` / ``MINETHON_IT_PORT`` /
``MINETHON_IT_USERNAME``. Unreachable server → the test skips.

The bot session runs in a subprocess on purpose: minethon ends the whole
process via ``os._exit`` when the server drops the bot (see
``_bot_runtime._stop_with_message``), which must not take pytest down with it,
and a wedged login (reachable port, unusable server) must hit the subprocess
timeout instead of hanging pytest forever. The parent only trusts the
``SMOKE_OK`` marker printed *before* ``bot.quit()``, so a hard exit can never
fake a pass.
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
_SMOKE_TIMEOUT_SECONDS = 90.0

_CHILD_SCRIPT = """
import os

HOST = os.environ.get("MINETHON_IT_HOST", "localhost")
PORT = int(os.environ.get("MINETHON_IT_PORT", "25565"))
USERNAME = os.environ.get("MINETHON_IT_USERNAME", "it_smoke")

try:
    from minethon import create_bot

    bot = create_bot(
        host=HOST,
        port=PORT,
        username=USERNAME,
        auth="offline",
        bypass_instruction_sleep=True,
    )
    bot.wait_spawn()
    pos = bot.get_pos()
    assert isinstance(pos, tuple) and len(pos) == 3, pos
    assert all(isinstance(axis, float) for axis in pos), pos
    bot.chat("minethon integration smoke")
    print("SMOKE_OK", flush=True)
except BaseException as exc:
    print(f"SMOKE_FAIL {type(exc).__name__}: {exc}", flush=True)
    os._exit(1)
# quit() fires minethon's end-handler, which hard-exits this process — fine
# here, the SMOKE_OK marker is already out.
bot.quit()
os._exit(0)
"""


def _server_reachable() -> bool:
    try:
        with socket.create_connection((_HOST, _PORT), _REACH_TIMEOUT_SECONDS):
            return True
    except OSError:
        return False


def test_connect_read_chat_quit() -> None:
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
        stdout, stderr = proc.communicate(timeout=_SMOKE_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
        pytest.fail(
            f"smoke child timed out after {_SMOKE_TIMEOUT_SECONDS}s — "
            f"server at {_HOST}:{_PORT} reachable but not usable?"
        )
    assert "SMOKE_OK" in stdout, (
        f"smoke child failed (exit {proc.returncode})\n"
        f"stdout:\n{stdout}\nstderr:\n{stderr}"
    )
