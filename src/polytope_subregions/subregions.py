import numpy as np
import numpy.typing as npt
import polytope as pc
from .subregionsStrategy import SubregionsStrategy
from affine_system import *
from common import PolytopeMap
from geometry import AbstractHalfspace
from .approximations import Euler
from affine_system import SwitchedAffineSystem, AffineMode
from .matrices import partition_matrices

class Subregions(SubregionsStrategy):
  def __init__(self):
    self._approxMethod = Euler

  def get_subregion(self, subsystem: AffineMode, polytope: pc.Polytope, K: int, h: float) -> list[AbstractHalfspace]:
    # obtiene la subregión para un modo particular
    approx = self._approxMethod(subsystem, polytope)
    r = 0 # r_0
    for k in range(0, K): # ir metiendo cosas al retorno en cada iteración?
                          # ver cómo calcular los semiespacios resultantes que definan el politopo
                          # es la intersección de cada X_i_k
      midr = approx.error_bound(r, h/2)
      posH, negH, c = partition_matrices(polytope, subsystem, r, h, midr)
      # calcular acá los semiespacios con posH y negH
      r = approx.error_bound(r, abs(h)) # calculamos r_k al final?
    # al final del for queda un calculo más con negH

  def get_subregions(self, sas: SwitchedAffineSystem, polytope: pc.Polytope, dwellTime: float, K: int) -> PolytopeMap:
    # recibe un politopo (y todo lo necesario) para devolver la lista de subregiones
    h = dwellTime/K
    modes = sas.get_all_modes()
    for i in modes:
      subsystem = sas.get_subsystem(i)
      self.get_subregion(subsystem, polytope, K, h)
