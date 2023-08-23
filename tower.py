from __future__ import annotations

from random_gen import RandomGen
from team import MonsterTeam
from battle import Battle

from elements import Element, EffectivenessCalculator

from data_structures.referential_array import ArrayR, ArrayRList
from data_structures.queue_adt import CircularQueue

from data_structures.bset import BSet
from data_structures.stack_adt import ArrayStack
from helpers import Flamikin, Faeboa

class BattleTower:

    MIN_LIVES = 2
    MAX_LIVES = 10

    def __init__(self, battle: Battle|None=None) -> None:
        """
        complexity: O(1)
        """

        self.battle = battle or Battle(verbosity=0)
        self.player_team = None
        self.enemy_teams = None
        EffectivenessCalculator.make_singleton()
        self.seen_elements = BSet(len(EffectivenessCalculator.instance.element_names))

    def set_my_team(self, team: MonsterTeam) -> None:
        """
        Sets the given team as the player team

        :complexity: O(n * e * c==) in worst case 
                     O(n * c==) in best case 
                     where n is the number of monsters in team, 
                     e is the number of elements and c== is the cost of comparison
        """
        # Generate the team lives here too.
        self.player_team = team
        self.player_team.lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES)
        #Elements in the player team will always be in the meta
        self.process_elements(team)


    def generate_teams(self, n: int) -> None:
        """
        Generates enemy teams to battle against

        :param n: The number of enemy teams to be generated
        :complexity: O(n) where n is the number of enemy teams to be generated

        """
        self.enemy_teams = CircularQueue[MonsterTeam](n)
        for _ in range(n):
            new_enemy_team = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
            new_enemy_team.lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES)
            self.enemy_teams.append(new_enemy_team)
            
    def battles_remaining(self) -> bool:
        """
        Checks if there are any more battle to be conducted. This occurs when both the player has more than 0 lives
        and there is at least one enemy with more than 0 lives.

        :returns: A boolean indicating if there are any more battle to be conducted
        :complexity: O(1) in best case
                     O(n) worst casewhere n is number of enemy teams
        """

        all_enemies_dead = True
        for _ in range(len(self.enemy_teams)):
            enemy_team = self.enemy_teams.serve()
            if  enemy_team.lives:
                all_enemies_dead = False
                # break
            self.enemy_teams.append(enemy_team)
        # else:
        #     self.enemy_teams.append(enemy_team)
        return self.player_team.lives > 0 and not all_enemies_dead

    def next_battle(self) -> tuple[Battle.Result, MonsterTeam, MonsterTeam, int, int]:
        """
        Initiates the next battle against the next team that has more than 0 lives

        :returns: A tuple containing the result of the battle, the player's team, the enemy's team, the current lives of the player, and the current lives of the enemy

        :complexity: O(m + l) best case
                     O(n + m + l) worst case 
                     where n is the number of teams, m is the total health of the monsters on the team with the least total health and l is the number of monsters on team with the most monsters
        """

        for _ in range(len(self.enemy_teams)):
            team_to_fight = self.enemy_teams.serve()
            self.enemy_teams.append(team_to_fight)
            if team_to_fight.lives:
                break
        

        self.process_elements(team_to_fight)
        curr_battle = Battle(3)
        result = curr_battle.battle(self.player_team, team_to_fight)
        if result == Battle.Result.TEAM1:
            team_to_fight.lives -= 1
        elif result == Battle.Result.TEAM2:
            self.player_team.lives -= 1
        elif result == Battle.Result.DRAW:
            team_to_fight.lives -= 1
            self.player_team.lives -= 1
        
        team_to_fight.regenerate_team()
        self.player_team.regenerate_team()
        
        return (result, self.player_team, team_to_fight, self.player_team.lives, team_to_fight.lives)

    def process_elements(self, team : MonsterTeam):
        """
        :param team: The team whose elements will be processed
        :complexity: O(nlog(n) * e * c==) in worst case. This occurs when the optimise team mode is chosen
                     O(n * c==) in best case 
                     where n is the number of monsters in team, 
                     e is the number of elements and c== is the cost of comparison
        """
        for _ in range(len(team.team)):
            monster = team.retrieve_from_team()
            monster_element = Element.from_string(monster.get_element())
            self.seen_elements.add(monster_element.value)
            team.add_to_team(monster)


    def out_of_meta(self) -> ArrayR[Element]:
        """
        Finds the elements that are out of the meta in regard to the next battle to happen

        :returns: An array of elements which are out of the meta

        :complexity: O(t * e * c==) in worst case. This occurs when the optimise team mode has been chosen.
                     O(t * c==) in best case 
                     where t is the number of monsters on the biggest team, e is the number of elements
                     and c== is the cost of comparison 
        """

        team_to_fight = self.enemy_teams.peek() # We do not want to remove this team of the queue as it is yet to fight against the player
        in_meta_elements = BSet(len(EffectivenessCalculator.instance.element_names))
        
        for _ in range(len(team_to_fight.team) + 1): #O(n * (e* c==  + log(n)) 
            monster = team_to_fight.retrieve_from_team()
            monster_element = Element.from_string(monster.get_element())

            if monster_element.value in self.seen_elements:
                in_meta_elements.add(monster_element.value)
                self.seen_elements.remove(monster_element.value)
            team_to_fight.add_to_team(monster)

        for _ in range(len(self.player_team.team) + 1): # O ( m * (c== * e + log(m))) 
            monster = self.player_team.retrieve_from_team()
            monster_element = Element.from_string(monster.get_element())

            if monster_element.value in self.seen_elements:
                in_meta_elements.add(monster_element.value)
                self.seen_elements.remove(monster_element.value)
            self.player_team.add_to_team(monster)

        out_of_meta_elements = ArrayR[Element](len(self.seen_elements))

        incrementor = 0

        for item in range(1, int.bit_length(self.seen_elements.elems) + 1): # O(bit_len)
            if item in self.seen_elements:
                out_of_meta_elements[incrementor] = Element(item)
                incrementor += 1
        
        self.seen_elements |= in_meta_elements
        return out_of_meta_elements


    def sort_by_lives(self):
        """
        Sorts the enemy teams according to their lives

        This function sorts the enemy teams queue in O(1) space complexity. The approach to do this is to look through the entire 
        queue for the smallest element and then append to the end of the queue. We then continue to do this until the entire queue
        is sorted.

        :complexity: O(n^2) where n is the number of enemy teams
        """
        # 1054 ONLY
        for i in range(1, len(self.enemy_teams) + 1):
            min_index = self.find_min_index(len(self.enemy_teams) - i)
            self.insert_min_to_rear(min_index)



    def find_min_index(self, unsorted_index : int) -> int:
        """
        Finds the index of the team between 0 and the unsorted index with the least lives 

        :param unsorted_index: The index up to which the queue is unsorted
        :returns: The index of the team with the least lives

        :complexity: O(n) where n is the number of teams
        """
        min_index = -1
        min_value = self.MAX_LIVES + 1
        for i in range(len(self.enemy_teams)):
            #Seek out the index with the minimum value
            curr_team = self.enemy_teams.serve()
            if curr_team.lives <= min_value and i <= unsorted_index:
                min_value = curr_team.lives
                min_index = i

            self.enemy_teams.append(curr_team)
        return min_index
    
    def insert_min_to_rear(self, index : int) -> None:
        """
        Inserts the team at the minimum index at the end of the team queue

        :param index: The index of the team that is to be inserted at the end of the team queue
        :complexity: O(n) is the number of enemy teams 
        """
        for i in range(len(self.enemy_teams)):
            if i == index:
                temp = self.enemy_teams.serve()
            else:
                self.enemy_teams.append(self.enemy_teams.serve())
     
        self.enemy_teams.append(temp)

             

def tournament_balanced(tournament_array: ArrayR[str]):
    """
    Determines if a tournament bracket is balanced

    :param tournament_array: An array containing a possible tournament bracket
    :returns: A boolean indicating if a tournament bracket is balanced

    :complexity: O(1) in best case
                 O(n) in the worst case where n is the number of elements in the tournament array
    """
    # 1054 ONLY
    if len(tournament_array) != 0 and (len(tournament_array) & (len(tournament_array) - 1) == 0):
        return False
    
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
    
    if len(stack) == 1:
        return True 
    else: #If there is more than one thing in the stack, that means a proper tournament was not able to be formed
        return False


if __name__ == "__main__":
        
        class GoodFlamikin(Flamikin):

            def get_attack(self):
                return 10000000

            def get_speed(self):
                return 10000000

            def get_defense(self):
                return 10000000

            def get_max_hp(self):
                return 10000000

            def ready_to_evolve(self):
                # Never evolve = never stats
                return False


        # Now give us an overpowered team so we can test the enemy losing lives.
        RandomGen.set_seed(123456789)
        bt = BattleTower(Battle(verbosity=0))
        bt.set_my_team(MonsterTeam(
            team_mode=MonsterTeam.TeamMode.BACK,
            selection_mode=MonsterTeam.SelectionMode.PROVIDED,
            provided_monsters=ArrayR.from_list([GoodFlamikin])
        ))
        bt.generate_teams(3)
        # They have lives 7 5 and 3


        while bt.battles_remaining():
            result, team1, team2, lives1, lives2 = bt.next_battle()
