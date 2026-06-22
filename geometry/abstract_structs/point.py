from abc import ABC, abstractmethod
import numpy as np

class AbstractPoint(ABC):
  # representación de un punto en un espacio n-dimensional
  @property
  @abstractmethod
  def id(self) -> int: # id del punto
    pass
  
  @abstractmethod
  def get_point(self) -> np.ndarray: # retorna la representación vectorial del punto
    pass