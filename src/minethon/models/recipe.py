"""Opaque recipe handle returned by mineflayer recipe queries.

Pure Python domain model — no JSPyBridge dependency.  The live JS
proxy is held in ``Bot._recipe_registry`` (keyed by ``id``), not here.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Recipe:
    """A typed handle to a mineflayer recipe.

    Treat as an opaque capability token returned by
    ``Bot.recipes_for()`` or ``Bot.recipes_all()`` and pass it back
    into ``Bot.craft()``.

    The underlying JS proxy is managed by ``Bot._recipe_registry``.
    Recipes are only valid for the session in which they were created;
    passing a stale ``Recipe`` from a previous connection will raise
    :class:`BridgeError`.
    """

    id: int
