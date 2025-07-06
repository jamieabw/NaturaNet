from NN.denseLayer import DenseLayer
from NN.tanh import Tanh
import numpy as np
import math
import pygame
DEFAULT_PREY_SIZE = 7
DEFAULT_PREY_VISION_SCOPE = 5
DEFAULT_PREY_SPEED = 2
class Prey:
    size = DEFAULT_PREY_SIZE
    preyPopulation = 0
    def __init__(self, random, windowSize, cellSize, network=None, foodEaten=0, TTL=15, darwinFactor=0):
        self.x = random.randint(0, windowSize[0]-1)
        self.y = random.randint(0, windowSize[1]-1)
        self.cellSize = cellSize
        self.windowSize = windowSize
        self.parentCell = (self.x // self.cellSize[0], self.y // self.cellSize[1])
        self.foodEaten = foodEaten
        self.TTL = TTL
        self.darwinFactor = darwinFactor
        # intelligence will be based on distance to nearest food, distance to nearest predator, angle to both of those in degrees, and (x,y)
        # architecture is 6,10,10,16,2
        if network is None:
            self.intelligence = [
                DenseLayer(2, 8),
                Tanh(),
                DenseLayer(8, 8),
                Tanh(),
                DenseLayer(8,2),
                Tanh()
            ]
        else:
            self.intelligence = network

    def movement(self, distanceToFood, foodCell, distanceToPred, cells):
        if self.TTL <= 0:
            return
        euclideanDistance = math.sqrt((cells[foodCell[0]][foodCell[1]].foodCoords[0][0] - self.x) ** 2 + (cells[foodCell[0]][foodCell[1]].foodCoords[0][1] - self.y) ** 2)
        #print(euclideanDistance / 120)
        dy, dx = (cells[foodCell[0]][foodCell[1]].foodCoords[0][1] - self.y),(cells[foodCell[0]][foodCell[1]].foodCoords[0][0] - self.x)
        #print(self.x, self.y, cells[foodCell[0]][foodCell[1]].foodCoords[0][0], cells[foodCell[0]][foodCell[1]].foodCoords[0][1])
        angle = math.atan2(dy, dx) / math.pi
        #print(angle * math.pi)
        #print(dy, dx)
        #print(self.x, self.y, foodCell[1] * 20, foodCell[0] * 20, angle * math.pi)
        #print(np.array([self.x / 1000, self.y / 800, distanceToFood / 5, angle]))
        #decision = self.predict(np.array([self.x / 1000, self.y / 800, distanceToFood / 5, angle, self.TTL / 30]))
        decision = self.predict(np.array([dy / 100, dx/100]))
        xMove, yMove = decision
        #print(xMove.shape, yMove.shape)
        if self.x + xMove * DEFAULT_PREY_SPEED >= 1000 or self.x + xMove * DEFAULT_PREY_SPEED <= 0:
            xMove = 0
        if self.y + yMove * DEFAULT_PREY_SPEED >= 800 or self.y + yMove * DEFAULT_PREY_SPEED <= 0:    
            yMove = 0
        
        #print(int(self.y + yMove * DEFAULT_PREY_SPEED) // self.cellSize[1], int(self.x + xMove * DEFAULT_PREY_SPEED) // self.cellSize[0],)
        #print(np.array(cells).shape)
        #print(self.parentCell)
        newX = int((self.x + xMove * DEFAULT_PREY_SPEED) // self.cellSize[0])
        newY = int((self.y + yMove * DEFAULT_PREY_SPEED) // self.cellSize[1])
        newX = max(0, min(newX, len(cells[0]) - 1))
        newY = max(0, min(newY, len(cells) - 1))

        if cells[newY][newX].heightLevel <= cells[self.parentCell[1]][self.parentCell[0]].heightLevel + 1:
            self.x += xMove * DEFAULT_PREY_SPEED
            self.y += yMove * DEFAULT_PREY_SPEED
            self.parentCell = (int(self.x // self.cellSize[0]), int(self.y // self.cellSize[1]))
            #print(self.parentCell)

    def predict(self, input):
        output = input
        for layer in self.intelligence:
            output = layer.forwardPropagation(np.nan_to_num(output, nan=0.0))
        #print(output)
        return output
    
    def eat(self):
        self.TTL += 5
        self.foodEaten += 1
        
    def setDarwinFactor(self):
        # function will be used to set a darwin factor which is what will be used to determine the most fit agents to reproduce for the next generation
        #self.darwinFactor = self.foodEaten * deathPenalty * someOtherAttribute
        if self.TTL > 0:
            #print("survived")
            self.darwinFactor = self.foodEaten * 2
        else:
            self.darwinFactor = self.foodEaten * 0.5
            #print("dead")
        pass

    @classmethod
    def evolvePrey(cls, parentA, parentB):
        # no mutation added yet, pure natural selection
        mutationRate = 0.05
        mutationStrength = 0.1
        childNetwork = []
        #print(np.array(parentA.intelligence).shape)
        #print(np.array(parentB.intelligence).shape)
        for layerA, layerB in zip(parentA.intelligence, parentB.intelligence):
            if isinstance(layerA, DenseLayer)and isinstance(layerB, DenseLayer):
                weightMask = np.random.rand(*layerA.weights.shape) < 0.5
                biasMask = np.random.rand(*layerA.biases.shape) < 0.5
                childWeights = np.where(weightMask, layerA.weights, layerB.weights)
                childBias = np.where(biasMask, layerA.biases, layerB.biases)
                newLayer = DenseLayer(layerA.weights.shape[1], layerA.weights.shape[0])
                #print(layerA.weights.shape[1], layerA.weights.shape[0])
                if np.random.rand() < mutationRate:
                    childWeights += np.random.normal(0, mutationStrength, childWeights.shape)
                    childBias += np.random.normal(0, mutationStrength, childBias.shape)
                    #print(childWeights)
                newLayer.weights = childWeights
                newLayer.biases = childBias
                childNetwork.append(newLayer)
            elif isinstance(layerA, Tanh) and isinstance(layerB, Tanh):
                # You can just copy one of them since activations do not have parameters
                childNetwork.append(Tanh())
            else:
                raise ValueError(f"Layer mismatch: {type(layerA)} vs {type(layerB)}")
        #childNetwork.reverse()
        #print(np.array(childNetwork).shape)
        return childNetwork


    
    """NOTE: REMEMBER CELLS[y][x] ACCESSES the x, y cell on a regular grid"""
    def findNearestFruit(self, cells):
        start_x, start_y = self.parentCell
        cellsToCheck = [(start_x, start_y, 0)]  # (x, y, distance)
        visited = set()
        visited.add((start_x, start_y))

        while cellsToCheck:
            newCells = []
            for x, y, dist in cellsToCheck:
                gridWidth = len(cells[0])
                gridHeight = len(cells)
                if not (0 <= x < gridWidth and 0 <= y < gridHeight):
                    print(f"Out-of-bounds access attempt: x={x}, y={y}")
                    continue  # skip this iteration
                currentCell = cells[y][x]
                if currentCell.hasFood:
                    # You can now return both the cell and the distance value
                    return (y, x), dist

                adjacent = self.getAdjacentCells(x, y, dist, visited, cells)
                newCells.extend(adjacent)

            cellsToCheck = newCells

        return 9999, 9999  # No reachable food

    
        

        

    def getAdjacentCells(self, x, y, currentDist, visited, cells):
        gridWidth = len(cells[0])
        gridHeight = len(cells)
        adjacentCells = []

        currentCell = cells[y][x]
        neighbors = []

        if x > 0:
            neighbors.append((x - 1, y))
        if x < gridWidth - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < gridHeight - 1:
            neighbors.append((x, y + 1))

        for nx, ny in neighbors:
            neighborCell = cells[ny][nx]
            if (nx, ny) not in visited:
                if neighborCell.heightLevel <= currentCell.heightLevel or \
                neighborCell.heightLevel == currentCell.heightLevel + 1:
                    adjacentCells.append((nx, ny, currentDist + 1))
                    visited.add((nx, ny))

        return adjacentCells
    
    def getRect(self):
        return pygame.Rect(self.x, self.y, Prey.size, Prey.size)

    
