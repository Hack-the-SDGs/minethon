"""q07_stack 本機實機測試解答（刻意不加入 Git）。

先由管理員 enable q07。真人進入自己的 world-g<N>，右鍵塔心的「開始任務」全像，
確認金色光柱出現後站在底座當第 1 層，再依序開 9 個終端執行:

    # 第 2 層: 疊在真人 TestPlayer 上
    uv run examples/quests/q07_stack/main.py 1 TestPlayer

    # 第 3 層以後: 自動疊在前一隻 bot 上
    uv run examples/quests/q07_stack/main.py 2
    uv run examples/quests/q07_stack/main.py 3
    ...
    uv run examples/quests/q07_stack/main.py 9

每個程序使用不同帳號 G<組別>_stack_<樓層編號>。真人是第 1 層，
所以參數 1 產生的 bot 是整座塔的第 2 層。
"""

from __future__ import annotations

import argparse

from minethon import Bot, PlayerNotFoundError, create_bot

MAX_BOT_LAYER = 9


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="啟動一隻 q07_stack 疊塔 bot")
    parser.add_argument(
        "layer",
        type=int,
        help="bot 編號 1 到 9，不同終端必須使用不同編號",
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="要疊上去的玩家名稱，layer=1 必填，其他層預設為前一隻 bot",
    )
    args = parser.parse_args()
    if not 1 <= args.layer <= MAX_BOT_LAYER:
        parser.error(f"layer 必須介於 1 到 {MAX_BOT_LAYER}")
    if args.layer == 1 and not args.target:
        parser.error("layer=1 時必須提供最底層真人玩家名稱")
    return args


def previous_bot_name(bot: Bot, layer: int) -> str:
    """由實際登入帳號推導同組前一層 bot 名稱。"""
    marker = "_stack_"
    username = str(bot.username)
    if marker not in username:
        raise RuntimeError(f"無法從登入帳號 {username!r} 推導 q07 組別")
    group_name, _ = username.split(marker, maxsplit=1)
    return f"{group_name}{marker}{layer - 1}"


def mount_target(bot: Bot, target: str) -> None:
    """持續讀取目標即時高度並右鍵，直到伺服器回報 bot 已成為乘客。"""
    attempts = 0
    while getattr(bot.entity, "vehicle", None) is None:
        attempts += 1
        try:
            bot.use_player(target)
        except PlayerNotFoundError:
            if attempts % 10 == 0:
                print(f"仍在等待 {target} 進入同世界與 entity 載入範圍...", flush=True)
            bot.wait(0.25)
            continue

        # use_player() 代表互動封包已送出，再等待 GSit 建立乘坐關係。
        for _ in range(10):
            if getattr(bot.entity, "vehicle", None) is not None:
                print(f"已成功疊到 {target} 上方。", flush=True)
                return
            bot.wait(0.1)

        if attempts % 5 == 0:
            print(
                "互動已送出但尚未乘坐，請檢查 GSit.PlayerSit 與 WorldGuard flags。",
                flush=True,
            )


def main() -> None:
    args = parse_args()
    bot = create_bot(f"g_stack_{args.layer}", instruction_sleep=0.1)
    target = args.target or previous_bot_name(bot, args.layer)
    print(f"{bot.username} 已登入，準備疊到 {target} 上。", flush=True)
    mount_target(bot, target)
    bot.run_forever()


if __name__ == "__main__":
    main()
