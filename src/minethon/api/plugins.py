"""Typed public plugin-management API."""

from minethon._bridge.plugin_host import PluginHost
from minethon.models.errors import PluginError


class PluginAPI:
    """Manage supported mineflayer plugins through a stable Python API."""

    _SUPPORTED_PLUGINS: tuple[str, ...] = ("mineflayer-pathfinder",)

    def __init__(self, host: PluginHost) -> None:
        self._host = host

    @property
    def supported(self) -> tuple[str, ...]:
        """Plugin package names that minethon currently wraps."""
        return self._SUPPORTED_PLUGINS

    def load(self, name: str) -> None:
        """Load a supported plugin by package name."""
        if name == "mineflayer-pathfinder":
            self._host.load_pathfinder()
            return
        raise PluginError(
            f"Unsupported plugin '{name}'. Supported plugins: {', '.join(self.supported)}"
        )

    def is_loaded(self, name: str) -> bool:
        """Whether a supported plugin is already active."""
        if name == "mineflayer-pathfinder":
            return self._host.is_pathfinder_loaded()
        raise PluginError(
            f"Unsupported plugin '{name}'. Supported plugins: {', '.join(self.supported)}"
        )
