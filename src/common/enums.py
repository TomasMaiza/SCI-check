from enum import Enum, auto

class OrientResult(Enum):
    # indica de qué lado de un semiespacio está un vértice
    IN = 1
    OUT = -1
    ON = 0

class PolytopeType(Enum):
    # indica si un politopo es una subregión o un poliedro a cubrir
    SUBREGION = auto()
    BASE = auto()