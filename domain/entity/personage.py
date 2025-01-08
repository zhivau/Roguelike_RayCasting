from ..base.consts import *
from ..base.base_objects import Position, TypeEffects
from .entity import Entity


class Personage(Entity):

    def __init__(
        self,
        entity_type=UNINITIALIZED,
        symbol=UNINITIALIZED,
        position=Position(),
        sector=UNINITIALIZED,
        grid_i_j=UNINITIALIZED,
        max_health=UNINITIALIZED,
        strength=UNINITIALIZED,
        agility=UNINITIALIZED,
    ):
        super().__init__(entity_type, symbol, position, sector, grid_i_j)
        self.max_health = max_health
        self.health = self.max_health
        self.agility = agility
        self.strength = strength
        self.effects = {}

    def load_data(self, **kwargs):
        super().load_data(**kwargs)
        self.max_health = kwargs["max_health"]
        self.health = kwargs["health"]
        self.agility = kwargs["agility"]
        self.strength = kwargs["strength"]

        for effect_type, duration in kwargs["effects"].items():
            self.effects[TypeEffects(effect_type)] = duration

    def check_current_max_health(self):
        if self.health > self.max_health:
            self.health = self.max_health

    def check_alive(self):
        result = False
        if self.health > 0:
            result = True
        return result

    def change_position(self, new_x, new_y):
        self.position.x = new_x
        self.position.y = new_y

    def change_max_health(self, value_for_change):
        self.max_health += value_for_change
        self.check_current_max_health()
        return self.check_alive()

    def take_heal(self, value_for_heal):
        self.health += value_for_heal
        self.check_current_max_health()
        return self.check_alive()

    def take_injure(self, value_for_injure):
        self.health -= value_for_injure
        return self.check_alive()

    def change_health(self, value_for_change):
        result = False
        if value_for_change >= 0:
            result = self.take_heal(value_for_change)
        else:
            result = self.take_injure(-value_for_change)
        return result

    def change_agility(self, value_for_change):
        self.agility += value_for_change

    def change_strength(self, value_for_change):
        self.strength += value_for_change

    def increase_effect(self, type_effect: TypeEffects, duration_effect: int):
        if type_effect in self.effects:
            if duration_effect < 0:
                self.effects[type_effect] = duration_effect
            else:
                self.effects[type_effect] += duration_effect
        else:
            self.effects[type_effect] = duration_effect

    def reduce_effect(self, type_effect: TypeEffects):
        self.effects[type_effect] -= 1
        if self.effects[type_effect] == 0:
            if type_effect == TypeEffects.MAX_HEALTH:
                self.change_max_health(-100)
            elif type_effect == TypeEffects.AGILITY:
                self.change_agility(-5)
            elif type_effect == TypeEffects.STRENGTH:
                self.change_strength(-10)

            del self.effects[type_effect]

    def get_hit_probability(self):
        result = 0.5 + 0.05 * self.agility
        return result

    def get_dodge_chance(self):
        result = 0 + 0.05 * self.agility
        if TypeEffects.DODGE in self.effects:
            result = 10
            del self.effects[TypeEffects.DODGE]
        return result

    def take_damage(self):
        effects_attack = []
        if TypeEffects.EUTHANASIA in self.effects:
            effects_attack.append(TypeEffects.EUTHANASIA)
            self.reduce_effect(TypeEffects.EUTHANASIA)
        if TypeEffects.VAMPIRING in self.effects:
            effects_attack.append(TypeEffects.VAMPIRING)
            self.reduce_effect(TypeEffects.VAMPIRING)
        damage = 1 + self.strength
        return damage, effects_attack
