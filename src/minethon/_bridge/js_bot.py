"""Encapsulates all operations on the JS mineflayer bot object."""

import pathlib
from typing import Any

from minethon._bridge._util import extract_js_stack
from minethon._bridge.runtime import BridgeRuntime
from minethon.config import BotConfig
from minethon.models.entity import EntityKind
from minethon.models.errors import BridgeError

# Mapping from EntityKind to the JS entity type string used by mineflayer.
# EntityKind.OTHER is intentionally omitted: mineflayer has no literal
# "other" type, so OTHER acts as a catch-all with no JS type filter.
_ENTITY_KIND_TO_JS: dict[EntityKind, str] = {
    EntityKind.PLAYER: "player",
    EntityKind.MOB: "mob",
    EntityKind.ANIMAL: "animal",
    EntityKind.HOSTILE: "hostile",
    EntityKind.PROJECTILE: "projectile",
    EntityKind.OBJECT: "object",
}

_JS_HELPERS_PATH = pathlib.Path(__file__).parent / "js" / "helpers.js"


class JSBotController:
    """The sole holder of the JS bot proxy.

    Quick-returning methods (chat, get_position, …) are synchronous and
    call JSPyBridge directly on the event-loop thread.

    Long-running methods (dig, place, equip, lookAt) use the
    ``start_*`` variants which delegate to ``js/helpers.js`` so they
    return immediately.  Completion is signalled via custom events on
    the JS bot that the :class:`EventRelay` picks up.
    """

    def __init__(self, runtime: BridgeRuntime, config: BotConfig) -> None:
        self._runtime = runtime
        self._config = config
        self._js_bot: Any = None
        self._helpers: Any = None

    def create_bot(self) -> None:
        """Call ``mineflayer.createBot()`` — starts connecting immediately."""
        mineflayer = self._runtime.require("mineflayer")
        options: dict[str, Any] = {
            "host": self._config.host,
            "port": self._config.port,
            "username": self._config.username,
        }
        # Optional fields — only set when explicitly provided so mineflayer
        # uses its own defaults for unset values.
        optional_fields: list[tuple[str, str]] = [
            ("password", "password"),
            ("hide_errors", "hideErrors"),
            ("disable_chat_signing", "disableChatSigning"),
            ("version", "version"),
            ("auth", "auth"),
            ("auth_server", "authServer"),
            ("session_server", "sessionServer"),
            ("log_errors", "logErrors"),
            ("check_timeout_interval", "checkTimeoutInterval"),
            ("keep_alive", "keepAlive"),
            ("respawn", "respawn"),
            ("chat_length_limit", "chatLengthLimit"),
            ("view_distance", "viewDistance"),
            ("default_chat_patterns", "defaultChatPatterns"),
            ("physics_enabled", "physicsEnabled"),
            ("brand", "brand"),
            ("skip_validation", "skipValidation"),
            ("profiles_folder", "profilesFolder"),
            ("load_internal_plugins", "loadInternalPlugins"),
        ]
        for py_attr, js_key in optional_fields:
            value = getattr(self._config, py_attr)
            if value is not None:
                options[js_key] = value
        self._js_bot = mineflayer.createBot(options)
        try:
            self._helpers = self._runtime.require(str(_JS_HELPERS_PATH.as_posix()))
        except Exception as exc:
            raise BridgeError(
                f"Failed to load JS helpers at {_JS_HELPERS_PATH}: {exc}",
                js_stack=extract_js_stack(exc),
            ) from exc

    @property
    def js_bot(self) -> Any:
        """Raw JS bot proxy (for event binding)."""
        return self._js_bot

    # -- Chat --

    def chat(self, message: str) -> None:
        """Send a chat message."""
        try:
            self._js_bot.chat(message)
        except Exception as exc:
            raise BridgeError(f"chat failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def whisper(self, username: str, message: str) -> None:
        """Send a whisper to a player."""
        try:
            self._js_bot.whisper(username, message)
        except Exception as exc:
            raise BridgeError(f"whisper failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    # -- State queries --

    def get_position(self) -> dict[str, float]:
        """Read bot position as ``{x, y, z}`` dict."""
        try:
            pos = self._js_bot.entity.position
            return {"x": float(pos.x), "y": float(pos.y), "z": float(pos.z)}
        except Exception as exc:
            raise BridgeError(f"get_position failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_health(self) -> float:
        """Read bot health (0-20)."""
        try:
            return float(self._js_bot.health)
        except Exception as exc:
            raise BridgeError(f"get_health failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_food(self) -> float:
        """Read bot food level (0-20)."""
        try:
            return float(self._js_bot.food)
        except Exception as exc:
            raise BridgeError(f"get_food failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_username(self) -> str:
        """Read bot username."""
        try:
            return str(self._js_bot.username)
        except Exception as exc:
            raise BridgeError(f"get_username failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_game_mode(self) -> str:
        """Read current game mode (``"survival"``, ``"creative"``, etc.)."""
        try:
            gm = self._js_bot.game.gameMode
            return str(gm) if gm is not None else "unknown"
        except Exception as exc:
            raise BridgeError(f"get_game_mode failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_players_dict(self) -> dict[str, dict[str, object]]:
        """Return online players as a Python dict (no JS proxy leaking)."""
        try:
            js_players = self._js_bot.players
            result: dict[str, dict[str, object]] = {}
            for key in js_players:
                p = js_players[key]
                result[str(key)] = {
                    "username": str(p.username),
                    "ping": int(p.ping) if hasattr(p, "ping") else 0,
                }
            return result
        except Exception as exc:
            raise BridgeError(f"get_players_dict failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def is_alive(self) -> bool:
        """Whether the bot entity is alive (health > 0)."""
        try:
            return float(self._js_bot.health) > 0
        except (TypeError, AttributeError):
            return False

    # -- World queries --

    def block_at(self, x: int, y: int, z: int) -> Any | None:
        """Return the raw JS Block at the given position, or ``None``."""
        try:
            Vec3 = self._runtime.require("vec3").Vec3
            pos = Vec3(x, y, z)
            return self._js_bot.blockAt(pos)
        except Exception as exc:
            raise BridgeError(f"block_at failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def find_blocks(
        self,
        block_name: str,
        max_distance: float,
        count: int,
    ) -> list[Any]:
        """Find blocks by name. Returns list of raw JS Block proxies."""
        try:
            mcdata = self._js_bot.registry
            block_type = getattr(mcdata.blocksByName, block_name, None)
            if block_type is None:
                return []
            block_id = int(block_type.id)

            positions = self._js_bot.findBlocks(
                {
                    "matching": block_id,
                    "maxDistance": max_distance,
                    "count": count,
                }
            )
            results: list[Any] = []
            for pos in positions:
                block = self._js_bot.blockAt(pos)
                if block is not None:
                    results.append(block)
            return results
        except Exception as exc:
            raise BridgeError(f"find_blocks failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_entity_by_id(self, entity_id: int) -> Any | None:
        """Look up an entity by its numeric ID."""
        try:
            entities = self._js_bot.entities
            return entities[str(entity_id)]
        except (KeyError, TypeError):
            return None
        except Exception as exc:
            raise BridgeError(f"get_entity_by_id failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_entity_by_filter(
        self,
        name: str | None,
        kind: EntityKind | None,
        max_distance: float,
    ) -> Any | None:
        """Find the nearest entity matching the filter criteria."""
        entity_type = _ENTITY_KIND_TO_JS.get(kind) if kind is not None else None
        try:
            bot_pos = self._js_bot.entity.position
            best: Any = None
            best_dist: float = max_distance

            entities = self._js_bot.entities
            for eid in entities:
                entity = entities[eid]
                if entity is None:
                    continue

                # Skip the bot itself
                if int(entity.id) == int(self._js_bot.entity.id):
                    continue

                # Name filter: check username first (players), then
                # name (mobs/objects).  Player entities have name="player"
                # so checking name first would never match by username.
                if name is not None:
                    ename = getattr(entity, "username", None)
                    if ename is None or str(ename) != name:
                        ename = getattr(entity, "name", None)
                        if ename is None or str(ename) != name:
                            continue

                # Type filter
                if entity_type is not None:
                    etype = getattr(entity, "type", None)
                    if etype is None or str(etype) != entity_type:
                        continue

                # Distance check
                epos = entity.position
                dx = float(epos.x) - float(bot_pos.x)
                dy = float(epos.y) - float(bot_pos.y)
                dz = float(epos.z) - float(bot_pos.z)
                dist = (dx * dx + dy * dy + dz * dz) ** 0.5

                if dist < best_dist:
                    best_dist = dist
                    best = entity

            return best
        except Exception as exc:
            raise BridgeError(f"get_entity_by_filter failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    # -- Synchronous actions (quick-returning) --

    def attack(self, js_entity: Any) -> None:
        """Attack an entity."""
        try:
            self._js_bot.attack(js_entity)
        except Exception as exc:
            raise BridgeError(f"attack failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def use_item(self) -> None:
        """Activate the held item."""
        try:
            self._js_bot.activateItem()
        except Exception as exc:
            raise BridgeError(f"use_item failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    # -- Non-blocking actions (long-running, completion via events) --

    def start_dig(self, js_block: Any) -> None:
        """Start digging without blocking. Completion via ``_minethon:digDone``."""
        try:
            self._helpers.startDig(self._js_bot, js_block)
        except Exception as exc:
            raise BridgeError(f"start_dig failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_place(
        self,
        js_reference_block: Any,
        face_x: float,
        face_y: float,
        face_z: float,
    ) -> None:
        """Start placing without blocking. Completion via ``_minethon:placeDone``."""
        try:
            Vec3 = self._runtime.require("vec3").Vec3
            face_vec = Vec3(face_x, face_y, face_z)
            self._helpers.startPlace(self._js_bot, js_reference_block, face_vec)
        except Exception as exc:
            raise BridgeError(f"start_place failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_equip(self, item_name: str) -> bool:
        """Start equipping without blocking. Completion via ``_minethon:equipDone``.

        Returns:
            ``True`` if the item was found and equip started,
            ``False`` if the item was not found in inventory.
        """
        try:
            inv = self._js_bot.inventory
            items = inv.items()
            for item in items:
                if str(item.name) == item_name:
                    self._helpers.startEquip(self._js_bot, item, "hand")
                    return True
            return False
        except Exception as exc:
            raise BridgeError(f"start_equip failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_look_at(self, x: float, y: float, z: float) -> None:
        """Start looking at a position without blocking.

        Completion via ``_minethon:lookAtDone``.
        """
        try:
            Vec3 = self._runtime.require("vec3").Vec3
            pos = Vec3(x, y, z)
            self._helpers.startLookAt(self._js_bot, pos)
        except Exception as exc:
            raise BridgeError(f"start_look_at failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    # -- Movement (quick-returning) --

    def set_control_state(self, control: str, state: bool) -> None:
        """Set a movement control state."""
        try:
            self._js_bot.setControlState(control, state)
        except Exception as exc:
            raise BridgeError(f"set_control_state failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def clear_control_states(self) -> None:
        """Stop all movement controls."""
        try:
            self._js_bot.clearControlStates()
        except Exception as exc:
            raise BridgeError(f"clear_control_states failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    # -- Additional state queries --

    def get_food_saturation(self) -> float:
        """Read bot food saturation."""
        try:
            return float(self._js_bot.foodSaturation)
        except Exception as exc:
            raise BridgeError(f"get_food_saturation failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_oxygen_level(self) -> float:
        """Read bot oxygen level (0-20)."""
        try:
            return float(self._js_bot.oxygenLevel)
        except Exception as exc:
            raise BridgeError(f"get_oxygen_level failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_spawn_point(self) -> dict[str, float] | None:
        """Read bot spawn point as ``{x, y, z}`` dict, or None."""
        try:
            sp = self._js_bot.spawnPoint
            if sp is None:
                return None
            return {"x": float(sp.x), "y": float(sp.y), "z": float(sp.z)}
        except (AttributeError, TypeError):
            return None

    def get_held_item_data(self) -> dict[str, Any] | None:
        """Read the held item as a plain dict, or None."""
        try:
            item = self._js_bot.heldItem
            if item is None:
                return None
            return {
                "name": str(item.name),
                "displayName": str(item.displayName),
                "count": int(item.count),
                "slot": int(item.slot),
                "stackSize": int(item.stackSize),
            }
        except (AttributeError, TypeError):
            return None

    def get_using_held_item(self) -> bool:
        """Whether the bot is currently using the held item."""
        try:
            return bool(self._js_bot.usingHeldItem)
        except (AttributeError, TypeError):
            return False

    def get_game_data(self) -> dict[str, Any]:
        """Read all bot.game.* properties as a plain dict."""
        try:
            g = self._js_bot.game
            return {
                "levelType": str(g.levelType) if getattr(g, "levelType", None) is not None else None,
                "dimension": str(g.dimension) if getattr(g, "dimension", None) is not None else None,
                "difficulty": str(g.difficulty) if getattr(g, "difficulty", None) is not None else None,
                "gameMode": str(g.gameMode) if getattr(g, "gameMode", None) is not None else "unknown",
                "hardcore": bool(g.hardcore) if getattr(g, "hardcore", None) is not None else False,
                "maxPlayers": int(g.maxPlayers) if getattr(g, "maxPlayers", None) is not None else 0,
                "serverBrand": str(g.serverBrand) if getattr(g, "serverBrand", None) is not None else None,
                "minY": int(g.minY) if getattr(g, "minY", None) is not None else 0,
                "height": int(g.height) if getattr(g, "height", None) is not None else 256,
            }
        except Exception as exc:
            raise BridgeError(f"get_game_data failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_experience(self) -> dict[str, Any]:
        """Read bot.experience.* properties."""
        try:
            exp = self._js_bot.experience
            return {
                "level": int(exp.level) if getattr(exp, "level", None) is not None else 0,
                "points": int(exp.points) if getattr(exp, "points", None) is not None else 0,
                "progress": float(exp.progress) if getattr(exp, "progress", None) is not None else 0.0,
            }
        except Exception as exc:
            raise BridgeError(f"get_experience failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_time_data(self) -> dict[str, Any]:
        """Read bot.time.* properties."""
        try:
            t = self._js_bot.time
            return {
                "timeOfDay": int(t.timeOfDay) if getattr(t, "timeOfDay", None) is not None else 0,
                "day": int(t.day) if getattr(t, "day", None) is not None else 0,
                "isDay": bool(t.isDay) if getattr(t, "isDay", None) is not None else True,
                "moonPhase": int(t.moonPhase) if getattr(t, "moonPhase", None) is not None else 0,
                "age": int(t.age) if getattr(t, "age", None) is not None else 0,
                "doDaylightCycle": bool(t.doDaylightCycle) if getattr(t, "doDaylightCycle", None) is not None else True,
            }
        except Exception as exc:
            raise BridgeError(f"get_time_data failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_is_raining(self) -> bool:
        """Whether it is raining."""
        try:
            return bool(self._js_bot.isRaining)
        except (AttributeError, TypeError):
            return False

    def get_rain_state(self) -> float:
        """Rain level (0-1)."""
        try:
            return float(self._js_bot.rainState)
        except (AttributeError, TypeError):
            return 0.0

    def get_thunder_state(self) -> float:
        """Thunder level (0-1)."""
        try:
            return float(self._js_bot.thunderState)
        except (AttributeError, TypeError):
            return 0.0

    def get_is_sleeping(self) -> bool:
        """Whether the bot is in bed."""
        try:
            return bool(self._js_bot.isSleeping)
        except (AttributeError, TypeError):
            return False

    def get_quick_bar_slot(self) -> int:
        """Current quick bar slot (0-8)."""
        try:
            return int(self._js_bot.quickBarSlot)
        except (AttributeError, TypeError):
            return 0

    def get_physics_enabled(self) -> bool:
        """Whether physics simulation is enabled."""
        try:
            return bool(self._js_bot.physicsEnabled)
        except (AttributeError, TypeError):
            return True

    def set_physics_enabled(self, enabled: bool) -> None:
        """Set physics simulation on/off."""
        try:
            self._js_bot.physicsEnabled = enabled
        except Exception as exc:
            raise BridgeError(f"set_physics_enabled failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_inventory_items(self) -> list[Any]:
        """Return raw JS Item proxies from bot.inventory.items()."""
        try:
            return list(self._js_bot.inventory.items())
        except Exception as exc:
            raise BridgeError(f"get_inventory_items failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_control_state_value(self, control: str) -> bool:
        """Read a specific control state."""
        try:
            return bool(self._js_bot.getControlState(control))
        except Exception as exc:
            raise BridgeError(f"get_control_state failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_tablist(self) -> dict[str, str]:
        """Read tablist header/footer as plain strings."""
        try:
            tl = self._js_bot.tablist
            header = str(tl.header) if getattr(tl, "header", None) is not None else ""
            footer = str(tl.footer) if getattr(tl, "footer", None) is not None else ""
            return {"header": header, "footer": footer}
        except (AttributeError, TypeError):
            return {"header": "", "footer": ""}

    def get_target_dig_block(self) -> Any | None:
        """Return the block currently being dug, or None."""
        try:
            return self._js_bot.targetDigBlock
        except (AttributeError, TypeError):
            return None

    def get_entities_snapshot(self) -> list[Any]:
        """Return all entity JS proxies as a list."""
        try:
            entities = self._js_bot.entities
            result: list[Any] = []
            for eid in entities:
                e = entities[eid]
                if e is not None:
                    result.append(e)
            return result
        except Exception as exc:
            raise BridgeError(f"get_entities_snapshot failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    # -- Additional synchronous actions --

    def end(self, reason: str | None = None) -> None:
        """End connection with the server."""
        try:
            if reason is not None:
                self._js_bot.end(reason)
            else:
                self._js_bot.end()
        except Exception:
            pass  # Best-effort

    def swing_arm(self, hand: str = "right", show_hand: bool = True) -> None:
        """Play arm swing animation."""
        try:
            self._js_bot.swingArm(hand, show_hand)
        except Exception as exc:
            raise BridgeError(f"swing_arm failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def activate_item(self, off_hand: bool = False) -> None:
        """Activate held item (eat, shoot bow, etc.)."""
        try:
            self._js_bot.activateItem(off_hand)
        except Exception as exc:
            raise BridgeError(f"activate_item failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def deactivate_item(self) -> None:
        """Deactivate held item (release bow, stop eating)."""
        try:
            self._js_bot.deactivateItem()
        except Exception as exc:
            raise BridgeError(f"deactivate_item failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def use_on(self, js_entity: Any) -> None:
        """Use held item on an entity (saddle, shears)."""
        try:
            self._js_bot.useOn(js_entity)
        except Exception as exc:
            raise BridgeError(f"use_on failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def mount(self, js_entity: Any) -> None:
        """Mount a vehicle entity."""
        try:
            self._js_bot.mount(js_entity)
        except Exception as exc:
            raise BridgeError(f"mount failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def dismount(self) -> None:
        """Dismount from the current vehicle."""
        try:
            self._js_bot.dismount()
        except Exception as exc:
            raise BridgeError(f"dismount failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def move_vehicle(self, left: float, forward: float) -> None:
        """Move the vehicle (-1 or 1 for each axis)."""
        try:
            self._js_bot.moveVehicle(left, forward)
        except Exception as exc:
            raise BridgeError(f"move_vehicle failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def set_quick_bar_slot(self, slot: int) -> None:
        """Select a quick bar slot (0-8)."""
        try:
            self._js_bot.setQuickBarSlot(slot)
        except Exception as exc:
            raise BridgeError(f"set_quick_bar_slot failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def stop_digging(self) -> None:
        """Stop the current digging operation."""
        try:
            self._js_bot.stopDigging()
        except Exception as exc:
            raise BridgeError(f"stop_digging failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def dig_time(self, js_block: Any) -> int:
        """Return dig time in milliseconds for the given block."""
        try:
            return int(self._js_bot.digTime(js_block))
        except Exception as exc:
            raise BridgeError(f"dig_time failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def can_dig_block(self, js_block: Any) -> bool:
        """Whether the block is diggable and in range."""
        try:
            return bool(self._js_bot.canDigBlock(js_block))
        except (AttributeError, TypeError):
            return False

    def can_see_block(self, js_block: Any) -> bool:
        """Whether the bot can see the block."""
        try:
            return bool(self._js_bot.canSeeBlock(js_block))
        except (AttributeError, TypeError):
            return False

    def block_at_cursor(self, max_distance: float = 256) -> Any | None:
        """Return the block the bot is looking at, or None."""
        try:
            return self._js_bot.blockAtCursor(max_distance)
        except (AttributeError, TypeError):
            return None

    def entity_at_cursor(self, max_distance: float = 3.5) -> Any | None:
        """Return the entity the bot is looking at, or None."""
        try:
            return self._js_bot.entityAtCursor(max_distance)
        except (AttributeError, TypeError):
            return None

    def accept_resource_pack(self) -> None:
        """Accept the server resource pack."""
        try:
            self._js_bot.acceptResourcePack()
        except Exception as exc:
            raise BridgeError(f"accept_resource_pack failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def deny_resource_pack(self) -> None:
        """Deny the server resource pack."""
        try:
            self._js_bot.denyResourcePack()
        except Exception as exc:
            raise BridgeError(f"deny_resource_pack failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def set_settings(self, options: dict[str, Any]) -> None:
        """Update bot.settings."""
        try:
            self._js_bot.setSettings(options)
        except Exception as exc:
            raise BridgeError(f"set_settings failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def support_feature(self, name: str) -> bool:
        """Check if a feature is supported in the current MC version."""
        try:
            return bool(self._js_bot.supportFeature(name))
        except (AttributeError, TypeError):
            return False

    def do_respawn(self) -> None:
        """Manually respawn (when auto-respawn is disabled)."""
        try:
            self._js_bot.respawn()
        except Exception as exc:
            raise BridgeError(f"respawn failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def is_a_bed(self, js_block: Any) -> bool:
        """Return True if the block is a bed."""
        try:
            return bool(self._js_bot.isABed(js_block))
        except (AttributeError, TypeError):
            return False

    def update_sign(self, js_block: Any, text: str, back: bool = False) -> None:
        """Update the text on a sign."""
        try:
            self._js_bot.updateSign(js_block, text, back)
        except Exception as exc:
            raise BridgeError(f"update_sign failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def set_command_block(self, x: int, y: int, z: int, command: str, options: dict[str, Any] | None = None) -> None:
        """Set a command block's properties."""
        try:
            Vec3 = self._runtime.require("vec3").Vec3
            pos = Vec3(x, y, z)
            if options is not None:
                self._js_bot.setCommandBlock(pos, command, options)
            else:
                self._js_bot.setCommandBlock(pos, command)
        except Exception as exc:
            raise BridgeError(f"set_command_block failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def close_window(self, js_window: Any) -> None:
        """Close a window."""
        try:
            self._js_bot.closeWindow(js_window)
        except Exception as exc:
            raise BridgeError(f"close_window failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def update_held_item(self) -> None:
        """Update bot.heldItem."""
        try:
            self._js_bot.updateHeldItem()
        except Exception as exc:
            raise BridgeError(f"update_held_item failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def get_equipment_dest_slot(self, destination: str) -> int:
        """Get the inventory slot ID for an equipment destination."""
        try:
            return int(self._js_bot.getEquipmentDestSlot(destination))
        except Exception as exc:
            raise BridgeError(f"get_equipment_dest_slot failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def recipes_for(self, item_type: int, metadata: int | None, min_result_count: int | None, crafting_table: Any | None) -> list[Any]:
        """Return recipes for the given item type."""
        try:
            return list(self._js_bot.recipesFor(item_type, metadata, min_result_count, crafting_table))
        except Exception as exc:
            raise BridgeError(f"recipes_for failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def recipes_all(self, item_type: int, metadata: int | None, crafting_table: Any | None) -> list[Any]:
        """Return all recipes for the given item type (regardless of inventory)."""
        try:
            return list(self._js_bot.recipesAll(item_type, metadata, crafting_table))
        except Exception as exc:
            raise BridgeError(f"recipes_all failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def creative_start_flying(self) -> None:
        """Set gravity to 0 for creative flight."""
        try:
            self._js_bot.creative.startFlying()
        except Exception as exc:
            raise BridgeError(f"creative_start_flying failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def creative_stop_flying(self) -> None:
        """Restore normal gravity."""
        try:
            self._js_bot.creative.stopFlying()
        except Exception as exc:
            raise BridgeError(f"creative_stop_flying failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    # -- Additional non-blocking actions (completion via events) --

    def start_look(self, yaw: float, pitch: float, force: bool = False) -> None:
        """Start looking at yaw/pitch. Completion via ``_minethon:lookDone``."""
        try:
            self._helpers.startLook(self._js_bot, yaw, pitch, force)
        except Exception as exc:
            raise BridgeError(f"start_look failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_sleep(self, js_bed_block: Any) -> None:
        """Start sleeping. Completion via ``_minethon:sleepDone``."""
        try:
            self._helpers.startSleep(self._js_bot, js_bed_block)
        except Exception as exc:
            raise BridgeError(f"start_sleep failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_wake(self) -> None:
        """Start waking. Completion via ``_minethon:wakeDone``."""
        try:
            self._helpers.startWake(self._js_bot)
        except Exception as exc:
            raise BridgeError(f"start_wake failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_unequip(self, destination: str) -> None:
        """Start unequipping. Completion via ``_minethon:unequipDone``."""
        try:
            self._helpers.startUnequip(self._js_bot, destination)
        except Exception as exc:
            raise BridgeError(f"start_unequip failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_toss_stack(self, js_item: Any) -> None:
        """Start tossing a stack. Completion via ``_minethon:tossStackDone``."""
        try:
            self._helpers.startTossStack(self._js_bot, js_item)
        except Exception as exc:
            raise BridgeError(f"start_toss_stack failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_toss(self, item_type: int, metadata: int | None, count: int | None) -> None:
        """Start tossing items. Completion via ``_minethon:tossDone``."""
        try:
            self._helpers.startToss(self._js_bot, item_type, metadata, count)
        except Exception as exc:
            raise BridgeError(f"start_toss failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_consume(self) -> None:
        """Start consuming held item. Completion via ``_minethon:consumeDone``."""
        try:
            self._helpers.startConsume(self._js_bot)
        except Exception as exc:
            raise BridgeError(f"start_consume failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_fish(self) -> None:
        """Start fishing. Completion via ``_minethon:fishDone``."""
        try:
            self._helpers.startFish(self._js_bot)
        except Exception as exc:
            raise BridgeError(f"start_fish failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_elytra_fly(self) -> None:
        """Start elytra flying. Completion via ``_minethon:elytraFlyDone``."""
        try:
            self._helpers.startElytraFly(self._js_bot)
        except Exception as exc:
            raise BridgeError(f"start_elytra_fly failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_craft(self, recipe: Any, count: int | None, crafting_table: Any | None) -> None:
        """Start crafting. Completion via ``_minethon:craftDone``."""
        try:
            self._helpers.startCraft(self._js_bot, recipe, count, crafting_table)
        except Exception as exc:
            raise BridgeError(f"start_craft failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_activate_block(self, js_block: Any, direction: Any | None = None, cursor_pos: Any | None = None) -> None:
        """Start activating block. Completion via ``_minethon:activateBlockDone``."""
        try:
            self._helpers.startActivateBlock(self._js_bot, js_block, direction, cursor_pos)
        except Exception as exc:
            raise BridgeError(f"start_activate_block failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_activate_entity(self, js_entity: Any) -> None:
        """Start activating entity. Completion via ``_minethon:activateEntityDone``."""
        try:
            self._helpers.startActivateEntity(self._js_bot, js_entity)
        except Exception as exc:
            raise BridgeError(f"start_activate_entity failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_activate_entity_at(self, js_entity: Any, x: float, y: float, z: float) -> None:
        """Start activating entity at position. Completion via ``_minethon:activateEntityAtDone``."""
        try:
            Vec3 = self._runtime.require("vec3").Vec3
            pos = Vec3(x, y, z)
            self._helpers.startActivateEntityAt(self._js_bot, js_entity, pos)
        except Exception as exc:
            raise BridgeError(f"start_activate_entity_at failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_open_container(self, js_block_or_entity: Any, direction: Any | None = None, cursor_pos: Any | None = None) -> None:
        """Start opening container. Completion via ``_minethon:openContainerDone``."""
        try:
            self._helpers.startOpenContainer(self._js_bot, js_block_or_entity, direction, cursor_pos)
        except Exception as exc:
            raise BridgeError(f"start_open_container failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_open_furnace(self, js_block: Any) -> None:
        """Start opening furnace. Completion via ``_minethon:openFurnaceDone``."""
        try:
            self._helpers.startOpenFurnace(self._js_bot, js_block)
        except Exception as exc:
            raise BridgeError(f"start_open_furnace failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_open_enchantment_table(self, js_block: Any) -> None:
        """Start opening enchantment table. Completion via ``_minethon:openEnchantmentTableDone``."""
        try:
            self._helpers.startOpenEnchantmentTable(self._js_bot, js_block)
        except Exception as exc:
            raise BridgeError(f"start_open_enchantment_table failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_open_anvil(self, js_block: Any) -> None:
        """Start opening anvil. Completion via ``_minethon:openAnvilDone``."""
        try:
            self._helpers.startOpenAnvil(self._js_bot, js_block)
        except Exception as exc:
            raise BridgeError(f"start_open_anvil failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_open_villager(self, js_entity: Any) -> None:
        """Start opening villager trade. Completion via ``_minethon:openVillagerDone``."""
        try:
            self._helpers.startOpenVillager(self._js_bot, js_entity)
        except Exception as exc:
            raise BridgeError(f"start_open_villager failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_trade(self, villager_instance: Any, trade_index: int, times: int | None = None) -> None:
        """Start trading. Completion via ``_minethon:tradeDone``."""
        try:
            self._helpers.startTrade(self._js_bot, villager_instance, trade_index, times)
        except Exception as exc:
            raise BridgeError(f"start_trade failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_tab_complete(self, text: str, assume_command: bool = False, send_block_in_sight: bool = True, timeout: int = 5000) -> None:
        """Start tab completion. Completion via ``_minethon:tabCompleteDone``."""
        try:
            self._helpers.startTabComplete(self._js_bot, text, assume_command, send_block_in_sight, timeout)
        except Exception as exc:
            raise BridgeError(f"start_tab_complete failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_write_book(self, slot: int, pages: list[str]) -> None:
        """Start writing a book. Completion via ``_minethon:writeBookDone``."""
        try:
            self._helpers.startWriteBook(self._js_bot, slot, pages)
        except Exception as exc:
            raise BridgeError(f"start_write_book failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_wait_for_chunks_to_load(self) -> None:
        """Start waiting for chunks. Completion via ``_minethon:chunksLoadedDone``."""
        try:
            self._helpers.startWaitForChunksToLoad(self._js_bot)
        except Exception as exc:
            raise BridgeError(f"start_wait_for_chunks_to_load failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_wait_for_ticks(self, ticks: int) -> None:
        """Start waiting for ticks. Completion via ``_minethon:waitForTicksDone``."""
        try:
            self._helpers.startWaitForTicks(self._js_bot, ticks)
        except Exception as exc:
            raise BridgeError(f"start_wait_for_ticks failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_click_window(self, slot: int, mouse_button: int, mode: int) -> None:
        """Start click window. Completion via ``_minethon:clickWindowDone``."""
        try:
            self._helpers.startClickWindow(self._js_bot, slot, mouse_button, mode)
        except Exception as exc:
            raise BridgeError(f"start_click_window failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_transfer(self, options: dict[str, Any]) -> None:
        """Start item transfer. Completion via ``_minethon:transferDone``."""
        try:
            self._helpers.startTransfer(self._js_bot, options)
        except Exception as exc:
            raise BridgeError(f"start_transfer failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_move_slot_item(self, source_slot: int, dest_slot: int) -> None:
        """Start moving slot item. Completion via ``_minethon:moveSlotItemDone``."""
        try:
            self._helpers.startMoveSlotItem(self._js_bot, source_slot, dest_slot)
        except Exception as exc:
            raise BridgeError(f"start_move_slot_item failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_put_away(self, slot: int) -> None:
        """Start putting away item. Completion via ``_minethon:putAwayDone``."""
        try:
            self._helpers.startPutAway(self._js_bot, slot)
        except Exception as exc:
            raise BridgeError(f"start_put_away failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_creative_fly_to(self, x: float, y: float, z: float) -> None:
        """Start creative fly-to. Completion via ``_minethon:creativeFlyToDone``."""
        try:
            Vec3 = self._runtime.require("vec3").Vec3
            dest = Vec3(x, y, z)
            self._helpers.startCreativeFlyTo(self._js_bot, dest)
        except Exception as exc:
            raise BridgeError(f"start_creative_fly_to failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_creative_set_inventory_slot(self, slot: int, item: Any) -> None:
        """Start creative set slot. Completion via ``_minethon:creativeSetSlotDone``."""
        try:
            self._helpers.startCreativeSetInventorySlot(self._js_bot, slot, item)
        except Exception as exc:
            raise BridgeError(f"start_creative_set_inventory_slot failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_creative_clear_slot(self, slot: int) -> None:
        """Start creative clear slot. Completion via ``_minethon:creativeClearSlotDone``."""
        try:
            self._helpers.startCreativeClearSlot(self._js_bot, slot)
        except Exception as exc:
            raise BridgeError(f"start_creative_clear_slot failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_creative_clear_inventory(self) -> None:
        """Start creative clear inventory. Completion via ``_minethon:creativeClearInventoryDone``."""
        try:
            self._helpers.startCreativeClearInventory(self._js_bot)
        except Exception as exc:
            raise BridgeError(f"start_creative_clear_inventory failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    def start_place_entity(self, js_reference_block: Any, face_x: float, face_y: float, face_z: float) -> None:
        """Start placing entity. Completion via ``_minethon:placeEntityDone``."""
        try:
            Vec3 = self._runtime.require("vec3").Vec3
            face_vec = Vec3(face_x, face_y, face_z)
            self._helpers.startPlaceEntity(self._js_bot, js_reference_block, face_vec)
        except Exception as exc:
            raise BridgeError(f"start_place_entity failed: {exc}", js_stack=extract_js_stack(exc)) from exc

    # -- Lifecycle --

    def quit(self) -> None:
        """Graceful disconnect."""
        if self._js_bot is not None:
            try:
                self._js_bot.quit()
            except Exception:
                pass  # Best-effort during shutdown
