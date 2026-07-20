from abc import ABC, abstractmethod
import numpy as np
from geometry.abstract_structs.point import AbstractPoint

class AbstractHalfspace(ABC):
  # representación de un semiespacio en un espacio n-dimensional
  @abstractmethod
  def get_points(self) -> tuple[AbstractPoint, ...]: # retorna los puntos que definen el semiespacio
    pass