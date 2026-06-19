"""临时测试：生成城市并彩色显示"""
from city.generator import generate_city
from mud.renderer import render_map, render_legend, render_location_detail

# 生成城市
grid = generate_city(seed=42)

# 选一个起始位置（找第一个非水域格子）
start_x, start_y = 5, 5
for y in range(grid.size):
    for x in range(grid.size):
        cell = grid.get_cell(x, y)
        if cell.tile and cell.tile.type_id != "water":
            start_x, start_y = x, y
            break
    else:
        continue
    break

print(f"\n玩家位置: ({start_x}, {start_y})")
print(render_legend())
print()
print(render_map(grid, start_x, start_y))
print(render_location_detail(grid, start_x, start_y))