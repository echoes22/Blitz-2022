from dataclasses import dataclass
from enum import Enum
from typing import Union, List

from game_message import Position, Diamond, Unit


class TargetType(Enum):
    DIAMOND = "DIAMOND",
    UNIT = "UNIT"


@dataclass
class Target:
    target_type: TargetType
    target: Union[Diamond, Unit]
    position: Position


@dataclass
class Map:
    grid: List[Position]
    targets: List[Target]

    def set_target(self, targets: List[Target]):
        self.targets = [target for target in targets if self.target_is_in_map(target)]

    def target_is_in_grid(self, target: Target):
        for poss in self.grid:
            if target.position.x == poss.x and target.position.y == poss.y:
                return True
        return False

#
# @dataclass
# class Game:
#     map: List[Map]
