"""
终端渲染器

纯英文符号渲染，避免中文字符宽度问题。
"""

from city.grid import CityGrid


# ── 颜色映射（只存背景色码） ──
COLOR_MAP = {
    "residential": "42",   # 绿底
    "commercial":  "43",   # 黄底
    "government":  "47",   # 白底
    "industrial":  "100",  # 灰底
    "park":        "42",   # 绿底
    "water":       "44",   # 蓝底
}

TYPE_LABELS = {
    "residential": "Residential",
    "commercial":  "Commercial",
    "government":  "Government",
    "industrial":  "Industrial",
    "park":        "Park",
    "water":       "Water",
}


def color_cell(symbol: str, bg: str, highlight: bool = False) -> str:
    """生成一个带背景色的格子，正好3字符宽"""
    if highlight:
        # 玩家所在格用方括号
        return f"\033[{bg}m[{symbol}]\033[0m"
    else:
        return f"\033[{bg}m {symbol} \033[0m"


def render_map(grid: CityGrid, player_x: int, player_y: int) -> str:
    """
    渲染地图。
    每个格子是 `[X]` 或 ` X ` 格式，正好3字符宽。
    格子之间用竖线分隔。
    """
    lines = []
    size = grid.size

    # 顶部边界
    lines.append("+" + "---+" * size)

    for y in range(size):
        # 格子行
        row = "|"
        for x in range(size):
            cell = grid.get_cell(x, y)
            if cell and cell.tile:
                bg = COLOR_MAP.get(cell.tile.type_id, "40")
                sym = cell.tile.symbol
            else:
                bg = "40"
                sym = "."

            is_player = (x == player_x and y == player_y)
            row += color_cell(sym, bg, highlight=is_player)
            row += "|"
        lines.append(row)

        # 分隔线
        lines.append("+" + "---+" * size)

    return "\n".join(lines)


def render_legend() -> str:
    """渲染图例"""
    items = []
    for type_id, bg in COLOR_MAP.items():
        sym = type_id[0].upper()
        block = f"\033[{bg}m {sym} \033[0m"
        items.append(f"{block} {TYPE_LABELS[type_id]}")
    return "  ".join(items)


def render_location_detail(grid: CityGrid, x: int, y: int) -> str:
    """渲染当前位置详情"""
    cell = grid.get_cell(x, y)
    if cell is None or cell.tile is None:
        return "You stand in emptiness."

    tile = cell.tile
    label = TYPE_LABELS.get(tile.type_id, "Unknown")

    lines = []
    lines.append("")
    lines.append("=" * 40)
    lines.append(f"[ {label} ]")
    lines.append("=" * 40)
    lines.append(tile.description)

    # 周围
    neighbors = grid.get_neighbors(x, y)
    directions = ["North", "East", "South", "West"]
    lines.append("")
    lines.append("Surroundings:")
    for d, n in zip(directions, neighbors):
        if n and n.tile:
            n_label = TYPE_LABELS.get(n.tile.type_id, "Unknown")
            lines.append(f"  {d}: {n_label}")
        else:
            lines.append(f"  {d}: Void")

    lines.append("=" * 40)
    return "\n".join(lines)