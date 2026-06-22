from geometry.abstract_structs.point import AbstractPoint
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class Point2D(AbstractPoint):
  # representación de un punto en el plano
  x: float
  y: float
  id: int

  def id(self) -> int: # id del punto
    return self.id

  def get_point(self) -> np.ndarray: # retorna la representación vectorial del punto
    return np.array([self.x, self.y])