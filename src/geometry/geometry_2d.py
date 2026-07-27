import numpy as np
from .geometry import AbstractGeometry
from .structs_2d import *

class Geometry2d(AbstractGeometry):
  # geometría 2d
  def create_point(self, coord: tuple[float, float]) -> Point2D: # crea un punto
    return Point2D(x = coord[0], y = coord[1])

  def create_simplex(self, vertices: tuple[Point2D, Point2D, Point2D]) -> Triangle2D: # crea un simplex
    return Triangle2D(v1 = vertices[0], v2 = vertices[1], v3 = vertices[2])

  def create_halfspace(self, points: tuple[Point2D, Point2D]) -> Halfspace2D: 
    # crea un semiespacio
    return Halfspace2D(points = points)

  def create_halfspace_from_vector(self, normalVector: np.ndarray, b: float) -> AbstractHalfspace: # crea un semiespacio
    return Halfspace2D(normalVector = normalVector, b = b)
