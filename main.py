"""
Polis —— 程序化城市 MUD 游戏
"""

import random
import os
from city.generator import generate_city
from city.tiles import WATER
from mud.renderer import render_map, render_legend, render_location_detail
from mud.parser import parse_command
from mud.events import EventManager, EventStage

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def find_starting_position(grid):
    """找一个非水域格子作为玩家出生点"""
    for y in range(grid.size):
        for x in range(grid.size):
            cell = grid.get_cell(x, y)
            if cell.tile and cell.tile is not WATER:
                return x, y
    return grid.size // 2, grid.size // 2  # 极端情况：全是水


def show_help():
    """显示帮助信息"""
    print("""
╔══════════════════════════════════════╗
║          POLIS - 指令列表             ║
╠══════════════════════════════════════╣
║  north / n  / 北     → 向北移动      ║
║  south / s  / 南     → 向南移动      ║
║  east  / e  / 东     → 向东移动      ║
║  west  / w  / 西     → 向西移动      ║
║  look  / l           → 观察当前位置   ║
║  map   / m           → 显示地图      ║
║  help  / ?           → 显示本帮助    ║
║  quit  / q           → 退出游戏      ║
╚══════════════════════════════════════╝
""")
    
def talk_to_npc(npc: dict, event_mgr, px: int, py: int) -> str:
    """根据NPC类型返回对话内容"""
    if npc.get("is_event_npc"):
        # ── 事件NPC的对话逻辑 ──
        if event_mgr.stage == EventStage.IDLE:
            event_mgr.stage = EventStage.NPC_FOUND
            result = event_mgr.get_npc_intro()
            event_mgr.stage = EventStage.CLUE_SEARCHING
            return result
        elif event_mgr.stage == EventStage.CLUE_SEARCHING:
            return event_mgr.get_npc_waiting()
        elif event_mgr.stage == EventStage.CLUE_FOUND:
            event_mgr.stage = EventStage.RESOLVED
            return event_mgr.get_npc_completion()
        elif event_mgr.stage == EventStage.RESOLVED:
            return f"{event_mgr.npc_name}微微点头，不再说话。"
        else:
            return f"{event_mgr.npc_name}沉默不语。"

    else:
        # ── 普通NPC的对话逻辑 ──
        if event_mgr.stage in (EventStage.IDLE, EventStage.CLUE_SEARCHING):
            # 算方向
            dx = event_mgr.npc_x - px
            dy = event_mgr.npc_y - py
            dir_h = "东" if dx > 0 else "西" if dx < 0 else ""
            dir_v = "南" if dy > 0 else "北" if dy < 0 else ""
            direction = dir_v + dir_h if dir_v or dir_h else ""
            if not direction:
                direction = "就在附近"
            return f"「找那个陌生人？」{npc['name']}想了想。「往{direction}走走看？」"
        elif event_mgr.stage == EventStage.CLUE_FOUND:
            return f"「听说有人在调查市长。」{npc['name']}压低声音。"
        else:
            return f"「最近城里不太平。」{npc['name']}说。"

def show_quest_status(event_mgr, city):
    """显示任务状态"""
    if event_mgr.stage == EventStage.IDLE:
        print("No active quest. Explore the city.")
    elif event_mgr.stage == EventStage.CLUE_SEARCHING:
        clue_cell = city.get_cell(event_mgr.clue_x, event_mgr.clue_y)
        clue_location = clue_cell.tile.name if clue_cell.tile else "未知"
        if clue_cell.landmark:
            clue_location += f" ({clue_cell.landmark})"
        print(f"Quest: Find clues in the {clue_location}.")
        print(f"Hint: Look for a {clue_cell.tile.name} on the map.")
    elif event_mgr.stage == EventStage.CLUE_FOUND:
        print("Quest: Return to the mysterious stranger.")
        print(f"He was last seen near ({event_mgr.npc_x}, {event_mgr.npc_y}).")
    elif event_mgr.stage == EventStage.RESOLVED:
        print("Quest complete. The city holds more secrets...")


def main():
    print("\n" + "=" * 42)
    print("  WELCOME TO POLIS")
    print("  A Procedural City MUD")
    print("=" * 42)

    seed = random.randint(0, 999999)
    print(f"\nGenerating city... (seed: {seed})")
    city = generate_city(seed=seed)
    event_mgr = EventManager(city, random.Random(seed))

    px, py = find_starting_position(city)
    print(f"You awaken at coordinates ({px}, {py}).")

    # 选人模式状态
    pending_npc_selection = False

    clear_screen()
    print(render_legend())
    print()
    print(render_map(city, px, py))
    print(render_location_detail(city, px, py, event_mgr))

    while True:
        try:
            raw = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFarewell.")
            break

        if not raw:
            continue

        # ── 如果在选人模式，优先处理选人输入 ──
        if pending_npc_selection:
            pending_npc_selection = False
            cell = city.get_cell(px, py)
            all_npcs = cell.npcs.copy()

            # 如果当前格有事件NPC，也加入可选列表
            if cell.has_event_npc and event_mgr.stage.value < EventStage.RESOLVED.value:
                event_npc = {
                    "name": event_mgr.npc_name,
                    "trait": event_mgr.npc_trait,
                    "profession": "神秘陌生人",
                    "is_event_npc": True,
                }
                all_npcs.append(event_npc)

            # 尝试匹配输入
            target_npc = None

            # 先尝试按数字匹配
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(all_npcs):
                    target_npc = all_npcs[idx]

            # 再尝试按名字匹配（模糊）
            if target_npc is None:
                for npc in all_npcs:
                    if npc["name"] in raw or raw.lower() in npc["name"].lower():
                        target_npc = npc
                        break

            if target_npc is None:
                clear_screen()
                print(render_map(city, px, py))
                print(f"No one matching '{raw}' is here.")
            else:
                clear_screen()
                print(render_map(city, px, py))
                print(talk_to_npc(target_npc, event_mgr, px, py))

            continue

        # ── 正常指令处理 ──
        cmd = parse_command(raw)

        if cmd["type"] == "quit":
            clear_screen()
            print("You leave the city behind. Farewell.")
            break

        elif cmd["type"] == "move":
            dx, dy = cmd["data"]
            nx, ny = px + dx, py + dy
            new_cell = city.get_cell(nx, ny)
            if new_cell is None:
                clear_screen()
                print("You cannot go that way — the city ends here.")
            else:
                px, py = nx, ny
                clear_screen()
                print(render_map(city, px, py))
                print(render_location_detail(city, px, py, event_mgr))

        elif cmd["type"] == "look":
            clear_screen()
            print(render_location_detail(city, px, py, event_mgr))

        elif cmd["type"] == "map":
            clear_screen()
            print(render_map(city, px, py))

        elif cmd["type"] == "help":
            clear_screen()
            show_help()

        elif cmd["type"] == "talk":
            target = cmd["data"]
            cell = city.get_cell(px, py)
            all_npcs = cell.npcs.copy()

            if cell.has_event_npc and event_mgr.stage.value < EventStage.RESOLVED.value:
                event_npc = {
                    "name": event_mgr.npc_name,
                    "trait": event_mgr.npc_trait,
                    "profession": "神秘陌生人",
                    "is_event_npc": True,
                }
                all_npcs.append(event_npc)

            if not all_npcs:
                clear_screen()
                print(render_map(city, px, py))
                print("There is no one here to talk to.")
                continue

            # 如果带了参数（talk 1 或 talk 王铁生）
            if target is not None:
                target_npc = None
                if target.isdigit():
                    idx = int(target) - 1
                    if 0 <= idx < len(all_npcs):
                        target_npc = all_npcs[idx]
                else:
                    for npc in all_npcs:
                        if target.lower() in npc["name"].lower():
                            target_npc = npc
                            break

                if target_npc is None:
                    clear_screen()
                    print(render_map(city, px, py))
                    print(f"No one matching '{target}' is here.")
                else:
                    clear_screen()
                    print(render_map(city, px, py))
                    print(talk_to_npc(target_npc, event_mgr, px, py))
            else:
                # 没带参数 → 列出NPC，进入选人模式
                clear_screen()
                print(render_map(city, px, py))
                print("Who do you want to talk to?\n")
                for i, npc in enumerate(all_npcs, 1):
                    print(f"  {i}. {npc['name']} — {npc['trait']}的{npc['profession']}")
                print("\nEnter a number or name:")
                pending_npc_selection = True

        elif cmd["type"] == "investigate":
            clear_screen()
            cell = city.get_cell(px, py)
            if cell.clue_target and event_mgr.stage == EventStage.CLUE_SEARCHING:
                event_mgr.stage = EventStage.CLUE_FOUND
                cell.clue_target = False
                print(render_map(city, px, py))
                print(event_mgr.get_clue_discovery())
                print("\nYou should return to the stranger.")
            else:
                print(render_map(city, px, py))
                print("You search the area but find nothing of interest.")

        elif cmd["type"] == "quest":
            clear_screen()
            print(render_map(city, px, py))
            show_quest_status(event_mgr, city)

        elif cmd["type"] == "unknown":
            clear_screen()
            print(render_map(city, px, py))
            print(f"'{cmd['data']}' is not a valid command.")
            print("Type 'help' for available commands.")


if __name__ == "__main__":
    main()