from .enums import *
from .types import *
from .logger import *

IN = OrientResult.IN
OUT = OrientResult.OUT
ON = OrientResult.ON

SUBREGION = PolytopeType.SUBREGION
BASE = PolytopeType.BASE

__all__ = ["OrientResult",  
           "PolytopeType",
           "SerializedPolytopeMap",
           "Point",
           "Edge", 
           "VerticesIndex", 
           "EdgesIndex", 
           "ON", 
           "OUT", 
           "IN",
           "SUBREGION",
           "BASE",
           "setup_logger",
           "log"]