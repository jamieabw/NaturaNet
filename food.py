import pygame
import random
FOOD_SIZE =  9
class Food:
    colour = (0,255,0)
    sprite = None
    def __init__(self, windowSize, cellSize):
        self.x = random.randint(0, windowSize[0]-40)
        self.y = random.randint(0,windowSize[1]-40)
        self.size = FOOD_SIZE
        self.parentCell = ((self.x + (self.size // 2)) // cellSize[0], (self.y + (self.size // 2)) // cellSize[1])
        self.sprite = pygame.image.load("Assets\\food1.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (11, 11))

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
