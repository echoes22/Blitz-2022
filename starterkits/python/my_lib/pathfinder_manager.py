from math import sqrt
from typing import Optional, List

from game_message import Tick, Position
from my_lib.models import Target


def _get_distance(pos1: Position, pos2: Position):
    return sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)


class PathFinderManager:
    def __init__(self, tick: Optional[Tick] = None):
        self._tick: Optional[Tick] = tick

    def set_tick(self, tick: Tick):
        self._tick = tick

    def get_nearest_targets(self, origin: Position, targets: List[Target]) -> List[Target]:
        target_result = [for target in targets]
        for target in targets:
            distance = _get_distance(unit_pos, diamond.position)
            if distance <= closest_diamond["distance"]:
                closest_diamond = {"diamond": diamond, "distance": distance}
