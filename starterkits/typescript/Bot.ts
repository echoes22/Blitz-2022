import { GameMessage, Action, Position } from "./GameInterface";

export class Bot {
  constructor() {
    console.log("Initializing your super duper mega bot");
    // This method should be use to initialize some variables you will need throughout the game.
  }

  /*
   * Here is where the magic happens, for now the moves are random. I bet you can do better ;)
   *
   * No path finding is required, you can simply send a destination per unit and the game will move your unit towards
   * it in the next turns.
   */
  getNextMove(gameMessage: GameMessage): Action[] {
    const spawnPoints = gameMessage.getSpawnPoints();
    const randomSpawnPoint =
      spawnPoints[Math.floor(Math.random() * spawnPoints.length)];
    const myTeam = gameMessage.getPlayerMapById().get(gameMessage.teamId);
    const randomPosition: Position = {
      x: Math.round(Math.random() * gameMessage.getHorizontalSize()),
      y: Math.round(Math.random() * gameMessage.getVerticalSize()),
    };

    return myTeam.units.map((unit) => {
      if (!unit.hasSpawned) {
        return {
          action: "SPAWN",
          target: randomSpawnPoint,
          type: "UNIT",
          unitId: unit.id,
        };
      }

      return {
        action: "MOVE",
        target: randomPosition,
        type: "UNIT",
        unitId: unit.id,
      };
    });
  }
}
