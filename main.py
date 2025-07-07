import pygame
from cell import Cell
from food import Food
from prey import Prey
from predator import Predator
import random
import copy
DEFAULT_WINDOW_SIZE = (1000, 800)
DEFAULT_BG_COLOUR = (200,200,200)
DEFAULT_CELL_SIZE = (20, 20)
DEFAULT_PREY_GENERATION_POPULATION = 200
DEFAULT_PRED_GENERATION_POPULATION = 10
DEFAULT_GENERATION_TIMEFRAME = 10
DEFAULT_FOOD_POPULATION = 150

class NaturaNet:
    def __init__(self, width=DEFAULT_WINDOW_SIZE[0], height=DEFAULT_WINDOW_SIZE[1], fps=60):
        pygame.display.init()
        pygame.mixer.init() # joystock.init causing problems with hanging so initialised separately 
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 30)
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
        self.generation = 0
        self.foodSpawnSize = 1
        self.generationTimeFrame = DEFAULT_GENERATION_TIMEFRAME
        self.foodPerGeneration = DEFAULT_FOOD_POPULATION
        for y in range(DEFAULT_WINDOW_SIZE[1] // DEFAULT_CELL_SIZE[1]):
            temp = []
            for x in range(DEFAULT_WINDOW_SIZE[0] // DEFAULT_CELL_SIZE[1]):
                temp.append(Cell(x, y, 0))
            self.cells.append(temp)
        self.startNewGeneration()
        # NOTE: self.cells[y][x] accesses cell (x,y)

    def eventHandler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        allDead = all(prey.TTL <= 0 for prey in self.prey)
        if self.clockTickCounter == self.fps * self.generationTimeFrame or allDead:
            self.clockTickCounter = 0
            self.startNewGeneration()

    def startNewGeneration(self):
        if self.generation == 0:
            self.prey = [Prey(random, (self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(DEFAULT_PREY_GENERATION_POPULATION)]
        else:
            newPrey = []
            self.cells = []
            for y in range(DEFAULT_WINDOW_SIZE[1] // DEFAULT_CELL_SIZE[1]):
                temp = []
                for x in range(DEFAULT_WINDOW_SIZE[0] // DEFAULT_CELL_SIZE[1]):
                    temp.append(Cell(x, y, 0))
                self.cells.append(temp)
            if self.generation != 0 and self.generation % 10 == 0:
                Prey.mutationRate = 0.4
                Prey.mutationStrength = 0.3
            sortedPrey = sorted(self.prey, key=lambda x : x.darwinFactor, reverse=True)
            topPrey = sortedPrey[:10]
            print(f"GENERATION: {self.generation}\nTOP PREY: {[topPrey[i].darwinFactor for i in range(10)]}")
            self.prey = []
            for i in range(5):                                                                                                                             
                newPrey.append(Prey(random, (self.width, self.height), DEFAULT_CELL_SIZE, network=copy.deepcopy(topPrey[i].intelligence)))
            for i in range(5):
                newPrey.append(Prey(random, (self.width, self.height), DEFAULT_CELL_SIZE, network=None))
                #print(f"GENERATION {self.generation}: {i} BEST SURVIVOR FROM PREVIOUS GENERATION: {topPrey[i].darwinFactor}")
            while len(newPrey) != DEFAULT_PREY_GENERATION_POPULATION:
                parentA = random.choice(topPrey)
                parentB = random.choice(topPrey)
                childIntelligence = Prey.evolvePrey(parentA, parentB)
                if childIntelligence is not None:
                    newPrey.append(Prey(random, (self.width, self.height), DEFAULT_CELL_SIZE, network=copy.deepcopy(childIntelligence)))
            self.prey = newPrey
        Prey.mutationRate = 0.2
        Prey.mutationStrength = 0.05
        self.generation += 1
        if self.generation % 15 == 0:
            self.generationTimeFrame += 5
        if self.generation != 0 and self.generation % 40 == 0:
            self.foodPerGeneration += 10
            self.foodSpawnSize += 1
        self.predators = []
        self.food = [Food(random, (self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(self.foodPerGeneration)]
        for food in self.food:
            self.cells[food.parentCell[1]][food.parentCell[0]].hasFood = True
            self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords.append((food.x, food.y))
        self.clockTickCounter = 0

    def update(self):
        if self.clockTickCounter % self.fps == 0:
            self.food.extend([Food(random, (self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(self.foodSpawnSize)])
            self.cells[self.food[-1].parentCell[1]][ self.food[-1].parentCell[0]].hasFood = True
            self.cells[self.food[-1].parentCell[1]][ self.food[-1].parentCell[0]].foodCoords.append((self.food[-1].x, self.food[-1].y))
        if self.clockTickCounter % 5 == 0:
            for prey in self.prey:
                #print(prey.TTL)
                if prey.TTL == 0:
                    Prey.preyPopulation -= 1
                prey.setDarwinFactor()
                (y, x), distance = prey.findNearestFruit(self.cells)
                prey.movement(distance, (y,x),random.randint(0,10), self.cells)
                #cellToHigh = self.cells[y][x]
                #print()
                #self.cells[y][x].colour = (0,0,0)
                if not self.cells[y][x].discovered:
                    self.cells[y][x].discovered = True
                    prey.foodDiscovered += 1
        for prey in self.prey:
            if self.clockTickCounter % (self.fps) == 0:
                prey.TTL -= 1
            if prey.TTL <= 0:
                continue
            preyRect = prey.getRect()
            for food in self.food:
                foodRect = food.getRect()
                if preyRect.colliderect(foodRect):#food.parentCell == prey.parentCell and preyRect.colliderect(foodRect):
                    
                    if len(self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords) == 1:
                        self.cells[food.parentCell[1]][food.parentCell[0]].hasFood = False
                        self.cells[food.parentCell[1]][food.parentCell[0]].resetColour()
                    if (food.x, food.y) in self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords:
                        self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords.remove((food.x, food.y))
                    #print(self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords)
                    self.food.remove(food)
                    prey.foodEaten += 1
                    prey.TTL += 5
                    #print(prey.foodEaten)
                    break

    
    def draw(self):
        self.display.fill(DEFAULT_BG_COLOUR)
        for y in range(self.height // DEFAULT_CELL_SIZE[1]):
            for x in range(self.width // DEFAULT_CELL_SIZE[1]):
                pygame.draw.rect(self.display, self.cells[y][x].colour, (self.cells[y][x].x, self.cells[y][x].y, DEFAULT_CELL_SIZE[0], DEFAULT_CELL_SIZE[1]))
                """if not self.cells[y][x].hasFood:
                    pygame.draw.rect(self.display, self.cells[y][x].colour, (self.cells[y][x].x, self.cells[y][x].y, DEFAULT_CELL_SIZE[0], DEFAULT_CELL_SIZE[1]))
                else:
                    pygame.draw.rect(self.display, (0,0,0), (self.cells[y][x].x, self.cells[y][x].y, DEFAULT_CELL_SIZE[0], DEFAULT_CELL_SIZE[1]))"""
        text = self.font.render(f"Generation: {self.generation}", True, (0, 0, 0))
        text.set_alpha(128)
        self.display.blit(text, (10, 10))
        for food in self.food:
            if food is not None: pygame.draw.rect(self.display, Food.colour, (food.x, food.y, food.size, food.size))
        for prey in self.prey:
            if prey.TTL > 0: pygame.draw.rect(self.display, (0,0,255), (prey.x, prey.y, Prey.size, Prey.size))
        for pred in self.predators:
            pygame.draw.rect(self.display, (255,0,0), (pred.x, pred.y, pred.size, pred.size))
        self.display.blit(text, (10, 10))
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