import math
from NN.activation import Activation
import numpy as np
class Tanh(Activation):
    def __init__(self):
        self.function = lambda x: (np.exp(2 * x) - 1) / (np.exp(2 * x) + 1)
        super().__init__(self.function)