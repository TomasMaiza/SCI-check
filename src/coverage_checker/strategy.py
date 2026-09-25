from abc import ABC, abstractmethod
from common import OrientResult
from geometry import Polytope

class CoverageCheckStrategy(ABC):
  @abstractmethod
  def envelope_check(self, 
                     polytope: Polytope, 
                     subregionsMap: list[Polytope]) -> OrientResult: 
    pass
