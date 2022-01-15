from typing import Optional, List

from game_message import Tick, Position, TickMap, TileType
from my_lib.models import Target, TargetPath


class PathFinderManager:
    def __init__(self, tick: Optional[Tick] = None):
        self._tick: Optional[Tick] = tick

    def set_tick(self, tick: Tick):
        self._tick = tick

    def get_nearest_target(self, origin: Position, targets: List[Target]) -> TargetPath:
        path = []
        nearest_target = None
        min_distance = 99999
        for target in targets:
            path = astar(self._tick.map, origin, target.position)
            distance = len(path)
            if distance <= min_distance:
                min_distance = distance
                nearest_target = target
        
        if nearest_target is not None:
            return TargetPath(nearest_target, path)
        return None
    
    
    def find_all_spawn(self) -> List[Position]:
        game_map = self._tick.map.tiles
        spawns = []
        for x in len(game_map):
            for y in range(x):
                if self._tick.map.get_tile_type_at(Position(x,y)) == TileType.SPAWN:
                    spawns.append(Position(x,y))
        return spawns

    def find_optimal_spawn(self, targets: List[Target]):
        spawns = self.find_all_spawn()
        optimal_spawn = None
        min_distance = 99999
        for spawn in spawns:
            my_target = self.get_nearest_target(spawn, targets)
            if len(my_target.path) <=min_distance:
                min_distance = len(my_target.path)
                optimal_spawn = spawn
        return optimal_spawn
            


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


def astar(tickmap: TickMap, start: Position, end: Position):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    maze = tickmap.tiles
    # Create start and end node
    start_node = Node(None, (start.x, start.y))

    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, (end.x, end.y))
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)
    counter = 0
    # Loop until you find the end
    while len(open_list) > 0:

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

            if tickmap.get_tile_type_at(Position(node_position[0], node_position[1])) == TileType.SPAWN:
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
