"""Bot configuration."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BotConfig:
    """Configuration for creating a Bot.

    Args:
        host: Server hostname or IP.
        port: Server port.
        username: Bot username.
        password: Account password (for authenticated servers).
        version: Minecraft version string (e.g. ``"1.20.1"``).
            Auto-detected when ``None``.
        auth: Authentication mode (``"microsoft"``, ``"mojang"``,
            ``"offline"``, or ``None`` for default).
        auth_server: Custom authentication server URL
            (e.g. ``"https://drasl.example.com/auth"``).
        session_server: Custom session server URL
            (e.g. ``"https://drasl.example.com/session"``).
        hide_errors: Suppress internal error logging from mineflayer.
        log_errors: Log errors to the console.
        disable_chat_signing: Disable chat message signing (1.19.1+).
        check_timeout_interval: Milliseconds between keep-alive checks.
            Set to ``0`` to disable. ``None`` uses mineflayer's default
            (currently ``30_000``).
        keep_alive: Send keep-alive packets.
        respawn: Auto-respawn after death.
        chat_length_limit: Maximum chat message length.
        view_distance: Client-side view distance
            (``"tiny"``, ``"short"``, ``"normal"``, ``"far"``).
        default_chat_patterns: Enable default chat pattern parsing.
        physics_enabled: Enable client-side physics simulation.
        brand: Custom client brand string.
        skip_validation: Skip account validation on login.
        profiles_folder: Path to the folder containing auth profiles.
        load_internal_plugins: Load mineflayer's built-in plugins.
    """

    host: str
    port: int = 25565
    username: str = "pyflayer"
    password: str | None = None
    version: str | None = None
    auth: str | None = None
    auth_server: str | None = None
    session_server: str | None = None
    hide_errors: bool = False
    log_errors: bool | None = None
    disable_chat_signing: bool = False
    check_timeout_interval: int | None = None
    keep_alive: bool | None = None
    respawn: bool | None = None
    chat_length_limit: int | None = None
    view_distance: str | None = None
    default_chat_patterns: bool | None = None
    physics_enabled: bool | None = None
    brand: str | None = None
    skip_validation: bool | None = None
    profiles_folder: str | None = None
    load_internal_plugins: bool | None = None
