import numpy as np

class Layer:
    def __init__(self):
        self.weights = None
        self.biases = None

    def forwardPropagation(self, input):
        pass

# back propagation not necessary as new generations created from merging previous survivors.