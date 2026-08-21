import numpy as np
from .geometry import AbstractGeometry
from .structs_3d import *

class Geometry3d(AbstractGeometry):
  # geometría 3d
  def create_point(self, coord: tuple[float, ...]) -> Point3D: # crea un punto
    return Point3D(x = coord[0], y = coord[1], z = coord[2])

  def create_simplex(self, vertices: tuple[Point3D, ...]) -> Tetrahedron3D:
    return Tetrahedron3D(vertices)

  def create_halfspace(self, points: tuple[Point3D, Point3D]) -> Halfspace3D: 
    # crea un semiespacio
    return Halfspace3D(points = points)

  def create_halfspace_from_vector(self, normalVector: np.ndarray, b: float) -> Halfspace3D: # crea un semiespacio
    return Halfspace3D(normalVector = normalVector, b = b)