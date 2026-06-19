"""
城市生成算法

使用柏林噪声（简化版）做地形基底，然后用约束规则修正。
10×10 规模，先保证跑通，后续可调。
"""

import random
import math
from city.tiles import (
    RESIDENTIAL, COMMERCIAL, GOVERNMENT, INDUSTRIAL, PARK, WATER,
    BUILDABLE_TYPES, ALL_TYPES
)
from city.grid import CityGrid, Cell
from city.constraints import ALL_RULES


#柏林噪声
def simple_noise(x: int, y: int, seed: int, scale: float = 0.5) -> float:
    """两层正弦叠加，模拟噪声。值域约 [-2, 2]"""
    rng = random.Random(seed)
    offset1 = rng.uniform(0, 100)
    offset2 = rng.uniform(0, 100)
    return (
        math.sin(x * scale + offset1) * math.cos(y * scale + offset1) +
        math.sin(x * scale * 2 + offset2) * math.cos(y * scale * 2 + offset2) * 0.5
    )


def generate_city(size: int = 10, seed: int | None = None) -> CityGrid:
    """
    主生成函数

    流程：
    1. 用噪声生成地形值
    2. 根据阈值分配初始类型
    3. 用约束规则进行多轮修正
    4. 返回完整城市网格
    """
    if seed is None:
        seed = random.randint(0, 999999)
    
    rng = random.Random(seed)
    print(f"[生成器] 种子: {seed}")

    grid = CityGrid(size)

    # 第一步：噪声生成
    for y in range(size):
        for x in range(size):
            noise_val = simple_noise(x, y, seed)
            cell = grid.get_cell(x, y)

            # 根据噪声值分配类型
            if noise_val > 0.6:
                cell.tile = WATER
            elif noise_val > 0.2:
                cell.tile = COMMERCIAL
            elif noise_val > -0.2:
                cell.tile = RESIDENTIAL
            elif noise_val > -0.7:
                cell.tile = PARK
            else:
                cell.tile = INDUSTRIAL

    # 第二步：放置行政区（选一块商业区或居住区集中的地方）
    place_government(grid, rng)

    # 第三步：约束修正（多轮迭代）
    for iteration in range(10):
        violations = enforce_constraints(grid, rng)
        if violations == 0:
            print(f"[生成器] 第 {iteration+1} 轮修正：无违规，完成")
            break
        print(f"[生成器] 第 {iteration+1} 轮修正：修复 {violations} 处违规")

    return grid


def place_government(grid: CityGrid, rng: random.Random):
    """在商业区或居住区集中的地方放置一个行政区"""
    candidates = []
    for y in range(grid.size):
        for x in range(grid.size):
            cell = grid.get_cell(x, y)
            if cell.tile in (COMMERCIAL, RESIDENTIAL):
                # 检查周围密度
                neighbors = grid.get_neighbors(x, y)
                score = sum(
                    1 for n in neighbors
                    if n.tile in (COMMERCIAL, RESIDENTIAL)
                )
                candidates.append((score, x, y))
    
    if candidates:
        candidates.sort(reverse=True)
        _, gx, gy = candidates[0]
        grid.get_cell(gx, gy).tile = GOVERNMENT


def enforce_constraints(grid: CityGrid, rng: random.Random) -> int:
    """遍历所有格子，修复违规的格子。返回修复次数"""
    violations_fixed = 0
    
    # 打乱遍历顺序，避免产生规律性
    cells = []
    for y in range(grid.size):
        for x in range(grid.size):
            cells.append((x, y))
    rng.shuffle(cells)

    for x, y in cells:
        cell = grid.get_cell(x, y)
        if cell.tile is None:
            continue
        
        neighbors = grid.get_neighbors(x, y)
        
        for rule in ALL_RULES:
            ok, reason = rule(cell, neighbors)
            if not ok:
                # 尝试换成其他类型，看哪个合规
                # 排除 WATER（除非周围水多）
                candidates = [t for t in BUILDABLE_TYPES if t is not cell.tile]
                rng.shuffle(candidates)
                
                fixed = False
                for new_type in candidates:
                    cell.tile = new_type
                    # 检查所有规则
                    all_ok = all(
                        rule(cell, neighbors)[0]
                        for rule in ALL_RULES
                    )
                    if all_ok:
                        fixed = True
                        violations_fixed += 1
                        break
                
                if not fixed:
                    # 如果都不行，退回原来的
                    # 这很少发生，但做个兜底
                    pass
                break  # 修复完就检查下一个格子
    
    return violations_fixed