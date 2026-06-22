from abc import ABC, abstractmethod
import numpy as np

class AbstractPredicates(ABC):
  # clase para implementar los predicados en dimensión n
    
  @abstractmethod # AL PRINCIPIO ORIENT PUEDE SER SIMPLEMENTE CHEQUEAR SI SE VERIFICA
  # LA INECUACIÓN (A LO MEJOR HACER OTRA FUNCIÓN MÁS ADEMÁS DE ORIENT)
  # BUSCAR ORIENT2D (Y 3D?) EN LIBRERÍA exactpred
  def orient(self) -> bool: # retorna ???
    pass

  @abstractmethod
  def orient_LPI(self) -> bool: # retorna ???
    pass

  @abstractmethod
  def orient_TPI(self) -> bool: # retorna ???
    pass