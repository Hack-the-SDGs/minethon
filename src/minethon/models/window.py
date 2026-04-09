"""Typed window and villager session handles."""

from dataclasses import dataclass, field

from minethon.models.item import ItemStack


@dataclass(frozen=True, slots=True)
class WindowHandle:
    """A typed handle to an opened mineflayer window."""

    id: int
    title: str
    kind: str
    _raw: object = field(repr=False, compare=False, hash=False)


@dataclass(frozen=True, slots=True)
class TradeOffer:
    """A villager trade offer snapshot."""

    first_input: ItemStack
    output: ItemStack
    secondary_input: ItemStack | None
    disabled: bool
    uses: int
    max_uses: int


@dataclass(frozen=True, slots=True)
class VillagerSession:
    """A typed villager trading session handle."""

    id: int
    title: str
    trades: tuple[TradeOffer, ...]
    _raw: object = field(repr=False, compare=False, hash=False)
