from __future__ import annotations

from random_gen import RandomGen
from team import MonsterTeam
from battle import Battle

from elements import Element, EffectivenessCalculator

from data_structures.referential_array import ArrayR, ArrayRList
from data_structures.queue_adt import CircularQueue
from data_structures.array_sorted_list import ArraySortedListWithKeys
from data_structures.bset import BSet
from data_structures.stack_adt import ArrayStack
from helpers import Flamikin, Faeboa

class BattleTower:

    MIN_LIVES = 2
    MAX_LIVES = 10

    def __init__(self, battle: Battle|None=None) -> None:
        self.battle = battle or Battle(verbosity=0)
        self.player_team = None
        self.player_lives = None
        self.enemy_teams = None
        self.enemy_lives = None
        EffectivenessCalculator.make_singleton()
        self.seen_elements = BSet(len(EffectivenessCalculator.instance.element_names)) # The element Steel element is the last element and so hold the size

    def set_my_team(self, team: MonsterTeam) -> None:
        # Generate the team lives here too.
        self.player_team = team
        self.player_lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES)
        #Elements in the player team will always be in the meta
        self.process_elements(team)


    def generate_teams(self, n: int) -> None:
        self.enemy_teams = ArrayRList[MonsterTeam](n)
        self.enemy_lives = ArrayRList[MonsterTeam](n)
        for _ in range(n):
            self.enemy_teams.add(MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM))
            self.enemy_lives.add(RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES))

    def battles_remaining(self) -> bool:
        return self.player_lives > 0 and not self.enemy_lives.is_empty()

    def next_battle(self) -> tuple[Battle.Result, MonsterTeam, MonsterTeam, int, int]:
        team_to_fight = self.enemy_teams.serve()
        self.process_elements(team_to_fight)
        curr_enemy_team_lives = self.enemy_lives.serve()
        curr_battle = Battle(3)
        result = curr_battle.battle(self.player_team, team_to_fight)
        if result == Battle.Result.TEAM1:
            curr_enemy_team_lives -= 1
        elif result == Battle.Result.TEAM2:
            self.player_lives -= 1
        elif result == Battle.Result.DRAW:
            curr_enemy_team_lives -= 1
            self.player_lives -= 1
        
        team_to_fight.regenerate_team()
        self.player_team.regenerate_team()

        self.enemy_teams._shuffle_left()
        self.enemy_lives._shuffle_left()
   
        if curr_enemy_team_lives > 0:
            self.enemy_teams.add(team_to_fight)
            self.enemy_lives.add(curr_enemy_team_lives)
        if self.player_lives <= 0:
            print("Player is out of lives")
       
        return (result, self.player_team.team.array.__str__(), team_to_fight.team.array.__str__(), self.player_lives, curr_enemy_team_lives)

    def process_elements(self, team : MonsterTeam):
        while not team.team.is_empty():
            monster_element = Element.from_string(team.retrieve_from_team().get_element())
            self.seen_elements.add(monster_element.value)
        team.regenerate_team()

    def out_of_meta(self) -> ArrayR[Element]:
        team_to_fight = self.enemy_teams[0]
        in_meta_elements = BSet(len(EffectivenessCalculator.instance.element_names))
        while not team_to_fight.team.is_empty():
            monster_element = Element.from_string(team_to_fight.retrieve_from_team().get_element())
            if monster_element.value in self.seen_elements:
                in_meta_elements.add(monster_element.value)
                self.seen_elements.remove(monster_element.value)
        while not self.player_team.team.is_empty():
            monster_element = Element.from_string(self.player_team.retrieve_from_team().get_element())
            if monster_element.value in self.seen_elements:
                in_meta_elements.add(monster_element.value)
                self.seen_elements.remove(monster_element.value)
        team_to_fight.regenerate_team()
        self.player_team.regenerate_team()
        out_of_meta_elements = ArrayR[Element](len(self.seen_elements))
        incrementor = 0

        for item in range(1, int.bit_length(self.seen_elements.elems) + 1):
            if item in self.seen_elements:
                out_of_meta_elements[incrementor] = Element(item)
                incrementor += 1
        
        self.seen_elements |= in_meta_elements
        return out_of_meta_elements


    def sort_by_lives(self):
        # 1054 ONLY
        for mark in range(len(self.enemy_teams)):
            temp= self.enemy_teams[mark]
            i = mark - 1
            while i >= 0 and self.enemy_teams[i] > temp:
                self.team[i + 1] = self.team[i]
                i -= 1
            self.team[i + 1] = temp


def tournament_balanced(tournament_array: ArrayR[str]):
    # 1054 ONLY
    print(len(tournament_array))
    stack = ArrayStack[str](len(tournament_array))
    i = 0
    for i in range(len(tournament_array)):
        top = tournament_array[i]
        if top == "+":
            try:
                player1 = stack.pop()
                player2 = stack.pop()
                if len(player1.split("v")) != len(player2.split("v")):
                    return False
                stack.push(f"({player1} v {player2})")
            except:
                return False
        else:
            stack.push(top)
    
    return True

if __name__ == "__main__":

        RandomGen.set_seed(123456789)
        bt = BattleTower(Battle(verbosity=0))
        bt.set_my_team(MonsterTeam(
            team_mode=MonsterTeam.TeamMode.BACK,
            selection_mode=MonsterTeam.SelectionMode.PROVIDED,
            provided_monsters=ArrayR.from_list([Faeboa])
        ))
        bt.generate_teams(3)
        print(bt.out_of_meta())
        bt.next_battle()
        print(bt.out_of_meta())
        bt.next_battle()
        print(bt.out_of_meta())
        bt.next_battle()
        print(bt.out_of_meta())
        bt.next_battle()
        print(bt.out_of_meta())
    # unbalanced = ArrayR.from_list([
    #         "a", "b", "+", "c", "d", "+", "+",
    #         "e", "f", "+", "g", "h", "+", "+", "+"
    #     ])
    # print(tournament_balanced(unbalanced))

