from __future__ import annotations
import abc

from stats import Stats

class MonsterBase(abc.ABC):

    
    def __init__(self, simple_mode=True, level:int=1) -> None:
        self.simple_mode = simple_mode
        self.init_level = level
        self.curr_level = level
        self.stats = self.get_simple_stats()
        self.hp  = self.stats.get_max_hp()

    def get_level(self):
        return self.level

    def level_up(self):
        self.curr_level += 1

    def get_hp(self):
        return self.hp

    def set_hp(self, val):
        self.hp = val

    def get_stat_args(self):
        return self.stats

    def get_attack(self):
        return self.stats.get_attack()

    def get_defense(self):
        return self.stats.get_defense()

    def get_speed(self):
        return self.stats.get_speed()

    def get_max_hp(self):
        return self.stats.get_max_hp()

    def alive(self) -> bool:
        return self.hp > 0

    def attack(self, other: MonsterBase):
        # Step 1: Compute attack stat vs. defense stat
        # Step 2: Apply type effectiveness
        # Step 3: Ceil to int
        # Step 4: Lose HP
        pass

    def ready_to_evolve(self) -> bool:
        return True if self.curr_level > self.init_level and self.get_evolution() else False
            

    def evolve(self) -> MonsterBase:
        return self.get_evolution()
    
    def __str__(self) -> str:
        return "LV." + self.curr_level + " " + self.get_name() + ", " + self.get_hp() + "/" + self.get_max_hp() + " HP" 

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
