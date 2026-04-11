"""Weapon types supported by minecrafthawkeye.

Ref: minecrafthawkeye/dist/types/index.js — ``Weapons``
"""

from enum import Enum


class Weapon(Enum):
    """Projectile weapon type for hawkeye combat operations.

    Each value corresponds to the string key expected by the
    ``minecrafthawkeye`` JS API.

    Ref: minecrafthawkeye/dist/types/index.js:7-53
    """

    BOW = "bow"
    CROSSBOW = "crossbow"
    TRIDENT = "trident"
    ENDER_PEARL = "ender_pearl"
    SNOWBALL = "snowball"
    EGG = "egg"
    SPLASH_POTION = "splash_potion"
