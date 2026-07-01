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
    for y in range(grid.size):
        for x in range(grid.size):
            cell = grid.get_cell(x, y)
            if cell.tile and cell.tile is not WATER:
                return x, y
    return grid.size // 2, grid.size // 2


def show_help():
    print("""
╔══════════════════════════════════════╗
║          POLIS - 指令列表             ║
╠══════════════════════════════════════╣
║  north/n/北      → 向北移动          ║
║  south/s/南      → 向南移动          ║
║  east/e/东       → 向东移动          ║
║  west/w/西       → 向西移动          ║
║  look/l          → 观察当前位置       ║
║  map/m           → 显示地图          ║
║  talk/t [编号]   → 与NPC对话         ║
║  investigate/inv → 调查当前位置       ║
║  quest/qst       → 查看任务列表       ║
║  help/?          → 显示本帮助         ║
║  quit/q          → 退出游戏           ║
╚══════════════════════════════════════╝
""")


def get_direction(px, py, tx, ty) -> str:
    """计算从(px,py)到(tx,ty)的方向"""
    dx = tx - px
    dy = ty - py
    dir_h = "东" if dx > 0 else "西" if dx < 0 else ""
    dir_v = "南" if dy > 0 else "北" if dy < 0 else ""
    result = dir_v + dir_h
    return result if result else "附近"


def get_common_dialogue(npc: dict, event_mgr, px: int, py: int) -> str:
    """从对话库中选取普通NPC的对话，优先给任务提示"""
    from data.dialogues import COMMON_DIALOGUES, HINT_DIALOGUES
    # ── 所有任务都未发现？引导玩家去最近的任务NPC ──
    all_idle = all(q.stage == EventStage.IDLE for q in event_mgr.quests)
    undiscovered = [q for q in event_mgr.quests if q.stage == EventStage.IDLE]
    if undiscovered:
        nearest = min(undiscovered,
                      key=lambda q: abs(q.npc_x - px) + abs(q.npc_y - py))
        direction = get_direction(px, py, nearest.npc_x, nearest.npc_y)
        hints = [
            f"「{direction}边还有个人在打听事。」{npc['name']}说。",
            f"「听说{direction}边也有人想找人帮忙。」{npc['name']}随口提了一句。",
        ]
        return random.choice(hints)
    if all_idle and event_mgr.quests:
        nearest = min(event_mgr.quests,
                      key=lambda q: abs(q.npc_x - px) + abs(q.npc_y - py))
        direction = get_direction(px, py, nearest.npc_x, nearest.npc_y)
        hints = [
            f"「最近{direction}边来了个陌生人，好像在打听事。」{npc['name']}说。",
            f"「{direction}边有个奇怪的人，你去看看？」{npc['name']}压低声音。",
        ]
        return random.choice(hints)
    
    # ── 优先：有进行中的任务时，给方向提示 ──
    active_quests = [q for q in event_mgr.quests
                     if q.stage in (EventStage.ACCEPTED, EventStage.CLUE_SEARCHING, EventStage.CLUE_FOUND)]

    if active_quests:
        # 找离玩家最近的任务NPC
        nearest = min(active_quests,
                      key=lambda q: abs(q.npc_x - px) + abs(q.npc_y - py))
        direction = get_direction(px, py, nearest.npc_x, nearest.npc_y)
        hints = [
            f"「你要找的人？」{npc['name']}朝{direction}指了指。「往那边。」",
            f"「{nearest.npc_name}？往{direction}走。」{npc['name']}头也不抬。",
            f"「{direction}边有个奇怪的人。」{npc['name']}压低声音。",
            f"「找人的话，往{direction}。」{npc['name']}用下巴指了指方向。",
        ]
        return random.choice(hints)

    # ── 其次：有已完成的线索需要交付时 ──
    clue_ready = [q for q in event_mgr.quests if q.stage == EventStage.CLUE_FOUND]
    if clue_ready:
        nearest = min(clue_ready,
                      key=lambda q: abs(q.npc_x - px) + abs(q.npc_y - py))
        direction = get_direction(px, py, nearest.npc_x, nearest.npc_y)
        return f"「你找到的东西，赶紧给{direction}边那个人看看吧。」{npc['name']}说。"

    # ── 然后：事件提示对话（HINT_DIALOGUES）──
    for entry in HINT_DIALOGUES:
        try:
            if entry["condition"](event_mgr, None):
                text = random.choice(entry["text"])
                return text.format(name=npc["name"], direction="某处")
        except:
            pass

    # ── 最后：通用闲聊 ──
    for entry in COMMON_DIALOGUES:
        try:
            if entry["condition"](event_mgr, None):
                text = random.choice(entry["text"])
                return text.format(name=npc["name"])
        except:
            pass

    return f"「嗯。」{npc['name']}应了一声。"


def talk_to_npc(npc: dict, event_mgr, px: int, py: int) -> str:
    """与NPC对话"""
    if npc.get("is_event_npc"):
        quest = event_mgr.get_npc_at(px, py)

        if quest is None:
            return f"「别管我是谁。」陌生人低声说。"

        if quest.stage == EventStage.IDLE:
            quest.stage = EventStage.ACCEPTED
            quest.is_active = True
            type_hint = {
                "residential": "居住区",
                "commercial": "商业区",
                "government": "行政区",
                "industrial": "工业区",
                "park": "公园",
            }.get(quest.clue_type, quest.clue_type)
            return (
                f"「终于有人来了。」{quest.npc_name}打量着你。\n"
                f"「去{type_hint}找找线索。」"
            )
        elif quest.stage == EventStage.ACCEPTED:
            quest.stage = EventStage.CLUE_SEARCHING
            return f"「快去{quest.clue_type}区。别让人发现。」{quest.npc_name}催促道。"
        elif quest.stage == EventStage.CLUE_SEARCHING:
            direction = get_direction(px, py, quest.clue_x, quest.clue_y)
            return f"「线索在{quest.clue_type}区。往{direction}方向找。」{quest.npc_name}说。"
        elif quest.stage == EventStage.CLUE_FOUND:
            quest.stage = EventStage.RESOLVED
            quest.is_completed = True
            return (
                f"{quest.npc_name}接过你找到的东西，仔细查看。\n"
                f"「果然如此。这件事比我想的更大。」\n"
                f"「你做了一件好事。记住今天。」\n\n"
                f"* 任务「{quest.title}」完成 *"
            )
        elif quest.stage == EventStage.RESOLVED:
            return f"{quest.npc_name}微微点头，不再说话。"

    # 普通NPC
    return get_common_dialogue(npc, event_mgr, px, py)


def show_quest_status(event_mgr, city):
    """显示所有任务"""
    print("══════════ 任务列表 ══════════")
    active = event_mgr.get_active_quests()
    completed = event_mgr.get_completed_quests()

    if not active and not completed:
        print("  暂无任务。四处探索吧。")
        return

    if active:
        print("进行中：")
        for quest in active:
            status = quest.get_status_text()
            print(f"  {status}")
            if quest.stage == EventStage.CLUE_SEARCHING:
                type_hint = {
                    "residential": "居住区",
                    "commercial": "商业区",
                    "government": "行政区",
                    "industrial": "工业区",
                    "park": "公园",
                }.get(quest.clue_type, quest.clue_type)
                print(f"    线索方向: 去{type_hint}")
            elif quest.stage == EventStage.CLUE_FOUND:
                print(f"    NPC位置: ({quest.npc_x}, {quest.npc_y})")

    if completed:
        print("\n已完成：")
        for quest in completed:
            print(f"  {quest.get_status_text()}")

    print("════════════════════════════")


def main():
    print("\n" + "=" * 42)
    print("  WELCOME TO POLIS")
    print("  A Procedural City MUD")
    print("=" * 42)

    seed = random.randint(0, 999999)
    print(f"\nGenerating city... (seed: {seed})")
    city = generate_city(seed=seed)
    event_mgr = EventManager(city, random.Random(seed))

    print("\n=== DEBUG: 任务信息 ===")
    for q in event_mgr.quests:
        npc_cell = city.get_cell(q.npc_x, q.npc_y)
        clue_cell = city.get_cell(q.clue_x, q.clue_y)
        print(f"任务: {q.title}")
        print(f"  NPC: ({q.npc_x},{q.npc_y}) 类型={npc_cell.tile.name} 标记={npc_cell.has_event_npc}")
        print(f"  线索: ({q.clue_x},{q.clue_y}) 类型={clue_cell.tile.name} 标记={clue_cell.clue_target}")
        print(f"  clue_type字段: {q.clue_type}")
        print()

        input("按回车继续...")

    px, py = find_starting_position(city)
    print(f"You awaken at coordinates ({px}, {py}).")
    print(f"There are {len(event_mgr.quests)} quests waiting to be discovered.")

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

        # ── 选人模式 ──
        if pending_npc_selection:
            pending_npc_selection = False
            cell = city.get_cell(px, py)
            all_npcs = cell.npcs.copy()

            if cell.has_event_npc:
                quest = event_mgr.get_npc_at(px, py)
                if quest and quest.stage != EventStage.RESOLVED:
                    event_npc = {
                        "name": quest.npc_name,
                        "trait": "神秘",
                        "profession": "陌生人",
                        "is_event_npc": True,
                    }
                    all_npcs.append(event_npc)

            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(all_npcs):
                    target_npc = all_npcs[idx]
                else:
                    target_npc = None
            else:
                target_npc = None
                for npc in all_npcs:
                    if raw.lower() in npc["name"].lower():
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

        # ── 正常指令 ──
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
                print("You cannot go that way.")
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

            if cell.has_event_npc:
                quest = event_mgr.get_npc_at(px, py)
                if quest and quest.stage != EventStage.RESOLVED:
                    event_npc = {
                        "name": quest.npc_name,
                        "trait": "神秘",
                        "profession": "陌生人",
                        "is_event_npc": True,
                    }
                    all_npcs.append(event_npc)

            if not all_npcs:
                clear_screen()
                print(render_map(city, px, py))
                print("There is no one here to talk to.")
                continue

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
            quest = event_mgr.get_clue_at(px, py)
            if quest and quest.stage == EventStage.CLUE_SEARCHING:
                quest.stage = EventStage.CLUE_FOUND
                cell.clue_target = False
                print(render_map(city, px, py))
                print("你在角落里翻找，发现了重要的线索。")
                print(f"快回去找 {quest.npc_name}！")
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