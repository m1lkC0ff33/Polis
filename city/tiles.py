"""
定义城市中所有街区类型。
每个类型有自己的名字、地图符号、终端颜色、基础描述。
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class TileType:
    """街区类型的数据结构"""
    type_id: str
    name: str
    symbol: str
    color: str
    description: str

RESIDENTIAL = TileType(
    type_id="residential",
    name="居住区",
    symbol="R",
    color="green",
    description="错落的民居之间，晾衣绳横跨小巷，隐约传来锅碗瓢盆的响动。"
)

COMMERCIAL = TileType(
    type_id="commercial",
    name="商业区",
    symbol="C",
    color="yellow",
    description="招牌林立，人声鼎沸。叫卖声、讨价还价声此起彼伏。"
)

GOVERNMENT = TileType(
    type_id="government",
    name="行政区",
    symbol="G",
    color="white",
    description="石板铺就的广场尽头矗立着市政厅，空气莫名安静下来。"
)

INDUSTRIAL = TileType(
    type_id="industrial",
    name="工业区",
    symbol="I",
    color="gray",
    description="烟囱吐着黑烟，空气里弥漫着铁锈和煤灰的气味。"
)

PARK = TileType(
    type_id="park",
    name="公园",
    symbol="P",
    color="green",
    description="几棵老树撑开枝叶，在喧嚣的城市中撑出一片难得的宁静。"
)

WATER = TileType(
    type_id="water",
    name="水域",
    symbol="W",
    color="blue",
    description="水面倒映着城市的灯火。水波轻轻拍打着堤岸。"
)

ALL_TYPES = [RESIDENTIAL, COMMERCIAL, GOVERNMENT, INDUSTRIAL, PARK, WATER]
BUILDABLE_TYPES = [RESIDENTIAL, COMMERCIAL, GOVERNMENT, INDUSTRIAL, PARK]