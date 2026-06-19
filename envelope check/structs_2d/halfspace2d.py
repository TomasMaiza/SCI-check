from abstract_structs import AbstractHalfspace
from .point2d import Point2D
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class Halfspace2D(AbstractHalfspace):
  # representación de un semiespacio en 2D
  normal_x: float
  normal_y: float
  offset: float

  def __post_init__(self): # verificación de que el vector normal no es nulo
    if self.normal_x == 0.0 and self.normal_y == 0.0:
      raise ValueError("El vector normal no puede ser nulo.")

  def get_halfspace(self) -> np.ndarray: # retorna la representación vectorial del semiespacio
    return np.array([self.normal_x, self.normal_y, self.offset])

  def get_points(self) -> tuple[Point2D, Point2D]: 
    # calcula y retorna los puntos que definen el semiespacio
    norm_sq = (self.normal_x ** 2) + (self.normal_y ** 2)

    p1_x = (self.offset * self.normal_x) / norm_sq # proyección p1
    p1_y = (self.offset * self.normal_y) / norm_sq

    p2_x = p1_x - self.normal_y # proyección p2
    p2_y = p1_y + self.normal_x

    return Point2D(x=p1_x, y=p1_y), Point2D(x=p2_x, y=p2_y)