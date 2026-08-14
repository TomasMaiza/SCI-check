from .enums import *
from .types import *
from .logger import *

IN = OrientResult.IN
OUT = OrientResult.OUT
ON = OrientResult.ON

__all__ = ["OrientResult", 
           "PolytopeMap", 
           "SerializedPolytopeMap",
           "Edge", 
           "VerticesIndex", 
           "EdgesIndex", 
           "ON", 
           "OUT", 
           "IN",
           "setup_logger",
           "log"]