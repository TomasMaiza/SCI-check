from abc import ABC, abstractmethod
from geometry import *
from common import Point, Edge

# Patrón adapter
class AtteneAdapter(ABC):
  # clase abstracta para adaptar estructuras a la librería de Indirect Predicates de Attene
  @abstractmethod
  def create_explicit_point(self, point: Point): 
    # crea un punto explícito
    pass

  @abstractmethod
  def create_explicit_points_from_halfspace(self, hs: Halfspace): 
    # retorna los puntos explícitos que definen un semiespacio
    pass
  