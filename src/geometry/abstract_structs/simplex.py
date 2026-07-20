from abc import ABC, abstractmethod
import numpy as np
from .point import AbstractPoint

class AbstractSimplex(ABC):
  # clase para representar  el triángulo
    
  @property
  @abstractmethod
  def get_vertices(self) -> tuple['AbstractPoint', ...]: # retorna sus vértices
    pass

  @abstractmethod
  def get_edges(self) -> tuple[tuple['AbstractPoint', 'AbstractPoint'], ...]: # retorna sus aristas
    pass