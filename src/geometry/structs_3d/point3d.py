from geometry.abstract_structs.point import AbstractPoint
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class Point3D(AbstractPoint):
  # representación de un punto en el plano
  x: float
  y: float
  z: float

  def get_point(self) -> tuple[float, float, float]: # retorna la representación vectorial del punto
    return (self.x, self.y, self.z)