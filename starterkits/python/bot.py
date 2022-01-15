import threading
from typing import List, Optional, Tuple

from game_command import CommandAction, CommandType
from game_message import Tick, Team, Unit, TickMap, TileType
from my_lib.action_manager import ActionManager
from my_lib.unit_manager import UnitManager
from game_message import Position


class Bot:
    def __init__(self):
        self.tick: Optional[Tick] = None
        self.team: Optional[Team] = None
        self.unit_manager = UnitManager()
        self.corners = None
        self.used_corner = None
        print("Initializing your super mega duper bot")

    def get_next_moves(self, tick: Tick) -> List:
        """
        Here is where the magic happens, for now the moves are random. I bet you can do better ;)

        No path finding is required, you can simply send a destination per unit and the game will move your unit towards
        it in the next turns.
        """
        self.tick = tick
        if self.tick.tick == 0 :
            self.corners = self.find_corners()
            self.used_corner = self.corners[0]



        self.team = tick.get_teams_by_id()[tick.teamId]
        self.unit_manager.init_tick(tick, self.team, [unit for team in self.tick.teams for unit in team.units])

        action_manager = ActionManager(tick, self.unit_manager)

        actions: List[CommandAction] = []
        thread = threading.Thread(target=run_action, args=(action_manager, self.team.units, actions, self.used_corner))
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
                        if (haut == 1 and gauche == 1 and self.tick.map.get_tile_type_at(Position(x-1, y + 1)) == TileType.EMPTY):
                            corners.append((Position(x, y),Position(x-1, y + 1)))
                        if (haut == 1 and droite == 1 and self.tick.map.get_tile_type_at(Position(x+1, y + 1)) == TileType.EMPTY):
                            corners.append((Position(x, y),Position(x+1, y + 1)))
                        if (bas == 1 and gauche == 1 and self.tick.map.get_tile_type_at(Position(x-1, y - 1)) == TileType.EMPTY):
                            corners.append((Position(x, y),Position(x-1, y - 1)))
                        if (bas == 1 and droite == 1 and self.tick.map.get_tile_type_at(Position(x+1, y - 1)) == TileType.EMPTY):
                            corners.append((Position(x, y),Position(x+1, y - 1)))
        return corners


def run_action(action_manager: ActionManager, team_units: List[Unit], actions: List[CommandAction], corner):
    for unit in team_units:
        if not unit.hasSpawned:
            spawn = action_manager.get_optimal_spawn(unit)
            actions.append(spawn)
        else:
            # CORNER_LAD
            if unit == team_units[0]:
                actions.append(action_manager.get_optimal_cornerlad_move(unit, corner))
            #DEFENDER
            elif unit == team_units[1]:
                actions.append(action_manager.get_optimal_defender_move(unit, corner))
            else:
                actions.append(action_manager.get_optimal_move(unit))


