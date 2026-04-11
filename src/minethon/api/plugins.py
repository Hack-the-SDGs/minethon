"""Typed public plugin-management API."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from minethon._bridge.plugin_registry import PluginRegistry


class PluginAPI:
    """Manage supported mineflayer plugins through a stable Python API."""

    def __init__(self, registry: PluginRegistry) -> None:
        self._registry = registry

    @property
    def supported(self) -> tuple[str, ...]:
        """Plugin package names that minethon currently wraps."""
        return self._registry.supported

    def load(self, name: str) -> None:
        """Load a supported plugin by package name.

        This is a **synchronous blocking** call because JSPyBridge is
        thread-affine — all JS calls must happen on the bridge-owner
        thread.  The first load may take a while if Node.js needs to
        resolve or install the npm package.

        Raises:
            PluginError: If the plugin is not registered.
            BridgeError: If loading the JS module fails.
        """
        self._registry.load(name)

    def is_loaded(self, name: str) -> bool:
        """Whether a supported plugin is already active.

        Returns ``False`` for plugin names not in :attr:`supported`.
        """
        return self._registry.is_loaded(name)
