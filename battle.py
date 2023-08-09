from __future__ import annotations
from enum import auto
from typing import Optional
import math

from base_enum import BaseEnum
from team import MonsterTeam
from elements import EffectivenessCalculator, Element
from data_structures.referential_array import ArrayR
from helpers import Flamikin, Aquariuma, Vineon, Strikeon, Normake, Marititan, Leviatitan, Treetower, Infernoth


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
        self.verbosity = verbosity
        self.result = None
        self.monster1_died = 0
        self.monster2_died = 0

    def process_turn(self) -> Optional[Battle.Result]:
        """
        Process a single turn of the battle. Should:
        * process actions chosen by each team
        * level and evolve monsters
        * remove fainted monsters and retrieve new ones.
        * return the battle result if completed.
        """
        choice1 = self.team1.choose_action
        choice2 = self.team2.choose_action

        if choice1 == self.Action.SPECIAL:
            self.team1.special()
        elif choice1 == self.Action.SWAP:
            temp = self.out1
            self.out1 = self.team1.retrieve_from_team()
            self.team1.add_to_team(temp)
        if choice2 == self.Action.SPECIAL:
            self.team2.special()
        elif choice2 == self.Action.SWAP:
            temp = self.out2
            self.out2 = self.team2.retrieve_from_team()
            self.team2.add_to_team(temp)

        first_monster_killed = False
        second_monster_killed = False                                     

        if choice1 == self.Action.ATTACK and choice2 == self.Action.ATTACK:
            if self.out1.get_speed () > self.out2.get_speed():
                self.out1.attack(self.out2)
                second_monster_killed = self.process_post_attack(self.out2, self.team2, 2, self.out1)

                #It cant retaliate if it just died
                if not second_monster_killed:
                    self.out2.attack(self.out1)
                    first_monster_killed = self.process_post_attack(self.out1, self.team1, 1, self.out2)
                

            elif self.out1.get_speed () < self.out2.get_speed():
                self.out2.attack(self.out1)
                first_monster_killed = self.process_post_attack(self.out1, self.team1, 1, self.out2)
                
                if not first_monster_killed:
                    self.out1.attack(self.out2)

                    second_monster_killed = self.process_post_attack(self.out2, self.team2, 2, self.out1)
                    

            else: #The equal logic will not be able to follow the structure in process_post_attack() due to this being the only way for a draw to occur
                self.out1.attack(self.out2)
                self.out2.attack(self.out1)

                 
                first_monster_killed,second_monster_killed = self.process_post_attack(self.out1, self.team1, 1, self.out2, True),self.process_post_attack(self.out2, self.team2, 2, self.out1, True)
                

        elif choice2 == self.Action.ATTACK:
            self.out2.attack(self.out1)
            first_monster_killed = self.process_post_attack(self.out1, self.team1, 1, self.out2)

            
        elif choice1 == self.Action.ATTACK:
            self.out1.attack(self.out2)
            second_monster_killed = self.process_post_attack(self.out2, self.team2, 2, self.out1)

        if not first_monster_killed and not second_monster_killed: #If neither monster dies, we must decrement their health by 1
            self.out2.set_hp(self.out2.get_hp() - 1)
            self.out1.set_hp(self.out1.get_hp() - 1)
            monster1 = self.out1
            monster2 = self.out2
            self.process_post_attack(monster2, self.team2, 2, monster1, True)
            self.process_post_attack(monster1, self.team1, 1, monster2, True)
        
        self.monster1_died = False
        self.monster2_died = False

    def process_post_attack(self, attacked_monster, team, team_num, attacking_monster, use_draw_logic = False):

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
                    self.monster1_died = 1
                    self.out1 = team.retrieve_from_team()
                    
                else:
                    self.monster2_died = 1
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
                        if team_num == 1 and not self.monster2_died and attacking_monster.get_hp():
                            self.out2 = attacking_monster.evolve() 
                        elif team_num == 2 and not self.monster1_died and attacking_monster.get_hp(): 
                            self.out1 = attacking_monster.evolve()
            

            return True #This only happens when a monster died, in which case the other monster should not be allowed to attack
        return False

    def battle(self, team1: MonsterTeam, team2: MonsterTeam) -> Battle.Result:
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
            Aquariuma,
            Aquariuma,
        ])
    )
    team2 = MonsterTeam(
        team_mode=MonsterTeam.TeamMode.FRONT,
        selection_mode=MonsterTeam.SelectionMode.PROVIDED,
        provided_monsters=ArrayR.from_list([
            Aquariuma,
            Aquariuma,
        ])
    )
    b = Battle(verbosity=3)
    team1.choose_action = Battle.Action.ATTACK
    team2.choose_action = Battle.Action.ATTACK
    print(b.battle(team1, team2))
