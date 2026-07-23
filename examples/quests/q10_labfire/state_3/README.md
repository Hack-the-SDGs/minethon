# q10_labfire state_3

未知迷宮 online DFS。

程式不使用預先建立的地圖。每到一格才檢查四個方向，遇到牆就換方向；可以前進時記錄相對座標並遞迴，搜尋完再回到原格。是否完成由伺服器判定。

```bash
uv run python examples/quests/q10_labfire/state_3/main.py
```
