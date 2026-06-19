from abc import ABC, abstractmethod
import numpy as np

class AbstractPredicates(ABC):
  # clase para implementar los predicados en dimensión n
    
  @property
  @abstractmethod
  def orient(self) -> bool: # retorna ???
    pass

  @abstractmethod
  def orient_LPI(self) -> bool: # retorna ???
    pass

  @abstractmethod
  def orient_TPI(self) -> bool: # retorna ???
    pass