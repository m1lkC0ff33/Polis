import random

def random_landmark(tile_type_id: str, rng: random.Random) -> str:
    from data.names_data import LANDMARK_NAMES
    pool = LANDMARK_NAMES.get(tile_type_id, ["未知地点"])
    return rng.choice(pool)

def random_npc_name(rng: random.Random) -> str:
    from data.names_data import (SURNAMES, GIVEN_NAMES_MALE,
                                  GIVEN_NAMES_FEMALE, WESTERN_FIRST, WESTERN_LAST)
    if rng.random() < 0.7:
        surname = rng.choice(SURNAMES)
        pool = GIVEN_NAMES_MALE if rng.random() < 0.5 else GIVEN_NAMES_FEMALE
        given = rng.choice(pool)
        return surname + given
    else:
        return rng.choice(WESTERN_FIRST) + " " + rng.choice(WESTERN_LAST)

def random_trait(rng: random.Random) -> str:
    from data.names_data import TRAITS
    return rng.choice(TRAITS)

def random_profession(tile_type_id: str, rng: random.Random) -> str:
    from data.names_data import PROFESSIONS
    pool = PROFESSIONS.get(tile_type_id, ["居民"])
    return rng.choice(pool)

def assign_names_to_city(grid, rng: random.Random):
    from data.names_data import LANDMARK_NAMES

    available_names = {
        type_id: list(pool) for type_id, pool in LANDMARK_NAMES.items()
    }

    for y in range(grid.size):
        for x in range(grid.size):
            cell = grid.get_cell(x, y)
            if cell.tile is None:
                continue

            type_id = cell.tile.type_id

            pool = available_names.get(type_id, [])
            if pool:
                idx = rng.randint(0, len(pool) - 1)
                cell.landmark = pool.pop(idx)
            else:
                fallback = LANDMARK_NAMES.get(type_id, ["地点"])[0]
                cell.landmark = f"{fallback}({rng.randint(2,9)})"

            cell.npcs = []
            npc_count = rng.choices([1, 2], weights=[0.7, 0.3])[0]
            for _ in range(npc_count):
                npc = {
                    "name": random_npc_name(rng),
                    "trait": random_trait(rng),
                    "profession": random_profession(type_id, rng),
                }
                cell.npcs.append(npc)

            # 重建描述
            desc = cell.tile.description
            if cell.landmark:
                desc += f" 这里坐落着【{cell.landmark}】。"
            if cell.npcs:
                for npc in cell.npcs:
                    desc += f" {npc['trait']}的{npc['profession']}{npc['name']}正在此处。"
            cell.description = desc