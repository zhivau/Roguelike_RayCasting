from ..base.consts import *
from ..base.base_objects import Position
from ..entity import Entity, Player, Item, Enemy


class Room:

    def __init__(self):
        self.sector = UNINITIALIZED
        self.grid_i_j = UNINITIALIZED
        self.pos_top_left_bot_right = [Position(), Position()]
        self.doors = [Position(), Position(), Position(), Position()]
        self.connections = [UNINITIALIZED for _ in range(4)]
        self.entities = [UNINITIALIZED for _ in range(MAX_ENTITIES_PER_ROOM)]
        self.entities_cnt = 0

    def to_dict(self):
        result = self.__dict__.copy()
        new_connections = []
        for connection in self.connections:
            if connection != UNINITIALIZED:
                new_connections.append(connection.sector)
            else:
                new_connections.append(UNINITIALIZED)
        result["connections"] = new_connections
        return result

    def load_data(self, **kwargs):
        self.sector = kwargs["sector"]
        self.grid_i_j = kwargs["grid_i_j"]

        self.pos_top_left_bot_right = [
            Position(**(kwargs["pos_top_left_bot_right"][0])),
            Position(**(kwargs["pos_top_left_bot_right"][1])),
        ]

        self.doors = [
            Position(**(kwargs["doors"][0])),
            Position(**(kwargs["doors"][1])),
            Position(**(kwargs["doors"][2])),
            Position(**(kwargs["doors"][3])),
        ]

        for direction, sector in enumerate(kwargs["connections"]):
            self.connections[direction] = sector

        self.entities_cnt = kwargs["entities_cnt"]

        for index, entity in enumerate(kwargs["entities"]):
            if type(entity) != int:
                if entity["entity_type"] == PLAYER:
                    self.entities[index] = Player()
                    self.entities[index].load_data(**entity)
                elif entity["entity_type"] == ENEMY:
                    self.entities[index] = Enemy()
                    self.entities[index].load_data(**entity)
                elif entity["entity_type"] == ITEM:
                    self.entities[index] = Item()
                    self.entities[index].load_data(**entity)
                else:
                    self.entities[index] = Entity()
                    self.entities[index].load_data(**entity)
            else:
                self.entities[index] = UNINITIALIZED

    def check_point_in_room(self, position: Position):
        result = False
        if (
            self.pos_top_left_bot_right[0].x
            < position.x
            < self.pos_top_left_bot_right[1].x
            and self.pos_top_left_bot_right[0].y
            < position.y
            < self.pos_top_left_bot_right[1].y
        ):
            result = True

        for door in self.doors:
            if door == position:
                result = True
                break

        return result

    def find_enemy_in_point(self, position: Position):
        result = None
        if self.entities is not None:
            for i in range(self.entities_cnt):
                if (
                    self.entities[i].entity_type == ENEMY
                    and position == self.entities[i].position
                ):
                    result = (i, self.entities[i])
                    break

        return result

    def find_item_in_point(self, position: Position):
        result = None
        if self.entities is not None:
            for i in range(self.entities_cnt):
                if (
                    self.entities[i].entity_type == ITEM
                    and position == self.entities[i].position
                ):
                    result = (i, self.entities[i])
                    break

        return result

    def find_entity_in_point(self, position):
        result = None
        if self.entities is not None:
            for i in range(self.entities_cnt):
                if position == self.entities[i].position:
                    result = self.entities[i]
                    break
        return result

    def delete_entity_by_id(self, index: int):
        self.entities.pop(index)
        self.entities.append(UNINITIALIZED)
        self.entities_cnt -= 1

    def get_enemy(self):
        result = []
        for i in range(self.entities_cnt):
            if self.entities[i].entity_type == ENEMY:
                result.append(self.entities[i])
        return result

    def get_items(self):
        result = []
        for i in range(self.entities_cnt):
            if self.entities[i].entity_type == ITEM:
                result.append(self.entities[i])
        return result

    def find_exit(self):
        result = None

        for i in range(self.entities_cnt):
            if self.entities[i].entity_type == EXIT:
                result = self.entities[i]
                break

        return result

    def get_walls(self):
        walls = []

        if self.doors[TOP].x == UNINITIALIZED:
            walls.append(
                (
                    self.pos_top_left_bot_right[0],
                    Position(
                        self.pos_top_left_bot_right[1].x,
                        self.pos_top_left_bot_right[0].y,
                    ),
                )
            )
        else:
            walls.append(
                (
                    self.pos_top_left_bot_right[0],
                    Position(self.doors[TOP].x - 1, self.doors[TOP].y),
                )
            )
            walls.append(
                (
                    Position(self.doors[TOP].x + 1, self.doors[TOP].y),
                    Position(
                        self.pos_top_left_bot_right[1].x,
                        self.pos_top_left_bot_right[0].y,
                    ),
                )
            )

        if self.doors[RIGHT].x == UNINITIALIZED:
            walls.append(
                (
                    Position(
                        self.pos_top_left_bot_right[1].x,
                        self.pos_top_left_bot_right[0].y,
                    ),
                    self.pos_top_left_bot_right[1],
                )
            )
        else:
            walls.append(
                (
                    Position(
                        self.pos_top_left_bot_right[1].x,
                        self.pos_top_left_bot_right[0].y,
                    ),
                    Position(self.doors[RIGHT].x, self.doors[RIGHT].y - 1),
                )
            )
            walls.append(
                (
                    Position(self.doors[RIGHT].x, self.doors[RIGHT].y + 1),
                    self.pos_top_left_bot_right[1],
                )
            )

        if self.doors[BOTTOM].x == UNINITIALIZED:
            walls.append(
                (
                    self.pos_top_left_bot_right[1],
                    Position(
                        self.pos_top_left_bot_right[0].x,
                        self.pos_top_left_bot_right[1].y,
                    ),
                )
            )
        else:
            walls.append(
                (
                    self.pos_top_left_bot_right[1],
                    Position(self.doors[BOTTOM].x + 1, self.doors[BOTTOM].y),
                )
            )
            walls.append(
                (
                    Position(self.doors[BOTTOM].x - 1, self.doors[BOTTOM].y),
                    Position(
                        self.pos_top_left_bot_right[0].x,
                        self.pos_top_left_bot_right[1].y,
                    ),
                )
            )

        if self.doors[LEFT].x == UNINITIALIZED:
            walls.append(
                (
                    Position(
                        self.pos_top_left_bot_right[0].x,
                        self.pos_top_left_bot_right[1].y,
                    ),
                    self.pos_top_left_bot_right[0],
                )
            )
        else:
            walls.append(
                (
                    Position(
                        self.pos_top_left_bot_right[0].x,
                        self.pos_top_left_bot_right[1].y,
                    ),
                    Position(self.doors[LEFT].x, self.doors[LEFT].y + 1),
                )
            )
            walls.append(
                (
                    Position(self.doors[LEFT].x, self.doors[LEFT].y - 1),
                    self.pos_top_left_bot_right[0],
                )
            )

        return walls

    def get_vertices(self):
        vertices = []

        for i in range(self.entities_cnt):
            vertices.append(
                Position(self.entities[i].position.x, self.entities[i].position.y + 1)
            )
            vertices.append(
                Position(self.entities[i].position.x, self.entities[i].position.y - 1)
            )
            vertices.append(
                Position(self.entities[i].position.x - 1, self.entities[i].position.y)
            )
            vertices.append(
                Position(self.entities[i].position.x + 1, self.entities[i].position.y)
            )

        vertices.append(
            Position(
                self.pos_top_left_bot_right[0].x + 1,
                self.pos_top_left_bot_right[0].y + 1,
            )
        )
        vertices.append(
            Position(
                self.pos_top_left_bot_right[1].x - 1,
                self.pos_top_left_bot_right[1].y - 1,
            )
        )
        vertices.append(
            Position(
                self.pos_top_left_bot_right[1].x - 1,
                self.pos_top_left_bot_right[0].y + 1,
            )
        )
        vertices.append(
            Position(
                self.pos_top_left_bot_right[0].x + 1,
                self.pos_top_left_bot_right[1].y - 1,
            )
        )

        return vertices

    def consists_player(self):
        for i in range(self.entities_cnt):
            if self.entities[i].entity_type == PLAYER:
                return True
        return False

    def add_entity(self, entity):
        if self.entities_cnt < MAX_ENTITIES_PER_ROOM - 2:
            self.entities[self.entities_cnt] = entity
            self.entities_cnt += 1
