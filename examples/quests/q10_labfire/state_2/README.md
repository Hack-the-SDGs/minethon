# q10_labfire state_2

已知迷宮 DFS。

```bash
uv run python examples/quests/q10_labfire/state_2/main.py
```

`MAZE` 中：

- `0`：可走
- `1`：牆或柵欄

DFS 走到新格後遞迴，回來時用 backtracking 回到原格。
