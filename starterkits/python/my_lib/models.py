from dataclasses import dataclass
from enum import Enum
from typing import Union, List

from game_message import Position, Diamond, Unit


class TargetType(Enum):
    DIAMOND = "DIAMOND",
    UNIT = "UNIT",
    EMPTY = "EMPTY"


@dataclass
class Target:
    target_type: TargetType
    source: Union[Diamond, Unit, None]
    position: Position


@dataclass
class TargetPath:
    target: Target
    path: List  # [(x, y)]

    def get_distance(self):
        return len(self.path)
