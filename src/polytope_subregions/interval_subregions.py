import numpy as np
from .subregions_strategy import SubregionsStrategy
from affine_system import *
from geometry import Polytope
#from .float_imp import Euler, Taylor, partition_matrices, partition_matrices_bound
from .interval_imp import get_subregion_from_julia
from affine_system import SwitchedAffineSystem, AffineMode

class IntervalSubregions(SubregionsStrategy):
  def __init__(self, dimension: int):
    self._approx = "Taylor"
    self._dimension = dimension
  
  def get_subregion(self, 
                    subsystem: AffineMode, 
                    polytope: Polytope) -> Polytope:
    # obtiene la subregión para un modo particular
    H, c = polytope.get_hrep_normalized() # normalized o no?
    S = polytope.get_vertices()
    A, b = subsystem.get_subsystem()
    
    matrixA, matrixb = get_subregion_from_julia(self._approx, H, c, S, A, b, self._h, self._K)
    subregionPolytope = type(polytope)(intDim = self._dimension, ambDim = self._dimension, A = matrixA, b = matrixb)
    return subregionPolytope

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
      polytopeMap.append(subregionPolytope)
    return polytopeMap