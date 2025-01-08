from ..base.consts import *
from ..base.base_objects import Position
from .room import Room
from .corridor import Corridor


class Level:

    def __init__(self):
        self.room_cnt = 0
        self.corridors_cnt = 0
        self.rooms = [
            [Room() for _ in range(ROOMS_PER_SIDE + 2)]
            for _ in range(ROOMS_PER_SIDE + 2)
        ]
        self.sequence = []
        self.corridors = [Corridor() for _ in range(MAX_CORRIDORS_NUMBER)]

    def to_dict(self):
        result = self.__dict__.copy()
        new_sequence = []
        for room in self.sequence:
            new_sequence.append(room.sector)
        result["sequence"] = new_sequence
        return result

    def load_data(self, **kwargs):
        self.room_cnt = kwargs["room_cnt"]
        self.corridors_cnt = kwargs["corridors_cnt"]

        for json_room_line, room_line in zip(kwargs["rooms"], self.rooms):
            for json_room, room in zip(json_room_line, room_line):
                room.load_data(**json_room)

        self.sequence = []
        for i in range(1, ROOMS_PER_SIDE + 1):
            for j in range(1, ROOMS_PER_SIDE + 1):
                if self.rooms[i][j].sector != UNINITIALIZED:
                    self.sequence.append(self.rooms[i][j])

                    for direction, sector in enumerate(self.rooms[i][j].connections):
                        if sector != UNINITIALIZED:
                            self.rooms[i][j].connections[direction] = self.rooms[
                                1 + sector // ROOMS_PER_SIDE
                            ][1 + sector % ROOMS_PER_SIDE]

        for json_corridor, corridor in zip(kwargs["corridors"], self.corridors):
            corridor.load_data(**json_corridor)

    def find_room_with_point(self, position: Position):
        result = None
        for line_rooms in self.rooms:
            for room in line_rooms:
                if room.sector != -1 and room.check_point_in_room(position):
                    result = room

                for door in room.doors:
                    if position == door:
                        result = room

        return result

    def find_corridor_with_point(self, position: Position):
        result = None
        for corridor in self.corridors:
            if corridor.check_point_in_corridor(position):
                result = corridor
                break
        return result

    def get_list_all_enemies(self):
        result = []
        for room in self.sequence:
            result.extend(room.get_enemy())
        return result

    def get_entities_without_player(self):
        result = []
        for room in self.sequence:
            result.extend(room.get_enemy())
            result.extend(room.get_items())
        return result

    def get_vertices(self):
        vertices = []

        for room in self.sequence:
            vertices.extend(room.get_vertices())

        for i in range(self.corridors_cnt):
            vertices.extend(self.corridors[i].get_vertices())

        return vertices

    def get_walls(self):
        walls = []

        for room in self.sequence:
            walls.extend(room.get_walls())

        for i in range(self.corridors_cnt):
            walls.extend(self.corridors[i].get_walls())

        return walls
