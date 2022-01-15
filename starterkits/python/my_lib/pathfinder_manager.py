from math import sqrt
from typing import Optional, List

from game_message import Tick, Position
from my_lib.models import Target


class PathFinderManager:
    def __init__(self, tick: Optional[Tick] = None):
        self._tick: Optional[Tick] = tick

    def set_tick(self, tick: Tick):
        self._tick = tick

    def get_nearest_target(self, origin: Position, targets: List[Target]) -> Target:
        min_distance = 99999
        nearest_target = None
        for target in targets:
            distance = self._get_distance(origin, target.position)
            if distance <= min_distance:
                nearest_target = target

        return nearest_target

    @staticmethod
    def _get_distance(pos1: Position, pos2: Position):
        return sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)
