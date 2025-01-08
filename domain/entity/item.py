from ..base.consts import *
from ..base.base_objects import Position, TypeEffects
from .entity import Entity


class Item(Entity):

    def __init__(
        self,
        symbol=UNINITIALIZED,
        position=Position(),
        sector=UNINITIALIZED,
        grid_i_j=UNINITIALIZED,
    ):
        super().__init__(ITEM, symbol, position, sector, grid_i_j)
        self.health = 0
        self.max_health = 0
        self.agility = 0
        self.strength = 0
        self.price = 0
        self.effects = {}

    def to_dict(self):
        result = self.__dict__.copy()

        dict_effects = {}
        for effect_type, duration in result["effects"].items():
            dict_effects[effect_type.value] = duration
        result["effects"] = dict_effects

        return result

    def load_data(self, **kwargs):
        super().load_data(**kwargs)
        self.health = kwargs["health"]
        self.max_health = kwargs["max_health"]
        self.agility = kwargs["agility"]
        self.strength = kwargs["strength"]
        self.price = kwargs["price"]

        for effect_type, duration in kwargs["effects"].items():
            self.effects[TypeEffects(effect_type)] = duration
