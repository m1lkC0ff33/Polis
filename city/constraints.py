"""
街区拼接规则校验

每条规则都是一个函数，接收一个 Cell 和它的邻居列表，
返回 (是否合规, 违规原因)。
"""

from city.tiles import (
    TileType, RESIDENTIAL, COMMERCIAL, GOVERNMENT,
    INDUSTRIAL, PARK, WATER
)


def rule_commercial_needs_residential(cell, neighbors):
    """商业区必须紧邻至少 1 个居住区"""
    if cell.tile is not COMMERCIAL:
        return True, ""  # 不是商业区，不用检查
    has_residential = any(n.tile is RESIDENTIAL for n in neighbors)
    if not has_residential:
        return False, "商业区需要紧邻至少一个居住区"
    return True, ""


def rule_industry_not_next_to_residential(cell, neighbors):
    """工业区不能紧邻居住区"""
    if cell.tile is not INDUSTRIAL:
        return True, ""
    has_residential = any(n.tile is RESIDENTIAL for n in neighbors)
    if has_residential:
        return False, "工业区不能紧邻居住区（需要商业区或空地缓冲）"
    return True, ""


def rule_government_surrounded(cell, neighbors):
    """行政区周围至少 2 个方向是居住区或商业区"""
    if cell.tile is not GOVERNMENT:
        return True, ""
    service_count = sum(
        1 for n in neighbors
        if n.tile in (RESIDENTIAL, COMMERCIAL)
    )
    if service_count < 2:
        return False, "行政区需要至少两个方向紧邻居住区或商业区"
    return True, ""


def rule_water_connectivity(cell, neighbors):
    """水域相邻格子中至少要有 2 个水域（形成河流/湖泊，避免孤池）"""
    if cell.tile is not WATER:
        return True, ""
    water_count = sum(1 for n in neighbors if n.tile is WATER)
    # 新放置的水域还没算入，所以检查的是邻居中已有水域数量
    if water_count < 2:
        return False, "水域需要至少两个相邻水域格（避免孤池）"
    return True, ""

def rule_park_needs_purpose(cell, neighbors):
    """公园需要紧邻居住区，或作为工业-居住缓冲带"""
    if cell.tile is not PARK:
        return True, ""
    
    has_residential = any(n.tile is RESIDENTIAL for n in neighbors)
    # 作为缓冲带：同时挨着工业和居住
    has_industrial = any(n.tile is INDUSTRIAL for n in neighbors)
    is_buffer = has_residential and has_industrial
    
    if has_residential or is_buffer:
        return True, ""
    
    return False, ""



# 所有规则汇总
ALL_RULES = [
    rule_commercial_needs_residential,
    rule_industry_not_next_to_residential,
    rule_government_surrounded,
    rule_water_connectivity,
    rule_park_needs_purpose
]