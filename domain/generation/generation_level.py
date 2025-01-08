from ..base.consts import *
from ..base.base_objects import TypeEffects, Position
from ..entity import Enemy, Player, Item, Entity

import random


def generate_sectors(cur_lvl):
    while cur_lvl.room_cnt < 3:
        sector = 0

        for i in range(1, ROOMS_PER_SIDE + 1):
            for j in range(1, ROOMS_PER_SIDE + 1):
                if (
                    cur_lvl.rooms[i][j].sector == UNINITIALIZED
                    and random.random() < ROOM_CHANCE
                ):
                    cur_lvl.rooms[i][j].sector = sector
                    cur_lvl.rooms[i][j].grid_i_j = [i, j]
                    cur_lvl.sequence.append(cur_lvl.rooms[i][j])
                    cur_lvl.room_cnt += 1
                sector += 1

    cur_lvl.sequence.sort(key=lambda r: r.sector)


def generate_primary_connections(cur_lvl):
    for i in range(1, ROOMS_PER_SIDE + 1):
        for j in range(1, ROOMS_PER_SIDE + 1):
            if cur_lvl.rooms[i][j].sector != UNINITIALIZED:
                if cur_lvl.rooms[i - 1][j].sector != UNINITIALIZED:
                    cur_lvl.rooms[i][j].connections[TOP] = cur_lvl.rooms[i - 1][j]
                if cur_lvl.rooms[i][j + 1].sector != UNINITIALIZED:
                    cur_lvl.rooms[i][j].connections[RIGHT] = cur_lvl.rooms[i][j + 1]
                if cur_lvl.rooms[i + 1][j].sector != UNINITIALIZED:
                    cur_lvl.rooms[i][j].connections[BOTTOM] = cur_lvl.rooms[i + 1][j]
                if cur_lvl.rooms[i][j - 1].sector != UNINITIALIZED:
                    cur_lvl.rooms[i][j].connections[LEFT] = cur_lvl.rooms[i][j - 1]


def generate_secondary_connections(cur_lvl):
    for i in range(cur_lvl.room_cnt - 1):
        cur = cur_lvl.sequence[i]
        next = cur_lvl.sequence[i + 1]

        if (
            cur.grid_i_j[0] == next.grid_i_j[0]
            and next.connections[LEFT] == UNINITIALIZED
        ):
            cur.connections[RIGHT] = next
            next.connections[LEFT] = cur
        elif (
            cur.grid_i_j[0] - next.grid_i_j[0] == -1
            and cur.connections[BOTTOM] == UNINITIALIZED
        ):
            if (
                cur.grid_i_j[1] < next.grid_i_j[1]
                and next.connections[LEFT] == UNINITIALIZED
            ):
                cur.connections[BOTTOM] = next
                next.connections[LEFT] = cur
            elif (
                cur.grid_i_j[1] > next.grid_i_j[1]
                and next.connections[RIGHT] == UNINITIALIZED
            ):
                cur.connections[BOTTOM] = next
                next.connections[RIGHT] = cur
            elif (
                cur.grid_i_j[1] > next.grid_i_j[1]
                and cur.connections[BOTTOM] == UNINITIALIZED
                and i < cur_lvl.room_cnt - 2
            ):
                cur.connections[BOTTOM] = cur_lvl.sequence[i + 2]
                cur_lvl.sequence[i + 2].connections[RIGHT] = cur
        elif (
            cur.grid_i_j[0] - next.grid_i_j[0] == -2
            and next.connections[TOP] == UNINITIALIZED
        ):
            cur.connections[BOTTOM] = next
            next.connections[TOP] = cur


def generate_rooms_geometry(cur_lvl):
    for i in range(1, ROOMS_PER_SIDE + 1):
        for j in range(1, ROOMS_PER_SIDE + 1):
            if cur_lvl.rooms[i][j].sector != UNINITIALIZED:
                generate_corners(
                    cur_lvl.rooms[i][j], (i - 1) * SECTOR_HEIGHT, (j - 1) * SECTOR_WIDTH
                )
                generate_doors(cur_lvl.rooms[i][j])


def generate_corners(room, offset_y, offset_x):
    room.pos_top_left_bot_right[0].y = (
        random.randint(0, CORNER_VERT_RANGE - 1) + offset_y + 1
    )
    room.pos_top_left_bot_right[0].x = (
        random.randint(0, CORNER_HOR_RANGE - 1) + offset_x + 1
    )

    room.pos_top_left_bot_right[1].y = (
        SECTOR_HEIGHT - 1 - random.randint(0, CORNER_VERT_RANGE - 1) + offset_y - 1
    )
    room.pos_top_left_bot_right[1].x = (
        SECTOR_WIDTH - 1 - random.randint(0, CORNER_HOR_RANGE - 1) + offset_x - 1
    )


def generate_doors(room):
    if room.connections[TOP] != UNINITIALIZED:
        room.doors[TOP].y = room.pos_top_left_bot_right[0].y
        room.doors[TOP].x = (
            random.randint(
                0,
                room.pos_top_left_bot_right[1].x - room.pos_top_left_bot_right[0].x - 2,
            )
            + room.pos_top_left_bot_right[0].x
            + 1
        )

    if room.connections[RIGHT] != UNINITIALIZED:
        room.doors[RIGHT].y = (
            random.randint(
                0,
                room.pos_top_left_bot_right[1].y - room.pos_top_left_bot_right[0].y - 2,
            )
            + room.pos_top_left_bot_right[0].y
            + 1
        )
        room.doors[RIGHT].x = room.pos_top_left_bot_right[1].x

    if room.connections[BOTTOM] != UNINITIALIZED:
        room.doors[BOTTOM].y = room.pos_top_left_bot_right[1].y
        room.doors[BOTTOM].x = (
            random.randint(
                0,
                room.pos_top_left_bot_right[1].x - room.pos_top_left_bot_right[0].x - 2,
            )
            + room.pos_top_left_bot_right[0].x
            + 1
        )

    if room.connections[LEFT] != UNINITIALIZED:
        room.doors[LEFT].y = (
            random.randint(
                0,
                room.pos_top_left_bot_right[1].y - room.pos_top_left_bot_right[0].y - 2,
            )
            + room.pos_top_left_bot_right[0].y
            + 1
        )
        room.doors[LEFT].x = room.pos_top_left_bot_right[0].x


def generate_corridors_geometry(cur_lvl):
    for i in range(1, ROOMS_PER_SIDE + 1):
        for j in range(1, ROOMS_PER_SIDE + 1):
            cur_room = cur_lvl.rooms[i][j]

            if (
                cur_room.connections[RIGHT] != UNINITIALIZED
                and cur_room.connections[RIGHT].connections[LEFT] == cur_room
            ):
                generate_left_to_right_corridor(
                    cur_lvl,
                    cur_room,
                    cur_room.connections[RIGHT],
                    cur_lvl.corridors[cur_lvl.corridors_cnt],
                )
                cur_lvl.corridors_cnt += 1
            if cur_room.connections[BOTTOM] != UNINITIALIZED:
                grid_i_diff = (
                    cur_room.grid_i_j[0] - cur_room.connections[BOTTOM].grid_i_j[0]
                )
                grid_j_diff = (
                    cur_room.grid_i_j[1] - cur_room.connections[BOTTOM].grid_i_j[1]
                )

                if grid_i_diff == -1 and grid_j_diff > 0:
                    generate_left_turn_corridor(
                        cur_room,
                        cur_room.connections[BOTTOM],
                        cur_lvl.corridors[cur_lvl.corridors_cnt],
                    )
                    cur_lvl.corridors_cnt += 1
                elif grid_i_diff == -1 and grid_j_diff < 0:
                    generate_right_turn_corridor(
                        cur_room,
                        cur_room.connections[BOTTOM],
                        cur_lvl.corridors[cur_lvl.corridors_cnt],
                    )
                    cur_lvl.corridors_cnt += 1
                else:
                    generate_top_to_bottom_corridor(
                        cur_lvl,
                        cur_room,
                        cur_room.connections[BOTTOM],
                        cur_lvl.corridors[cur_lvl.corridors_cnt],
                    )
                    cur_lvl.corridors_cnt += 1


def generate_left_to_right_corridor(cur_lvl, left_room, right_room, corridor):
    corridor.corridor_type = LEFT_TO_RIGHT_CORRIDOR
    corridor.points_cnt = 4
    corridor.points[0] = left_room.doors[RIGHT]

    corridor.rooms_sector[0] = left_room.sector
    corridor.rooms_sector[1] = right_room.sector

    corridor.rooms_grid_i_j[0] = left_room.grid_i_j
    corridor.rooms_grid_i_j[1] = right_room.grid_i_j

    x_min = left_room.doors[RIGHT].x
    x_max = right_room.doors[LEFT].x

    for i in range(1, ROOMS_PER_SIDE + 1):
        if (
            cur_lvl.rooms[i][left_room.grid_i_j[1]].sector != UNINITIALIZED
            and i != left_room.grid_i_j[0]
        ):
            x_min = max(
                cur_lvl.rooms[i][left_room.grid_i_j[1]].pos_top_left_bot_right[1].x,
                x_min,
            )
    for i in range(1, ROOMS_PER_SIDE + 1):
        if (
            cur_lvl.rooms[i][right_room.grid_i_j[1]].sector != UNINITIALIZED
            and i != right_room.grid_i_j[0]
        ):
            x_max = min(
                cur_lvl.rooms[i][right_room.grid_i_j[1]].pos_top_left_bot_right[0].x,
                x_min,
            )

    if 0 <= x_max - x_min <= 2:
        random_center_x = x_min + 1
    elif x_max - x_min < 0:
        random_center_x = random.randint(1, x_min - x_max - 2) + x_min
    else:
        random_center_x = random.randint(1, x_max - x_min - 2) + x_min

    corridor.points[1].x, corridor.points[1].y = (
        random_center_x,
        left_room.doors[RIGHT].y,
    )
    corridor.points[2].x, corridor.points[2].y = (
        random_center_x,
        right_room.doors[LEFT].y,
    )
    corridor.points[3] = right_room.doors[LEFT]


def generate_left_turn_corridor(top_room, bottom_left_room, corridor):
    corridor.rooms_sector[0] = top_room.sector
    corridor.rooms_sector[1] = bottom_left_room.sector

    corridor.rooms_grid_i_j[0] = top_room.grid_i_j
    corridor.rooms_grid_i_j[1] = bottom_left_room.grid_i_j

    corridor.corridor_type = LEFT_TURN_CORRIDOR
    corridor.points_cnt = 3
    corridor.points[0] = top_room.doors[BOTTOM]
    corridor.points[1].x, corridor.points[1].y = (
        top_room.doors[BOTTOM].x,
        bottom_left_room.doors[RIGHT].y,
    )
    corridor.points[2] = bottom_left_room.doors[RIGHT]


def generate_right_turn_corridor(top_room, bottom_right_room, corridor):
    corridor.rooms_sector[0] = top_room.sector
    corridor.rooms_sector[1] = bottom_right_room.sector

    corridor.rooms_grid_i_j[0] = top_room.grid_i_j
    corridor.rooms_grid_i_j[1] = bottom_right_room.grid_i_j

    corridor.corridor_type = RIGHT_TURN_CORRIDOR
    corridor.points_cnt = 3
    corridor.points[0] = top_room.doors[BOTTOM]
    corridor.points[1].x, corridor.points[1].y = (
        top_room.doors[BOTTOM].x,
        bottom_right_room.doors[LEFT].y,
    )
    corridor.points[2] = bottom_right_room.doors[LEFT]


def generate_top_to_bottom_corridor(cur_lvl, top_room, bottom_room, corridor):
    corridor.corridor_type = TOP_TO_BOTTOM_CORRIDOR
    corridor.points_cnt = 4
    corridor.points[0] = top_room.doors[BOTTOM]

    corridor.rooms_sector[0] = top_room.sector
    corridor.rooms_sector[1] = bottom_room.sector

    corridor.rooms_grid_i_j[0] = top_room.grid_i_j
    corridor.rooms_grid_i_j[1] = bottom_room.grid_i_j

    y_min = top_room.doors[BOTTOM].y
    y_max = bottom_room.doors[TOP].y

    for j in range(1, ROOMS_PER_SIDE + 1):
        if cur_lvl.rooms[top_room.grid_i_j[0]][j].sector != UNINITIALIZED:
            y_min = max(
                cur_lvl.rooms[top_room.grid_i_j[0]][j].pos_top_left_bot_right[1].y,
                y_min,
            )
    for j in range(1, ROOMS_PER_SIDE + 1):
        if cur_lvl.rooms[bottom_room.grid_i_j[0]][j].sector != UNINITIALIZED:
            y_max = min(
                cur_lvl.rooms[bottom_room.grid_i_j[0]][j].pos_top_left_bot_right[0].y,
                y_max,
            )

    if 0 <= y_max - y_min <= 2:
        random_center_y = y_min + 1
    elif y_max - y_min < 0:
        random_center_y = random.randint(1, y_max - y_min - 2) + y_min
    else:
        random_center_y = random.randint(1, y_max - y_min - 2) + y_min

    corridor.points[1].x, corridor.points[1].y = (
        top_room.doors[BOTTOM].x,
        random_center_y,
    )
    corridor.points[2].x, corridor.points[2].y = (
        bottom_room.doors[TOP].x,
        random_center_y,
    )
    corridor.points[3] = bottom_room.doors[TOP]


def check_unoccupied(room, pos):
    status = UNOCCUPIED
    for i in range(room.entities_cnt):
        if (
            room.entities[i].position.x == pos.x
            and room.entities[i].position.y == pos.y
        ):
            status = OCCUPIED
            break
    return status


def generate_entity_coord(room, pos):
    top_x, top_y = room.pos_top_left_bot_right[0].x, room.pos_top_left_bot_right[0].y
    bot_x, bot_y = room.pos_top_left_bot_right[1].x, room.pos_top_left_bot_right[1].y

    while True:
        pos.x = random.randint(1, bot_x - top_x - 1) + top_x
        pos.y = random.randint(1, bot_y - top_y - 1) + top_y

        if check_unoccupied(room, pos) == UNOCCUPIED:
            break


def generate_player_pos(cur_lvl):
    room_index = random.randint(0, cur_lvl.room_cnt - 1)
    spawn_room = cur_lvl.sequence[room_index]
    player_pos = Position()

    generate_entity_coord(spawn_room, player_pos)

    player = Player(player_pos, spawn_room.sector, spawn_room.grid_i_j)

    spawn_room.visited = True
    spawn_room.visible = True

    spawn_room.entities[spawn_room.entities_cnt] = player
    spawn_room.entities_cnt += 1


def generate_exit(cur_lvl):
    room_index = random.randint(0, cur_lvl.room_cnt - 1)
    exit_room = cur_lvl.sequence[room_index]
    exit_pos = Position()

    generate_entity_coord(exit_room, exit_pos)

    exit_entity = Entity(
        EXIT, EXIT_CHAR, exit_pos, exit_room.sector, exit_room.grid_i_j
    )

    exit_room.entities[exit_room.entities_cnt] = exit_entity
    exit_room.entities_cnt += 1


def generate_enemies(cur_lvl, level_number):
    for i in range(cur_lvl.room_cnt):
        enemies_cnt = random.randint(0, 1 + level_number // 6)

        for j in range(enemies_cnt):

            enemy_pos = Position()

            generate_entity_coord(cur_lvl.sequence[i], enemy_pos)

            enemy = Enemy(
                random.choice(ENEMY_POOL),
                enemy_pos,
                cur_lvl.sequence[i].sector,
                cur_lvl.sequence[i].grid_i_j,
                3,
            )

            if enemy.symbol == ZOMBIE:
                enemy.max_health = 10 + (level_number // 5) * 5
                enemy.strength = 2 + (level_number // 5) * 1
            elif enemy.symbol == VAMPIRE:
                enemy.max_health = 10 + (level_number // 5) * 5
                enemy.strength = 1 + (level_number // 10) * 1
                enemy.agility = 1 + (level_number // 5) * 1
                enemy.hostility = 4

                enemy.increase_effect(TypeEffects.VAMPIRING, -1)
                enemy.increase_effect(TypeEffects.DODGE, -1)
            elif enemy.symbol == GHOST:
                enemy.max_health = 5 + (level_number // 5) * 5
                enemy.strength = 1 + (level_number // 10) * 1
                enemy.agility = 1 + (level_number // 5) * 1
                enemy.hostility = 2
            elif enemy.symbol == ORC:
                enemy.max_health = 15 + (level_number // 5) * 5
                enemy.strength = 4 + (level_number // 5) * 1
            elif enemy.symbol == SNAKE_MAGE:
                enemy.max_health = 7 + (level_number // 5) * 5
                enemy.strength = 1 + (level_number // 5) * 1
                enemy.agility = 2 + (level_number // 5) * 1

                enemy.increase_effect(TypeEffects.EUTHANASIA, -1)
            elif enemy.symbol == MIMIC:
                enemy.max_health = 15 + (level_number // 5) * 5
                enemy.strength = 1 + (level_number // 10) * 1
                enemy.agility = 1 + (level_number // 5) * 1
                enemy.hostility = 1

            cur_lvl.sequence[i].entities[cur_lvl.sequence[i].entities_cnt] = enemy
            cur_lvl.sequence[i].entities_cnt += 1


def generate_items(cur_lvl, level_number):
    for i in range(cur_lvl.room_cnt):
        items_cnt = random.randint(0, 1 + (MAX_LEVELS - 1 - level_number) // 11)

        for j in range(items_cnt):

            item_pos = Position()

            generate_entity_coord(cur_lvl.sequence[i], item_pos)

            item = Item(
                random.choice(ITEM_POOL),
                item_pos,
                cur_lvl.sequence[i].sector,
                cur_lvl.sequence[i].grid_i_j,
            )

            if item.symbol == FOOD:
                item.health = random.randint(25, 25 + (level_number // 5) * 25)
            elif item.symbol == SCROLL:
                chance = random.random()
                if chance < 0.33:
                    item.max_health = random.randint(25, 25 + (level_number // 5) * 25)
                elif 0.33 < chance < 0.66:
                    item.agility = random.randint(1, 1 + (level_number // 6) * 2)
                else:
                    item.strength = random.randint(2, 2 + (level_number // 6) * 2)
            elif item.symbol == POTION:
                chance = random.random()
                if chance < 0.33:
                    item.effects[TypeEffects.MAX_HEALTH] = random.randint(
                        30, 30 + (level_number // 3) * 5
                    )
                elif 0.33 < chance < 0.66:
                    item.effects[TypeEffects.AGILITY] = random.randint(
                        30, 30 + (level_number // 3) * 5
                    )
                else:
                    item.effects[TypeEffects.STRENGTH] = random.randint(
                        30, 30 + (level_number // 3) * 5
                    )
            elif item.symbol == WEAPON:
                item.strength = random.randint(3, 3 + (level_number // 5) * 3)
            elif item.symbol == TREASURE:
                item.price = random.randint(50, 50 + (level_number // 3) * 50)

            cur_lvl.sequence[i].entities[cur_lvl.sequence[i].entities_cnt] = item
            cur_lvl.sequence[i].entities_cnt += 1
