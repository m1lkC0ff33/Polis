"""
事件系统

管理事件链的状态：NPC位置、任务进度、线索位置。
"""

import random
from enum import Enum


class EventStage(Enum):
    """事件链的四个阶段"""
    IDLE = 0               # 还没找到NPC
    NPC_FOUND = 1          # 找到了，还没接任务
    CLUE_SEARCHING = 2     # 接了任务，正在找线索
    CLUE_FOUND = 3         # 找到线索，回去找NPC
    RESOLVED = 4           # 事件完成


class EventManager:
    """管理整个事件链"""

    def __init__(self, city_grid, rng: random.Random):
        self.grid = city_grid
        self.rng = rng
        self.stage = EventStage.IDLE

        # NPC位置
        self.npc_x: int = -1
        self.npc_y: int = -1
        self.npc_name: str = ""
        self.npc_trait: str = ""

        # 线索位置
        self.clue_x: int = -1
        self.clue_y: int = -1
        self.clue_type: str = ""       # 线索要求的街区类型

        # 放置NPC和线索
        self._place_npc()
        self._place_clue()

    def _place_npc(self):
        """随机选一个非水域格子放置NPC"""
        from city.tiles import WATER
        candidates = []
        for y in range(self.grid.size):
            for x in range(self.grid.size):
                cell = self.grid.get_cell(x, y)
                if cell.tile and cell.tile is not WATER:
                    candidates.append((x, y))

        self.npc_x, self.npc_y = self.rng.choice(candidates)
        self.grid.get_cell(self.npc_x, self.npc_y).has_event_npc = True

        # 随机名字
        from data.names import random_npc_name, random_trait
        self.npc_name = random_npc_name(self.rng)
        self.npc_trait = random_trait(self.rng)

    def _place_clue(self):
        """
        选一个和NPC不同位置的格子作为线索目标。
        优先选和NPC所在格子类型不同的街区。
        """
        from city.tiles import WATER
        npc_cell = self.grid.get_cell(self.npc_x, self.npc_y)

        candidates = []
        for y in range(self.grid.size):
            for x in range(self.grid.size):
                if x == self.npc_x and y == self.npc_y:
                    continue
                cell = self.grid.get_cell(x, y)
                if cell.tile and cell.tile is not WATER:
                    candidates.append((x, y))

        self.clue_x, self.clue_y = self.rng.choice(candidates)
        clue_cell = self.grid.get_cell(self.clue_x, self.clue_y)
        clue_cell.clue_target = True
        self.clue_type = clue_cell.tile.type_id

    def get_npc_intro(self) -> str:
        """NPC首次见面的台词"""
        clue_type_name = {
            "residential": "居住区",
            "commercial": "商业区",
            "government": "行政区",
            "industrial": "工业区",
            "park": "公园",
        }.get(self.clue_type, "某个地方")

        return (
            f"「你也在调查这座城市？」{self.npc_name}压低声音说。\n"
            f"「去{clue_type_name}找找。那里有东西。」"
        )

    def get_npc_waiting(self) -> str:
        """玩家还没找到线索时的对话"""
        clue_type_name = {
            "residential": "居住区",
            "commercial": "商业区",
            "government": "行政区",
            "industrial": "工业区",
            "park": "公园",
        }.get(self.clue_type, "那个地方")
        return f"「{clue_type_name}。快去。」{self.npc_name}不耐烦地摆了摆手。"

    def get_npc_completion(self) -> str:
        """交付线索后的对话"""
        return (
            f"{self.npc_name}看着你找到的东西，沉默了片刻。\n"
            f"「果然。市长和码头的走私脱不了干系。」\n"
            f"「你做了件好事。记住今天。」\n\n"
            f"* 事件完成 *"
        )

    def get_clue_discovery(self) -> str:
        """找到线索时的描述"""
        return (
            "你在角落里翻找，手指碰到了什么东西——\n"
            "一封信。信纸上印着市长府的徽记，内容提到了码头的货物清单。\n"
            "「周三午夜，老地方。别让人看见。」"
        )