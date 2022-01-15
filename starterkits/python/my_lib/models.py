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
class TargetPath:
    target: Target
    path: List
