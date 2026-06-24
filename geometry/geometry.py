from abc import ABC, abstractmethod
import numpy as np
from .abstract_structs.point import AbstractPoint
from .abstract_structs.halfspace import AbstractHalfspace
from .abstract_structs.lpipoint import AbstractLPIPoint
from .abstract_structs.simplex import AbstractSimplex
from common.enums import OrientResult

class AbstractGeometry(ABC):
  # clase abstracta para generar estructuras geométricas de dimensión n
  @abstractmethod
  def create_point(self, coord: tuple[float, ...]) -> AbstractPoint: # crea un punto
    pass

  @abstractmethod
  def create_lpi_point(self, coord: tuple[float, ...], hs: AbstractHalfspace) -> AbstractLPIPoint: # crea un punto lpi
    pass

  @abstractmethod
  def create_simplex(self, vertices: tuple[float, ...]) -> AbstractSimplex: # crea un simplex
    pass

  @abstractmethod
  def create_halfspace(self, normal: tuple[float, ...], offset: float) -> AbstractHalfspace: # crea un semiespacio
    pass