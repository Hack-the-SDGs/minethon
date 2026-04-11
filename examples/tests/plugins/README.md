# Plugin Tests

插件系統及個別 Type A 插件的測試。

## 遊戲模式: Varies

## 測試項目

- test_plugin_system.py — PluginAPI: supported、load、is_loaded
- test_armor.py — ArmorAPI: equip_best（需給 bot 盔甲）
- test_tool.py — ToolAPI: equip_for_block（需給 bot 工具）
- test_gui.py — GuiAPI: click_item、drop_item、raw_query（需給 bot 物品）
- test_panorama.py — PanoramaAPI (experimental): raw_take_panorama、raw_take_picture
- test_dashboard.py — DashboardAPI (experimental): log

## 前置條件

- 各測試的前置條件見腳本內說明
- panorama 需要 native `node-canvas-webgl` 環境
- dashboard 使用 blessed terminal UI，可能與 Python stdout 衝突
