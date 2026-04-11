# 移動測試

測試 bot 的移動相關 API：導航、視角控制、跳躍、載具操作。

## 測試清單

| 腳本 | 說明 |
|------|------|
| `test_goto.py` | `goto()` 導航至指定座標，驗證位置變化 |
| `test_look.py` | `look_at()` / `look()` 視角控制 |
| `test_jump.py` | `jump()` 跳躍，驗證 Y 座標變化 |
| `test_vehicle.py` | `mount()` / `dismount()` / `move_vehicle()` / `elytra_fly()` 載具操作 |

## 建議遊戲模式

Survival 或 Creative 皆可。載具測試需要附近有可騎乘生物（馬、豬等）。

## 執行

```bash
uv run --env-file examples/tests/.env examples/tests/movement/test_goto.py
uv run --env-file examples/tests/.env examples/tests/movement/test_look.py
uv run --env-file examples/tests/.env examples/tests/movement/test_jump.py
uv run --env-file examples/tests/.env examples/tests/movement/test_vehicle.py
```
