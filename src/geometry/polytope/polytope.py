from abc import ABC, abstractmethod
import numpy as np
from typing import Optional
from geometry import AbstractPoint, AbstractHalfspace, Hyperplane
from common import Edge

class Polytope(ABC):
  # Clase abstracta para representar politopos

  _intDim: int # dimensión intrínseca del politopo
  _ambDim: int # dimensión ambiental
  _boundaries: list['Polytope']
  _vertices: np.ndarray
  _A: np.ndarray 
  _b: np.ndarray
  # _supporting_hyperplane: Hyperplane | None

  def __init__(self,
               intDim: int,
               ambDim: int,
               vertices: Optional['tuple[AbstractPoint, ...]'] = None, 
               A: Optional['np.ndarray'] = None, 
               b: Optional['np.ndarray'] = None):
    pass

  @abstractmethod
  def get_vertices(self) -> np.ndarray:
    # permite obtener los vértices del politopo
    pass

  @abstractmethod
  def get_hrep(self) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen al politopo (Ax <= b)
    pass

  @abstractmethod
  def get_edges(self) -> list[tuple[tuple[float, ...], tuple[float, ...]]]:
    # retorna las aristas del politopo
    pass

  @abstractmethod
  def get_boundaries(self) -> list['Polytope']:
    # devuelve las caras del politopo como objetos Polytope
    pass

  @abstractmethod
  def get_halfspaces(self) -> list[AbstractHalfspace]:
    # devuelve la lista de los semiespacios que definen al politopo
    pass

  @abstractmethod
  def get_supporting_hyperplane(self) -> Hyperplane:
    # retorna el hiperplano que contiene al politopo si intDim < ambDim
    pass

  @abstractmethod
  def reduce(self):
    # elimina las inecuaciones redundantes
    pass