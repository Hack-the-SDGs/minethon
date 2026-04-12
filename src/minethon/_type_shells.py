"""Runtime-importable type shells.

These classes exist so users can write annotations like
`from minethon.models import ChatMessage` without hitting ImportError.
Their real member surfaces live in `src/minethon/bot.pyi`.
"""

from __future__ import annotations


class _Shell:
    """Runtime type shell. See `minethon.bot` stubs for members."""


class Vec3(_Shell): ...


class ChatMessageScore(_Shell): ...


class ChatMessage(_Shell): ...


class Effect(_Shell): ...


class Entity(_Shell): ...


class Block(_Shell): ...


class Item(_Shell): ...


class Window(_Shell): ...


class Recipe(_Shell): ...


class Move(_Shell): ...


class Goal(_Shell): ...


class GoalBlock(_Shell): ...


class GoalNear(_Shell): ...


class GoalXZ(_Shell): ...


class GoalNearXZ(_Shell): ...


class GoalY(_Shell): ...


class GoalGetToBlock(_Shell): ...


class GoalFollow(_Shell): ...


class GoalCompositeAll(_Shell): ...


class GoalCompositeAny(_Shell): ...


class GoalInvert(_Shell): ...


class GoalPlaceBlock(_Shell): ...


class GoalLookAtBlock(_Shell): ...


class GoalBreakBlock(_Shell): ...


class Goals(_Shell): ...


class Movements(_Shell): ...


class Pathfinder(_Shell): ...


class ComputedPath(_Shell): ...


class PartiallyComputedPath(_Shell): ...


class PathfinderModule(_Shell): ...


class Player(_Shell): ...


class ChatPattern(_Shell): ...


class SkinParts(_Shell): ...


class GameSettings(_Shell): ...


class GameState(_Shell): ...


class Experience(_Shell): ...


class PhysicsOptions(_Shell): ...


class Time(_Shell): ...


class ControlStateStatus(_Shell): ...


class Instrument(_Shell): ...


class FindBlockOptions(_Shell): ...


class TransferOptions(_Shell): ...


class creativeMethods(_Shell): ...  # noqa: N801


class simpleClick(_Shell): ...  # noqa: N801


class Tablist(_Shell): ...


class chatPatternOptions(_Shell): ...  # noqa: N801


class CommandBlockOptions(_Shell): ...


class VillagerTrade(_Shell): ...


class Enchantment(_Shell): ...


class Chest(_Shell): ...


class Dispenser(_Shell): ...


class Furnace(_Shell): ...


class EnchantmentTable(_Shell): ...


class Anvil(_Shell): ...


class Villager(_Shell): ...


TYPE_SHELL_NAMES = (
    "Vec3",
    "ChatMessageScore",
    "ChatMessage",
    "Effect",
    "Entity",
    "Block",
    "Item",
    "Window",
    "Recipe",
    "Move",
    "Goal",
    "GoalBlock",
    "GoalNear",
    "GoalXZ",
    "GoalNearXZ",
    "GoalY",
    "GoalGetToBlock",
    "GoalFollow",
    "GoalCompositeAll",
    "GoalCompositeAny",
    "GoalInvert",
    "GoalPlaceBlock",
    "GoalLookAtBlock",
    "GoalBreakBlock",
    "Goals",
    "Movements",
    "Pathfinder",
    "ComputedPath",
    "PartiallyComputedPath",
    "PathfinderModule",
    "Player",
    "ChatPattern",
    "SkinParts",
    "GameSettings",
    "GameState",
    "Experience",
    "PhysicsOptions",
    "Time",
    "ControlStateStatus",
    "Instrument",
    "FindBlockOptions",
    "TransferOptions",
    "creativeMethods",
    "simpleClick",
    "Tablist",
    "chatPatternOptions",
    "CommandBlockOptions",
    "VillagerTrade",
    "Enchantment",
    "Chest",
    "Dispenser",
    "Furnace",
    "EnchantmentTable",
    "Anvil",
    "Villager",
)


class BotOptions(dict[str, object]):
    """Runtime shell for the generated `TypedDict` in `bot.pyi`."""
