"""Unit tests for the knockback (`entity_velocity`) NaN repair wiring.

mineflayer 4.37.0 gates the 1.21.2+ nested `velocity` packet shape behind
`supportFeature('entityVelocityIsLpVec3')`, a feature the minecraft-data it
installs against never shipped, so the legacy branch reads `packet.velocityX`
(undefined) and writes NaN into `entity.velocity`. The first hit the bot takes
then NaN-poisons `bot.entity.position` through the physics tick, and every
position read in Python comes back None. `create_bot` installs a node-side
listener that re-parses the nested shape.

The JS logic itself runs in node and is exercised end to end by
`tests/integration/test_velocity_repair_js.py` (node only, no Minecraft server).
What belongs here is the Python wiring around it: the guard for a missing
protocol client, the eval/install handshake, and the call site in create_bot.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

import minethon._bot_runtime as rt


def test_missing_protocol_client_warns_instead_of_crashing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evaluated: list[str] = []
    monkeypatch.setattr(rt, "eval_js", evaluated.append)

    with pytest.warns(RuntimeWarning, match="擊退"):
        rt._install_velocity_repair(SimpleNamespace(_client=None))

    # Nothing to attach the listener to — eval_js must not run (it would spawn
    # a node process just to build an installer that has no client to serve).
    assert evaluated == []


def test_repair_evaluates_the_template_and_installs_on_the_js_bot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    installed: list[Any] = []

    def fake_eval_js(code: str) -> Any:
        assert code is rt._VELOCITY_REPAIR_JS
        return installed.append

    monkeypatch.setattr(rt, "eval_js", fake_eval_js)
    js_bot = SimpleNamespace(_client=SimpleNamespace())

    rt._install_velocity_repair(js_bot)

    # The evaluated template returns a JS arrow function; the repair must call
    # it with the raw JS bot so the listener ends up on that bot's _client.
    assert installed == [js_bot]


def test_create_bot_installs_the_repair(monkeypatch: pytest.MonkeyPatch) -> None:
    # The tests above drive _install_velocity_repair directly, so without this
    # the call site in create_bot could be deleted with every test still green —
    # the exact way two earlier repairs in this repo once shipped as dead code.
    installed: list[Any] = []
    js_bot = SimpleNamespace(_client=SimpleNamespace(), vehicle=None)

    monkeypatch.setattr(rt, "eval_js", lambda _code: installed.append)
    monkeypatch.setattr(rt, "On", lambda *_a, **_k: lambda fn: fn)
    monkeypatch.setattr(rt, "Once", lambda *_a, **_k: lambda fn: fn)
    monkeypatch.setattr(
        rt, "get_mineflayer", lambda: SimpleNamespace(createBot=lambda _opts: js_bot)
    )
    monkeypatch.setattr(rt, "_install_quiet_interrupt", lambda: None)
    # create_bot probes the server's TCP port first, and a failed probe calls
    # os._exit — which would take the test runner with it.
    monkeypatch.setattr(rt, "_require_reachable", lambda *_a: None)
    # Patch the module reference, not `atexit.register` itself — the latter is
    # the real stdlib module and would swallow every registration process-wide.
    monkeypatch.setattr(rt, "atexit", SimpleNamespace(register=lambda *_a: None))

    rt.create_bot(host="example.invalid", username="tester")

    assert installed == [js_bot]
