import threading
from typing import List, Optional

from game_command import CommandAction
from game_message import Tick, Team, Unit
from my_lib.action_manager import ActionManager
from my_lib.pathfinder_manager import PathFinderManager
from my_lib.spawn_manager import SpawnManager
from my_lib.unit_manager import UnitManager


class Bot:
    def __init__(self):
        self.tick: Optional[Tick] = None
        self.team: Optional[Team] = None
        self.unit_manager = UnitManager()
        self.spawn_manager = SpawnManager()
        self.pathfinder = PathFinderManager(self.unit_manager, self.spawn_manager)
        self.action_manager = ActionManager(self.unit_manager, self.pathfinder, self.spawn_manager)
        print("Initializing your super mega duper bot")

    def get_next_moves(self, tick: Tick) -> List:
        """
        Here is where the magic happens, for now the moves are random. I bet you can do better ;)

        No path finding is required, you can simply send a destination per unit and the game will move your unit towards
        it in the next turns.
        """
        if tick.tick == 0:
            self.spawn_manager.init_tick(tick)
        self.tick = tick
        self.team = tick.get_teams_by_id()[tick.teamId]
        self.unit_manager.init_tick(tick, self.team, [unit for team in self.tick.teams for unit in team.units])
        self.pathfinder.set_tick_map(tick.map)
        self.action_manager.init_tick(tick)

        actions: List[CommandAction] = []
        thread = threading.Thread(target=run_action, args=(self.action_manager, self.team.units, actions))
        thread.start()
        thread.join(timeout=0.95)

        return actions


def run_action(action_manager: ActionManager, team_units: List[Unit], actions: List[CommandAction]):
    for unit in team_units:
        if not unit.hasSpawned:
            spawn = action_manager.get_optimal_spawn(unit)
            actions.append(spawn)
        else:
            actions.append(action_manager.get_optimal_move(unit))
