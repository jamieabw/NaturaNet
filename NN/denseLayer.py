import numpy as np
from NN.baseLayer import Layer
class DenseLayer(Layer):
    def __init__(self, inputLength, outputLength):
        self.weights = np.random.randn(outputLength, inputLength)
        self.biases = np.random.randn(outputLength)

    def forwardPropagation(self, input):
        self.input = input
        return np.dot(self.weights, self.input) + self.biases
