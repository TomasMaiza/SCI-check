from abc import ABC, abstractmethod
import numpy as np
from .point import AbstractPoint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.common.types import Edge

class AbstractSimplex(ABC):
  # clase para representar  el triángulo
    
  @property
  @abstractmethod
  def get_vertices(self) -> tuple['AbstractPoint', ...]: # retorna sus vértices
    pass

  @abstractmethod
  def get_edges(self) -> tuple['Edge', ...]: # retorna sus aristas
    pass

  @abstractmethod
  def get_inverse_edges(self) -> tuple['Edge', ...]:
    # retorna las aristas con el sentido invertido
    pass

  @abstractmethod
  def get_all_edges(self) -> tuple[tuple['Edge', ...], tuple['Edge', ...]]:
    # retorna las aristas en ambos sentidos
    pass