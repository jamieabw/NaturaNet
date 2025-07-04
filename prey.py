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
    def __init__(self, random, windowSize, cellSize, network=None, foodEaten=0, TTL=15, darwinFactor=0):
        self.x = random.randint(0, windowSize[0])
        self.y = random.randint(0, windowSize[1])
        self.cellSize = cellSize
        self.windowSize = windowSize
        self.parentCell = (self.x // self.cellSize[0], self.y // self.cellSize[1])
        self.foodEaten = foodEaten
        self.TTL = TTL
        self.darwinFactor = darwinFactor
        # intelligence will be based on 6 input neurones: x, y, distance to food  (x, y), distance to predator (x, y)
        # architecture is 6,10,10,16,2
        if network is None:
            self.intelligence = [
                DenseLayer(3, 10),
                Tanh(),
                DenseLayer(10, 10),
                Tanh(),
                DenseLayer(10,16),
                Tanh(),
                DenseLayer(16,2),
                Tanh()
            ]
        else:
            self.intelligence = network

    def movement(self, distanceToFood, distanceToPred, cells):
        decision = self.predict(np.array([self.x / 1000, self.y / 800, distanceToFood]))
        xMove, yMove = decision
        #print(xMove.shape, yMove.shape)
        if self.x + xMove * DEFAULT_PREY_SPEED >= 1000 or self.x + xMove * DEFAULT_PREY_SPEED <= 0:
            xMove = 0
        if self.y + yMove * DEFAULT_PREY_SPEED >= 800 or self.y + yMove * DEFAULT_PREY_SPEED <= 0:    
            yMove = 0
        
        #print(int(self.y + yMove * DEFAULT_PREY_SPEED) // self.cellSize[1], int(self.x + xMove * DEFAULT_PREY_SPEED) // self.cellSize[0],)
        #print(np.array(cells).shape)
        #print(self.parentCell)
        if  cells[int(self.y + yMove * DEFAULT_PREY_SPEED) // self.cellSize[1]][int(self.x + xMove * DEFAULT_PREY_SPEED) // self.cellSize[0]].heightLevel <= cells[self.parentCell[1]][self.parentCell[0]].heightLevel + 1:
            self.x += xMove * DEFAULT_PREY_SPEED
            self.y += yMove * DEFAULT_PREY_SPEED
            self.parentCell = (int(self.x // self.cellSize[0]), int(self.y // self.cellSize[1]))
            #print(self.parentCell)

    def predict(self, input):
        output = input
        for layer in self.intelligence:
            output = layer.forwardPropagation(output)
        return output
    
    def eat(self):
        self.TTL += 5
        self.foodEaten += 1
        
    def setDarwinFactor(self):
        # function will be used to set a darwin factor which is what will be used to determine the most fit agents to reproduce for the next generation
        #self.darwinFactor = self.foodEaten * deathPenalty * someOtherAttribute
        pass
    
    """NOTE: REMEMBER CELLS[y][x] ACCESSES the x, y cell on a regular grid"""
    def findNearestFruit(self, cells):
        start_x, start_y = self.parentCell
        cellsToCheck = [(start_x, start_y, 0)]  # (x, y, distance)
        visited = set()
        visited.add((start_x, start_y))

        while cellsToCheck:
            newCells = []
            for x, y, dist in cellsToCheck:
                currentCell = cells[y][x]
                if currentCell.hasFood:
                    # You can now return both the cell and the distance value
                    return currentCell, dist

                adjacent = self.getAdjacentCells(x, y, dist, visited, cells)
                newCells.extend(adjacent)

            cellsToCheck = newCells

        return None, None  # No reachable food

    
        

        

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

    
