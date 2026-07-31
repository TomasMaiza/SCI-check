from abc import ABC, abstractmethod
import numpy as np
import numpy.typing as npt
import polytope as pc
from affine_system import *
from common import PolytopeMap
from geometry import AbstractHalfspace
from affine_system import SwitchedAffineSystem

class SubregionsStrategy(ABC):
  @abstractmethod
  def __init__(self):
    pass

  @abstractmethod
  def get_subregion(self, polytope: pc.Polytope) -> list[AbstractHalfspace]:
    # obtiene la subregión para un modo particular
    pass

  @abstractmethod
  def get_subregions(self, 
                     sas: SwitchedAffineSystem, 
                     polytope: pc.Polytope, 
                     dwellTime: float, 
                     K: int) -> PolytopeMap:
    # recibe un politopo (y todo lo necesario) para devolver la lista de subregiones
    pass

  