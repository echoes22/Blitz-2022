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
                actions.append(self.get_optimal_spawn(unit))

            else:
                actions.append(
                    self.get_optimal_move(unit)
                )

            # CommandAction(action=CommandType.MOVE, unitId=unit.id, target=self.get_random_position(tick.map))

        return actions

    def get_optimal_spawn(self, unit: Unit)->CommandAction:
        # Diamonds to Target
        untargeted_diamond = [diamond for diamond in self.tick.map.diamonds if
                             diamond.ownerId is None and self.target_manager.target_is_available_for_unit(unit, diamond.position)]

        target_list = [Target(TargetType.DIAMOND, diamond, diamond.position) for diamond in
                       untargeted_diamond]

        destination_and_target_path = self.pathfinder.find_optimal_spawn(target_list)
        self.target_manager.set_target_of_unit(unit,destination_and_target_path["target_path"].target)
        return CommandAction(action=CommandType.SPAWN, unitId=unit.id, target=destination_and_target_path["spawn"])

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
        if unit.hasDiamond:
            return self.get_optimal_hodler_move(unit)
        elif not unit.hasDiamond:
            return self.move_to_nearest_diamond(unit)

    def get_optimal_hodler_move(self, unit: Unit) -> CommandAction:
        current_enemy_units_positions = self.get_current_enemy_units_positions()
        if unit.isSummoning:
            return CommandAction(action=CommandType.NONE, unitId=unit.id, target=None)
        if self.tick.tick == self.tick.totalTick - 1:
            return self.create_drop_action(unit)
        elif self.position_is_dangerous(unit, current_enemy_units_positions):
            return self.create_drop_action(unit)
        elif (self.tick.tick < self.tick.totalTick - 7
                and not unit.isSummoning
                and not unit.diamondId in [x.id for x in self.tick.map.diamonds if x.summonLevel == 5]
                and self.summoning_is_safe(unit, current_enemy_units_positions)
            ):
            return self.create_summon_action(unit)
        else:
            nearest_enemy_pos = self.get_nearest_enemy_position(unit, current_enemy_units_positions)
            new_pos = self.move_away_from_target_pos(unit, nearest_enemy_pos)
            return self.create_move_action(unit, new_pos)

    def move_to_nearest_diamond(self, unit: Unit) -> CommandAction:
        # sorting advailable targets
        untargeted_diamond = [diamond for diamond in self.tick.map.diamonds if
                              diamond.ownerId is None and self.target_manager.target_is_available_for_unit(unit,
                                                                                                           diamond.position)]
        # todo voir si une autre unit serait plus proche du target

        # formating targets
        target_list = [Target(TargetType.DIAMOND, diamond, diamond.position) for diamond in
                       untargeted_diamond]

        # finding nearest diamond
        target_path = self.pathfinder.get_nearest_target(unit.position, target_list)

        if target_path is None:
            # todo KILLL
            pass

        # setting target
        self.target_manager.set_target_of_unit(unit, target_path.target)

        # move to next position
        next_position = target_path.get_next_position()

        return self.create_move_action(unit, next_position)

    def create_move_action(self, unit: Unit, destination: Position) -> CommandAction:
        return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=destination)

    def create_drop_action(self, unit: Unit) -> CommandAction:
        droppable_pos = self.find_free_adjacent_tile(unit)
        return CommandAction(action=CommandType.DROP, unitId=unit.id, target=droppable_pos)

    def create_summon_action(self, unit: Unit) -> CommandAction:
        return CommandAction(action=CommandType.SUMMON, unitId=unit.id, target=None)

    def find_free_adjacent_tile(self, unit: Unit) -> Position:
        current_unit_positions = self.get_current_unit_positions()
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

    def get_current_unit_positions(self):
        current_unit_positions = []
        for team in self.tick.teams:
            for unit in team.units:
                current_unit_positions.append(unit.position)
        return current_unit_positions

    def get_current_enemy_units_positions(self):
        current_enemy_unit_positions = []
        for team in self.tick.teams:
            if team.id != self.tick.teamId:
                for unit in team.units:
                    current_enemy_unit_positions.append(unit.position)
        return current_enemy_unit_positions

    def get_nearest_enemy_position(self, unit: Unit, enemy_pos: List[Position]):
        closest_pos = enemy_pos[0]
        closest_distance = self.get_distance(unit.position, closest_pos)
        for pos in enemy_pos:
            current_distance = self.get_distance(unit.position, pos)
            if current_distance < closest_distance:
                closest_pos = pos
                closest_distance = current_distance
        return closest_pos

    def move_away_from_target_pos(self, unit: Unit, target_pos: Position) -> Position:
        current_unit_positions = self.get_current_unit_positions()
        current_distance = self.get_distance(unit.position, target_pos)
        best_position = unit.position
        try:
            new_pos = Position(unit.position.x - 1, unit.position.y)
            new_distance = self.get_distance(new_pos, target_pos)
            if (self.tick.map.get_tile_type_at(target_pos) == TileType.EMPTY
                and new_pos not in current_unit_positions
                and new_distance > current_distance):
                best_position = new_pos
                current_distance = new_distance
        except:
            pass
        try:
            new_pos = Position(unit.position.x + 1, unit.position.y)
            new_distance = self.get_distance(new_pos, target_pos)
            if (self.tick.map.get_tile_type_at(target_pos) == TileType.EMPTY
                and new_pos not in current_unit_positions
                and new_distance > current_distance):
                best_position = new_pos
                current_distance = new_distance
        except:
            pass
        try:
            new_pos = Position(unit.position.x, unit.position.y - 1)
            new_distance = self.get_distance(new_pos, target_pos)
            if (self.tick.map.get_tile_type_at(target_pos) == TileType.EMPTY
                and new_pos not in current_unit_positions
                and new_distance > current_distance):
                best_position = new_pos
                current_distance = new_distance
        except:
            pass
        try:
            new_pos = Position(unit.position.x, unit.position.y + 1)
            new_distance = self.get_distance(new_pos, target_pos)
            if (self.tick.map.get_tile_type_at(target_pos) == TileType.EMPTY
                and new_pos not in current_unit_positions
                and new_distance > current_distance):
                best_position = new_pos
                current_distance = new_distance
        except:
            pass

        return best_position

    def position_is_dangerous(self, unit: Unit, enemy_pos: List[Position]) -> bool:
        for pos in enemy_pos:
            if self.get_distance(unit.position, pos) <= 1:
                return True
        return False

    def summoning_is_safe(self, unit: Unit, enemy_positions: List[Position]) -> bool:
        # inefficient
        unit_diamond = [x for x in self.tick.map.diamonds if x.id == unit.diamondId][0]
        for pos in enemy_positions:
            if self.get_distance(unit.position, pos) <= unit_diamond.summonLevel:
                return False
        return True

    def get_distance(self, origin: Position, destination: Position) -> int:
        return self.pathfinder.get_nearest_target(origin, [Target(TargetType.EMPTY, None, destination)]).get_distance()
