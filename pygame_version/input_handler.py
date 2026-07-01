"""输入处理"""

import pygame


def handle_input(event) -> str | None:
    """
    处理单个事件，返回指令字符串。
    返回 None 表示无操作。
    """
    if event.type != pygame.KEYDOWN:
        return None

    key = event.key

    # 移动
    if key in (pygame.K_UP, pygame.K_w):
        return "move north"
    elif key in (pygame.K_DOWN, pygame.K_s):
        return "move south"
    elif key in (pygame.K_LEFT, pygame.K_a):
        return "move west"
    elif key in (pygame.K_RIGHT, pygame.K_d):
        return "move east"

    # 功能键
    elif key == pygame.K_l:
        return "look"
    elif key == pygame.K_m:
        return "map"
    elif key == pygame.K_t:
        return "talk"
    elif key == pygame.K_i:
        return "investigate"
    elif key == pygame.K_q:
        return "quest"
    elif key == pygame.K_ESCAPE:
        return "quit"
    elif key == pygame.K_h:
        return "help"

    return None