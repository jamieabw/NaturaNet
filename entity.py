import random
import numpy as np
from NN.denseLayer import DenseLayer
from NN.tanh import Tanh
from NN.softmax import Softmax
import random
import pygame

class Entity:
    mutationRate = 0.2
    mutationStrength = 0.05
    def __init__(self, windowSize, cellSize, speed, network=None, TTL=20, size=7, tag=None):
        self.x = random.randint(0, windowSize[0]-40)
        self.y = random.randint(0, windowSize[1]-40)
        self.cellSize = cellSize
        self.windowSize = windowSize
        self.size = size
        self.parentCell = ((self.x + (self.size // 2)) // self.cellSize[0], (self.y + (self.size // 2)) // self.cellSize[1])
        self.foodEaten = 0
        self.foodDiscovered = 0
        self.TTL = TTL
        self.previousXMove = 0
        self.previousYMove = 0
        self.darwinFactor = 0
        self.penalty = 0
        self.moveCloserBonus = 0
        self.shortestDistanceEver = 999
        self.speed = speed
        self.eatenPenalty = 0
        if network is None and tag=="Prey":
            self.intelligence = [
                DenseLayer(12, 12), # this will be different to predator eventually
                Tanh(),
                DenseLayer(12, 5),
                Softmax()
            ]
        elif network is None and tag=="Predator":
            self.intelligence = [
                DenseLayer(9, 8),
                Tanh(),
                DenseLayer(8, 5),
                Softmax()
            ]
        else:
            self.intelligence = network

    @classmethod
    def regenPopulation(cls, previousPopulation, generation, N, entity, width, height, cellSize):
        newPopulation = []
        populationSize = len(previousPopulation)
        previousSortedPopulation = sorted(previousPopulation, key=lambda x : x.darwinFactor, reverse=True)
        topNOfPopulation = previousSortedPopulation[:N]
        print(f"GENERATION {generation}: {[_.darwinFactor for _ in topNOfPopulation]}")
        for i in range(5):
            newPopulation.append(entity((width, height), cellSize, network=topNOfPopulation[i].intelligence))
        for i in range(5):
            newPopulation.append(entity((width, height), cellSize, network=None))
        while len(newPopulation) != populationSize:
            parentA = random.choice(topNOfPopulation)
            parentB = random.choice(topNOfPopulation)
            #print(parentA, parentB)
            childIntelligence = cls.evolve(parentA, parentB)
            newPopulation.append(entity((width, height), cellSize, network=childIntelligence))
        return newPopulation

    def getStimuli(self):
        distanceFromTop = self.y / self.windowSize[1]
        distanceFromBottom = (self.windowSize[1] - self.y) / self.windowSize[1]
        distanceFromLeft = self.x / self.windowSize[0]
        distanceFromRight = (self.windowSize[0] - self.x) / self.windowSize[0]
        return (distanceFromBottom, distanceFromTop, distanceFromLeft, distanceFromRight)

    def movement(self, stimuli, cells):
        decision = np.argmax(self.predict(stimuli))
        xMove, yMove = 0,0
        if decision == 0:
            yMove = -1
        elif decision == 1:
            yMove = 1
        elif decision == 2:
            xMove = -1
        elif decision == 3:
            xMove = 1
        elif decision == 4:
            pass

        if self.x + xMove * self.speed >= 1000 or self.x + xMove * self.speed <= 0:
            xMove = 0
            self.penalty += 1
        if self.y + yMove * self.speed >= 800 or self.y + yMove * self.speed <= 0:    
            yMove = 0
            self.penalty += 1

        self.previousXMove = xMove
        self.previousYMove = yMove
        newX = int(((self.x + xMove * self.speed) + (self.size // 2)) // self.cellSize[0])
        newY = int(((self.y + yMove * self.speed)+ (self.size // 2)) // self.cellSize[1])
        newX = max(0, min(newX, len(cells[0]) - 1))
        newY = max(0, min(newY, len(cells) - 1))

        if cells[newY][newX].heightLevel <= cells[self.parentCell[1]][self.parentCell[0]].heightLevel + 1:
            self.x += xMove * self.speed
            self.y += yMove * self.speed
            self.parentCell = (newX, newY)
            #print(self.parentCell)

    def predict(self, input):
        output = input
        for layer in self.intelligence:
            output = layer.forwardPropagation(np.nan_to_num(output, nan=0.0))
        return output

    def eat(self):
        self.TTL += 5
        self.foodEaten += 1

    def setDarwinFactor(self):
        if self.TTL > 0:
            #print("survived")
            self.darwinFactor = self.moveCloserBonus + (self.foodDiscovered * 2) + self.TTL + (self.foodEaten * 20) - self.penalty
        else:
            self.darwinFactor = self.moveCloserBonus + (self.foodDiscovered * 2) + (self.foodEaten * 5) - self.penalty - self.eatenPenalty
            #print("dead")

    @classmethod
    def evolve(cls, parentA, parentB):
        # no mutation added yet, pure natural selection
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
                #
                #print(childWeights)
                #print(layerA.weights.shape[1], layerA.weights.shape[0])
                """if np.random.rand() < mutationRate:
                    childWeights += np.random.normal(0, mutationStrength, childWeights.shape)
                    childBias += np.random.normal(0, mutationStrength, childBias.shape)"""
                weightMutationMask = np.random.rand(*childWeights.shape) < cls.mutationRate
                childWeights += weightMutationMask * np.random.normal(0, cls.mutationStrength, childWeights.shape)
                biasMutationMask = np.random.rand(*childBias.shape)< cls.mutationRate
                childBias += biasMutationMask * np.random.normal(0, cls.mutationStrength, childBias.shape)
                    #print(childWeights)
                childWeights = np.clip(childWeights, -1, 1)
                childBias   = np.clip(childBias, -1, 1)

                newLayer.weights = childWeights
                newLayer.biases = childBias
                childNetwork.append(newLayer)
            elif isinstance(layerA, Tanh) and isinstance(layerB, Tanh):
                # You can just copy one of them since activations do not have parameters
                childNetwork.append(Tanh())
            elif isinstance(layerA, Softmax) and isinstance(layerB, Softmax):
                # You can just copy one of them since activations do not have parameters
                childNetwork.append(Softmax())
            else:
                raise ValueError(f"Layer mismatch: {type(layerA)} vs {type(layerB)}")
        #childNetwork.reverse()
        #print(np.array(childNetwork).shape)
        return childNetwork

    def update(self):
        pass

    def findNearest(self, cells, toFind):
        startX, startY = self.parentCell
        cellsToCheck = [(startX, startY, 0)]  # (x, y, distance)
        visited = set()
        visited.add((startX, startY))

        while cellsToCheck:
            newCells = []
            for x, y, dist in cellsToCheck:
                gridWidth = len(cells[0])
                gridHeight = len(cells)
                if not (0 <= x < gridWidth and 0 <= y < gridHeight):
                    print(f"Out-of-bounds access attempt: x={x}, y={y}")
                    continue  # skip this iteration
                currentCell = cells[y][x]
                if toFind == "Food":
                    if currentCell.hasFood:
                        return (y, x), dist
                elif toFind == "Prey":
                    if currentCell.hasPrey:
                        return (y, x), dist
                    
                elif toFind == "Predator":
                    if currentCell.hasPred:
                        return (y, x), dist
                adjacent = self.getAdjacentCells(x, y, dist, visited, cells)
                newCells.extend(adjacent)

            cellsToCheck = newCells

        return None, None # No reachable food

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
        return pygame.Rect(self.x, self.y, self.size, self.size)