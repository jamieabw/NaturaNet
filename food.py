FOOD_SIZE =  5
class Food:
    colour = (255,0,0)
    def __init__(self, random, windowSize, cellSize):
        self.x = random.randint(0, windowSize[0])
        self.y = random.randint(0,windowSize[1])
        self.size = FOOD_SIZE
        self.parentCell = (self.x // cellSize[0], self.y // cellSize[1])
