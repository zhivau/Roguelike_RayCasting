from ..base.consts import *
from ..base.base_objects import Position, TypeEffects
from .item import Item
from .backpack import Backpack
from .personage import Personage


class Player(Personage):

    def __init__(
        self, position=Position(), sector=UNINITIALIZED, grid_i_j=UNINITIALIZED
    ):

        super().__init__(PLAYER, PLAYER_CHAR, position, sector, grid_i_j, 100, 5, 1)

        self.treasures = 0
        self.weapon = UNINITIALIZED
        self.backpack = Backpack()

    def to_dict(self):
        result = self.__dict__.copy()

        dict_effects = {}
        for key, value in result["effects"].items():
            dict_effects[key.value] = value
        result["effects"] = dict_effects

        return result

    def load_data(self, **kwargs):
        super().load_data(**kwargs)
        self.treasures = kwargs["treasures"]

        if type(kwargs["weapon"]) != int:
            self.weapon = Item()
            self.weapon.load_data(**kwargs["weapon"])
        else:
            self.weapon = UNINITIALIZED

        self.backpack.load_data(**kwargs["backpack"])

    def change_treasures(self, value_for_change):
        self.treasures += value_for_change

    def use_item_in_backpack(self, index_item: int):
        item = self.backpack.items[index_item]

        is_alive = self.change_max_health(item.max_health)
        is_alive = self.change_health(item.health)
        self.change_agility(item.agility)
        self.change_strength(item.strength)

        for type_effect, duration_effect in item.effects.items():
            if (
                TypeEffects.MAX_HEALTH not in self.effects
                and type_effect == TypeEffects.MAX_HEALTH
            ):
                self.change_max_health(100)
            elif (
                TypeEffects.AGILITY not in self.effects
                and type_effect == TypeEffects.AGILITY
            ):
                self.change_agility(5)
            elif (
                TypeEffects.STRENGTH not in self.effects
                and type_effect == TypeEffects.STRENGTH
            ):
                self.change_strength(10)

            self.increase_effect(type_effect, duration_effect)

        self.backpack.remove_item(index_item)

        if item.symbol == WEAPON:
            if self.weapon != UNINITIALIZED:
                old_weapon = self.weapon
                self.change_strength(-old_weapon.strength)
                self.add_item_to_backpack(old_weapon)
            self.weapon = item

        return is_alive

    def add_item_to_backpack(self, item):
        result = False

        if (
            item.symbol in self.backpack.number_item_type
            and self.backpack.number_item_type[item.symbol] < 9
        ):
            result = True
            self.backpack.number_item_type[item.symbol] += 1
            self.backpack.items.append(item)

            if item.symbol == TREASURE:
                self.change_treasures(item.price)
        elif item.symbol not in self.backpack.number_item_type:
            result = True
            self.backpack.number_item_type[item.symbol] = 1
            self.backpack.items.append(item)

            if item.symbol == TREASURE:
                self.change_treasures(item.price)

        return result

    def drop_weapon(self):
        drop_weapon = None

        if self.weapon != UNINITIALIZED:
            self.change_strength(-self.weapon.strength)
            drop_weapon = self.weapon
            self.weapon = UNINITIALIZED

        return drop_weapon
