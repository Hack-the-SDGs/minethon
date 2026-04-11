# Window Tests

容器、合成、村民交易、熔爐/鐵砧等視窗操作測試。

## 遊戲模式: Survival

## 測試項目

- test_container.py — open_container、close_window、click_window、put_away、transfer、move_slot_item
- test_crafting.py — recipes_for、recipes_all、craft
- test_villager.py — open_villager、trade
- test_furnace_anvil.py — open_furnace、open_enchantment_table、open_anvil、write_book

## 前置條件

- test_container.py: 需放置箱子在 bot 附近
- test_crafting.py: 需給 bot 木材以合成木棍
- test_villager.py: 需有村民在附近
- test_furnace_anvil.py: 需放置熔爐、附魔台、鐵砧在附近；write_book 需有書與羽毛筆
