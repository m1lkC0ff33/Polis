"""Polis — Pygame 2D 版本"""

import pygame
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mud.events import EventStage
from city.generator import generate_city
from city.tiles import WATER
from mud.events import EventManager
from pygame_version.renderer import (
    init_fonts, draw_map, draw_legend, draw_info_bar,
    COLOR_BG, MAP_OFFSET_X, MAP_OFFSET_Y, TILE_SIZE,
)
from pygame_version.input_handler import handle_input
from pygame_version.ui import draw_dialog, draw_npc_list, draw_quest_panel
from data.dialogues import COMMON_DIALOGUES, HINT_DIALOGUES


def find_start(grid):
    for y in range(grid.size):
        for x in range(grid.size):
            cell = grid.get_cell(x, y)
            if cell.tile and cell.tile is not WATER:
                return x, y
    return grid.size // 2, grid.size // 2

def get_direction(px, py, tx, ty) -> str:
    """计算方向"""
    dx = tx - px
    dy = ty - py
    dir_h = "东" if dx > 0 else "西" if dx < 0 else ""
    dir_v = "南" if dy > 0 else "北" if dy < 0 else ""
    result = dir_v + dir_h
    return result if result else "附近"

def get_common_dialogue(npc: dict, event_mgr, px: int, py: int) -> str:
    """普通NPC对话——从对话库中按条件选取"""
    name = npc["name"]

    # ── 优先：有未发现的任务时，指向最近的任务NPC ──
    undiscovered = [q for q in event_mgr.quests if q.stage == EventStage.IDLE]
    if undiscovered:
        nearest = min(undiscovered,
                      key=lambda q: abs(q.npc_x - px) + abs(q.npc_y - py))
        direction = get_direction(px, py, nearest.npc_x, nearest.npc_y)
        hints = [
            f"「{direction}边来了个陌生人，好像在打听事。」{name}说。",
            f"「{direction}边有个奇怪的人，你去看看？」{name}压低声音。",
            f"「找人的话，往{direction}。」{name}用下巴指了指。",
        ]
        return random.choice(hints)

    # ── 有进行中的任务？指向最近的任务NPC ──
    active = [q for q in event_mgr.quests
              if q.stage in (EventStage.ACCEPTED, EventStage.CLUE_SEARCHING)]
    if active:
        nearest = min(active,
                      key=lambda q: abs(q.npc_x - px) + abs(q.npc_y - py))
        direction = get_direction(px, py, nearest.npc_x, nearest.npc_y)
        hints = [
            f"「你要找的人？」{name}朝{direction}指了指。",
            f"「{nearest.npc_name}？往{direction}走。」{name}头也不抬。",
        ]
        return random.choice(hints)

    # ── 有线索待交付？指向最近的任务NPC ──
    clue_ready = [q for q in event_mgr.quests if q.stage == EventStage.CLUE_FOUND]
    if clue_ready:
        nearest = min(clue_ready,
                      key=lambda q: abs(q.npc_x - px) + abs(q.npc_y - py))
        direction = get_direction(px, py, nearest.npc_x, nearest.npc_y)
        return f"「你找到的东西，赶紧给{direction}边那个人看看吧。」{name}说。"

    # ── 所有任务完成？用对话库 ──
    all_done = all(q.stage == EventStage.RESOLVED for q in event_mgr.quests)
    if all_done:
        for entry in COMMON_DIALOGUES:
            try:
                if entry["condition"](event_mgr, None):
                    text = random.choice(entry["text"])
                    return text.format(name=name)
            except:
                pass

    # ── 兜底：对话库的最后一条（无条件）──
    for entry in COMMON_DIALOGUES:
        try:
            if entry["condition"](event_mgr, None):
                text = random.choice(entry["text"])
                return text.format(name=name)
        except:
            pass

    return f"「嗯。」{name}应了一声。"

def talk_to_npc(npc: dict, event_mgr, px: int, py: int) -> str:
    if npc.get("is_event_npc"):
        quest = event_mgr.get_npc_at(px, py)
        if quest is None:
            return "「别管我是谁。」"
        if quest.stage == EventStage.IDLE:
            quest.stage = EventStage.ACCEPTED
            quest.is_active = True
            type_hint = {
                "residential": "居住区", "commercial": "商业区",
                "government": "行政区", "industrial": "工业区", "park": "公园",
            }.get(quest.clue_type, quest.clue_type)
            return f"「终于有人来了。」{quest.npc_name}打量着你。\n「去{type_hint}找找线索。」"
        elif quest.stage == EventStage.ACCEPTED:
            quest.stage = EventStage.CLUE_SEARCHING
            return f"「快去{quest.clue_type}区。」"
        elif quest.stage == EventStage.CLUE_SEARCHING:
            return f"「线索在{quest.clue_type}区。」"
        elif quest.stage == EventStage.CLUE_FOUND:
            quest.stage = EventStage.RESOLVED
            quest.is_completed = True
            return f"「果然如此。这件事比我想的更大。」\n* 任务完成 *"
        elif quest.stage == EventStage.RESOLVED:
            return f"{quest.npc_name}微微点头，不再说话。"
    else:
        return get_common_dialogue(npc, event_mgr, px, py)


def main():
    pygame.init()
    init_fonts()

    SCREEN_W = 820
    SCREEN_H = 680
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Polis — Procedural City MUD")
    clock = pygame.time.Clock()

    # 生成城市
    seed = random.randint(0, 999999)
    city = generate_city(seed=seed)
    event_mgr = EventManager(city, random.Random(seed))

    px, py = find_start(city)

    # 状态
    mode = "explore"           # explore | dialog | quest
    dialog_text = ""
    pending_npc_select = False

    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if mode == "dialog":
                # 任意键关闭对话框
                if event.type == pygame.KEYDOWN:
                    mode = "explore"
                continue

            if mode == "quest":
                if event.type == pygame.KEYDOWN:
                    mode = "explore"
                continue

            # explore 模式下的输入
            cmd = handle_input(event)
            if cmd is None:
                continue

            if cmd == "quit":
                running = False

            elif cmd.startswith("move "):
                direction = cmd.split()[1]
                dx, dy = {"north": (0,-1), "south": (0,1),
                          "west": (-1,0), "east": (1,0)}[direction]
                nx, ny = px + dx, py + dy
                if 0 <= nx < city.size and 0 <= ny < city.size:
                    px, py = nx, ny

            elif cmd == "talk":
                cell = city.get_cell(px, py)
                all_npcs = cell.npcs.copy()
                if cell.has_event_npc:
                    quest = event_mgr.get_npc_at(px, py)
                    if quest and quest.stage.value < 4:
                        all_npcs.append({
                            "name": quest.npc_name,
                            "trait": "神秘",
                            "profession": "陌生人",
                            "is_event_npc": True,
                        })
                if not all_npcs:
                    dialog_text = "这里没人可以对话。"
                    mode = "dialog"
                elif len(all_npcs) == 1:
                    dialog_text = talk_to_npc(all_npcs[0], event_mgr, px, py)
                    mode = "dialog"
                else:
                    pending_npc_select = True

            elif cmd == "investigate":
                quest = event_mgr.get_clue_at(px, py)
                if quest and quest.stage.value == EventStage.CLUE_SEARCHING:
                    quest.stage = EventStage.CLUE_FOUND
                    city.get_cell(px, py).clue_target = False
                    dialog_text = "你找到了线索！\n快回去找陌生人。"
                else:
                    dialog_text = "你翻了翻，什么都没找到。"
                mode = "dialog"

            elif cmd == "quest":
                mode = "quest"

        # ── NPC选择（数字键）──
        if pending_npc_select:
            keys = pygame.key.get_pressed()
            for i in range(1, 10):
                if keys[getattr(pygame, f"K_{i}")]:
                    cell = city.get_cell(px, py)
                    all_npcs = cell.npcs.copy()
                    if cell.has_event_npc:
                        quest = event_mgr.get_npc_at(px, py)
                        if quest and quest.stage.value < 4:
                            all_npcs.append({
                                "name": quest.npc_name,
                                "trait": "神秘",
                                "profession": "陌生人",
                                "is_event_npc": True,
                            })
                    if i <= len(all_npcs):
                        dialog_text = talk_to_npc(all_npcs[i-1], event_mgr, px, py)
                        mode = "dialog"
                    pending_npc_select = False
                    break

        # ── 绘制 ──
        screen.fill(COLOR_BG)
        draw_map(screen, city, px, py)
        draw_legend(screen, city)
        draw_info_bar(screen, city, px, py)

        # NPC列表
        if pending_npc_select:
            cell = city.get_cell(px, py)
            all_npcs = cell.npcs.copy()
            if cell.has_event_npc:
                quest = event_mgr.get_npc_at(px, py)
                if quest and quest.stage.value < 4:
                    all_npcs.append({
                        "name": quest.npc_name,
                        "trait": "神秘",
                        "profession": "陌生人",
                        "is_event_npc": True,
                    })
            draw_npc_list(screen, all_npcs, city.size)

        # 对话框
        if mode == "dialog":
            draw_dialog(screen, dialog_text, city.size)

        # 任务面板
        if mode == "quest":
            draw_quest_panel(screen, event_mgr, city.size, px, py)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()