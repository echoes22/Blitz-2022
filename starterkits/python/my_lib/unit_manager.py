from typing import List

from game_message import Tick, Unit
from my_lib.models import PrioritizedUnit, PrioritizedMode


class UnitManager:
    def __init__(self):
        self._team = None
        self._units = None
        self._spawned_allied_units = None
        self._spawned_enemy_units = None
        self._allied_units = None
        self._enemy_units = None
        self._allied_unit_ids = None
        self._allied_unit_positions = None

    def get_units(self) -> List[PrioritizedUnit]:
        return self._units

    def get_allied_units(self) -> List[PrioritizedUnit]:
        return self._allied_units

    def get_spawned_allied_units(self):
        if not self._spawned_allied_units:
            self._spawned_allied_units = [unit for unit in self._allied_units if unit.hasSpawned]
        return self._spawned_allied_units

    def get_spawned_enemy_units(self):
        if not self._spawned_enemy_units:
            self._spawned_enemy_units = [unit for unit in self._enemy_units if unit.hasSpawned]
        return self._spawned_enemy_units

    def get_allied_unit_ids(self):
        if not self._allied_unit_ids:
            self._allied_unit_ids = [unit.id for unit in self._allied_units]
        return self._allied_unit_ids

    def get_allied_unit_positions(self):
        if not self._allied_unit_positions:
            self._allied_unit_positions = [unit.id for unit in self.get_spawned_allied_units()]
        return self._allied_unit_positions

    def init_tick(self, tick: Tick):
        self._enemy_units = []
        self._units = []
        for team in tick.teams:
            if team.id == tick.teamId:
                self._team = team
                self._allied_units = [self.unit_to_prioritized_unit(unit) for unit in team.units]
            else:
                self._enemy_units.extend([self.unit_to_prioritized_unit(unit) for unit in team.units])
            self._units.extend([self.unit_to_prioritized_unit(unit) for unit in team.units])
        self._spawned_enemy_units = None
        self._spawned_allied_units = None

    @staticmethod
    def unit_to_prioritized_unit(unit: Unit, mode: PrioritizedMode = PrioritizedMode.SHORT_RANGE) -> PrioritizedUnit:
        return PrioritizedUnit(unit.id, unit.teamId, unit.path, unit.hasDiamond, unit.hasSpawned, unit.isSummoning,
                               unit.lastState, unit.diamondId, unit.position, mode)
