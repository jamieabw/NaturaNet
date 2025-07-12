from entity import Entity
import numpy as np
import math
DEFAULT_PRED_SIZE = 18
DEFAULT_PRED_SPEED = 1.05
class Predator(Entity):
    sprite = None
    def __init__(self, windowSize, cellSize, network=None, TTL=20):
        super().__init__(windowSize, cellSize, DEFAULT_PRED_SPEED, network, TTL, DEFAULT_PRED_SIZE, "Predator")

    def getStimuli(self, preyCell, cells, tileDistanceToPrey) -> np.array:
        """
        Creates a list of stimuli which be used as inputs for the predator's intelligence. Stimuli
        includes: distance to nearest prey (x, y, tiles all normalised) and distance to walls (normalised).
        """
        distanceFromBottom, distanceFromTop, distanceFromLeft, distanceFromRight = super().getStimuli()
        dy, dx = (cells[preyCell[0]][preyCell[1]].preyCoords[0][1] - self.y)/220,(cells[preyCell[0]][preyCell[1]].preyCoords[0][0] - self.x)/220
        stimuli = np.array([dx, dy, tileDistanceToPrey / 12, distanceFromTop, distanceFromBottom, distanceFromLeft, distanceFromRight, self.previousXMove, self.previousYMove])
        noise = np.random.normal(0, 0.01, stimuli.shape) 
        return stimuli + noise
    
    def movement(self, distanceToCellWithPrey, nearestCellWithPrey, cells):
        """
        Deals with movement, if the predator is alive, get the stimuli then pass it through the prey's neural network
        to get a movement direction to apply.
        """
        if self.TTL < 0:
            return
        euclideanDistance = math.sqrt((cells[nearestCellWithPrey[0]][nearestCellWithPrey[1]].preyCoords[0][0] - self.x) ** 2 
                                      + (cells[nearestCellWithPrey[0]][nearestCellWithPrey[1]].preyCoords[0][1] - self.y) ** 2)
        if euclideanDistance < self.shortestDistanceEver:
            self.shortestDistanceEver = euclideanDistance
            self.moveCloserBonus += 0.1
        stimuli = self.getStimuli(nearestCellWithPrey, cells, distanceToCellWithPrey)
        super().movement(stimuli, cells)


    def eat(self):
        """
        Increases TTL (Time To Live) of predator by 3 seconds every time a prey is eaten (due to the abundance of prey).
        """
        self.TTL += 3
        self.foodEaten += 1
    
    def update(self, cells):
        """
        Sets the darwin factor (Fitness) of the predator, finds the nearest prey and deals
        with movement.
        """
        self.setDarwinFactor()
        (nearestCellWithPrey), distanceToCellWithPrey = self.findNearest(cells, "Prey")
        self.movement(distanceToCellWithPrey, nearestCellWithPrey, cells)

        