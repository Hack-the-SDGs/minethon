# Lifecycle Tests

測試連線、重生、斷線等生命週期操作。

## 遊戲模式: Survival

## 測試項目

- test_connect_spawn.py — 連線、等待重生、斷線、is_connected、is_alive
- test_respawn.py — 死亡→重生循環、DeathEvent、RespawnEvent

## 前置條件

- test_respawn.py: 需手動殺死 bot 觸發死亡事件
