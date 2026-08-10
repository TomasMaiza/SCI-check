from abc import ABC, abstractmethod
import numpy as np
from geometry import AbstractPoint, AbstractHalfspace

class Polytope(ABC):
  # Clase abstracta para representar politopos

  @abstractmethod
  def get_vertices(self) -> np.ndarray:
    # permite obtener los vértices del politopo
    pass

  @abstractmethod
  def get_hrep(self) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen al politopo
    pass

  @abstractmethod
  def intersect(self, p: 'Polytope') -> 'Polytope':
    # permite intersecar el politopo con otro
    pass

  @abstractmethod
  def union(self, p: 'Polytope') -> list['Polytope']:
    # permite calcular la unión del politopo con otro
    # retorna una lista por si la región resultante no es convexa
    pass

  @abstractmethod
  def difference(self, p: 'Polytope') -> list['Polytope']:
    # permite calcular la diferencia entre dos politopos
    pass

  @abstractmethod
  def is_empty(self) -> bool:
    # retorna si el politopo es vacío
    pass

  @abstractmethod
  def contains(self, x: AbstractPoint):
    # retorna si un punto pertenece al politopo
    # usar predicados para hacerlo exacto?
    pass

  @abstractmethod
  def subset(self, p: 'Polytope') -> bool:
    # retorna si el politopo es subconjunto de p
    pass

  @abstractmethod
  def reduce(self):
    # elimina las inecuaciones redundantes
    pass