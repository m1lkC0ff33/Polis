"""
10x10 的二维网格。每个格子可以是 None或一个 TileType。
"""

from city.tiles import TileType


class Cell:
    """网格中的一个单元格"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.tile: TileType | None = None
        self.landmark: str = ""
        self.description: str = ""

    def __repr__(self):
        if self.tile is None:
            return "·"
        return self.tile.symbol


class CityGrid:
    """10×10 城市网格"""
    def __init__(self, size: int = 10):
        self.size = size
        self.grid: list[list[Cell]] = []
        for y in range(size):
            row = []
            for x in range(size):
                row.append(Cell(x, y))
            self.grid.append(row)

    def get_cell(self, x: int, y: int) -> Cell | None:
        """获取指定坐标的格子，越界返回 None"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[y][x]
        return None

    def get_neighbors(self, x: int, y: int) -> list[Cell]:
        """获取上下左右四个邻居（不含对角线）"""
        neighbors = []
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            cell = self.get_cell(x + dx, y + dy)
            if cell is not None:
                neighbors.append(cell)
        return neighbors

    def set_tile(self, x: int, y: int, tile: TileType):
        """给指定格子设置街区类型"""
        self.grid[y][x].tile = tile

    def count_type(self, tile: TileType) -> int:
        """统计某种街区类型的数量"""
        count = 0
        for row in self.grid:
            for cell in row:
                if cell.tile is tile:
                    count += 1
        return count

    def __repr__(self):
        """打印整个网格"""
        lines = []
        for row in self.grid:
            line = " ".join(str(cell) for cell in row)
            lines.append(line)
        return "\n".join(lines)