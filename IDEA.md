預設大家的聊天室不會共用（透過其他插件做到）。只有自己的機器人和自己看得到對話文字，避免輸出偵錯內容、輸入指令時影響到大家
全部都是同步的行為

class Bot:
"""學員用：只給能互相組合的基本積木。原生型別、無 pathfinder。"""

    # ── 生命週期 ──
    def wait_spawn(self) -> None: ...                 # 卡住直到進入世界（讓學員寫直線腳本）
    def wait(self, seconds: float) -> None: ...       # 安全等待，維持連線

    # ── 位置與朝向（讀） ──
    def get_x(self) -> float: ...
    def get_y(self) -> float: ...
    def get_z(self) -> float: ...
    def get_pos(self) -> tuple[float, float, float]: ...
    def get_yaw(self) -> float: ...                   # ＋補：目前水平朝向
    def get_pitch(self) -> float: ...                 # ＋補：目前俯仰

    # ── 狀態（讀） ──
    def get_height(self) -> int: ...                  # 目前大小等級 1~5
    def get_sneak(self) -> bool: ...
    def is_riding(self) -> bool: ...  # ＋補：是否正坐在／騎在別的實體上
    def get_hand(self) -> tuple[str, int] | None: ... # (物品名, 數量) 或 None

    # ── 世界感知（讀）← 競賽必備，建議新增 ──
    def get_block(self, x: int, y: int, z: int) -> str | None: ...
    def get_block_property(self, x: int, y: int, z: int, property_name: str): ...  # ＋補：讀方塊屬性
    def get_block_in_front(self) -> tuple[tuple[int, int, int], str] | None: ...  # ＋補：正前方一格
    def look_block(self) -> tuple[tuple[int, int, int], str] | None: ...
    def find_block(self, name: str) -> tuple[int, int, int] | None: ...
    def find_blocks(self, name: str, max: int = 16) -> list[tuple[int, int, int]]: ...

    # ── 移動 ──
    def move_forward(self, blocks: float = 1.0) -> tuple[float, float, float]: ...
    def move_backward(self, blocks: float = 1.0) -> tuple[float, float, float]: ...
    def move_left(self, blocks: float = 1.0) -> tuple[float, float, float]: ...
    def move_right(self, blocks: float = 1.0) -> tuple[float, float, float]: ...
    def jump(self) -> tuple[float, float, float]: ...           # ＋補

    # ── 朝向（寫） ──
    def turn_left(self) -> tuple[float, float]: ...             # 預設 90°
    def turn_right(self) -> tuple[float, float]: ...
    def turn(self, degrees: float) -> tuple[float, float]: ...  # 相對轉
    def set_turn(self, yaw: float) -> tuple[float, float]: ...  # 絕對朝向
    def look_at(self, x: int, y: int, z: int) -> tuple[float, float]: ...  # ＋補：瞄準方塊

    # ── 大小 ──
    def set_height(self, level: int) -> None: ...     # 只接受 1~5，其餘報錯

    # ── 物品 ──
    def hold(self, name: str) -> bool: ...            # 原生字串，不用 Block/Item
    def unhold(self) -> bool: ...
    def drop(self) -> bool: ...

    # ── 行為（作用在「正在瞄準的方塊/面」）──
    def dig(self) -> tuple[tuple[int, int, int], str] | None: ...    # 原 break()，改名！
    def place(self) -> tuple[tuple[int, int, int], str] | None: ...
    def use(self) -> bool: ...
    def sneak(self, on: bool) -> bool: ...            # 持久狀態
    # def attack(self) -> bool: ...                   # （選）競賽若要打怪再加

    # ── 伺服器權威動作（關卡 datapack 驗證）──
    def action(self, name: str, value: int | None = None) -> None: ...  # ＋補：送 /trigger <帳號>_<動作>

    # ── 聊天 ──
    def chat(self, obj) -> None: ...                  # 公開聊天（str(obj)）；分組可見性由伺服器插件處理


# （原構想的 `_BotAdvance` 隱藏類別未實作——進階能力改由 `Bot.__getattr__`
#   直接委託 mineflayer JS proxy 提供，見 AGENTS.md「公開模組分層」。）
