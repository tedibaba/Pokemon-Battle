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
        The function initializes a class instance with a battle object, player team, enemy teams, and a
        set of seen elements.
        
        :param battle: The `battle` parameter is an instance of the `Battle` class or `None`. It is used
        to initialize the `self.battle` attribute of the class. If `battle` is `None`, a new instance of
        the `Battle` class is created with a verbosity level of 0
        
        :param battle: A battle object
     
        complexity: O(1)
        """

        self.battle = battle or Battle(verbosity=0)
        self.player_team = None
        self.enemy_teams = None
        EffectivenessCalculator.make_singleton()
        self.seen_elements = BSet(len(EffectivenessCalculator.instance.element_names))

    def set_my_team(self, team: MonsterTeam) -> None:
        """
        The function sets the given team as the player team and generates the team lives, while also
        processing the elements in the team.
        
        :implementation:
            Sets the given team as the player team and assigns the team a random number of lives.

        :param team: The `team` parameter is an instance of the `MonsterTeam` class, which represents a
        team of monsters

        :complexity: 
        
            Best case:  O(n)
            Worst case: 
            O(n * e) in worst case 
                     in best case 
                     where n is the number of monsters in team, 
                     e is the number of elements 
        """
        # Generate the team lives here too.
        self.player_team = team
        self.player_team.lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES)



    def generate_teams(self, n: int) -> None:
        """
        The function generates a specified number of enemy teams for battle. 

        :implementation:
            We create n teams and then add them into a queue. We have used a queue since the FIFO nature of the queue
            is exactly what we need when deciding which team will be fighting against the player.

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
        The function checks if there are any more battles to be conducted by checking if both the player
        and at least one enemy team have more than 0 lives.

        :implementation:
            If there is 1 or more teams remaining in the enemy team queue and the player has 1 or more lives, then there are 
            battles remaining.

        :returns: A boolean indicating if there are any more battle to be conducted
        :complexity: O(1) in best case
                     O(n) worst casewhere n is number of enemy teams
        """
        return self.player_team.lives > 0 and len(self.enemy_teams) > 0

    def next_battle(self) -> tuple[Battle.Result, MonsterTeam, MonsterTeam, int, int]:
        """
        Initiates the next battle against the next team that has more than 0 lives

        :implementation:
            We get the next enemy team to fight from the queue. Then we execute the fight and update the lives based
            on the result of the battle. Then both teams are revived and the enemy team is added back to the queue if
            it is has 1 or more lives.

        :returns: A tuple containing the result of the battle, the player's team, the enemy's team, 
        the current lives of the player, and the current lives of the enemy

        :complexity: O(m + l) best case
                     O(n + m + l) worst case 
                     where n is the number of teams, m is the total health of the monsters on the team with the least total health and l is the number of monsters on team with the most monsters
        """
        
        team_to_fight = self.enemy_teams.serve()

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
        

        self.player_team.regenerate_team()

        if team_to_fight.lives:
            team_to_fight.regenerate_team()
            self.enemy_teams.append(team_to_fight)
        
        return (result, self.player_team, team_to_fight, self.player_team.lives, team_to_fight.lives)

    def process_elements(self, team : MonsterTeam):
        """
        The function processes the elements of a given MonsterTeam by retrieving each monster,
        extracting its element, and adding it to a set of seen elements.

        :implementation:
            For each monster in a team, we add its element to the set of seen elements
        
        :param team: The team whose elements will be processed
        :complexity: 
            FRONT/BACK:
                Best case: O(n)
                Worst case: O(n * e)

            OPTIMISE:
                Best case: O(n^2log(n))
                Worst case: O(n^2log(n) * e)

                where n is the number of monsters in team, 
                e is the number of elements 
        """
        for _ in range(len(team.team)):
            monster = team.retrieve_from_team()
            monster_element = Element.from_string(monster.get_element())
            self.seen_elements.add(monster_element.value)
            team.add_to_team(monster)


    def out_of_meta(self) -> ArrayR[Element]:
        """
        Finds the elements that are out of the meta in regard to the next battle to happen

        :implementation:
            We peek the queue to see the next enemy team to fight but do not remove from the queue.
            We then loop through both the enemy team and player team monster while removing those monsters'
            element from the seen element set and adding to an in meta element set. The left over elements in the seen
            element set are the out of meta elements which we add into a referential array. We then use bitwise OR with
            the in meta element set to return the seen element set to its original state.

        :returns: An array of elements which are out of the meta

        :complexity: O(t * e ) in worst case. This occurs when the optimise team mode has been chosen.
                     O(t  in best case 
                     where t is the number of monsters on the biggest team, e is the number of elements
              
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

        for item in range(1, len(EffectivenessCalculator.instance.element_names) + 1): # O(e)
            if item in self.seen_elements:
                out_of_meta_elements[incrementor] = Element(item)
                incrementor += 1
        
        self.seen_elements |= in_meta_elements
        return out_of_meta_elements


    def sort_by_lives(self):
        """
        Sorts the enemy team queue by their number of lives

        :implementation:
            We sort the enemy team queue using a method inspired by selection sort. This function sorts the enemy teams queue in O(1) space complexity. 
            The approach to do this is to look through the entire queue for the smallest element and then append to the end of the queue. 
            We then continue to do this until the entire queue is sorted.

        :complexity: O(n^2) where n is the number of enemy teams
        """
        # 1054 ONLY
        for i in range(1, len(self.enemy_teams) + 1):
            min_index = self.find_min_index(len(self.enemy_teams) - i)
            self.insert_min_to_rear(min_index)



    def find_min_index(self, unsorted_index : int) -> int:
        """
        The function `find_min_index` finds the index of the team with the least lives among the teams
        up to a given unsorted index.

        :implementation: 
            We go through the entire queue while looking for the index with minimum lives. We also check during this process
            to make sure the supposed index is not one that has already been placed into its correct place (i.e. already been chosen
            as the min index by the method).

        :param unsorted_index: The index up to which the queue is unsorted
        :returns: The index of the team with the least lives

        :complexity: O(n) where n is the number of teams
        """
        min_index = -1
        min_value = self.MAX_LIVES + 1
        for i in range(len(self.enemy_teams)):
            #Seek out the index with the minimum value
            curr_team = self.enemy_teams.serve()
            if curr_team.lives <= min_value and i <= unsorted_index: # The second condition makes sure we are not going to pick a index that we have already sorted
                min_value = curr_team.lives
                min_index = i

            self.enemy_teams.append(curr_team)
        return min_index
    
    def insert_min_to_rear(self, index : int) -> None:
        """
        Inserts the team at the minimum index at the end of the team queue

        :implementation:
            Inserts the given index at the end of the team queue by looping through the entire queue
            and witholding the desired index from the queue. The desired index is then added back into
            the queue at the end of the loop.

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

    :implementation:
        Uses a similar idea to the complex calculator in that a stack is used but in this situation,
        the only operator we have is + which indicates brackets coming together. 
    
    :param tournament_array: An array containing a possible tournament bracket
    :returns: A boolean indicating if a tournament bracket is balanced

    :complexity: O(n) in the worst case where n is the number of elements in the tournament array
    """
    # 1054 ONLY
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
