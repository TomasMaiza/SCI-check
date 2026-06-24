import numpy as np
from .geometry import AbstractGeometry
from .structs_2d.point2d import Point2D
from .structs_2d.halfspace2d import Halfspace2D
from .structs_2d.lpipoint2d import LPIPoint2D
from .structs_2d.triangle2d import Triangle2D

class Geometry2d(AbstractGeometry):
  # geometría 2d
  def create_point(self, coord: tuple[float, float]) -> Point2D: # crea un punto
    return Point2D(x = coord[0], y = coord[1])

  def create_lpi_point(self, coord: tuple[float, float], hs: Halfspace2D) -> LPIPoint2D: # crea un punto lpi
    return LPIPoint2D(x = coord[0], y = coord[1], halfspace = hs)

  def create_simplex(self, vertices: tuple[Point2D, Point2D, Point2D]) -> Triangle2D: # crea un simplex
    return Triangle2D(v1 = vertices[0], v2 = vertices[1], v3 = vertices[2])

  def create_halfspace(self, normal: tuple[float, float], offset: float) -> Halfspace2D: 
    # crea un semiespacio
    return Halfspace2D(normal_x = normal[0], normal_y = normal[1], offset = offset)