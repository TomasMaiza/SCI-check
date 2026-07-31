import numpy as np
import numpy.typing as npt
import polytope as pc
from .strategy import ApproximationStrategy
from affine_system import *
from polytope_subregions.matrices import sas_augmented_matrix, augmented_x
from math import factorial

class Taylor(ApproximationStrategy):
  def __init__(self, 
               subsystem: AffineMode, 
               polytope: pc.Polytope,
               maxR: float):
    # Inicializa la función de aproximación y la función de error
    self._maxR = maxR
    self._A, self._b = subsystem.get_subsystem()
    self._homA = sas_augmented_matrix(subsystem)
    self._S = pc.extreme(polytope)
  
  def apply(self, h: float, s: int, order: int, x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    # aplica la función de aproximación
    homx = augmented_x(x)
    Phi = self.get_matrix(h, s, order)
    return Phi @ homx
  
  def error_bound(self, r: float, tau: float) -> float:
    # calcula el error de la aproximación
    pass
  
  def get_matrix(self, h: float, s: int, order: int) -> npt.NDArray[np.float64]:
    # calcula la matriz de la aproximación tomando el paso s
    tau = h / s
    dim = self._homA.shape[0]
    I = np.eye(dim, dtype=np.float64)
    Q = I.copy()
    term = I.copy()
    for j in range(1, order + 1):
      term = term @ (self._homA * tau) / j
      Q = Q + term
            
    # Squaring: Elevamos la matriz del micro-paso a la potencia s
    return np.linalg.matrix_power(Q, s)