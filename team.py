from __future__ import annotations
from enum import auto
from typing import Optional, TYPE_CHECKING

from base_enum import BaseEnum
from monster_base import MonsterBase
from random_gen import RandomGen
from helpers import get_all_monsters

from data_structures.referential_array import ArrayR
from data_structures.queue_adt import CircularQueue
from data_structures.stack_adt import ArrayStack
from data_structures.array_sorted_list import ArraySortedListWithKeys

if TYPE_CHECKING:
    from battle import Battle

class MonsterTeam:

    class TeamMode(BaseEnum):

        FRONT = auto()
        BACK = auto()
        OPTIMISE = auto()

    class SelectionMode(BaseEnum):

        RANDOM = auto()
        MANUAL = auto()
        PROVIDED = auto()

    class SortMode(BaseEnum):

        HP = auto()
        ATTACK = auto()
        DEFENSE = auto()
        SPEED = auto()
        LEVEL = auto()

    TEAM_LIMIT = 6

    def __init__(self, team_mode: TeamMode, selection_mode, **kwargs) -> None:
        # Add any preinit logic here.
        self.team_mode = team_mode

        if team_mode == self.TeamMode.FRONT:
            self.team = ArrayStack[MonsterBase](6)
            
        elif team_mode == self.TeamMode.BACK:
            self.team = CircularQueue[MonsterBase](6)

        elif team_mode == self.TeamMode.OPTIMISE:
            self.sort_mode = str(kwargs["sort_key"])[9:].lower()
            self.descending = True 
            # self.team_increment = 0
            self.team = ArraySortedListWithKeys[MonsterBase](6)#ArrayR[MonsterBase](6)  
  
        else:
            raise ValueError(f"team_mode {team_mode} not supported.")

        self.monsters = CircularQueue[MonsterBase](6) #Keeping a track of the team for revival What do I do for revival :(
        
        if selection_mode == self.SelectionMode.RANDOM:
            self.select_randomly(**kwargs)
        elif selection_mode == self.SelectionMode.MANUAL:
            self.select_manually(**kwargs)
        elif selection_mode == self.SelectionMode.PROVIDED:
            self.select_provided(**kwargs)
        else:
            raise ValueError(f"selection_mode {selection_mode} not supported.")
        
    
    def add_to_team(self, monster: MonsterBase):
        if self.team_mode == self.TeamMode.FRONT:
            self.team.push(monster)
        elif self.team_mode == self.TeamMode.BACK:
            self.team.append(monster)
        elif self.team_mode == self.TeamMode.OPTIMISE:
            if self.descending:
                self.team.add(monster, self.sort_mode)
            else:
                self.team.add(monster, self.sort_mode, False)

            

    def retrieve_from_team(self) -> MonsterBase:
        if self.team_mode == self.TeamMode.FRONT:
            return self.team.pop()
        elif self.team_mode == self.TeamMode.BACK:
            return self.team.serve()            
        elif self.team_mode == self.TeamMode.OPTIMISE:
            return self.team.delete_at_index(0)

    def special(self) -> None:

        if self.team_mode == self.TeamMode.FRONT:
            temp_team_holder = CircularQueue[MonsterBase](min(3, len(self.team)))
            for _ in range(min(3, len(self.team))):
                temp_team_holder.append(self.team.pop())
            for _ in range(len(temp_team_holder)):
                self.team.push(temp_team_holder.serve())

        elif self.team_mode == self.TeamMode.BACK:
            first_half_size = len(self.team)//2
            first_half_team = CircularQueue[MonsterBase](first_half_size)
            second_half_team = ArrayStack[MonsterBase](len(self.team) - first_half_size) 
            for _ in range(first_half_size):
                first_half_team.append(self.team.serve())
            for _ in range(len(self.team)):
                second_half_team.push(self.team.serve())
            for _ in range(len(second_half_team)):
                self.team.append(second_half_team.pop())
            for _ in range(len(first_half_team)):
                self.team.append(first_half_team.serve())

        elif self.team_mode == self.TeamMode.OPTIMISE:
            self.descending = not self.descending
            temp_team = ArraySortedListWithKeys[MonsterBase](6)
            for _ in range(len(self.team)):
                temp_team.add(self.retrieve_from_team(), self.sort_mode, self.descending)
            self.team= temp_team


    def regenerate_team(self) -> None:

        if self.team_mode == self.TeamMode.FRONT or self.team_mode == self.TeamMode.BACK:
            self.team.clear()

        elif self.team_mode == self.TeamMode.OPTIMISE:
            self.team = ArraySortedListWithKeys[MonsterBase](6)
            self.descending = True

        for _ in range(len(self.monsters)):
                monster = self.monsters.serve()
                self.add_to_team(monster)
                self.monsters.append(monster)

    def select_randomly(self):
        team_size = RandomGen.randint(1, self.TEAM_LIMIT)
        monsters = get_all_monsters()
        n_spawnable = 0
        for x in range(len(monsters)):
            if monsters[x].can_be_spawned():
                n_spawnable += 1

        for _ in range(team_size):
            spawner_index = RandomGen.randint(0, n_spawnable-1)
            cur_index = -1
            for x in range(len(monsters)):
                if monsters[x].can_be_spawned():
                    cur_index += 1
                    if cur_index == spawner_index:
                        # Spawn this monster
                        self.add_to_team(monsters[x]())
                        self.monsters.append(monsters[x]())
                        break
            else:
                raise ValueError("Spawning logic failed.")

    def select_manually(self):
        """
        Prompt the user for input on selecting the team.
        Any invalid input should have the code prompt the user again.

        First input: Team size. Single integer
        For _ in range(team size):
            Next input: Prompt selection of a Monster class.
                * Should take a single input, asking for an integer.
                    This integer corresponds to an index (1-indexed) of the helpers method
                    get_all_monsters()
                * If invalid of monster is not spawnable, should ask again.

        Add these monsters to the team in the same order input was provided. Example interaction:

        How many monsters are there? 2
        MONSTERS Are:
        1: Flamikin [✔️]
        2: Infernoth [❌]
        3: Infernox [❌]
        4: Aquariuma [✔️]
        5: Marititan [❌]
        6: Leviatitan [❌]
        7: Vineon [✔️]
        8: Treetower [❌]
        9: Treemendous [❌]
        10: Rockodile [✔️]
        11: Stonemountain [❌]
        12: Gustwing [✔️]
        13: Stormeagle [❌]
        14: Frostbite [✔️]
        15: Blizzarus [❌]
        16: Thundrake [✔️]
        17: Thunderdrake [❌]
        18: Shadowcat [✔️]
        19: Nightpanther [❌]
        20: Mystifly [✔️]
        21: Telekite [❌]
        22: Metalhorn [✔️]
        23: Ironclad [❌]
        24: Normake [❌]
        25: Strikeon [✔️]
        26: Venomcoil [✔️]
        27: Pythondra [✔️]
        28: Constriclaw [✔️]print
        33: Leafadder [✔️]
        34: Iceviper [✔️]
        35: Rockpython [✔️]
        36: Soundcobra [✔️]
        37: Psychosnake [✔️]
        38: Groundviper [✔️]
        39: Faeboa [✔️]
        40: Bugrattler [✔️]
        41: Darkadder [✔️]
        Which monster are you spawning? 38
        MONSTERS Are:
        1: Flamikin [✔️]
        2: Infernoth [❌]
        3: Infernox [❌]
        4: Aquariuma [✔️]
        5: Marititan [❌]
        6: Leviatitan [❌]
        7: Vineon [✔️]
        8: Treetower [❌]
        9: Treemendous [❌]
        10: Rockodile [✔️]
        11: Stonemountain [❌]
        12: Gustwing [✔️]
        13: Stormeagle [❌]
        14: Frostbite [✔️]
        15: Blizzarus [❌]
        16: Thundrake [✔️]
        17: Thunderdrake [❌]
        18: Shadowcat [✔️]
        19: Nightpanther [❌]
        20: Mystifly [✔️]
        21: Telekite [❌]
        22: Metalhorn [✔️]
        23: Ironclad [❌]
        24: Normake [❌]
        25: Strikeon [✔️]()
        27: Pythondra [✔️]
        28: Constriclaw [✔️]
        29: Shockserpent [✔️]
        30: Driftsnake [✔️]
        31: Aquanake [✔️]
        32: Flameserpent [✔️]
        33: Leafadder [✔️]
        34: Iceviper [✔️]
        35: Rockpython [✔️]
        36: Soundcobra [✔️]
        37: Psychosnake [✔️]
        38: Groundviper [✔️]
        39: Faeboa [✔️]
        40: Bugrattler [✔️]
        41: Darkadder [✔️]
        Which monster are you spawning? 2
        This monster cannot be spawned.
        Which monster are you spawning? 1
        """
        while True:
            try:
                team_size = int(input("Enter the number of monsters on your team: "))
                if 1 <= team_size <= 6:
                    break
                print("Please enter a number between 1 and 6.")
            except:
                print("Please enter a number between 1 and 6.")
        monsters = get_all_monsters()
        while team_size > 0:
            
            monster_index = int(input("Enter the index of the monster you would like on your team: "))
            if 1 <= monster_index <= 41 and monsters[monster_index - 1].can_be_spawned(): 
                self.add_to_team(monsters[monster_index- 1]())
                self.monsters.append(monsters[monster_index- 1]())
                team_size -= 1
            else:
                print("Sorry, a monster with that index does not exist or cannot be spawned. Please enter another monster.")


    def select_provided(self, provided_monsters:Optional[ArrayR[type[MonsterBase]]]=None, **kwargs):
        """
        Generates a team based on a list of already provided monster classes.

        While the type hint imples the argument can be none, this method should never be None

        Example team if in TeamMode.FRONT:
        [Gustwing Instance, Aquariuma Instance, Flamikin Instance]
        """
        for monster in provided_monsters:
            if monster.can_be_spawned() and not self.team.is_full():
                self.add_to_team(monster())
                self.monsters.append(monster())
            else:
                raise ValueError("Too many monsters or a monster cannot be spawned")
            
    def choose_action(self, currently_out: MonsterBase, enemy: MonsterBase) -> Battle.Action:
        # This is just a placeholder function that doesn't matter much for testing.
        from battle import Battle
        if currently_out.get_speed() >= enemy.get_speed() or currently_out.get_hp() >= enemy.get_hp():
            return Battle.Action.ATTACK
        return Battle.Action.SWAP

