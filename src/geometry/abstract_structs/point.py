from abc import ABC, abstractmethod
import numpy as np

class AbstractPoint(ABC):
  # representación de un punto en un espacio n-dimensional
  
  @abstractmethod
  def get_point(self) -> tuple[float, ...]: # retorna la representación vectorial del punto
    pass