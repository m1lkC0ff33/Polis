"""
对话库

存储所有NPC的对话模板。每条对话有触发条件和文本。
"""

# 对话条目格式：
# {
#     "condition": 条件函数，接收 (event_mgr, player) 返回 True/False,
#     "text": 对话文本模板，可用 {name} 占位,
# }

# ── 通用对话（所有普通NPC共享）──

COMMON_DIALOGUES = [
    {
        "condition": lambda em, p: em.stage.value >= 4,  # 任何事件完成后
        "text": [
            "「这城市最近不太对劲。」{name}摇了摇头。",
            "「我听说有人在查走私的事。」{name}压低声音。",
            "「市长的脸色最近很难看。」{name}说。",
        ],
    },
    {
        "condition": lambda em, p: em.stage.value >= 1,  # 有事件在进行
        "text": [
            "「最近城里来了不少陌生人。」{name}随口说道。",
            "「你也在打听那些事？」{name}警惕地看了你一眼。",
        ],
    },
    {
        "condition": lambda em, p: True,  # 无条件——兜底
        "text": [
            "「今天天气不错。」{name}说。",
            "「忙啊，忙得脚不沾地。」{name}擦了把汗。",
            "「你是新来的？看着面生。」{name}打量着你。",
            "「有什么需要帮忙的吗？」{name}问道。",
        ],
    },
]

# ── 带事件提示的对话（特定条件触发）──

HINT_DIALOGUES = [
    {
        "condition": lambda em, p: em.stage == em.__class__.CLUE_SEARCHING,
        "text": [
            "「找那个陌生人？」{name}朝{direction}指了指。「往那边走走看。」",
            "「你要找的人大概在{direction}方向。」{name}小声说。",
        ],
    },
    {
        "condition": lambda em, p: em.stage == em.__class__.CLUE_FOUND,
        "text": [
            "「找到你要的东西了？赶紧去找那个人吧。」{name}说。",
        ],
    },
]