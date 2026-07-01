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
TALK_COMMANDS = {"talk", "t", "对话", "交谈"}
INVESTIGATE_COMMANDS = {"investigate", "inv", "调查", "搜查"}
QUEST_COMMANDS = {"quest", "任务", "进度"}


def parse_direction(raw: str) -> tuple[int, int] | None:
    """尝试解析移动指令，返回 (dx, dy)。不匹配返回 None。"""
    cleaned = raw.strip().lower()
    return DIRECTION_MAP.get(cleaned)


def parse_command(raw: str) -> dict:
    """玩家指令识别与回应"""
    cleaned = raw.strip()
    lowered = cleaned.lower()

    if lowered == "talk" or lowered == "t" or lowered in TALK_COMMANDS:
        return {"type": "talk", "data": None}
    if lowered.startswith("talk ") or lowered.startswith("t "):
        parts = cleaned.split(maxsplit=1)
        target = parts[1].strip() if len(parts) > 1 else None
        return {"type": "talk", "data": target}

    direction = parse_direction(cleaned)
    if direction is not None:
        return {"type": "move", "data": direction}

    if lowered in INVESTIGATE_COMMANDS:
        return {"type": "investigate", "data": None}
    
    if lowered in QUEST_COMMANDS:
        return {"type": "quest", "data": None}

    if lowered in LOOK_COMMANDS:
        return {"type": "look", "data": None}
    if lowered in MAP_COMMANDS:
        return {"type": "map", "data": None}
    if lowered in HELP_COMMANDS:
        return {"type": "help", "data": None}
    if lowered in QUIT_COMMANDS:
        return {"type": "quit", "data": None}

    return {"type": "unknown", "data": cleaned}