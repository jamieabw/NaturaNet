from entity import Entity
import numpy as np
import math
DEFAULT_PRED_SIZE = 18
DEFAULT_PRED_SPEED = 4
class Predator(Entity):
    sprite = None
    def __init__(self, windowSize, cellSize, network=None, TTL=40):
        super().__init__(windowSize, cellSize, DEFAULT_PRED_SPEED, network, TTL, DEFAULT_PRED_SIZE, "Predator")

    def getStimuli(self, preyCell, cells, tileDistanceToPrey):
        distanceFromBottom, distanceFromTop, distanceFromLeft, distanceFromRight = super().getStimuli()
        dy, dx = (cells[preyCell[0]][preyCell[1]].preyCoords[0][1] - self.y)/220,(cells[preyCell[0]][preyCell[1]].preyCoords[0][0] - self.x)/220
        stimuli = np.array([dx, dy, tileDistanceToPrey / 6, distanceFromTop, distanceFromBottom, distanceFromLeft, distanceFromRight, self.previousXMove, self.previousYMove])
        noise = np.random.normal(0, 0.01, stimuli.shape) 
        #print(f"PREDATOR FROM FOOD: \n{dx, dy}")
        return stimuli + noise
    
    def movement(self, distanceToCellWithPrey, nearestCellWithPrey, cells):
        if self.TTL < 0:
            return
        euclideanDistance = math.sqrt((cells[nearestCellWithPrey[0]][nearestCellWithPrey[1]].preyCoords[0][0] - self.x) ** 2 
                                      + (cells[nearestCellWithPrey[0]][nearestCellWithPrey[1]].preyCoords[0][1] - self.y) ** 2)
        if euclideanDistance < self.shortestDistanceEver:
            self.shortestDistanceEver = euclideanDistance
            self.moveCloserBonus += 0.1
        stimuli = self.getStimuli(nearestCellWithPrey, cells, distanceToCellWithPrey)
        super().movement(stimuli, cells)
    
    def update(self, cells):
        self.setDarwinFactor()
        (nearestCellWithPrey), distanceToCellWithPrey = self.findNearest(cells, "Prey")
        #print(distanceToCellWithPrey)
        #cells[nearestCellWithPrey[0]][nearestCellWithPrey[1]].colour = (0,0,0)
        self.movement(distanceToCellWithPrey, nearestCellWithPrey, cells)
        