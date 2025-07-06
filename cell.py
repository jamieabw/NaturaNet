DEFAULT_HEIGHT_COLOURS = [(200,200,200), (175,175,175), (150,150,150), (125,125,125)]
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

