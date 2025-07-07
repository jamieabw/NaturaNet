import pygame
FOOD_SIZE =  7
class Food:
    colour = (0,255,0)
    def __init__(self, random, windowSize, cellSize):
        self.x = random.randint(0, windowSize[0]-1)
        self.y = random.randint(0,windowSize[1]-1)
        self.size = FOOD_SIZE
        self.parentCell = (self.x // cellSize[0], self.y // cellSize[1])

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
