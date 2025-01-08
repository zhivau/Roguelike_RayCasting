from ..base.consts import *
from ..base.base_objects import Position
from .personage import Personage

import random


class Enemy(Personage):

    def __init__(
        self,
        symbol=UNINITIALIZED,
        position=Position(),
        sector=UNINITIALIZED,
        grid_i_j=UNINITIALIZED,
        hostility=UNINITIALIZED,
    ):
        super().__init__(ENEMY, symbol, position, sector, grid_i_j, 10, 1, 0)
        self.hostility = hostility

    def to_dict(self):
        result = self.__dict__.copy()

        dict_effects = {}
        for key, value in result["effects"].items():
            dict_effects[key.value] = value
        result["effects"] = dict_effects

        return result

    def load_data(self, **kwargs):
        super().load_data(**kwargs)
        self.hostility = kwargs["hostility"]

    def get_movement_options(self):
        result = []

        if self.symbol == ZOMBIE:
            result.append((0, 1))
            result.append((0, -1))
            result.append((1, 0))
            result.append((-1, 0))
        elif self.symbol == VAMPIRE:
            result.append((0, 1))
            result.append((0, -1))
            result.append((1, 0))
            result.append((-1, 0))
        elif self.symbol == GHOST:
            pass
        elif self.symbol == ORC:
            result.append((0, 2))
            result.append((0, -2))
            result.append((2, 0))
            result.append((-2, 0))
        elif self.symbol == SNAKE_MAGE:
            result.append((1, 1))
            result.append((1, -1))
            result.append((-1, 1))
            result.append((-1, -1))
        elif self.symbol == MIMIC:
            result.append((0, 0))

        return result

    def get_treasures(self):
        result = random.uniform(0.5, 1.5)

        if self.symbol == ZOMBIE:
            result = int(result * 50)
        elif self.symbol == VAMPIRE:
            result = int(result * 100)
        elif self.symbol == GHOST:
            result = int(result * 75)
        elif self.symbol == ORC:
            result = int(result * 100)
        elif self.symbol == SNAKE_MAGE:
            result = int(result * 125)
        elif self.symbol == MIMIC:
            result = int(result * 25)

        return result
