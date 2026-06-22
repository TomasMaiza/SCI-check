from enum import Enum

class OrientResult(Enum):
    # indica de qué lado de un semiespacio está un vértice
    IN = 1
    OUT = -1
    ON = 0