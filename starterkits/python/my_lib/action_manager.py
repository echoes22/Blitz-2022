import random
from typing import List

from game_command import CommandAction, CommandType
from game_message import Unit, Tick, Position, TileType
from my_lib.models import TargetType, Target, Corner
from my_lib.pathfinder_manager import PathFinderManager
from my_lib.target_manager import TargetManager
from my_lib.unit_manager import UnitManager


class ActionManager:
    def __init__(self, tick: Tick, unit_manager: UnitManager, corner: Corner):
        self.tick: Tick = tick
        self.team = tick.get_teams_by_id()[tick.teamId]
        self.target_manager = TargetManager(self.team.units, tick.map)
        self.pathfinder = PathFinderManager(unit_manager)
        self.pathfinder.set_tick_map(tick.map)
        self.pathfinder.set_enemy_units(self.enemy_units)
        self.pathfinder.set_ally_units(self.ally_units)
        self.corner: Corner = corner
        self.unit_manager = unit_manager

    def get_optimal_spawn(self, unit: Unit) -> CommandAction:
        # Diamonds to Target
        target_list = [Target(TargetType.DIAMOND, diamond, diamond.position) for diamond in
                       self.unit_manager.get_available_diamonds() if
                       self.target_manager.target_is_available_for_unit(unit, diamond.position)]

        destination_and_target_path = self.pathfinder.find_optimal_spawn(target_list)
        if not destination_and_target_path:
            return CommandAction(action=CommandType.NONE, unitId=unit.id, target=self.get_random_spawn_position())
        self.target_manager.set_target_of_unit(unit, destination_and_target_path["target_path"].target)
        return CommandAction(action=CommandType.SPAWN, unitId=unit.id, target=destination_and_target_path["spawn"])

    def get_random_spawn_position(self) -> Position:
        spawns = self.pathfinder.find_all_spawn()
        return spawns[random.randint(0, len(spawns) - 1)]

    def get_optimal_move(self, unit: Unit) -> CommandAction:
        if unit.hasDiamond:
            return self.get_optimal_hodler_move(unit)
        else:
            return self.move_to_nearest_diamond(unit)

    
    def get_optimal_cornerlad_move(self, unit: Unit) -> CommandAction:
        untargeted_diamond_pos = [diamond.position for diamond in self.tick.map.diamonds if diamond.ownerId is None]
        if self.corner[0] in untargeted_diamond_pos:
            if unit.hasDiamond:
                return self.create_drop_action(unit) 
            return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=self.corner[0])
        
        if not unit.hasDiamond:
            return self.move_to_nearest_diamond(unit)

        




        current_enemy_units_positions = self.get_current_enemy_units_positions()
        if unit.isSummoning:
            return CommandAction(action=CommandType.NONE, unitId=unit.id, target=None)   
        if self.tick.tick == self.tick.totalTick - 1:
            return self.create_drop_action(unit)  

        elif unit.position != self.corner[0] :
            my_corner = Corner
            my_corner.position = self.corner[0]
            my_target =  Target(TargetType.CORNER, my_corner, self.corner[0])

            allies_position = [unit.position for unit in self.ally_units]
            target_path = self.pathfinder.get_nearest_target(unit.position, [my_corner], allies_position)
            # setting target
            self.target_manager.set_target_of_unit(unit, my_target)

            # move to next position
            next_position = target_path.get_next_position()

            return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=next_position)


        elif (self.tick.tick < self.tick.totalTick - 7
              and not unit.isSummoning
              and not unit.diamondId in [x.id for x in self.tick.map.diamonds if x.summonLevel == 5]
              and self.summoning_is_safe(unit, current_enemy_units_positions)
        ):
            return self.create_summon_action(unit)
        else:
            return CommandAction(action=CommandType.NONE, unitId=unit.id, target=None) 

    def get_optimal_defender_move(self, unit: Unit) -> CommandAction:
        if unit.hasDiamond:
            return self.create_drop_action(unit) 


        current_enemy_units_positions = self.get_current_enemy_units_positions()
    
        if self.tick.tick == self.tick.totalTick - 1:
            return self.create_drop_action(unit)  

        elif unit.position != self.corner[1] :
            my_corner = Corner
            my_corner.position = self.corner[1]
            my_target =  Target(TargetType.CORNER, my_corner, self.corner[1])

            allies_position = [unit.position for unit in self.ally_units]
            target_path = self.pathfinder.get_nearest_target(unit.position, [my_corner], allies_position)
            # setting target
            self.target_manager.set_target_of_unit(unit, my_target)

            # move to next position
            # PERTE DE 1 TOUR??? ON ARRANGE ÇA?
            next_position = target_path.get_next_position()
            return self.create_move_action(unit, next_position)
        else:
            enemies_nearby = [enemies for enemies in self.enemy_units if
                              self.tick.map.get_tile_type_at(
                                  enemies.position) == TileType.EMPTY and self.pathfinder.simple_distance(
                                  enemies.position, unit.position) < 1.5]
            if enemies_nearby:
                if self.tick.map.get_tile_type_at(unit.position) == TileType.EMPTY:
                    return CommandAction(action=CommandType.ATTACK, unitId=unit.id, target=enemies_nearby[0].position)
            else:
                return CommandAction(action=CommandType.NONE, unitId=unit.id, target=None) 
        

    def get_optimal_hodler_move(self, unit: Unit) -> CommandAction:
        current_enemy_units_positions = [unit.position for unit in self.unit_manager.get_spawned_enemy_units()]
        if unit.isSummoning:
            return CommandAction(action=CommandType.NONE, unitId=unit.id, target=None)
        if self.tick.tick == self.tick.totalTick - 1:
            return self.create_drop_action(unit)
        elif self.position_is_dangerous(unit, current_enemy_units_positions):
            return self.create_drop_action(unit)
        elif (self.tick.tick < self.tick.totalTick - 7
              and not unit.isSummoning
              and not unit.diamondId in [x.id for x in self.tick.map.diamonds if x.summonLevel == 5]
              and self.summoning_is_safe(unit, current_enemy_units_positions)
        ):
            return self.create_summon_action(unit)
        else:
            nearest_enemy_pos = self.get_nearest_enemy_position(unit, current_enemy_units_positions)
            if nearest_enemy_pos is None:
                return CommandAction(action=CommandType.NONE, unitId=unit.id, target=None)
            new_pos = self.move_away_from_target_pos(unit, nearest_enemy_pos)
            return self.create_move_action(unit, new_pos)

    def move_to_nearest_diamond(self, unit: Unit) -> CommandAction:
        # todo voir si une autre unit serait plus proche du target
        untargeted_diamond = [diamond for diamond in self.tick.map.diamonds if
                              self.target_manager.target_is_available_for_unit(unit,
                                                                               diamond.position)]
    
        untargeted_diamond = [diamond for diamond in untargeted_diamond  if diamond.position not in  [self.corner[0],self.corner[1]]]


        # formating targets
        target_list = [Target(TargetType.DIAMOND, diamond, diamond.position) for diamond in
                       self.unit_manager.get_available_diamonds() if
                       self.target_manager.target_is_available_for_unit(unit, diamond.position)]

        allies_position = [unit.position for unit in self.unit_manager.get_spawned_allied_units()]
        # finding nearest diamond
        target_path = self.pathfinder.get_nearest_target(unit.position, target_list, allies_position)
        if target_path is None:
            return CommandAction(action=CommandType.NONE, unitId=unit.id, target=None)

        # setting target
        self.target_manager.set_target_of_unit(unit, target_path.target)

        # move to next position
        next_position = target_path.get_next_position()

        return self.create_move_action(unit, next_position)

    def create_move_action(self, unit: Unit, destination: Position) -> CommandAction:
        if not unit.hasDiamond:
            enemies_nearby = [enemies for enemies in self.unit_manager.get_spawned_enemy_units() if
                              self.tick.map.get_tile_type_at(
                                  enemies.position) == TileType.EMPTY and self.pathfinder.simple_distance(
                                  enemies.position, unit.position) < 1.5]
            if enemies_nearby:
                if self.tick.map.get_tile_type_at(unit.position) == TileType.EMPTY:
                    return CommandAction(action=CommandType.ATTACK, unitId=unit.id, target=enemies_nearby[0].position)
                else:
                    delta_x = enemies_nearby[0].position.x - unit.position.x
                    if delta_x:  # si delta_x ça veux dire qu'il est à droite ou à gauche
                        try:
                            pos = Position(enemies_nearby[0].position.x + 1, enemies_nearby[0].position.y)
                            if self.tick.map.get_tile_type_at(pos) == TileType.EMPTY:
                                return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=pos)

                            pos = Position(enemies_nearby[0].position.x - 1, enemies_nearby[0].position.y)
                            if self.tick.map.get_tile_type_at(pos) == TileType.EMPTY:
                                return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=pos)
                        except:
                            pass
                    else:
                        try:
                            pos = Position(enemies_nearby[0].position.x, enemies_nearby[0].position.y + 1)
                            if self.tick.map.get_tile_type_at(pos) == TileType.EMPTY:
                                return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=pos)

                            pos = Position(enemies_nearby[0].position.x, enemies_nearby[0].position.y - 1)
                            if self.tick.map.get_tile_type_at(pos) == TileType.EMPTY:
                                return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=pos)
                        except:
                            pass
                return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=self.find_free_adjacent_tile(unit))
        return CommandAction(action=CommandType.MOVE, unitId=unit.id, target=destination)

    def create_drop_action(self, unit: Unit) -> CommandAction:
        droppable_pos = self.find_free_adjacent_tile(unit)
        return CommandAction(action=CommandType.DROP, unitId=unit.id, target=droppable_pos)

    def create_summon_action(self, unit: Unit) -> CommandAction:
        return CommandAction(action=CommandType.SUMMON, unitId=unit.id, target=None)

    def find_free_adjacent_tile(self, unit: Unit) -> Position:
        current_unit_positions = self.get_current_unit_positions()
        try:
            pos = Position(unit.position.x - 1, unit.position.y)
            if (self.tick.map.get_tile_type_at(pos) == TileType.EMPTY
                    and pos not in current_unit_positions):
                return pos
        except:
            pass
        try:
            pos = Position(unit.position.x + 1, unit.position.y)
            if (self.tick.map.get_tile_type_at(pos) == TileType.EMPTY
                    and pos not in current_unit_positions):
                return pos
        except:
            pass
        try:
            pos = Position(unit.position.x, unit.position.y - 1)
            if (self.tick.map.get_tile_type_at(pos) == TileType.EMPTY
                    and pos not in current_unit_positions):
                return pos
        except:
            pass
        try:
            pos = Position(unit.position.x, unit.position.y + 1)
            if (self.tick.map.get_tile_type_at(pos) == TileType.EMPTY
                    and pos not in current_unit_positions):
                return pos
        except:
            pass

    def get_current_unit_positions(self):
        current_unit_positions = []
        for team in self.tick.teams:
            for unit in team.units:
                current_unit_positions.append(unit.position)
        return current_unit_positions

    def get_current_enemy_units(self) -> List[Unit]:
        current_enemy_units = []
        for team in self.tick.teams:
            if team.id != self.tick.teamId:
                for unit in team.units:
                    if unit.hasSpawned:
                        current_enemy_units.append(unit)
        return current_enemy_units

    def get_nearest_enemy_position(self, unit: Unit, enemy_pos: List[Position]):
        if not enemy_pos:
            return None
        closest_pos = None
        for pos in enemy_pos:
            if pos:
                closest_pos = pos
                break
        if closest_pos:
            closest_distance = self.get_distance(unit.position, closest_pos)
            if closest_distance is not None:
                for pos in enemy_pos:
                    current_distance = self.get_distance(unit.position, pos)
                    if current_distance is not None and current_distance < closest_distance:
                        closest_pos = pos
                        closest_distance = current_distance
        return closest_pos

    def move_away_from_target_pos(self, unit: Unit, target_pos: Position) -> Position:
        current_unit_positions = self.get_current_unit_positions()
        current_distance = self.get_distance(unit.position, target_pos)
        best_position = unit.position

        diamond_list_position_on_ground = [diamond.position for diamond in self.tick.map.diamonds if
                                           not diamond.ownerId]

        try:
            new_pos = Position(unit.position.x - 1, unit.position.y)
            is_diamond_on_ground = [position for position in diamond_list_position_on_ground if
                                    position.x == new_pos.x and position.y == new_pos.y]
            if self.tick.map.get_tile_type_at(new_pos) == TileType.EMPTY and not is_diamond_on_ground:
                new_distance = self.get_distance(new_pos, target_pos)

                if new_pos not in current_unit_positions and new_distance > current_distance:
                    best_position = new_pos
                    current_distance = new_distance

        except:
            pass
        try:
            new_pos = Position(unit.position.x + 1, unit.position.y)
            is_diamond_on_ground = [position for position in diamond_list_position_on_ground if
                                    position.x == new_pos.x and position.y == new_pos.y]
            if self.tick.map.get_tile_type_at(new_pos) == TileType.EMPTY and not is_diamond_on_ground:
                new_distance = self.get_distance(new_pos, target_pos)

                if new_pos not in current_unit_positions and new_distance > current_distance:
                    best_position = new_pos
                    current_distance = new_distance
        except:
            pass
        try:
            new_pos = Position(unit.position.x, unit.position.y - 1)
            is_diamond_on_ground = [position for position in diamond_list_position_on_ground if
                                    position.x == new_pos.x and position.y == new_pos.y]
            if self.tick.map.get_tile_type_at(new_pos) == TileType.EMPTY and not is_diamond_on_ground:
                new_distance = self.get_distance(new_pos, target_pos)

                if new_pos not in current_unit_positions and new_distance > current_distance:
                    best_position = new_pos
                    current_distance = new_distance
        except:
            pass
        try:
            new_pos = Position(unit.position.x, unit.position.y + 1)
            is_diamond_on_ground = [position for position in diamond_list_position_on_ground if
                                    position.x == new_pos.x and position.y == new_pos.y]
            if self.tick.map.get_tile_type_at(new_pos) == TileType.EMPTY and not is_diamond_on_ground:
                new_distance = self.get_distance(new_pos, target_pos)

                if new_pos not in current_unit_positions and new_distance > current_distance:
                    best_position = new_pos
                    current_distance = new_distance
        except:
            pass

        return best_position

    def position_is_dangerous(self, unit: Unit, enemy_pos: List[Position]) -> bool:
        for pos in enemy_pos:
            distance = self.pathfinder.simple_distance(unit.position, pos)
            if distance is not None and distance < 2:
                return True
        return False

    def summoning_is_safe(self, unit: Unit, enemy_positions: List[Position]) -> bool:
        # inefficient
        unit_diamond = [x for x in self.tick.map.diamonds if x.id == unit.diamondId][0]
        for pos in enemy_positions:
            distance = self.get_distance(unit.position, pos)
            if distance is not None and distance <= unit_diamond.summonLevel + 3:
                return False
        return True

    def get_distance(self, origin: Position, destination: Position) -> int:
        target_path = self.pathfinder.get_nearest_target(origin, [Target(TargetType.EMPTY, None, destination)])
        return target_path.get_distance() if target_path else None
