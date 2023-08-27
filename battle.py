from __future__ import annotations
from enum import auto
from typing import Optional
import math

from base_enum import BaseEnum
from team import MonsterTeam
from elements import EffectivenessCalculator
from data_structures.referential_array import ArrayR


class Battle:

    class Action(BaseEnum):
        ATTACK = auto()
        SWAP = auto()
        SPECIAL = auto()

    class Result(BaseEnum):
        TEAM1 = auto()
        TEAM2 = auto()
        DRAW = auto()

    def __init__(self, verbosity=0) -> None:
        """

        :complexity: O(1) both best/worst case
        """
        self.verbosity = verbosity
        self.result = None

    def process_turn(self) -> Optional[Battle.Result]:
        """
        Process a single turn of the battle. Should:
        * process actions chosen by each team
        * level and evolve monsters
        * remove fainted monsters and retrieve new ones.
        * return the battle result if completed.

        :complexity: 

        FRONT/BACK:
            Best case: O(1)
            Worst case: O(l * e)

            Best case occurs when SWAP is called by both teams
            Worst case occurs when both teams choose to attack
            
        OPTIMISE:
            Best case: O(n)
            Worst case:  O(n^2)

            The best case occurs when SWAP is called by both teams
            The worst case occurs when a special is called on both teams

        where n is the number of monsters, l is the number of letters in the longest element name and
        e is the number of elements

        """

        if self.team1.choose_action(self.out1, self.out2) == self.Action.SPECIAL:
            self.team1.special()
        elif self.team1.choose_action(self.out1, self.out2) == self.Action.SWAP:
            temp = self.out1
            self.out1 = self.team1.retrieve_from_team()
            self.team1.add_to_team(temp)
        if self.team2.choose_action(self.out2, self.out1) == self.Action.SPECIAL:
            self.team2.special()
        elif self.team2.choose_action(self.out2, self.out1) == self.Action.SWAP:
            temp = self.out2
            self.out2 = self.team2.retrieve_from_team()
            self.team2.add_to_team(temp)

        #We save the monster so we can check process the attack on the monster that been attacked instead of the present monster alive
        monster1 = self.out1
        monster2 = self.out2
        if self.team1.choose_action(self.out1, self.out2) == self.Action.ATTACK and self.team2.choose_action(self.out2, self.out1) == self.Action.ATTACK:
            if monster1.get_speed () > monster2.get_speed():
                monster1.attack(monster2)
                self.process_post_attack(monster2, self.team2, 2, monster1)

                #It cant retaliate if it just died
                if monster2.alive():
                    monster2.attack(monster1)
                    self.process_post_attack(monster1, self.team1, 1, monster2)
                
            elif monster1.get_speed () < monster2.get_speed():
                monster2.attack(monster1)
                self.process_post_attack(monster1, self.team1, 1, monster2)
                
                if monster1.alive():
                    monster1.attack(monster2)
                    self.process_post_attack(monster2, self.team2, 2, monster1)
                    
            else: #The equal logic will not be able to follow the structure in process_post_attack() due to this being the only way for a draw to occur
                monster1.attack(monster2)
                monster2.attack(monster1)

                self.process_post_attack(monster1, self.team1, 1, monster2, True)
                self.process_post_attack(monster2, self.team2, 2, monster1, True)
                
        elif self.team2.choose_action(monster2, monster1) == self.Action.ATTACK:
            monster2.attack(monster1)
            self.process_post_attack(monster1, self.team1, 1, monster2)
            
        elif self.team1.choose_action(monster1, monster2) == self.Action.ATTACK:
            monster1.attack(monster2)
            self.process_post_attack(monster2, self.team2, 2, monster1)

        if monster1.alive() and monster2.alive(): #If neither monster dies, we must decrement their health by 1
            monster2.set_hp(monster2.get_hp() - 1)
            monster1.set_hp(monster1.get_hp() - 1)

            self.process_post_attack(monster2, self.team2, 2, monster1, True)
            self.process_post_attack(monster1, self.team1, 1, monster2, True)
        

    def process_post_attack(self, attacked_monster, team, team_num, attacking_monster, use_draw_logic = False) -> bool:
        """
        The function processes what happens after a monster has attacked, including checking if the
        attacked monster has been defeated, updating the game result, retrieving a monster from the team
        if necessary, leveling up the attacking monster, and evolving the attacking monster if ready.
        
        :param attacked_monster: The monster that was attacked
        :param team: The team of the monster that was attacked
        :param team_num: The parameter `team_num` represents the number of the team that was attacked.
        It is used to determine which team the attacking monster belongs to and which team the attacked
        monster belongs to. The value of `team_num` can be either 1 or 2, indicating the first team or
        the second
        :param attacking_monster: The monster that is performing the attack
        :param use_draw_logic: The `use_draw_logic` parameter is a boolean flag that indicates whether
        or not logic for a draw should be used. It is used to handle the case when both monsters have
        been damaged at the same time. If `use_draw_logic` is set to `True`, then the logic for a draw,
        defaults to False (optional)
        :returns: a boolean value. If a monster has died as a result of the attack, the function returns
        True. Otherwise, it returns False.
        
        :complexity: O(1) 
        """
        if attacked_monster.get_hp() <= 0:   
            if team.team.is_empty():
                if self.result:
                    self.result = self.Result.DRAW
                else:
                    if team_num == 1:
                        self.result =  self.Result.TEAM2
                    else:
                        self.result =  self.Result.TEAM1
            else:
                if team_num == 1:
                    self.out1 = team.retrieve_from_team()
                    
                else:
                    self.out2 = team.retrieve_from_team()

            if attacking_monster.get_hp():
                attacking_monster.level_up()
                if attacking_monster.ready_to_evolve():
                    if not use_draw_logic:
                        if team_num == 1:
                            self.out2 = attacking_monster.evolve() 
                        elif team_num == 2: 
                            self.out1 = attacking_monster.evolve()    
                    else:
                        if team_num == 1 and  attacking_monster.get_hp():
                            self.out2 = attacking_monster.evolve() 
                        elif team_num == 2 and  attacking_monster.get_hp(): 
                            self.out1 = attacking_monster.evolve()

    def battle(self, team1: MonsterTeam, team2: MonsterTeam) -> Battle.Result:
        """
        Simulates a battle between two monster teams

        :param team1: The first monster team 
        :param team2: The second monster team
        
        :returns: A result indicating the outcome of the battle

        :complexity: 
            Best case: O(n) 
            Worst case: O(m) 

            where n is the number of monsters on the team with the smallest size and 
            m is the total health of the monsters on the team with the least total health. This will occur when no attacks are chosen.
        """
        
        EffectivenessCalculator.make_singleton()
        if self.verbosity > 0:
            print(f"Team 1: {team1} vs. Team 2: {team2}")
        # Add any pregame logic here.
        self.turn_number = 0
        self.team1 = team1
        self.team2 = team2
        self.out1 = team1.retrieve_from_team()
        self.out2 = team2.retrieve_from_team()
        while self.result is None:
            print(self.out1, self.out2)            
            self.process_turn()
       
        return self.result


if __name__ == "__main__":
    team1 = MonsterTeam(
        team_mode=MonsterTeam.TeamMode.BACK,
        selection_mode=MonsterTeam.SelectionMode.PROVIDED,
        provided_monsters=ArrayR.from_list([
            Flamikin,
            Aquariuma,
            Vineon,
            Strikeon,
        ])
    )
    team2 = MonsterTeam(
        team_mode=MonsterTeam.TeamMode.FRONT,
        selection_mode=MonsterTeam.SelectionMode.PROVIDED,
        provided_monsters=ArrayR.from_list([
            Flamikin,
            Aquariuma,
            Vineon,
            Strikeon,
        ])
    )
    b = Battle(verbosity=3)
    # team1.choose_action = lambda out, team: Battle.Action.ATTACK

    # team2.choose_action = lambda out, team: Battle.Action.ATTACK
    print(b.battle(team1, team2))
