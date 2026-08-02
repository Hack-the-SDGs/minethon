"""Shared guards for unit tests.

單元測試絕對不能碰到真正的 JSPyBridge——`get_vec3` 會啟動 node 並在
javascript 套件目錄跑 npm install，在 CI 的乾淨環境裡是網路運氣問題
（Release & Publish 就這樣紅過一次）。這裡用 autouse fixture 把
`_commands.get_vec3` 換成 tuple 工廠——個別測試仍可用自己的
monkeypatch 覆蓋。需要真 Vec3 的測試請標 integration。
"""

from __future__ import annotations

import pytest

import minethon._commands as cmd


@pytest.fixture(autouse=True)
def _stub_get_vec3(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cmd, "get_vec3", lambda: lambda x, y, z: (x, y, z))
