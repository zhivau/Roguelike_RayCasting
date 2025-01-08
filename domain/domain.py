from .base.base_objects import Position, TypeEffects, TypeCommand, GameStatus
from .generation.dungeon import Dungeon
from .base.consts import *

import random
import math


class GameSession:

    def __init__(self):
        self.dungeon = Dungeon()

        self.dungeon.generate_level()
        self.current_level = self.dungeon.levels[self.dungeon.level_number]

        self.player = UNINITIALIZED

        for i in range(self.current_level.room_cnt):
            for j in range(self.current_level.sequence[i].entities_cnt):
                cur_entity = self.current_level.sequence[i].entities[j]
                if cur_entity.entity_type == PLAYER:
                    self.player = cur_entity
                    break

        self.game_stats = {
            "sum_treasures": 0,
            "treasures": 0,
            "level_number": 0,
            "killed_enemies": 0,
            "foods": 0,
            "scrolls": 0,
            "potions": 0,
            "misses": 0,
            "hits": 0,
            "moves": 0,
        }

    def to_dict(self):
        result = self.__dict__.copy()
        del result["current_level"]
        return result

    def load_data(self, **kwargs):
        self.dungeon.load_data(**kwargs["dungeon"])
        self.current_level = self.dungeon.levels[self.dungeon.level_number]

        self.game_stats = kwargs["game_stats"]

        self.player.load_data(**kwargs["player"])

        for i in range(self.current_level.room_cnt):
            for j in range(self.current_level.sequence[i].entities_cnt):
                cur_entity = self.current_level.sequence[i].entities[j]
                if cur_entity.entity_type == PLAYER:
                    self.current_level.sequence[i].entities[j] = self.player
                    break

    def calculate_distance(self, point_1: Position, point_2: Position):
        x = point_1.x - point_2.x
        y = point_1.y - point_2.y
        return math.sqrt((x * x + y * y))

    def fight(self, attacking, attacked):
        hit = False
        chance_hit = attacking.get_hit_probability() - attacked.get_dodge_chance()

        damage = 0
        effects = []

        if random.random() < chance_hit:
            damage, effects = attacking.take_damage()
            hit = True

        attacked_is_dead = not attacked.take_injure(damage)

        chance_effect = random.random()
        if TypeEffects.VAMPIRING in effects:
            attacking.take_heal(damage)
        if TypeEffects.EUTHANASIA in effects and chance_effect < 0.3:
            attacked.increase_effect(TypeEffects.SLEEP, 1)

        if attacking == self.player and attacked_is_dead:
            self.player.change_treasures(attacked.get_treasures())

        return attacked_is_dead, hit

    def use_item(self, index_item):
        item = self.player.backpack.items[index_item]
        if item.symbol == POTION:
            self.game_stats["potions"] += 1
        elif item.symbol == SCROLL:
            self.game_stats["scrolls"] += 1
        elif item.symbol == FOOD:
            self.game_stats["foods"] += 1

        return self.player.use_item_in_backpack(index_item)

    def check_correct_move(self, new_position: Position):
        result = False
        if self.player.sector != UNINITIALIZED:
            room_with_player = self.current_level.rooms[self.player.grid_i_j[0]][
                self.player.grid_i_j[1]
            ]
            result = room_with_player.check_point_in_room(new_position)

            for door in room_with_player.doors:
                if new_position == door:
                    result = True
                    break

            for corridor in self.current_level.corridors:
                if corridor.check_point_in_corridor(new_position):
                    result = True
                    break

        return result

    def change_position_player(self, room, new_position):
        if room is not None:

            if self.player.sector != room.sector:
                previous_room = self.current_level.rooms[self.player.grid_i_j[0]][
                    self.player.grid_i_j[1]
                ]

                for i in range(previous_room.entities_cnt):
                    if previous_room.entities[i].entity_type == PLAYER:
                        previous_room.entities.pop(i)
                        previous_room.entities.append(UNINITIALIZED)
                        previous_room.entities_cnt -= 1
                        break

                room.entities[room.entities_cnt] = self.player
                room.entities_cnt += 1

                self.player.sector = room.sector
                self.player.grid_i_j = room.grid_i_j

        self.player.position = new_position

    def choose_new_position_enemy(self, enemy, list_points):
        result = Position()

        if (
            abs(enemy.position.x - self.player.position.x) <= 1
            and abs(enemy.position.y - self.player.position.y) <= 1
        ):
            result.x = self.player.position.x
            result.y = self.player.position.y
        elif (
            enemy.sector == self.player.sector
            and self.calculate_distance(enemy.position, self.player.position)
            <= enemy.hostility
        ):
            min_distance = self.calculate_distance(list_points[0], self.player.position)
            result = list_points[0]
            for point in list_points:
                current_distance = self.calculate_distance(point, self.player.position)
                if current_distance < min_distance:
                    min_distance = current_distance
                    result = point
        else:
            result = random.choice(list_points)

        if (
            not self.current_level.rooms[enemy.grid_i_j[0]][
                enemy.grid_i_j[1]
            ].check_point_in_room(result)
            and self.current_level.find_room_with_point(result) is not None
        ):
            next_room = self.current_level.find_room_with_point(result)
            previous_room = self.current_level.rooms[enemy.grid_i_j[0]][
                enemy.grid_i_j[1]
            ]

            if next_room.entities_cnt < MAX_ENTITIES_PER_ROOM - 2:
                for i in range(previous_room.entities_cnt):
                    if previous_room.entities[i] == enemy:
                        previous_room.entities.pop(i)
                        previous_room.entities.append(UNINITIALIZED)
                        previous_room.entities_cnt -= 1
                        break

                next_room.entities[next_room.entities_cnt] = enemy
                next_room.entities_cnt += 1

                enemy.sector = next_room.sector
                enemy.grid_i_j = next_room.grid_i_j

        return result

    def get_new_position_enemy(self, enemy):
        room = self.current_level.rooms[enemy.grid_i_j[0]][enemy.grid_i_j[1]]

        corridors = []
        for i in range(self.current_level.corridors_cnt):
            if (
                self.current_level.corridors[i].rooms_sector[0] == room.sector
                or self.current_level.corridors[i].rooms_sector[1] == room.sector
            ):
                corridors.append(self.current_level.corridors[i])

        near_rooms = []
        for near_room in self.current_level.sequence:
            for corridor in corridors:
                if (
                    near_room.sector == corridor.rooms_sector[0]
                    or near_room.sector == corridor.rooms_sector[1]
                    and near_room.sector != room.sector
                ):
                    near_rooms.append(near_room)

        list_movement_options = enemy.get_movement_options()
        list_points = []

        for movement_option in list_movement_options:
            new_position = Position()
            new_position.x = enemy.position.x + movement_option[0]
            new_position.y = enemy.position.y + movement_option[1]
            if room.check_point_in_room(new_position):
                list_points.append(new_position)

            for corridor in corridors:
                if corridor.check_point_in_corridor(new_position):
                    list_points.append(new_position)

            for near_room in near_rooms:
                if near_room.check_point_in_room(new_position):
                    list_points.append(new_position)

        if len(list_points) == 0:
            new_position = Position()
            new_position.x = random.randint(
                room.pos_top_left_bot_right[0].x + 1,
                room.pos_top_left_bot_right[1].x - 1,
            )
            new_position.y = random.randint(
                room.pos_top_left_bot_right[0].y + 1,
                room.pos_top_left_bot_right[1].y - 1,
            )
            list_points.append(new_position)

        return self.choose_new_position_enemy(enemy, list_points)

    def move_enemies(self):
        user_dead = False
        list_enemies = self.current_level.get_list_all_enemies()

        for enemy in list_enemies:
            position_enemy = self.get_new_position_enemy(enemy)

            if enemy.symbol == GHOST:
                if TypeEffects.INVISIBILITY in enemy.effects:
                    enemy.reduce_effect(TypeEffects.INVISIBILITY)

                chance_invisibility = random.random()
                if (
                    TypeEffects.INVISIBILITY not in enemy.effects
                    and chance_invisibility < 0.3
                ):
                    enemy.increase_effect(TypeEffects.INVISIBILITY, 2)

            if self.player.position == position_enemy:
                user_dead = self.fight(enemy, self.player)[0]
            else:
                enemy.position = position_enemy

        return user_dead

    def move_user(self, direction_x, direction_y):
        user_dead = False
        new_position = Position()
        new_position.x = self.player.position.x + direction_x
        new_position.y = self.player.position.y + direction_y

        if self.check_correct_move(new_position):
            self.game_stats["moves"] += 1

            room = self.current_level.find_room_with_point(new_position)
            corridor = self.current_level.find_corridor_with_point(new_position)
            if room is not None and TypeEffects.SLEEP not in self.player.effects:
                enemy = room.find_enemy_in_point(new_position)
                item = room.find_item_in_point(new_position)

                if enemy is not None:
                    enemy_dead, hit = self.fight(self.player, enemy[1])
                    if enemy_dead:
                        room.delete_entity_by_id(enemy[0])
                        self.game_stats["killed_enemies"] += 1
                    if hit:
                        self.game_stats["hits"] += 1
                    else:
                        self.game_stats["misses"] += 1
                else:
                    if item is not None and self.player.add_item_to_backpack(item[1]):
                        if item[1].symbol == TREASURE:
                            self.game_stats["treasures"] += 1
                        room.delete_entity_by_id(item[0])
                    self.change_position_player(room, new_position)
            elif corridor is not None and TypeEffects.SLEEP not in self.player.effects:
                room1 = self.current_level.rooms[corridor.rooms_grid_i_j[0][0]][
                    corridor.rooms_grid_i_j[0][1]
                ]
                room2 = self.current_level.rooms[corridor.rooms_grid_i_j[1][0]][
                    corridor.rooms_grid_i_j[1][1]
                ]

                enemy1 = room1.find_enemy_in_point(new_position)
                enemy2 = room2.find_enemy_in_point(new_position)

                room_with_player = self.current_level.rooms[self.player.grid_i_j[0]][
                    self.player.grid_i_j[1]
                ]
                item = room_with_player.find_item_in_point(new_position)

                if enemy1 is not None:
                    if self.fight(self.player, enemy1[1])[0]:
                        room1.delete_entity_by_id(enemy1[0])
                elif enemy2 is not None:
                    if self.fight(self.player, enemy2[1])[0]:
                        room2.delete_entity_by_id(enemy2[0])
                else:
                    if item is not None and self.player.add_item_to_backpack(item[1]):
                        if item[1].symbol == TREASURE:
                            self.game_stats["treasures"] += 1
                        room_with_player.delete_entity_by_id(item[0])
                    self.change_position_player(room_with_player, new_position)

            user_dead = self.move_enemies()

            if TypeEffects.SLEEP in self.player.effects:
                self.player.reduce_effect(TypeEffects.SLEEP)
            if TypeEffects.EUTHANASIA in self.player.effects:
                self.player.reduce_effect(TypeEffects.EUTHANASIA)
            if TypeEffects.VAMPIRING in self.player.effects:
                self.player.reduce_effect(TypeEffects.VAMPIRING)
            if TypeEffects.INVISIBILITY in self.player.effects:
                self.player.reduce_effect(TypeEffects.INVISIBILITY)
            if TypeEffects.MAX_HEALTH in self.player.effects:
                self.player.reduce_effect(TypeEffects.MAX_HEALTH)
            if TypeEffects.AGILITY in self.player.effects:
                self.player.reduce_effect(TypeEffects.AGILITY)
            if TypeEffects.STRENGTH in self.player.effects:
                self.player.reduce_effect(TypeEffects.STRENGTH)

        return user_dead

    def check_player_on_exit(self):
        result = False

        if self.player.sector != UNINITIALIZED:
            room_with_player = self.current_level.rooms[self.player.grid_i_j[0]][
                self.player.grid_i_j[1]
            ]
            exit_level = room_with_player.find_exit()
            if exit_level is not None and exit_level.position == self.player.position:
                result = True

        return result

    def process_command(self, type_command: TypeCommand, index_item=UNINITIALIZED):
        result = GameStatus.CONTINUES
        user_dead = False

        match type_command:
            case TypeCommand.UP:
                user_dead = self.move_user(0, -1)
            case TypeCommand.DOWN:
                user_dead = self.move_user(0, 1)
            case TypeCommand.LEFT:
                user_dead = self.move_user(-1, 0)
            case TypeCommand.RIGHT:
                user_dead = self.move_user(1, 0)
            case TypeCommand.GETWEAPONS:
                weapons = self.player.backpack.get_list_weapons()
                index_weapon = weapons[index_item - 1][0]
                self.use_item(index_weapon)
            case TypeCommand.GETFOODS:
                foods = self.player.backpack.get_list_foods()
                index_food = foods[index_item - 1][0]
                self.use_item(index_food)
            case TypeCommand.GETPOTIONS:
                potions = self.player.backpack.get_list_potions()
                index_potion = potions[index_item - 1][0]
                self.use_item(index_potion)
            case TypeCommand.GETSCROLLS:
                scrolls = self.player.backpack.get_list_scrolls()
                index_scroll = scrolls[index_item - 1][0]
                self.use_item(index_scroll)
            case TypeCommand.NEWGAME:
                self.dungeon = Dungeon()

                self.dungeon.generate_level()
                self.current_level = self.dungeon.levels[self.dungeon.level_number]

                for i in range(self.current_level.room_cnt):
                    for j in range(self.current_level.sequence[i].entities_cnt):
                        cur_entity = self.current_level.sequence[i].entities[j]
                        if cur_entity.entity_type == PLAYER:
                            self.player = cur_entity
                            break

                self.game_stats = {
                    "sum_treasures": 0,
                    "treasures": 0,
                    "level_number": 0,
                    "killed_enemies": 0,
                    "foods": 0,
                    "scrolls": 0,
                    "potions": 0,
                    "misses": 0,
                    "hits": 0,
                    "moves": 0,
                }
            case TypeCommand.DROPWEAPON:
                new_pos_weapon = self.choose_position_for_drop_weapon(
                    self.player.weapon
                )

                if new_pos_weapon is not None:
                    drop_weapon = self.player.drop_weapon()
                    drop_weapon.position = new_pos_weapon
                    self.current_level.rooms[self.player.grid_i_j[0]][
                        self.player.grid_i_j[1]
                    ].add_entity(drop_weapon)

        if user_dead:
            result = GameStatus.LOST
        elif self.check_player_on_exit():
            if self.dungeon.level_number < 20:
                self.dungeon.generate_level()
                self.current_level = self.dungeon.levels[self.dungeon.level_number]

                for i in range(self.current_level.room_cnt):
                    for j in range(self.current_level.sequence[i].entities_cnt):
                        cur_entity = self.current_level.sequence[i].entities[j]
                        if cur_entity.entity_type == PLAYER:
                            new_player = cur_entity
                            new_player.backpack = self.player.backpack
                            new_player.treasures = self.player.treasures
                            new_player.effects = self.player.effects
                            new_player.max_health = self.player.max_health
                            new_player.health = self.player.health
                            new_player.agility = self.player.agility
                            new_player.strength = self.player.strength
                            new_player.weapon = self.player.weapon
                            self.player = new_player
                            break

                result = GameStatus.NEXTLEVEL
            else:
                result = GameStatus.WON

        if (
            result == GameStatus.LOST
            or result == GameStatus.WON
            or type_command == TypeCommand.EXITGAME
            or type_command == TypeCommand.SAVEGAME
        ):
            self.game_stats["level_number"] = self.dungeon.level_number
            self.game_stats["sum_treasures"] = self.player.treasures

        return result

    def choose_position_for_drop_weapon(self, drop_weapon):
        if type(drop_weapon) != int:
            new_pos_weapon = Position()
            new_pos_weapon.x, new_pos_weapon.y = (
                self.player.position.x,
                self.player.position.y,
            )

            room_with_player = self.current_level.rooms[self.player.grid_i_j[0]][
                self.player.grid_i_j[1]
            ]

            if room_with_player.entities_cnt < MAX_ENTITIES_PER_ROOM - 2:
                for y in range(-1, 2):
                    for x in range(-1, 2):
                        if x == 0 and y == 0:
                            continue

                        if self.check_correct_move(
                            Position(new_pos_weapon.x + x, new_pos_weapon.y + y)
                        ):
                            if (
                                room_with_player.find_entity_in_point(
                                    Position(new_pos_weapon.x + x, new_pos_weapon.y + y)
                                )
                                is None
                            ):
                                return Position(
                                    new_pos_weapon.x + x, new_pos_weapon.y + y
                                )

        return None
