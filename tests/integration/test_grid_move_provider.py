"""Opt-in integration checks for the grid_move v1 scoreboard protocol.

These tests need server-side fixtures and therefore skip unless their specific
environment flag is present. They document the two deployment-sensitive facts:

* ``MINETHON_IT_UNDISPLAYED_PROVIDER`` names a trigger objective whose title is
  ``minethon:grid_move:v1`` and which has a score for the test bot, but is not in
  any display slot. Vanilla does not track it to the client, so discovery must
  return no provider.
* ``MINETHON_IT_Q10_GRID=1`` requires an active q10 stage-one run for the test
  bot. Ten public ``move_forward(1)`` calls must each commit one exact cell,
  whether ACK arrives as a score packet or trigger re-enable completion.
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
_TEST_TIMEOUT_SECONDS = 120.0


def _server_reachable() -> bool:
    try:
        with socket.create_connection((_HOST, _PORT), _REACH_TIMEOUT_SECONDS):
            return True
    except OSError:
        return False


def _run_child(script: str, marker: str) -> None:
    if not _server_reachable():
        pytest.skip(f"no Minecraft server reachable at {_HOST}:{_PORT}")

    proc = subprocess.Popen(  # noqa: S603 — own interpreter + static test script
        [sys.executable, "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=_TEST_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            proc.kill()
        else:
            os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
        pytest.fail(f"grid provider child timed out after {_TEST_TIMEOUT_SECONDS}s")
    assert marker in stdout, (
        f"grid provider child failed (exit {proc.returncode})\n"
        f"stdout:\n{stdout}\nstderr:\n{stderr}"
    )


def test_undisplayed_provider_is_not_discovered() -> None:
    objective = os.environ.get("MINETHON_IT_UNDISPLAYED_PROVIDER")
    if not objective:
        pytest.skip(
            "set MINETHON_IT_UNDISPLAYED_PROVIDER to a server-side provider "
            "objective that deliberately has no display slot"
        )

    script = f"""
import os

from minethon import create_bot

bot = create_bot(
    host=os.environ.get("MINETHON_IT_HOST", "localhost"),
    port=int(os.environ.get("MINETHON_IT_PORT", "25565")),
    username=os.environ.get("MINETHON_IT_USERNAME", "it_grid_hidden"),
    auth="offline",
    bypass_instruction_sleep=True,
)
bot.wait_spawn()
assert {objective!r} not in list(bot.scoreboards)
assert bot._grid_move_context() is None
print("UNDISPLAYED_PROVIDER_OK", flush=True)
bot.quit()
"""
    _run_child(script, "UNDISPLAYED_PROVIDER_OK")


def test_q10_provider_moves_ten_exact_cells() -> None:
    if os.environ.get("MINETHON_IT_Q10_GRID") != "1":
        pytest.skip("set MINETHON_IT_Q10_GRID=1 with an active q10 stage-one run")

    script = """
import os

from minethon import create_bot

bot = create_bot(
    host=os.environ.get("MINETHON_IT_HOST", "localhost"),
    port=int(os.environ.get("MINETHON_IT_PORT", "25565")),
    username=os.environ.get("MINETHON_IT_USERNAME", "G0_labfire_1"),
    auth="offline",
    bypass_instruction_sleep=True,
)
bot.wait_spawn()
sequences = []
for _ in range(10):
    before = bot.get_pos()
    after = bot.move_forward(1)
    dx = abs(after[0] - before[0])
    dz = abs(after[2] - before[2])
    assert abs(dx + dz - 1.0) <= 1e-9, (before, after)
    assert abs(after[0] % 1.0 - 0.5) <= 1e-9, after
    assert abs(after[2] % 1.0 - 0.5) <= 1e-9, after
    objective, username, ack = bot._grid_move_context()
    assert objective == "q.labfire.step", objective
    if ack is None:
        assert objective in (bot._enabled_trigger_objectives() or set())
        sequences.append(bot._grid_move_sequence)
    else:
        assert ack < 0, ack
        sequences.append(abs(ack) // 10)
assert all(right == left + 1 for left, right in zip(sequences, sequences[1:]))
print("Q10_GRID_MOVE_OK", flush=True)
bot.quit()
"""
    _run_child(script, "Q10_GRID_MOVE_OK")
