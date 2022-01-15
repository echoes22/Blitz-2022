import threading
from typing import List, Optional

from game_command import CommandAction
from game_message import Tick, Team, Unit, Position, TileType
from my_lib.action_manager import ActionManager
from my_lib.pathfinder_manager import PathFinderManager
from my_lib.spawn_manager import SpawnManager
from my_lib.unit_manager import UnitManager


class Bot:
    def __init__(self):
        self.tick: Optional[Tick] = None
        self.team: Optional[Team] = None
        self.corners = None
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
        self.tick = tick
        if tick.tick == 0:
            self.corners = self.find_corners()
            self.spawn_manager.init_tick(tick)
        self.team = tick.get_teams_by_id()[tick.teamId]
        self.unit_manager.init_tick(tick, self.team, [unit for team in self.tick.teams for unit in team.units])
        self.pathfinder.set_tick_map(tick.map)
        self.action_manager.init_tick(tick)

        actions: List[CommandAction] = []
        thread = threading.Thread(target=run_action, args=(self.action_manager, self.team.units, actions, self.corners))
        thread.start()
        thread.join(timeout=0.95)

        return actions

    def find_corners(self):
        game_map = self.tick.map.tiles
        corners = []
        for x in range(len(game_map)):
            for y in range(len(game_map[x])):
                gauche = 0
                droite = 0
                bas = 0
                haut = 0
                if self.tick.map.get_tile_type_at(Position(x, y)) == TileType.EMPTY:
                    try:
                        if self.tick.map.get_tile_type_at(Position(x - 1, y)) == TileType.EMPTY:
                            gauche += 1
                    except:
                        pass

                    try:
                        if self.tick.map.get_tile_type_at(Position(x, y - 1)) == TileType.EMPTY:
                            bas += 1
                    except:
                        pass

                    try:
                        if self.tick.map.get_tile_type_at(Position(x + 1, y)) == TileType.EMPTY:
                            droite += 1
                    except:
                        pass

                    try:
                        if self.tick.map.get_tile_type_at(Position(x, y + 1)) == TileType.EMPTY:
                            haut += 1
                    except:
                        pass
                    if (haut+bas == 1 and gauche+droite == 1):
                        if (haut == 1 and gauche == 1):
                            corners.append((Position(x, y),Position(0, 0)))
                        if (haut == 1 and droite == 1):
                            corners.append((Position(x, y),Position(0, 0)))
                        if (bas == 1 and gauche == 1):
                            corners.append((Position(x, y),Position(0, 0)))
                        if (bas == 1 and droite == 1):
                            corners.append((Position(x, y),Position(0, 0)))
        return corners

def run_action(action_manager: ActionManager, team_units: List[Unit], actions: List[CommandAction], corners):
    for unit in team_units:
        if not unit.hasSpawned:
            spawn = action_manager.get_optimal_spawn(unit)
            actions.append(spawn)
        else:
            actions.append(action_manager.get_optimal_move(unit, corners))

