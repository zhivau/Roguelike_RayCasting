from ..base.consts import *
from .item import Item


class Backpack:

    def __init__(self):
        self.items = []
        self.number_item_type = {}

    def to_dict(self):
        result = self.__dict__
        return result

    def load_data(self, **kwargs):
        for item in kwargs["items"]:
            new_item = Item()
            new_item.load_data(**item)
            self.items.append(new_item)

        self.number_item_type = kwargs["number_item_type"]

    def add_item(self, new_item: Item):
        result = False

        if (
            new_item.symbol in self.number_item_type
            and self.number_item_type[new_item.symbol] < 9
        ):
            result = True
            self.number_item_type[new_item.symbol] += 1
            self.items.append(new_item)
        elif new_item.symbol not in self.number_item_type:
            result = True
            self.number_item_type[new_item.symbol] = 1
            self.items.append(new_item)

        return result

    def remove_item(self, index_item: int):
        symbol = self.items[index_item].symbol
        self.number_item_type[symbol] -= 1
        self.items.pop(index_item)

    def get_list_weapons(self):
        result = []
        i = 0

        for item in self.items:
            if item.symbol == WEAPON:
                result.append((i, item))
            i += 1

        return result

    def get_list_foods(self):
        result = []
        i = 0

        for item in self.items:
            if item.symbol == FOOD:
                result.append((i, item))
            i += 1

        return result

    def get_list_scrolls(self):
        result = []
        i = 0

        for item in self.items:
            if item.symbol == SCROLL:
                result.append((i, item))
            i += 1

        return result

    def get_list_potions(self):
        result = []
        i = 0

        for item in self.items:
            if item.symbol == POTION:
                result.append((i, item))
            i += 1

        return result
