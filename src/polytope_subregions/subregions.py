import numpy as np
import numpy.typing as npt
import polytope as pc
from .subregionsStrategy import SubregionsStrategy
from affine_system import *
from common import PolytopeMap
from geometry import AbstractHalfspace, AbstractGeometry
from .approximations import Euler
from affine_system import SwitchedAffineSystem, AffineMode
from .matrices import partition_matrices

class Subregions(SubregionsStrategy):
  def __init__(self, geometry: AbstractGeometry):
    self._approxMethod = Euler
    self._geometry = geometry

  def _create_halfspaces_list(self, subregionPolytope: pc.Polytope) -> list[AbstractHalfspace]:
    halfspaces = []
    for A, b in zip(subregionPolytope.A, subregionPolytope.b):
      hs = self._geometry.create_halfspace(normal_vector, constant_value)
      halfspaces.append(hs)

  def get_subregion(self, subsystem: AffineMode, polytope: pc.Polytope, K: int, h: float) -> list[AbstractHalfspace]:
    # obtiene la subregión para un modo particular
    approx = self._approxMethod(subsystem, polytope)
    phi = approx.get_matrix(h) # matriz de la aproximación. h ES CONSTANTE? o va h*k?
    r = 0 # r_0
    subregionA = [] # apilamos las matrices de las inecuaciones
    subregionb = []
    for k in range(0, K + 1):
      midr = approx.error_bound(r, h/2)
      Hplus, Hminus, c = partition_matrices(polytope, subsystem, r, h, midr)
      if k > 0:
        subregionA.append(Hminus @ phi)
        subregionb.append(c)
      if k < K:
        subregionA.append(Hplus @ phi)
        subregionb.append(c)
      r = approx.error_bound(r, abs(h)) # calculamos r_k al final?
    matrixA = np.vstack(subregionA)
    matrixb = np.vstack(subregionb)
    subregionPolytope = pc.Polytope(matrixA, matrixb)
    subregionPolytope = pc.reduce(subregionPolytope)
    return self._create_halfspaces_list(subregionPolytope)

  def get_subregions(self, sas: SwitchedAffineSystem, polytope: pc.Polytope, dwellTime: float, K: int) -> PolytopeMap:
    # recibe un politopo (y todo lo necesario) para devolver la lista de subregiones
    h = dwellTime/K
    modes = sas.get_all_modes()
    for i in modes:
      subsystem = sas.get_subsystem(i)
      self.get_subregion(subsystem, polytope, K, h)
