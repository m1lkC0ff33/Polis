"""
输入解析器

把玩家输入的自然语言转成游戏指令。
目前支持的指令：移动、查看、退出。
"""

# ── 方向映射 ──
# 支持多种写法：north / n / 北 / wangbei 都行

DIRECTION_MAP = {
    # 英文
    "north": (0, -1),
    "n": (0, -1),
    "south": (0, 1),
    "s": (0, 1),
    "east": (1, 0),
    "e": (1, 0),
    "west": (-1, 0),
    "w": (-1, 0),
    # 中文
    "北": (0, -1),
    "南": (0, 1),
    "东": (1, 0),
    "西": (-1, 0),
    # 常见别称
    "上": (0, -1),
    "下": (0, 1),
    "左": (-1, 0),
    "右": (1, 0),
    "northward": (0, -1),
    "southward": (0, 1),
    "eastward": (1, 0),
    "westward": (-1, 0),
}

# ── 查看指令 ──
LOOK_COMMANDS = {"look", "l", "看", "查看", "观察"}
MAP_COMMANDS = {"map", "m", "地图"}
HELP_COMMANDS = {"help", "h", "?", "帮助"}
QUIT_COMMANDS = {"quit", "q", "exit", "退出"}


def parse_direction(raw: str) -> tuple[int, int] | None:
    """尝试解析移动指令，返回 (dx, dy)。不匹配返回 None。"""
    cleaned = raw.strip().lower()
    return DIRECTION_MAP.get(cleaned)


def parse_command(raw: str) -> dict:
    """
    解析玩家输入，返回标准化指令字典。

    返回格式：
    {
        "type": "move" | "look" | "map" | "help" | "quit" | "unknown",
        "data": 相关数据
    }
    """
    cleaned = raw.strip()
    lowered = cleaned.lower()

    # 1. 移动指令
    direction = parse_direction(cleaned)
    if direction is not None:
        return {"type": "move", "data": direction}

    # 2. 查看
    if lowered in LOOK_COMMANDS:
        return {"type": "look", "data": None}

    # 3. 地图
    if lowered in MAP_COMMANDS:
        return {"type": "map", "data": None}

    # 4. 帮助
    if lowered in HELP_COMMANDS:
        return {"type": "help", "data": None}

    # 5. 退出
    if lowered in QUIT_COMMANDS:
        return {"type": "quit", "data": None}

    # 6. 未识别
    return {"type": "unknown", "data": cleaned}