import numpy as np
from entity import Entity
import math
DEFAULT_PREY_SIZE = 15
DEFAULT_PREY_SPEED = 1
class Prey(Entity):
    sprite = None
    means = []
    medians = []
    bests = []
    worsts = []
    stds = []
    def __init__(self, windowSize, cellSize, network=None, TTL=20, size=DEFAULT_PREY_SIZE):
        super().__init__(windowSize, cellSize, DEFAULT_PREY_SPEED, network, TTL, size, "Prey")

    def getStimuli(self, foodCell, cells, tileDistanceToFood, predCell, tileDistanceToPred) -> np.array:
        """
        Creates an array of the various stimuli that will be used as inputs for the prey's intelligence,
        inputs are distance from each wall (normalised), distance from nearest predator (x, y, tiles all normalised), 
        distance from nearest food (x, y, tiles all normalised), adds a random amount of noise to improve their intelligence
        by varying the input signals slightly.
        """
        distanceFromBottom, distanceFromTop, distanceFromLeft, distanceFromRight = super().getStimuli()
        dyFood, dxFood = (cells[foodCell[0]][foodCell[1]].foodCoords[0][1] - self.y)/100,(cells[foodCell[0]][foodCell[1]].foodCoords[0][0] - self.x)/100
        if predCell is not None:
            dyPred, dxPred = (cells[predCell[0]][predCell[1]].predCoords[0][1] - self.y)/220,(cells[predCell[0]][predCell[1]].predCoords[0][0] - self.x)/220
        else:
             dyPred, dxPred, tileDistanceToPred = 1200 / 220, 1200/220, 60
        stimuli = np.array([dxFood, dyFood,
                            dxPred, dyPred,
                             distanceFromTop, distanceFromBottom, distanceFromLeft, distanceFromRight,
                               self.previousXMove, self.previousYMove])
        #print(stimuli)
        #noise = np.random.normal(0, 0.01, stimuli.shape) 
        return stimuli #+ noise


    def movement(self, distanceToFood, foodCell, distanceToPred, predCell, cells):
        """
        Deals with movement, if the prey is alive, get the stimuli then pass it through the prey's neural network
        to get a movement direction to apply.
        """
        if self.TTL <= 0:
            return
        euclideanDistance = math.sqrt((cells[foodCell[0]][foodCell[1]].foodCoords[0][0] - self.x) ** 2 + (cells[foodCell[0]][foodCell[1]].foodCoords[0][1] - self.y) ** 2)
        if euclideanDistance < self.shortestDistanceEver:
            self.shortestDistanceEver = euclideanDistance
            self.moveCloserBonus += 0.1
        stimuli = self.getStimuli(foodCell, cells, distanceToFood, predCell, distanceToPred)
        super().movement(stimuli, cells)

    def update(self,cells,generation, allDead):
        """
        Updates the prey's darwin factor (fitness) whilst still alive, gets the nearest food and predator
        (if generation >= 50), then updates the movement.
        """
        self.setDarwinFactor()
        (nearestCellWithFood), distanceToCellWithFood = self.findNearest(cells, "Food")
        if generation >= 50 and not allDead:
            (nearestCellWithPred), distanceToCellWithPred = self.findNearest(cells, "Predator")
        else:
             (nearestCellWithPred), distanceToCellWithPred = None, None
        self.movement(distanceToCellWithFood, nearestCellWithFood, distanceToCellWithPred, nearestCellWithPred, cells)
        if not cells[nearestCellWithFood[0]][nearestCellWithFood[1]].foodDiscovered:
                    cells[nearestCellWithFood[0]][nearestCellWithFood[1]].foodDiscovered = True
                    self.foodDiscovered += 1



    


    
        

        

    

    
