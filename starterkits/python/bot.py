import random
from math import sqrt
from typing import List, Optional

from game_command import CommandAction, CommandType
from game_message import Tick, Position, Team, TickMap, TileType, Unit, Diamond
from my_lib.target_manager import TargetManager


class Bot:
    def __init__(self):
        self.tick: Optional[Tick] = None
        self.target_manager: Optional[TargetManager] = None
        self.team: Optional[Team] = None
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
        return self.move_to_nearest_diamond(unit)

    def move_to_nearest_diamond(self, unit: Unit) -> CommandAction:
        diamond = self.find_nearest_diamond(unit)

        return self.create_move_action(unit, diamond.position)

    def find_nearest_diamond(self, unit: Unit) -> Diamond:
        unit_pos = unit.position
        diamond_list = self.tick.map.diamonds

        closest_diamond = (diamond_list[0], 999999)
        for diamond in diamond_list:
            if not diamond.ownerId:
                diamond_pos = diamond.position
                distance = self.get_distance(unit_pos, diamond_pos)
                if distance <= closest_diamond[1]:
                    closest_diamond = (diamond, distance)

        return closest_diamond[0]

    def get_distance(self, pos1: Position, pos2: Position):
        return sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2)

    def create_move_action(self, unit: Unit, destination: Position) -> CommandAction:
        return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=destination)
