# GENERATED FROM mineflayer/index.d.ts — DO NOT EDIT MANUALLY.
# Regenerate via: uv run python scripts/generate_stubs.py
#
# This file is the IDE completion overlay for src/minethon/bot.py.
# Runtime behavior lives in bot.py; types live here.
#
# Ref: src/mineflayer/js/node_modules/mineflayer/index.d.ts
# Ref: src/mineflayer/js/node_modules/vec3/index.d.ts
# Ref: src/mineflayer/js/node_modules/prismarine-entity/index.d.ts
# Ref: src/mineflayer/js/node_modules/prismarine-block/index.d.ts
# Ref: src/mineflayer/js/node_modules/prismarine-item/index.d.ts
# Ref: src/mineflayer/js/node_modules/prismarine-chat/index.d.ts
# Ref: src/mineflayer/js/node_modules/prismarine-windows/index.d.ts
# Ref: src/mineflayer/js/node_modules/prismarine-recipe/index.d.ts
from __future__ import annotations

from collections.abc import Callable
from typing import Literal, Self, TypedDict, overload


# --- External types (from vec3 / prismarine-* packages) ---
# These are Protocol stubs mirroring the fields/methods used by mineflayer.
# Ref: src/mineflayer/js/node_modules/<pkg>/index.d.ts

class Vec3:
    """三維向量
    Minecraft 的位置、速度、方向都用這個類
    支援各種位移、距離、算術運算；**多數「帶 `ed` 結尾」的 method 回傳新物件，不會修改自身**；不帶的多為 in-place 修改
    """
    x: float
    """X 軸座標"""
    y: float
    """Y 軸座標"""
    z: float
    """Z 軸座標"""
    def isZero(self) -> bool:
        """是否為零向量（三軸皆為 `0`）

        Returns:
            布林
        """
        ...
    def at(self, id: int) -> float:
        """依索引取軸座標：`0` 取 x、`1` 取 y、`2` 取 z

        Args:
            id: 索引 `0` / `1` / `2`
        """
        ...
    def xz(self) -> tuple[float, float]:
        """以 `(x, z)` 回傳長度 2 的 tuple"""
        ...
    def xy(self) -> tuple[float, float]:
        """以 `(x, y)` 回傳長度 2 的 tuple"""
        ...
    def yz(self) -> tuple[float, float]:
        """以 `(y, z)` 回傳長度 2 的 tuple"""
        ...
    def xzy(self) -> Vec3:
        """Returns:
            一個新 `Vec3`，y 與 z 互換（座標變 `(x, z, y)`）
        """
        ...
    def set(self, x: float, y: float, z: float) -> Self:
        """**原地**修改三軸為給定值，回傳自身

        Args:
            x: 新的軸座標值
            y: 新的軸座標值
            z: 新的軸座標值
        """
        ...
    def update(self, other: Vec3) -> Self:
        """**原地**把自己的值複製成 `other` 的值，回傳自身

        Args:
            other: 來源 `Vec3`
        """
        ...
    def rounded(self) -> Vec3:
        """Returns:
            一個新 `Vec3`，各軸四捨五入到整數
        """
        ...
    def round(self) -> Self:
        """**原地**四捨五入各軸，回傳自身"""
        ...
    def floored(self) -> Vec3:
        """Returns:
            一個新 `Vec3`，各軸向下取整。用來把浮點位置對齊到所屬方塊座標時常用
        """
        ...
    def floor(self) -> Self:
        """**原地**向下取整，回傳自身"""
        ...
    def offset(self, dx: float, dy: float, dz: float) -> Vec3:
        """Args:
            dx: 各軸偏移量（浮點數）
            dy: 各軸偏移量（浮點數）
            dz: 各軸偏移量（浮點數）

        Returns:
            一個新的 `Vec3`，座標為自身加上 `(dx, dy, dz)`。**不會修改自身**

        ```python
        feet = bot.entity.position
        head = feet.offset(0, bot.entity.height, 0)
        ```
        """
        ...
    def translate(self, dx: float, dy: float, dz: float) -> Self:
        """**原地**位移，回傳自身

        Args:
            dx: 各軸位移量
            dy: 各軸位移量
            dz: 各軸位移量
        """
        ...
    def add(self, other: Vec3) -> Self:
        """**原地**加上另一向量，回傳自身

        Args:
            other: `Vec3`
        """
        ...
    def subtract(self, other: Vec3) -> Self:
        """**原地**減去另一向量"""
        ...
    def multiply(self, other: Vec3) -> Self:
        """**原地**各軸相乘"""
        ...
    def divide(self, other: Vec3) -> Self:
        """**原地**各軸相除"""
        ...
    def plus(self, other: Vec3) -> Vec3:
        """Returns:
            新的 `Vec3`，座標是自身加上 `other` 的各軸值
        """
        ...
    def minus(self, other: Vec3) -> Vec3:
        """Returns:
            新的 `Vec3`，座標是自身減去 `other`
        """
        ...
    def scaled(self, scalar: float) -> Vec3:
        """Returns:
            新的 `Vec3`，各軸座標都乘上 `scalar`
        """
        ...
    def abs(self) -> Vec3:
        """Returns:
            一個新 `Vec3`，各軸取絕對值
        """
        ...
    def volume(self) -> float:
        """Returns:
            `x * y * z` 的體積
        """
        ...
    def modulus(self, other: Vec3) -> Vec3:
        """Returns:
            一個新 `Vec3`，對 `other` 取 modulo
        """
        ...
    def distanceTo(self, other: Vec3) -> float:
        """Returns:
            到另一個向量的歐氏距離
        """
        ...
    def distanceSquared(self, other: Vec3) -> float:
        """Returns:
            到另一向量的歐氏距離**平方**
        """
        ...
    def equals(self, other: Vec3, error: float = ...) -> bool:
        """判斷兩個向量是否「近乎相等」

        Args:
            other: 要比較的另一個 `Vec3`
            error: 允許的誤差；省略時要完全相等
        """
        ...
    def toString(self) -> str:
        """Returns:
            `"(x, y, z)"` 格式的字串
        """
        ...
    def clone(self) -> Vec3:
        """Returns:
            一個和自身相同座標的新 `Vec3`。避免意外修改共用物件時使用
        """
        ...
    def min(self, other: Vec3) -> Vec3:
        """Returns:
            新 `Vec3`，各軸取兩者最小值
        """
        ...
    def max(self, other: Vec3) -> Vec3:
        """Returns:
            新 `Vec3`，各軸取兩者最大值
        """
        ...
    def norm(self) -> float:
        """Returns:
            向量長度
        """
        ...
    def dot(self, other: Vec3) -> float:
        """Returns:
            與另一向量的點積
        """
        ...
    def cross(self, other: Vec3) -> Vec3:
        """Returns:
            與另一向量的外積結果新 `Vec3`
        """
        ...
    def unit(self) -> Vec3:
        """Returns:
            單位化後的新 `Vec3`（方向相同、長度 1）；零向量會回傳零向量
        """
        ...
    def normalize(self) -> Vec3:
        """**原地**單位化，回傳自身"""
        ...
    def scale(self, scalar: float) -> Self:
        """**原地**把各軸乘上 `scalar`，回傳自身

        Args:
            scalar: 純量
        """
        ...
    def xyDistanceTo(self, other: Vec3) -> float:
        """只考慮 x、y 軸的距離"""
        ...
    def xzDistanceTo(self, other: Vec3) -> float:
        """只考慮 x、z 軸的距離（忽略 y）
        Minecraft 算「水平距離」最常用這個
        """
        ...
    def yzDistanceTo(self, other: Vec3) -> float:
        """只考慮 y、z 軸的距離"""
        ...
    def innerProduct(self, other: Vec3) -> float:
        """Returns:
            內積
        """
        ...
    def manhattanDistanceTo(self, other: Vec3) -> float:
        """Returns:
            曼哈頓距離
        """
        ...
    def toArray(self) -> tuple[float, float, float]:
        """Returns:
            `[x, y, z]` 的 tuple
        """
        ...


class ChatMessage:
    """Minecraft 聊天訊息物件
    伺服器 emit 的事件參數多半是這個類型；需要印字時用 `.toString()` 或 `.toAnsi()`
    """
    json: object
    """原始的 JSON 物件"""
    extra: list[ChatMessage] | None
    """額外 children 訊息陣列（ChatMessage 本身是樹狀結構），沒有則為 `None`"""
    translate: str | None
    """(選填) 訊息對應的翻譯 key，例如 `"chat.type.text"`"""
    selector: str | None
    keybind: str | None
    score: object | None
    def append(self, *messages: object) -> None:
        """把一到多個子訊息或字串附加到自身"""
        ...
    def clone(self) -> ChatMessage:
        """Returns:
            一個同內容的新 `ChatMessage`
        """
        ...
    def toString(self, language: object = ...) -> str:
        """攤平為純文字字串（**去除所有顏色與樣式**）
        通常學生只會用這個

        Args:
            language: (選填) 翻譯字典物件；預設使用內建 English 翻譯表
        """
        ...
    def toMotd(self, language: object = ...) -> str:
        """攤平為含 `§x` 顏色碼的字串"""
        ...
    def toAnsi(self, language: object = ...) -> str:
        """攤平為 ANSI 跳脫碼字串——印到終端機會顯示真正的顏色"""
        ...
    def toHTML(self, language: object = ..., styles: object = ...) -> str:
        """攤平為 HTML 字串，含內嵌 CSS"""
        ...
    def length(self) -> int:
        """取得這則訊息的子元件數量"""
        ...
    def getText(self, idx: int, language: object = ...) -> str:
        """取得第 `idx` 個子元件的純文字"""
        ...
    def valueOf(self) -> str:
        """同 `toString()`，供 `str()` / `+` 字串拼接使用"""
        ...


EntityType = Literal['player', 'mob', 'object', 'global', 'orb', 'projectile', 'hostile', 'other']


class Effect:
    """狀態效果物件"""
    id: int
    """狀態效果的數字 ID"""
    amplifier: int
    """等級 `0` ~ `N`（**從 0 開始**）
    Minecraft 的「力量 II」在這裡是 `amplifier=1`
    """
    duration: int
    """剩餘持續時間"""


class Entity:
    """世界中任意實體的抽象
    玩家、怪物、掉落物、箭、船、末影珍珠等都是 `Entity`
    """
    id: int
    """實體在當前世界中的整數 ID"""
    type: EntityType
    """實體類別字串：`"player"` / `"mob"` / `"object"` / `"global"` / `"orb"` / `"projectile"` / `"hostile"` / `"other"`
    用來快速判斷要如何對待它
    """
    uuid: str | None
    """實體的 UUID 字串"""
    username: str | None
    """若為玩家實體（`type == "player"`），這裡是玩家名稱；其他實體則為 `None`"""
    mobType: str | None
    """生物類型字串（例如 `"Zombie"`、`"Cow"`）；非生物 entity 為 `None`"""
    displayName: str | None
    """實體的顯示名稱字串；若沒有自訂名稱可能為 `None`"""
    entityType: int | None
    """舊版用的實體類型數字 ID"""
    kind: str | None
    """大分類字串，例如 `"Hostile mobs"`、`"Passive mobs"`、`"Vehicles"`"""
    name: str | None
    """內部名稱字串"""
    objectType: str | None
    """非生物類實體（如物品、投擲物）的類別字串"""
    count: int | None
    """掉落物實體的數量；非掉落物為 `None`"""
    position: Vec3
    """實體目前位置的 `Vec3`"""
    velocity: Vec3
    """實體當下的速度向量"""
    yaw: float
    """水平朝向"""
    pitch: float
    """俯仰角（弧度）；正值朝下、負值朝上"""
    height: float
    """實體的高度（方塊為單位）
    玩家約 `1.8`
    """
    width: float
    """實體寬度"""
    onGround: bool
    """是否站在地上"""
    equipment: list[Item]
    """實體身上的裝備陣列，索引 `0` = 主手、`1` = 腳、`2` = 腿、`3` = 胸、`4` = 頭
    沒穿為 `None`
    """
    heldItem: Item
    """實體手上拿的物品 `Item`"""
    metadata: list[object]
    """實體的 raw metadata 陣列
    包含旗標（例如著火、隱形）、當前狀態值等
    結構原生、不易解析，除錯用
    """
    isValid: bool
    """實體是否仍在世界中（布林）
    已消失 / 超出視野的實體會變 `False`
    """
    health: float | None
    """實體目前血量（若伺服器有送出血量資訊）；無資訊時為 `None`"""
    food: float | None
    """若為玩家，這裡是飽食度 `[0, 20]`；其他實體為 `None`"""
    foodSaturation: float | None
    """若為玩家，飽食度緩衝；其他實體為 `None`"""
    elytraFlying: bool | None
    """實體目前是否張開鞘翅飛行中"""
    player: object | None
    """若為玩家實體，這裡是 `Player` 物件（含 `ping`、`uuid` 等）；其他實體為 `None`"""
    effects: list[Effect]
    """實體身上的狀態效果陣列，每個元素是 `Effect`"""
    vehicle: Entity
    """實體目前所騎的載具 `Entity`，沒有則為 `None`"""
    passengers: list[Entity]
    """騎在這個實體身上的乘員 `Entity` 陣列"""
    def setEquipment(self, index: int, item: Item) -> None:
        """更新實體指定裝備槽的顯示物品

        Args:
            index: `0` 主手、`1` 腳、`2` 腿、`3` 胸、`4` 頭
            item: 要顯示的 `Item`
        """
        ...
    def getCustomName(self) -> ChatMessage | None:
        """Returns:
            實體的自訂名稱 `ChatMessage`，沒有則為 `None`
        """
        ...
    def getDroppedItem(self) -> Item | None:
        """若此實體是掉落物 entity，回傳其物品 `Item`，否則為 `None`"""
        ...


class Block:
    """世界中一格方塊的表示"""
    stateId: int
    """方塊的 state 數字 ID（1.13+ flattening 後的真正唯一識別碼）
    新版 pattern 請優先用這個
    """
    type: int
    """方塊的數字 ID"""
    metadata: int
    """方塊的 metadata 整數值；依方塊類型有不同語意"""
    light: int
    """方塊的可見光等級 `0` ~ `15`"""
    skyLight: int
    """方塊的天光等級 `0` ~ `15`"""
    blockEntity: object
    """若為含資料的方塊（招牌、箱子、音符盒等），這裡是它的 NBT-like 物件"""
    entity: object | None
    """若方塊本身是 entity（少見），這裡是 raw NBT；否則為 `None`"""
    hash: int | None
    """Bedrock Edition 專用的方塊狀態雜湊值；Java 平台上通常為 `None`"""
    biome: object
    """所在生物群系 `Biome` 物件"""
    name: str
    """方塊的 Minecraft 名稱 ID，例如 `"stone"` / `"diamond_ore"`"""
    displayName: str
    """方塊的顯示名稱（英文），例如 `"Stone"` / `"Diamond Ore"`"""
    shapes: list[tuple[float, float, float, float, float, float]]
    """方塊的碰撞形狀陣列，每個元素是 `[xmin, ymin, zmin, xmax, ymax, zmax]` 的邊界盒"""
    hardness: float
    """方塊的硬度值（浮點數）；愈大代表空手打愈久"""
    boundingBox: Literal['block', 'empty']
    """物理判定的大致形狀字串：`"block"`（實心 / 半實心）或 `"empty"`"""
    transparent: bool
    """方塊視覺上是否半透明"""
    diggable: bool
    """這個方塊是否可以被挖（布林）
    基岩這類是 `False`
    """
    isWaterlogged: bool | None
    """方塊目前是否含水（1.13+ 的水方塊疊加機制）
    非水方塊型態可能為 `None`
    """
    material: str | None
    """材質分類字串：`"rock"`、`"wood"`、`"plant"`、`"dirt"`、`"web"` 等；可能為 `None`
    用來判斷該用什麼工具挖
    """
    harvestTools: dict[str, bool] | None
    """可以有效採集此方塊的工具 ID 字典 `{itemId: True}`；空的話代表空手也能採集"""
    position: Vec3
    """方塊在世界中的 `Vec3` 座標"""
    def canHarvest(self, heldItemType: int | None) -> bool:
        """能否用目前持有的工具收穫這個方塊

        Args:
            heldItemType: 手上工具的物品 ID 整數，或 `None` 代表空手
        """
        ...
    def getProperties(self) -> dict[str, object]:
        """解析 block state，回傳屬性字典"""
        ...
    def digTime(
        self,
        heldItemType: int | None,
        creative: bool,
        inWater: bool,
        notOnGround: bool,
        enchantments: object = ...,
        effects: list[Effect] | None = ...,
    ) -> float:
        """估算挖掉此方塊所需毫秒數（與 `bot.digTime(block)` 相似但更細，可指定環境參數）

        Args:
            heldItemType: 手持工具 ID，空手為 `None`
            creative: 是否創造模式
            inWater: 是否在水中
            notOnGround: 是否在空中（沒踏地）
            enchantments: (選填) 工具上的附魔列表
            effects: (選填) 身上的狀態效果列表
        """
        ...


class Item:
    """物品堆疊的表示"""
    type: int
    """物品的數字 ID"""
    slot: int
    """這個物品目前所在的槽位編號"""
    count: int
    """這堆物品的數量"""
    metadata: int
    """物品的 metadata 整數值"""
    nbt: object | None
    """raw NBT 資料物件（附魔、自訂名稱、耐久等都在裡面）；沒有則為 `None`"""
    stackId: int | None
    """多玩家共享場景中物品堆疊的識別碼，1.17.1+ 才有；否則為 `None`"""
    name: str
    """物品的 Minecraft 名稱 ID，例如 `"diamond"` / `"iron_pickaxe"`"""
    displayName: str
    """物品的顯示名稱"""
    stackSize: int
    """這種物品單格最多能疊幾個"""
    maxDurability: int
    """工具 / 武器 / 護甲的最大耐久；沒有耐久概念的物品為 `0`"""
    durabilityUsed: int
    """工具已經消耗掉多少耐久
    剩餘耐久 = `maxDurability - durabilityUsed`
    """
    enchants: list[dict[str, object]]
    """附魔列表，陣列元素形如 `{name: "sharpness", lvl: 3}`"""
    blocksCanPlaceOn: list[tuple[str]]
    """冒險模式下此物品可以放置在哪些方塊上"""
    blocksCanDestroy: list[tuple[str]]
    """冒險模式下此物品可以破壞哪些方塊"""
    repairCost: int
    """物品在鐵砧維修所需的等級代價"""
    customName: str | None
    """玩家自訂的顯示名稱字串，沒取名為 `None`"""
    customLore: str | list[str] | None
    """玩家自訂的 lore（補充說明），可能是單一字串、字串陣列，或 `None`"""
    customModel: str | None
    """自訂 model string（用於資源包），沒有為 `None`"""
    spawnEggMobName: str
    """若為生怪蛋，這裡是它會生出的生物名稱字串"""


class Window:
    """開啟的任意容器 / 視窗"""
    id: int
    """視窗的協定 ID"""
    type: int | str
    title: str
    """視窗標題字串"""
    slots: list[Item | None]
    """視窗中所有物品槽位的陣列；空槽為 `None`"""
    inventoryStart: int
    """玩家物品欄區塊在整個 slots 陣列中的起始索引"""
    inventoryEnd: int
    """玩家物品欄區塊的結束索引"""
    hotbarStart: int
    """快捷欄區塊的起始索引"""
    craftingResultSlot: int
    """合成結果槽的索引；沒有合成區則為 `-1`"""
    requiresConfirmation: bool
    selectedItem: Item | None
    """目前游標上拿著的 `Item`（滑鼠按住拖放用），沒有則為 `None`"""
    def findInventoryItem(
        self, itemType: int, metadata: int | None, notFull: bool
    ) -> Item | None:
        """在玩家物品欄中找第一個符合的 `Item`，沒找到回 `None`

        Args:
            itemType: 物品 ID 整數
            metadata: metadata；不關心傳 `None`
            notFull: `True` 代表只要沒達 stackSize 的那堆
        """
        ...
    def findContainerItem(
        self, itemType: int, metadata: int | None, notFull: bool
    ) -> Item | None:
        """同上但在容器區找"""
        ...
    def firstEmptySlotRange(self, start: int, end: int) -> int | None:
        """在指定範圍中找第一個空槽的編號，沒找到回 `None`"""
        ...
    def firstEmptyHotbarSlot(self) -> int | None:
        """快捷欄中第一個空槽的編號，找不到回 `None`"""
        ...
    def firstEmptyContainerSlot(self) -> int | None:
        """容器區中第一個空槽的編號"""
        ...
    def firstEmptyInventorySlot(self, hotbarFirst: bool = ...) -> int | None:
        """物品欄中第一個空槽的編號

        Args:
            hotbarFirst: 預設 `True`，先從快捷欄找
        """
        ...
    def items(self) -> list[Item]:
        """Returns:
            玩家物品欄中的所有物品 `Item` 陣列
        """
        ...
    def containerItems(self) -> list[Item]:
        """Returns:
            容器區所有物品 `Item` 陣列
        """
        ...
    def count(self, itemType: int | str, metadata: int | None) -> int:
        """玩家物品欄中有多少指定物品

        Args:
            itemType: 物品 ID 或名稱
            metadata: 目標 metadata；不關心傳 `None`
        """
        ...
    def emptySlotCount(self) -> int:
        """玩家物品欄中空槽的數量"""
        ...


class Recipe:
    """合成配方物件
    由 `bot.recipesFor(...)` 取得
    """
    result: object
    """合成產出的 `RecipeItem`"""
    inShape: list[list[object]]
    """輸入配方的形狀（2D 陣列），空格為 `None`"""
    outShape: list[list[object]]
    """輸出配方的形狀"""
    ingredients: list[object]
    """合成需要的材料 `RecipeItem` 陣列"""
    delta: list[object]
    """合成後物品欄的變化量"""
    requiresTable: bool
    """是否需要工作台（布林）
    `False` 代表玩家 2x2 合成區就能做
    """


# --- mineflayer-pathfinder stubs ---
# Only pathfinder gets a typed wrapper (AGENTS.md: all other plugins go
# through `bot.require(...)` and their own README).
# Ref: node_modules/mineflayer-pathfinder/index.d.ts

class Move:
    x: float
    y: float
    z: float
    cost: float
    remainingBlocks: int
    parkour: bool
    hash: str


class Goal:
    """所有目標類別的基底
    學生通常直接用 `GoalNear` 等子類而不是這個
    """
    def hasChanged(self) -> bool:
        """目標參數是否自上次尋路後有改動"""
        ...
    def isValid(self) -> bool:
        """目標是否仍然可以作為有效目標"""
        ...


class GoalBlock(Goal):
    """抵達指定整數座標那格方塊上
    需要精確落地時使用
    """
    x: float
    y: float
    z: float
    def __init__(self, x: float, y: float, z: float) -> None: ...


class GoalNear(Goal):
    """最常用的目標：抵達 `(x, y, z)` 附近 `range` 格內即算到達

    Args:
        x: 目標世界座標
        y: 目標世界座標
        z: 目標世界座標

    Args:
        range: 容許的半徑（方塊為單位）
    """
    x: float
    y: float
    z: float
    rangeSq: float
    def __init__(self, x: float, y: float, z: float, range: float) -> None: ...


class GoalXZ(Goal):
    """抵達指定 X / Z 平面，Y 不限"""
    x: float
    z: float
    def __init__(self, x: float, z: float) -> None: ...


class GoalNearXZ(Goal):
    """同 `GoalXZ` 但帶距離容許值：抵達 `(x, z)` 平面 `range` 格內即算達成，Y 不限

    Args:
        x: 水平座標
        z: 水平座標

    Args:
        range: 容許半徑
    """
    x: float
    z: float
    rangeSq: float
    def __init__(self, x: float, z: float, range: float) -> None: ...


class GoalY(Goal):
    """爬升 / 下降到指定 Y 高度；X、Z 不限"""
    y: float
    def __init__(self, y: float) -> None: ...


class GoalGetToBlock(Goal):
    """抵達指定整數座標**旁邊**
    適合用來走到箱子前、工作台前這類需要「站旁邊操作」的物件
    """
    x: float
    y: float
    z: float
    def __init__(self, x: float, y: float, z: float) -> None: ...


class GoalFollow(Goal):
    """持續跟著某個實體，保持距離在 `range` 格內
    搭配 `setGoal(..., dynamic=True)` 使用

    Args:
        entity: 要跟隨的 `Entity`
        range: 保持的距離上限
    """
    x: float
    y: float
    z: float
    entity: Entity
    rangeSq: float
    def __init__(self, entity: Entity, range: float) -> None: ...


class GoalCompositeAll(Goal):
    """只有全部子目標都滿足時才算達成
    通常用來疊加多個空間約束
    """
    def __init__(self, goals: list[Goal] = ...) -> None: ...
    def push(self, goal: Goal) -> None: ...


class GoalCompositeAny(Goal):
    """任一子目標達成就結束
    適合「到達任一地標即可」的需求
    """
    def __init__(self, goals: list[Goal] = ...) -> None: ...
    def push(self, goal: Goal) -> None: ...


class GoalInvert(Goal):
    """把一個「抵達某點」目標翻轉成「遠離某點」——會朝讓啟發式最大化的方向移動"""
    def __init__(self, goal: Goal) -> None: ...


class Goals:
    """Container exposing pathfinder's goal constructors.

    Accessed via `pf.goals.GoalNear(...)` where
    `pf = bot.load_plugin('mineflayer-pathfinder')`.
    """
    Goal: type[Goal]
    GoalBlock: type[GoalBlock]
    GoalNear: type[GoalNear]
    GoalXZ: type[GoalXZ]
    GoalNearXZ: type[GoalNearXZ]
    GoalY: type[GoalY]
    GoalGetToBlock: type[GoalGetToBlock]
    GoalFollow: type[GoalFollow]
    GoalCompositeAll: type[GoalCompositeAll]
    GoalCompositeAny: type[GoalCompositeAny]
    GoalInvert: type[GoalInvert]


class Movements:
    """尋路的移動規則集合
    決定機器人能挖、能跳、能游、能跑、允許哪些方塊放置等
    """
    canDig: bool
    """是否允許為了開路而挖方塊"""
    canOpenDoors: bool
    """是否允許開門穿過"""
    allow1by1towers: bool
    """是否允許在原地往上疊方塊製作 1x1 高塔"""
    allowFreeMotion: bool
    """是否允許「直線穿越」非方塊化地形"""
    allowParkour: bool
    """是否允許跨越需要跳躍的距離"""
    allowSprinting: bool
    """是否允許跑步（布林）
    跑步比較快但耗更多食物
    """
    allowEntityDetection: bool
    """是否偵測會阻擋路徑的實體（布林）
    開啟後尋路每次會重新掃附近實體，耗一點效能但比較安全
    """
    digCost: float
    """為了開路而挖方塊時加在路徑成本上的懲罰值
    預設較大以降低挖路傾向
    """
    placeCost: float
    """為了開路而放置方塊時的成本懲罰"""
    maxDropDown: int
    """允許直接向下跳躍的最大高度（方塊數）
    超過這個值會找別的路或不通
    """
    def __init__(self, bot: object) -> None: ...


class Pathfinder:
    """尋路插件提供給機器人的執行時 API
    載入插件後會自動掛在 `bot.pathfinder` 上
    """
    thinkTimeout: int
    """尋路總思考時間上限（毫秒）
    超過會停下來並 emit `path_update` 回報 timeout
    """
    tickTimeout: int
    """每個 tick 內思考時間上限"""
    def setGoal(self, goal: Goal | None, dynamic: bool = ...) -> None:
        """設定機器人要去的目標；會在背景持續尋路並移動
        傳 `None` 可取消當前任務

        Args:
            goal: 任一 `Goal` 實例；`None` 代表取消
            dynamic: 預設 `False`。設 `True` 時，目標位置會被持續重新檢查（適合跟隨會移動的實體）
        """
        ...
    def setMovements(self, movements: Movements) -> None:
        """套用一套移動規則
        通常只需要在初始化或更改規則時呼叫一次

        Args:
            movements: `Movements` 實例
        """
        ...
    def goto(self, goal: Goal) -> None:
        """阻塞直到抵達目標或失敗
        **慎用**：在 JSPyBridge 下會阻塞當前執行緒；若放在事件 handler 裡會卡住 callback 執行緒，通常只建議在主程式使用
        """
        ...
    def stop(self) -> None:
        """取消當前尋路任務並停下移動"""
        ...
    def isMoving(self) -> bool:
        """機器人目前是否正在執行尋路移動"""
        ...
    def isMining(self) -> bool:
        """機器人是否正在為尋路挖方塊"""
        ...
    def isBuilding(self) -> bool:
        """機器人是否正在為尋路放置方塊"""
        ...
    def bestHarvestTool(self, block: Block) -> Item | None:
        """Args:
            block: 要挖的 `Block`

        Returns:
            物品欄中最適合挖此方塊的 `Item`，沒有合用的工具則回 `None`
        """
        ...


class PathfinderModule:
    """The npm module returned by `bot.load_plugin('mineflayer-pathfinder')`.

    Ref: node_modules/mineflayer-pathfinder/index.d.ts — top-level exports
    """
    pathfinder: Callable[..., None]
    goals: Goals
    Movements: type[Movements]


# --- Mineflayer type aliases ---
ChatLevel = Literal['enabled', 'commandsOnly', 'disabled']
ViewDistance = Literal['far'] | Literal['normal'] | Literal['short'] | Literal['tiny'] | float
MainHands = Literal['left', 'right']
LevelType = Literal['default', 'flat', 'largeBiomes', 'amplified', 'customized', 'buffet', 'default_1_1']
GameMode = Literal['survival', 'creative', 'adventure', 'spectator']
Dimension = Literal['the_nether', 'overworld', 'the_end']
Difficulty = Literal['peaceful', 'easy', 'normal', 'hard']
ControlState = Literal['forward', 'back', 'left', 'right', 'jump', 'sprint', 'sneak']
EquipmentDestination = Literal['hand', 'head', 'torso', 'legs', 'feet', 'off-hand']

# --- Mineflayer aux interfaces ---

class Player:
    """伺服器玩家名單中的一筆資料；由 `bot.players[username]` 取得"""
    uuid: str
    """玩家 UUID 字串"""
    username: str
    """玩家遊戲名稱"""
    displayName: ChatMessage
    """玩家的顯示名稱 `ChatMessage`"""
    gamemode: float
    """玩家的遊戲模式數字 ID"""
    ping: float
    """玩家延遲毫秒"""
    entity: Entity
    """玩家的 `Entity` 物件（若該玩家目前在視野內）；否則為 `None`"""
    skinData: object | None
    """玩家膚色貼圖資料 dict（含 `url` 和 `model`），可能為 `None`"""
    profileKeys: object | None

class ChatPattern:
    """Ref: mineflayer/index.d.ts — ChatPattern"""
    pattern: object
    type: str
    description: str

class SkinParts:
    """Ref: mineflayer/index.d.ts — SkinParts"""
    showCape: bool
    showJacket: bool
    showLeftSleeve: bool
    showRightSleeve: bool
    showLeftPants: bool
    showRightPants: bool
    showHat: bool

class GameSettings:
    """Ref: mineflayer/index.d.ts — GameSettings"""
    chat: ChatLevel
    colorsEnabled: bool
    viewDistance: ViewDistance
    difficulty: float
    skinParts: SkinParts
    mainHand: MainHands

class GameState:
    """Ref: mineflayer/index.d.ts — GameState"""
    levelType: LevelType
    gameMode: GameMode
    hardcore: bool
    dimension: Dimension
    difficulty: Difficulty
    maxPlayers: float
    serverBrand: str

class Experience:
    """Ref: mineflayer/index.d.ts — Experience"""
    level: float
    points: float
    progress: float

class PhysicsOptions:
    """Ref: mineflayer/index.d.ts — PhysicsOptions"""
    maxGroundSpeed: float
    terminalVelocity: float
    walkingAcceleration: float
    gravity: float
    groundFriction: float
    playerApothem: float
    playerHeight: float
    jumpSpeed: float
    yawSpeed: float
    pitchSpeed: float
    sprintSpeed: float
    maxGroundSpeedSoulSand: float
    maxGroundSpeedWater: float

class Time:
    """Ref: mineflayer/index.d.ts — Time"""
    doDaylightCycle: bool
    bigTime: int
    time: float
    timeOfDay: float
    day: float
    isDay: bool
    moonPhase: float
    bigAge: int
    age: float

class ControlStateStatus:
    """Ref: mineflayer/index.d.ts — ControlStateStatus"""
    forward: bool
    back: bool
    left: bool
    right: bool
    jump: bool
    sprint: bool
    sneak: bool

class Instrument:
    """Ref: mineflayer/index.d.ts — Instrument"""
    id: float
    name: Literal['harp', 'doubleBass', 'snareDrum', 'sticks', 'bassDrum']

class FindBlockOptions:
    """Ref: mineflayer/index.d.ts — FindBlockOptions"""
    point: Vec3 | None
    matching: float | list[float] | Callable[[object], object]
    maxDistance: float | None
    count: float | None
    useExtraInfo: bool | Callable[[object], object] | None

class TransferOptions:
    """Ref: mineflayer/index.d.ts — TransferOptions"""
    window: Window
    itemType: float
    metadata: float | None
    count: float | None
    sourceStart: float
    sourceEnd: float
    destStart: float
    destEnd: float

class creativeMethods:
    """Ref: mineflayer/index.d.ts — creativeMethods"""
    setInventorySlot: Callable[[float, Item | None], None]
    clearSlot: Callable[[float], None]
    clearInventory: Callable[[], None]
    flyTo: Callable[[Vec3], None]
    startFlying: Callable[[], None]
    stopFlying: Callable[[], None]

class simpleClick:
    """Ref: mineflayer/index.d.ts — simpleClick"""
    leftMouse: Callable[[float], None]
    rightMouse: Callable[[float], None]

class Tablist:
    """Ref: mineflayer/index.d.ts — Tablist"""
    header: ChatMessage
    footer: ChatMessage

class chatPatternOptions:
    """Ref: mineflayer/index.d.ts — chatPatternOptions"""
    repeat: bool
    parse: bool

class CommandBlockOptions:
    """Ref: mineflayer/index.d.ts — CommandBlockOptions"""
    mode: float
    trackOutput: bool
    conditional: bool
    alwaysActive: bool

class VillagerTrade:
    """Ref: mineflayer/index.d.ts — VillagerTrade"""
    inputItem1: Item
    outputItem: Item
    inputItem2: Item | None
    hasItem2: bool
    tradeDisabled: bool
    nbTradeUses: float
    maximumNbTradeUses: float
    xp: float | None
    specialPrice: float | None
    priceMultiplier: float | None
    demand: float | None
    realPrice: float | None

class Enchantment:
    """Ref: mineflayer/index.d.ts — Enchantment"""
    level: float
    expected: object

# --- Mineflayer container classes ---

class Chest:
    """繼承 `Window`，`bot.openChest(...)` 的回傳型別"""
    def close(self) -> None:
        """關閉這個箱子
        等同 `bot.closeWindow(chest)`
        """
        ...
    def deposit(self, itemType: float, metadata: float | None, count: float | None) -> None:
        """從物品欄存入箱子

        Args:
            itemType: 物品 ID 整數
            metadata: 選擇特定 metadata，不關心傳 `None`
            count: 要存入的數量
        """
        ...
    def withdraw(self, itemType: float, metadata: float | None, count: float | None) -> None:
        """從箱子取出到物品欄"""
        ...

class Dispenser:
    """繼承 `Window`，發射器 / 投擲器
    方法與 `Chest` 幾乎相同
    """
    def close(self) -> None:
        """關閉這個發射器"""
        ...
    def deposit(self, itemType: float, metadata: float | None, count: float | None) -> None:
        """從物品欄存入發射器"""
        ...
    def withdraw(self, itemType: float, metadata: float | None, count: float | None) -> None:
        """從發射器取出"""
        ...

class Furnace:
    """繼承 `Window`，`bot.openFurnace(...)` 回傳型別"""
    fuel: float
    """目前燃料進度"""
    progress: float
    """目前冶煉進度"""
    def close(self) -> None:
        """關閉熔爐"""
        ...
    def takeInput(self) -> Item:
        """取出輸入槽的物品"""
        ...
    def takeFuel(self) -> Item:
        """取出燃料槽的物品"""
        ...
    def takeOutput(self) -> Item:
        """取出輸出槽的物品"""
        ...
    def putInput(self, itemType: float, metadata: float | None, count: float) -> None:
        """放入指定物品到輸入槽"""
        ...
    def putFuel(self, itemType: float, metadata: float | None, count: float) -> None:
        """放入指定燃料到燃料槽"""
        ...
    def inputItem(self) -> Item:
        """Returns:
            輸入槽目前的 `Item`
        """
        ...
    def fuelItem(self) -> Item:
        """Returns:
            燃料槽目前的 `Item`
        """
        ...
    def outputItem(self) -> Item:
        """Returns:
            輸出槽目前的 `Item`
        """
        ...

class EnchantmentTable:
    """繼承 `Window`，附魔台"""
    enchantments: list[Enchantment]
    """目前顯示的三個附魔選項陣列，每個元素含 `level` 和 `expected`"""
    def close(self) -> None:
        """關閉附魔台"""
        ...
    def targetItem(self) -> Item:
        """Returns:
            目前放在附魔台上的 `Item`
        """
        ...
    def enchant(self, choice: str | float) -> Item:
        """選擇某個附魔選項進行附魔

        Args:
            choice: 選項編號 `0` / `1` / `2`，或對應的字串名稱
        """
        ...
    def takeTargetItem(self) -> Item:
        """把附魔好的物品拿出來"""
        ...
    def putTargetItem(self, item: Item) -> Item:
        """把要附魔的物品放進附魔台"""
        ...
    def putLapis(self, item: Item) -> Item:
        """放青金石進去"""
        ...

class Anvil:
    """鐵砧視窗"""
    def combine(self, itemOne: Item, itemTwo: Item, name: str | None = ...) -> None:
        """把兩個物品在鐵砧上合併（修復 / 附魔合併），可順便改名

        Args:
            itemOne: 左槽物品
            itemTwo: 右槽物品
            name: (選填) 新名稱字串
        """
        ...
    def rename(self, item: Item, name: str | None = ...) -> None:
        """重新命名一個物品

        Args:
            item: 要改名的物品
            name: 新名稱
        """
        ...

class Villager:
    """繼承 `Window`，村民交易面板"""
    trades: list[VillagerTrade]
    """村民目前的交易選項陣列，每筆是 `VillagerTrade`"""
    def close(self) -> None:
        """關閉交易面板"""
        ...

# --- Event callback type aliases ---
_OnEvent_chat = Callable[[str, str, str | None, ChatMessage, list[str] | None], None]
_OnEvent_whisper = Callable[[str, str, str | None, ChatMessage, list[str] | None], None]
_OnEvent_actionBar = Callable[[ChatMessage], None]
_OnEvent_error = Callable[[Exception], None]
_OnEvent_message = Callable[[ChatMessage, str], None]
_OnEvent_messagestr = Callable[[str, str, ChatMessage], None]
_OnEvent_unmatchedMessage = Callable[[str, ChatMessage], None]
_OnEvent_inject_allowed = Callable[[], None]
_OnEvent_login = Callable[[], None]
_OnEvent_spawn = Callable[[], None]
_OnEvent_respawn = Callable[[], None]
_OnEvent_game = Callable[[], None]
_OnEvent_title = Callable[[str, Literal["subtitle", "title"]], None]
_OnEvent_rain = Callable[[], None]
_OnEvent_time = Callable[[], None]
_OnEvent_kicked = Callable[[str, bool], None]
_OnEvent_end = Callable[[str], None]
_OnEvent_spawnReset = Callable[[], None]
_OnEvent_death = Callable[[], None]
_OnEvent_health = Callable[[], None]
_OnEvent_breath = Callable[[], None]
_OnEvent_entitySwingArm = Callable[[Entity], None]
_OnEvent_entityHurt = Callable[[Entity, Entity], None]
_OnEvent_entityDead = Callable[[Entity], None]
_OnEvent_entityTaming = Callable[[Entity], None]
_OnEvent_entityTamed = Callable[[Entity], None]
_OnEvent_entityShakingOffWater = Callable[[Entity], None]
_OnEvent_entityEatingGrass = Callable[[Entity], None]
_OnEvent_entityHandSwap = Callable[[Entity], None]
_OnEvent_entityWake = Callable[[Entity], None]
_OnEvent_entityEat = Callable[[Entity], None]
_OnEvent_entityCriticalEffect = Callable[[Entity], None]
_OnEvent_entityMagicCriticalEffect = Callable[[Entity], None]
_OnEvent_entityCrouch = Callable[[Entity], None]
_OnEvent_entityUncrouch = Callable[[Entity], None]
_OnEvent_entityEquip = Callable[[Entity], None]
_OnEvent_entitySleep = Callable[[Entity], None]
_OnEvent_entitySpawn = Callable[[Entity], None]
_OnEvent_entityElytraFlew = Callable[[Entity], None]
_OnEvent_usedFirework = Callable[[], None]
_OnEvent_itemDrop = Callable[[Entity], None]
_OnEvent_playerCollect = Callable[[Entity, Entity], None]
_OnEvent_entityAttributes = Callable[[Entity], None]
_OnEvent_entityGone = Callable[[Entity], None]
_OnEvent_entityMoved = Callable[[Entity], None]
_OnEvent_entityDetach = Callable[[Entity, Entity], None]
_OnEvent_entityAttach = Callable[[Entity, Entity], None]
_OnEvent_entityUpdate = Callable[[Entity], None]
_OnEvent_entityEffect = Callable[[Entity, Effect], None]
_OnEvent_entityEffectEnd = Callable[[Entity, Effect], None]
_OnEvent_playerJoined = Callable[[Player], None]
_OnEvent_playerUpdated = Callable[[Player], None]
_OnEvent_playerLeft = Callable[[Player], None]
_OnEvent_blockUpdate = Callable[[Block | None, Block], None]
_OnEvent_blockUpdate__x__y__z_ = Callable[[Block | None, Block | None], None]
_OnEvent_chunkColumnLoad = Callable[[Vec3], None]
_OnEvent_chunkColumnUnload = Callable[[Vec3], None]
_OnEvent_soundEffectHeard = Callable[[str, Vec3, float, float], None]
_OnEvent_hardcodedSoundEffectHeard = Callable[[float, float, Vec3, float, float], None]
_OnEvent_noteHeard = Callable[[Block, Instrument, float], None]
_OnEvent_pistonMove = Callable[[Block, float, float], None]
_OnEvent_chestLidMove = Callable[[Block, float, Block | None], None]
_OnEvent_blockBreakProgressObserved = Callable[[Block, float], None]
_OnEvent_blockBreakProgressEnd = Callable[[Block], None]
_OnEvent_diggingCompleted = Callable[[Block], None]
_OnEvent_diggingAborted = Callable[[Block], None]
_OnEvent_move = Callable[[Vec3], None]
_OnEvent_forcedMove = Callable[[], None]
_OnEvent_mount = Callable[[], None]
_OnEvent_dismount = Callable[[Entity], None]
_OnEvent_windowOpen = Callable[[Window], None]
_OnEvent_windowClose = Callable[[Window], None]
_OnEvent_sleep = Callable[[], None]
_OnEvent_wake = Callable[[], None]
_OnEvent_experience = Callable[[], None]
_OnEvent_physicsTick = Callable[[], None]
_OnEvent_physicTick = Callable[[], None]
_OnEvent_scoreboardCreated = Callable[[object], None]
_OnEvent_scoreboardDeleted = Callable[[object], None]
_OnEvent_scoreboardTitleChanged = Callable[[object], None]
_OnEvent_scoreUpdated = Callable[[object, float], None]
_OnEvent_scoreRemoved = Callable[[object, float], None]
_OnEvent_scoreboardPosition = Callable[[str, object], None]
_OnEvent_teamCreated = Callable[[object], None]
_OnEvent_teamRemoved = Callable[[object], None]
_OnEvent_teamUpdated = Callable[[object], None]
_OnEvent_teamMemberAdded = Callable[[object], None]
_OnEvent_teamMemberRemoved = Callable[[object], None]
_OnEvent_bossBarCreated = Callable[[object], None]
_OnEvent_bossBarDeleted = Callable[[object], None]
_OnEvent_bossBarUpdated = Callable[[object], None]
_OnEvent_resourcePack = Callable[[str, str | None, str | None], None]
_OnEvent_particle = Callable[[object], None]

class BotOptions(TypedDict, total=False):
    """Options accepted by `create_bot(**opts)`.

    Ref: mineflayer/index.d.ts — interface BotOptions
    """
    logErrors: bool
    hideErrors: bool
    loadInternalPlugins: bool
    plugins: dict[str, object]
    chat: ChatLevel
    colorsEnabled: bool
    viewDistance: ViewDistance
    mainHand: MainHands
    difficulty: float
    chatLengthLimit: float
    physicsEnabled: bool
    maxCatchupTicks: float
    client: object
    brand: str
    defaultChatPatterns: bool
    respawn: bool
    host: str
    port: float
    username: str
    password: str
    version: str
    auth: Literal['mojang', 'microsoft', 'offline']
    authServer: str
    sessionServer: str
    onMsaCode: Callable[[object], None]
    authTitle: str

class Bot:
    """操縱 Minecraft 機器人的核心物件
    由 `create_bot(...)` 建立，透過 `@bot.on(event)` 註冊事件處理器、呼叫 `bot.chat(...)` 等方法操作機器人

    機器人連線完成後會非同步地進入世界
    **請務必等 `spawn` 事件觸發後**，再呼叫跟位置 / 世界有關的 API；在此之前 `bot.entity` 等屬性尚未就緒
    """
    username: str
    """機器人登入伺服器用的遊戲名稱
    登入前可能還是 `None`
    """
    protocolVersion: str
    """伺服器協議版本數字；跨版本邏輯用的"""
    majorVersion: str
    """大版本字串"""
    version: str
    """伺服器協議對應的 Minecraft 版本字串"""
    entity: Entity
    """機器人自身的 `Entity` 物件
    常用欄位：`position` / `velocity` / `yaw` / `pitch` / `onGround` / `height` 等
    """
    entities: dict[str, Entity]
    """所有機器人可見實體的對應表，key 是實體數字 ID、value 是 `Entity`
    含玩家、怪物、掉落物、箭、船等
    """
    fireworkRocketDuration: float
    """機器人使用煙火飛行時剩餘推進的 tick 數"""
    spawnPoint: Vec3
    """世界出生點 `Vec3` 座標"""
    game: GameState
    player: Player
    """機器人自己的 `Player` 物件（名單上的那一筆，含 `ping`、顯示名稱等），等同 `bot.players[bot.username]`"""
    players: dict[str, Player]
    """所有連線玩家的對應表，key 是玩家名稱、value 是 `Player`
    支援 `bot.players["alice"]` 查找，也支援 `for name in bot.players:` 迭代取得全部名稱

    ```python
    for name in bot.players:
        print(name, "延遲", bot.players[name].ping, "ms")
    ```
    """
    isRaining: bool
    """當前世界是否在下雨"""
    thunderState: float
    """目前雷雨強度（`0` ~ `1` 浮點）
    搭配 `bot.isRaining` 判斷天氣
    """
    chatPatterns: list[object]
    """目前註冊的 chat pattern 列表（含 regex、類型、描述）
    偵錯用
    """
    settings: object
    """遊戲設定物件
    含 `chat`（`"enabled"` / `"commandsOnly"` / `"disabled"`）、`colorsEnabled`、`viewDistance`、`difficulty`、`mainHand`、`skinParts` 等欄位
    """
    experience: Experience
    health: float
    """機器人目前血量，範圍 `[0, 20]`，每 1 代表半顆心"""
    food: float
    """機器人目前飽食度，範圍 `[0, 20]`，每 1 代表半支雞腿"""
    foodSaturation: float
    """飽食度的「隱藏緩衝」
    飽食度緩衝 > 0 時，`bot.food` 不會下降；吃東西同時會增加 `food` 和 `foodSaturation`
    """
    oxygenLevel: float
    """氧氣量，範圍 `[0, 20]`
    水中會持續扣減，歸零後開始扣血
    """
    physics: PhysicsOptions
    """物理參數字典：`gravity`、`terminalVelocity`、`walkingAcceleration`、`jumpSpeed`、`sprintSpeed`、`maxGroundSpeed` 等可調數值
    改寫會直接影響機器人運動；**後果自負**
    """
    physicsEnabled: bool
    """是否啟用物理模擬（布林）
    關掉後機器人不會自動落地、移動等，完全靠指令控制
    """
    time: Time
    quickBarSlot: float
    """快捷欄目前選取的槽位"""
    inventory: Window
    """機器人的物品欄 `Window` 物件
    用 `bot.inventory.items()` 取所有物品、`bot.inventory.findInventoryItem(...)` 搜尋特定物品
    """
    targetDigBlock: Block
    """目前正在挖的方塊 `Block`，沒有在挖時為 `None`"""
    isSleeping: bool
    """機器人目前是否躺在床上"""
    scoreboards: dict[str, object]
    """所有記分板 `{name: ScoreBoard}` 對應表"""
    scoreboard: dict[str, object]
    """按顯示槽位取得當前顯示的記分板 `{slot: ScoreBoard}`"""
    teams: dict[str, object]
    """所有隊伍 `{name: Team}` 對應表"""
    teamMap: dict[str, object]
    """以玩家名稱或實體名稱對應到所屬 `Team` 的快速查表"""
    controlState: ControlStateStatus
    creative: creativeMethods
    """創造模式輔助方法集合：`bot.creative.setInventorySlot`、`bot.creative.flyTo`、`bot.creative.startFlying` 等
    僅在伺服器給予 creative 權限時可用
    """
    world: object
    """世界資料物件（`prismarine-world` 的 `WorldSync`）
    多數情況不直接碰；用 `bot.blockAt` 等高階 API 即可
    """
    heldItem: Item | None
    """機器人目前手上拿的物品 `Item`，空手時為 `None`"""
    usingHeldItem: bool
    """機器人目前是否正在「使用」（長按右鍵）手上的物品"""
    currentWindow: Window | None
    """目前開啟的視窗（若有）
    沒開任何視窗時為 `None`
    """
    simpleClick: simpleClick
    """視窗點擊的簡單包裝
    通常只需要 `bot.simpleClick.leftMouse(slot)` 或 `bot.simpleClick.rightMouse(slot)`
    """
    tablist: Tablist
    """玩家名單（Tab 鍵那一塊）
    含 `header`（`ChatMessage`）與 `footer`
    """
    registry: object
    """mineflayer 持有的 `minecraft-data` registry
    用來反查方塊 / 物品 / 生物的 ID 與 metadata
    """
    connect: Callable[[BotOptions], None]
    """對已建立但尚未連線的 bot 做一次 reconnect
    一般腳本用不到——`create_bot(...)` 已自動連線

    Args:
        options: `BotOptions` dict
    """
    supportFeature: object
    """查詢當前連線的協定版本是否支援某個功能字串
    用於跨版本相容邏輯

    Args:
        feature: 功能名稱字串（對應 `minecraft-data` 的 feature 列表）
            - 回傳 `True` / `False`
    """
    end: Callable[[str | None], None]
    """主動關掉連線
    `bot.quit(...)` 是把協定層的 quit 送出再關；`bot.end(...)` 比較直接，伺服器可能看不到離線原因
    除非明白兩者差異，建議優先用 `bot.quit(...)`

    Args:
        reason: (選填) 原因字串
    """
    blockAt: Callable[[Vec3, bool | None], Block | None]
    """查詢世界中某個座標的方塊

    Args:
        point: 要查的 `Vec3`（整數座標）
        extraInfos: 預設 `True`，會多解析一些屬性（招牌文字、箱子內容等 metadata）；設 `False` 可以省一點效能

    Returns:
        `Block` 或 `None`（該區塊尚未載入時）
    """
    blockInSight: Callable[[float, float], Block | None]
    """沿機器人視線往前逐步推進，回傳第一個碰到的方塊；超過範圍或沒碰到就回 `None`

    Args:
        maxSteps: 最多走幾步取樣
        vectorLength: 每一步的向量長度
    """
    blockAtCursor: Callable[[float | None, Callable[..., object] | None], Block | None]
    """從機器人的視線方向投射，回傳視線末端所指的方塊
    `bot.blockInSight(...)` 的高階版本

    Args:
        maxDistance: 最遠測距（預設 `256`）
        matcher: 自訂篩選函式，接受 `Block` 回傳布林；預設收下所有方塊
    """
    blockAtEntityCursor: Callable[[Entity | None, float | None, Callable[..., object] | None], Block | None]
    """跟 `blockAtCursor` 類似，但從指定實體的視線出發
    常用來偵測別人正在看的方塊

    Args:
        entity: 觀察者 `Entity`，預設是機器人自己
        maxDistance: 最遠測距
        matcher: 篩選函式
    """
    canSeeBlock: Callable[[Block], bool]
    """檢查機器人目前是否能「看到」某方塊

    Args:
        block: 要檢查的 `Block`

    Returns:
        布林
    """
    findBlock: Callable[[FindBlockOptions], Block | None]
    """從附近尋找一個符合條件的方塊

    Args:
        options: 字典，至少需要 `matching`：
            - `matching`：方塊 ID 整數、ID 整數的陣列、或接受 `Block` 回傳布林的函式
            - `maxDistance`：(選填) 搜尋半徑，預設 16
            - `count`：(選填) 傳給 `findBlocks` 用，`findBlock` 通常不用設
            - `point`：(選填) 搜尋中心座標，預設為機器人當前位置

    Returns:
        第一個找到的 `Block`，沒找到回 `None`

    ```python
    diamond = bot.findBlock({"matching": 56, "maxDistance": 32})
    if diamond is not None:
        print("找到鑽石礦在", diamond.position)
    ```
    """
    findBlocks: Callable[[FindBlockOptions], list[Vec3]]
    """跟 `bot.findBlock` 同樣的參數結構，但會回傳**所有**符合的方塊 `Vec3` 座標的列表

    Args:
        options: 見 `bot.findBlock`；多加一個 `count` 限制回傳數量（預設 `1`）
    """
    canDigBlock: Callable[[Block], bool]
    """檢查當前手上的工具能不能挖動該方塊

    Args:
        block: 要檢查的 `Block`

    Returns:
        布林
    """
    recipesFor: Callable[[float, float | None, float | None, Block | bool | None], list[Recipe]]
    """查詢目前物品欄能合成指定物品的配方列表

    Args:
        itemType: 目標物品 ID 整數
        metadata: 目標的 metadata；不關心傳 `None`
        minResultCount: 最少要產出幾個才列入結果
        craftingTable: 傳 `Block` 代表用該工作台；`True` 代表允許 3x3 配方；`False` / `None` 代表只找玩家 2x2
    """
    recipesAll: Callable[[float, float | None, Block | bool | None], list[Recipe]]
    """同 `recipesFor`，但回傳**所有**可能的配方"""
    quit: Callable[[str | None], None]
    """送出協定層的斷線封包再關閉連線，`"end"` 事件會隨後觸發
    對伺服器比較友善

    Args:
        reason: 顯示在機器人自己 log 的字串；可省略
    """
    tabComplete: Callable[[str, bool | None, bool | None, float | None], list[str]]
    """請伺服器回傳聊天框 Tab 自動補全結果

    Args:
        str: 要補全的開頭字串
        assumeCommand: 是否當作指令補全（斜線後面的字串）
        sendBlockInSight: 是否附帶視線所指方塊（伺服器上下文提示用）
        timeout: 等待伺服器回覆的毫秒數
    """
    chat: Callable[[str], None]
    """在公開聊天中發送一則訊息

    Args:
        message: 要送出的內容字串；以 `/` 開頭會被當作指令送出。單則訊息超過伺服器長度限制時，會自動切成多則送出

    ```python
    bot.chat("大家好")
    bot.chat("/time set day")  # 以斜線開頭會被當作指令
    ```
    """
    whisper: Callable[[str, str], None]
    """對指定玩家傳送私聊訊息
    （相當於 `/tell`、`/msg`）

    Args:
        username: 目標玩家的遊戲名稱
        message: 訊息內容
    """
    chatAddPattern: Callable[[object, str, str | None], float]
    """新增一個 chat pattern，符合 pattern 的聊天訊息會以 `chatType` 指定的事件名觸
    **已停用**，請改用 `addChatPattern(name, pattern, options)`
    """
    setSettings: Callable[[object], None]
    """更新 `bot.settings`

    Args:
        options: `GameSettings` 的部分欄位 dict
    """
    loadPlugin: Callable[[Callable[..., object]], None]
    """`bot.load_plugin(...)` 的原生版本：直接接收 mineflayer 風格的 `(bot, options) => void` 函式
    **學生請改用 `bot.load_plugin(name)`**，這個是給進階使用者／minethon 內部用的

    Args:
        plugin: 插件 installer 函式
    """
    loadPlugins: Callable[[list[Callable[..., object]]], None]
    """`bot.load_plugin(...)` 的原生版本：直接接收 mineflayer 風格的 `(bot, options) => void` 函式
    **學生請改用 `bot.load_plugin(name)`**，這個是給進階使用者／minethon 內部用的

    Args:
        plugins: 插件 installer 函式的陣列
    """
    hasPlugin: Callable[[Callable[..., object]], bool]
    """查詢某個 installer 函式是否已載入

    Returns:
        布林
    """
    sleep: Callable[[Block], None]
    """讓機器人躺上床睡覺
    **只在夜晚或雷雨時有效**，白天呼叫會出錯

    Args:
        bedBlock: 目標床（`Block`）
    """
    isABed: Callable[[Block], bool]
    """判斷指定方塊是不是床

    Args:
        bedBlock: 要檢查的 `Block`
            - 回傳布林
    """
    wake: Callable[[], None]
    """從床上起床
    一般白天會自動醒，這個方法是強制提前起
    """
    elytraFly: Callable[[], None]
    """張開鞘翅開始滑翔
    要已站在空中且穿著鞘翅
    """
    setControlState: Callable[[ControlState, bool], None]
    """按下或放開一個移動鍵，效果會**一直持續**直到下次設定變更
    搭配事件使用，在想停下的時機再把狀態設回 `False`

    Args:
        control: `"forward"` / `"back"` / `"left"` / `"right"` / `"jump"` / `"sprint"` / `"sneak"` 其中之一
        state: `True` 按下、`False` 放開

    範例：進入世界後一直往前走，收到 `"stop"` 訊息才停下

    ```python
    @bot.on("spawn")
    def on_spawn():
        bot.setControlState("forward", True)

    @bot.on("chat")
    def on_chat(username, message, *_):
        if message == "stop":
            bot.setControlState("forward", False)
    ```
    """
    getControlState: Callable[[ControlState], bool]
    """讀取當前某個移動按鍵的按住狀態

    Args:
        control: 同 `setControlState` 的按鍵名

    Returns:
        布林
    """
    clearControlStates: Callable[[], None]
    """一次放開所有移動鍵，回到靜止狀態
    出事時「全部停下」的緊急按鈕
    """
    getExplosionDamages: Callable[[Entity, Vec3, float, bool | None], float | None]
    """計算如果在 `position` 發生爆炸，指定實體會吃到多少傷害

    Args:
        targetEntity: 受害 `Entity`
        position: 爆炸中心 `Vec3`
        radius: 爆炸半徑
        rawDamages: `True` 回傳原始傷害；`False`（預設）回傳考慮護甲後的實際傷害

    Returns:
        浮點數或 `None`
    """
    lookAt: Callable[[Vec3, bool | None], None]
    """讓機器人轉頭看向世界座標中的某個點

    Args:
        point: 目標 `Vec3`（世界絕對座標）。看玩家臉的話常傳 `target.position.offset(0, target.height, 0)`
        force: 是否強制瞬間轉向；預設 `False` 會以物理角速度平滑轉動，設 `True` 立即到位（比較適合自動化場景）
    """
    look: Callable[[float, float, bool | None], None]
    """直接設定機器人的視角角度

    Args:
        yaw: 水平角度
        pitch: 俯仰角度
        force: `True` 瞬間到位；`False`（預設）平滑轉動
    """
    updateSign: Callable[[Block, str, bool | None], None]
    """改寫一個招牌的文字內容

    Args:
        block: 招牌 `Block`
        text: 新文字（可用 `\n` 分行）
        back: `True` 寫到背面（1.20+）；預設寫正面
    """
    equip: Callable[[Item | float, EquipmentDestination | None], None]
    """把某個物品裝備到指定裝備槽

    Args:
        item: 要裝備的 `Item`，或它的數字 ID
        destination: `"hand"` / `"head"` / `"torso"` / `"legs"` / `"feet"` / `"off-hand"`；傳 `None` 代表用預設對應
    """
    unequip: Callable[[EquipmentDestination | None], None]
    """卸下指定裝備槽的裝備

    Args:
        destination: `"hand"` / `"head"` / `"torso"` / `"legs"` / `"feet"` / `"off-hand"`，或 `None` 用預設
    """
    tossStack: Callable[[Item], None]
    """整疊丟出某個物品

    Args:
        item: 物品欄中的 `Item`
    """
    toss: Callable[[float, float | None, float | None], None]
    """丟出指定數量的物品

    Args:
        itemType: 物品 ID 整數
        metadata: 物品的 metadata 值，不關心就傳 `None`
        count: 要丟的數量
    """
    dig: Callable[[Callable[[Block, bool | Literal['ignore'] | None], object]], object]
    """對指定方塊進行挖掘
    完成或失敗會透過 `"diggingCompleted"` / `"diggingAborted"` 事件回報
    **handler 內呼叫會阻塞**當下的 callback thread，建議在主執行流程呼叫

    Args:
        block: 目標 `Block` 物件（用 `bot.blockAt(pos)` 或 `bot.findBlock(...)` 取得）
        forceLook: `True` / `False` / `"ignore"`；`"ignore"` 代表完全不轉頭，直接挖（通常是呼叫者已自己對準過）
        digFace: `"auto"`（預設）、`"raycast"`，或傳一個 `Vec3` 指定從哪個方向打。多數情況留預設即可
    """
    stopDigging: Callable[[], None]
    """停止當前挖掘動作
    會觸發 `"diggingAborted"` 事件
    """
    digTime: Callable[[Block], float]
    """估算挖完指定方塊需要的毫秒數

    Args:
        block: 目標 `Block`
            - 回傳毫秒整數
    """
    placeBlock: Callable[[Block, Vec3], None]
    """對著 `referenceBlock` 的某一面放下一個方塊
    （放的是目前手上的物品）

    Args:
        referenceBlock: 當作「貼著」的現存方塊
        faceVector: 單位向量，指出要貼在哪一面（例如 `Vec3(0, 1, 0)` 是貼在上表面）
    """
    placeEntity: Callable[[Block, Vec3], Entity]
    """同 `placeBlock`，但放置的是實體（例如終界箱蓋、盔甲架、船），回傳放出的 `Entity`"""
    activateBlock: Callable[[Block, Vec3 | None, Vec3 | None], None]
    """對方塊「使用」（右鍵點擊），例如拉桿、按鈕、打開門

    Args:
        block: 目標 `Block`
        direction: 點擊的面向量；省略會自動判斷
        cursorPos: 精細的點擊位置；一般省略即可
    """
    activateEntity: Callable[[Entity], None]
    """對實體「使用」（右鍵）——例如騎馬、交易、上色羊

    Args:
        entity: 目標 `Entity`
    """
    activateEntityAt: Callable[[Entity, Vec3], None]
    """同 `activateEntity`，但指定精細的點擊位置

    Args:
        entity: 目標 `Entity`
        position: 點擊座標 `Vec3`
    """
    consume: Callable[[], None]
    """吃掉當前手持的食物或喝掉藥水
    等同於長按右鍵直到完成
    """
    fish: Callable[[], None]
    """執行釣魚動作：在手持釣竿時拋出、等魚上鉤、收竿
    整個流程用一次呼叫完成，過程中若要中斷請呼叫 `bot.activateItem()` 收竿或直接換槽
    """
    activateItem: Callable[[bool | None], None]
    """使用目前手上的物品（相當於按右鍵）——吃東西、拉弓、擋盾、喝藥水都用這個
    要「停下」請呼叫 `bot.deactivateItem()`

    Args:
        offhand: `True` 使用副手物品；預設 `False` 用主手
    """
    deactivateItem: Callable[[], None]
    """停止「持續使用」的物品動作
    （停止拉弓、放下盾等等）
    """
    useOn: Callable[[Entity], None]
    """對實體使用手上物品

    Args:
        targetEntity: 目標 `Entity`
    """
    attack: Callable[[Entity], None]
    """對指定實體進行一次近戰攻擊

    Args:
        entity: 目標 `Entity`
    """
    swingArm: Callable[[Literal['left'] | Literal['right'] | None, bool | None], None]
    """播放揮手動畫

    Args:
        hand: `"left"` / `"right"` 或省略（預設主手）
        showHand: `True` 實際播動畫；`False` 靜默
    """
    mount: Callable[[Entity], None]
    """騎上指定載具

    Args:
        entity: 載具 `Entity`（馬、船、礦車等）
    """
    dismount: Callable[[], None]
    """下目前所騎載具"""
    moveVehicle: Callable[[float, float], None]
    """控制目前所騎載具的移動

    Args:
        left: 左右方向（`-1` ~ `1`）
        forward: 前後方向（`-1` ~ `1`）
    """
    setQuickBarSlot: Callable[[float], None]
    """切換快捷欄槽位

    Args:
        slot: `0` 到 `8` 的整數
    """
    craft: Callable[[Recipe, float | None, Block | None], None]
    """用指定配方合成物品
    要有對應材料

    Args:
        recipe: 從 `bot.recipesFor(...)` 取得的 `Recipe`
        count: 要合成幾次（每次產出 recipe 定義的量），省略為 1
        craftingTable: 若是 3x3 配方，指定要使用的工作台 `Block`
    """
    writeBook: Callable[[float, list[str]], None]
    """把一本「未寫字的書」（write book）寫滿內容

    Args:
        slot: 物品欄中空白書所在的槽位整數
        pages: 每一頁的文字字串陣列
    """
    openContainer: Callable[[Block | Entity, Vec3 | None, Vec3 | None], Chest | Dispenser]
    """打開任意容器方塊或實體

    Args:
        chest: 目標 `Block` 或 `Entity`
        direction: 點擊的面；通常不需指定
        cursorPos: 精細點擊座標
    """
    openChest: Callable[[Block | Entity, float | None, Vec3 | None], Chest]
    """打開箱子，回傳 `Chest` 物件"""
    openFurnace: Callable[[Block], Furnace]
    """打開熔爐，回傳 `Furnace`"""
    openDispenser: Callable[[Block], Dispenser]
    """打開發射器或投擲器，回傳 `Dispenser`"""
    openEnchantmentTable: Callable[[Block], EnchantmentTable]
    """打開附魔台，回傳 `EnchantmentTable`"""
    openAnvil: Callable[[Block], Anvil]
    """打開鐵砧，回傳 `Anvil`"""
    openVillager: Callable[[Entity], Villager]
    """與村民互動打開交易面板，回傳 `Villager`

    Args:
        villager: 村民 `Entity`
    """
    trade: Callable[[Villager, str | float, float | None], None]
    """跟村民完成一筆交易

    Args:
        villagerInstance: `bot.openVillager` 回傳的 `Villager`
        tradeIndex: 交易列表中的第幾筆（0-based，可用字串名稱或整數）
        times: 要交易幾次，省略為 1
    """
    setCommandBlock: Callable[[Vec3, str, CommandBlockOptions], None]
    """修改指令方塊內容

    Args:
        pos: 指令方塊座標 `Vec3`
        command: 要寫入的指令字串（不需要開頭 `/`）
        options: `{mode, trackOutput, conditional, alwaysActive}` 設定字典
    """
    clickWindow: Callable[[float, float, float], None]
    """低階視窗點擊——直接模擬滑鼠事件
    一般請用更高階的 `bot.equip` / `bot.toss` 等

    Args:
        slot: 槽位整數
        mouseButton: `0` 左鍵、`1` 右鍵
        mode: 點擊模式 `0` ~ `6`（協定層定義）
    """
    putSelectedItemRange: Callable[[float, float, Window, object], None]
    """把當前游標上的物品塞進某視窗指定槽位範圍"""
    putAway: Callable[[float], None]
    """把視窗裡 `slot` 的物品收回到物品欄"""
    closeWindow: Callable[[Window], None]
    """關掉指定視窗

    Args:
        window: 由 `openX` 方法取得的 `Window`
    """
    transfer: Callable[[TransferOptions], None]
    """在視窗內移動物品

    Args:
        options: 含 `window`、`itemType`、`metadata`、`count`、`sourceStart` / `sourceEnd`、`destStart` / `destEnd` 的 dict
    """
    openBlock: Callable[[Block, Vec3 | None, Vec3 | None], Window]
    """開啟任意有視窗的方塊；實際回傳型別依方塊而定"""
    openEntity: Callable[[Entity, object], Window]
    """使用指定 Class 構造視窗，用在自訂實體或非標準 Interactive Entity
    進階用法
    """
    moveSlotItem: Callable[[float, float], None]
    """在物品欄裡把某槽物品移到另一槽"""
    updateHeldItem: Callable[[], None]
    """立即將「目前快捷欄選中」的變更同步到伺服器
    多數情況不用手動呼叫
    """
    getEquipmentDestSlot: Callable[[str], float]
    """查詢裝備類型對應的槽位編號

    Args:
        destination: `"hand"` / `"head"` / `"torso"` / `"legs"` / `"feet"` / `"off-hand"`
            - 回傳整數槽位
    """
    waitForChunksToLoad: Callable[[], None]
    """阻塞等周遭的區塊全部載入完成再繼續
    `spawn` 事件後呼叫可確保 `bot.blockAt` 之類都有結果
    """
    entityAtCursor: Callable[[float | None], Entity | None]
    """從機器人視線方向投射，回傳第一個碰到的實體
    沒找到則回傳 `None`

    Args:
        maxDistance: 最遠測距，預設 `3`
    """
    nearestEntity: Callable[[Callable[[Entity], bool] | None], Entity | None]
    """找出最近的一個實體，可自訂篩選函式
    沒找到則回傳 `None`

    Args:
        filter: (選填) 接受 `Entity` 回傳布林的函式
    """
    waitForTicks: Callable[[float], None]
    """等指定 tick 數（每 tick 約 50ms）
    阻塞式：會卡住呼叫它的執行緒，**handler 內不要用**

    Args:
        ticks: 要等的 tick 數整數
    """
    addChatPattern: Callable[[str, object, chatPatternOptions | None], float]
    """註冊一個 chat pattern，讓特定格式的聊天訊息觸發自訂事件

    Args:
        name: 事件名稱（會觸發 `f"chat:{name}"` 事件）
        pattern: 正則表達式物件（使用 JavaScript 的 `RegExp`）
        options: (選填) `{repeat: bool, parse: bool}`。`parse=True` 時會把 regex 捕獲組傳進事件；`repeat=True` 表示事件可多次觸發事件
    """
    addChatPatternSet: Callable[[str, list[object], chatPatternOptions | None], float]
    """同 `addChatPattern`，但傳入多個 pattern 當一組（全部順序比中才觸發）
    適合跨行訊息
    """
    removeChatPattern: Callable[[str | float], None]
    """移除之前註冊的 chat pattern

    Args:
        name: pattern 名稱，或 `addChatPattern` 回傳的整數 ID
    """
    awaitMessage: Callable[[list[str] | list[object]], str]
    """阻塞等待第一則符合任一 pattern 的聊天訊息

    Args:
        *patterns: 一到多個字串或 `RegExp`

    Returns:
        符合的字串
    """
    acceptResourcePack: Callable[[], None]
    """同意伺服器的資源包請求"""
    denyResourcePack: Callable[[], None]
    """拒絕伺服器的資源包請求"""
    respawn: Callable[[], None]
    """死後手動重生"""

    # --- Typed event overloads (generated from BotEvents) ---
    @overload
    def on(self, event: Literal["chat"]) -> Callable[[_OnEvent_chat], _OnEvent_chat]:
        """頻道上有公開聊天訊息時觸發事件
        **自己發的訊息也會觸發**，需自行以 `username == bot.username` 比對忽略

        Args:
            username: 發話者的遊戲名稱
            message: 已去除顏色碼與控制字元的純文字
            translate: 聊天類型字串（例如 `chat.type.text`）；多數 Bukkit 系伺服器會是 `None`
            jsonMsg: 伺服器原始的 JSON 訊息物件，保留顏色、點擊事件等 metadata
            matches: 若有自訂 chat pattern 且比中時，是捕獲的字串陣列；否則為 `None`

        See Also:
            `"whisper"`

        ```python
        @bot.on("chat")
        def on_chat(username, message, *_):
            if username == bot.username:
                return
            if message == "hi":
                bot.chat("哈囉")
        ```
        """
        ...
    @overload
    def on(self, event: Literal["whisper"]) -> Callable[[_OnEvent_whisper], _OnEvent_whisper]:
        """有玩家對你私聊（`/tell`、`/msg` 指令）時觸發事件

        Args:
            username: 發話者的遊戲名稱
            message: 已去除顏色碼與控制字元的純文字
            translate: 聊天類型字串（例如 `chat.type.text`）；多數 Bukkit 系伺服器會是 `None`
            jsonMsg: 伺服器原始的 JSON 訊息物件，保留顏色、點擊事件等 metadata
            matches: 若有自訂 chat pattern 且比中時，是捕獲的字串陣列；否則為 `None`

        See Also:
            `"chat"`
        """
        ...
    @overload
    def on(self, event: Literal["actionBar"]) -> Callable[[_OnEvent_actionBar], _OnEvent_actionBar]:
        """伺服器在動作列推送訊息時觸發事件
        （血條上方的懸浮文字）

        Args:
            jsonMsg: 伺服器原始的 JSON 訊息物件
        """
        ...
    @overload
    def on(self, event: Literal["error"]) -> Callable[[_OnEvent_error], _OnEvent_error]:
        """機器人遇到不致命的例外（例如解析封包失敗）時觸發事件
        把這個事件印出來有助於 debug

        Args:
            err: `Error` 物件
        """
        ...
    @overload
    def on(self, event: Literal["message"]) -> Callable[[_OnEvent_message], _OnEvent_message]:
        """**任何**文字訊息抵達時觸發事件
        公開聊天、私聊、系統訊息、指令輸出都涵蓋
        用來記錄所有進入機器人的文字

        Args:
            jsonMsg: 伺服器原始的 JSON 訊息物件
            position: 訊息來源位置字串：`"chat"`（一般聊天）、`"system"`（系統訊息）、`"game_info"`（動作列）
        """
        ...
    @overload
    def on(self, event: Literal["messagestr"]) -> Callable[[_OnEvent_messagestr], _OnEvent_messagestr]:
        """**任何**文字訊息抵達時觸發事件
        公開聊天、私聊、系統訊息、指令輸出都涵蓋
        用來記錄所有進入機器人的文字
        同 `"message"` 但把內容用 `toString()` 攤平成純字串，方便直接印

        Args:
            message: 已攤平的字串訊息
            position: 訊息來源位置字串：`"chat"`（一般聊天）、`"system"`（系統訊息）、`"game_info"`（動作列）
            jsonMsg: 伺服器原始的 JSON 訊息物件
        """
        ...
    @overload
    def on(self, event: Literal["unmatchedMessage"]) -> Callable[[_OnEvent_unmatchedMessage], _OnEvent_unmatchedMessage]:
        """系統訊息沒有對應到任何已註冊的 chat pattern 時觸發事件
        一般玩家很少用到，多半是開發自訂 pattern 時才會監聽

        Args:
            stringMsg: 原始純文字訊息
            jsonMsg: 原始 JSON 訊息物件
        """
        ...
    @overload
    def on(self, event: Literal["inject_allowed"]) -> Callable[[_OnEvent_inject_allowed], _OnEvent_inject_allowed]:
        """mineflayer 載入 `minecraft-data` 並允許插件 inject 時觸發事件（無參數）
        這是**插件開發**的 hook，一般腳本不需要監聽；建議還是等 `"spawn"` 事件觸發後再動作
        """
        ...
    @overload
    def on(self, event: Literal["login"]) -> Callable[[_OnEvent_login], _OnEvent_login]:
        """成功登入伺服器但**尚未進入世界**時觸發事件（無參數）
        此時世界尚未載入，請勿呼叫位置相關的 API，要等待 `"spawn"` 事件觸發後才可以呼叫
        此事件通常只拿來印 log 或做連線成功的標記
        """
        ...
    @overload
    def on(self, event: Literal["spawn"]) -> Callable[[_OnEvent_spawn], _OnEvent_spawn]:
        """機器人在世界中生成（或重新生成）後觸發事件（無參數）
        這是可以真正開始移動的時機

        可查詢 `bot.entity.position`、發聊天訊息、載入插件等都應該在這個事件**之後**進行

        死亡重生、跨維度傳送也會再次觸發事件
        """
        ...
    @overload
    def on(self, event: Literal["respawn"]) -> Callable[[_OnEvent_respawn], _OnEvent_respawn]:
        """機器人重生進入世界時觸發事件（無參數）
        （`"death"` 後會先觸發此事件，接著才是 `"spawn"`）
        """
        ...
    @overload
    def on(self, event: Literal["game"]) -> Callable[[_OnEvent_game], _OnEvent_game]:
        """遊戲模式、維度、難度等 `bot.game` 欄位有變更時觸發事件（無參數）
        要讀新值請直接看 `bot.game.*`
        """
        ...
    @overload
    def on(self, event: Literal["title"]) -> Callable[[_OnEvent_title], _OnEvent_title]:
        """伺服器推送大型標題或副標題時觸發事件

        Args:
            text: 標題文字
            type: `"title"` 或 `"subtitle"`
        """
        ...
    @overload
    def on(self, event: Literal["rain"]) -> Callable[[_OnEvent_rain], _OnEvent_rain]:
        """天氣開始下雨或停雨時觸發事件（無參數）
        要判斷現在狀態請讀 `bot.isRaining`
        """
        ...
    @overload
    def on(self, event: Literal["time"]) -> Callable[[_OnEvent_time], _OnEvent_time]:
        """世界時間有更新時觸發事件（無參數）
        伺服器定時同步、或 `/time set` 指令
        由於幾乎每個 tick 都會觸發，**不要在這裡做耗時工作**
        """
        ...
    @overload
    def on(self, event: Literal["kicked"]) -> Callable[[_OnEvent_kicked], _OnEvent_kicked]:
        """被伺服器踢出時觸發事件
        通常緊接著會觸發 `"end"` 事件

        Args:
            reason: 伺服器送出的踢出原因原始字串，由 mineflayer 原樣轉送未做解析；現代伺服器通常是 JSON 格式的 `ChatMessage`，要顯示給使用者時用 `ChatMessage.fromNotch(reason).toString()` 轉純文字
            loggedIn: `True` 代表已登入後才被踢、`False` 代表握手階段就被拒絕
        """
        ...
    @overload
    def on(self, event: Literal["end"]) -> Callable[[_OnEvent_end], _OnEvent_end]:
        """連線斷開時觸發事件
        正常離線、被踢、網路中斷都會觸發事件
        這也是 `bot.run_forever()` 結束阻塞並讓 script 退出的訊號

        Args:
            reason: 斷線原因
        """
        ...
    @overload
    def on(self, event: Literal["spawnReset"]) -> Callable[[_OnEvent_spawnReset], _OnEvent_spawnReset]:
        """床被破壞 / 重生點重置時觸發事件（無參數）
        例如睡覺用的床被人敲掉
        """
        ...
    @overload
    def on(self, event: Literal["death"]) -> Callable[[_OnEvent_death], _OnEvent_death]:
        """機器人死亡時觸發事件（無參數）
        mineflayer 會自動重生，稍後會再次觸發 `"spawn"` 事件
        """
        ...
    @overload
    def on(self, event: Literal["health"]) -> Callable[[_OnEvent_health], _OnEvent_health]:
        """血量或飽食度有變動時觸發事件（無參數）
        要讀取新值請直接看 `bot.health` / `bot.food`
        """
        ...
    @overload
    def on(self, event: Literal["breath"]) -> Callable[[_OnEvent_breath], _OnEvent_breath]:
        """氧氣量有變動時觸發（無參數）
        要讀新值請看 `bot.oxygenLevel`
        """
        ...
    @overload
    def on(self, event: Literal["entitySwingArm"]) -> Callable[[_OnEvent_entitySwingArm], _OnEvent_entitySwingArm]:
        """實體揮手時觸發事件
        （近戰攻擊、採集動作）

        Args:
            entity: 揮手的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityHurt"]) -> Callable[[_OnEvent_entityHurt], _OnEvent_entityHurt]:
        """實體受傷時觸發事件

        Args:
            entity: 受傷的 `Entity`
            source: 傷害來源 `Entity`（可能是攻擊者或 `None`）
        """
        ...
    @overload
    def on(self, event: Literal["entityDead"]) -> Callable[[_OnEvent_entityDead], _OnEvent_entityDead]:
        """實體死亡時觸發事件

        Args:
            entity: 死亡的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityTaming"]) -> Callable[[_OnEvent_entityTaming], _OnEvent_entityTaming]:
        """玩家正在嘗試馴服動物時觸發事件
        （例如餵骨頭給狼）

        Args:
            entity: 被馴服中的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityTamed"]) -> Callable[[_OnEvent_entityTamed], _OnEvent_entityTamed]:
        """動物成功被馴服時觸發事件

        Args:
            entity: 被馴服的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityShakingOffWater"]) -> Callable[[_OnEvent_entityShakingOffWater], _OnEvent_entityShakingOffWater]:
        """動物抖水時觸發事件

        Args:
            entity: 抖水的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityEatingGrass"]) -> Callable[[_OnEvent_entityEatingGrass], _OnEvent_entityEatingGrass]:
        """羊在吃草時觸發事件

        Args:
            entity: 吃草的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityHandSwap"]) -> Callable[[_OnEvent_entityHandSwap], _OnEvent_entityHandSwap]:
        """實體左右手物品互換時觸發事件

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityWake"]) -> Callable[[_OnEvent_entityWake], _OnEvent_entityWake]:
        """實體從床上醒來時觸發事件

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityEat"]) -> Callable[[_OnEvent_entityEat], _OnEvent_entityEat]:
        """實體在吃東西時觸發事件
        伺服器每次送出吃東西動畫封包（`packet.animation` = 3）時觸發一次

        Args:
            entity: 吃東西的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityCriticalEffect"]) -> Callable[[_OnEvent_entityCriticalEffect], _OnEvent_entityCriticalEffect]:
        """實體被打出暴擊時觸發事件
        （有爆擊粒子效果）

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityMagicCriticalEffect"]) -> Callable[[_OnEvent_entityMagicCriticalEffect], _OnEvent_entityMagicCriticalEffect]:
        """附魔武器的特殊效果觸發時

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityCrouch"]) -> Callable[[_OnEvent_entityCrouch], _OnEvent_entityCrouch]:
        """實體開始蹲下時觸發事件
        （按下 shift）

        Args:
            entity: 潛行中的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityUncrouch"]) -> Callable[[_OnEvent_entityUncrouch], _OnEvent_entityUncrouch]:
        """實體結束蹲下時觸發事件

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityEquip"]) -> Callable[[_OnEvent_entityEquip], _OnEvent_entityEquip]:
        """實體換裝備或更換手持物品時觸發事件

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entitySleep"]) -> Callable[[_OnEvent_entitySleep], _OnEvent_entitySleep]:
        """實體上床睡覺時觸發事件

        Args:
            entity: 上床的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entitySpawn"]) -> Callable[[_OnEvent_entitySpawn], _OnEvent_entitySpawn]:
        """視野中有新實體出現時觸發事件
        若是玩家實體會另外觸發 `"playerJoined"`

        Args:
            entity: 新出現的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityElytraFlew"]) -> Callable[[_OnEvent_entityElytraFlew], _OnEvent_entityElytraFlew]:
        """實體張開鞘翅飛行時觸發事件

        Args:
            entity: 飛行中的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["usedFirework"]) -> Callable[[_OnEvent_usedFirework], _OnEvent_usedFirework]:
        """玩家使用煙火時觸發事件
        （通常用於鞘翅推進）

        Args:
            fireworkEntityId: 煙火實體的數字 ID
        """
        ...
    @overload
    def on(self, event: Literal["itemDrop"]) -> Callable[[_OnEvent_itemDrop], _OnEvent_itemDrop]:
        """實體丟出物品時觸發事件
        （例如死亡時掉落）

        Args:
            entity: 被掉出的物品 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["playerCollect"]) -> Callable[[_OnEvent_playerCollect], _OnEvent_playerCollect]:
        """玩家撿起掉落物或其他實體時觸發事件

        Args:
            collector: 撿拾的 `Entity`（通常是玩家）
            collected: 被撿拾的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityAttributes"]) -> Callable[[_OnEvent_entityAttributes], _OnEvent_entityAttributes]:
        """實體的屬性表變動時觸發事件
        （移動速度、最大血量等）

        Args:
            entity: 被更新的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityGone"]) -> Callable[[_OnEvent_entityGone], _OnEvent_entityGone]:
        """實體離開視野或被移除時觸發事件

        Args:
            entity: 消失的 `Entity`（讀取它的資料仍可，但不再更新）
        """
        ...
    @overload
    def on(self, event: Literal["entityMoved"]) -> Callable[[_OnEvent_entityMoved], _OnEvent_entityMoved]:
        """實體位置有變動時觸發事件
        **這是高頻事件**，每 tick 都可能觸發，請勿在此做耗時工作

        Args:
            entity: 移動中的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityDetach"]) -> Callable[[_OnEvent_entityDetach], _OnEvent_entityDetach]:
        """實體離開載具時觸發事件

        Args:
            entity: 乘員
            vehicle: 載具
        """
        ...
    @overload
    def on(self, event: Literal["entityAttach"]) -> Callable[[_OnEvent_entityAttach], _OnEvent_entityAttach]:
        """實體掛上載具時觸發事件
        （騎上馬、船等）

        Args:
            entity: 乘員 `Entity`
            vehicle: 載具 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityUpdate"]) -> Callable[[_OnEvent_entityUpdate], _OnEvent_entityUpdate]:
        """實體的 metadata（旁枝屬性，如染色、坐騎狀態等）變動時觸發事件

        Args:
            entity: 被更新的 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["entityEffect"]) -> Callable[[_OnEvent_entityEffect], _OnEvent_entityEffect]:
        """實體被套上狀態效果時觸發事件

        Args:
            entity: 對應 `Entity`
            effect: `Effect` 物件（含 `id`、`amplifier`、`duration`）
        """
        ...
    @overload
    def on(self, event: Literal["entityEffectEnd"]) -> Callable[[_OnEvent_entityEffectEnd], _OnEvent_entityEffectEnd]:
        """實體身上的狀態效果消失時觸發事件

        Args:
            entity: 對應 `Entity`
            effect: 剛結束的 `Effect`
        """
        ...
    @overload
    def on(self, event: Literal["playerJoined"]) -> Callable[[_OnEvent_playerJoined], _OnEvent_playerJoined]:
        """有玩家加入伺服器時觸發事件

        Args:
            player: 加入的 `Player` 物件（含 `.username`、`.uuid`、`.ping` 等）
        """
        ...
    @overload
    def on(self, event: Literal["playerUpdated"]) -> Callable[[_OnEvent_playerUpdated], _OnEvent_playerUpdated]:
        """玩家資訊更新時觸發事件
        **這是高頻事件**，每 tick 都可能觸發，請勿在此做耗時工作
        （延遲、顯示名稱、遊戲模式等）

        Args:
            player: 被更新的 `Player`
        """
        ...
    @overload
    def on(self, event: Literal["playerLeft"]) -> Callable[[_OnEvent_playerLeft], _OnEvent_playerLeft]:
        """有玩家離線時觸發事件

        Args:
            player: 離線的 `Player` 物件
        """
        ...
    @overload
    def on(self, event: Literal["blockUpdate"]) -> Callable[[_OnEvent_blockUpdate], _OnEvent_blockUpdate]:
        """**任何**方塊變動時觸發事件
        **這是高頻事件**，每 tick 都可能觸發，請勿在此做耗時工作

        Args:
            oldBlock: 變更前的 `Block`（可能為 `None`，如果原本是載入邊界）
            newBlock: 變更後的 `Block`
        """
        ...
    @overload
    def on(self, event: Literal["blockUpdate:(x, y, z)"]) -> Callable[[_OnEvent_blockUpdate__x__y__z_], _OnEvent_blockUpdate__x__y__z_]:
        """特定座標的方塊發生變化時觸發事件
        事件名裡的 `(x, y, z)` 要換成實際整數，例如 `"blockUpdate:(100,64,200)"`

        Args:
            oldBlock: 變更前 `Block`，可能為 `None`
            newBlock: 變更後 `Block`，可能為 `None`
        """
        ...
    @overload
    def on(self, event: Literal["chunkColumnLoad"]) -> Callable[[_OnEvent_chunkColumnLoad], _OnEvent_chunkColumnLoad]:
        """區塊柱載入到機器人視野時觸發事件

        Args:
            position: 區塊柱的角落座標 `Vec3`（只有 x、z 有意義）
        """
        ...
    @overload
    def on(self, event: Literal["chunkColumnUnload"]) -> Callable[[_OnEvent_chunkColumnUnload], _OnEvent_chunkColumnUnload]:
        """區塊柱卸載時觸發事件

        Args:
            position: 區塊柱角落座標
        """
        ...
    @overload
    def on(self, event: Literal["soundEffectHeard"]) -> Callable[[_OnEvent_soundEffectHeard], _OnEvent_soundEffectHeard]:
        """可識別的音效事件觸發時觸發事件

        Args:
            soundName: 音效名稱字串（例如 `"entity.creeper.primed"`）
            position: 音效發生位置 `Vec3`
            volume: 音量（浮點數）
            pitch: 音高（浮點數）
        """
        ...
    @overload
    def on(self, event: Literal["hardcodedSoundEffectHeard"]) -> Callable[[_OnEvent_hardcodedSoundEffectHeard], _OnEvent_hardcodedSoundEffectHeard]:
        """舊版硬編碼音效觸發時觸發事件
        多數情境下用 `"soundEffectHeard"` 就夠了

        Args:
            soundId: 音效的數字 ID
            soundCategory: 類別 ID
            position: 位置 `Vec3`
            volume: 音量
            pitch: 音高
        """
        ...
    @overload
    def on(self, event: Literal["noteHeard"]) -> Callable[[_OnEvent_noteHeard], _OnEvent_noteHeard]:
        """音符盒被擊發時觸發事件

        Args:
            block: 音符盒 `Block`
            instrument: 演奏的樂器（含 `id` 與 `name` 如 `"harp"`、`"bassDrum"`）
            pitch: 音高 `0` ~ `24`
        """
        ...
    @overload
    def on(self, event: Literal["pistonMove"]) -> Callable[[_OnEvent_pistonMove], _OnEvent_pistonMove]:
        """任何活塞推/拉動作發生時觸發事件

        Args:
            block: 活塞方塊
            isPulling: `1` 為拉、`0` 為推
            direction: 方向編號 `0` ~ `5`（下、上、北、南、西、東）
        """
        ...
    @overload
    def on(self, event: Literal["chestLidMove"]) -> Callable[[_OnEvent_chestLidMove], _OnEvent_chestLidMove]:
        """任何箱子被打開或關上時觸發事件
        （例如動畫狀態變化時）

        Args:
            block: 箱子方塊
            isOpen: `1` 為開啟動畫、`0` 為關閉動畫
            block2: 若為雙箱，另一半的方塊；單箱為 `None`
        """
        ...
    @overload
    def on(self, event: Literal["blockBreakProgressObserved"]) -> Callable[[_OnEvent_blockBreakProgressObserved], _OnEvent_blockBreakProgressObserved]:
        """看見附近有人在挖方塊時觸發（不是自己挖的）

        Args:
            block: 正在被挖的 `Block`
            destroyStage: 破壞進度 `0` ~ `9`；`9` 時接近挖斷
        """
        ...
    @overload
    def on(self, event: Literal["blockBreakProgressEnd"]) -> Callable[[_OnEvent_blockBreakProgressEnd], _OnEvent_blockBreakProgressEnd]:
        """挖掘動作結束時觸發（可能挖斷，也可能中途放棄）

        Args:
            block: 對應的 `Block`
        """
        ...
    @overload
    def on(self, event: Literal["diggingCompleted"]) -> Callable[[_OnEvent_diggingCompleted], _OnEvent_diggingCompleted]:
        """`bot.dig(block)` 成功挖掉方塊時觸發事件

        Args:
            block: 被挖掉的 `Block`（此時方塊類型多半已變成空氣，位置資訊仍可用）
        """
        ...
    @overload
    def on(self, event: Literal["diggingAborted"]) -> Callable[[_OnEvent_diggingAborted], _OnEvent_diggingAborted]:
        """`bot.dig(block)` 被中斷時觸發事件
        例如玩家移動離開太遠、或方塊被他人搶挖

        Args:
            block: 中途放棄的目標方塊
        """
        ...
    @overload
    def on(self, event: Literal["move"]) -> Callable[[_OnEvent_move], _OnEvent_move]:
        """機器人位置或視角改變時觸發事件
        **這是高頻事件**，每 tick 都可能觸發，請勿在此做耗時工作

        Args:
            position: 移動前的 `Vec3`（可以和 `bot.entity.position` 比較得知移動方向 / 距離）
        """
        ...
    @overload
    def on(self, event: Literal["forcedMove"]) -> Callable[[_OnEvent_forcedMove], _OnEvent_forcedMove]:
        """被伺服器強制傳送時觸發事件（無參數）
        （例如teleport、`/tp` 指令等）
        重要：此事件觸發後，機器人的當前位置會跟路徑規劃的預期不符，常需重新規劃路線
        """
        ...
    @overload
    def on(self, event: Literal["mount"]) -> Callable[[_OnEvent_mount], _OnEvent_mount]:
        """機器人騎上載具時觸發事件（無參數）
        （例如馬、船、礦車等）
        可讀 `bot.vehicle` 看載具
        """
        ...
    @overload
    def on(self, event: Literal["dismount"]) -> Callable[[_OnEvent_dismount], _OnEvent_dismount]:
        """機器人下載具時觸發事件

        Args:
            vehicle: 剛離開的載具 `Entity`
        """
        ...
    @overload
    def on(self, event: Literal["windowOpen"]) -> Callable[[_OnEvent_windowOpen], _OnEvent_windowOpen]:
        """物品欄之外的視窗被打開時觸發事件
        （例如箱子、熔爐、鐵砧、交易面板等）

        Args:
            window: 剛開啟的 `Window`
        """
        ...
    @overload
    def on(self, event: Literal["windowClose"]) -> Callable[[_OnEvent_windowClose], _OnEvent_windowClose]:
        """視窗關閉時觸發事件

        Args:
            window: 剛關閉的 `Window`
        """
        ...
    @overload
    def on(self, event: Literal["sleep"]) -> Callable[[_OnEvent_sleep], _OnEvent_sleep]:
        """機器人自己進入睡眠狀態時觸發事件（無參數）"""
        ...
    @overload
    def on(self, event: Literal["wake"]) -> Callable[[_OnEvent_wake], _OnEvent_wake]:
        """機器人自己醒來時觸發事件（無參數）"""
        ...
    @overload
    def on(self, event: Literal["experience"]) -> Callable[[_OnEvent_experience], _OnEvent_experience]:
        """經驗值有變動時觸發（無參數）
        要讀新值請看 `bot.experience`
        """
        ...
    @overload
    def on(self, event: Literal["physicsTick"]) -> Callable[[_OnEvent_physicsTick], _OnEvent_physicsTick]:
        """每個物理 tick（~20Hz）觸發一次（無參數）
        **這是高頻事件**，每 tick 都可能觸發，請勿在此做耗時工作
        """
        ...
    @overload
    def on(self, event: Literal["physicTick"]) -> Callable[[_OnEvent_physicTick], _OnEvent_physicTick]:
        """`"physicsTick"` 的舊別名（無參數）
        新程式碼請用 `"physicsTick"`；保留只是為了相容老插件
        """
        ...
    @overload
    def on(self, event: Literal["scoreboardCreated"]) -> Callable[[_OnEvent_scoreboardCreated], _OnEvent_scoreboardCreated]:
        """有新記分板被建立時觸發事件

        Args:
            scoreboard: 剛建立的 `ScoreBoard`
        """
        ...
    @overload
    def on(self, event: Literal["scoreboardDeleted"]) -> Callable[[_OnEvent_scoreboardDeleted], _OnEvent_scoreboardDeleted]:
        """記分板被刪除時觸發事件

        Args:
            scoreboard: 被刪除的 `ScoreBoard`
        """
        ...
    @overload
    def on(self, event: Literal["scoreboardTitleChanged"]) -> Callable[[_OnEvent_scoreboardTitleChanged], _OnEvent_scoreboardTitleChanged]:
        """記分板標題變動時觸發事件

        Args:
            scoreboard: 對應 `ScoreBoard`
        """
        ...
    @overload
    def on(self, event: Literal["scoreUpdated"]) -> Callable[[_OnEvent_scoreUpdated], _OnEvent_scoreUpdated]:
        """記分板裡某個項目的分數被更新時觸發事件

        Args:
            scoreboard: 對應 `ScoreBoard`
            item: 被更新的條目編號
        """
        ...
    @overload
    def on(self, event: Literal["scoreRemoved"]) -> Callable[[_OnEvent_scoreRemoved], _OnEvent_scoreRemoved]:
        """記分板裡某條目被移除時觸發事件

        Args:
            scoreboard: 對應 `ScoreBoard`
            item: 被移除的條目編號
        """
        ...
    @overload
    def on(self, event: Literal["scoreboardPosition"]) -> Callable[[_OnEvent_scoreboardPosition], _OnEvent_scoreboardPosition]:
        """記分板顯示位置被切換時觸發事件
        （側邊欄、玩家名下方等）

        Args:
            position: 新的顯示位置（`DisplaySlot`）
            scoreboard: 對應 `ScoreBoard`
        """
        ...
    @overload
    def on(self, event: Literal["teamCreated"]) -> Callable[[_OnEvent_teamCreated], _OnEvent_teamCreated]:
        """有隊伍被建立時觸發事件

        Args:
            team: 新的 `Team`
        """
        ...
    @overload
    def on(self, event: Literal["teamRemoved"]) -> Callable[[_OnEvent_teamRemoved], _OnEvent_teamRemoved]:
        """隊伍被移除時觸發事件

        Args:
            team: 被移除的 `Team`
        """
        ...
    @overload
    def on(self, event: Literal["teamUpdated"]) -> Callable[[_OnEvent_teamUpdated], _OnEvent_teamUpdated]:
        """隊伍資訊變動時觸發事件
        （顏色、前綴等）

        Args:
            team: 被更新的 `Team`
        """
        ...
    @overload
    def on(self, event: Literal["teamMemberAdded"]) -> Callable[[_OnEvent_teamMemberAdded], _OnEvent_teamMemberAdded]:
        """有玩家被加進隊伍時觸發事件

        Args:
            team: 隊伍 `Team`（新成員列表可從 `team.members` 讀）
        """
        ...
    @overload
    def on(self, event: Literal["teamMemberRemoved"]) -> Callable[[_OnEvent_teamMemberRemoved], _OnEvent_teamMemberRemoved]:
        """玩家被踢出隊伍時觸發事件

        Args:
            team: 對應 `Team`
        """
        ...
    @overload
    def on(self, event: Literal["bossBarCreated"]) -> Callable[[_OnEvent_bossBarCreated], _OnEvent_bossBarCreated]:
        """伺服器推送新的 Boss 血條時觸發事件

        Args:
            bossBar: 新的 `BossBar`
        """
        ...
    @overload
    def on(self, event: Literal["bossBarDeleted"]) -> Callable[[_OnEvent_bossBarDeleted], _OnEvent_bossBarDeleted]:
        """Boss 血條被移除時觸發事件

        Args:
            bossBar: 被移除的 `BossBar`
        """
        ...
    @overload
    def on(self, event: Literal["bossBarUpdated"]) -> Callable[[_OnEvent_bossBarUpdated], _OnEvent_bossBarUpdated]:
        """Boss 血條（血量、標題、顏色等）有變動時觸發事件

        Args:
            bossBar: 對應 `BossBar`
        """
        ...
    @overload
    def on(self, event: Literal["resourcePack"]) -> Callable[[_OnEvent_resourcePack], _OnEvent_resourcePack]:
        """伺服器要求客戶端下載資源包時觸發事件
        **注意**：mineflayer 三個呼叫點傳入的參數順序不一致（`resource_pack.js:23/43/46`），收到的資料語意會隨觸發路徑不同
        需要使用此事件時，請對照 JS 原始碼判斷當下情境

        Args:
            url: 資源包網址（通常是，但不保證）
            hash: SHA-1 雜湊值或 uuid，**順序視路徑而定**
            uuid: 套件 UUID，**順序視路徑而定**
        """
        ...
    @overload
    def on(self, event: Literal["particle"]) -> Callable[[_OnEvent_particle], _OnEvent_particle]:
        """伺服器在世界中生成粒子效果時觸發事件
        （例如爆炸、煙霧、藥水光芒）

        Args:
            particle: `Particle` 物件，含位置、類型等資訊
        """
        ...

    @overload
    def once(self, event: Literal["chat"]) -> Callable[[_OnEvent_chat], _OnEvent_chat]:
        """頻道上有公開聊天訊息時觸發事件
        **自己發的訊息也會觸發**，需自行以 `username == bot.username` 比對忽略

        Args:
            username: 發話者的遊戲名稱
            message: 已去除顏色碼與控制字元的純文字
            translate: 聊天類型字串（例如 `chat.type.text`）；多數 Bukkit 系伺服器會是 `None`
            jsonMsg: 伺服器原始的 JSON 訊息物件，保留顏色、點擊事件等 metadata
            matches: 若有自訂 chat pattern 且比中時，是捕獲的字串陣列；否則為 `None`

        See Also:
            `"whisper"`

        ```python
        @bot.on("chat")
        def on_chat(username, message, *_):
            if username == bot.username:
                return
            if message == "hi":
                bot.chat("哈囉")
        ```
        """
        ...
    @overload
    def once(self, event: Literal["whisper"]) -> Callable[[_OnEvent_whisper], _OnEvent_whisper]:
        """有玩家對你私聊（`/tell`、`/msg` 指令）時觸發事件

        Args:
            username: 發話者的遊戲名稱
            message: 已去除顏色碼與控制字元的純文字
            translate: 聊天類型字串（例如 `chat.type.text`）；多數 Bukkit 系伺服器會是 `None`
            jsonMsg: 伺服器原始的 JSON 訊息物件，保留顏色、點擊事件等 metadata
            matches: 若有自訂 chat pattern 且比中時，是捕獲的字串陣列；否則為 `None`

        See Also:
            `"chat"`
        """
        ...
    @overload
    def once(self, event: Literal["actionBar"]) -> Callable[[_OnEvent_actionBar], _OnEvent_actionBar]:
        """伺服器在動作列推送訊息時觸發事件
        （血條上方的懸浮文字）

        Args:
            jsonMsg: 伺服器原始的 JSON 訊息物件
        """
        ...
    @overload
    def once(self, event: Literal["error"]) -> Callable[[_OnEvent_error], _OnEvent_error]:
        """機器人遇到不致命的例外（例如解析封包失敗）時觸發事件
        把這個事件印出來有助於 debug

        Args:
            err: `Error` 物件
        """
        ...
    @overload
    def once(self, event: Literal["message"]) -> Callable[[_OnEvent_message], _OnEvent_message]:
        """**任何**文字訊息抵達時觸發事件
        公開聊天、私聊、系統訊息、指令輸出都涵蓋
        用來記錄所有進入機器人的文字

        Args:
            jsonMsg: 伺服器原始的 JSON 訊息物件
            position: 訊息來源位置字串：`"chat"`（一般聊天）、`"system"`（系統訊息）、`"game_info"`（動作列）
        """
        ...
    @overload
    def once(self, event: Literal["messagestr"]) -> Callable[[_OnEvent_messagestr], _OnEvent_messagestr]:
        """**任何**文字訊息抵達時觸發事件
        公開聊天、私聊、系統訊息、指令輸出都涵蓋
        用來記錄所有進入機器人的文字
        同 `"message"` 但把內容用 `toString()` 攤平成純字串，方便直接印

        Args:
            message: 已攤平的字串訊息
            position: 訊息來源位置字串：`"chat"`（一般聊天）、`"system"`（系統訊息）、`"game_info"`（動作列）
            jsonMsg: 伺服器原始的 JSON 訊息物件
        """
        ...
    @overload
    def once(self, event: Literal["unmatchedMessage"]) -> Callable[[_OnEvent_unmatchedMessage], _OnEvent_unmatchedMessage]:
        """系統訊息沒有對應到任何已註冊的 chat pattern 時觸發事件
        一般玩家很少用到，多半是開發自訂 pattern 時才會監聽

        Args:
            stringMsg: 原始純文字訊息
            jsonMsg: 原始 JSON 訊息物件
        """
        ...
    @overload
    def once(self, event: Literal["inject_allowed"]) -> Callable[[_OnEvent_inject_allowed], _OnEvent_inject_allowed]:
        """mineflayer 載入 `minecraft-data` 並允許插件 inject 時觸發事件（無參數）
        這是**插件開發**的 hook，一般腳本不需要監聽；建議還是等 `"spawn"` 事件觸發後再動作
        """
        ...
    @overload
    def once(self, event: Literal["login"]) -> Callable[[_OnEvent_login], _OnEvent_login]:
        """成功登入伺服器但**尚未進入世界**時觸發事件（無參數）
        此時世界尚未載入，請勿呼叫位置相關的 API，要等待 `"spawn"` 事件觸發後才可以呼叫
        此事件通常只拿來印 log 或做連線成功的標記
        """
        ...
    @overload
    def once(self, event: Literal["spawn"]) -> Callable[[_OnEvent_spawn], _OnEvent_spawn]:
        """機器人在世界中生成（或重新生成）後觸發事件（無參數）
        這是可以真正開始移動的時機

        可查詢 `bot.entity.position`、發聊天訊息、載入插件等都應該在這個事件**之後**進行

        死亡重生、跨維度傳送也會再次觸發事件
        """
        ...
    @overload
    def once(self, event: Literal["respawn"]) -> Callable[[_OnEvent_respawn], _OnEvent_respawn]:
        """機器人重生進入世界時觸發事件（無參數）
        （`"death"` 後會先觸發此事件，接著才是 `"spawn"`）
        """
        ...
    @overload
    def once(self, event: Literal["game"]) -> Callable[[_OnEvent_game], _OnEvent_game]:
        """遊戲模式、維度、難度等 `bot.game` 欄位有變更時觸發事件（無參數）
        要讀新值請直接看 `bot.game.*`
        """
        ...
    @overload
    def once(self, event: Literal["title"]) -> Callable[[_OnEvent_title], _OnEvent_title]:
        """伺服器推送大型標題或副標題時觸發事件

        Args:
            text: 標題文字
            type: `"title"` 或 `"subtitle"`
        """
        ...
    @overload
    def once(self, event: Literal["rain"]) -> Callable[[_OnEvent_rain], _OnEvent_rain]:
        """天氣開始下雨或停雨時觸發事件（無參數）
        要判斷現在狀態請讀 `bot.isRaining`
        """
        ...
    @overload
    def once(self, event: Literal["time"]) -> Callable[[_OnEvent_time], _OnEvent_time]:
        """世界時間有更新時觸發事件（無參數）
        伺服器定時同步、或 `/time set` 指令
        由於幾乎每個 tick 都會觸發，**不要在這裡做耗時工作**
        """
        ...
    @overload
    def once(self, event: Literal["kicked"]) -> Callable[[_OnEvent_kicked], _OnEvent_kicked]:
        """被伺服器踢出時觸發事件
        通常緊接著會觸發 `"end"` 事件

        Args:
            reason: 伺服器送出的踢出原因原始字串，由 mineflayer 原樣轉送未做解析；現代伺服器通常是 JSON 格式的 `ChatMessage`，要顯示給使用者時用 `ChatMessage.fromNotch(reason).toString()` 轉純文字
            loggedIn: `True` 代表已登入後才被踢、`False` 代表握手階段就被拒絕
        """
        ...
    @overload
    def once(self, event: Literal["end"]) -> Callable[[_OnEvent_end], _OnEvent_end]:
        """連線斷開時觸發事件
        正常離線、被踢、網路中斷都會觸發事件
        這也是 `bot.run_forever()` 結束阻塞並讓 script 退出的訊號

        Args:
            reason: 斷線原因
        """
        ...
    @overload
    def once(self, event: Literal["spawnReset"]) -> Callable[[_OnEvent_spawnReset], _OnEvent_spawnReset]:
        """床被破壞 / 重生點重置時觸發事件（無參數）
        例如睡覺用的床被人敲掉
        """
        ...
    @overload
    def once(self, event: Literal["death"]) -> Callable[[_OnEvent_death], _OnEvent_death]:
        """機器人死亡時觸發事件（無參數）
        mineflayer 會自動重生，稍後會再次觸發 `"spawn"` 事件
        """
        ...
    @overload
    def once(self, event: Literal["health"]) -> Callable[[_OnEvent_health], _OnEvent_health]:
        """血量或飽食度有變動時觸發事件（無參數）
        要讀取新值請直接看 `bot.health` / `bot.food`
        """
        ...
    @overload
    def once(self, event: Literal["breath"]) -> Callable[[_OnEvent_breath], _OnEvent_breath]:
        """氧氣量有變動時觸發（無參數）
        要讀新值請看 `bot.oxygenLevel`
        """
        ...
    @overload
    def once(self, event: Literal["entitySwingArm"]) -> Callable[[_OnEvent_entitySwingArm], _OnEvent_entitySwingArm]:
        """實體揮手時觸發事件
        （近戰攻擊、採集動作）

        Args:
            entity: 揮手的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityHurt"]) -> Callable[[_OnEvent_entityHurt], _OnEvent_entityHurt]:
        """實體受傷時觸發事件

        Args:
            entity: 受傷的 `Entity`
            source: 傷害來源 `Entity`（可能是攻擊者或 `None`）
        """
        ...
    @overload
    def once(self, event: Literal["entityDead"]) -> Callable[[_OnEvent_entityDead], _OnEvent_entityDead]:
        """實體死亡時觸發事件

        Args:
            entity: 死亡的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityTaming"]) -> Callable[[_OnEvent_entityTaming], _OnEvent_entityTaming]:
        """玩家正在嘗試馴服動物時觸發事件
        （例如餵骨頭給狼）

        Args:
            entity: 被馴服中的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityTamed"]) -> Callable[[_OnEvent_entityTamed], _OnEvent_entityTamed]:
        """動物成功被馴服時觸發事件

        Args:
            entity: 被馴服的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityShakingOffWater"]) -> Callable[[_OnEvent_entityShakingOffWater], _OnEvent_entityShakingOffWater]:
        """動物抖水時觸發事件

        Args:
            entity: 抖水的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityEatingGrass"]) -> Callable[[_OnEvent_entityEatingGrass], _OnEvent_entityEatingGrass]:
        """羊在吃草時觸發事件

        Args:
            entity: 吃草的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityHandSwap"]) -> Callable[[_OnEvent_entityHandSwap], _OnEvent_entityHandSwap]:
        """實體左右手物品互換時觸發事件

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityWake"]) -> Callable[[_OnEvent_entityWake], _OnEvent_entityWake]:
        """實體從床上醒來時觸發事件

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityEat"]) -> Callable[[_OnEvent_entityEat], _OnEvent_entityEat]:
        """實體在吃東西時觸發事件
        伺服器每次送出吃東西動畫封包（`packet.animation` = 3）時觸發一次

        Args:
            entity: 吃東西的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityCriticalEffect"]) -> Callable[[_OnEvent_entityCriticalEffect], _OnEvent_entityCriticalEffect]:
        """實體被打出暴擊時觸發事件
        （有爆擊粒子效果）

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityMagicCriticalEffect"]) -> Callable[[_OnEvent_entityMagicCriticalEffect], _OnEvent_entityMagicCriticalEffect]:
        """附魔武器的特殊效果觸發時

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityCrouch"]) -> Callable[[_OnEvent_entityCrouch], _OnEvent_entityCrouch]:
        """實體開始蹲下時觸發事件
        （按下 shift）

        Args:
            entity: 潛行中的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityUncrouch"]) -> Callable[[_OnEvent_entityUncrouch], _OnEvent_entityUncrouch]:
        """實體結束蹲下時觸發事件

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityEquip"]) -> Callable[[_OnEvent_entityEquip], _OnEvent_entityEquip]:
        """實體換裝備或更換手持物品時觸發事件

        Args:
            entity: 對應 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entitySleep"]) -> Callable[[_OnEvent_entitySleep], _OnEvent_entitySleep]:
        """實體上床睡覺時觸發事件

        Args:
            entity: 上床的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entitySpawn"]) -> Callable[[_OnEvent_entitySpawn], _OnEvent_entitySpawn]:
        """視野中有新實體出現時觸發事件
        若是玩家實體會另外觸發 `"playerJoined"`

        Args:
            entity: 新出現的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityElytraFlew"]) -> Callable[[_OnEvent_entityElytraFlew], _OnEvent_entityElytraFlew]:
        """實體張開鞘翅飛行時觸發事件

        Args:
            entity: 飛行中的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["usedFirework"]) -> Callable[[_OnEvent_usedFirework], _OnEvent_usedFirework]:
        """玩家使用煙火時觸發事件
        （通常用於鞘翅推進）

        Args:
            fireworkEntityId: 煙火實體的數字 ID
        """
        ...
    @overload
    def once(self, event: Literal["itemDrop"]) -> Callable[[_OnEvent_itemDrop], _OnEvent_itemDrop]:
        """實體丟出物品時觸發事件
        （例如死亡時掉落）

        Args:
            entity: 被掉出的物品 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["playerCollect"]) -> Callable[[_OnEvent_playerCollect], _OnEvent_playerCollect]:
        """玩家撿起掉落物或其他實體時觸發事件

        Args:
            collector: 撿拾的 `Entity`（通常是玩家）
            collected: 被撿拾的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityAttributes"]) -> Callable[[_OnEvent_entityAttributes], _OnEvent_entityAttributes]:
        """實體的屬性表變動時觸發事件
        （移動速度、最大血量等）

        Args:
            entity: 被更新的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityGone"]) -> Callable[[_OnEvent_entityGone], _OnEvent_entityGone]:
        """實體離開視野或被移除時觸發事件

        Args:
            entity: 消失的 `Entity`（讀取它的資料仍可，但不再更新）
        """
        ...
    @overload
    def once(self, event: Literal["entityMoved"]) -> Callable[[_OnEvent_entityMoved], _OnEvent_entityMoved]:
        """實體位置有變動時觸發事件
        **這是高頻事件**，每 tick 都可能觸發，請勿在此做耗時工作

        Args:
            entity: 移動中的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityDetach"]) -> Callable[[_OnEvent_entityDetach], _OnEvent_entityDetach]:
        """實體離開載具時觸發事件

        Args:
            entity: 乘員
            vehicle: 載具
        """
        ...
    @overload
    def once(self, event: Literal["entityAttach"]) -> Callable[[_OnEvent_entityAttach], _OnEvent_entityAttach]:
        """實體掛上載具時觸發事件
        （騎上馬、船等）

        Args:
            entity: 乘員 `Entity`
            vehicle: 載具 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityUpdate"]) -> Callable[[_OnEvent_entityUpdate], _OnEvent_entityUpdate]:
        """實體的 metadata（旁枝屬性，如染色、坐騎狀態等）變動時觸發事件

        Args:
            entity: 被更新的 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["entityEffect"]) -> Callable[[_OnEvent_entityEffect], _OnEvent_entityEffect]:
        """實體被套上狀態效果時觸發事件

        Args:
            entity: 對應 `Entity`
            effect: `Effect` 物件（含 `id`、`amplifier`、`duration`）
        """
        ...
    @overload
    def once(self, event: Literal["entityEffectEnd"]) -> Callable[[_OnEvent_entityEffectEnd], _OnEvent_entityEffectEnd]:
        """實體身上的狀態效果消失時觸發事件

        Args:
            entity: 對應 `Entity`
            effect: 剛結束的 `Effect`
        """
        ...
    @overload
    def once(self, event: Literal["playerJoined"]) -> Callable[[_OnEvent_playerJoined], _OnEvent_playerJoined]:
        """有玩家加入伺服器時觸發事件

        Args:
            player: 加入的 `Player` 物件（含 `.username`、`.uuid`、`.ping` 等）
        """
        ...
    @overload
    def once(self, event: Literal["playerUpdated"]) -> Callable[[_OnEvent_playerUpdated], _OnEvent_playerUpdated]:
        """玩家資訊更新時觸發事件
        **這是高頻事件**，每 tick 都可能觸發，請勿在此做耗時工作
        （延遲、顯示名稱、遊戲模式等）

        Args:
            player: 被更新的 `Player`
        """
        ...
    @overload
    def once(self, event: Literal["playerLeft"]) -> Callable[[_OnEvent_playerLeft], _OnEvent_playerLeft]:
        """有玩家離線時觸發事件

        Args:
            player: 離線的 `Player` 物件
        """
        ...
    @overload
    def once(self, event: Literal["blockUpdate"]) -> Callable[[_OnEvent_blockUpdate], _OnEvent_blockUpdate]:
        """**任何**方塊變動時觸發事件
        **這是高頻事件**，每 tick 都可能觸發，請勿在此做耗時工作

        Args:
            oldBlock: 變更前的 `Block`（可能為 `None`，如果原本是載入邊界）
            newBlock: 變更後的 `Block`
        """
        ...
    @overload
    def once(self, event: Literal["blockUpdate:(x, y, z)"]) -> Callable[[_OnEvent_blockUpdate__x__y__z_], _OnEvent_blockUpdate__x__y__z_]:
        """特定座標的方塊發生變化時觸發事件
        事件名裡的 `(x, y, z)` 要換成實際整數，例如 `"blockUpdate:(100,64,200)"`

        Args:
            oldBlock: 變更前 `Block`，可能為 `None`
            newBlock: 變更後 `Block`，可能為 `None`
        """
        ...
    @overload
    def once(self, event: Literal["chunkColumnLoad"]) -> Callable[[_OnEvent_chunkColumnLoad], _OnEvent_chunkColumnLoad]:
        """區塊柱載入到機器人視野時觸發事件

        Args:
            position: 區塊柱的角落座標 `Vec3`（只有 x、z 有意義）
        """
        ...
    @overload
    def once(self, event: Literal["chunkColumnUnload"]) -> Callable[[_OnEvent_chunkColumnUnload], _OnEvent_chunkColumnUnload]:
        """區塊柱卸載時觸發事件

        Args:
            position: 區塊柱角落座標
        """
        ...
    @overload
    def once(self, event: Literal["soundEffectHeard"]) -> Callable[[_OnEvent_soundEffectHeard], _OnEvent_soundEffectHeard]:
        """可識別的音效事件觸發時觸發事件

        Args:
            soundName: 音效名稱字串（例如 `"entity.creeper.primed"`）
            position: 音效發生位置 `Vec3`
            volume: 音量（浮點數）
            pitch: 音高（浮點數）
        """
        ...
    @overload
    def once(self, event: Literal["hardcodedSoundEffectHeard"]) -> Callable[[_OnEvent_hardcodedSoundEffectHeard], _OnEvent_hardcodedSoundEffectHeard]:
        """舊版硬編碼音效觸發時觸發事件
        多數情境下用 `"soundEffectHeard"` 就夠了

        Args:
            soundId: 音效的數字 ID
            soundCategory: 類別 ID
            position: 位置 `Vec3`
            volume: 音量
            pitch: 音高
        """
        ...
    @overload
    def once(self, event: Literal["noteHeard"]) -> Callable[[_OnEvent_noteHeard], _OnEvent_noteHeard]:
        """音符盒被擊發時觸發事件

        Args:
            block: 音符盒 `Block`
            instrument: 演奏的樂器（含 `id` 與 `name` 如 `"harp"`、`"bassDrum"`）
            pitch: 音高 `0` ~ `24`
        """
        ...
    @overload
    def once(self, event: Literal["pistonMove"]) -> Callable[[_OnEvent_pistonMove], _OnEvent_pistonMove]:
        """任何活塞推/拉動作發生時觸發事件

        Args:
            block: 活塞方塊
            isPulling: `1` 為拉、`0` 為推
            direction: 方向編號 `0` ~ `5`（下、上、北、南、西、東）
        """
        ...
    @overload
    def once(self, event: Literal["chestLidMove"]) -> Callable[[_OnEvent_chestLidMove], _OnEvent_chestLidMove]:
        """任何箱子被打開或關上時觸發事件
        （例如動畫狀態變化時）

        Args:
            block: 箱子方塊
            isOpen: `1` 為開啟動畫、`0` 為關閉動畫
            block2: 若為雙箱，另一半的方塊；單箱為 `None`
        """
        ...
    @overload
    def once(self, event: Literal["blockBreakProgressObserved"]) -> Callable[[_OnEvent_blockBreakProgressObserved], _OnEvent_blockBreakProgressObserved]:
        """看見附近有人在挖方塊時觸發（不是自己挖的）

        Args:
            block: 正在被挖的 `Block`
            destroyStage: 破壞進度 `0` ~ `9`；`9` 時接近挖斷
        """
        ...
    @overload
    def once(self, event: Literal["blockBreakProgressEnd"]) -> Callable[[_OnEvent_blockBreakProgressEnd], _OnEvent_blockBreakProgressEnd]:
        """挖掘動作結束時觸發（可能挖斷，也可能中途放棄）

        Args:
            block: 對應的 `Block`
        """
        ...
    @overload
    def once(self, event: Literal["diggingCompleted"]) -> Callable[[_OnEvent_diggingCompleted], _OnEvent_diggingCompleted]:
        """`bot.dig(block)` 成功挖掉方塊時觸發事件

        Args:
            block: 被挖掉的 `Block`（此時方塊類型多半已變成空氣，位置資訊仍可用）
        """
        ...
    @overload
    def once(self, event: Literal["diggingAborted"]) -> Callable[[_OnEvent_diggingAborted], _OnEvent_diggingAborted]:
        """`bot.dig(block)` 被中斷時觸發事件
        例如玩家移動離開太遠、或方塊被他人搶挖

        Args:
            block: 中途放棄的目標方塊
        """
        ...
    @overload
    def once(self, event: Literal["move"]) -> Callable[[_OnEvent_move], _OnEvent_move]:
        """機器人位置或視角改變時觸發事件
        **這是高頻事件**，每 tick 都可能觸發，請勿在此做耗時工作

        Args:
            position: 移動前的 `Vec3`（可以和 `bot.entity.position` 比較得知移動方向 / 距離）
        """
        ...
    @overload
    def once(self, event: Literal["forcedMove"]) -> Callable[[_OnEvent_forcedMove], _OnEvent_forcedMove]:
        """被伺服器強制傳送時觸發事件（無參數）
        （例如teleport、`/tp` 指令等）
        重要：此事件觸發後，機器人的當前位置會跟路徑規劃的預期不符，常需重新規劃路線
        """
        ...
    @overload
    def once(self, event: Literal["mount"]) -> Callable[[_OnEvent_mount], _OnEvent_mount]:
        """機器人騎上載具時觸發事件（無參數）
        （例如馬、船、礦車等）
        可讀 `bot.vehicle` 看載具
        """
        ...
    @overload
    def once(self, event: Literal["dismount"]) -> Callable[[_OnEvent_dismount], _OnEvent_dismount]:
        """機器人下載具時觸發事件

        Args:
            vehicle: 剛離開的載具 `Entity`
        """
        ...
    @overload
    def once(self, event: Literal["windowOpen"]) -> Callable[[_OnEvent_windowOpen], _OnEvent_windowOpen]:
        """物品欄之外的視窗被打開時觸發事件
        （例如箱子、熔爐、鐵砧、交易面板等）

        Args:
            window: 剛開啟的 `Window`
        """
        ...
    @overload
    def once(self, event: Literal["windowClose"]) -> Callable[[_OnEvent_windowClose], _OnEvent_windowClose]:
        """視窗關閉時觸發事件

        Args:
            window: 剛關閉的 `Window`
        """
        ...
    @overload
    def once(self, event: Literal["sleep"]) -> Callable[[_OnEvent_sleep], _OnEvent_sleep]:
        """機器人自己進入睡眠狀態時觸發事件（無參數）"""
        ...
    @overload
    def once(self, event: Literal["wake"]) -> Callable[[_OnEvent_wake], _OnEvent_wake]:
        """機器人自己醒來時觸發事件（無參數）"""
        ...
    @overload
    def once(self, event: Literal["experience"]) -> Callable[[_OnEvent_experience], _OnEvent_experience]:
        """經驗值有變動時觸發（無參數）
        要讀新值請看 `bot.experience`
        """
        ...
    @overload
    def once(self, event: Literal["physicsTick"]) -> Callable[[_OnEvent_physicsTick], _OnEvent_physicsTick]:
        """每個物理 tick（~20Hz）觸發一次（無參數）
        **這是高頻事件**，每 tick 都可能觸發，請勿在此做耗時工作
        """
        ...
    @overload
    def once(self, event: Literal["physicTick"]) -> Callable[[_OnEvent_physicTick], _OnEvent_physicTick]:
        """`"physicsTick"` 的舊別名（無參數）
        新程式碼請用 `"physicsTick"`；保留只是為了相容老插件
        """
        ...
    @overload
    def once(self, event: Literal["scoreboardCreated"]) -> Callable[[_OnEvent_scoreboardCreated], _OnEvent_scoreboardCreated]:
        """有新記分板被建立時觸發事件

        Args:
            scoreboard: 剛建立的 `ScoreBoard`
        """
        ...
    @overload
    def once(self, event: Literal["scoreboardDeleted"]) -> Callable[[_OnEvent_scoreboardDeleted], _OnEvent_scoreboardDeleted]:
        """記分板被刪除時觸發事件

        Args:
            scoreboard: 被刪除的 `ScoreBoard`
        """
        ...
    @overload
    def once(self, event: Literal["scoreboardTitleChanged"]) -> Callable[[_OnEvent_scoreboardTitleChanged], _OnEvent_scoreboardTitleChanged]:
        """記分板標題變動時觸發事件

        Args:
            scoreboard: 對應 `ScoreBoard`
        """
        ...
    @overload
    def once(self, event: Literal["scoreUpdated"]) -> Callable[[_OnEvent_scoreUpdated], _OnEvent_scoreUpdated]:
        """記分板裡某個項目的分數被更新時觸發事件

        Args:
            scoreboard: 對應 `ScoreBoard`
            item: 被更新的條目編號
        """
        ...
    @overload
    def once(self, event: Literal["scoreRemoved"]) -> Callable[[_OnEvent_scoreRemoved], _OnEvent_scoreRemoved]:
        """記分板裡某條目被移除時觸發事件

        Args:
            scoreboard: 對應 `ScoreBoard`
            item: 被移除的條目編號
        """
        ...
    @overload
    def once(self, event: Literal["scoreboardPosition"]) -> Callable[[_OnEvent_scoreboardPosition], _OnEvent_scoreboardPosition]:
        """記分板顯示位置被切換時觸發事件
        （側邊欄、玩家名下方等）

        Args:
            position: 新的顯示位置（`DisplaySlot`）
            scoreboard: 對應 `ScoreBoard`
        """
        ...
    @overload
    def once(self, event: Literal["teamCreated"]) -> Callable[[_OnEvent_teamCreated], _OnEvent_teamCreated]:
        """有隊伍被建立時觸發事件

        Args:
            team: 新的 `Team`
        """
        ...
    @overload
    def once(self, event: Literal["teamRemoved"]) -> Callable[[_OnEvent_teamRemoved], _OnEvent_teamRemoved]:
        """隊伍被移除時觸發事件

        Args:
            team: 被移除的 `Team`
        """
        ...
    @overload
    def once(self, event: Literal["teamUpdated"]) -> Callable[[_OnEvent_teamUpdated], _OnEvent_teamUpdated]:
        """隊伍資訊變動時觸發事件
        （顏色、前綴等）

        Args:
            team: 被更新的 `Team`
        """
        ...
    @overload
    def once(self, event: Literal["teamMemberAdded"]) -> Callable[[_OnEvent_teamMemberAdded], _OnEvent_teamMemberAdded]:
        """有玩家被加進隊伍時觸發事件

        Args:
            team: 隊伍 `Team`（新成員列表可從 `team.members` 讀）
        """
        ...
    @overload
    def once(self, event: Literal["teamMemberRemoved"]) -> Callable[[_OnEvent_teamMemberRemoved], _OnEvent_teamMemberRemoved]:
        """玩家被踢出隊伍時觸發事件

        Args:
            team: 對應 `Team`
        """
        ...
    @overload
    def once(self, event: Literal["bossBarCreated"]) -> Callable[[_OnEvent_bossBarCreated], _OnEvent_bossBarCreated]:
        """伺服器推送新的 Boss 血條時觸發事件

        Args:
            bossBar: 新的 `BossBar`
        """
        ...
    @overload
    def once(self, event: Literal["bossBarDeleted"]) -> Callable[[_OnEvent_bossBarDeleted], _OnEvent_bossBarDeleted]:
        """Boss 血條被移除時觸發事件

        Args:
            bossBar: 被移除的 `BossBar`
        """
        ...
    @overload
    def once(self, event: Literal["bossBarUpdated"]) -> Callable[[_OnEvent_bossBarUpdated], _OnEvent_bossBarUpdated]:
        """Boss 血條（血量、標題、顏色等）有變動時觸發事件

        Args:
            bossBar: 對應 `BossBar`
        """
        ...
    @overload
    def once(self, event: Literal["resourcePack"]) -> Callable[[_OnEvent_resourcePack], _OnEvent_resourcePack]:
        """伺服器要求客戶端下載資源包時觸發事件
        **注意**：mineflayer 三個呼叫點傳入的參數順序不一致（`resource_pack.js:23/43/46`），收到的資料語意會隨觸發路徑不同
        需要使用此事件時，請對照 JS 原始碼判斷當下情境

        Args:
            url: 資源包網址（通常是，但不保證）
            hash: SHA-1 雜湊值或 uuid，**順序視路徑而定**
            uuid: 套件 UUID，**順序視路徑而定**
        """
        ...
    @overload
    def once(self, event: Literal["particle"]) -> Callable[[_OnEvent_particle], _OnEvent_particle]:
        """伺服器在世界中生成粒子效果時觸發事件
        （例如爆炸、煙霧、藥水光芒）

        Args:
            particle: `Particle` 物件，含位置、類型等資訊
        """
        ...

    # --- Minethon-specific methods (defined in bot.py) ---
    # Populated after bot.load_plugin('mineflayer-pathfinder'):
    pathfinder: Pathfinder

    @overload
    def load_plugin(
        self,
        name: Literal["mineflayer-pathfinder"],
        version: str | None = ...,
        *,
        export_key: str | None = ...,
        **options: object,
    ) -> PathfinderModule:
        """一鍵載入一個 Type A 的 mineflayer 插件（例如 `mineflayer-pathfinder`）

        Args:
            name: npm 套件名稱
            version: 要釘住的版本字串；省略時使用 bridge 已安裝的版本。建議**一律填**以確保可重現
            export_key: 該套件的 installer 函式掛在 module 的哪個屬性上。pathfinder 已內建對照，其他套件不相符時可傳這個覆寫
            **options: 會轉傳給「HOF 風格」的插件（例如 `@ssmidge/mineflayer-dashboard`）。普通插件會忽略

        Returns:
            該插件的原生 JS module，方便取用它匯出的 class / 常數
        """
        ...
    @overload
    def load_plugin(
        self,
        name: str,
        version: str | None = ...,
        *,
        export_key: str | None = ...,
        **options: object,
    ) -> object:
        """一鍵載入一個 Type A 的 mineflayer 插件（例如 `mineflayer-pathfinder`）

        Args:
            name: npm 套件名稱
            version: 要釘住的版本字串；省略時使用 bridge 已安裝的版本。建議**一律填**以確保可重現
            export_key: 該套件的 installer 函式掛在 module 的哪個屬性上。pathfinder 已內建對照，其他套件不相符時可傳這個覆寫
            **options: 會轉傳給「HOF 風格」的插件（例如 `@ssmidge/mineflayer-dashboard`）。普通插件會忽略

        Returns:
            該插件的原生 JS module，方便取用它匯出的 class / 常數
        """
        ...
    def require(self, name: str, version: str | None = ...) -> object:
        """原始逃生口——載入任意 JS 套件並回傳原生 proxy
        用在 Type B / C / D 插件（prismarine-viewer、web-inventory、statemachine 等）需要自行初始化時

        Args:
            name: npm 套件名稱
            version: (選填) 要釘住的版本字串

        Returns:
            的物件未做型別包裝，請對照該插件 README 操作
        """
        ...
    def run_forever(self) -> None:
        """阻塞呼叫它的執行緒，直到機器人斷線（`"end"` 事件觸發）
        學生腳本最後通常加這一行讓 script 不會提早結束
        按 Ctrl-C 會乾淨退出
        """
        ...


def create_bot(**options: object) -> Bot:
    """建立並啟動一個 mineflayer 機器人
    常用選項以 `snake_case` 傳入，內部會自動轉成 `camelCase` 給 JS 端

    常用選項：

    Args:
        host: Minecraft 伺服器網址或 IP
        port: 連線 port（預設 `25565`）
        username: 機器人的遊戲名稱
        password: 正版帳號密碼（Mojang / Drasl 等自訂 auth 時用）
        version: 強制協議版本字串，例如 `"1.20.4"`；省略會自動偵測
        auth: 驗證方式：`"mojang"` / `"microsoft"` / `"offline"`
        auth_server: 自訂 auth 伺服器網址（Drasl / Yggdrasil-compatible）
        session_server: 自訂 session 伺服器網址
            - 其他 `mineflayer.createBot()` 接受的選項都能直接傳

    回傳 `Bot`。連線是非同步進行的；請監聽 `"spawn"` 事件之後再動手操作世界

    ```python
    bot = create_bot(
        host="play.camp.tw",
        username="alice",
        auth="mojang",
        auth_server="https://drasl.example.com/auth",
        session_server="https://drasl.example.com/session",
    )
    ```
    """
    ...
