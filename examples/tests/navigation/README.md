# Navigation Tests

PathFinder 導航測試，驗證 `bot.navigation` 所有公開方法。

## 遊戲模式: Survival

## 測試項目

- test_pathfinder.py — goto、follow、stop、is_navigating

## 前置條件

- mineflayer-pathfinder 會自動載入，無需手動 `bot.plugins.load()`
- test_pathfinder.py: `follow` 測試需要另一位玩家在場
