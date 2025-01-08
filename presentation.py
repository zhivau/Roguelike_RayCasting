from domain.base.consts import *
from domain.base.base_objects import TypeEffects, TypeCommand, Position

import curses
import math


class View:

    def __init__(self, screen, game_session):
        self.screen = screen

        self.game_session = game_session
        self.player = self.game_session.player

        self.sequence = []
        for i in range(self.game_session.current_level.room_cnt):
            self.sequence.append([self.game_session.current_level.sequence[i], False])
        self.corridors = []
        for i in range(self.game_session.current_level.corridors_cnt):
            self.corridors.append([self.game_session.current_level.corridors[i], False])

        self.playground = [
            [[OUTER_AREA_CHAR, 1] for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)
        ]

        self.fill_area = []
        self.vertices = self.game_session.current_level.get_vertices()
        self.walls = self.game_session.current_level.get_walls()

        self.all_game_stats = []

    def to_dict(self):
        result = dict()

        result["sequence"] = []
        for room, visited in self.sequence:
            result["sequence"].append((room.sector, visited))

        result["corridors"] = []
        for corridor, visited in self.corridors:
            result["corridors"].append((corridor.rooms_sector, visited))

        result["all_game_stats"] = self.all_game_stats

        return result

    def load_data(self, **kwargs):
        for room, visited in zip(self.sequence, kwargs["sequence"]):
            room[1] = visited[1]

        for corridor, visited in zip(self.corridors, kwargs["corridors"]):
            corridor[1] = visited[1]

        self.all_game_stats = kwargs["all_game_stats"]

    def print_map(self):
        for i in range(MAP_HEIGHT):
            for j in range(MAP_WIDTH):
                self.screen.attron(curses.color_pair(self.playground[i][j][1]))
                self.screen.addch(i, j, self.playground[i][j][0])
                self.screen.attroff(curses.color_pair(self.playground[i][j][1]))

        self.print_backpack()
        self.print_weapon()
        self.print_player_stats()
        self.print_player_effects()
        self.print_game_stats()
        self.print_user_info()

    def print_user_info(self):
        self.screen.addstr(0, MAP_WIDTH + 40, f"WASD to move")
        self.screen.addstr(1, MAP_WIDTH + 40, f"H to choose weapon from backpack")
        self.screen.addstr(2, MAP_WIDTH + 40, f"I to drop current weapon")
        self.screen.addstr(3, MAP_WIDTH + 40, f"J to choose food from backpack")
        self.screen.addstr(5, MAP_WIDTH + 40, f"K to choose potion from backpack")
        self.screen.addstr(6, MAP_WIDTH + 40, f"E to choose scroll from backpack")
        self.screen.addstr(7, MAP_WIDTH + 40, f"B to save and quit")
        self.screen.addstr(8, MAP_WIDTH + 40, f"Q to quit")

        self.screen.addstr(10, MAP_WIDTH + 40, f"@ - player")

        self.screen.addstr(12, MAP_WIDTH + 40, f"$ - treasure")
        self.screen.addstr(13, MAP_WIDTH + 40, f"/ - weapon")
        self.screen.addstr(14, MAP_WIDTH + 40, f"? - scroll")
        self.screen.addstr(15, MAP_WIDTH + 40, f"! - potion")
        self.screen.addstr(16, MAP_WIDTH + 40, f"* - food")

        self.screen.addstr(18, MAP_WIDTH + 40, f"O - orc")
        self.screen.addstr(19, MAP_WIDTH + 40, f"g - ghost")
        self.screen.addstr(20, MAP_WIDTH + 40, f"m - mimik")
        self.screen.addstr(21, MAP_WIDTH + 40, f"v- vampire")
        self.screen.addstr(22, MAP_WIDTH + 40, f"s- mage snake")
        self.screen.addstr(22, MAP_WIDTH + 40, f"z- zombie")

    def print_game_stats(self):
        self.screen.addstr(
            MAP_HEIGHT,
            0,
            f"current level: {self.game_session.dungeon.level_number + 1}",
        )

        self.screen.addstr(
            MAP_HEIGHT + 12,
            0,
            f"current game: {self.game_session.game_stats}",
        )

        for index, item in enumerate(self.all_game_stats, 1):
            self.screen.addstr(
                MAP_HEIGHT + 12 + index,
                0,
                f"{index}: {self.all_game_stats[index - 1]}",
            )

    def print_backpack(self):
        self.screen.addstr(MAP_HEIGHT + 2, 0, "backpack: ")

        for index, item in enumerate(self.player.backpack.items, 1):
            self.screen.addstr(MAP_HEIGHT + 2, 5 + index * 7, f"{index}) {item.symbol}")

    def print_weapon(self):
        self.screen.addstr(
            MAP_HEIGHT + 4,
            0,
            f"weapon: {self.player.weapon.strength if self.player.weapon != UNINITIALIZED else '-'}",
        )

    def print_player_stats(self):
        self.screen.addstr(
            MAP_HEIGHT + 6,
            0,
            f"health: {self.player.health}/{self.player.max_health} agility: {self.player.agility}  strength: {self.player.strength}",
        )
        self.screen.addstr(MAP_HEIGHT + 8, 0, f"treasures: {self.player.treasures}")

    def print_player_effects(self):
        self.screen.addstr(MAP_HEIGHT + 10, 0, "effects: ")

        for index, type_effect in enumerate(self.player.effects, 1):
            self.screen.addstr(
                MAP_HEIGHT + 10,
                index * 15,
                str(type_effect) + ": " + str(self.player.effects[type_effect]),
            )

    def update_map(self):
        for room in self.sequence:
            if room[0].check_point_in_room(self.player.position):
                room[1] = True

        for corridor in self.corridors:
            if corridor[0].check_point_in_corridor(self.player.position):
                corridor[1] = True

        self.corridors_to_map()
        self.rooms_to_map()
        self.entities_to_map()

    def update_level(self):
        self.player = self.game_session.player

        self.sequence = []
        for i in range(self.game_session.current_level.room_cnt):
            self.sequence.append([self.game_session.current_level.sequence[i], False])

        self.corridors = []
        for i in range(self.game_session.current_level.corridors_cnt):
            self.corridors.append([self.game_session.current_level.corridors[i], False])

        self.vertices = self.game_session.current_level.get_vertices()
        self.walls = self.game_session.current_level.get_walls()

    def clear_map(self):
        for i in range(MAP_HEIGHT):
            for j in range(MAP_WIDTH):
                self.playground[i][j][0] = OUTER_AREA_CHAR
                self.playground[i][j][1] = 1

    def clear_user_interface(self):
        for i in range(MAP_HEIGHT, MAP_HEIGHT + 15):
            for j in range(MAP_WIDTH + 50):
                self.screen.addch(i, j, " ")

        for i in range(0, int(MAP_HEIGHT / 2)):
            for j in range(MAP_WIDTH, MAP_WIDTH + 50):
                self.screen.addch(i, j, " ")

    def rooms_to_map(self):
        for room in self.sequence:
            if room[1]:

                top_room_corner = room[0].pos_top_left_bot_right[0]
                bot_room_corner = room[0].pos_top_left_bot_right[1]

                self.rectangle_to_map(top_room_corner, bot_room_corner)
                self.fill_rectangle(top_room_corner, bot_room_corner)

                for pos in room[0].doors:
                    if pos.x != UNINITIALIZED and pos.y != UNINITIALIZED:
                        self.playground[pos.y][pos.x][0] = DOOR_CHAR

    def entities_to_map(self):
        for room in self.sequence:
            if room[1]:
                for i in range(room[0].entities_cnt):
                    entity = room[0].entities[i]
                    if self.is_visible_entity(entity) and entity.entity_type != PLAYER:
                        if entity.symbol != GHOST or (
                            entity.symbol == GHOST
                            and TypeEffects.INVISIBILITY not in entity.effects
                        ):
                            self.playground[entity.position.y][entity.position.x][
                                0
                            ] = entity.symbol
                        if entity.symbol == ZOMBIE:
                            self.playground[entity.position.y][entity.position.x][1] = 7
                        elif entity.symbol == VAMPIRE:
                            self.playground[entity.position.y][entity.position.x][1] = 6
                        elif entity.symbol == ORC:
                            self.playground[entity.position.y][entity.position.x][1] = 8
                        else:
                            self.playground[entity.position.y][entity.position.x][1] = 5

        self.playground[self.player.position.y][self.player.position.x][
            0
        ] = self.player.symbol

    def is_visible_entity(self, entity):
        result = False
        for point in self.fill_area:
            if point == entity.position:
                result = True
                break

        return result

    def update_area(self):
        self.vertices = self.game_session.current_level.get_vertices()

        intersection_points = get_intersection_points(
            self.vertices, self.walls, self.player
        )

        edges_area = []
        for point in intersection_points:
            edges_area.append(
                get_area_edge_bresenham(
                    self.player.position.x, self.player.position.y, point.x, point.y
                )
            )

        self.fill_area = get_fill_area(edges_area, self.player)

        for i in range(MAP_HEIGHT):
            for j in range(MAP_WIDTH):
                self.playground[i][j][1] = 1

        for point in self.fill_area:
            self.playground[point.y][point.x][1] = 5

    def rectangle_to_map(self, top, bot):
        self.playground[top.y][top.x][0] = WALL_CHAR

        for i in range(top.x + 1, bot.x + 1):
            self.playground[top.y][i][0] = WALL_CHAR

        for i in range(top.y + 1, bot.y):
            self.playground[i][top.x][0] = WALL_CHAR
            self.playground[i][bot.x][0] = WALL_CHAR

        for i in range(top.x, bot.x + 1):
            self.playground[bot.y][i][0] = WALL_CHAR

    def fill_rectangle(self, top, bot):
        for i in range(top.y + 1, bot.y):
            for j in range(top.x + 1, bot.x):
                self.playground[i][j][0] = INNER_AREA_CHAR

    def corridors_to_map(self):
        for corridor in self.corridors:
            if corridor[0].corridor_type == LEFT_TO_RIGHT_CORRIDOR and corridor[1]:
                self.draw_horizontal_line(corridor[0].points[0], corridor[0].points[1])
                self.draw_vertical_line(corridor[0].points[1], corridor[0].points[2])
                self.draw_horizontal_line(corridor[0].points[2], corridor[0].points[3])
            elif corridor[0].corridor_type == LEFT_TURN_CORRIDOR and corridor[1]:
                self.draw_vertical_line(corridor[0].points[0], corridor[0].points[1])
                self.draw_horizontal_line(corridor[0].points[1], corridor[0].points[2])
            elif corridor[0].corridor_type == RIGHT_TURN_CORRIDOR and corridor[1]:
                self.draw_vertical_line(corridor[0].points[0], corridor[0].points[1])
                self.draw_horizontal_line(corridor[0].points[1], corridor[0].points[2])
            elif corridor[0].corridor_type == TOP_TO_BOTTOM_CORRIDOR and corridor[1]:
                self.draw_vertical_line(corridor[0].points[0], corridor[0].points[1])
                self.draw_horizontal_line(corridor[0].points[1], corridor[0].points[2])
                self.draw_vertical_line(corridor[0].points[2], corridor[0].points[3])

    def draw_horizontal_line(self, first_dot, second_dot):
        for x in range(
            min(first_dot.x, second_dot.x), max(first_dot.x, second_dot.x) + 1
        ):
            self.playground[first_dot.y][x][0] = CORRIDOR_CHAR

        for x in range(
            min(first_dot.x, second_dot.x), max(first_dot.x, second_dot.x) + 1
        ):
            if self.playground[first_dot.y + 1][x][0] != CORRIDOR_CHAR:
                self.playground[first_dot.y + 1][x][0] = WALL_CHAR
            if self.playground[first_dot.y - 1][x][0] != CORRIDOR_CHAR:
                self.playground[first_dot.y - 1][x][0] = WALL_CHAR

    def draw_vertical_line(self, first_dot, second_dot):
        for y in range(
            min(first_dot.y, second_dot.y), max(first_dot.y, second_dot.y) + 1
        ):
            self.playground[y][first_dot.x][0] = CORRIDOR_CHAR

        for y in range(
            min(first_dot.y, second_dot.y), max(first_dot.y, second_dot.y) + 1
        ):
            if self.playground[y][first_dot.x + 1][0] != CORRIDOR_CHAR:
                self.playground[y][first_dot.x + 1][0] = WALL_CHAR
            if self.playground[y][first_dot.x - 1][0] != CORRIDOR_CHAR:
                self.playground[y][first_dot.x - 1][0] = WALL_CHAR

    def get_signal(self):
        key = self.screen.getch()
        result = TypeCommand.NOSIG
        index_item = UNINITIALIZED

        move_up = {ord("w"), ord("W"), ord("ц"), ord("Ц")}
        move_down = {ord("s"), ord("S"), ord("ы"), ord("Ы")}
        move_left = {ord("a"), ord("A"), ord("ф"), ord("Ф")}
        move_right = {ord("d"), ord("D"), ord("в"), ord("В")}
        get_weapons = {ord("h"), ord("H"), ord("р"), ord("Р")}
        get_food = {ord("j"), ord("J"), ord("о"), ord("О")}
        get_potion = {ord("k"), ord("K"), ord("л"), ord("Л")}
        get_scrolls = {ord("e"), ord("E"), ord("у"), ord("У")}
        drop_weapon = {ord("i"), ord("I"), ord("г"), ord("Г")}
        exit_game = {ord("q"), ord("Q"), ord("й"), ord("Й")}
        save_game = {ord("b"), ord("B"), ord("и"), ord("И")}
        new_game = {ord("\n")}

        if key in move_up:
            result = TypeCommand.UP
        elif key in move_down:
            result = TypeCommand.DOWN
        elif key in move_left:
            result = TypeCommand.LEFT
        elif key in move_right:
            result = TypeCommand.RIGHT
        elif key in get_weapons:
            weapons = self.player.backpack.get_list_weapons()

            if weapons:
                result = TypeCommand.GETWEAPONS

                self.screen.addstr(0, MAP_WIDTH + 1, "choose weapon: ")

                index_item = self.choose_item(weapons)
                if index_item == UNINITIALIZED:
                    result = TypeCommand.NOSIG
        elif key in get_food:
            foods = self.player.backpack.get_list_foods()

            if foods:
                result = TypeCommand.GETFOODS

                self.screen.addstr(0, MAP_WIDTH + 1, "choose food: ")

                index_item = self.choose_item(foods)
                if index_item == UNINITIALIZED:
                    result = TypeCommand.NOSIG
        elif key in get_potion:
            potions = self.player.backpack.get_list_potions()

            if potions:
                result = TypeCommand.GETPOTIONS

                self.screen.addstr(0, MAP_WIDTH + 1, "choose potion: ")

                index_item = self.choose_item(potions)
                if index_item == UNINITIALIZED:
                    result = TypeCommand.NOSIG
        elif key in get_scrolls:
            scrolls = self.player.backpack.get_list_scrolls()

            if scrolls:
                result = TypeCommand.GETSCROLLS

                self.screen.addstr(0, MAP_WIDTH + 1, "choose scroll: ")

                index_item = self.choose_item(scrolls)
                if index_item == UNINITIALIZED:
                    result = TypeCommand.NOSIG
        elif key in exit_game:
            result = TypeCommand.EXITGAME
        elif key in save_game:
            result = TypeCommand.SAVEGAME
        elif key in drop_weapon:
            result = TypeCommand.DROPWEAPON
        elif key in new_game:
            result = TypeCommand.NEWGAME

        return result, index_item

    def choose_item(self, items):
        numbers = [
            ord("1"),
            ord("!"),
            ord("2"),
            ord('"'),
            ord("3"),
            ord("№"),
            ord("4"),
            ord(";"),
            ord("5"),
            ord("%"),
            ord("6"),
            ord(":"),
            ord("7"),
            ord("?"),
            ord("8"),
            ord("*"),
            ord("9"),
            ord("("),
        ]

        exit_game = {ord("q"), ord("Q"), ord("й"), ord("Й")}

        for index, item in enumerate(items, 1):
            if item[1].symbol != POTION:
                self.screen.addstr(
                    index,
                    MAP_WIDTH + 1,
                    f"{index}) {item[1].symbol} mh:{item[1].max_health} h:{item[1].health} s:{item[1].strength} a:{item[1].agility}",
                )
            else:
                self.screen.addstr(
                    index,
                    MAP_WIDTH + 1,
                    f"{index})",
                )
                step = 0
                for effect, duration in item[1].effects.items():
                    self.screen.addstr(
                        index + step, MAP_WIDTH + 4, f"{effect.value}: {duration}"
                    )
                    step += 1

        self.screen.refresh()

        index_item = self.screen.getch()
        while index_item not in numbers[: len(items) * 2]:
            if index_item in exit_game:
                break
            index_item = self.screen.getch()

        if index_item in exit_game:
            index_result = UNINITIALIZED
        else:
            index_result = char_code_to_digit(index_item)
        return index_result


def get_offset_ray_point(ray, angle):
    offset_ray_point = Position()
    offset_ray_point.x = (
        (ray[1].x - ray[0].x) * math.cos(angle)
        - (ray[1].y - ray[0].y) * math.sin(angle)
        + ray[0].x
    )
    offset_ray_point.y = (
        (ray[1].y - ray[0].y) * math.cos(angle)
        - (ray[1].x - ray[0].x) * math.sin(angle)
        + ray[0].y
    )
    return offset_ray_point


def get_closest_intersection_point(ray, walls):
    smallest_r = float("inf")
    intersection_point = None

    for wall in walls:

        a, b = wall
        c, d = ray

        denominator = (d.x - c.x) * (b.y - a.y) - (b.x - a.x) * (d.y - c.y)

        if denominator == 0:
            continue

        r = ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) / denominator
        if r < 0 or smallest_r < r:
            continue

        s = ((a.x - c.x) * (d.y - c.y) - (d.x - c.x) * (a.y - c.y)) / denominator
        if s < 0 or s > 1:
            continue

        smallest_r = r
        intersection_point = Position()
        intersection_point.x = s * (b.x - a.x) + a.x
        intersection_point.y = s * (b.y - a.y) + a.y

    return intersection_point


def get_intersection_points(vertices, walls, player):

    intersection_points = []
    for vertex in vertices:
        extra_offset_point1 = get_offset_ray_point(
            [player.position, vertex], -ANGLE_OFFSET
        )
        extra_offset_point2 = get_offset_ray_point(
            [player.position, vertex], ANGLE_OFFSET
        )

        closest_point = get_closest_intersection_point([player.position, vertex], walls)
        extra_closest_point1 = get_closest_intersection_point(
            [player.position, extra_offset_point1], walls
        )
        extra_closest_point2 = get_closest_intersection_point(
            [player.position, extra_offset_point2], walls
        )

        if closest_point is not None:
            intersection_points.append(closest_point)
        if extra_closest_point1 is not None:
            intersection_points.append(extra_closest_point1)
        if extra_closest_point2 is not None:
            intersection_points.append(extra_closest_point2)

    intersection_points.sort(
        key=lambda p: math.atan2(p.y - player.position.y, p.x - player.position.x)
    )
    return intersection_points


def get_area_edge_bresenham(x0, y0, x1, y1):
    edge_area = []

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x = x0
    y = y0
    n = 1 + dx + dy
    x_inc = 1 if x1 > x0 else -1
    y_inc = 1 if y1 > y0 else -1
    error = dx - dy
    dx *= 2
    dy *= 2

    for _ in range(int(n)):
        edge_area.append(Position(x, y))

        if error > 0:
            x += x_inc
            error -= dy
        else:
            y += y_inc
            error += dx

    return edge_area


def get_fill_area(edges, player):
    fill_area = []

    edge_points = [point for edge in edges for point in edge]

    for point in edge_points:
        if (point.x - player.position.x) ** 2 + (
            point.y - player.position.y
        ) ** 2 <= RADIUS_VIEW**2:
            fill_area.append(point)
    return fill_area


def char_code_to_digit(char_code):
    result = UNINITIALIZED

    numbers = [
        (ord("1"), ord("!")),
        (ord("2"), ord('"')),
        (ord("3"), ord("№")),
        (ord("4"), ord(";")),
        (ord("5"), ord("%")),
        (ord("6"), ord(":")),
        (ord("7"), ord("?")),
        (ord("8"), ord("*")),
        (ord("9"), ord("(")),
    ]

    for number_var1, number_var2 in numbers:
        if number_var1 == char_code or number_var2 == char_code:
            result = int(chr(number_var1))
            break

    return result
