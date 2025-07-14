import pygame
import time
from cell import Cell
from food import Food
from prey import Prey
from predator import Predator
import matplotlib.pyplot as plt
import threading

DEFAULT_WINDOW_SIZE = (1000, 800)
DEFAULT_BG_COLOUR = (200, 200, 200)
DEFAULT_CELL_SIZE = (20, 20)
DEFAULT_PREY_GENERATION_POPULATION = 200
DEFAULT_PRED_GENERATION_POPULATION = 50
DEFAULT_GENERATION_TIMEFRAME = 21
DEFAULT_FOOD_POPULATION = 150
PREDATOR_SPAWN_GENERATION = 200

class NaturaNet:
    def __init__(self, width=DEFAULT_WINDOW_SIZE[0], height=DEFAULT_WINDOW_SIZE[1], fps=60):
        pygame.display.init()
        pygame.mixer.init()
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
        self.prey = []
        self.predators = []
        self.generation = 0
        self.foodSpawnSize = 1
        self.generationTimeFrame = DEFAULT_GENERATION_TIMEFRAME
        self.foodPerGeneration = DEFAULT_FOOD_POPULATION
        self.allPredDead = False

        # Initialize grid cells
        for y in range(DEFAULT_WINDOW_SIZE[1] // DEFAULT_CELL_SIZE[1]):
            temp = []
            for x in range(DEFAULT_WINDOW_SIZE[0] // DEFAULT_CELL_SIZE[0]):
                temp.append(Cell(x, y, 0))
            self.cells.append(temp)
        self.startNewGeneration()

        # Load sprites
        sprite = pygame.image.load("Assets\\food1.png").convert_alpha()
        sprite = pygame.transform.scale(sprite, (11, 11))
        Food.sprite = sprite

        sprite = pygame.image.load("Assets\\prey1.png").convert_alpha()
        sprite = pygame.transform.scale(sprite, (18, 18))
        Prey.sprite = sprite

        sprite = pygame.image.load("Assets\\pred1.png").convert_alpha()
        sprite = pygame.transform.scale(sprite, (21, 21))
        Predator.sprite = sprite

    def displayStats(self):
        """
        Mostly for debugging, when space is pressed statistcs of process will be shown
        on graphs.
        """
        generations = list(range(len(Prey.means)))
        fig, (axis1, axis2) = plt.subplots(1, 2, figsize=(12,5))
        # prey first
        axis1.plot(generations, Prey.means, label="Mean")
        axis1.plot(generations, Prey.medians, label="Median")
        axis1.plot(generations, Prey.bests, label="Best")
        #axis1.plot(generations, Prey.worsts, label="Worst")
        axis1.plot(generations, Prey.stds, label="Standard Deviation")
        axis1.set_title("Prey Statistics")
        axis1.set_xlabel("Generation")
        axis1.set_ylabel("Darwin Factor")
        axis1.legend()
        axis1.grid(True)
        # predators second
        if self.generation > PREDATOR_SPAWN_GENERATION:
            axis2.plot(generations, Predator.means, label="Mean")
            axis2.plot(generations, Predator.medians, label="Median")
            axis2.plot(generations, Predator.bests, label="Best")
            #axis2.plot(generations, Predator.worsts, label="Worst")
            axis2.plot(generations, Predator.stds, label="Standard Deviation")
            axis2.set_title("Predator Statistics")
            axis2.set_xlabel("Generation")
            axis2.set_ylabel("Darwin Factor")
            axis2.legend()
            axis2.grid(True)

        plt.tight_layout()
        plt.show()


    def eventHandler(self, gen_elapsed):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.displayStats()

        allDead = all(prey.TTL <= 0 for prey in self.prey)
        self.allPredDead = all(pred.TTL <= 0 for pred in self.predators)

        if gen_elapsed >= self.generationTimeFrame or allDead:
            self.startNewGeneration()
            self.genStartTime = time.perf_counter()

    def startNewGeneration(self):
        """
        Starts a new generation. If first generation, it populates prey with random intelligence;
        after that, uses mixing neural networks, mutations, and random injections. Predators
        start from generation 200 onward to give prey a head start. Super mutations every 10 generations,
        longer timeframes every 20 generations, and increased food every 40 generations.
        """
        if self.generation == 0:
            self.prey = [Prey((self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(DEFAULT_PREY_GENERATION_POPULATION)]
        else:
            self.cells = []
            for y in range(DEFAULT_WINDOW_SIZE[1] // DEFAULT_CELL_SIZE[1]):
                temp = []
                for x in range(DEFAULT_WINDOW_SIZE[0] // DEFAULT_CELL_SIZE[0]):
                    temp.append(Cell(x, y, 0))
                self.cells.append(temp)

            if self.generation % 10 == 0:
                Prey.mutationRate = 0.08
                Prey.mutationStrength = 0.15

            self.prey = Prey.regenPopulation(self.prey, self.generation, 25, Prey, self.width, self.height, DEFAULT_CELL_SIZE)
            if self.generation > PREDATOR_SPAWN_GENERATION:
                self.predators = Predator.regenPopulation(self.predators, self.generation, 12, Predator, self.width, self.height, DEFAULT_CELL_SIZE)
        if self.generation == PREDATOR_SPAWN_GENERATION:
            self.predators = [Predator((self.width, self.height), DEFAULT_CELL_SIZE) for _ in range(DEFAULT_PRED_GENERATION_POPULATION)]

        Prey.mutationRate = 0.05
        Prey.mutationStrength = 0.1

        self.generation += 1

        if self.generation % 20 == 0 and self.generationTimeFrame <= 100:
            self.generationTimeFrame += 5
        if self.generation % 40 == 0 and self.generation <= 100:
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

    def update(self, deltaTime):
        """
        Resets cells, updates TTLs using real-time delta, spawns food at correct intervals,
        updates positions, and handles collisions.
        """
        for row in self.cells:
            for cell in row:
                cell.preyCoords = []
                cell.hasPrey = False
                cell.resetColour()

        # Food spawn logic
        self.foodSpawnTimer += deltaTime
        if self.foodSpawnTimer >= 1.0:
            self.foodSpawnTimer -= 1.0
            for _ in range(self.foodSpawnSize):
                newFood = Food((self.width, self.height), DEFAULT_CELL_SIZE)
                self.food.append(newFood)
                self.cells[newFood.parentCell[1]][newFood.parentCell[0]].hasFood = True
                self.cells[newFood.parentCell[1]][newFood.parentCell[0]].foodCoords.append((newFood.x, newFood.y))

        # Update prey
        for prey in self.prey:
            prey.setDarwinFactor()
            if prey.TTL > 0:
                prey.TTL -= deltaTime
                prey.update(self.cells, self.generation, self.allPredDead)
                self.cells[prey.parentCell[1]][prey.parentCell[0]].preyCoords.append((prey.x, prey.y))
                self.cells[prey.parentCell[1]][prey.parentCell[0]].hasPrey = True

        # Update predators
        for row in self.cells:
            for cell in row:
                cell.hasPred = False
                cell.predCoords = []
                cell.resetColour()

        for pred in self.predators:
            pred.setDarwinFactor()
            if pred.TTL > 0:
                pred.TTL -= deltaTime
                pred.update(self.cells)
                self.cells[pred.parentCell[1]][pred.parentCell[0]].predCoords.append((pred.x, pred.y))
                self.cells[pred.parentCell[1]][pred.parentCell[0]].hasPred = True

        # Handle collisions
        for prey in self.prey:
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
                        prey.eatenPenalty += 20
                        pred.eat()
                        break

    def draw(self):
        """
        Resets the screen, draws cells, prey, predators, food, and overlays generation number text.
        """
        self.display.fill(DEFAULT_BG_COLOUR)
        for y in range(self.height // DEFAULT_CELL_SIZE[1]):
            for x in range(self.width // DEFAULT_CELL_SIZE[1]):
                pygame.draw.rect(self.display, self.cells[y][x].colour, (self.cells[y][x].x, self.cells[y][x].y, DEFAULT_CELL_SIZE[0], DEFAULT_CELL_SIZE[1]))
        text = self.font.render(f"Generation: {self.generation}", True, (0, 0, 0))
        text.set_alpha(128)
        self.display.blit(text, (10, 10))
        for food in self.food:
            if food is not None:
                self.display.blit(Food.sprite, (food.x, food.y))
        for prey in self.prey:
            if prey.TTL > 0:
                self.display.blit(Prey.sprite, (prey.x, prey.y))
        for pred in self.predators:
            if pred.TTL > 0:
                self.display.blit(Predator.sprite, (pred.x, pred.y))
        pygame.display.flip()

    def run(self):
        """
        Main loop. Handles events, updates agents using real-time seconds,
        draws, and ensures correct frame pacing.
        """
        self.lastTime = time.perf_counter()
        self.genStartTime = self.lastTime
        self.foodSpawnTimer = 0.0

        while self.running:
            currentTime = time.perf_counter()
            deltaTime = currentTime - self.lastTime
            self.lastTime = currentTime

            genElapsed = currentTime - self.genStartTime

            self.eventHandler(genElapsed)
            self.update(deltaTime)
            self.draw()
            self.clock.tick(self.fps)

        pygame.quit()

if __name__ == "__main__":
    simulatorInstance = NaturaNet()
    simulatorInstance.run()
