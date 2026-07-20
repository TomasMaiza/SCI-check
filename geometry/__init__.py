from .geometry import AbstractGeometry
from .geometry_2d import Geometry2d

GeometryFactory = {2: Geometry2d} # agregar acá las distintas dimensiones

__all__ = ["AbstractGeometry", "GeometryFactory"]