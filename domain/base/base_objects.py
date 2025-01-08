from .consts import *
from enum import Enum


class TypeEffects(Enum):
    DODGE = "dodge"
    INVISIBILITY = "invisibility"
    SLEEP = "sleep"
    EUTHANASIA = "euthanasia"
    VAMPIRING = "vampiring"

    MAX_HEALTH = "max_health"
    AGILITY = "agility"
    STRENGTH = "strength"

    def __str__(self):
        return self.value


class TypeCommand(Enum):
    UP = "w"
    DOWN = "s"
    LEFT = "a"
    RIGHT = "d"
    GETWEAPONS = "h"
    DROPWEAPON = "i"
    GETFOODS = "j"
    GETPOTIONS = "k"
    GETSCROLLS = "e"
    NEWGAME = "enter"
    SAVEGAME = "save"
    EXITGAME = "exit"
    NOSIG = "nosig"


class GameStatus(Enum):
    CONTINUES = "continue"
    NEXTLEVEL = "next level"
    LOST = "lose"
    WON = "win"


class Position:

    def __init__(self, x=UNINITIALIZED, y=UNINITIALIZED):
        self.x = x
        self.y = y

    def __str__(self):
        return f"x:{self.x} y:{self.y}"

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False

    def to_dict(self):
        return self.__dict__
