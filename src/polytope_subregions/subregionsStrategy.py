from abc import ABC, abstractmethod
import numpy as np
import numpy.typing as npt
import polytope as pc
from affine_system import *
from common import PolytopeMap
from geometry import AbstractHalfspace
from .approximations import Euler

class SubregionsStrategy(ABC):
  def __init__(self):
    self._approx = Euler

  def get_subregion(self) -> list[AbstractHalfspace]:
    # obtiene la subregión para un modo particular
    pass

  def get_subregions(self, polytope: pc.Polytope, dwellTime: float) -> PolytopeMap:
    # recibe un politopo (y todo lo necesario) para devolver la lista de subregiones

    pass

  