from abc import ABC, abstractmethod
from common import PolytopeMap, OrientResult, VerticesIndex, EdgesIndex
from geometry import AbstractSimplex

class CoverageCheckStrategy(ABC):
  @abstractmethod
  def envelope_check(self, 
                     triangle: AbstractSimplex, 
                     polytopeSet: PolytopeMap, 
                     verticesIndex: VerticesIndex, 
                     edgesIndex: EdgesIndex) -> OrientResult:
    pass
