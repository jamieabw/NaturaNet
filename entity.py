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
    def regenPopulation(cls, previousPopulation, generation, N, entity, width, height, cellSize) -> list:
        """
        Regenerates the population at the start of a new generation, gets the top N entities of that kind,
        automatically reinjects the top 5 best entities, and inject 5 with random intelligence then refills
        the rest of the population with merged networks from the top N best entities, applies random mutations too.
        """
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
            childIntelligence = cls.evolve(parentA, parentB)
            newPopulation.append(entity((width, height), cellSize, network=childIntelligence))
        return newPopulation

    def getStimuli(self) -> tuple:
        """
        Returns a tuple of the distances from each wall to be called as a super in subclasses.
        """
        distanceFromTop = self.y / self.windowSize[1]
        distanceFromBottom = (self.windowSize[1] - self.y) / self.windowSize[1]
        distanceFromLeft = self.x / self.windowSize[0]
        distanceFromRight = (self.windowSize[0] - self.x) / self.windowSize[0]
        return (distanceFromBottom, distanceFromTop, distanceFromLeft, distanceFromRight)

    def movement(self, stimuli, cells):
        """
        Utilises the entities intelligence to make a decision of which direction to move, or
        whether they should move at all. Applies a fixed penalty if an attempt to get out of
        bounds is made to prevent wall hugging.
        """
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

    def predict(self, input) -> np.array:
        """
        Iteratively passes the input through the neural network to get the decision.
        """
        output = input
        for layer in self.intelligence:
            output = layer.forwardPropagation(np.nan_to_num(output, nan=0.0))
        return output

    def eat(self):
        """
        Increases TTL (Time To Live) of entity when they consume their specific food type.
        """
        self.TTL += 5
        self.foodEaten += 1

    def setDarwinFactor(self):
        """
        How the top N successful entities per generation are calculated, takes into account numerous bonuses
        and penalties to weed out the most successful entities. Those who are deal get a heavily reduced fitness
        regardless of food consumption.
        """
        if self.TTL > 0:
            self.darwinFactor = self.moveCloserBonus + (self.foodDiscovered * 2) + self.TTL + (self.foodEaten * 20) - self.penalty
        else:
            self.darwinFactor = self.moveCloserBonus + (self.foodDiscovered * 2) + (self.foodEaten * 5) - self.penalty - self.eatenPenalty

    @classmethod
    def evolve(cls, parentA, parentB) -> list:
        """
        Merges two neural networks together randomly to simulate genetic inheritance,
        mutations are randomly applied at random strengths to diversify the gene pool.
        """
        childNetwork = []
        for layerA, layerB in zip(parentA.intelligence, parentB.intelligence):
            if isinstance(layerA, DenseLayer)and isinstance(layerB, DenseLayer):
                weightMask = np.random.rand(*layerA.weights.shape) < 0.5
                biasMask = np.random.rand(*layerA.biases.shape) < 0.5
                childWeights = np.where(weightMask, layerA.weights, layerB.weights)
                childBias = np.where(biasMask, layerA.biases, layerB.biases)
                newLayer = DenseLayer(layerA.weights.shape[1], layerA.weights.shape[0])
                weightMutationMask = np.random.rand(*childWeights.shape) < cls.mutationRate
                childWeights += weightMutationMask * np.random.normal(0, cls.mutationStrength, childWeights.shape)
                biasMutationMask = np.random.rand(*childBias.shape)< cls.mutationRate
                childBias += biasMutationMask * np.random.normal(0, cls.mutationStrength, childBias.shape)
                childWeights = np.clip(childWeights, -1, 1)
                childBias   = np.clip(childBias, -1, 1)

                newLayer.weights = childWeights
                newLayer.biases = childBias
                childNetwork.append(newLayer)
            elif isinstance(layerA, Tanh) and isinstance(layerB, Tanh):
                childNetwork.append(Tanh())
            elif isinstance(layerA, Softmax) and isinstance(layerB, Softmax):
                childNetwork.append(Softmax())
            else:
                raise ValueError(f"Layer mismatch: {type(layerA)} vs {type(layerB)}")
        return childNetwork

    def update(self):
        pass

    def findNearest(self, cells, toFind) -> tuple:
        """
        Gets the nearest (specific type of entity [food, prey, predators]) using djikstra's then
        calculates tile and x, y distance.
        """
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
                    continue 
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

    def getAdjacentCells(self, x, y, currentDist, visited, cells) -> list:
        """
        Returns the left, right, up and down cells relative to the cell the entity is in,
        used for djikstra's.
        """
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