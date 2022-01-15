from typing import Optional, List

from game_message import Unit, Position, Tick
from my_lib.models import Target, TargetType, PrioritizedTarget, PrioritizedMode, PrioritizedUnit
from my_lib.pathfinder_manager import PathFinderManager
from my_lib.unit_manager import UnitManager


class TargetManager:
    def __init__(self, unit_manager: UnitManager, pathfinder: PathFinderManager):
        self._unit_manager = unit_manager
        self._tick = None
        self._targets = None
        self._diamond_targets = None
        self._pathfinder = pathfinder

    def init_tick(self, tick: Tick):
        self._tick = tick
        self._targets = {unit: None for unit in self._unit_manager.get_allied_units()}
        self._diamond_targets = None

    def get_diamond_targets(self):
        if not self._diamond_targets:
            self._diamond_targets = [Target(TargetType.DIAMOND, diamond, diamond.position)
                                     for diamond in self._tick.map.diamonds if not diamond.ownerId
                                     or diamond.ownerId not in self._unit_manager.get_allied_unit_ids()]
        return self._diamond_targets

    def get_prioritized_target(self, unit: PrioritizedUnit, target: Target) -> Optional[PrioritizedTarget]:
        value = target.source.points * target.source.summonLevel
        if unit.hasSpawned:
            target_path = self._pathfinder.get_target_path(unit.position, target)
            if not target_path:
                return None

            if unit.mode == PrioritizedMode.LONG_RANGE:
                value *= target_path.get_distance()
            elif unit.mode == PrioritizedMode.SHORT_RANGE:
                value /= target_path.get_distance()

        return PrioritizedTarget(target.target_type, target.source, target.position, value)

    def get_targets(self, unit: PrioritizedUnit) -> List[Target]:
        return sorted([self.get_prioritized_target(unit, target) for target in self.get_diamond_targets() if
                       self.target_is_available_for_unit(unit, target.position)], key=lambda t: t.value, reverse=True)

    def get_target_of_unit(self, unit: Unit) -> Optional[Target]:
        return self._targets[unit]

    def unit_has_target(self, unit: Unit) -> bool:
        return self._targets[unit] is not None

    def set_target_of_unit(self, unit: Unit, target: Target) -> bool:
        if self.target_is_available_for_unit(unit, target.source.position):
            self._targets[unit] = target
            return True
        return False

    def target_is_available_for_unit(self, unit: Unit, position: Position) -> bool:
        if position is None:
            return True
        if unit is None:
            return False

        for curr_unit in self._unit_manager.get_allied_units():
            if curr_unit != unit:
                curr_target = self.get_target_of_unit(curr_unit)
                if curr_target is not None and curr_target.source.position == position:
                    return False
        return True
