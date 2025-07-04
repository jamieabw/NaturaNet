from NN.denseLayer import DenseLayer
from NN.tanh import Tanh
import numpy as np
import math

DEFAULT_PREY_SIZE = 7
DEFAULT_PREY_VISION_SCOPE = 5
DEFAULT_PREY_SPEED = 2
class Prey:
    size = DEFAULT_PREY_SIZE
    def __init__(self, random, windowSize, cellSize, network=None):
        self.x = random.randint(0, windowSize[0])
        self.y = random.randint(0, windowSize[1])
        self.parentCell = (self.x // cellSize[0], self.y // cellSize[1])
        # intelligence will be based on 6 input neurones: x, y, distance to food  (x, y), distance to predator (x, y)
        # architecture is 6,10,10,16,2
        if network is None:
            self.intelligence = [
                DenseLayer(6, 10),
                Tanh(),
                DenseLayer(10, 10),
                Tanh(),
                DenseLayer(10,16),
                Tanh(),
                DenseLayer(16,2),
                Tanh()
            ]
        else:
            self.intelligence = network

    def movement(self, distanceToFood, distanceToPred):
        decision = self.predict(np.array([self.x / 1000, self.y / 800, distanceToFood[0], distanceToFood[1], distanceToPred[0], distanceToPred[1]]))
        xMove, yMove = decision
        #print(xMove.shape, yMove.shape)
        if math.isnan(xMove) or math.isnan(yMove):
            print("nan found")
        if self.x + xMove * DEFAULT_PREY_SPEED < 1000 and self.x + xMove * DEFAULT_PREY_SPEED > 0:
            self.x += xMove * DEFAULT_PREY_SPEED
        if self.y + yMove * DEFAULT_PREY_SPEED < 800 and self.y + yMove * DEFAULT_PREY_SPEED > 0:    
            self.y += yMove * DEFAULT_PREY_SPEED


    def predict(self, input):
        output = input
        for layer in self.intelligence:
            output = layer.forwardPropagation(output)
        return output
