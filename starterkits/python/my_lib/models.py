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
class PrioritizedTarget(Target):
    value: int = 0


@dataclass
class TargetPath:
    target: Target
    path: List  # [(x, y)]

    def get_distance(self):
        return len(self.path)

    def get_next_position(self):
        if self.get_distance() > 1:
            return Position(self.path[1][0], self.path[1][1])
        return None


class PrioritizedMode(Enum):
    LONG_RANGE = 1,
    SHORT_RANGE = 2


@dataclass
class PrioritizedUnit(Unit):
    mode: PrioritizedMode = PrioritizedMode.SHORT_RANGE

    def __hash__(self):
        return int(self.id)

    def __eq__(self, other):
        return self.id == other.id
