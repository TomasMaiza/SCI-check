from abc import ABC, abstractmethod
import numpy as np
from typing import Optional
from geometry.abstract_structs.point import AbstractPoint

class AbstractHalfspace(ABC):
  # representación de un semiespacio en un espacio n-dimensional
  @abstractmethod
  def get_points(self) -> tuple[AbstractPoint, ...]: # retorna los puntos que definen el semiespacio
    pass

  @abstractmethod
  def create_from_normal_vector(self, normalVector: np.ndarray, b: float): # permite crear el semiespacio a partir del vector normal
    pass