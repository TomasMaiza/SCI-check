from abc import ABC, abstractmethod
import numpy as np
from common.enums import OrientResult
from geometry.abstract_structs.point import AbstractPoint
from geometry.abstract_structs.lpipoint import AbstractLPIPoint
from geometry.abstract_structs.halfspace import AbstractHalfspace

class AbstractPredicates(ABC):
  # clase para implementar los predicados en dimensión n
    
  @abstractmethod
  def orient(self, v: AbstractPoint, f: AbstractHalfspace) -> OrientResult: # retorna IN, OUT, ON
    pass

  @abstractmethod
  def orient_LPI(self) -> OrientResult: # retorna IN, OUT, ON
    pass

  @abstractmethod
  def orient_TPI(self) -> OrientResult: # retorna IN, OUT, ON
    pass