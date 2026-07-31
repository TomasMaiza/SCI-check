from abc import ABC, abstractmethod
from common import PolytopeMap, OrientResult, VerticesIndex, EdgesIndex
from geometry import AbstractSimplex

class CoverageCheckStrategy(ABC):
  @abstractmethod
  def __init__(self):
    pass

  @abstractmethod
  def envelope_check(self, 
                     triangle: AbstractSimplex, 
                     polytopeSet: PolytopeMap, 
                     verticesIndex: VerticesIndex, 
                     edgesIndex: EdgesIndex) -> OrientResult:
    pass
