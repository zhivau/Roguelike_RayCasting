from .level import Level
from .generation_level import *


class Dungeon:

    def __init__(self):
        self.levels = [Level() for _ in range(MAX_LEVELS)]
        self.level_number = UNINITIALIZED

    def to_dict(self):
        return self.__dict__

    def load_data(self, **kwargs):
        for json_level, level in zip(kwargs["levels"], self.levels):
            level.load_data(**json_level)
        self.level_number = kwargs["level_number"]

    def generate_level(self):
        self.level_number += 1

        generate_sectors(self.levels[self.level_number])
        generate_primary_connections(self.levels[self.level_number])
        generate_secondary_connections(self.levels[self.level_number])
        generate_rooms_geometry(self.levels[self.level_number])
        generate_corridors_geometry(self.levels[self.level_number])

        generate_player_pos(self.levels[self.level_number])
        generate_exit(self.levels[self.level_number])
        generate_enemies(self.levels[self.level_number], self.level_number)
        generate_items(self.levels[self.level_number], self.level_number)
