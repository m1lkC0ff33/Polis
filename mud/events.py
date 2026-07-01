"""
事件系统

管理多个事件链、任务状态、NPC对话条件。
"""

import random
from enum import Enum


class EventStage(Enum):
    IDLE = 0
    ACCEPTED = 1
    CLUE_SEARCHING = 2
    CLUE_FOUND = 3
    RESOLVED = 4


class Quest:
    """单个任务的数据结构"""
    def __init__(self, quest_id: str, title: str, description: str,
                 npc_name: str, clue_type: str,
                 clue_x: int, clue_y: int, npc_x: int, npc_y: int):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.npc_name = npc_name
        self.clue_type = clue_type
        self.clue_x = clue_x
        self.clue_y = clue_y
        self.npc_x = npc_x
        self.npc_y = npc_y
        self.stage = EventStage.IDLE
        self.is_active = False
        self.is_completed = False

    def get_status_text(self) -> str:
        type_names = {
            "residential": "居住区",
            "commercial": "商业区",
            "government": "行政区",
            "industrial": "工业区",
            "park": "公园",
        }
        if self.stage == EventStage.IDLE:
            return f"[ ] {self.title}"
        elif self.stage in (EventStage.ACCEPTED, EventStage.CLUE_SEARCHING):
            hint = type_names.get(self.clue_type, self.clue_type)
            return f"[!] {self.title} — 去{hint}找线索"
        elif self.stage == EventStage.CLUE_FOUND:
            return f"[?] {self.title} — 回去找 {self.npc_name}"
        elif self.stage == EventStage.RESOLVED:
            return f"[✓] {self.title} — 已完成"


class EventManager:
    def __init__(self, city_grid, rng: random.Random):
        self.grid = city_grid
        self.rng = rng
        self.quests: list[Quest] = []
        self.stage = EventStage.IDLE  # 兼容旧代码

        # 生成2-3个任务
        self._generate_quests()

    def _generate_quests(self):
        from city.tiles import WATER

        # 任务模板
        quest_templates = [
            {
                "quest_id": "smuggle",
                "title": "码头走私",
                "description": "调查码头走私的线索",
                "clue_hint": "找个工业区或商业区翻翻",
            },
            {
                "quest_id": "mayor_secret",
                "title": "市长的秘密",
                "description": "找到市长受贿的证据",
                "clue_hint": "去行政区附近找找",
            },
            {
                "quest_id": "missing_merchant",
                "title": "失踪的商人",
                "description": "寻找失踪商人的下落",
                "clue_hint": "居住区或许有人知道什么",
            },
        ]

        # 随机选2-3个
        count = self.rng.randint(2, 3)
        chosen = self.rng.sample(quest_templates, count)

        # 为每个任务分配NPC和线索位置
        used_positions = set()
        for template in chosen:
            npc_x, npc_y = self._random_empty_spot(used_positions)
            used_positions.add((npc_x, npc_y))
            clue_x, clue_y = self._random_empty_spot(used_positions)
            used_positions.add((clue_x, clue_y))

            # 标记格子
            self.grid.get_cell(npc_x, npc_y).has_event_npc = True
            self.grid.get_cell(clue_x, clue_y).clue_target = True

            # 线索类型
            clue_type = self.grid.get_cell(clue_x, clue_y).tile.type_id

            # 随机NPC名字
            from data.names import random_npc_name, random_trait
            npc_name = random_npc_name(self.rng)

            quest = Quest(
                quest_id=template["quest_id"],
                title=template["title"],
                description=template["clue_hint"],
                npc_name=npc_name,
                clue_type=clue_type,
                clue_x=clue_x,
                clue_y=clue_y,
                npc_x=npc_x,
                npc_y=npc_y,
            )
            self.quests.append(quest)

    def _random_empty_spot(self, used_positions: set) -> tuple:
        from city.tiles import WATER
        candidates = []
        for y in range(self.grid.size):
            for x in range(self.grid.size):
                cell = self.grid.get_cell(x, y)
                if cell.tile and cell.tile is not WATER:
                    if (x, y) not in used_positions:
                        candidates.append((x, y))
        return self.rng.choice(candidates)

    def get_npc_at(self, x: int, y: int) -> Quest | None:
        """返回该位置的事件NPC对应的任务（如果有）"""
        for quest in self.quests:
            if quest.npc_x == x and quest.npc_y == y:
                return quest
        return None

    def get_clue_at(self, x: int, y: int) -> Quest | None:
        """返回该位置的线索对应的任务（如果有）"""
        for quest in self.quests:
            if quest.clue_x == x and quest.clue_y == y:
                return quest
        return None

    def get_active_quests(self) -> list[Quest]:
        return [q for q in self.quests if q.stage != EventStage.RESOLVED]

    def get_completed_quests(self) -> list[Quest]:
        return [q for q in self.quests if q.stage == EventStage.RESOLVED]

    @property
    def npc_x(self):
        """兼容旧代码——返回第一个可用任务的NPC位置"""
        for q in self.quests:
            if q.stage != EventStage.RESOLVED:
                return q.npc_x
        return self.quests[0].npc_x if self.quests else 0

    @property
    def npc_y(self):
        for q in self.quests:
            if q.stage != EventStage.RESOLVED:
                return q.npc_y
        return self.quests[0].npc_y if self.quests else 0

    @property
    def npc_name(self):
        for q in self.quests:
            if q.stage != EventStage.RESOLVED:
                return q.npc_name
        return "陌生人"

    @property
    def npc_trait(self):
        return "神秘"

    @property
    def clue_x(self):
        for q in self.quests:
            if q.stage in (EventStage.CLUE_SEARCHING, EventStage.CLUE_FOUND):
                return q.clue_x
        return 0

    @property
    def clue_y(self):
        for q in self.quests:
            if q.stage in (EventStage.CLUE_SEARCHING, EventStage.CLUE_FOUND):
                return q.clue_y
        return 0