"""Generate src/minethon/bot.pyi from mineflayer's index.d.ts.

Strategy:
- `Bot` / `BotEvents` / `BotOptions` / mineflayer's aux interfaces are parsed
  out of `index.d.ts` and mechanically converted to Python type stubs.
- External dependencies that mineflayer imports (`vec3`, `prismarine-entity`,
  `prismarine-block`, `prismarine-item`, `prismarine-chat`,
  `prismarine-windows`, `prismarine-recipe`) have their own `.d.ts` files,
  which we parse alongside mineflayer's and inline the relevant classes as
  Python Protocols. Nothing is invented — each definition traces back to a
  TypeScript source.

The generator handles the subset of TypeScript syntax used by these files:
primitives, unions, arrays, mapped dict types, function types, `Promise<T>`
(stripped → sync return), object types, and `Literal` unions. Unsupported
constructs fall through as `object` with a comment.

Run: uv run python scripts/generate_stubs.py
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DTS_ROOT = REPO_ROOT / "src/mineflayer/js/node_modules"
MF_INDEX = DTS_ROOT / "mineflayer/index.d.ts"
OUT_PATH = REPO_ROOT / "src/minethon/bot.pyi"


# --------------------------------------------------------------------------- #
#  TypeScript → Python type conversion
# --------------------------------------------------------------------------- #


TS_PRIMITIVES = {
    "string": "str",
    "number": "float",
    "boolean": "bool",
    "void": "None",
    "null": "None",
    "undefined": "None",
    "any": "object",
    "unknown": "object",
    "bigint": "int",
    "BigInt": "int",
    "object": "object",
    "Object": "object",
    "Function": "Callable[..., object]",
    "Buffer": "bytes",
    "this": "Self",
    "Error": "Exception",
    "RegExp": "object",
    "Date": "object",
    # TS types we don't fully model — treat as opaque
    "NBT": "object",
    "ClientOptions": "object",
    "Client": "object",
    "Registry": "object",
    "IndexedData": "object",
    "ScoreBoard": "object",
    "Team": "object",
    "BossBar": "object",
    "Particle": "object",
    "DisplaySlot": "str",
    "SkinData": "object",
    "ChatPattern": "object",
    "GameSettings": "object",
    "PluginOptions": "dict[str, object]",
    "Plugin": "Callable[..., object]",
}

# Re-exported name overrides
TS_NAME_REMAP = {
    "TypedEmitter": "object",  # TS utility; irrelevant for Python stubs
}


def split_top_level(text: str, sep: str) -> list[str]:
    """Split `text` by `sep`, skipping occurrences inside <>, {}, (), [] groups."""
    depth = {"<": 0, "{": 0, "(": 0, "[": 0}
    pairs = {">": "<", "}": "{", ")": "(", "]": "["}
    parts: list[str] = []
    buf = []
    for ch in text:
        if ch in depth:
            depth[ch] += 1
        elif ch in pairs:
            depth[pairs[ch]] = max(0, depth[pairs[ch]] - 1)
        at_top = all(v == 0 for v in depth.values())
        if ch == sep and at_top:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf).strip())
    return [p for p in parts if p]


def ts_to_py(ts: str) -> str:
    """Convert a TypeScript type expression to a Python type expression."""
    ts = ts.strip()
    if not ts:
        return "object"

    # Strip surrounding parens: (T) → T, but only if they wrap the whole thing
    while ts.startswith("(") and ts.endswith(")"):
        inner = ts[1:-1]
        if _balanced(inner):
            ts = inner.strip()
        else:
            break

    # Function type: (args) => R
    fn_match = re.match(r"^\((.*)\)\s*=>\s*(.+)$", ts, re.DOTALL)
    if fn_match:
        args_str, ret_str = fn_match.groups()
        arg_parts = split_top_level(args_str, ",") if args_str.strip() else []
        py_args: list[str] = []
        for arg in arg_parts:
            # Drop rest-spread marker
            arg = arg.lstrip(".").strip()
            # Pull off name?: type or name: type
            m = re.match(r"^(\w+)(\?)?\s*:\s*(.+)$", arg)
            if m:
                _, opt, type_str = m.groups()
                py = ts_to_py(type_str)
                if opt and py != "None":
                    py = f"{py} | None"
                py_args.append(py)
            else:
                py_args.append(ts_to_py(arg))
        ret_py = ts_to_py(ret_str)
        if not py_args:
            return f"Callable[[], {ret_py}]"
        return f"Callable[[{', '.join(py_args)}], {ret_py}]"

    # Intersection A & B — use first part (best-effort)
    if "&" in ts and _no_generic_ampersand(ts):
        parts = split_top_level(ts, "&")
        if parts and parts[0] != ts:
            return ts_to_py(parts[0])

    # Union
    union_parts = split_top_level(ts, "|")
    if len(union_parts) > 1:
        # Literal detection
        if all(_is_literal_token(p) for p in union_parts):
            return f"Literal[{', '.join(union_parts)}]"
        py_parts = [ts_to_py(p) for p in union_parts]
        # Deduplicate while preserving order
        seen = []
        for p in py_parts:
            if p not in seen:
                seen.append(p)
        # Move None to the end
        if "None" in seen:
            seen = [p for p in seen if p != "None"] + ["None"]
        return " | ".join(seen)

    # Array: T[]
    arr_match = re.match(r"^(.+)\[\]$", ts)
    if arr_match and _balanced(arr_match.group(1)):
        return f"list[{ts_to_py(arr_match.group(1))}]"

    # Tuple: [A, B, C]
    if ts.startswith("[") and ts.endswith("]"):
        inner = ts[1:-1]
        if _balanced(inner):
            parts = split_top_level(inner, ",")
            py = [ts_to_py(p) for p in parts]
            return f"tuple[{', '.join(py)}]"

    # Array<T>
    arr_g = re.match(r"^Array<(.+)>$", ts)
    if arr_g:
        return f"list[{ts_to_py(arr_g.group(1))}]"

    # Promise<T> — strip, sync return
    prom = re.match(r"^Promise<(.+)>$", ts)
    if prom:
        return ts_to_py(prom.group(1))

    # Partial<T> → T (loose)
    part = re.match(r"^Partial<(.+)>$", ts)
    if part:
        return ts_to_py(part.group(1))

    # Readonly<T> → T
    ro = re.match(r"^Readonly<(.+)>$", ts)
    if ro:
        return ts_to_py(ro.group(1))

    # Mapped dict type: { [k: string]: V } or { [K in Foo]: V }
    map_m = re.match(
        r"^\{\s*\[\s*\w+\s*(?::\s*\w+|\s+in\s+\w+)\s*\]\s*:\s*(.+?)\s*,?\s*\}$",
        ts,
        re.DOTALL,
    )
    if map_m:
        return f"dict[str, {ts_to_py(map_m.group(1))}]"

    # Literal primitives
    if re.match(r"^'[^']*'$", ts):
        return f"Literal[{ts}]"
    if re.match(r"^\"[^\"]*\"$", ts):
        return f"Literal[{ts}]"
    if re.match(r"^-?\d+(\.\d+)?$", ts):
        return f"Literal[{ts}]"
    if ts in ("true", "false"):
        return f"Literal[{ts.capitalize()}]"

    # Generic ref: Foo<T, U> — drop generic params
    gen = re.match(r"^([A-Za-z_]\w*)<.+>$", ts)
    if gen:
        return TS_NAME_REMAP.get(gen.group(1), gen.group(1))

    # Known primitive / remapped name
    if ts in TS_PRIMITIVES:
        return TS_PRIMITIVES[ts]
    if ts in TS_NAME_REMAP:
        return TS_NAME_REMAP[ts]

    # Keyof / typeof / other exotic — fall back to object
    if ts.startswith(("keyof ", "typeof ")):
        return "object"

    # Class / interface reference: keep the name as-is
    if re.match(r"^[A-Za-z_]\w*$", ts):
        return ts

    # Unknown — fall back to object
    return "object"


def _balanced(text: str) -> bool:
    return all(
        text.count(a) == text.count(b)
        for a, b in [("<", ">"), ("(", ")"), ("[", "]"), ("{", "}")]
    )


def _is_literal_token(token: str) -> bool:
    token = token.strip()
    if re.match(r"^'[^']*'$", token):
        return True
    if re.match(r"^\"[^\"]*\"$", token):
        return True
    if re.match(r"^-?\d+(\.\d+)?$", token):
        return True
    return False


def _no_generic_ampersand(ts: str) -> bool:
    # Naive: treat `&` outside <> / () as intersection
    depth = 0
    for ch in ts:
        if ch in "<({[":
            depth += 1
        elif ch in ">)}]":
            depth = max(0, depth - 1)
        elif ch == "&" and depth == 0:
            return True
    return False


# --------------------------------------------------------------------------- #
#  .d.ts block parsing
# --------------------------------------------------------------------------- #


@dataclass
class Member:
    name: str
    ts_type: str
    optional: bool = False
    is_method: bool = False
    params: str = ""  # Raw arg list for methods
    returns: str = "void"


@dataclass
class InterfaceBlock:
    name: str
    extends: list[str] = field(default_factory=list)
    members: list[Member] = field(default_factory=list)


def strip_ts_comments(text: str) -> str:
    """Remove `/* ... */` and `//` comments from TS source."""
    # Block comments
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    # Line comments (preserve URLs by only stripping from `//` after a column)
    text = re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"(?<=\s)//.*$", "", text, flags=re.MULTILINE)
    return text


def find_interface(text: str, name: str) -> str | None:
    """Extract the body of `export interface NAME { ... }` (balanced braces)."""
    pattern = rf"export\s+interface\s+{re.escape(name)}\b[^{{]*\{{"
    m = re.search(pattern, text)
    if not m:
        return None
    start = m.end()  # Position after opening brace
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i]
        i += 1
    return None


def find_interface_extends(text: str, name: str) -> list[str]:
    pattern = rf"export\s+interface\s+{re.escape(name)}\s+extends\s+([^{{]+)\{{"
    m = re.search(pattern, text)
    if not m:
        return []
    raw = m.group(1).strip()
    # Split by comma, strip generics
    parts = split_top_level(raw, ",")
    out = []
    for p in parts:
        base = re.sub(r"<.*>", "", p).strip()
        if base:
            out.append(base)
    return out


def find_class(text: str, name: str) -> str | None:
    """Extract the body of `export [declare ]class NAME [extends ...] { ... }`."""
    pattern = rf"export\s+(?:declare\s+)?class\s+{re.escape(name)}\b[^{{]*\{{"
    m = re.search(pattern, text)
    if not m:
        return None
    start = m.end()
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i]
        i += 1
    return None


def parse_members(body: str) -> list[Member]:
    """Parse interface/class body into Member list.

    Handles:
    - `name: type` (property)
    - `name?: type` (optional property)
    - `name(args): return` (method)
    - `name?(args): return` (optional method)

    Splits on top-level `;` or newline boundaries.
    """
    # Normalize: drop leading `readonly`, `static`, access modifiers, `get `, `set `, `declare `
    body = body.strip()

    # Members are separated by `;` or newlines; but function types span multiple lines.
    # We scan token-by-token, tracking depth and splitting at top-level `;` or top-level newline
    # that isn't inside a type declaration.

    members: list[Member] = []
    i = 0
    while i < len(body):
        # Skip whitespace / semicolons
        while i < len(body) and body[i] in " \t\n;,":
            i += 1
        if i >= len(body):
            break

        start = i
        depth = 0
        # Scan until top-level `;`, newline at top-level, or end
        while i < len(body):
            ch = body[i]
            if ch in "<({[":
                depth += 1
            elif ch in ">)}]":
                depth = max(0, depth - 1)
            elif ch in ";" and depth == 0:
                break
            elif ch == "\n" and depth == 0:
                # But only treat newline as separator if the next non-space char
                # starts a new member (identifier-ish) or closes the block
                j = i + 1
                while j < len(body) and body[j] in " \t\r":
                    j += 1
                if j >= len(body):
                    break
                # Looks like a new member if next line starts with identifier
                if re.match(r"[A-Za-z_]|['\"]|\}", body[j]):
                    break
            i += 1

        raw_member = body[start:i].strip()
        if raw_member:
            parsed = _parse_single_member(raw_member)
            if parsed:
                members.append(parsed)
        # Skip the separator
        i += 1
    return members


def _parse_single_member(raw: str) -> Member | None:
    """Parse one member declaration."""
    # Drop modifiers
    raw = re.sub(
        r"^\s*(public|private|protected|readonly|static|declare|get|set)\s+",
        "",
        raw,
    )
    raw = raw.strip()
    if not raw:
        return None

    # Constructor — skip for our purposes (Python users don't call class constructors
    # directly for these proxies)
    if raw.startswith("constructor"):
        return None

    # Quoted key: 'foo'(args): ret or 'foo': type
    quoted_match = re.match(r"^(['\"])([^'\"]+)\1\s*(.*)$", raw, re.DOTALL)
    if quoted_match:
        name = quoted_match.group(2)
        rest = quoted_match.group(3).strip()
    else:
        ident_match = re.match(r"^([A-Za-z_]\w*)(\??)(.*)$", raw, re.DOTALL)
        if not ident_match:
            return None
        name = ident_match.group(1)
        opt_mark = ident_match.group(2)
        rest = ident_match.group(3).strip()

    optional = False
    if not quoted_match:
        optional = opt_mark == "?"

    # Method signature: `(args): return` or `(args)`
    if rest.startswith("("):
        # Balance-scan to end of args
        depth = 1
        j = 1
        while j < len(rest) and depth > 0:
            if rest[j] == "(":
                depth += 1
            elif rest[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        args_str = rest[1:j]
        after = rest[j + 1 :].strip()
        if after.startswith(":"):
            returns = after[1:].strip()
        else:
            returns = "void"
        return Member(
            name=name,
            ts_type="",
            optional=optional,
            is_method=True,
            params=args_str,
            returns=returns,
        )

    # Property: `: type`
    if rest.startswith(":"):
        ts_type = rest[1:].strip()
        # Remove trailing comma/semicolon
        ts_type = ts_type.rstrip(",;").strip()
        return Member(name=name, ts_type=ts_type, optional=optional)

    # No match
    return None


def parse_method_args(params: str) -> list[tuple[str, str, bool]]:
    """Parse a TS method argument list → list of (py_name, py_type, has_default)."""
    if not params.strip():
        return []
    parts = split_top_level(params, ",")
    out: list[tuple[str, str, bool]] = []
    for raw in parts:
        raw = raw.strip().lstrip(".").strip()  # strip rest-spread
        m = re.match(r"^(\w+)(\?)?\s*:\s*(.+)$", raw, re.DOTALL)
        if not m:
            # Bare param with no type
            name = raw.split(":", 1)[0].strip().rstrip("?")
            out.append((_py_name(name), "object", False))
            continue
        name, opt, ts_type = m.groups()
        py_type = ts_to_py(ts_type)
        has_default = bool(opt)
        if has_default and "None" not in py_type:
            py_type = f"{py_type} | None"
        out.append((_py_name(name), py_type, has_default))
    return out


def _py_name(name: str) -> str:
    """Keep JS camelCase for arg names (students read .pyi against JS docs)."""
    # Avoid Python reserved words
    if name in {
        "class",
        "def",
        "if",
        "else",
        "for",
        "while",
        "return",
        "from",
        "import",
    }:
        return f"{name}_"
    return name


# --------------------------------------------------------------------------- #
#  External-type Protocol stubs (from vec3 / prismarine-* .d.ts)
# --------------------------------------------------------------------------- #


EXTERNAL_STUBS = '''\
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


EntityType = Literal['player', 'mob', 'object', 'global', 'orb', 'projectile', 'hostile', 'other']


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
    boundingBox: Literal['block', 'empty']
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
'''


# --------------------------------------------------------------------------- #
#  Emission helpers
# --------------------------------------------------------------------------- #


def render_property(member: Member) -> str:
    py_type = ts_to_py(member.ts_type)
    if member.optional and "None" not in py_type:
        py_type = f"{py_type} | None"
    return f"    {member.name}: {py_type}"


def render_method(member: Member) -> str:
    args = parse_method_args(member.params)
    ret_py = ts_to_py(member.returns)
    parts = ["self"]
    for name, py_type, has_default in args:
        default = " = ..." if has_default else ""
        parts.append(f"{name}: {py_type}{default}")
    return f"    def {member.name}({', '.join(parts)}) -> {ret_py}: ..."


def render_interface(name: str, body: str) -> list[str]:
    """Render a mineflayer interface body as a Python class."""
    members = parse_members(body)
    lines = [f"class {name}:"]
    lines.append(f'    """Ref: mineflayer/index.d.ts — {name}"""')
    if not members:
        lines.append("    pass")
        return lines
    for m in members:
        if m.is_method:
            lines.append(render_method(m))
        else:
            lines.append(render_property(m))
    return lines


def render_type_alias(name: str, ts_expr: str) -> str:
    py = ts_to_py(ts_expr)
    return f"{name} = {py}"


# --------------------------------------------------------------------------- #
#  Event-specific rendering
# --------------------------------------------------------------------------- #


def render_bot_events(events_body: str) -> tuple[list[str], list[tuple[str, str]]]:
    """Parse BotEvents body, emit callback type aliases + return [(event, alias)]."""
    members = parse_members(events_body)
    lines: list[str] = ["# --- Event callback type aliases ---"]
    event_callbacks: list[tuple[str, str]] = []
    for m in members:
        if not m.is_method and not m.ts_type:
            continue
        # Each event is declared as a property whose type is a function:
        # `chat: (username: string, message: string, ...) => Promise<void> | void`
        # But our parse_members may emit it as `is_method=True` if we catch the "("...
        # Fix: events body member either has ts_type starting with "(" OR is_method due
        # to our argument-list detection.
        if m.is_method:
            # Build a Callable from params + returns
            args = parse_method_args(m.params)
            ret_py = ts_to_py(m.returns)
            py_args = [py for _, py, _ in args]
            cb_type = (
                f"Callable[[{', '.join(py_args)}], {ret_py}]"
                if py_args
                else f"Callable[[], {ret_py}]"
            )
        else:
            cb_type = ts_to_py(m.ts_type)
        alias = f"_OnEvent_{_sanitize_alias(m.name)}"
        lines.append(f"{alias} = {cb_type}")
        event_callbacks.append((m.name, alias))
    return lines, event_callbacks


def _sanitize_alias(name: str) -> str:
    """Event names like 'blockUpdate:(x, y, z)' → identifier-safe."""
    return re.sub(r"\W", "_", name)


def render_on_overloads(
    event_callbacks: list[tuple[str, str]], method: str
) -> list[str]:
    """Emit @overload defs for `on` or `once`."""
    lines: list[str] = []
    for event, alias in event_callbacks:
        lines.append("    @overload")
        lines.append(
            f'    def {method}(self, event: Literal["{event}"]) -> '
            f"Callable[[{alias}], {alias}]: ..."
        )
    # No `event: str` fallback on purpose — forces students to use a known event
    # name and get IDE completion. Custom events from plugins should go through
    # `bot.raw.on(...)` (reserved for a future raw escape hatch).
    return lines


# --------------------------------------------------------------------------- #
#  Bot rendering
# --------------------------------------------------------------------------- #


def render_bot(bot_body: str, event_callbacks: list[tuple[str, str]]) -> list[str]:
    members = parse_members(bot_body)
    lines = ["class Bot:"]
    lines.append(
        '    """Pythonic façade over a mineflayer Bot proxy.\n\n'
        "    Every property and method below mirrors mineflayer's Bot interface.\n\n"
        '    Ref: mineflayer/index.d.ts — interface Bot\n    """'
    )
    # Skip private `_client` field (exposed as raw JS only)
    for m in members:
        if m.name.startswith("_"):
            continue
        if m.is_method:
            lines.append(render_method(m))
        else:
            lines.append(render_property(m))

    # Event overloads
    lines.append("")
    lines.append("    # --- Typed event overloads (generated from BotEvents) ---")
    lines.extend(render_on_overloads(event_callbacks, "on"))
    lines.append("")
    lines.extend(render_on_overloads(event_callbacks, "once"))
    lines.append("")
    # run_forever — defined in runtime but we surface it in the stub
    lines.append("    def run_forever(self) -> None: ...")
    return lines


# --------------------------------------------------------------------------- #
#  Options & createBot
# --------------------------------------------------------------------------- #


def render_bot_options(body: str) -> list[str]:
    """BotOptions → TypedDict (total=False since most are optional)."""
    members = parse_members(body)
    lines = ["class BotOptions(TypedDict, total=False):"]
    lines.append(
        '    """Options accepted by `create_bot(**opts)`.\n\n'
        '    Ref: mineflayer/index.d.ts — interface BotOptions\n    """'
    )
    # minecraft-protocol ClientOptions (merged in) — surface the common fields
    extras = [
        Member(name="host", ts_type="string"),
        Member(name="port", ts_type="number"),
        Member(name="username", ts_type="string"),
        Member(name="password", ts_type="string", optional=True),
        Member(name="version", ts_type="string", optional=True),
        Member(
            name="auth", ts_type="'mojang' | 'microsoft' | 'offline'", optional=True
        ),
        Member(name="authServer", ts_type="string", optional=True),
        Member(name="sessionServer", ts_type="string", optional=True),
        Member(name="onMsaCode", ts_type="(data: object) => void", optional=True),
        Member(name="authTitle", ts_type="string", optional=True),
    ]
    # Merge, preferring parsed body entries
    parsed_names = {m.name for m in members}
    for extra in extras:
        if extra.name not in parsed_names:
            members.append(extra)
    for m in members:
        if m.is_method:
            # TypedDict can't hold methods — serialize as callable prop
            continue
        py_type = ts_to_py(m.ts_type)
        lines.append(f"    {m.name}: {py_type}")
    return lines


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #


HEADER = """\
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

"""


# Mineflayer type aliases and aux interfaces we want to emit (selectively)
MINEFLAYER_TYPE_ALIASES = [
    "ChatLevel",
    "ViewDistance",
    "MainHands",
    "LevelType",
    "GameMode",
    "Dimension",
    "Difficulty",
    "ControlState",
    "EquipmentDestination",
]

MINEFLAYER_INTERFACES = [
    "Player",
    "ChatPattern",
    "SkinParts",
    "GameSettings",
    "GameState",
    "Experience",
    "PhysicsOptions",
    "Time",
    "ControlStateStatus",
    "Instrument",
    "FindBlockOptions",
    "TransferOptions",
    "creativeMethods",
    "simpleClick",
    "Tablist",
    "chatPatternOptions",
    "CommandBlockOptions",
    "VillagerTrade",
    "Enchantment",
]

# Classes from mineflayer/index.d.ts we need to expose (Window subclasses)
MINEFLAYER_CLASSES = [
    "Chest",
    "Dispenser",
    "Furnace",
    "EnchantmentTable",
    "Anvil",
    "Villager",
]


def extract_type_alias(text: str, name: str) -> str | None:
    """Pull a one- or multi-line `export type NAME = ...` declaration.

    mineflayer's `.d.ts` doesn't end type aliases with `;`, so we collect
    lines until we hit either a blank line or another top-level declaration.
    """
    lines = text.split("\n")
    start_re = re.compile(rf"^\s*export\s+type\s+{re.escape(name)}\s*=\s*(.*)$")
    for i, line in enumerate(lines):
        m = start_re.match(line)
        if not m:
            continue
        expr = m.group(1).strip()
        j = i + 1
        while j < len(lines):
            nxt = lines[j].strip()
            if not nxt:
                break
            # Stop at the start of the next declaration
            if re.match(
                r"^(export\s+|declare\s+|interface\s+|class\s+|function\s+|type\s+)",
                nxt,
            ):
                break
            # Accept continuation if the current expression is incomplete OR
            # the next line starts with a union / intersection operator.
            if expr.rstrip().endswith(("|", "&", ",", "=", "<")) or nxt.startswith(
                ("|", "&", ",")
            ):
                expr = (expr + " " + nxt).strip()
                j += 1
            else:
                break
        expr = re.sub(r"\s+", " ", expr).rstrip(";").strip()
        return expr
    return None


def main() -> None:
    mf_text = MF_INDEX.read_text()
    mf_text = strip_ts_comments(mf_text)

    out: list[str] = [HEADER, EXTERNAL_STUBS, ""]

    # Type aliases
    out.append("# --- Mineflayer type aliases ---")
    for alias in MINEFLAYER_TYPE_ALIASES:
        expr = extract_type_alias(mf_text, alias)
        if expr is None:
            print(f"warn: type alias {alias} not found", file=sys.stderr)
            continue
        out.append(render_type_alias(alias, expr))
    out.append("")

    # Supporting interfaces
    out.append("# --- Mineflayer aux interfaces ---")
    for iface in MINEFLAYER_INTERFACES:
        body = find_interface(mf_text, iface)
        if body is None:
            print(f"warn: interface {iface} not found", file=sys.stderr)
            continue
        out.append("")
        out.extend(render_interface(iface, body))
    out.append("")

    # Window-family container classes
    out.append("# --- Mineflayer container classes ---")
    for cls in MINEFLAYER_CLASSES:
        body = find_class(mf_text, cls)
        if body is None:
            print(f"warn: class {cls} not found", file=sys.stderr)
            continue
        out.append("")
        out.extend(render_interface(cls, body))
    out.append("")

    # BotEvents → callback aliases
    events_body = find_interface(mf_text, "BotEvents")
    if events_body is None:
        raise SystemExit("Cannot find BotEvents interface")
    ev_lines, event_callbacks = render_bot_events(events_body)
    out.extend(ev_lines)
    out.append("")

    # BotOptions
    bot_opts_body = find_interface(mf_text, "BotOptions")
    if bot_opts_body is None:
        raise SystemExit("Cannot find BotOptions interface")
    out.extend(render_bot_options(bot_opts_body))
    out.append("")

    # Bot
    bot_body = find_interface(mf_text, "Bot")
    if bot_body is None:
        raise SystemExit("Cannot find Bot interface")
    out.extend(render_bot(bot_body, event_callbacks))
    out.append("")

    # Module-level factory
    out.append("")
    out.append("def create_bot(**options: object) -> Bot: ...")
    out.append("")

    OUT_PATH.write_text("\n".join(out))
    print(f"Wrote {OUT_PATH} ({len(out)} lines)")


if __name__ == "__main__":
    main()
