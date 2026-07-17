"""Public exception hierarchy for minethon."""

from __future__ import annotations


class MinethonError(Exception):
    """Base class for user-facing minethon errors."""


class NotSpawnedError(MinethonError):
    """Raised when world-dependent APIs are used before the bot spawns."""


class PlayerNotFoundError(MinethonError):
    """Raised when a named player cannot be found.

    Reserved: no current student command looks up players by name, so nothing
    raises this yet — it exists so future named-player commands (look at /
    go to a player…) have their error type ready without an API break.
    """


class PluginNotInstalledError(MinethonError):
    """Raised when a plugin-backed attribute is accessed before installation."""


class VersionPinRequiredError(MinethonError):
    """Raised when a raw npm package is requested without an explicit version."""


__all__ = [
    "MinethonError",
    "NotSpawnedError",
    "PlayerNotFoundError",
    "PluginNotInstalledError",
    "VersionPinRequiredError",
]
