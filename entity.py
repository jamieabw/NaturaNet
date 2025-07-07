import random
import numpy as np
from NN.denseLayer import DenseLayer
from NN.tanh import Tanh
from NN.softmax import Softmax
class Entity:
    def __init__(self, random, windowSize, cellSize, network=None, foodEaten=0, TTL=20):
        self.x = random.randint(0, windowSize[0]-1)
        self.y = random.randint(0, windowSize[1]-1)
        self.cellSize = cellSize
        self.windowSize = windowSize
        self.parentCell = (self.x // self.cellSize[0], self.y // self.cellSize[1])
        self.foodEaten = foodEaten
        self.TTL = TTL
        self.previousXMove = 0
        self.previousYMove = 0
        if network is None:
            self.intelligence = [
                DenseLayer(8, 6),
                Tanh(),
                DenseLayer(6, 5),
                Softmax()
            ]
        else:
            self.intelligence = network

    def getStimuli(self):
        pass

    def movement(self):
        pass

    def predict(self, input):
        output = input
        for layer in self.intelligence:
            output = layer.forwardPropagation(np.nan_to_num(output, nan=0.0))
        return output

    def eat(self):
        pass

    def setDarwinFactor(self):
        if self.TTL > 0:
            #print("survived")
            self.darwinFactor = self.moveCloserBonus + (self.foodDiscovered * 2) + self.TTL + (self.foodEaten * 20) - self.penalty
        else:
            self.darwinFactor = self.moveCloserBonus + (self.foodDiscovered * 2) + (self.foodEaten * 5) - self.penalty
            #print("dead")

    @classmethod
    def evolve(cls):
        pass

    def findNearestFood(self):
        pass

    def getAdjacentCells(self):
        pass

    def getRect(self):
        pass