DEFAULT_HEIGHT_COLOURS = [(0,200,0), (0,175,0), (0,150,0), (0,125,0)]
DEFAULT_CELL_SIZE = (20, 20)

class Cell:
    def __init__(self, xPos, yPos, heightLevel):
        self.heightLevel = heightLevel
        self.colour = DEFAULT_HEIGHT_COLOURS[self.heightLevel]
        self.x = xPos * 20
        self.y = yPos * 20
        self.hasFood = False
        self.hasPred = False
        self.foodCoords = []
        self.discovered = False
    def resetColour(self):
        self.colour = DEFAULT_HEIGHT_COLOURS[self.heightLevel]

