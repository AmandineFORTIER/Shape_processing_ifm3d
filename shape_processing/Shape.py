from enum import Enum

class Shape(Enum):
    """
    Enum to define the different types of shapes.

    These shapes can be detected by this algorithm.
    ALL : detects all types of shapes.\n
    PARTIAL : detects the shapes that are on the edge of the image.\n
    UNKNOW : if it's another type of shape.
    """
    ALL = 0
    CIRCLE = 1
    ELLIPSE = 2
    TRIANGLE = 3
    SQUARE = 4
    RECTANGLE = 5
    PENTAGON = 6
    HEXAGON = 7
    HEPTAGON = 8
    OCTAGON = 9
    PARTIAL = 10
    UNKNOW = 11