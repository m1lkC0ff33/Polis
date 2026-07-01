"""UI组件：对话框、NPC选择、任务面板"""

import pygame
from pygame_version.renderer import (
    normal_font, small_font,
    COLOR_TEXT, COLOR_TEXT_BRIGHT, COLOR_HIGHLIGHT,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    MAP_OFFSET_X, MAP_OFFSET_Y, TILE_SIZE,
)

from mud.events import EventStage
def draw_dialog(screen, text: str, grid_size: int):
    """
    在屏幕底部绘制对话框。
    按任意键关闭——返回后由调用方处理。
    """
    panel_x = MAP_OFFSET_X
    panel_w = grid_size * TILE_SIZE
    panel_y = MAP_OFFSET_Y + grid_size * TILE_SIZE + 50
    panel_h = 120

    # 背景
    pygame.draw.rect(screen, COLOR_PANEL_BG,
                     (panel_x, panel_y, panel_w, panel_h),
                     border_radius=6)
    pygame.draw.rect(screen, COLOR_PANEL_BORDER,
                     (panel_x, panel_y, panel_w, panel_h),
                     2, border_radius=6)

    # 文字（支持换行）
    lines = text.split("\n")
    y_offset = panel_y + 15
    for line in lines:
        rendered = normal_font().render(line, True, COLOR_TEXT_BRIGHT)
        screen.blit(rendered, (panel_x + 15, y_offset))
        y_offset += 26

    # 提示
    hint = small_font().render("Press any key to continue...", True, (120, 120, 120))
    screen.blit(hint, (panel_x + panel_w - hint.get_width() - 15,
                       panel_y + panel_h - 25))


def draw_npc_list(screen, npcs: list, grid_size: int):
    """
    绘制NPC选择列表（在右侧面板）。
    返回无——实际选择逻辑在main里处理。
    """
    x = MAP_OFFSET_X + grid_size * TILE_SIZE + 25
    y = MAP_OFFSET_Y + 200

    title = normal_font().render("NPCs here:", True, COLOR_HIGHLIGHT)
    screen.blit(title, (x, y))
    y += 30

    for i, npc in enumerate(npcs, 1):
        line = f"{i}. {npc['name']} — {npc['trait']}的{npc['profession']}"
        text = small_font().render(line, True, COLOR_TEXT)
        screen.blit(text, (x, y))
        y += 22


def draw_quest_panel(screen, event_mgr, grid_size: int, px: int = 0, py: int = 0):
    """绘制任务面板——显示每个任务的状态和方向提示"""
    x = MAP_OFFSET_X
    y = MAP_OFFSET_Y + grid_size * TILE_SIZE + 50
    w = grid_size * TILE_SIZE
    h = 200

    pygame.draw.rect(screen, COLOR_PANEL_BG,
                     (x, y, w, h), border_radius=6)
    pygame.draw.rect(screen, COLOR_PANEL_BORDER,
                     (x, y, w, h), 2, border_radius=6)

    title = normal_font().render("Quests", True, COLOR_HIGHLIGHT)
    screen.blit(title, (x + 15, y + 10))
    y += 40

    if not event_mgr.quests:
        text = small_font().render("No quests in this city.", True, COLOR_TEXT)
        screen.blit(text, (x + 15, y))
        return

    type_names = {
        "residential": "居住区", "commercial": "商业区",
        "government": "行政区", "industrial": "工业区", "park": "公园",
    }

    for q in event_mgr.quests:
        if q.stage == EventStage.IDLE:
            status = f"[ ] {q.title} — 待发现"
            color = (140, 140, 140)
        elif q.stage == EventStage.ACCEPTED:
            hint = type_names.get(q.clue_type, q.clue_type)
            status = f"[!] {q.title} — 去{hint}找线索"
            color = COLOR_TEXT_BRIGHT
        elif q.stage == EventStage.CLUE_SEARCHING:
            hint = type_names.get(q.clue_type, q.clue_type)
            direction = get_direction(px, py, q.clue_x, q.clue_y)
            status = f"[!] {q.title} — 去{hint}（{direction}方向）"
            color = COLOR_HIGHLIGHT
        elif q.stage == EventStage.CLUE_FOUND:
            direction = get_direction(px, py, q.npc_x, q.npc_y)
            status = f"[?] {q.title} — 回去找{q.npc_name}（{direction}方向）"
            color = (255, 200, 60)
        elif q.stage == EventStage.RESOLVED:
            status = f"[✓] {q.title} — 已完成"
            color = (100, 180, 100)
        else:
            status = f"   {q.title}"
            color = COLOR_TEXT

        text = small_font().render(status, True, color)
        screen.blit(text, (x + 15, y))
        y += 22

def get_direction(px, py, tx, ty) -> str:
    """计算方向"""
    dx = tx - px
    dy = ty - py
    dir_h = "东" if dx > 0 else "西" if dx < 0 else ""
    dir_v = "南" if dy > 0 else "北" if dy < 0 else ""
    result = dir_v + dir_h
    return result if result else "附近"