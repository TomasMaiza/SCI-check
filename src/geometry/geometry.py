from abc import ABC, abstractmethod
import numpy as np
from .abstract_structs import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .polytope import Polytope

class AbstractGeometry(ABC):
  # clase abstracta para generar estructuras geométricas de dimensión n
  @abstractmethod
  def create_point(self, coord: tuple[float, ...]) -> AbstractPoint: # crea un punto
    pass

  @abstractmethod
  def create_simplex(self, vertices: tuple[AbstractPoint, ...]) -> AbstractSimplex: # crea un simplex
    pass

  @abstractmethod
  def create_halfspace(self, points: tuple[AbstractPoint, ...]) -> AbstractHalfspace: # crea un semiespacio
    pass

  @abstractmethod
  def create_halfspace_from_vector(self, normalVector: np.ndarray, b: float) -> AbstractHalfspace: # crea un semiespacio
    pass

  @abstractmethod
  def get_dimension(self) -> int: # retorna la dimensión
    pass

  @abstractmethod
  def create_halfspaces_list(self, subregionPolytope: 'Polytope') -> list[AbstractHalfspace]:
    # crea una lista de semiespacios que definen un politopo
    pass