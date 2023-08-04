from __future__ import annotations
import abc

from stats import Stats
import math 
from elements import Element, EffectivenessCalculator

class MonsterBase(abc.ABC):

    def __init__(self, simple_mode=True, level:int=1) -> None:
        """
        Initialise an instance of a monster.

        :simple_mode: Whether to use the simple or complex stats of this monster
        :level: The starting level of this monster. Defaults to 1.
        """
        if simple_mode:
            self.stats = self.get_simple_stats()
        else:
            self.stats = self.get_complex_stats()

        self.init_level = level
        self.curr_level = level
        
        self.hp  = self.get_max_hp()

    def get_level(self):
        """The current level of this monster instance"""
        return self.curr_level

    def level_up(self):
        """Increase the level of this monster instance by 1"""
        prev_max_health = self.get_max_hp()
        self.curr_level += 1
        self.set_hp(self.get_max_hp() - (prev_max_health - self.get_hp()))

    def get_hp(self):
        """Get the current HP of this monster instance"""
        return self.hp

    def set_hp(self, val):
        """Set the current HP of this monster instance"""
        self.hp = val

    def get_attack(self):
        """Get the attack of this monster instance"""
        return self.stats.get_attack()

    def get_defense(self):
        """Get the defense of this monster instance"""
        return self.stats.get_defense()

    def get_speed(self):
        """Get the speed of this monster instance"""
        return self.stats.get_speed()

    def get_max_hp(self):
        """Get the maximum HP of this monster instance"""
        return self.stats.get_max_hp()

    def alive(self) -> bool:
        """Whether the current monster instance is alive (HP > 0 )"""
        return self.hp > 0

    def attack(self, other: MonsterBase):
        """Attack another monster instance"""
        # Step 1: Compute attack stat vs. defense stat
        # Step 2: Apply type effectiveness
        # Step 3: Ceil to int
        # Step 4: Lose HP
        self_element, other_element = Element.from_string(self.get_element()), Element.from_string(other.get_element())
        element_multiplier = EffectivenessCalculator.get_effectiveness(self_element, other_element)
        if other.get_defense() < self.get_attack() / 2:
            damage = element_multiplier * (self.get_attack() - other.get_defense())
        elif other.get_defense() < self.get_attack():
            damage = element_multiplier * (5/8 * self.get_attack() - other.get_defense() / 4)
        else:
            damage = element_multiplier * self.get_attack() / 4
        other.set_hp(other.get_hp() -  math.ceil(damage))

    def ready_to_evolve(self) -> bool:
        """Whether this monster is ready to evolve. See assignment spec for specific logic."""
        return True if self.curr_level > self.init_level and self.get_evolution() else False
            

    def evolve(self) -> MonsterBase:
        """Evolve this monster instance by returning a new instance of a monster class."""
        evolution =  (self.get_evolution())(level = self.curr_level)
        evolution.set_hp(evolution.get_hp() - (self.get_max_hp() - self.get_hp()))
        return evolution
    
    def __str__(self) -> str:
        return "LV." + str(self.curr_level) + " " + self.get_name() + ", " + str(self.get_hp()) + "/" + str(self.get_max_hp()) + " HP" 

    ### NOTE
    # Below is provided by the factory - classmethods
    # You do not need to implement them
    # And you can assume they have implementations in the above methods.

    @classmethod
    @abc.abstractmethod
    def get_name(cls) -> str:
        """Returns the name of the Monster - Same for all monsters of the same type."""
        pass

    @classmethod
    @abc.abstractmethod
    def get_description(cls) -> str:
        """Returns the description of the Monster - Same for all monsters of the same type."""
        pass 

    @classmethod
    @abc.abstractmethod
    def get_evolution(cls) -> type[MonsterBase]:
        """
        Returns the class of the evolution of the Monster, if it exists.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_element(cls) -> str:
        """
        Returns the element of the Monster.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def can_be_spawned(cls) -> bool:
        """
        Returns whether this monster type can be spawned on a team.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_simple_stats(cls) -> Stats:
        """
        Returns the simple stats class for this monster, if it exists.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_complex_stats(cls) -> Stats:
        """
        Returns the complex stats class for this monster, if it exists.
        Same for all monsters of the same type.
        """
        pass
