from ..base.consts import *
from ..base.base_objects import Position


class Corridor:

    def __init__(self):
        self.corridor_type = UNINITIALIZED
        self.points = [Position() for _ in range(4)]
        self.points_cnt = 0
        self.rooms_sector = [UNINITIALIZED, UNINITIALIZED]
        self.rooms_grid_i_j = [UNINITIALIZED, UNINITIALIZED]

    def to_dict(self):
        return self.__dict__

    def load_data(self, **kwargs):
        self.corridor_type = kwargs["corridor_type"]
        self.points = [
            Position(**(kwargs["points"][0])),
            Position(**(kwargs["points"][1])),
            Position(**(kwargs["points"][2])),
            Position(**(kwargs["points"][3])),
        ]
        self.points_cnt = kwargs["points_cnt"]

        self.rooms_sector = kwargs["rooms_sector"]
        self.rooms_grid_i_j = kwargs["rooms_grid_i_j"]

    def check_point_in_corridor(self, pos: Position):
        result = False

        if self.points_cnt == 4:
            p0, p1, p2, p3 = self.points

            if min(p0.x, p1.x) <= pos.x <= max(p0.x, p1.x) and min(
                p0.y, p1.y
            ) <= pos.y <= max(p0.y, p1.y):
                result = True
            elif min(p1.x, p2.x) <= pos.x <= max(p1.x, p2.x) and min(
                p1.y, p2.y
            ) <= pos.y <= max(p1.y, p2.y):
                result = True
            elif min(p2.x, p3.x) <= pos.x <= max(p2.x, p3.x) and min(
                p2.y, p3.y
            ) <= pos.y <= max(p2.y, p3.y):
                result = True
        elif self.points_cnt == 3:
            p0, p1, p2 = self.points[:3]

            if min(p0.x, p1.x) <= pos.x <= max(p0.x, p1.x) and min(
                p0.y, p1.y
            ) <= pos.y <= max(p0.y, p1.y):
                result = True
            elif min(p1.x, p2.x) <= pos.x <= max(p1.x, p2.x) and min(
                p1.y, p2.y
            ) <= pos.y <= max(p1.y, p2.y):
                result = True

        return result

    def get_walls(self):
        walls = None

        if self.points_cnt == 4:
            if self.corridor_type == LEFT_TO_RIGHT_CORRIDOR:
                if self.points[1].y <= self.points[2].y:
                    walls = [
                        (
                            Position(self.points[0].x, self.points[0].y + 1),
                            Position(self.points[1].x - 1, self.points[1].y + 1),
                        ),
                        (
                            Position(self.points[0].x, self.points[0].y - 1),
                            Position(self.points[1].x + 1, self.points[1].y - 1),
                        ),
                        (
                            Position(self.points[1].x + 1, self.points[1].y - 1),
                            Position(self.points[2].x + 1, self.points[2].y - 1),
                        ),
                        (
                            Position(self.points[1].x - 1, self.points[1].y + 1),
                            Position(self.points[2].x - 1, self.points[2].y + 1),
                        ),
                        (
                            Position(self.points[2].x - 1, self.points[2].y + 1),
                            Position(self.points[3].x, self.points[3].y + 1),
                        ),
                        (
                            Position(self.points[2].x + 1, self.points[2].y - 1),
                            Position(self.points[3].x, self.points[3].y - 1),
                        ),
                    ]
                elif self.points[1].y > self.points[2].y:
                    walls = [
                        (
                            Position(self.points[0].x, self.points[0].y + 1),
                            Position(self.points[1].x + 1, self.points[1].y + 1),
                        ),
                        (
                            Position(self.points[0].x, self.points[0].y - 1),
                            Position(self.points[1].x - 1, self.points[1].y - 1),
                        ),
                        (
                            Position(self.points[1].x + 1, self.points[1].y + 1),
                            Position(self.points[2].x + 1, self.points[2].y + 1),
                        ),
                        (
                            Position(self.points[1].x - 1, self.points[1].y - 1),
                            Position(self.points[2].x - 1, self.points[2].y - 1),
                        ),
                        (
                            Position(self.points[2].x + 1, self.points[2].y + 1),
                            Position(self.points[3].x, self.points[3].y + 1),
                        ),
                        (
                            Position(self.points[2].x - 1, self.points[2].y - 1),
                            Position(self.points[3].x, self.points[3].y - 1),
                        ),
                    ]
            elif self.corridor_type == TOP_TO_BOTTOM_CORRIDOR:
                if self.points[1].x > self.points[2].x:
                    walls = [
                        (
                            Position(self.points[0].x + 1, self.points[0].y),
                            Position(self.points[1].x + 1, self.points[1].y + 1),
                        ),
                        (
                            Position(self.points[0].x - 1, self.points[0].y),
                            Position(self.points[1].x - 1, self.points[1].y - 1),
                        ),
                        (
                            Position(self.points[1].x + 1, self.points[1].y + 1),
                            Position(self.points[2].x + 1, self.points[2].y + 1),
                        ),
                        (
                            Position(self.points[1].x - 1, self.points[1].y - 1),
                            Position(self.points[2].x - 1, self.points[2].y - 1),
                        ),
                        (
                            Position(self.points[2].x + 1, self.points[2].y + 1),
                            Position(self.points[3].x + 1, self.points[3].y),
                        ),
                        (
                            Position(self.points[2].x - 1, self.points[2].y - 1),
                            Position(self.points[3].x - 1, self.points[3].y),
                        ),
                    ]
                elif self.points[1].x <= self.points[2].x:
                    walls = [
                        (
                            Position(self.points[0].x + 1, self.points[0].y),
                            Position(self.points[1].x + 1, self.points[1].y - 1),
                        ),
                        (
                            Position(self.points[0].x - 1, self.points[0].y),
                            Position(self.points[1].x - 1, self.points[1].y + 1),
                        ),
                        (
                            Position(self.points[1].x - 1, self.points[1].y + 1),
                            Position(self.points[2].x - 1, self.points[2].y + 1),
                        ),
                        (
                            Position(self.points[1].x + 1, self.points[1].y - 1),
                            Position(self.points[2].x + 1, self.points[2].y - 1),
                        ),
                        (
                            Position(self.points[2].x + 1, self.points[2].y - 1),
                            Position(self.points[3].x + 1, self.points[3].y),
                        ),
                        (
                            Position(self.points[2].x - 1, self.points[2].y + 1),
                            Position(self.points[3].x - 1, self.points[3].y),
                        ),
                    ]
        elif self.points_cnt == 3:
            if self.corridor_type == LEFT_TURN_CORRIDOR:
                walls = [
                    (
                        Position(self.points[0].x + 1, self.points[0].y),
                        Position(self.points[1].x + 1, self.points[1].y + 1),
                    ),
                    (
                        Position(self.points[0].x - 1, self.points[0].y),
                        Position(self.points[1].x - 1, self.points[1].y - 1),
                    ),
                    (
                        Position(self.points[1].x + 1, self.points[1].y + 1),
                        Position(self.points[2].x, self.points[2].y + 1),
                    ),
                    (
                        Position(self.points[1].x - 1, self.points[1].y - 1),
                        Position(self.points[2].x, self.points[2].y - 1),
                    ),
                ]
            elif self.corridor_type == RIGHT_TURN_CORRIDOR:
                walls = [
                    (
                        Position(self.points[0].x + 1, self.points[0].y),
                        Position(self.points[1].x + 1, self.points[1].y - 1),
                    ),
                    (
                        Position(self.points[0].x - 1, self.points[0].y),
                        Position(self.points[1].x - 1, self.points[1].y + 1),
                    ),
                    (
                        Position(self.points[1].x - 1, self.points[1].y + 1),
                        Position(self.points[2].x, self.points[2].y + 1),
                    ),
                    (
                        Position(self.points[1].x + 1, self.points[1].y - 1),
                        Position(self.points[2].x, self.points[2].y - 1),
                    ),
                ]

        return walls

    def get_vertices(self):
        return self.points[: self.points_cnt]
