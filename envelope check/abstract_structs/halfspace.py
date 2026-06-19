from abc import ABC, abstractmethod
import numpy as np

class AbstractHalfspace(ABC):
  # representación de un semiespacio en un espacio n-dimensional
  @abstractmethod
  def get_halfspace(self) -> np.ndarray: # retorna la representación vectorial del semiespacio
    pass

  @abstractmethod
  def get_points(self) -> np.ndarray: # retorna los puntos que definen el semiespacio
    pass