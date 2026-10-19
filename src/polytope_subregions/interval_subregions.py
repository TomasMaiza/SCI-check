import numpy as np
from .subregions_strategy import SubregionsStrategy
from affine_system import *
from geometry import Polytope
#from .float_imp import Euler, Taylor, partition_matrices, partition_matrices_bound
from affine_system import SwitchedAffineSystem, AffineMode

class IntervalSubregions(SubregionsStrategy):
  def __init__(self, dimension: int):
    pass
  
  def get_subregion(self, 
                    subsystem: AffineMode, 
                    polytope: Polytope) -> Polytope:
    # obtiene la subregión para un modo particular
    pass

  def get_subregions(self, 
                     sas: SwitchedAffineSystem, 
                     polytope: Polytope, 
                     dwellTime: float, 
                     K: int) -> list[Polytope]:
    # recibe un politopo, el sistema y los parámetros para devolver la lista de subregiones
    h = dwellTime/K
    self._K = K
    self._h = h
    modes = sas.get_all_modes()
    polytopeMap = [] # inicializo el mapa de politopos para cada modo
    for i in modes:
      subsystem = sas.get_subsystem(i)
      subregionPolytope = self.get_subregion(subsystem, polytope)
      #if len(halfspaces) != 0:
      polytopeMap.append(subregionPolytope)
    return polytopeMap