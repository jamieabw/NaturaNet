from NN.baseLayer import Layer
class Activation:
    def __init__(self, function):
        self.function = function

    def forwardPropagation(self, input):
        self.input = input
        return self.function(self.input)