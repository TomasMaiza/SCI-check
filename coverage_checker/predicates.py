from abc import ABC, abstractmethod
from common import OrientResult
from geometry.abstract_structs import *

class AbstractPredicates(ABC):
  # clase para implementar los predicados en dimensión n
    
  @abstractmethod
  def orient(self, v: AbstractPoint, f: AbstractHalfspace) -> OrientResult: # retorna IN, OUT, ON
    pass

  @abstractmethod
  def orient_LPI(self, v1: AbstractPoint, v2: AbstractPoint, f1: AbstractHalfspace, f2: AbstractHalfspace) -> OrientResult: # retorna IN, OUT, ON
    pass

  @abstractmethod
  def orient_TPI(self) -> OrientResult: # retorna IN, OUT, ON
    pass