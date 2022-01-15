import random
from typing import List, Optional

from game_command import CommandAction, CommandType
from game_message import Tick, Position, Team, TickMap, TileType, Unit
from my_lib.models import Target, TargetType
from my_lib.pathfinder_manager import PathFinderManager
from my_lib.target_manager import TargetManager


class Bot:
    def __init__(self):

        self.tick: Optional[Tick] = None
        self.target_manager: Optional[TargetManager] = None
        self.team: Optional[Team] = None
        self.pathfinder = PathFinderManager()
        print("Initializing your super mega duper bot")

    def get_next_moves(self, tick: Tick) -> List:
        """
        Here is where the magic happens, for now the moves are random. I bet you can do better ;)

        No path finding is required, you can simply send a destination per unit and the game will move your unit towards
        it in the next turns.
        """
        self.tick = tick
        self.team = tick.get_teams_by_id()[tick.teamId]
        self.target_manager = TargetManager(self.team.units, tick.map)
        self.pathfinder.set_tick(tick)

        actions: List = []

        for unit in self.team.units:
            if not unit.hasSpawned:
                actions.append(
                    CommandAction(
                        action=CommandType.SPAWN, unitId=unit.id, target=self.get_random_spawn_position(tick.map)
                    )
                )
            else:
                actions.append(
                    self.get_optimal_move(unit)
                )

            # CommandAction(action=CommandType.MOVE, unitId=unit.id, target=self.get_random_position(tick.map))

        return actions

    def get_random_position(self, tick_map: TickMap) -> Position:
        return Position(
            random.randint(0, tick_map.get_map_size_x() - 1), random.randint(0, tick_map.get_map_size_y() - 1)
        )

    def get_random_spawn_position(self, tick_map: TickMap) -> Position:
        spawns: List[Position] = []

        for x in range(tick_map.get_map_size_x()):
            for y in range(tick_map.get_map_size_y()):
                position = Position(x, y)
                if tick_map.get_tile_type_at(position) == TileType.SPAWN:
                    spawns.append(position)

        return spawns[random.randint(0, len(spawns) - 1)]

    def get_optimal_move(self, unit: Unit) -> CommandAction:
        if not unit.hasDiamond:
            return self.move_to_nearest_diamond(unit)
        if self.tick.tick == self.tick.totalTick - 1 and unit.hasDiamond:
            return self.create_drop_action(unit)
        elif (self.tick.tick < self.tick.totalTick - 7
              and unit.hasDiamond
              and not unit.isSummoning
              and not unit.diamondId in [x.id for x in self.tick.map.diamonds if x.summonLevel == 5]
        ):
            return self.create_summon_action(unit)
        else:
            return self.create_move_action(unit, self.get_random_position(self.tick.map))

    def move_to_nearest_diamond(self, unit: Unit) -> CommandAction:
        # sorting advailable targets
        untargeted_diamond = [diamond for diamond in self.tick.map.diamonds if
                              self.target_manager.target_is_available_for_unit(unit, diamond.position)]
        # formating targets
        target_list = [Target(TargetType.DIAMOND, diamond, diamond.position) for diamond in
                       untargeted_diamond]

        # finding nearest diamond
        target_path = self.pathfinder.get_nearest_target(unit.position, target_list)
        # setting target
        self.target_manager.set_target_of_unit(unit, target_path.target)

        # move to next position
        return self.create_move_action(unit, Position(target_path.path[0][0], target_path.path[0][1]))

    def create_move_action(self, unit: Unit, destination: Position) -> CommandAction:
        return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=destination)

    def create_drop_action(self, unit: Unit) -> CommandAction:
        droppable_pos = self.find_free_adjacent_tile(unit)
        return CommandAction(action=CommandType.DROP, unitId=unit.id, target=droppable_pos)

    def create_summon_action(self, unit: Unit) -> CommandAction:
        return CommandAction(action=CommandType.SUMMON, unitId=unit.id, target=None)

    def find_free_adjacent_tile(self, unit: Unit) -> Position:
        current_unit_positions = []
        for team in self.tick.teams:
            for unit in team.units:
                current_unit_positions.append(unit.position)
        try:
            pos = Position(unit.position.x - 1, unit.position.y)
            if (self.tick.map.get_tile_type_at(pos) == TileType.EMPTY
                and pos not in current_unit_positions):
                return pos
        except:
            pass
        try:
            pos = Position(unit.position.x + 1, unit.position.y)
            if (self.tick.map.get_tile_type_at(pos) == TileType.EMPTY
                and pos not in current_unit_positions):
                return pos
        except:
            pass
        try:
            pos = Position(unit.position.x, unit.position.y - 1)
            if (self.tick.map.get_tile_type_at(pos) == TileType.EMPTY
                and pos not in current_unit_positions):
                return pos
        except:
            pass
        try:
            pos = Position(unit.position.x, unit.position.y + 1)
            if (self.tick.map.get_tile_type_at(pos) == TileType.EMPTY
                and pos not in current_unit_positions):
                return pos
        except:
            pass