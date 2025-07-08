from NN.denseLayer import DenseLayer
from NN.tanh import Tanh
from NN.softmax import Softmax
import numpy as np
from entity import Entity
import math
import pygame
import random
DEFAULT_PREY_SIZE = 15
DEFAULT_PREY_SPEED = 2
class Prey(Entity):
    sprite = None
    def __init__(self, windowSize, cellSize, network=None, TTL=20, size=DEFAULT_PREY_SIZE):
        super().__init__(windowSize, cellSize, DEFAULT_PREY_SPEED, network, TTL, size, "Prey")

    def getStimuli(self, foodCell, cells, tileDistanceToFood, predCell, tileDistanceToPred):
        distanceFromBottom, distanceFromTop, distanceFromLeft, distanceFromRight = super().getStimuli()
        dyFood, dxFood = (cells[foodCell[0]][foodCell[1]].foodCoords[0][1] - self.y)/100,(cells[foodCell[0]][foodCell[1]].foodCoords[0][0] - self.x)/100
        dyPred, dxPred = (cells[predCell[0]][predCell[1]].predCoords[0][1] - self.y)/220,(cells[predCell[0]][predCell[1]].predCoords[0][0] - self.x)/220
        stimuli = np.array([dxFood, dyFood, tileDistanceToFood / 6,
                            dxPred, dyPred, tileDistanceToPred /6,
                             distanceFromTop, distanceFromBottom, distanceFromLeft, distanceFromRight,
                               self.previousXMove, self.previousYMove])
        noise = np.random.normal(0, 0.01, stimuli.shape) 
        #print(f"PREY from predator: \n{dxPred, dyPred}")
        return stimuli + noise


    def movement(self, distanceToFood, foodCell, distanceToPred, predCell, cells):
        if self.TTL <= 0:
            return
        euclideanDistance = math.sqrt((cells[foodCell[0]][foodCell[1]].foodCoords[0][0] - self.x) ** 2 + (cells[foodCell[0]][foodCell[1]].foodCoords[0][1] - self.y) ** 2)
        if euclideanDistance < self.shortestDistanceEver:
            self.shortestDistanceEver = euclideanDistance
            self.moveCloserBonus += 0.1
        stimuli = self.getStimuli(foodCell, cells, distanceToFood, predCell, distanceToPred)
        super().movement(stimuli, cells)

    def update(self,cells):
        self.setDarwinFactor()
        (nearestCellWithFood), distanceToCellWithFood = self.findNearest(cells, "Food")
        (nearestCellWithPred), distanceToCellWithPred = self.findNearest(cells, "Predator")
        self.movement(distanceToCellWithFood, nearestCellWithFood, distanceToCellWithPred, nearestCellWithPred, cells)
        if not cells[nearestCellWithFood[0]][nearestCellWithFood[1]].foodDiscovered:
                    cells[nearestCellWithFood[0]][nearestCellWithFood[1]].foodDiscovered = True
                    self.foodDiscovered += 1
        #cells[nearestCellWithFood[0]][nearestCellWithFood[1]].colour = (0,0,0)



    


    
        

        

    

    
