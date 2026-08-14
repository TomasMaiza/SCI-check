from .geometry import AbstractGeometry
from .geometry_2d import Geometry2d
from .geometry_3d import Geometry3d
from .abstract_structs import *
from .polytope import *

GeometryFactory = {2: Geometry2d, 3: Geometry3d} # agregar acá las distintas dimensiones

__all__ = ["AbstractGeometry", 
           "GeometryFactory", 
           "AbstractHalfspace", 
           "AbstractPoint", 
           "AbstractSimplex",
           "Polytope",
           "PolytopeImp"]