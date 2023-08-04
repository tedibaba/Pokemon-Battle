from __future__ import annotations

from random_gen import RandomGen
from team import MonsterTeam
from battle import Battle

from elements import Element

from data_structures.referential_array import ArrayR
from data_structures.queue_adt import Queue

class BattleTower:

    MIN_LIVES = 2
    MAX_LIVES = 10

    def __init__(self, battle: Battle|None=None) -> None:
        self.battle = battle or Battle(verbosity=0)
        self.player_team = None
        self.player_lives = None
        self.enemy_teams = None
        self.enemy_lives = None

    def set_my_team(self, team: MonsterTeam) -> None:
        # Generate the team lives here too.
        self.player_team = team
        self.player_lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES)

    def generate_teams(self, n: int) -> None:
        self.enemy_teams = Queue[MonsterTeam](n)
        self.enemy_lives = Queue[MonsterTeam](n)
        for _ in range(n):
            self.enemy_teams.append(MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM))
            self.enemy_lives.append(RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES))

    def battles_remaining(self) -> bool:
        return self.player_lives > 0 and not self.enemy_lives.is_empty()

    def next_battle(self) -> tuple[Battle.Result, MonsterTeam, MonsterTeam, int, int]:
        team_to_fight = self.enemy_teams.serve()
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
        
        if curr_enemy_team_lives > 0:
            team_to_fight.regenerate_team()
            self.enemy_teams.append(team_to_fight)
        elif self.player_lives <= 0:
            print("Player is out of lives")
            exit()
        return (result, , )

    def out_of_meta(self) -> ArrayR[Element]:
        raise NotImplementedError

    def sort_by_lives(self):
        # 1054 ONLY
        raise NotImplementedError

def tournament_balanced(tournament_array: ArrayR[str]):
    # 1054 ONLY
    raise NotImplementedError

if __name__ == "__main__":

    RandomGen.set_seed(129371)

    bt = BattleTower(Battle(verbosity=3))
    bt.set_my_team(MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM))
    bt.generate_teams(3)

    for result, my_team, tower_team, player_lives, tower_lives in bt:
        print(result, my_team, tower_team, player_lives, tower_lives)
