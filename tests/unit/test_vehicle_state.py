"""Unit tests for keeping `bot.vehicle` honest after a dismount.

mineflayer sets `bot.vehicle` on mount but never clears it on a 1.9+ server
(its three `dismount` emit sites are all unreachable — see
`_bot_runtime._clear_stale_vehicle`), which pins `is_riding()` to True for the
rest of the session. `create_bot` installs a `set_passengers` repair listener,
and `is_riding()` additionally checks the vehicle's `isValid` for the despawn
case, which sends no `set_passengers` at all.
"""

from __future__ import annotations

import threading
from types import SimpleNamespace
from typing import Any

import pytest

import minethon._bot_runtime as rt
import minethon._commands as cmd
from minethon._bot_runtime import Bot
from minethon.errors import MinethonError

_BOT_ID = 42
_VEHICLE_ID = 7


class FakeBot:
    """Minimal stand-in for the mineflayer JS bot proxy."""

    def __init__(
        self,
        vehicle: Any,
        dismount: Any = None,
        *,
        sneaking: bool = False,
        new_input_packet: bool = True,
        server_obeys: bool = True,
        obey_after_polls: int = 0,
    ) -> None:
        self._vehicle = vehicle
        self.entity = SimpleNamespace(id=_BOT_ID)
        self.entities: dict[int, Any] = {}
        self.emitted: list[tuple[str, Any]] = []
        self.controls: list[tuple[str, bool]] = []
        self.written: list[tuple[str, Any]] = []
        self.dismount = dismount
        self._state = {"sneak": sneaking}
        self._new_input_packet = new_input_packet
        # Stands in for the server acting on the input, which is what really
        # ends the ride — dismount() polls until it does. `obey_after_polls`
        # models the round trip: the ride only ends after that many reads of
        # `vehicle`, so a dismount() that returned without polling would still
        # see the bot aboard.
        self._server_obeys = server_obeys
        self._obey_after_polls = obey_after_polls
        self._input_sent = False
        self._client = SimpleNamespace(write=self._write)

    @property
    def vehicle(self) -> Any:
        if self._input_sent and self._server_obeys:
            if self._obey_after_polls <= 0:
                self._vehicle = None
            else:
                self._obey_after_polls -= 1
        return self._vehicle

    @vehicle.setter
    def vehicle(self, value: Any) -> None:
        self._vehicle = value

    def emit(self, event: str, payload: Any = None) -> None:
        self.emitted.append((event, payload))

    def _write(self, name: str, payload: Any) -> None:
        self.written.append((name, payload))
        if name == "steer_vehicle":
            self._input_sent = True

    def supportFeature(self, name: str) -> bool:  # noqa: N802
        return self._new_input_packet if name == "newPlayerInputPacket" else False

    def setControlState(self, control: str, state: bool) -> None:  # noqa: N802
        # physics.js drops a write that doesn't change the control — the reason
        # dismount() has to clear sneak before pressing it.
        if self._state.get(control) == state:
            return
        self._state[control] = state
        self.controls.append((control, state))
        if control == "sneak" and state:
            self._input_sent = True

    def getControlState(self, control: str) -> bool:  # noqa: N802
        return bool(self._state.get(control))


def _packet(entity_id: int, passengers: list[int]) -> dict[str, Any]:
    """A `set_passengers` payload shaped the way it really crosses the bridge.

    protodef builds packet payloads as plain JS objects and JSPyBridge inlines
    those by value, so the handler receives a plain dict — not a Proxy. Using
    SimpleNamespace here would let attribute-access code pass a test it would
    fail against a live bridge.
    """
    return {"entityId": entity_id, "passengers": passengers}


def _vehicle(*, valid: bool = True) -> Any:
    return SimpleNamespace(id=_VEHICLE_ID, isValid=valid)


def _riding() -> tuple[FakeBot, Any]:
    vehicle = _vehicle()
    return FakeBot(vehicle), vehicle


# ── the repair itself ────────────────────────────────────────────────


def test_clears_vehicle_when_the_bot_left_the_list() -> None:
    # Vanilla's dismount packet: the vehicle's own id, and a passenger list the
    # bot has already been removed from.
    bot, _ = _riding()

    rt._clear_stale_vehicle(bot, _packet(_VEHICLE_ID, []))

    assert bot.vehicle is None


def test_clears_vehicle_when_other_riders_remain_aboard() -> None:
    # The bot got off a vehicle someone else is still riding, so the list is
    # non-empty but no longer contains the bot.
    bot, _ = _riding()

    rt._clear_stale_vehicle(bot, _packet(_VEHICLE_ID, [99]))

    assert bot.vehicle is None


def test_emits_dismount_with_the_vehicle_it_left() -> None:
    bot, vehicle = _riding()

    rt._clear_stale_vehicle(bot, _packet(_VEHICLE_ID, []))

    assert bot.emitted == [("dismount", vehicle)]


def test_keeps_vehicle_when_another_entity_changed_passengers() -> None:
    # A boat across the map loading its passengers must not dismount the bot.
    bot, vehicle = _riding()

    rt._clear_stale_vehicle(bot, _packet(_VEHICLE_ID + 1, []))

    assert bot.vehicle is vehicle
    assert bot.emitted == []


def test_keeps_vehicle_when_the_bot_is_still_aboard() -> None:
    # A second rider mounting the same vehicle re-sends the list with the bot
    # still in it.
    bot, vehicle = _riding()

    rt._clear_stale_vehicle(bot, _packet(_VEHICLE_ID, [_BOT_ID, 99]))

    assert bot.vehicle is vehicle
    assert bot.emitted == []


def test_does_nothing_when_not_riding() -> None:
    bot = FakeBot(None)

    rt._clear_stale_vehicle(bot, _packet(_VEHICLE_ID, []))

    assert bot.vehicle is None
    assert bot.emitted == []


def test_ignores_someone_else_mounting_while_the_bot_is_off() -> None:
    bot = FakeBot(None)

    rt._clear_stale_vehicle(bot, _packet(_VEHICLE_ID, [99]))

    assert bot.vehicle is None
    assert bot.emitted == []


def test_ignores_the_detach_sentinel_when_not_riding() -> None:
    # `entityId == -1` is mineflayer's "no vehicle" marker, never a real entity,
    # so the restore branch must not look it up in bot.entities.
    bot = FakeBot(None)
    bot.entities = {-1: _vehicle()}

    rt._clear_stale_vehicle(bot, _packet(-1, [_BOT_ID]))

    assert bot.vehicle is None


def test_restores_a_remount_this_handler_had_already_undone() -> None:
    # Dismount + remount of the same vehicle inside one tick. mineflayer settles
    # its JS state on "aboard" immediately; our Python callbacks drain later, so
    # the dismount packet arrives first and clears bot.vehicle. The mount packet
    # behind it has to put it back, or is_riding() reports False forever while
    # the bot is really riding.
    bot, vehicle = _riding()
    bot.entities = {_VEHICLE_ID: vehicle}

    rt._clear_stale_vehicle(bot, _packet(_VEHICLE_ID, []))
    assert bot.vehicle is None
    rt._clear_stale_vehicle(bot, _packet(_VEHICLE_ID, [_BOT_ID]))

    assert bot.vehicle is vehicle


# ── wiring onto the protocol client ──────────────────────────────────


def test_repair_is_registered_on_the_right_emitters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # `set_passengers` is a protocol packet and has to sit on bot._client;
    # `respawn` is a bot event and has to sit on the bot. Swapping either one
    # makes it silently never fire — exactly the mineflayer bug worked around
    # here.
    registered: list[tuple[Any, str]] = []
    client = SimpleNamespace()
    js_bot = SimpleNamespace(_client=client)

    def fake_on(emitter: Any, event: str) -> Any:
        registered.append((emitter, event))
        return lambda fn: fn

    monkeypatch.setattr(rt, "On", fake_on)
    rt._install_dismount_repair(js_bot)

    assert registered == [(client, "set_passengers"), (js_bot, "respawn")]


def _install_capturing(monkeypatch: pytest.MonkeyPatch, js_bot: Any) -> dict[str, Any]:
    """Install the repair, returning the registered callbacks keyed by event."""
    handlers: dict[str, Any] = {}

    def fake_on(_emitter: Any, event: str) -> Any:
        def register(fn: Any) -> Any:
            handlers[event] = fn
            return fn

        return register

    monkeypatch.setattr(rt, "On", fake_on)
    rt._install_dismount_repair(js_bot)
    return handlers


def test_dismount_packet_flips_is_riding_to_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # End-to-end: the callback that actually gets registered, invoked with the
    # real (packet, metadata) arity node-minecraft-protocol emits, driving the
    # public method whose contract this exists to keep.
    js_bot, _ = _riding()
    bot = Bot(js_bot)
    handlers = _install_capturing(monkeypatch, js_bot)
    assert bot.is_riding() is True

    handlers["set_passengers"](_packet(_VEHICLE_ID, []), {"name": "set_passengers"})

    assert bot.is_riding() is False


def test_respawn_resets_a_vehicle_nothing_else_would_clear(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Death and dimension change take the bot off its vehicle without any
    # set_passengers and without an entity_destroy for the entities left in the
    # old dimension, so neither other repair fires.
    js_bot, vehicle = _riding()
    bot = Bot(js_bot)
    handlers = _install_capturing(monkeypatch, js_bot)

    handlers["respawn"]()

    assert bot.is_riding() is False
    # Same event as the packet path, so a handler waiting on `dismount` wakes
    # whether the bot got off or died getting off.
    assert js_bot.emitted == [("dismount", vehicle)]


def test_respawn_is_quiet_when_the_bot_was_not_riding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    js_bot = FakeBot(None)
    handlers = _install_capturing(monkeypatch, js_bot)

    handlers["respawn"]()

    assert js_bot.emitted == []


def test_registered_handlers_isolate_their_own_exceptions(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    # Both callbacks must go through _normalize_handler. Unwrapped, an exception
    # (e.g. `vehicle` timing out on a dying bridge) travels back into JS as an
    # unhandled promise rejection, which terminates the node process.
    class Exploding:
        _client = SimpleNamespace()

        def __getattr__(self, name: str) -> Any:
            msg = f"Timed out accessing '{name}'"
            raise RuntimeError(msg)

    js_bot = Exploding()
    handlers = _install_capturing(monkeypatch, js_bot)

    assert handlers["set_passengers"](_packet(_VEHICLE_ID, []), {}) is None
    assert handlers["respawn"]() is None

    assert capsys.readouterr().out.count("事件處理發生錯誤") == 2


def test_missing_protocol_client_warns_instead_of_crashing() -> None:
    with pytest.warns(RuntimeWarning, match="is_riding"):
        rt._install_dismount_repair(SimpleNamespace(_client=None))


def test_create_bot_installs_the_repair(monkeypatch: pytest.MonkeyPatch) -> None:
    # Everything above drives _install_dismount_repair directly, so without this
    # the call site in create_bot could be deleted with every test still green —
    # the exact way two earlier versions of this feature shipped as dead code.
    registered: list[tuple[Any, str]] = []
    js_bot, _ = _riding()

    def fake_on(emitter: Any, event: str) -> Any:
        registered.append((emitter, event))
        return lambda fn: fn

    monkeypatch.setattr(rt, "On", fake_on)
    monkeypatch.setattr(rt, "Once", lambda *_a, **_k: lambda fn: fn)
    monkeypatch.setattr(
        rt, "get_mineflayer", lambda: SimpleNamespace(createBot=lambda _opts: js_bot)
    )
    monkeypatch.setattr(rt, "_install_quiet_interrupt", lambda: None)
    # create_bot probes the server's TCP port before handing off to mineflayer,
    # and a failed probe calls os._exit — which would take the test runner with
    # it. `example.invalid` never resolves, so this has to be stubbed.
    monkeypatch.setattr(rt, "_require_reachable", lambda *_a: None)
    # Patch the module reference, not `atexit.register` itself — the latter is
    # the real stdlib module and would swallow every registration process-wide
    # for the duration of the test.
    monkeypatch.setattr(rt, "atexit", SimpleNamespace(register=lambda *_a: None))

    rt.create_bot(host="example.invalid", username="tester")

    assert (js_bot._client, "set_passengers") in registered
    assert (js_bot, "respawn") in registered


# ── dismount() ───────────────────────────────────────────────────────


def test_dismount_sends_the_sneak_input_while_riding() -> None:
    # Vanilla dismounts on the sneak input; mineflayer's own dismount() sends
    # the jump flag on 1.21.3+. Going through the sneak control is what reaches
    # the server as `player_input {shift: ...}`.
    js_bot = FakeBot(_vehicle())

    Bot(js_bot).dismount()

    assert js_bot.controls == [("sneak", True), ("sneak", False)]


def test_dismount_forces_an_edge_when_already_sneaking() -> None:
    # setControlState is a no-op when the value is unchanged, so pressing sneak
    # on a bot that already holds it sends nothing and only the release reaches
    # the server — never the press it acts on. And the student's sneak has to
    # survive the call.
    js_bot = FakeBot(_vehicle(), sneaking=True)

    Bot(js_bot).dismount()

    assert js_bot.controls == [
        ("sneak", False),
        ("sneak", True),
        ("sneak", False),
        ("sneak", True),
    ]
    assert js_bot.getControlState("sneak") is True


def test_dismount_holds_sneak_between_press_and_release(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Press and release inside one server tick can cancel out.
    slept: list[float] = []
    monkeypatch.setattr(cmd.time, "sleep", slept.append)
    js_bot = FakeBot(_vehicle())

    Bot(js_bot).dismount()

    # Asserted as a literal: comparing against the constant would still pass if
    # someone set it to zero, which is exactly the case that breaks.
    assert slept == [0.1]


def test_dismount_uses_the_legacy_packet_before_1_21_3() -> None:
    # There the sneak control goes out as entity_action, a different packet from
    # the steer_vehicle shift bit mineflayer used on those versions.
    js_bot = FakeBot(_vehicle(), new_input_packet=False)

    Bot(js_bot).dismount()

    # 0x02 is the unmount bit; 0x01 is jump, which would silently make the bot
    # hop on its vehicle instead.
    assert js_bot.written == [
        ("steer_vehicle", {"sideways": 0.0, "forward": 0.0, "jump": 0x02})
    ]
    assert js_bot.controls == []


def test_dismount_blocks_until_the_server_takes_the_bot_off() -> None:
    # The mixin is blocking throughout, and the *server* is what ends the ride.
    # obey_after_polls models that round trip, so a dismount() that returned
    # right after writing the input would leave the bot still aboard here — and
    # the student's next command would run from a vehicle.
    js_bot = FakeBot(_vehicle(), obey_after_polls=3)
    bot = Bot(js_bot)

    bot.dismount()

    assert bot.is_riding() is False


def test_dismount_raises_when_the_server_ignores_the_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The sneak premise is the unverified part of this whole change, so "the
    # server didn't act" is the likeliest failure — returning None there would
    # let the next command run from a vehicle with no clue why it did nothing.
    monkeypatch.setattr(cmd, "_DISMOUNT_TIMEOUT_SECONDS", 0.05)
    monkeypatch.setattr(cmd, "_DISMOUNT_HOLD_SECONDS", 0.0)
    bot = Bot(FakeBot(_vehicle(), server_obeys=False))

    with pytest.raises(MinethonError, match="下車"):
        bot.dismount()


def _dismount_in_a_worker(js_bot: FakeBot, before: Any = None) -> list[Any]:
    """Run ``dismount()`` on another thread; returns what it raised, if anything."""
    outcome: list[Any] = []

    def target() -> None:
        if before is not None:
            before()
        try:
            Bot(js_bot).dismount()
        except BaseException as exc:  # noqa: BLE001 — recorded, then asserted on
            outcome.append(exc)

    worker = threading.Thread(target=target)
    worker.start()
    worker.join(timeout=2.0)
    assert not worker.is_alive(), "dismount() never returned"
    return outcome


def test_dismount_does_not_wait_on_the_bridge_callback_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # JSPyBridge drains every Python callback on one executor thread, and the
    # only thing that ends the ride is our own set_passengers handler — so a
    # handler that waited here would be sitting on the thread that has to
    # release it. Send the input and get out instead of burning the timeout.
    monkeypatch.setattr(cmd, "_DISMOUNT_HOLD_SECONDS", 0.0)
    loop = SimpleNamespace(callbackExecutor=None)
    monkeypatch.setattr(cmd, "js_config", SimpleNamespace(event_loop=loop))
    js_bot = FakeBot(_vehicle(), server_obeys=False)

    def become_the_executor() -> None:
        loop.callbackExecutor = threading.current_thread()

    assert _dismount_in_a_worker(js_bot, before=become_the_executor) == []
    assert js_bot.controls == [("sneak", True), ("sneak", False)]


def test_dismount_still_waits_on_an_ordinary_worker_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Only the bridge's own thread is special. A thread the student made can
    # still be released by the callback thread, so it gets the full contract.
    monkeypatch.setattr(cmd, "_DISMOUNT_HOLD_SECONDS", 0.0)
    monkeypatch.setattr(cmd, "_DISMOUNT_TIMEOUT_SECONDS", 0.05)
    executor = SimpleNamespace(callbackExecutor=threading.main_thread())
    monkeypatch.setattr(cmd, "js_config", SimpleNamespace(event_loop=executor))

    raised = _dismount_in_a_worker(FakeBot(_vehicle(), server_obeys=False))

    assert [type(exc) for exc in raised] == [MinethonError]


def test_dismount_falls_back_when_the_executor_cannot_be_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # config.event_loop is a JSPyBridge implementation detail. If it moves, err
    # toward skipping the wait rather than risking the deadlock.
    monkeypatch.setattr(cmd, "_DISMOUNT_HOLD_SECONDS", 0.0)
    monkeypatch.setattr(cmd, "js_config", SimpleNamespace(event_loop=None))

    assert _dismount_in_a_worker(FakeBot(_vehicle(), server_obeys=False)) == []


def test_dismount_never_calls_mineflayers_own_dismount() -> None:
    # It emits a bot-level `error` when not riding, which minethon turns into
    # os._exit(1). Not calling it at all removes the path rather than guarding
    # a check a callback thread could invalidate in between.
    def boom() -> None:
        msg = "mineflayer dismount() must not be reached"
        raise AssertionError(msg)

    js_bot = FakeBot(_vehicle(), dismount=boom)

    Bot(js_bot).dismount()


def test_dismount_is_a_no_op_when_not_riding() -> None:
    # A student polling `while bot.is_riding(): bot.dismount()`, or calling it
    # without checking, must not trip mineflayer's fatal `error` branch.
    js_bot = FakeBot(None)

    Bot(js_bot).dismount()

    assert js_bot.controls == []


def test_dismount_is_a_no_op_after_the_vehicle_despawned() -> None:
    js_bot = FakeBot(_vehicle(valid=False))

    Bot(js_bot).dismount()

    assert js_bot.controls == []


# ── is_riding()'s own despawn guard ──────────────────────────────────


def test_is_riding_is_false_after_the_vehicle_despawns() -> None:
    # entity_destroy flips isValid but nothing clears bot.vehicle — the
    # entityGone listener meant to do it is registered on the wrong emitter.
    bot = Bot(FakeBot(_vehicle(valid=False)))

    assert bot.is_riding() is False


def test_protocol_client_is_reached_through_js_not_the_bot() -> None:
    # tests/integration/test_vehicle_dismount.py hooks the raw `set_passengers`
    # packet, which means reaching the minecraft-protocol client. Bot.__getattr__
    # refuses every underscore name, so `bot._client` is an AttributeError and
    # only `bot._js._client` works. Pinning it here because the integration test
    # skips without a server and would ship the mistake unnoticed.
    client = SimpleNamespace()
    bot = Bot(SimpleNamespace(_client=client))

    assert bot._js._client is client
    with pytest.raises(AttributeError):
        _ = bot._client


def test_is_riding_is_true_when_isvalid_is_missing() -> None:
    # A live bridge proxy answers None for a JS attribute that isn't there
    # instead of raising. Only an explicit False means the vehicle despawned;
    # reading None as "not riding" would turn q07's `while not bot.is_riding()`
    # into an infinite loop.
    bot = Bot(FakeBot(SimpleNamespace(id=_VEHICLE_ID)))

    assert bot.is_riding() is True


# The plain True/False cases live in test_commands_reads.py::
# test_is_riding_reflects_bot_vehicle — only the repair-specific ones are here.
