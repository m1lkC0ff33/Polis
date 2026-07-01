"""Pygame 渲染器"""

import pygame
from city.grid import CityGrid

# ── 颜色 ──
COLOR_MAP = {
    "residential": (100, 180, 100),
    "commercial":  (220, 200, 60),
    "government":  (220, 220, 220),
    "industrial":  (140, 140, 140),
    "park":        (80, 180, 160),
    "water":       (60, 120, 200),
}
COLOR_DEFAULT = (40, 40, 40)
COLOR_PLAYER = (255, 255, 255)
COLOR_BG = (20, 20, 20)
COLOR_TEXT = (200, 200, 200)
COLOR_TEXT_BRIGHT = (255, 255, 255)
COLOR_HIGHLIGHT = (255, 255, 0)
COLOR_PANEL_BG = (30, 30, 40)
COLOR_PANEL_BORDER = (80, 80, 100)

# ── 布局常量 ──
TILE_SIZE = 50
MAP_OFFSET_X = 30
MAP_OFFSET_Y = 30

# ── 字体 ──
_font_small = None
_font_normal = None
_font_large = None


def init_fonts():
    global _font_small, _font_normal, _font_large
    _font_small = pygame.font.SysFont("microsoftyahei", 16)
    _font_normal = pygame.font.SysFont("microsoftyahei", 20, bold=True)
    _font_large = pygame.font.SysFont("microsoftyahei", 26, bold=True)


def small_font():
    return _font_small


def normal_font():
    return _font_normal


def large_font():
    return _font_large


def draw_map(screen, grid: CityGrid, px: int, py: int):
    """绘制城市地图"""
    for y in range(grid.size):
        for x in range(grid.size):
            cell = grid.get_cell(x, y)
            if cell.tile:
                color = COLOR_MAP.get(cell.tile.type_id, COLOR_DEFAULT)
                symbol = cell.tile.symbol
            else:
                color = COLOR_DEFAULT
                symbol = "·"

            rect = pygame.Rect(
                MAP_OFFSET_X + x * TILE_SIZE,
                MAP_OFFSET_Y + y * TILE_SIZE,
                TILE_SIZE - 2,
                TILE_SIZE - 2
            )
            pygame.draw.rect(screen, color, rect, border_radius=3)

            # 符号
            text = normal_font().render(symbol, True, COLOR_TEXT_BRIGHT)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

    # 玩家高亮框
    player_rect = pygame.Rect(
        MAP_OFFSET_X + px * TILE_SIZE,
        MAP_OFFSET_Y + py * TILE_SIZE,
        TILE_SIZE - 2,
        TILE_SIZE - 2
    )
    pygame.draw.rect(screen, COLOR_PLAYER, player_rect, 3, border_radius=3)


def draw_legend(screen, grid: CityGrid):
    """绘制图例"""
    x = MAP_OFFSET_X + grid.size * TILE_SIZE + 25
    y = MAP_OFFSET_Y

    title = normal_font().render("Legend", True, COLOR_TEXT)
    screen.blit(title, (x, y))
    y += 28

    for type_id, color in COLOR_MAP.items():
        pygame.draw.rect(screen, color, (x, y, 14, 14), border_radius=2)
        label = small_font().render(type_id.capitalize(), True, COLOR_TEXT)
        screen.blit(label, (x + 20, y - 1))
        y += 22


def draw_info_bar(screen, grid: CityGrid, px: int, py: int):
    """底部信息栏"""
    y = MAP_OFFSET_Y + grid.size * TILE_SIZE + 15
    cell = grid.get_cell(px, py)

    if cell.tile:
        info = f"[{cell.tile.name}] ({px},{py})"
        if cell.landmark:
            info += f"  —  {cell.landmark}"
    else:
        info = "Void"

    text = normal_font().render(info, True, COLOR_TEXT_BRIGHT)
    screen.blit(text, (MAP_OFFSET_X, y))