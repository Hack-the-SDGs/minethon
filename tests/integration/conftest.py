"""Integration test fixtures.

Integration tests exercise the real JSPyBridge ↔ mineflayer path and need a
reachable Minecraft server. They are skipped unless explicitly requested with
``pytest -m integration``.
"""

from __future__ import annotations

import pytest


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip integration tests unless explicitly requested via ``-m``."""
    if "integration" not in (config.getoption("-m", default="") or ""):
        skip = pytest.mark.skip(reason="integration tests need -m integration")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip)
