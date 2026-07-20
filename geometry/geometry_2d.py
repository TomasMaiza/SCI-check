import numpy as np
from .geometry import AbstractGeometry
from .structs_2d.point2d import Point2D
from .structs_2d.halfspace2d import Halfspace2D
from .structs_2d.triangle2d import Triangle2D

class Geometry2d(AbstractGeometry):
  # geometría 2d
  def create_point(self, coord: tuple[float, float]) -> Point2D: # crea un punto
    return Point2D(x = coord[0], y = coord[1])

  def create_simplex(self, vertices: tuple[Point2D, Point2D, Point2D]) -> Triangle2D: # crea un simplex
    return Triangle2D(v1 = vertices[0], v2 = vertices[1], v3 = vertices[2])

  def create_halfspace(self, points: tuple[Point2D, Point2D]) -> Halfspace2D: 
    # crea un semiespacio
    return Halfspace2D(p1 = points[0], p2 = points[1])