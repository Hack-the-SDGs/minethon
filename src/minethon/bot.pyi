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
    """3D vector (from `vec3` package).

    Ref: vec3/index.d.ts — Vec3
    """

    x: float
    y: float
    z: float
    def isZero(self) -> bool: ...
    def at(self, id: int) -> float: ...
    def xz(self) -> tuple[float, float]: ...
    def xy(self) -> tuple[float, float]: ...
    def yz(self) -> tuple[float, float]: ...
    def xzy(self) -> Vec3: ...
    def set(self, x: float, y: float, z: float) -> Self: ...
    def update(self, other: Vec3) -> Self: ...
    def rounded(self) -> Vec3: ...
    def round(self) -> Self: ...
    def floored(self) -> Vec3: ...
    def floor(self) -> Self: ...
    def offset(self, dx: float, dy: float, dz: float) -> Vec3: ...
    def translate(self, dx: float, dy: float, dz: float) -> Self: ...
    def add(self, other: Vec3) -> Self: ...
    def subtract(self, other: Vec3) -> Self: ...
    def multiply(self, other: Vec3) -> Self: ...
    def divide(self, other: Vec3) -> Self: ...
    def plus(self, other: Vec3) -> Vec3: ...
    def minus(self, other: Vec3) -> Vec3: ...
    def scaled(self, scalar: float) -> Vec3: ...
    def abs(self) -> Vec3: ...
    def volume(self) -> float: ...
    def modulus(self, other: Vec3) -> Vec3: ...
    def distanceTo(self, other: Vec3) -> float: ...
    def distanceSquared(self, other: Vec3) -> float: ...
    def equals(self, other: Vec3, error: float = ...) -> bool: ...
    def toString(self) -> str: ...
    def clone(self) -> Vec3: ...
    def min(self, other: Vec3) -> Vec3: ...
    def max(self, other: Vec3) -> Vec3: ...
    def norm(self) -> float: ...
    def dot(self, other: Vec3) -> float: ...
    def cross(self, other: Vec3) -> Vec3: ...
    def unit(self) -> Vec3: ...
    def normalize(self) -> Vec3: ...
    def scale(self, scalar: float) -> Self: ...
    def xyDistanceTo(self, other: Vec3) -> float: ...
    def xzDistanceTo(self, other: Vec3) -> float: ...
    def yzDistanceTo(self, other: Vec3) -> float: ...
    def innerProduct(self, other: Vec3) -> float: ...
    def manhattanDistanceTo(self, other: Vec3) -> float: ...
    def toArray(self) -> tuple[float, float, float]: ...

class ChatMessage:
    """Minecraft chat message (from `prismarine-chat` package).

    Ref: prismarine-chat/index.d.ts — ChatMessage
    """

    json: object
    extra: list[ChatMessage] | None
    translate: str | None
    selector: str | None
    keybind: str | None
    score: object | None
    def append(self, *messages: object) -> None: ...
    def clone(self) -> ChatMessage: ...
    def toString(self, language: object = ...) -> str: ...
    def toMotd(self, language: object = ...) -> str: ...
    def toAnsi(self, language: object = ...) -> str: ...
    def toHTML(self, language: object = ..., styles: object = ...) -> str: ...
    def length(self) -> int: ...
    def getText(self, idx: int, language: object = ...) -> str: ...
    def valueOf(self) -> str: ...

EntityType = Literal[
    "player", "mob", "object", "global", "orb", "projectile", "hostile", "other"
]

class Effect:
    """Potion effect on an entity.

    Ref: prismarine-entity/index.d.ts — Effect
    """

    id: int
    amplifier: int
    duration: int

class Entity:
    """A world entity (player, mob, dropped item, projectile, etc.).

    Ref: prismarine-entity/index.d.ts — Entity
    """

    id: int
    type: EntityType
    uuid: str | None
    username: str | None
    mobType: str | None
    displayName: str | None
    entityType: int | None
    kind: str | None
    name: str | None
    objectType: str | None
    count: int | None
    position: Vec3
    velocity: Vec3
    yaw: float
    pitch: float
    height: float
    width: float
    onGround: bool
    equipment: list[Item]
    heldItem: Item
    metadata: list[object]
    isValid: bool
    health: float | None
    food: float | None
    foodSaturation: float | None
    elytraFlying: bool | None
    player: object | None
    effects: list[Effect]
    vehicle: Entity
    passengers: list[Entity]
    def setEquipment(self, index: int, item: Item) -> None: ...
    def getCustomName(self) -> ChatMessage | None: ...
    def getDroppedItem(self) -> Item | None: ...

class Block:
    """A world block.

    Ref: prismarine-block/index.d.ts — Block
    """

    stateId: int
    type: int
    metadata: int
    light: int
    skyLight: int
    blockEntity: object
    entity: object | None
    hash: int | None
    biome: object
    name: str
    displayName: str
    shapes: list[tuple[float, float, float, float, float, float]]
    hardness: float
    boundingBox: Literal["block", "empty"]
    transparent: bool
    diggable: bool
    isWaterlogged: bool | None
    material: str | None
    harvestTools: dict[str, bool] | None
    position: Vec3
    def canHarvest(self, heldItemType: int | None) -> bool: ...
    def getProperties(self) -> dict[str, object]: ...
    def digTime(
        self,
        heldItemType: int | None,
        creative: bool,
        inWater: bool,
        notOnGround: bool,
        enchantments: object = ...,
        effects: list[Effect] | None = ...,
    ) -> float: ...

class Item:
    """An inventory item.

    Ref: prismarine-item/index.d.ts — Item
    """

    type: int
    slot: int
    count: int
    metadata: int
    nbt: object | None
    stackId: int | None
    name: str
    displayName: str
    stackSize: int
    maxDurability: int
    durabilityUsed: int
    enchants: list[dict[str, object]]
    blocksCanPlaceOn: list[tuple[str]]
    blocksCanDestroy: list[tuple[str]]
    repairCost: int
    customName: str | None
    customLore: str | list[str] | None
    customModel: str | None
    spawnEggMobName: str

class Window:
    """An open window / container (chest, furnace, inventory, etc.).

    Ref: prismarine-windows/index.d.ts — Window
    """

    id: int
    type: int | str
    title: str
    slots: list[Item | None]
    inventoryStart: int
    inventoryEnd: int
    hotbarStart: int
    craftingResultSlot: int
    requiresConfirmation: bool
    selectedItem: Item | None
    def findInventoryItem(
        self, itemType: int, metadata: int | None, notFull: bool
    ) -> Item | None: ...
    def findContainerItem(
        self, itemType: int, metadata: int | None, notFull: bool
    ) -> Item | None: ...
    def firstEmptySlotRange(self, start: int, end: int) -> int | None: ...
    def firstEmptyHotbarSlot(self) -> int | None: ...
    def firstEmptyContainerSlot(self) -> int | None: ...
    def firstEmptyInventorySlot(self, hotbarFirst: bool = ...) -> int | None: ...
    def items(self) -> list[Item]: ...
    def containerItems(self) -> list[Item]: ...
    def count(self, itemType: int | str, metadata: int | None) -> int: ...
    def emptySlotCount(self) -> int: ...

class Recipe:
    """A crafting recipe.

    Ref: prismarine-recipe/index.d.ts — Recipe
    """

    result: object
    inShape: list[list[object]]
    outShape: list[list[object]]
    ingredients: list[object]
    delta: list[object]
    requiresTable: bool

# --- Mineflayer type aliases ---
ChatLevel = Literal["enabled", "commandsOnly", "disabled"]
ViewDistance = (
    Literal["far"] | Literal["normal"] | Literal["short"] | Literal["tiny"] | float
)
MainHands = Literal["left", "right"]
LevelType = Literal[
    "default", "flat", "largeBiomes", "amplified", "customized", "buffet", "default_1_1"
]
GameMode = Literal["survival", "creative", "adventure", "spectator"]
Dimension = Literal["the_nether", "overworld", "the_end"]
Difficulty = Literal["peaceful", "easy", "normal", "hard"]
ControlState = Literal["forward", "back", "left", "right", "jump", "sprint", "sneak"]
EquipmentDestination = Literal["hand", "head", "torso", "legs", "feet", "off-hand"]

# --- Mineflayer aux interfaces ---

class Player:
    """Ref: mineflayer/index.d.ts — Player"""

    uuid: str
    username: str
    displayName: ChatMessage
    gamemode: float
    ping: float
    entity: Entity
    skinData: object | None
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
    name: Literal["harp", "doubleBass", "snareDrum", "sticks", "bassDrum"]

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
    """Ref: mineflayer/index.d.ts — Chest"""
    def close(self) -> None: ...
    def deposit(
        self, itemType: float, metadata: float | None, count: float | None
    ) -> None: ...
    def withdraw(
        self, itemType: float, metadata: float | None, count: float | None
    ) -> None: ...

class Dispenser:
    """Ref: mineflayer/index.d.ts — Dispenser"""
    def close(self) -> None: ...
    def deposit(
        self, itemType: float, metadata: float | None, count: float | None
    ) -> None: ...
    def withdraw(
        self, itemType: float, metadata: float | None, count: float | None
    ) -> None: ...

class Furnace:
    """Ref: mineflayer/index.d.ts — Furnace"""

    fuel: float
    progress: float
    def close(self) -> None: ...
    def takeInput(self) -> Item: ...
    def takeFuel(self) -> Item: ...
    def takeOutput(self) -> Item: ...
    def putInput(
        self, itemType: float, metadata: float | None, count: float
    ) -> None: ...
    def putFuel(
        self, itemType: float, metadata: float | None, count: float
    ) -> None: ...
    def inputItem(self) -> Item: ...
    def fuelItem(self) -> Item: ...
    def outputItem(self) -> Item: ...

class EnchantmentTable:
    """Ref: mineflayer/index.d.ts — EnchantmentTable"""

    enchantments: list[Enchantment]
    def close(self) -> None: ...
    def targetItem(self) -> Item: ...
    def enchant(self, choice: str | float) -> Item: ...
    def takeTargetItem(self) -> Item: ...
    def putTargetItem(self, item: Item) -> Item: ...
    def putLapis(self, item: Item) -> Item: ...

class Anvil:
    """Ref: mineflayer/index.d.ts — Anvil"""
    def combine(self, itemOne: Item, itemTwo: Item, name: str | None = ...) -> None: ...
    def rename(self, item: Item, name: str | None = ...) -> None: ...

class Villager:
    """Ref: mineflayer/index.d.ts — Villager"""

    trades: list[VillagerTrade]
    def close(self) -> None: ...

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
    auth: Literal["mojang", "microsoft", "offline"]
    authServer: str
    sessionServer: str
    onMsaCode: Callable[[object], None]
    authTitle: str

class Bot:
    """Pythonic façade over a mineflayer Bot proxy.

    Every property and method below mirrors mineflayer's Bot interface.

    Ref: mineflayer/index.d.ts — interface Bot
    """

    username: str
    protocolVersion: str
    majorVersion: str
    version: str
    entity: Entity
    entities: dict[str, Entity]
    fireworkRocketDuration: float
    spawnPoint: Vec3
    game: GameState
    player: Player
    players: dict[str, Player]
    isRaining: bool
    thunderState: float
    chatPatterns: list[object]
    settings: object
    experience: Experience
    health: float
    food: float
    foodSaturation: float
    oxygenLevel: float
    physics: PhysicsOptions
    physicsEnabled: bool
    time: Time
    quickBarSlot: float
    inventory: Window
    targetDigBlock: Block
    isSleeping: bool
    scoreboards: dict[str, object]
    scoreboard: dict[str, object]
    teams: dict[str, object]
    teamMap: dict[str, object]
    controlState: ControlStateStatus
    creative: creativeMethods
    world: object
    heldItem: Item | None
    usingHeldItem: bool
    currentWindow: Window | None
    simpleClick: simpleClick
    tablist: Tablist
    registry: object
    connect: Callable[[BotOptions], None]
    supportFeature: object
    end: Callable[[str | None], None]
    blockAt: Callable[[Vec3, bool | None], Block | None]
    blockInSight: Callable[[float, float], Block | None]
    blockAtCursor: Callable[[float | None, Callable[..., object] | None], Block | None]
    blockAtEntityCursor: Callable[
        [Entity | None, float | None, Callable[..., object] | None], Block | None
    ]
    canSeeBlock: Callable[[Block], bool]
    findBlock: Callable[[FindBlockOptions], Block | None]
    findBlocks: Callable[[FindBlockOptions], list[Vec3]]
    canDigBlock: Callable[[Block], bool]
    recipesFor: Callable[
        [float, float | None, float | None, Block | bool | None], list[Recipe]
    ]
    recipesAll: Callable[[float, float | None, Block | bool | None], list[Recipe]]
    quit: Callable[[str | None], None]
    tabComplete: Callable[[str, bool | None, bool | None, float | None], list[str]]
    chat: Callable[[str], None]
    whisper: Callable[[str, str], None]
    chatAddPattern: Callable[[object, str, str | None], float]
    setSettings: Callable[[object], None]
    loadPlugin: Callable[[Callable[..., object]], None]
    loadPlugins: Callable[[list[Callable[..., object]]], None]
    hasPlugin: Callable[[Callable[..., object]], bool]
    sleep: Callable[[Block], None]
    isABed: Callable[[Block], bool]
    wake: Callable[[], None]
    elytraFly: Callable[[], None]
    setControlState: Callable[[ControlState, bool], None]
    getControlState: Callable[[ControlState], bool]
    clearControlStates: Callable[[], None]
    getExplosionDamages: Callable[[Entity, Vec3, float, bool | None], float | None]
    lookAt: Callable[[Vec3, bool | None], None]
    look: Callable[[float, float, bool | None], None]
    updateSign: Callable[[Block, str, bool | None], None]
    equip: Callable[[Item | float, EquipmentDestination | None], None]
    unequip: Callable[[EquipmentDestination | None], None]
    tossStack: Callable[[Item], None]
    toss: Callable[[float, float | None, float | None], None]
    dig: Callable[[Callable[[Block, bool | Literal["ignore"] | None], object]], object]
    stopDigging: Callable[[], None]
    digTime: Callable[[Block], float]
    placeBlock: Callable[[Block, Vec3], None]
    placeEntity: Callable[[Block, Vec3], Entity]
    activateBlock: Callable[[Block, Vec3 | None, Vec3 | None], None]
    activateEntity: Callable[[Entity], None]
    activateEntityAt: Callable[[Entity, Vec3], None]
    consume: Callable[[], None]
    fish: Callable[[], None]
    activateItem: Callable[[bool | None], None]
    deactivateItem: Callable[[], None]
    useOn: Callable[[Entity], None]
    attack: Callable[[Entity], None]
    swingArm: Callable[[Literal["left"] | Literal["right"] | None, bool | None], None]
    mount: Callable[[Entity], None]
    dismount: Callable[[], None]
    moveVehicle: Callable[[float, float], None]
    setQuickBarSlot: Callable[[float], None]
    craft: Callable[[Recipe, float | None, Block | None], None]
    writeBook: Callable[[float, list[str]], None]
    openContainer: Callable[
        [Block | Entity, Vec3 | None, Vec3 | None], Chest | Dispenser
    ]
    openChest: Callable[[Block | Entity, float | None, Vec3 | None], Chest]
    openFurnace: Callable[[Block], Furnace]
    openDispenser: Callable[[Block], Dispenser]
    openEnchantmentTable: Callable[[Block], EnchantmentTable]
    openAnvil: Callable[[Block], Anvil]
    openVillager: Callable[[Entity], Villager]
    trade: Callable[[Villager, str | float, float | None], None]
    setCommandBlock: Callable[[Vec3, str, CommandBlockOptions], None]
    clickWindow: Callable[[float, float, float], None]
    putSelectedItemRange: Callable[[float, float, Window, object], None]
    putAway: Callable[[float], None]
    closeWindow: Callable[[Window], None]
    transfer: Callable[[TransferOptions], None]
    openBlock: Callable[[Block, Vec3 | None, Vec3 | None], Window]
    openEntity: Callable[[Entity, object], Window]
    moveSlotItem: Callable[[float, float], None]
    updateHeldItem: Callable[[], None]
    getEquipmentDestSlot: Callable[[str], float]
    waitForChunksToLoad: Callable[[], None]
    entityAtCursor: Callable[[float | None], Entity | None]
    nearestEntity: Callable[[Callable[[Entity], bool] | None], Entity | None]
    waitForTicks: Callable[[float], None]
    addChatPattern: Callable[[str, object, chatPatternOptions | None], float]
    addChatPatternSet: Callable[[str, list[object], chatPatternOptions | None], float]
    removeChatPattern: Callable[[str | float], None]
    awaitMessage: Callable[[list[str] | list[object]], str]
    acceptResourcePack: Callable[[], None]
    denyResourcePack: Callable[[], None]
    respawn: Callable[[], None]

    # --- Typed event overloads (generated from BotEvents) ---
    @overload
    def on(
        self, event: Literal["chat"]
    ) -> Callable[[_OnEvent_chat], _OnEvent_chat]: ...
    @overload
    def on(
        self, event: Literal["whisper"]
    ) -> Callable[[_OnEvent_whisper], _OnEvent_whisper]: ...
    @overload
    def on(
        self, event: Literal["actionBar"]
    ) -> Callable[[_OnEvent_actionBar], _OnEvent_actionBar]: ...
    @overload
    def on(
        self, event: Literal["error"]
    ) -> Callable[[_OnEvent_error], _OnEvent_error]: ...
    @overload
    def on(
        self, event: Literal["message"]
    ) -> Callable[[_OnEvent_message], _OnEvent_message]: ...
    @overload
    def on(
        self, event: Literal["messagestr"]
    ) -> Callable[[_OnEvent_messagestr], _OnEvent_messagestr]: ...
    @overload
    def on(
        self, event: Literal["unmatchedMessage"]
    ) -> Callable[[_OnEvent_unmatchedMessage], _OnEvent_unmatchedMessage]: ...
    @overload
    def on(
        self, event: Literal["inject_allowed"]
    ) -> Callable[[_OnEvent_inject_allowed], _OnEvent_inject_allowed]: ...
    @overload
    def on(
        self, event: Literal["login"]
    ) -> Callable[[_OnEvent_login], _OnEvent_login]: ...
    @overload
    def on(
        self, event: Literal["spawn"]
    ) -> Callable[[_OnEvent_spawn], _OnEvent_spawn]: ...
    @overload
    def on(
        self, event: Literal["respawn"]
    ) -> Callable[[_OnEvent_respawn], _OnEvent_respawn]: ...
    @overload
    def on(
        self, event: Literal["game"]
    ) -> Callable[[_OnEvent_game], _OnEvent_game]: ...
    @overload
    def on(
        self, event: Literal["title"]
    ) -> Callable[[_OnEvent_title], _OnEvent_title]: ...
    @overload
    def on(
        self, event: Literal["rain"]
    ) -> Callable[[_OnEvent_rain], _OnEvent_rain]: ...
    @overload
    def on(
        self, event: Literal["time"]
    ) -> Callable[[_OnEvent_time], _OnEvent_time]: ...
    @overload
    def on(
        self, event: Literal["kicked"]
    ) -> Callable[[_OnEvent_kicked], _OnEvent_kicked]: ...
    @overload
    def on(self, event: Literal["end"]) -> Callable[[_OnEvent_end], _OnEvent_end]: ...
    @overload
    def on(
        self, event: Literal["spawnReset"]
    ) -> Callable[[_OnEvent_spawnReset], _OnEvent_spawnReset]: ...
    @overload
    def on(
        self, event: Literal["death"]
    ) -> Callable[[_OnEvent_death], _OnEvent_death]: ...
    @overload
    def on(
        self, event: Literal["health"]
    ) -> Callable[[_OnEvent_health], _OnEvent_health]: ...
    @overload
    def on(
        self, event: Literal["breath"]
    ) -> Callable[[_OnEvent_breath], _OnEvent_breath]: ...
    @overload
    def on(
        self, event: Literal["entitySwingArm"]
    ) -> Callable[[_OnEvent_entitySwingArm], _OnEvent_entitySwingArm]: ...
    @overload
    def on(
        self, event: Literal["entityHurt"]
    ) -> Callable[[_OnEvent_entityHurt], _OnEvent_entityHurt]: ...
    @overload
    def on(
        self, event: Literal["entityDead"]
    ) -> Callable[[_OnEvent_entityDead], _OnEvent_entityDead]: ...
    @overload
    def on(
        self, event: Literal["entityTaming"]
    ) -> Callable[[_OnEvent_entityTaming], _OnEvent_entityTaming]: ...
    @overload
    def on(
        self, event: Literal["entityTamed"]
    ) -> Callable[[_OnEvent_entityTamed], _OnEvent_entityTamed]: ...
    @overload
    def on(
        self, event: Literal["entityShakingOffWater"]
    ) -> Callable[[_OnEvent_entityShakingOffWater], _OnEvent_entityShakingOffWater]: ...
    @overload
    def on(
        self, event: Literal["entityEatingGrass"]
    ) -> Callable[[_OnEvent_entityEatingGrass], _OnEvent_entityEatingGrass]: ...
    @overload
    def on(
        self, event: Literal["entityHandSwap"]
    ) -> Callable[[_OnEvent_entityHandSwap], _OnEvent_entityHandSwap]: ...
    @overload
    def on(
        self, event: Literal["entityWake"]
    ) -> Callable[[_OnEvent_entityWake], _OnEvent_entityWake]: ...
    @overload
    def on(
        self, event: Literal["entityEat"]
    ) -> Callable[[_OnEvent_entityEat], _OnEvent_entityEat]: ...
    @overload
    def on(
        self, event: Literal["entityCriticalEffect"]
    ) -> Callable[[_OnEvent_entityCriticalEffect], _OnEvent_entityCriticalEffect]: ...
    @overload
    def on(
        self, event: Literal["entityMagicCriticalEffect"]
    ) -> Callable[
        [_OnEvent_entityMagicCriticalEffect], _OnEvent_entityMagicCriticalEffect
    ]: ...
    @overload
    def on(
        self, event: Literal["entityCrouch"]
    ) -> Callable[[_OnEvent_entityCrouch], _OnEvent_entityCrouch]: ...
    @overload
    def on(
        self, event: Literal["entityUncrouch"]
    ) -> Callable[[_OnEvent_entityUncrouch], _OnEvent_entityUncrouch]: ...
    @overload
    def on(
        self, event: Literal["entityEquip"]
    ) -> Callable[[_OnEvent_entityEquip], _OnEvent_entityEquip]: ...
    @overload
    def on(
        self, event: Literal["entitySleep"]
    ) -> Callable[[_OnEvent_entitySleep], _OnEvent_entitySleep]: ...
    @overload
    def on(
        self, event: Literal["entitySpawn"]
    ) -> Callable[[_OnEvent_entitySpawn], _OnEvent_entitySpawn]: ...
    @overload
    def on(
        self, event: Literal["entityElytraFlew"]
    ) -> Callable[[_OnEvent_entityElytraFlew], _OnEvent_entityElytraFlew]: ...
    @overload
    def on(
        self, event: Literal["usedFirework"]
    ) -> Callable[[_OnEvent_usedFirework], _OnEvent_usedFirework]: ...
    @overload
    def on(
        self, event: Literal["itemDrop"]
    ) -> Callable[[_OnEvent_itemDrop], _OnEvent_itemDrop]: ...
    @overload
    def on(
        self, event: Literal["playerCollect"]
    ) -> Callable[[_OnEvent_playerCollect], _OnEvent_playerCollect]: ...
    @overload
    def on(
        self, event: Literal["entityAttributes"]
    ) -> Callable[[_OnEvent_entityAttributes], _OnEvent_entityAttributes]: ...
    @overload
    def on(
        self, event: Literal["entityGone"]
    ) -> Callable[[_OnEvent_entityGone], _OnEvent_entityGone]: ...
    @overload
    def on(
        self, event: Literal["entityMoved"]
    ) -> Callable[[_OnEvent_entityMoved], _OnEvent_entityMoved]: ...
    @overload
    def on(
        self, event: Literal["entityDetach"]
    ) -> Callable[[_OnEvent_entityDetach], _OnEvent_entityDetach]: ...
    @overload
    def on(
        self, event: Literal["entityAttach"]
    ) -> Callable[[_OnEvent_entityAttach], _OnEvent_entityAttach]: ...
    @overload
    def on(
        self, event: Literal["entityUpdate"]
    ) -> Callable[[_OnEvent_entityUpdate], _OnEvent_entityUpdate]: ...
    @overload
    def on(
        self, event: Literal["entityEffect"]
    ) -> Callable[[_OnEvent_entityEffect], _OnEvent_entityEffect]: ...
    @overload
    def on(
        self, event: Literal["entityEffectEnd"]
    ) -> Callable[[_OnEvent_entityEffectEnd], _OnEvent_entityEffectEnd]: ...
    @overload
    def on(
        self, event: Literal["playerJoined"]
    ) -> Callable[[_OnEvent_playerJoined], _OnEvent_playerJoined]: ...
    @overload
    def on(
        self, event: Literal["playerUpdated"]
    ) -> Callable[[_OnEvent_playerUpdated], _OnEvent_playerUpdated]: ...
    @overload
    def on(
        self, event: Literal["playerLeft"]
    ) -> Callable[[_OnEvent_playerLeft], _OnEvent_playerLeft]: ...
    @overload
    def on(
        self, event: Literal["blockUpdate"]
    ) -> Callable[[_OnEvent_blockUpdate], _OnEvent_blockUpdate]: ...
    @overload
    def on(
        self, event: Literal["blockUpdate:(x, y, z)"]
    ) -> Callable[[_OnEvent_blockUpdate__x__y__z_], _OnEvent_blockUpdate__x__y__z_]: ...
    @overload
    def on(
        self, event: Literal["chunkColumnLoad"]
    ) -> Callable[[_OnEvent_chunkColumnLoad], _OnEvent_chunkColumnLoad]: ...
    @overload
    def on(
        self, event: Literal["chunkColumnUnload"]
    ) -> Callable[[_OnEvent_chunkColumnUnload], _OnEvent_chunkColumnUnload]: ...
    @overload
    def on(
        self, event: Literal["soundEffectHeard"]
    ) -> Callable[[_OnEvent_soundEffectHeard], _OnEvent_soundEffectHeard]: ...
    @overload
    def on(
        self, event: Literal["hardcodedSoundEffectHeard"]
    ) -> Callable[
        [_OnEvent_hardcodedSoundEffectHeard], _OnEvent_hardcodedSoundEffectHeard
    ]: ...
    @overload
    def on(
        self, event: Literal["noteHeard"]
    ) -> Callable[[_OnEvent_noteHeard], _OnEvent_noteHeard]: ...
    @overload
    def on(
        self, event: Literal["pistonMove"]
    ) -> Callable[[_OnEvent_pistonMove], _OnEvent_pistonMove]: ...
    @overload
    def on(
        self, event: Literal["chestLidMove"]
    ) -> Callable[[_OnEvent_chestLidMove], _OnEvent_chestLidMove]: ...
    @overload
    def on(
        self, event: Literal["blockBreakProgressObserved"]
    ) -> Callable[
        [_OnEvent_blockBreakProgressObserved], _OnEvent_blockBreakProgressObserved
    ]: ...
    @overload
    def on(
        self, event: Literal["blockBreakProgressEnd"]
    ) -> Callable[[_OnEvent_blockBreakProgressEnd], _OnEvent_blockBreakProgressEnd]: ...
    @overload
    def on(
        self, event: Literal["diggingCompleted"]
    ) -> Callable[[_OnEvent_diggingCompleted], _OnEvent_diggingCompleted]: ...
    @overload
    def on(
        self, event: Literal["diggingAborted"]
    ) -> Callable[[_OnEvent_diggingAborted], _OnEvent_diggingAborted]: ...
    @overload
    def on(
        self, event: Literal["move"]
    ) -> Callable[[_OnEvent_move], _OnEvent_move]: ...
    @overload
    def on(
        self, event: Literal["forcedMove"]
    ) -> Callable[[_OnEvent_forcedMove], _OnEvent_forcedMove]: ...
    @overload
    def on(
        self, event: Literal["mount"]
    ) -> Callable[[_OnEvent_mount], _OnEvent_mount]: ...
    @overload
    def on(
        self, event: Literal["dismount"]
    ) -> Callable[[_OnEvent_dismount], _OnEvent_dismount]: ...
    @overload
    def on(
        self, event: Literal["windowOpen"]
    ) -> Callable[[_OnEvent_windowOpen], _OnEvent_windowOpen]: ...
    @overload
    def on(
        self, event: Literal["windowClose"]
    ) -> Callable[[_OnEvent_windowClose], _OnEvent_windowClose]: ...
    @overload
    def on(
        self, event: Literal["sleep"]
    ) -> Callable[[_OnEvent_sleep], _OnEvent_sleep]: ...
    @overload
    def on(
        self, event: Literal["wake"]
    ) -> Callable[[_OnEvent_wake], _OnEvent_wake]: ...
    @overload
    def on(
        self, event: Literal["experience"]
    ) -> Callable[[_OnEvent_experience], _OnEvent_experience]: ...
    @overload
    def on(
        self, event: Literal["physicsTick"]
    ) -> Callable[[_OnEvent_physicsTick], _OnEvent_physicsTick]: ...
    @overload
    def on(
        self, event: Literal["physicTick"]
    ) -> Callable[[_OnEvent_physicTick], _OnEvent_physicTick]: ...
    @overload
    def on(
        self, event: Literal["scoreboardCreated"]
    ) -> Callable[[_OnEvent_scoreboardCreated], _OnEvent_scoreboardCreated]: ...
    @overload
    def on(
        self, event: Literal["scoreboardDeleted"]
    ) -> Callable[[_OnEvent_scoreboardDeleted], _OnEvent_scoreboardDeleted]: ...
    @overload
    def on(
        self, event: Literal["scoreboardTitleChanged"]
    ) -> Callable[
        [_OnEvent_scoreboardTitleChanged], _OnEvent_scoreboardTitleChanged
    ]: ...
    @overload
    def on(
        self, event: Literal["scoreUpdated"]
    ) -> Callable[[_OnEvent_scoreUpdated], _OnEvent_scoreUpdated]: ...
    @overload
    def on(
        self, event: Literal["scoreRemoved"]
    ) -> Callable[[_OnEvent_scoreRemoved], _OnEvent_scoreRemoved]: ...
    @overload
    def on(
        self, event: Literal["scoreboardPosition"]
    ) -> Callable[[_OnEvent_scoreboardPosition], _OnEvent_scoreboardPosition]: ...
    @overload
    def on(
        self, event: Literal["teamCreated"]
    ) -> Callable[[_OnEvent_teamCreated], _OnEvent_teamCreated]: ...
    @overload
    def on(
        self, event: Literal["teamRemoved"]
    ) -> Callable[[_OnEvent_teamRemoved], _OnEvent_teamRemoved]: ...
    @overload
    def on(
        self, event: Literal["teamUpdated"]
    ) -> Callable[[_OnEvent_teamUpdated], _OnEvent_teamUpdated]: ...
    @overload
    def on(
        self, event: Literal["teamMemberAdded"]
    ) -> Callable[[_OnEvent_teamMemberAdded], _OnEvent_teamMemberAdded]: ...
    @overload
    def on(
        self, event: Literal["teamMemberRemoved"]
    ) -> Callable[[_OnEvent_teamMemberRemoved], _OnEvent_teamMemberRemoved]: ...
    @overload
    def on(
        self, event: Literal["bossBarCreated"]
    ) -> Callable[[_OnEvent_bossBarCreated], _OnEvent_bossBarCreated]: ...
    @overload
    def on(
        self, event: Literal["bossBarDeleted"]
    ) -> Callable[[_OnEvent_bossBarDeleted], _OnEvent_bossBarDeleted]: ...
    @overload
    def on(
        self, event: Literal["bossBarUpdated"]
    ) -> Callable[[_OnEvent_bossBarUpdated], _OnEvent_bossBarUpdated]: ...
    @overload
    def on(
        self, event: Literal["resourcePack"]
    ) -> Callable[[_OnEvent_resourcePack], _OnEvent_resourcePack]: ...
    @overload
    def on(
        self, event: Literal["particle"]
    ) -> Callable[[_OnEvent_particle], _OnEvent_particle]: ...
    @overload
    def once(
        self, event: Literal["chat"]
    ) -> Callable[[_OnEvent_chat], _OnEvent_chat]: ...
    @overload
    def once(
        self, event: Literal["whisper"]
    ) -> Callable[[_OnEvent_whisper], _OnEvent_whisper]: ...
    @overload
    def once(
        self, event: Literal["actionBar"]
    ) -> Callable[[_OnEvent_actionBar], _OnEvent_actionBar]: ...
    @overload
    def once(
        self, event: Literal["error"]
    ) -> Callable[[_OnEvent_error], _OnEvent_error]: ...
    @overload
    def once(
        self, event: Literal["message"]
    ) -> Callable[[_OnEvent_message], _OnEvent_message]: ...
    @overload
    def once(
        self, event: Literal["messagestr"]
    ) -> Callable[[_OnEvent_messagestr], _OnEvent_messagestr]: ...
    @overload
    def once(
        self, event: Literal["unmatchedMessage"]
    ) -> Callable[[_OnEvent_unmatchedMessage], _OnEvent_unmatchedMessage]: ...
    @overload
    def once(
        self, event: Literal["inject_allowed"]
    ) -> Callable[[_OnEvent_inject_allowed], _OnEvent_inject_allowed]: ...
    @overload
    def once(
        self, event: Literal["login"]
    ) -> Callable[[_OnEvent_login], _OnEvent_login]: ...
    @overload
    def once(
        self, event: Literal["spawn"]
    ) -> Callable[[_OnEvent_spawn], _OnEvent_spawn]: ...
    @overload
    def once(
        self, event: Literal["respawn"]
    ) -> Callable[[_OnEvent_respawn], _OnEvent_respawn]: ...
    @overload
    def once(
        self, event: Literal["game"]
    ) -> Callable[[_OnEvent_game], _OnEvent_game]: ...
    @overload
    def once(
        self, event: Literal["title"]
    ) -> Callable[[_OnEvent_title], _OnEvent_title]: ...
    @overload
    def once(
        self, event: Literal["rain"]
    ) -> Callable[[_OnEvent_rain], _OnEvent_rain]: ...
    @overload
    def once(
        self, event: Literal["time"]
    ) -> Callable[[_OnEvent_time], _OnEvent_time]: ...
    @overload
    def once(
        self, event: Literal["kicked"]
    ) -> Callable[[_OnEvent_kicked], _OnEvent_kicked]: ...
    @overload
    def once(self, event: Literal["end"]) -> Callable[[_OnEvent_end], _OnEvent_end]: ...
    @overload
    def once(
        self, event: Literal["spawnReset"]
    ) -> Callable[[_OnEvent_spawnReset], _OnEvent_spawnReset]: ...
    @overload
    def once(
        self, event: Literal["death"]
    ) -> Callable[[_OnEvent_death], _OnEvent_death]: ...
    @overload
    def once(
        self, event: Literal["health"]
    ) -> Callable[[_OnEvent_health], _OnEvent_health]: ...
    @overload
    def once(
        self, event: Literal["breath"]
    ) -> Callable[[_OnEvent_breath], _OnEvent_breath]: ...
    @overload
    def once(
        self, event: Literal["entitySwingArm"]
    ) -> Callable[[_OnEvent_entitySwingArm], _OnEvent_entitySwingArm]: ...
    @overload
    def once(
        self, event: Literal["entityHurt"]
    ) -> Callable[[_OnEvent_entityHurt], _OnEvent_entityHurt]: ...
    @overload
    def once(
        self, event: Literal["entityDead"]
    ) -> Callable[[_OnEvent_entityDead], _OnEvent_entityDead]: ...
    @overload
    def once(
        self, event: Literal["entityTaming"]
    ) -> Callable[[_OnEvent_entityTaming], _OnEvent_entityTaming]: ...
    @overload
    def once(
        self, event: Literal["entityTamed"]
    ) -> Callable[[_OnEvent_entityTamed], _OnEvent_entityTamed]: ...
    @overload
    def once(
        self, event: Literal["entityShakingOffWater"]
    ) -> Callable[[_OnEvent_entityShakingOffWater], _OnEvent_entityShakingOffWater]: ...
    @overload
    def once(
        self, event: Literal["entityEatingGrass"]
    ) -> Callable[[_OnEvent_entityEatingGrass], _OnEvent_entityEatingGrass]: ...
    @overload
    def once(
        self, event: Literal["entityHandSwap"]
    ) -> Callable[[_OnEvent_entityHandSwap], _OnEvent_entityHandSwap]: ...
    @overload
    def once(
        self, event: Literal["entityWake"]
    ) -> Callable[[_OnEvent_entityWake], _OnEvent_entityWake]: ...
    @overload
    def once(
        self, event: Literal["entityEat"]
    ) -> Callable[[_OnEvent_entityEat], _OnEvent_entityEat]: ...
    @overload
    def once(
        self, event: Literal["entityCriticalEffect"]
    ) -> Callable[[_OnEvent_entityCriticalEffect], _OnEvent_entityCriticalEffect]: ...
    @overload
    def once(
        self, event: Literal["entityMagicCriticalEffect"]
    ) -> Callable[
        [_OnEvent_entityMagicCriticalEffect], _OnEvent_entityMagicCriticalEffect
    ]: ...
    @overload
    def once(
        self, event: Literal["entityCrouch"]
    ) -> Callable[[_OnEvent_entityCrouch], _OnEvent_entityCrouch]: ...
    @overload
    def once(
        self, event: Literal["entityUncrouch"]
    ) -> Callable[[_OnEvent_entityUncrouch], _OnEvent_entityUncrouch]: ...
    @overload
    def once(
        self, event: Literal["entityEquip"]
    ) -> Callable[[_OnEvent_entityEquip], _OnEvent_entityEquip]: ...
    @overload
    def once(
        self, event: Literal["entitySleep"]
    ) -> Callable[[_OnEvent_entitySleep], _OnEvent_entitySleep]: ...
    @overload
    def once(
        self, event: Literal["entitySpawn"]
    ) -> Callable[[_OnEvent_entitySpawn], _OnEvent_entitySpawn]: ...
    @overload
    def once(
        self, event: Literal["entityElytraFlew"]
    ) -> Callable[[_OnEvent_entityElytraFlew], _OnEvent_entityElytraFlew]: ...
    @overload
    def once(
        self, event: Literal["usedFirework"]
    ) -> Callable[[_OnEvent_usedFirework], _OnEvent_usedFirework]: ...
    @overload
    def once(
        self, event: Literal["itemDrop"]
    ) -> Callable[[_OnEvent_itemDrop], _OnEvent_itemDrop]: ...
    @overload
    def once(
        self, event: Literal["playerCollect"]
    ) -> Callable[[_OnEvent_playerCollect], _OnEvent_playerCollect]: ...
    @overload
    def once(
        self, event: Literal["entityAttributes"]
    ) -> Callable[[_OnEvent_entityAttributes], _OnEvent_entityAttributes]: ...
    @overload
    def once(
        self, event: Literal["entityGone"]
    ) -> Callable[[_OnEvent_entityGone], _OnEvent_entityGone]: ...
    @overload
    def once(
        self, event: Literal["entityMoved"]
    ) -> Callable[[_OnEvent_entityMoved], _OnEvent_entityMoved]: ...
    @overload
    def once(
        self, event: Literal["entityDetach"]
    ) -> Callable[[_OnEvent_entityDetach], _OnEvent_entityDetach]: ...
    @overload
    def once(
        self, event: Literal["entityAttach"]
    ) -> Callable[[_OnEvent_entityAttach], _OnEvent_entityAttach]: ...
    @overload
    def once(
        self, event: Literal["entityUpdate"]
    ) -> Callable[[_OnEvent_entityUpdate], _OnEvent_entityUpdate]: ...
    @overload
    def once(
        self, event: Literal["entityEffect"]
    ) -> Callable[[_OnEvent_entityEffect], _OnEvent_entityEffect]: ...
    @overload
    def once(
        self, event: Literal["entityEffectEnd"]
    ) -> Callable[[_OnEvent_entityEffectEnd], _OnEvent_entityEffectEnd]: ...
    @overload
    def once(
        self, event: Literal["playerJoined"]
    ) -> Callable[[_OnEvent_playerJoined], _OnEvent_playerJoined]: ...
    @overload
    def once(
        self, event: Literal["playerUpdated"]
    ) -> Callable[[_OnEvent_playerUpdated], _OnEvent_playerUpdated]: ...
    @overload
    def once(
        self, event: Literal["playerLeft"]
    ) -> Callable[[_OnEvent_playerLeft], _OnEvent_playerLeft]: ...
    @overload
    def once(
        self, event: Literal["blockUpdate"]
    ) -> Callable[[_OnEvent_blockUpdate], _OnEvent_blockUpdate]: ...
    @overload
    def once(
        self, event: Literal["blockUpdate:(x, y, z)"]
    ) -> Callable[[_OnEvent_blockUpdate__x__y__z_], _OnEvent_blockUpdate__x__y__z_]: ...
    @overload
    def once(
        self, event: Literal["chunkColumnLoad"]
    ) -> Callable[[_OnEvent_chunkColumnLoad], _OnEvent_chunkColumnLoad]: ...
    @overload
    def once(
        self, event: Literal["chunkColumnUnload"]
    ) -> Callable[[_OnEvent_chunkColumnUnload], _OnEvent_chunkColumnUnload]: ...
    @overload
    def once(
        self, event: Literal["soundEffectHeard"]
    ) -> Callable[[_OnEvent_soundEffectHeard], _OnEvent_soundEffectHeard]: ...
    @overload
    def once(
        self, event: Literal["hardcodedSoundEffectHeard"]
    ) -> Callable[
        [_OnEvent_hardcodedSoundEffectHeard], _OnEvent_hardcodedSoundEffectHeard
    ]: ...
    @overload
    def once(
        self, event: Literal["noteHeard"]
    ) -> Callable[[_OnEvent_noteHeard], _OnEvent_noteHeard]: ...
    @overload
    def once(
        self, event: Literal["pistonMove"]
    ) -> Callable[[_OnEvent_pistonMove], _OnEvent_pistonMove]: ...
    @overload
    def once(
        self, event: Literal["chestLidMove"]
    ) -> Callable[[_OnEvent_chestLidMove], _OnEvent_chestLidMove]: ...
    @overload
    def once(
        self, event: Literal["blockBreakProgressObserved"]
    ) -> Callable[
        [_OnEvent_blockBreakProgressObserved], _OnEvent_blockBreakProgressObserved
    ]: ...
    @overload
    def once(
        self, event: Literal["blockBreakProgressEnd"]
    ) -> Callable[[_OnEvent_blockBreakProgressEnd], _OnEvent_blockBreakProgressEnd]: ...
    @overload
    def once(
        self, event: Literal["diggingCompleted"]
    ) -> Callable[[_OnEvent_diggingCompleted], _OnEvent_diggingCompleted]: ...
    @overload
    def once(
        self, event: Literal["diggingAborted"]
    ) -> Callable[[_OnEvent_diggingAborted], _OnEvent_diggingAborted]: ...
    @overload
    def once(
        self, event: Literal["move"]
    ) -> Callable[[_OnEvent_move], _OnEvent_move]: ...
    @overload
    def once(
        self, event: Literal["forcedMove"]
    ) -> Callable[[_OnEvent_forcedMove], _OnEvent_forcedMove]: ...
    @overload
    def once(
        self, event: Literal["mount"]
    ) -> Callable[[_OnEvent_mount], _OnEvent_mount]: ...
    @overload
    def once(
        self, event: Literal["dismount"]
    ) -> Callable[[_OnEvent_dismount], _OnEvent_dismount]: ...
    @overload
    def once(
        self, event: Literal["windowOpen"]
    ) -> Callable[[_OnEvent_windowOpen], _OnEvent_windowOpen]: ...
    @overload
    def once(
        self, event: Literal["windowClose"]
    ) -> Callable[[_OnEvent_windowClose], _OnEvent_windowClose]: ...
    @overload
    def once(
        self, event: Literal["sleep"]
    ) -> Callable[[_OnEvent_sleep], _OnEvent_sleep]: ...
    @overload
    def once(
        self, event: Literal["wake"]
    ) -> Callable[[_OnEvent_wake], _OnEvent_wake]: ...
    @overload
    def once(
        self, event: Literal["experience"]
    ) -> Callable[[_OnEvent_experience], _OnEvent_experience]: ...
    @overload
    def once(
        self, event: Literal["physicsTick"]
    ) -> Callable[[_OnEvent_physicsTick], _OnEvent_physicsTick]: ...
    @overload
    def once(
        self, event: Literal["physicTick"]
    ) -> Callable[[_OnEvent_physicTick], _OnEvent_physicTick]: ...
    @overload
    def once(
        self, event: Literal["scoreboardCreated"]
    ) -> Callable[[_OnEvent_scoreboardCreated], _OnEvent_scoreboardCreated]: ...
    @overload
    def once(
        self, event: Literal["scoreboardDeleted"]
    ) -> Callable[[_OnEvent_scoreboardDeleted], _OnEvent_scoreboardDeleted]: ...
    @overload
    def once(
        self, event: Literal["scoreboardTitleChanged"]
    ) -> Callable[
        [_OnEvent_scoreboardTitleChanged], _OnEvent_scoreboardTitleChanged
    ]: ...
    @overload
    def once(
        self, event: Literal["scoreUpdated"]
    ) -> Callable[[_OnEvent_scoreUpdated], _OnEvent_scoreUpdated]: ...
    @overload
    def once(
        self, event: Literal["scoreRemoved"]
    ) -> Callable[[_OnEvent_scoreRemoved], _OnEvent_scoreRemoved]: ...
    @overload
    def once(
        self, event: Literal["scoreboardPosition"]
    ) -> Callable[[_OnEvent_scoreboardPosition], _OnEvent_scoreboardPosition]: ...
    @overload
    def once(
        self, event: Literal["teamCreated"]
    ) -> Callable[[_OnEvent_teamCreated], _OnEvent_teamCreated]: ...
    @overload
    def once(
        self, event: Literal["teamRemoved"]
    ) -> Callable[[_OnEvent_teamRemoved], _OnEvent_teamRemoved]: ...
    @overload
    def once(
        self, event: Literal["teamUpdated"]
    ) -> Callable[[_OnEvent_teamUpdated], _OnEvent_teamUpdated]: ...
    @overload
    def once(
        self, event: Literal["teamMemberAdded"]
    ) -> Callable[[_OnEvent_teamMemberAdded], _OnEvent_teamMemberAdded]: ...
    @overload
    def once(
        self, event: Literal["teamMemberRemoved"]
    ) -> Callable[[_OnEvent_teamMemberRemoved], _OnEvent_teamMemberRemoved]: ...
    @overload
    def once(
        self, event: Literal["bossBarCreated"]
    ) -> Callable[[_OnEvent_bossBarCreated], _OnEvent_bossBarCreated]: ...
    @overload
    def once(
        self, event: Literal["bossBarDeleted"]
    ) -> Callable[[_OnEvent_bossBarDeleted], _OnEvent_bossBarDeleted]: ...
    @overload
    def once(
        self, event: Literal["bossBarUpdated"]
    ) -> Callable[[_OnEvent_bossBarUpdated], _OnEvent_bossBarUpdated]: ...
    @overload
    def once(
        self, event: Literal["resourcePack"]
    ) -> Callable[[_OnEvent_resourcePack], _OnEvent_resourcePack]: ...
    @overload
    def once(
        self, event: Literal["particle"]
    ) -> Callable[[_OnEvent_particle], _OnEvent_particle]: ...
    def run_forever(self) -> None: ...

def create_bot(**options: object) -> Bot: ...
