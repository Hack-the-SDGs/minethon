# Service Tests

Type B 服務測試（prismarine-viewer、mineflayer-web-inventory）。

## 遊戲模式: Any

## 測試項目

- test_viewer.py — ViewerAPI: start、stop、is_started
- test_inventory_viewer.py — InventoryViewerAPI: initialize、start、stop、is_running、is_initialized、port

## 前置條件

- 測試會啟動 HTTP 伺服器，確保 port 3007/3008 未被佔用
- 需手動開啟瀏覽器確認 UI 正常顯示
