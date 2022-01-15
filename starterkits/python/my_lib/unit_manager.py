from typing import List

from game_message import Team, Unit, Tick


class UnitManager:
    def __init__(self):
        self._team = None
        self._units = None
        self._spawned_allied_units = None
        self._spawned_enemy_units = None
        self._available_diamonds = None

    def get_units(self):
        return self._units

    def get_spawned_allied_units(self):
        if not self._spawned_allied_units:
            self._spawned_allied_units = [unit for unit in self._team.units if unit.hasSpawned]
        return self._spawned_allied_units

    def get_spawned_enemy_units(self):
        if not self._spawned_enemy_units:
            self._spawned_enemy_units = [unit for unit in self._units if
                                         unit.hasSpawned and unit.teamId != self._team.id]
        return self._spawned_enemy_units

    def init_tick(self, tick: Tick, team: Team, units: List[Unit]):
        self._team = team
        self._units = units
        allied_ids = [unit.id for unit in self.get_spawned_allied_units()]
        self._available_diamonds = [diamond for diamond in tick.map.diamonds if diamond.ownerId not in allied_ids]
        self._spawned_enemy_units = None
        self._spawned_allied_units = None

    def get_available_diamonds(self):
        return self._available_diamonds
