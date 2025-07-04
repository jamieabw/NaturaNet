import pygame
from cell import Cell
from food import Food
from prey import Prey
from predator import Predator
import random
DEFAULT_WINDOW_SIZE = (1000, 800)
DEFAULT_BG_COLOUR = (200,200,200)
DEFAULT_CELL_SIZE = (20, 20)
DEFAULT_PREY_GENERATION_POPULATION = 50
DEFAULT_PRED_GENERATION_POPULATION = 10
DEFAULT_GENERATION_TIMEFRAME = 30

class NaturaNet:
    def __init__(self, width=DEFAULT_WINDOW_SIZE[0], height=DEFAULT_WINDOW_SIZE[1], fps=60):
        pygame.display.init()
        pygame.mixer.init() # joystock.init causing problems with hanging so initialised separately
        pygame.font.init()
        self.width, self.height = width, height
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("NaturaNet")
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.running = True
        self.cells = []
        self.food = []
        self.clockTickCounter = 0
        self.prey = []
        self.predators = []
        for y in range(DEFAULT_WINDOW_SIZE[1] // DEFAULT_CELL_SIZE[1]):
            temp = []
            for x in range(DEFAULT_WINDOW_SIZE[0] // DEFAULT_CELL_SIZE[1]):
                temp.append(Cell(x, y, random.randint(0,3)))
            self.cells.append(temp)
        self.startNewGeneration()
        # NOTE: self.cells[y][x] accesses cell (x,y)

    def eventHandler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        if self.clockTickCounter == self.fps * DEFAULT_GENERATION_TIMEFRAME:
            self.startNewGeneration()

    def startNewGeneration(self):
        self.prey = [Prey(random, (self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(DEFAULT_PREY_GENERATION_POPULATION)]

        self.predators = []
        self.food = [Food(random, (self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(20)]
        self.clockTickCounter = 0

    def update(self):
        if self.clockTickCounter % self.fps == 0: self.food.append(Food(random, (self.width, self.height), DEFAULT_CELL_SIZE))
        if self.clockTickCounter % 5 == 0:
            for prey in self.prey:
                prey.movement((0.2, 0.1), (0.4, 0.3))
        #self.cells[self.food[-1].parentCell[1]][self.food[-1].parentCell[0]].colour = (0,0,0) self
    
    def draw(self):
        self.display.fill(DEFAULT_BG_COLOUR)
        for y in range(self.height // DEFAULT_CELL_SIZE[1]):
            for x in range(self.width // DEFAULT_CELL_SIZE[1]):
                pygame.draw.rect(self.display, self.cells[y][x].colour, (self.cells[y][x].x, self.cells[y][x].y, DEFAULT_CELL_SIZE[0], DEFAULT_CELL_SIZE[1]))
        for food in self.food:
            if food is not None: pygame.draw.rect(self.display, Food.colour, (food.x, food.y, food.size, food.size))
        for prey in self.prey:
            pygame.draw.rect(self.display, (0,255,0), (prey.x, prey.y, Prey.size, Prey.size))
        for pred in self.predators:
            pygame.draw.rect(self.display, (0,0,255), (pred.x, pred.y, pred.size, pred.size))
        pygame.display.flip()

    def run(self):
        while self.running:
            self.eventHandler()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
            self.clockTickCounter += 1
        pygame.quit()

if __name__ == "__main__":
    simulatorInstance = NaturaNet()
    simulatorInstance.run()