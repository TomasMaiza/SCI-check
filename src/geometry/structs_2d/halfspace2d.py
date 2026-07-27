from geometry.abstract_structs.halfspace import AbstractHalfspace
from .point2d import Point2D
import numpy as np
from typing import Optional

class Halfspace2D(AbstractHalfspace):
  # representación de un semiespacio en 2D
  p1: Point2D
  p2: Point2D

  def __init__(self, points: Optional['tuple[Point2D, Point2D]'] = None, 
               normalVector: Optional[np.ndarray] = None, 
               b: Optional[float] = None):
    if normalVector is None and b is None:
      self.p1 = points[0]
      self.p2 = points[1]
    elif points is None:
      self.create_from_normal_vector(normalVector, b)
    else:
      raise ValueError("Inicialización inválida: Debes proveer (p1, p2) o (normalVector, b).")

  def get_points(self) -> tuple[Point2D, Point2D]: 
    return self.p1, self.p2

  def create_from_normal_vector(self, normalVector: np.ndarray, b: float):
    # crea un semiespacio a partir de la representación vectorial (Ax <= b).
    basePoint = (b / np.dot(normalVector, normalVector)) * normalVector
    perpVector = np.array([-normalVector[1], normalVector[0]]) # el vector perpendicular a (x,y) es (-y, x)
    self.p1 = Point2D((basePoint[0], basePoint[1]))    
    p2 = basePoint + perpVector
    self.p2 = Point2D((p2[0], p2[1]))
