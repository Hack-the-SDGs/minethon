"""minethon -- A Python-first Mineflayer SDK."""

from minethon.api.navigation import NavigationAPI
from minethon.api.observe import ObserveAPI
from minethon.bot import Bot
from minethon.models.block import Block
from minethon.models.entity import Entity, EntityKind
from minethon.models.errors import (
    BridgeError,
    InventoryError,
    NavigationError,
    NotSpawnedError,
    PluginError,
    MinethonConnectionError,
    MinethonError,
)
from minethon.models.item import ItemStack
from minethon.models.vec3 import Vec3
from minethon.raw import RawBotHandle

__all__ = [
    # Core
    "Bot",
    "RawBotHandle",
    # Sub-APIs
    "NavigationAPI",
    "ObserveAPI",
    # Types
    "Block",
    "Entity",
    "EntityKind",
    "ItemStack",
    "Vec3",
    # Errors
    "BridgeError",
    "InventoryError",
    "MinethonConnectionError",
    "MinethonError",
    "NavigationError",
    "NotSpawnedError",
    "PluginError",
]
