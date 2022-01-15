from copy import deepcopy
from typing import List

from game_message import Position, TickMap, TileType, Unit
from my_lib.models import Target, TargetPath


class PathFinderManager:
    def __init__(self):
        self._tick_map: TickMap = None
        self._enemy_units: List[Unit] = []
        self._ally_units: List[Unit] = []

    def set_tick_map(self, tick_map: TickMap):
        self._tick_map = tick_map

    def set_enemy_units(self, enemy_units: List[Unit]):
        self._enemy_units = enemy_units

    def set_ally_units(self, ally_units: List[Unit]):
        self._ally_units = ally_units

    def get_nearest_target(self, origin: Position, targets: List[Target],
                           blacklisted_positions: List[Position] = []) -> TargetPath:
        result_path = []
        nearest_target = None
        min_distance = 99999
        for target in targets:
            # todo garder les valeurs en cache pour évité de recalculer
            path = astar(self._tick_map, origin, target.position, blacklisted_positions)
            if not path:
                continue
            distance = len(path)

            if distance <= min_distance:
                min_distance = distance
                nearest_target = target
                result_path = path

        if nearest_target is not None:
            return TargetPath(nearest_target, result_path)
        return None

    def find_all_spawn(self) -> List[Position]:
        game_map = self._tick_map.tiles
        spawns = []
        for x in range(len(game_map)):
            for y in range(len(game_map[x])):
                if self._tick_map.get_tile_type_at(Position(x, y)) == TileType.SPAWN:
                    spawns.append(Position(x, y))
        return spawns

    def find_optimal_spawn(self, targets: List[Target]):
        optimal_spawn_and_target_path = None
        spawns = self.find_all_spawn()
        optimal_spawn = None
        min_distance = 99999
        unit_positions = [unit.position for unit in self._ally_units] + [unit.position for unit in self._enemy_units]

        print([f"{position.x} {position.y}" for position in unit_positions])
        for spawn in spawns:
            my_target = self.get_nearest_target(spawn, targets, unit_positions)
            if my_target is None:
                continue
            distance = my_target.get_distance()
            if distance <= min_distance:
                min_distance = len(my_target.path)
                optimal_spawn_and_target_path = {"spawn": spawn, "target_path": my_target}
        return optimal_spawn_and_target_path


class Node:
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __hash__(self):  # <-- added a hash method
        return hash(self.position)


def astar(tickmap: TickMap, start: Position, end: Position, blacklisted_positions: List[Position] = []):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    maze = deepcopy(tickmap.tiles)
    for b_position in blacklisted_positions:
        maze[b_position.x][b_position.y] = "WALL"
    # Create start and end node
    start_node = Node(None, (start.x, start.y))

    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, (end.x, end.y))
    end_node.g = end_node.h = end_node.f = 0

    if start_node == end_node:
        return None

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)
    counter = 0
    # Loop until you find the end
    while len(open_list) > 0:
        if counter > 100:
            return None
        counter += 1

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)  # <-- change append to add

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (
                    len(maze[len(maze) - 1]) - 1) or node_position[1] < 0:
                continue

            if (tickmap.get_tile_type_at(Position(node_position[0], node_position[1])) == TileType.SPAWN
                    and tickmap.get_tile_type_at(start) == TileType.SPAWN):
                condition = ["SPAWN", "EMPTY"]
            else:
                condition = ["EMPTY"]

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] not in condition:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            if child in closed_list:  # <-- remove inner loop so continue takes you to the end of the outer loop
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + (
                    (child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)
