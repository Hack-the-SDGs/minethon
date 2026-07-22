# q10_labfire state_2

已知迷宮 DFS。

管理員須先用 `function quests:q10_labfire/start {group:N}` 啟動同組任務；
`create_bot("g_labfire_2")` 會以本機組別登入並進入對應的 `world-g<N>`。

```bash
uv run python examples/quests/q10_labfire/state_2/main.py
```

`MAZE` 中：

- `0`：可走
- `1`：牆或柵欄

DFS 走到新格後遞迴，回來時用 backtracking 回到原格。
