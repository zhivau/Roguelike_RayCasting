from ..base.consts import *
from ..base.base_objects import Position


class Entity:

    def __init__(
        self,
        entity_type=UNINITIALIZED,
        symbol=UNINITIALIZED,
        position=Position(),
        sector=UNINITIALIZED,
        grid_i_j=UNINITIALIZED,
    ):
        self.entity_type = entity_type
        self.symbol = symbol
        self.position = position
        self.sector = sector
        self.grid_i_j = grid_i_j

    def to_dict(self):
        return self.__dict__

    def load_data(self, **kwargs):
        self.entity_type = kwargs["entity_type"]
        self.symbol = kwargs["symbol"]

        self.position = Position(**kwargs["position"])

        self.sector = kwargs["sector"]
        self.grid_i_j = kwargs["grid_i_j"]
