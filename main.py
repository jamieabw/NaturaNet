import pygame
from cell import Cell
from food import Food
from prey import Prey
from predator import Predator
DEFAULT_WINDOW_SIZE = (1000, 800)
DEFAULT_BG_COLOUR = (200,200,200)
DEFAULT_CELL_SIZE = (20, 20)
DEFAULT_PREY_GENERATION_POPULATION = 200
DEFAULT_PRED_GENERATION_POPULATION = 40
DEFAULT_GENERATION_TIMEFRAME = 15
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
        self.allPredDead = False
        for y in range(DEFAULT_WINDOW_SIZE[1] // DEFAULT_CELL_SIZE[1]):
            temp = []
            for x in range(DEFAULT_WINDOW_SIZE[0] // DEFAULT_CELL_SIZE[1]):
                temp.append(Cell(x, y,0))
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
        self.allPredDead = all(pred.TTL <= 0 for pred in self.predators)
        if self.clockTickCounter == self.fps * self.generationTimeFrame or allDead:
            self.clockTickCounter = 0
            self.startNewGeneration()

    def startNewGeneration(self):
        """
        Starts a new generation, if first generation it populates the prey with random intelligence, after that it will use a combination
        of mixing neural networks, mutations, and also random intelligence injections into the population. After generation 50, predators will
        also be populated so the prey have an advantageous head start. Every 10th generation 'super mutations' will be activated where prey are
        more likely to get a mutated weight or bias in their neural network intelligence, and the mutation will be more extreme than other generations
        in order to increase the gene pool. Every 20th generation the timeframe will increase by 5 seconds up until 100 seconds. Every 40th generation,
        1 more food will spawn per second up until 3 food per second (generation 120).
        """
        if self.generation == 0:
            self.prey = [Prey((self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(DEFAULT_PREY_GENERATION_POPULATION)]
        elif self.generation == 50:
            self.predators = [Predator((self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(DEFAULT_PRED_GENERATION_POPULATION)]
        else:
            self.cells = []
            for y in range(DEFAULT_WINDOW_SIZE[1] // DEFAULT_CELL_SIZE[1]):
                temp = []
                for x in range(DEFAULT_WINDOW_SIZE[0] // DEFAULT_CELL_SIZE[1]):
                    temp.append(Cell(x, y, 0))
                self.cells.append(temp)
            if self.generation != 0 and self.generation % 10 == 0:
                Prey.mutationRate = 0.4
                Prey.mutationStrength = 0.3
            self.prey = Prey.regenPopulation(self.prey, self.generation, 25, Prey, self.width, self.height, DEFAULT_CELL_SIZE)
            if self.generation > 50:
                self.predators = Predator.regenPopulation(self.predators, self.generation, 10, Predator, self.width, self.height, DEFAULT_CELL_SIZE)
        Prey.mutationRate = 0.2
        Prey.mutationStrength = 0.05
        self.generation += 1
        if self.generation % 20 == 0 and self.generationTimeFrame <= 100:
            self.generationTimeFrame += 5
        if self.generation != 0 and self.generation % 40 == 0 and self.generation <= 100:
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
        """
        Resets all cells so they dont contain any predators, so those which do contain a predator can be flagged (so the prey can find the nearest
        predator using djikstra's). Adds n food to the map to prevent prey from dying out as the generation time frame increases. Also, deals with
        collisions for prey, predator and food.
        """
        for row in self.cells:
            for cell in row:
                cell.preyCoords = []
                cell.hasPrey = False
                cell.resetColour()

        if self.clockTickCounter % self.fps == 0:
            self.food.extend([Food((self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(self.foodSpawnSize)])
            self.cells[self.food[-1].parentCell[1]][ self.food[-1].parentCell[0]].hasFood = True
            self.cells[self.food[-1].parentCell[1]][ self.food[-1].parentCell[0]].foodCoords.append((self.food[-1].x, self.food[-1].y))
        if self.clockTickCounter % 2 == 0:
            for prey in self.prey:
                prey.setDarwinFactor()
                if prey.TTL > 0:
                    prey.update(self.cells, self.generation, self.allPredDead)
                    self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords.append((prey.x, prey.y))
                    self.cells[prey.parentCell[1]][prey.parentCell[0]].hasPrey = True
            for row in self.cells:
                for cell in row:
                    cell.hasPred = False
                    cell.predCoords = []
                    cell.resetColour()
            for pred in self.predators:
                pred.setDarwinFactor()
                if pred.TTL <= 0:
                    continue
                pred.update(self.cells)
                if self.clockTickCounter % (self.fps) == 0:
                    pred.TTL -=1
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
                    if preyRect.colliderect(foodRect):  
                        if len(self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords) == 1:
                            self.cells[food.parentCell[1]][food.parentCell[0]].hasFood = False
                            self.cells[food.parentCell[1]][food.parentCell[0]].foodDiscovered = False
                        if (food.x, food.y) in self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords:
                            self.cells[food.parentCell[1]][food.parentCell[0]].foodCoords.remove((food.x, food.y))
                        self.food.remove(food)
                        prey.eat()
                        break
                for pred in self.predators:
                    if pred.TTL <= 0:
                        continue
                    predRect = pred.getRect()
                    if preyRect.colliderect(predRect):
                        if len(self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords) == 1:
                            self.cells[prey.parentCell[1]][prey.parentCell[0]].hasPrey = False
                        if (prey.x, prey.y) in self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords:
                            self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords.remove((prey.x, prey.y))
                            prey.TTL = 0
                            prey.eatenPenalty += 50
                            pred.eat()
                            break

    
    def draw(self):
        """
        Resets the screen, draws the cells, prey and predators, draws the text detailing the generation number on the top right.
        """
        self.display.fill(DEFAULT_BG_COLOUR)
        for y in range(self.height // DEFAULT_CELL_SIZE[1]):
            for x in range(self.width // DEFAULT_CELL_SIZE[1]):
                pygame.draw.rect(self.display, self.cells[y][x].colour, (self.cells[y][x].x, self.cells[y][x].y, DEFAULT_CELL_SIZE[0], DEFAULT_CELL_SIZE[1]))
        text = self.font.render(f"Generation: {self.generation}", True, (0, 0, 0))
        text.set_alpha(128)
        self.display.blit(text, (10, 10))
        for food in self.food:
            if food is not None: self.display.blit(Food.sprite, (food.x, food.y))
        for prey in self.prey:
            if prey.TTL > 0: self.display.blit(Prey.sprite, (prey.x, prey.y))
        for pred in self.predators:
            if pred.TTL > 0: self.display.blit(Predator.sprite, (pred.x, pred.y))
        self.display.blit(text, (10, 10))
        pygame.display.flip()

    def run(self):
        """
        Main game loop.
        """
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