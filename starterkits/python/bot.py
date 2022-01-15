import threading
from typing import List, Optional

from game_command import CommandAction
from game_message import Tick, Team, Unit
from my_lib.action_manager import ActionManager
from my_lib.unit_manager import UnitManager


class Bot:
    def __init__(self):
        self.tick: Optional[Tick] = None
        self.team: Optional[Team] = None
        self.unit_manager = UnitManager()
        print("Initializing your super mega duper bot")

    def get_next_moves(self, tick: Tick) -> List:
        """
        Here is where the magic happens, for now the moves are random. I bet you can do better ;)

        No path finding is required, you can simply send a destination per unit and the game will move your unit towards
        it in the next turns.
        """
        self.tick = tick
        self.team = tick.get_teams_by_id()[tick.teamId]
        self.unit_manager.init_tick(tick, self.team, [unit for team in self.tick.teams for unit in team.units])

        action_manager = ActionManager(tick, self.unit_manager)

        actions: List[CommandAction] = []
        thread = threading.Thread(target=run_action, args=(action_manager, self.team.units, actions))
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
