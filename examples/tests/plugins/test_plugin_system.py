"""測試 PluginAPI（插件管理系統）。

驗證項目:
- bot.plugins.supported 回傳支援的插件名稱 tuple
- bot.plugins.load(name) 載入插件
- bot.plugins.is_loaded(name) 查詢是否已載入
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import (
    check_false,
    check_true,
    check_type,
    info,
    passed,
    run_test,
    section,
)

from minethon import Bot


async def test_plugin_system(bot: Bot) -> None:
    # -- supported --
    section("supported")
    supported = bot.plugins.supported
    check_type("supported", supported, tuple)
    info(f"支援的插件數量: {len(supported)}")
    for name in supported:
        info(f"  - {name}")

    # -- is_loaded (未載入前) --
    section("is_loaded (載入前)")
    if supported:
        test_plugin = supported[0]
        # mineflayer-pathfinder 可能已自動載入，選一個未載入的
        for name in supported:
            if not bot.plugins.is_loaded(name):
                test_plugin = name
                break
        info(f"測試插件: {test_plugin}")
        was_loaded = bot.plugins.is_loaded(test_plugin)
        info(f"is_loaded({test_plugin!r}) = {was_loaded}")

        if not was_loaded:
            # -- load --
            section("load")
            bot.plugins.load(test_plugin)
            passed(f"load({test_plugin!r}) 成功")

            # -- is_loaded (載入後) --
            section("is_loaded (載入後)")
            check_true(
                f"is_loaded({test_plugin!r})", bot.plugins.is_loaded(test_plugin)
            )
        else:
            info(f"{test_plugin} 已被自動載入，驗證 is_loaded 為 True")
            check_true(
                f"is_loaded({test_plugin!r})", bot.plugins.is_loaded(test_plugin)
            )

    # -- 驗證未知插件 --
    section("is_loaded (未知插件)")
    check_false(
        "is_loaded('nonexistent-plugin')", bot.plugins.is_loaded("nonexistent-plugin")
    )


if __name__ == "__main__":
    asyncio.run(run_test("plugin_system", test_plugin_system))
