# 物品欄測試

測試 bot 的物品欄相關 API：物品列表、裝備/卸裝、丟棄、使用/消耗。

## 測試清單

| 腳本 | 說明 |
|------|------|
| `test_inventory_items.py` | `get_inventory_items()` / `held_item` / `quick_bar_slot` / `set_quick_bar_slot()` |
| `test_equip_unequip.py` | `equip()` / `unequip()` 裝備與卸裝 |
| `test_toss.py` | `toss()` 丟棄物品 |
| `test_use_consume.py` | `use_item()` / `deactivate_item()` / `swing_arm()` / `consume()` |

## 建議遊戲模式

Survival 或 Creative。需要透過 `/give` 指令或手動交給 bot 物品。

## 執行

```bash
uv run --env-file examples/tests/.env examples/tests/inventory/test_inventory_items.py
uv run --env-file examples/tests/.env examples/tests/inventory/test_equip_unequip.py
uv run --env-file examples/tests/.env examples/tests/inventory/test_toss.py
uv run --env-file examples/tests/.env examples/tests/inventory/test_use_consume.py
```
