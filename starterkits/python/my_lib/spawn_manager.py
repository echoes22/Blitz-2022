from math import ceil
from typing import List

from game_message import Position, TileType


class SpawnManager:
   def __init__(self):
      self._spawns = None
      self._tick_map = None

   def init_tick(self, tick):
      self._tick_map = tick.map
      if not self._spawns:
         game_map = self._tick_map.tiles
         spawns = []
         for x in range(len(game_map)):
            for y in range(len(game_map[x])):
               if self._tick_map.get_tile_type_at(Position(x, y)) == TileType.SPAWN:
                  try:
                     if self._tick_map.get_tile_type_at(Position(x - 1, y)) == TileType.EMPTY:
                        spawns.append(Position(x, y))
                        continue
                  except:
                     pass

                  try:
                     if self._tick_map.get_tile_type_at(Position(x, y - 1)) == TileType.EMPTY:
                        spawns.append(Position(x, y))
                        continue
                  except:
                     pass

                  try:
                     if self._tick_map.get_tile_type_at(Position(x + 1, y)) == TileType.EMPTY:
                        spawns.append(Position(x, y))
                        continue
                  except:
                     pass

                  try:
                     if self._tick_map.get_tile_type_at(Position(x, y + 1)) == TileType.EMPTY:
                        spawns.append(Position(x, y))
                        continue
                  except:
                     pass
            self._spawns = spawns[::ceil(len(spawns) / 10)] if len(spawns) > 10 else spawns

   def find_all_spawn(self) -> List[Position]:
      return self._spawns
