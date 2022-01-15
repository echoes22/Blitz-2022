from typing import List, Optional

from game_message import TickMap, Unit, Position


class TargetManager:
    def __init__(self, units: List[Unit], map: TickMap):
        self._map = map
        self._units = units
        self._targets = {unit.id: None for unit in units}

    def get_target_of_unit(self, unit: Unit) -> Optional[Position]:
        return self._targets[unit.id]

    def unit_has_target(self, unit: Unit) -> bool:
        return self._targets[unit.id] is not None

    def set_target_of_unit(self, unit: Unit, position: Position) -> bool:
        if self.target_is_available_for_unit(unit, position):
            self._targets[unit.id] = position
            return True
        return False

    def target_is_available_for_unit(self, unit: Unit, target: Position) -> bool:
        if target is None:
            return True
        if unit is None:
            return False

        for curr_unit in self._units:
            if curr_unit.id != unit.id:
                curr_target = self.get_target_of_unit(curr_unit)
                if curr_target is not None and curr_target.x == target.x and curr_target.y == target.y:
                    return False

        return True
