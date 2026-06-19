"""
Polis —— 程序化城市 MUD 游戏
"""

import random
import os
from city.generator import generate_city
from city.tiles import WATER
from mud.renderer import render_map, render_legend, render_location_detail
from mud.parser import parse_command

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


def main():
    print("\n" + "=" * 42)
    print("  WELCOME TO POLIS")
    print("  A Procedural City MUD")
    print("=" * 42)

    # 生成城市
    seed = random.randint(0, 999999)
    print(f"\nGenerating city... (seed: {seed})")
    city = generate_city(seed=seed)

    # 玩家起始位置
    px, py = find_starting_position(city)
    print(f"You awaken at coordinates ({px}, {py}).")

    # 首次显示
    print(render_legend())
    print()
    print(render_map(city, px, py))
    print(render_location_detail(city, px, py))

    # ── 主循环 ──
    while True:
        try:
            raw = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFarewell.")
            break

        if not raw:
            continue

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
                print(render_location_detail(city, px, py))

        elif cmd["type"] == "look":
            clear_screen()
            print(render_location_detail(city, px, py))

        elif cmd["type"] == "map":
            clear_screen()
            print(render_map(city, px, py))

        elif cmd["type"] == "help":
            clear_screen()
            show_help()

        elif cmd["type"] == "unknown":
            clear_screen()
            print(f"You tried to '{cmd['data']}', but nothing happens.")
            print("Type 'help' for available commands.")


if __name__ == "__main__":
    main()