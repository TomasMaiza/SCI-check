from abc import ABC, abstractmethod
from common import OrientResult, Point
from geometry.abstract_structs import *
from geometry import Polytope

class AbstractPredicates(ABC):
  # clase para implementar los predicados en dimensión n
    
  @abstractmethod
  def orient(self, v: Point, f: Halfspace) -> OrientResult: # retorna IN, OUT, ON
    pass

  @abstractmethod
  def orient_LPI(self, 
                 v1: Point, 
                 v2: Point, 
                 f1: Halfspace, 
                 ref: Halfspace) -> OrientResult: # retorna IN, OUT, ON
    pass

  @abstractmethod
  def orient_TPI(self, 
                 polytope: Polytope, 
                 f1: Halfspace, 
                 f2: Halfspace, 
                 ref: Halfspace) -> OrientResult: # retorna IN, OUT, ON
    pass

  @abstractmethod
  def implicit_point_in_polytope(self, 
                                 polytope: Polytope, 
                                 f1: Halfspace, 
                                 f2: Halfspace) -> bool: 
    # retorna si un punto implícito está en el plano de un triángulo
    pass