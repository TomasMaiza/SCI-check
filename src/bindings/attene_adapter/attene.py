from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from geometry import *

if TYPE_CHECKING:
  from src.common.types import Edge

# Patrón adapter
class AtteneAdapter(ABC):
  # clase abstracta para adaptar estructuras a la librería de Indirect Predicates de Attene
  @abstractmethod
  def create_explicit_point(self, point: AbstractPoint): 
    # crea un punto explícito
    pass

  @abstractmethod
  def create_explicit_points_from_halfspace(self, hs: Halfspace): 
    # retorna los puntos explícitos que definen un semiespacio
    pass
  