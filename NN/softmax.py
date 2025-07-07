import math
from NN.activation import Activation
import numpy as np
class Softmax(Activation):
    def __init__(self):
        self.function = lambda x: np.exp(x - np.max(x)) / np.sum(np.exp(x - np.max(x)))
        super().__init__(self.function)