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
DEFAULT_PRED_GENERATION_POPULATION = 20
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
                temp.append(Cell(x, y, random.randint(0,1)))
            self.cells.append(temp)
        self.startNewGeneration()
        # NOTE: self.cells[y][x] accesses cell (x,y)
        sprite = pygame.image.load("Assets\\food1.png").convert_alpha()
        sprite = pygame.transform.scale(sprite, (11, 11))
        Food.sprite = sprite
        sprite = pygame.image.load("Assets\\prey1.png").convert_alpha()
        sprite = pygame.transform.scale(sprite, (18, 18))
        Prey.sprite = sprite
        sprite = pygame.image.load("Assets\\pred1.png").convert_alpha()
        sprite = pygame.transform.scale(sprite, (21, 21))
        Predator.sprite = sprite

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
            self.prey = [Prey((self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(DEFAULT_PREY_GENERATION_POPULATION)]
            self.predators = [Predator((self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(DEFAULT_PRED_GENERATION_POPULATION)]
        else:
            self.cells = []
            for y in range(DEFAULT_WINDOW_SIZE[1] // DEFAULT_CELL_SIZE[1]):
                temp = []
                for x in range(DEFAULT_WINDOW_SIZE[0] // DEFAULT_CELL_SIZE[1]):
                    temp.append(Cell(x, y, random.randint(0,1)))
                self.cells.append(temp)
            if self.generation != 0 and self.generation % 10 == 0:
                Prey.mutationRate = 0.4
                Prey.mutationStrength = 0.3
            self.prey = Prey.regenPopulation(self.prey, self.generation, 10, Prey, self.width, self.height, DEFAULT_CELL_SIZE)
            self.predators = Predator.regenPopulation(self.predators, self.generation, 5, Predator, self.width, self.height, DEFAULT_CELL_SIZE)
        Prey.mutationRate = 0.2
        Prey.mutationStrength = 0.05
        self.generation += 1
        if self.generation % 15 == 0:
            self.generationTimeFrame += 5
        if self.generation != 0 and self.generation % 40 == 0:
            self.foodPerGeneration += 10
            self.foodSpawnSize += 1
        self.food = [Food((self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(self.foodPerGeneration)]
        for food in self.food:
            self.cells[food.parentCell[1]][food.parentCell[0]].hasFood = True
            self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords.append((food.x, food.y))
        for prey in self.prey:
            self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords.append((prey.x, prey.y))
            self.cells[prey.parentCell[1]][prey.parentCell[0]].hasPrey = True
        for pred in self.predators:
            self.cells[pred.parentCell[1]][pred.parentCell[0]].predCoords.append((pred.x, pred.y))
            self.cells[pred.parentCell[1]][pred.parentCell[0]].hasPred = True
        self.clockTickCounter = 0

    def update(self):
        for row in self.cells:
            for cell in row:
                #print(cell.preyCoords)
                #print(cell.predCoords)
                cell.preyCoords = []
                cell.hasPrey = False
                cell.resetColour()

        if self.clockTickCounter % self.fps == 0:
            self.food.extend([Food((self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(self.foodSpawnSize)])
            self.cells[self.food[-1].parentCell[1]][ self.food[-1].parentCell[0]].hasFood = True
            self.cells[self.food[-1].parentCell[1]][ self.food[-1].parentCell[0]].foodCoords.append((self.food[-1].x, self.food[-1].y))
        if self.clockTickCounter % 5 == 0:
            for prey in self.prey:
                #print(prey.TTL)
                #currentCell = (max(0,min((prey.x + (prey.size // 2)) // DEFAULT_CELL_SIZE[0], len(self.cells[0])-1)), max(0,min((prey.y + (prey.size // 2)) // DEFAULT_CELL_SIZE[1], len(self.cells)-1)))
                #prey.parentCell = (currentCell[1], currentCell[0])
                #print(currentCell, prey.parentCell)
                prey.update(self.cells)
                if prey.TTL > 0:
                    self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords.append((prey.x, prey.y))
                    self.cells[prey.parentCell[1]][prey.parentCell[0]].hasPrey = True

                
                #print(self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords)
                #self.cells[prey.parentCell[1]][prey.parentCell[0]].colour = (0,0,0)
                #cellToHigh = self.cells[y][x]
                #print()
            for row in self.cells:
                for cell in row:
                    cell.hasPred = False
                    cell.predCoords = []
                    
            for pred in self.predators:
                pred.update(self.cells)
                self.cells[pred.parentCell[1]][pred.parentCell[0]].predCoords.append((pred.x, pred.y))
                self.cells[pred.parentCell[1]][pred.parentCell[0]].hasPred = True
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
                        self.cells[food.parentCell[1]][food.parentCell[0]].foodDiscovered = False
                        #self.cells[food.parentCell[1]][food.parentCell[0]].resetColour()
                    if (food.x, food.y) in self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords:
                        self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords.remove((food.x, food.y))
                    #print(self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords)
                    self.food.remove(food)
                    prey.foodEaten += 1
                    prey.TTL += 5
                    #print(prey.foodEaten)
                    break
            for pred in self.predators:
                predRect = pred.getRect()
                if preyRect.colliderect(predRect):
                    if len(self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords) == 1:
                        self.cells[prey.parentCell[1]][prey.parentCell[0]].hasPrey = False
                        self.cells[prey.parentCell[1]][prey.parentCell[0]].preyDiscovered = False
                        #self.cells[food.parentCell[1]][food.parentCell[0]].resetColour()
                    if (prey.x, prey.y) in self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords:
                        self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords.remove((prey.x, prey.y))
                        #print(self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords)
                        prey.TTL = 0
                    pred.foodEaten += 1
                    pred.TTL += 5
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
            if food is not None: self.display.blit(Food.sprite, (food.x, food.y))
        for prey in self.prey:
            if prey.TTL > 0: self.display.blit(Prey.sprite, (prey.x, prey.y))
        for pred in self.predators:
            #print("pred")
            if pred.TTL > 0: self.display.blit(Predator.sprite, (pred.x, pred.y))
            #pygame.draw.rect(self.display, (255,0,0), (pred.x, pred.y, pred.size, pred.size))
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