import numpy as np
import numpy.typing as npt
import polytope as pc
from .strategy import ApproximationStrategy
from affine_system import *
from polytope_subregions.matrices import sas_augmented_matrix

class Euler(ApproximationStrategy):
  def __init__(self, subsystem: AffineMode, polytope: pc.Polytope):
    # Inicializa la función de aproximación y la función de error
    self._A, self._b = subsystem.get_subsystem()
    self._homA = sas_augmented_matrix(subsystem)
    self._S = pc.extreme(polytope)
  
  def apply(self, s: float, x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    # aplica la función de aproximación
    return x + s * (self._A @ x + self._b) # el @ hace el producto matricial
  
  def error_bound(self, r: float, tau: float) -> float:
    # calcula el error de la aproximación
    normA = np.linalg.norm(self._A, ord=2)
    M = self._get_M(normA)
    return r * (1 + normA * tau) + M * (np.exp(normA * tau) - 1 - normA * tau)

  def _get_M(self, normA: float):
    # auxiliar para calcular M
    if normA < 1e-12:
      return 0.0
    m = -1 # vamos a calcular el valor máximo de una norma así que inicio en un número negativo
    for x in self._S:
      norm = np.linalg.norm(self._A @ x + self._b, ord=2)
      if norm > m:
        m = norm
    return 1/normA * m

  def get_matrix(self, s: float) -> npt.NDArray[np.float64]:
    # calcula la matriz de la aproximación tomando el paso s con la matriz aumentada
    dim = self._homA.shape[0]
    I = np.eye(dim, dtype=np.float64)
    return I + s * self._homA